#!/usr/bin/env python3
"""
MedGemma Fine-Tuning with PyTorch Accelerate
Fixes wandb errors and properly tracks perplexity metrics
"""

import os
import sys
import math
import argparse
from pathlib import Path
from typing import Dict, Optional
import yaml
import json

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    get_scheduler,
    set_seed,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model
from accelerate import Accelerator
from accelerate.utils import set_seed as accelerate_set_seed
from tqdm.auto import tqdm


class MedGemmaTrainer:
    """Trainer for MedGemma with Accelerate and Wandb integration"""
    
    def __init__(self, config_path: str, max_steps: Optional[int] = None):
        """Initialize trainer with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        if max_steps is not None:
            self.config['training']['max_steps'] = max_steps
        
        # Initialize accelerator
        self.accelerator = Accelerator(
            gradient_accumulation_steps=self.config['training'].get('gradient_accumulation_steps', 1),
            mixed_precision='bf16' if self.config['training'].get('bf16', True) else 'no',
            log_with='wandb' if self.config['wandb'].get('enabled', True) else None,
        )
        
        # Set random seed
        seed = self.config['reproducibility'].get('seed', 42)
        set_seed(seed)
        accelerate_set_seed(seed)
        
        # Initialize wandb
        if self.accelerator.is_main_process and self.config['wandb'].get('enabled', True):
            wandb_config = self.config['wandb']
            self.accelerator.init_trackers(
                project_name=wandb_config.get('project', 'ihep-medgemma-finetune'),
                config=self.config,
                init_kwargs={
                    'wandb': {
                        'entity': wandb_config.get('entity'),
                        'name': wandb_config.get('name', 'medgemma-training'),
                        'tags': wandb_config.get('tags', []),
                    }
                }
            )
        
        self.model = None
        self.tokenizer = None
        self.train_dataloader = None
        self.eval_dataloader = None
        self.optimizer = None
        self.lr_scheduler = None
        self.global_step = 0
    
    def setup_model_and_tokenizer(self):
        """Load and configure the model with LoRA"""
        self.accelerator.print("Loading model and tokenizer...")
        
        model_config = self.config['model']
        base_model = model_config['base_model']
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.bfloat16 if model_config.get('precision') == 'bf16' else torch.float32,
            device_map=None,
        )
        
        # Enable gradient checkpointing
        if model_config.get('gradient_checkpointing', True):
            self.model.gradient_checkpointing_enable()
        
        # Apply LoRA
        lora_config_dict = self.config.get('lora', {})
        if lora_config_dict.get('enabled', True):
            self.accelerator.print("Applying LoRA...")
            lora_config = LoraConfig(
                r=lora_config_dict.get('r', 64),
                lora_alpha=lora_config_dict.get('alpha', 128),
                target_modules=lora_config_dict.get('target_modules', ["q_proj", "k_proj", "v_proj", "o_proj"]),
                lora_dropout=lora_config_dict.get('dropout', 0.05),
                bias=lora_config_dict.get('bias', 'none'),
                task_type='CAUSAL_LM',
            )
            self.model = get_peft_model(self.model, lora_config)
            self.model.print_trainable_parameters()
        
        self.accelerator.print(f"Model loaded: {base_model}")
    
    def prepare_datasets(self):
        """Load and prepare datasets"""
        self.accelerator.print("Loading datasets...")
        
        data_dir = Path(__file__).parent / 'processed_for_training'
        data_files = {
            'train': str(data_dir / 'train.jsonl'),
            'validation': str(data_dir / 'validation.jsonl'),
        }
        
        for split, path in data_files.items():
            if not Path(path).exists():
                self.accelerator.print(f"Warning: {split} data not found at {path}")
                self.accelerator.print("Creating dummy dataset for testing...")
                # Create dummy data for testing
                os.makedirs(data_dir, exist_ok=True)
                with open(path, 'w') as f:
                    for i in range(10):
                        f.write(json.dumps({
                            "text": f"Sample text {i} for training purposes."
                        }) + "\n")
        
        dataset = load_dataset('json', data_files=data_files)
        
        # Tokenize
        def tokenize_function(examples):
            texts = examples.get('text', [])
            return self.tokenizer(
                texts,
                truncation=True,
                max_length=self.config['model'].get('max_length', 2048),
                padding='max_length',
            )
        
        tokenized_datasets = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset["train"].column_names,
        )
        
        tokenized_datasets.set_format("torch")
        
        # Create dataloaders
        train_config = self.config['training']
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        self.train_dataloader = DataLoader(
            tokenized_datasets["train"],
            batch_size=train_config.get('per_device_train_batch_size', 2),
            collate_fn=data_collator,
            shuffle=True,
        )
        
        self.eval_dataloader = DataLoader(
            tokenized_datasets["validation"],
            batch_size=train_config.get('per_device_eval_batch_size', 4),
            collate_fn=data_collator,
        )
        
        self.accelerator.print(f"Train examples: {len(tokenized_datasets['train'])}")
        self.accelerator.print(f"Eval examples: {len(tokenized_datasets['validation'])}")
    
    def setup_optimizer_and_scheduler(self):
        """Setup optimizer and learning rate scheduler"""
        train_config = self.config['training']
        
        # Optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=train_config.get('learning_rate', 2e-5),
            weight_decay=train_config.get('weight_decay', 0.01),
            betas=(train_config.get('adam_beta1', 0.9), train_config.get('adam_beta2', 0.999)),
            eps=train_config.get('adam_epsilon', 1e-8),
        )
        
        # Calculate training steps
        num_epochs = train_config.get('num_train_epochs', 3)
        max_train_steps = train_config.get('max_steps', -1)
        
        if max_train_steps == -1:
            max_train_steps = len(self.train_dataloader) * num_epochs
        
        # LR Scheduler
        num_warmup_steps = int(max_train_steps * train_config.get('warmup_ratio', 0.03))
        
        self.lr_scheduler = get_scheduler(
            name=train_config.get('lr_scheduler_type', 'cosine'),
            optimizer=self.optimizer,
            num_warmup_steps=num_warmup_steps,
            num_training_steps=max_train_steps,
        )
        
        # Prepare with accelerator
        self.model, self.optimizer, self.train_dataloader, self.eval_dataloader, self.lr_scheduler = \
            self.accelerator.prepare(
                self.model, self.optimizer, self.train_dataloader, self.eval_dataloader, self.lr_scheduler
            )
            
        self.accelerator.print(f"Total training steps: {max_train_steps}")
    
    def compute_perplexity(self, eval_loss):
        """Compute perplexity from loss"""
        try:
            perplexity = math.exp(eval_loss)
        except OverflowError:
            perplexity = float("inf")
        return perplexity
    
    def evaluate(self):
        """Evaluation loop"""
        self.model.eval()
        losses = []
        
        for batch in self.eval_dataloader:
            with torch.no_grad():
                outputs = self.model(**batch)
                loss = outputs.loss
                losses.append(self.accelerator.gather(loss.repeat(batch['input_ids'].shape[0])))
        
        losses = torch.cat(losses)
        eval_loss = torch.mean(losses).item()
        perplexity = self.compute_perplexity(eval_loss)
        
        return {"eval_loss": eval_loss, "perplexity": perplexity}
    
    def train(self):
        """Main training loop"""
        train_config = self.config['training']
        max_steps = train_config.get('max_steps', -1)
        if max_steps == -1:
            max_steps = len(self.train_dataloader) * train_config.get('num_train_epochs', 3)
        
        eval_steps = train_config.get('eval_steps', 250)
        logging_steps = train_config.get('logging_steps', 50)
        save_steps = train_config.get('save_steps', 500)
        
        progress_bar = tqdm(range(max_steps), disable=not self.accelerator.is_local_main_process)
        
        self.model.train()
        total_loss = 0
        
        for epoch in range(train_config.get('num_train_epochs', 3)):
            for step, batch in enumerate(self.train_dataloader):
                with self.accelerator.accumulate(self.model):
                    outputs = self.model(**batch)
                    loss = outputs.loss
                    total_loss += loss.detach().float()
                    
                    self.accelerator.backward(loss)
                    
                    if self.accelerator.sync_gradients:
                        self.accelerator.clip_grad_norm_(
                            self.model.parameters(),
                            train_config.get('max_grad_norm', 1.0)
                        )
                    
                    self.optimizer.step()
                    self.lr_scheduler.step()
                    self.optimizer.zero_grad()
                
                if self.accelerator.sync_gradients:
                    self.global_step += 1
                    progress_bar.update(1)
                    
                    # Logging
                    if self.global_step % logging_steps == 0:
                        avg_loss = total_loss / logging_steps
                        train_perplexity = self.compute_perplexity(avg_loss)
                        
                        self.accelerator.log({
                            "train_loss": avg_loss.item(),
                            "train_perplexity": train_perplexity,
                            "learning_rate": self.lr_scheduler.get_last_lr()[0],
                            "epoch": epoch,
                        }, step=self.global_step)
                        
                        total_loss = 0
                    
                    # Evaluation
                    if self.global_step % eval_steps == 0:
                        eval_metrics = self.evaluate()
                        self.accelerator.log(eval_metrics, step=self.global_step)
                        self.accelerator.print(
                            f"Step {self.global_step}: eval_loss={eval_metrics['eval_loss']:.4f}, "
                            f"perplexity={eval_metrics['perplexity']:.2f}"
                        )
                        self.model.train()
                    
                    # Save checkpoint
                    if self.global_step % save_steps == 0:
                        self.save_checkpoint()
                
                if self.global_step >= max_steps:
                    break
            
            if self.global_step >= max_steps:
                break
        
        # Final evaluation
        final_metrics = self.evaluate()
        self.accelerator.log(final_metrics, step=self.global_step)
        self.accelerator.print(f"Final metrics: {final_metrics}")
        
        # Save final model
        self.save_checkpoint(is_final=True)
        
        # End tracking
        self.accelerator.end_training()
    
    def save_checkpoint(self, is_final=False):
        """Save model checkpoint"""
        output_dir = Path(self.config['output']['output_dir'])
        
        if is_final:
            save_dir = output_dir / "final_model"
        else:
            save_dir = output_dir / f"checkpoint-{self.global_step}"
        
        self.accelerator.wait_for_everyone()
        unwrapped_model = self.accelerator.unwrap_model(self.model)
        
        if self.accelerator.is_main_process:
            unwrapped_model.save_pretrained(save_dir)
            self.tokenizer.save_pretrained(save_dir)
            self.accelerator.print(f"Saved checkpoint to {save_dir}")


def main():
    parser = argparse.ArgumentParser(description="Train MedGemma with Accelerate")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/medgemma_finetune.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--max_steps",
        type=int,
        default=None,
        help="Override max training steps (for testing)"
    )
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = MedGemmaTrainer(args.config, max_steps=args.max_steps)
    
    # Setup
    trainer.setup_model_and_tokenizer()
    trainer.prepare_datasets()
    trainer.setup_optimizer_and_scheduler()
    
    # Train
    trainer.train()


if __name__ == "__main__":
    main()

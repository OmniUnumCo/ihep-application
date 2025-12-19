# MedGemma Training with PyTorch Accelerate

This directory contains the training infrastructure for fine-tuning MedGemma using PyTorch Accelerate, with proper wandb integration and perplexity tracking.

## Quick Start

```bash
cd ihep/training_datasets
./quick_start.sh
```

## Files Created

- **`train_medgemma.py`**: Main training script with Accelerate integration
  - Fixes wandb errors with proper metric synchronization
  - Computes and logs perplexity correctly across distributed training
  - Supports LoRA fine-tuning
  - Automatic mixed-precision (bf16) training
  - Gradient checkpointing for memory efficiency

- **`configs/accelerate_config.yaml`**: Accelerate configuration
  - Distributed training settings
  - Mixed precision configuration
  - Multi-GPU support

- **`quick_start.sh`**: Helper script for setup

## Usage

### 1. Install Dependencies

```bash
pip install torch transformers datasets accelerate peft bitsandbytes wandb tensorboard
```

Or install from requirements:
```bash
pip install -r ../applications/backend/requirements.txt
```

### 2. Prepare Your Data

Make sure you have processed training data in `processed_for_training/`:
- `train.jsonl`
- `validation.jsonl`

If not, run the preprocessing script:
```bash
python scripts/preprocess_for_medgemma.py
```

### 3. Configure Wandb (Optional)

```bash
wandb login
```

Edit `configs/medgemma_finetune.yaml` to set your wandb entity:
```yaml
wandb:
  enabled: true
  project: "ihep-medgemma-finetune"
  entity: "your-wandb-entity"  # Set this
  name: "medgemma-digital-twins-v1"
```

### 4. Run Training

**Test run (10 steps):**
```bash
python train_medgemma.py --config configs/medgemma_finetune.yaml --max_steps 10
```

**Full training (single GPU):**
```bash
python train_medgemma.py --config configs/medgemma_finetune.yaml
```

**Distributed training (multi-GPU):**
```bash
accelerate launch --config_file configs/accelerate_config.yaml \
  train_medgemma.py --config configs/medgemma_finetune.yaml
```

## What This Fixes

### Wandb Errors
- ✅ Proper initialization through Accelerate's tracker system
- ✅ Metric synchronization across distributed processes
- ✅ Automatic logging of train/eval metrics
- ✅ No more duplicate or missing runs

### Perplexity Tracking
- ✅ Correct calculation: `perplexity = exp(loss)`
- ✅ Overflow handling for high loss values
- ✅ Logged separately for train and eval
- ✅ Synchronized across GPUs in distributed training

### Other Improvements
- ✅ Gradient accumulation support
- ✅ Mixed precision (bf16) training
- ✅ Proper checkpoint saving
- ✅ Learning rate scheduling
- ✅ Progress bars with tqdm

## Monitoring

### Wandb Dashboard
Your training metrics will appear in the wandb dashboard:
- `train_loss`: Training loss per logging step
- `train_perplexity`: Training perplexity
- `eval_loss`: Evaluation loss
- `perplexity`: Evaluation perplexity
- `learning_rate`: Current learning rate
- `epoch`: Current epoch

### Tensorboard (Alternative)
If you prefer tensorboard:
```bash
tensorboard --logdir outputs/medgemma_ihep_finetune
```

## Checkpoints

Checkpoints are saved to `outputs/medgemma_ihep_finetune/`:
- `checkpoint-{step}/`: Intermediate checkpoints every 500 steps
- `final_model/`: Final trained model

## Troubleshooting

### "No GPU available"
The script will work on CPU but will be very slow. Consider using Google Colab or a cloud GPU.

### "Out of memory"
Reduce batch size in `configs/medgemma_finetune.yaml`:
```yaml
training:
  per_device_train_batch_size: 1  # Reduce from 2
  gradient_accumulation_steps: 16  # Increase to maintain effective batch size
```

### "Wandb not initialized"
Make sure `wandb.enabled: true` in the config and you've run `wandb login`.

### "Data files not found"
Run the preprocessing script or the trainer will create dummy data for testing.

## Configuration

All training parameters are in `configs/medgemma_finetune.yaml`:
- Model settings (base model, precision, max length)
- LoRA configuration (rank, alpha, target modules)
- Training hyperparameters (LR, batch size, epochs)
- Evaluation settings
- Wandb configuration

## Next Steps

1. ✅ Test with dummy data: `python train_medgemma.py --max_steps 10`
2. Prepare real training data with preprocessing scripts
3. Configure wandb entity and project name
4. Run full training
5. Monitor metrics in wandb dashboard
6. Evaluate final model on test set

## Support

For questions or issues, refer to:
- [TRAINING_GUIDE.md](./TRAINING_GUIDE.md) - Comprehensive training documentation
- [PyTorch Accelerate Docs](https://huggingface.co/docs/accelerate)
- [Weights & Biases Docs](https://docs.wandb.ai)

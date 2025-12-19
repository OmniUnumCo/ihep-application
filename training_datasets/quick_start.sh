#!/bin/bash
# Quick start script for MedGemma training

echo "==================================="
echo "MedGemma Training - Quick Start"
echo "==================================="

# Check if in correct directory
if [ ! -f "configs/medgemma_finetune.yaml" ]; then
    echo "Error: Please run this script from the training_datasets directory"
    exit 1
fi

# Install dependencies
echo "Step 1: Installing dependencies..."
pip install -q torch transformers datasets accelerate peft bitsandbytes wandb tensorboard evaluate scipy pyyaml tqdm

# Check for processed data
if [ ! -d "processed_for_training" ]; then
    echo "Step 2: Creating dummy training data for testing..."
    mkdir -p processed_for_training
else
    echo "Step 2: Found existing processed_for_training directory"
fi

# Login to wandb (optional)
echo ""
echo "Step 3: Wandb setup (optional)"
read -p "Do you want to login to Weights & Biases? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    wandb login
else
    echo "Skipping wandb login. You can login later with: wandb login"
fi

echo ""
echo "==================================="
echo "Setup complete! You can now run:"
echo ""
echo "  # Test run (10 steps):"
echo "  python train_medgemma.py --config configs/medgemma_finetune.yaml --max_steps 10"
echo ""
echo "  # Full training:"
echo "  python train_medgemma.py --config configs/medgemma_finetune.yaml"
echo ""
echo "  # Distributed training (multi-GPU):"
echo "  accelerate launch --config_file configs/accelerate_config.yaml train_medgemma.py --config configs/medgemma_finetune.yaml"
echo "==================================="

# MedGemma Training with Accelerate - Quick Reference

## 🎯 What Was Fixed

✅ **Wandb Errors**: Proper integration through Accelerate's tracker system  
✅ **Perplexity Tracking**: Correctly calculated and logged with `exp(loss)`  
✅ **Distributed Training**: Multi-GPU support with metric synchronization  
✅ **Mixed Precision**: Automatic bf16 training for better performance  

---

## 🚀 Quick Start

```bash
cd /Users/nexus1/Documents/ihep-app/ihep/training_datasets

# Run helper script
./quick_start.sh

# Or manually:
pip install torch transformers datasets accelerate peft wandb

# Test (10 steps)
python train_medgemma.py --config configs/medgemma_finetune.yaml --max_steps 10

# Full training
python train_medgemma.py --config configs/medgemma_finetune.yaml
```

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `train_medgemma.py` | Main training script with Accelerate |
| `configs/accelerate_config.yaml` | Distributed training config |
| `quick_start.sh` | Setup helper script |
| `ACCELERATE_TRAINING.md` | Full documentation |

---

## 🔧 Configuration

Edit [configs/medgemma_finetune.yaml](file:///Users/nexus1/Documents/ihep-app/ihep/training_datasets/configs/medgemma_finetune.yaml):

```yaml
wandb:
  enabled: true
  project: "ihep-medgemma-finetune"
  entity: "your-wandb-entity"  # ← Set this!
  
training:
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
  learning_rate: 2.0e-5
  num_train_epochs: 3
```

---

## 📊 Metrics in Wandb

Your runs will now properly log:
- `train_loss` & `train_perplexity` (every 50 steps)
- `eval_loss` & `perplexity` (every 250 steps)
- `learning_rate` & `epoch`

---

## 🐛 Common Issues

**Out of Memory?**
```yaml
training:
  per_device_train_batch_size: 1  # Reduce
  gradient_accumulation_steps: 16  # Increase
```

**Wandb not working?**
```bash
wandb login
# Check wandb.enabled: true in config
```

**No data files?**
```bash
# Preprocessing will create dummy data for testing
# Or run your preprocessing script:
python scripts/preprocess_for_medgemma.py
```

---

## 📖 Full Documentation

- [ACCELERATE_TRAINING.md](file:///Users/nexus1/Documents/ihep-app/ihep/training_datasets/ACCELERATE_TRAINING.md) - Complete guide
- [TRAINING_GUIDE.md](file:///Users/nexus1/Documents/ihep-app/ihep/training_datasets/TRAINING_GUIDE.md) - Original training docs
- [Walkthrough](file:///Users/nexus1/.gemini/antigravity/brain/cc96e9ee-559f-48c2-b031-4aa172c8d3a2/walkthrough.md) - What was implemented

---

**Ready to train!** 🎉

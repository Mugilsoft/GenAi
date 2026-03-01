import torch
import torch.nn as nn
from transformers import (
    T5ForConditionalGeneration,
    RobertaTokenizer,
    get_linear_schedule_with_warmup
)
from torch.optim import AdamW
from peft import LoraConfig, get_peft_model, TaskType
from torch.cuda.amp import autocast, GradScaler
import pandas as pd
import json
import numpy as np
from pathlib import Path
from tqdm.auto import tqdm
from datetime import datetime
import matplotlib.pyplot as plt
from data_loader import create_data_loaders

def set_seed(seed: int = 42):
    """Set random seeds for reproducibility"""
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def train_epoch(model, train_loader, optimizer, scheduler, device, config, scaler=None):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    grad_accum_steps = config['gradient_accumulation_steps']
    progress_bar = tqdm(train_loader, desc="Training")
    
    optimizer.zero_grad()
    
    for step, batch in enumerate(progress_bar):
        # Move batch to device
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        # Forward pass with mixed precision (only if CUDA is available)
        use_amp = scaler is not None and device.type == 'cuda'
        with autocast(enabled=use_amp):
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            loss = outputs.loss / grad_accum_steps
        
        total_loss += loss.item() * grad_accum_steps
        
        # Backward pass
        if scaler is not None:
            scaler.scale(loss).backward()
        else:
            loss.backward()
        
        # Update weights every grad_accum_steps
        if (step + 1) % grad_accum_steps == 0:
            if scaler is not None:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), config['max_grad_norm'])
                scaler.step(optimizer)
                scaler.update()
            else:
                torch.nn.utils.clip_grad_norm_(model.parameters(), config['max_grad_norm'])
                optimizer.step()
            
            scheduler.step()
            optimizer.zero_grad()
        
        # Update progress bar
        progress_bar.set_postfix({'loss': loss.item() * grad_accum_steps})
    
    return total_loss / len(train_loader)

def evaluate(model, val_loader, device):
    """Evaluate on validation set"""
    model.eval()
    total_loss = 0
    
    with torch.no_grad():
        progress_bar = tqdm(val_loader, desc="Evaluating")
        for batch in progress_bar:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            total_loss += outputs.loss.item()
            progress_bar.set_postfix({'loss': outputs.loss.item()})
    
    return total_loss / len(val_loader)

def main():
    # Set paths
    BASE_DIR = Path(__file__).parent.parent
    MODEL_DIR = BASE_DIR / 'models'
    DATA_DIR = BASE_DIR / 'data' / 'processed'
    
    # Load config
    config_path = MODEL_DIR / 'training_config.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    set_seed()
    
    # Load data
    print("Loading data...")
    try:
        train_data = pd.read_json(DATA_DIR / 'train.json')
        val_data = pd.read_json(DATA_DIR / 'validation.json')
    except Exception as e:
        print(f"Error loading data: {e}. Please ensure data is preprocessed.")
        return

    # Initialize tokenizer and model
    print(f"Loading model: {config['model_name']}")
    tokenizer = RobertaTokenizer.from_pretrained(config['model_name'])
    model = T5ForConditionalGeneration.from_pretrained(config['model_name'])
    
    # Apply LoRA if configured
    if config.get('use_lora', False):
        print("Applying LoRA...")
        lora_config = LoraConfig(
            r=config['lora_r'],
            lora_alpha=config['lora_alpha'],
            target_modules=config['lora_target_modules'],
            lora_dropout=config['lora_dropout'],
            bias="none",
            task_type=TaskType.SEQ_2_SEQ_LM
        )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
    
    model = model.to(device)
    
    # Create data loaders
    train_loader, val_loader = create_data_loaders(train_data, val_data, tokenizer, config)
    
    # Setup optimizer and scheduler
    optimizer = AdamW(
        model.parameters(),
        lr=config['learning_rate'],
        weight_decay=config['weight_decay']
    )
    
    total_steps = len(train_loader) * config['num_epochs']
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=config['warmup_steps'],
        num_training_steps=total_steps
    )
    
    # Training Loop
    history = {'train_loss': [], 'val_loss': [], 'learning_rate': []}
    best_val_loss = float('inf')
    patience_counter = 0
    
    # Initialize GradScaler for mixed precision (only if CUDA is available)
    scaler = None
    if device.type == 'cuda' and (config.get('fp16', False) or config.get('bf16', False)):
        scaler = GradScaler()
        print("Mixed precision training enabled")
    else:
        print("Mixed precision training disabled (CPU or not configured)")
    
    print("Starting training...")
    for epoch in range(config['num_epochs']):
        print(f"\nEpoch {epoch + 1}/{config['num_epochs']}")
        
        train_loss = train_epoch(model, train_loader, optimizer, scheduler, device, config, scaler=scaler)
        val_loss = evaluate(model, val_loader, device)
        
        current_lr = optimizer.param_groups[0]['lr']
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['learning_rate'].append(current_lr)
        
        print(f"Epoch {epoch + 1} Summary: Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, LR: {current_lr:.2e}")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            model_save_path = MODEL_DIR / 'best_model'
            model.save_pretrained(model_save_path)
            tokenizer.save_pretrained(model_save_path)
            print(f"✓ Model saved to {model_save_path}")
        else:
            patience_counter += 1
            if patience_counter >= config['early_stopping_patience']:
                print(f"Early stopping triggered after {epoch + 1} epochs")
                break
    
    # Save history
    with open(MODEL_DIR / 'training_history.json', 'w') as f:
        json.dump(history, f, indent=2)
    
    print("Training complete!")

if __name__ == '__main__':
    main()

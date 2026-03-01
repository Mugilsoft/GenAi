import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from typing import Dict, Any

class CodeDataset(Dataset):
    """Custom Dataset for code generation tasks with pre-tokenization"""
    
    def __init__(self, data: pd.DataFrame, tokenizer: Any, max_input_length: int, max_output_length: int):
        """
        Initialize the dataset and pre-tokenize everything
        """
        self.tokenizer = tokenizer
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
        
        print(f"Pre-tokenizing {len(data)} samples...")
        
        # Pre-tokenize all inputs
        self.inputs = self.tokenizer(
            [str(x) for x in data['input'].tolist()],
            max_length=self.max_input_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Pre-tokenize all outputs
        self.outputs = self.tokenizer(
            [str(x) for x in data['output'].tolist()],
            max_length=self.max_output_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Prepare labels (replace padding token id with -100 for loss calculation)
        self.labels = self.outputs['input_ids'].clone()
        self.labels[self.labels == self.tokenizer.pad_token_id] = -100
    
    def __len__(self) -> int:
        return len(self.labels)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        return {
            'input_ids': self.inputs['input_ids'][idx],
            'attention_mask': self.inputs['attention_mask'][idx],
            'labels': self.labels[idx]
        }

def create_data_loaders(
    train_data: pd.DataFrame,
    val_data: pd.DataFrame,
    tokenizer: Any,
    config: Dict[str, Any]
) -> tuple[DataLoader, DataLoader]:
    """
    Create training and validation data loaders
    
    Args:
        train_data: Training data DataFrame
        val_data: Validation data DataFrame
        tokenizer: HuggingFace tokenizer
        config: Configuration dictionary
        
    Returns:
        Tuple of (train_loader, val_loader)
    """
    train_dataset = CodeDataset(
        train_data,
        tokenizer,
        config['max_input_length'],
        config['max_output_length']
    )

    val_dataset = CodeDataset(
        val_data,
        tokenizer,
        config['max_input_length'],
        config['max_output_length']
    )

    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=0  # Set to 0 for Windows compatibility
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=config['batch_size'],
        shuffle=False,
        num_workers=0
    )
    
    return train_loader, val_loader

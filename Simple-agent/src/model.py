"""
Model wrapper for the coding agent.
Provides a simple interface for loading and using the trained model.
"""

import torch
from transformers import T5ForConditionalGeneration, RobertaTokenizer
from pathlib import Path
from typing import Optional, Dict, Any
import json


class CodingAgentModel:
    """Wrapper class for the coding agent model"""
    
    def __init__(self, model_path: str, device: Optional[str] = None):
        """
        Initialize the coding agent model
        
        Args:
            model_path: Path to the trained model directory
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
        """
        self.model_path = Path(model_path).resolve()
        
        # Check if model path exists
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model directory not found at {self.model_path}. "
                "Please ensure the model is trained and saved in this directory."
            )
        
        # Set device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        # Load model and tokenizer
        # Use as_posix() to ensure forward slashes on Windows, which transformers handles better
        model_str = self.model_path.as_posix()
        print(f"Loading model from {model_str}...")
        self.model = T5ForConditionalGeneration.from_pretrained(model_str)
        self.tokenizer = RobertaTokenizer.from_pretrained(model_str)
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Load configuration
        config_path = self.model_path.parent / 'training_config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                'max_input_length': 512,
                'max_output_length': 512,
                'num_beams': 4,
                'temperature': 0.7,
                'top_p': 0.95
            }
        
        print(f"Model loaded successfully on {self.device}")
    
    def generate(
        self,
        language: str,
        framework: str,
        task: str,
        context: str = "",
        max_length: Optional[int] = None,
        num_beams: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None
    ) -> str:
        """
        Generate code based on description
        
        Args:
            language: Programming language (csharp, typescript, sql)
            framework: Framework (dotnet8, angular, mssql)
            task: Description of what to generate
            context: Additional context (optional)
            max_length: Maximum output length (uses config default if None)
            num_beams: Number of beams for beam search (uses config default if None)
            temperature: Sampling temperature (uses config default if None)
            top_p: Top-p sampling parameter (uses config default if None)
        
        Returns:
            Generated code as string
        """
        # Use config defaults if not specified
        max_length = max_length or self.config['max_output_length']
        num_beams = num_beams or self.config['num_beams']
        temperature = temperature or self.config['temperature']
        top_p = top_p or self.config['top_p']
        
        # Create input prompt
        prompt = self._create_prompt(language, framework, task, context)
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors='pt',
            max_length=self.config['max_input_length'],
            truncation=True
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs['input_ids'],
                max_length=max_length,
                num_beams=num_beams,
                temperature=temperature,
                top_p=top_p,
                early_stopping=True,
                do_sample=temperature > 0
            )
        
        # Decode
        generated_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return generated_code
    
    def _create_prompt(self, language: str, framework: str, task: str, context: str = "") -> str:
        """Create formatted input prompt"""
        prompt = f"Language: {language}\n"
        prompt += f"Framework: {framework}\n"
        prompt += f"Task: {task}\n"
        if context:
            prompt += f"Context: {context}\n"
        return prompt
    
    def batch_generate(self, requests: list[Dict[str, Any]]) -> list[str]:
        """
        Generate code for multiple requests
        
        Args:
            requests: List of dictionaries with keys: language, framework, task, context (optional)
        
        Returns:
            List of generated code strings
        """
        results = []
        for request in requests:
            code = self.generate(
                language=request['language'],
                framework=request['framework'],
                task=request['task'],
                context=request.get('context', '')
            )
            results.append(code)
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            'model_path': str(self.model_path),
            'device': str(self.device),
            'num_parameters': sum(p.numel() for p in self.model.parameters()),
            'config': self.config
        }


if __name__ == '__main__':
    # Example usage
    # Get the directory of the current script
    current_dir = Path(__file__).parent
    model_dir = (current_dir.parent / 'models' / 'best_model').resolve()
    
    model = CodingAgentModel(str(model_dir))
    
    # Generate C# code
    code = model.generate(
        language='csharp',
        framework='dotnet8',
        task='Create a simple API controller with GET endpoint',
        context='ASP.NET Core 8'
    )
    
    print("Generated Code:")
    print("=" * 80)
    print(code)
    print("=" * 80)
    
    # Get model info
    info = model.get_model_info()
    print("\nModel Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")

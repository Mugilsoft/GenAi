# Coding Agent ML System

A machine learning-based coding assistant for .NET Core 8+, Angular, TypeScript, and SQL development.

## Overview

This project implements a transformer-based coding agent that can:
- Generate code snippets for .NET Core 8+, Angular, TypeScript, and SQL
- Complete partial code implementations
- Explain existing code
- Suggest bug fixes and improvements

## Project Structure

```
simple-coding-agent/
├── notebooks/              # Jupyter notebooks for development
│   ├── 01_data_collection.ipynb
│   ├── 02_data_preprocessing.ipynb
│   ├── 03_model_architecture.ipynb
│   ├── 04_training.ipynb
│   ├── 05_evaluation.ipynb
│   └── 06_inference_demo.ipynb
├── data/                   # Dataset storage
│   ├── raw/               # Raw collected data
│   └── processed/         # Preprocessed datasets
├── src/                    # Source code
│   ├── model.py           # Model wrapper
│   ├── api.py             # Flask API server
│   └── utils.py           # Utility functions
├── models/                 # Trained model weights
├── tests/                  # Unit tests
└── requirements.txt        # Python dependencies
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Jupyter Notebooks

```bash
jupyter notebook
```

Navigate to the `notebooks/` directory and run the notebooks in order:
1. **01_data_collection.ipynb** - Collect code samples
2. **02_data_preprocessing.ipynb** - Preprocess and clean data
3. **03_model_architecture.ipynb** - Design model architecture
4. **04_training.ipynb** - Train the model
5. **05_evaluation.ipynb** - Evaluate model performance
6. **06_inference_demo.ipynb** - Test the trained model

## Usage

### Training the Model

Follow the notebooks in sequence to train your own model from scratch.

### Using the API

Start the Flask API server:

```bash
python src/api.py
```

The API will be available at `http://localhost:5000`

#### API Endpoints

- **POST /generate** - Generate code from description
- **POST /complete** - Complete partial code
- **POST /explain** - Explain code functionality
- **POST /fix** - Suggest bug fixes

Example request:

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "language": "csharp",
    "description": "Create a simple ASP.NET Core controller",
    "context": ""
  }'
```

## Model Architecture

The system uses a fine-tuned transformer model based on CodeBERT/CodeT5:
- **Base Model**: Pre-trained on large code corpus
- **Fine-tuning**: Specialized for .NET Core 8+, Angular, TypeScript, SQL
- **Architecture**: Encoder-decoder transformer
- **Tokenizer**: Code-aware tokenization

## Development Workflow

1. **Data Collection**: Gather code samples from repositories and documentation
2. **Preprocessing**: Clean and tokenize data
3. **Training**: Fine-tune pre-trained model on collected data
4. **Evaluation**: Test on held-out dataset
5. **Deployment**: Serve via Flask API

## Testing

Run unit tests:

```bash
pytest tests/
```

## Performance Metrics

- **Perplexity**: Measures model confidence
- **BLEU Score**: Measures code generation quality
- **Exact Match**: Percentage of perfectly generated snippets

## Contributing

This is a research/development project. Contributions and improvements are welcome.

## License

MIT License

## Notes

- Model training requires GPU for reasonable performance
- Initial training may take several hours depending on dataset size
- Fine-tuning is recommended over training from scratch

"""
Flask API server for the coding agent model.
Provides REST API endpoints for code generation.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from model import CodingAgentModel
from pathlib import Path
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load model
MODEL_PATH = (Path(__file__).parent.parent / 'models' / 'best_model').resolve()
try:
    # Pass as string, the model class now handles existence checks
    model = CodingAgentModel(str(MODEL_PATH))
    logger.info("Model loaded successfully")
except FileNotFoundError as e:
    logger.error(f"Model not found: {str(e)}")
    logger.warning("API will run in 'unhealthy' state until model is available.")
    model = None
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    model = None


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if model is not None else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None
    })


@app.route('/generate', methods=['POST'])
def generate_code():
    """
    Generate code from description
    
    Request body:
    {
        "language": "csharp|typescript|sql",
        "framework": "dotnet8|angular|mssql",
        "task": "Description of what to generate",
        "context": "Additional context (optional)",
        "max_length": 512 (optional),
        "num_beams": 4 (optional),
        "temperature": 0.7 (optional)
    }
    
    Response:
    {
        "code": "Generated code",
        "language": "csharp",
        "framework": "dotnet8",
        "task": "Original task description"
    }
    """
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        # Parse request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['language', 'framework', 'task']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract parameters
        language = data['language']
        framework = data['framework']
        task = data['task']
        context = data.get('context', '')
        max_length = data.get('max_length')
        num_beams = data.get('num_beams')
        temperature = data.get('temperature')
        
        # Validate language and framework
        valid_languages = ['csharp', 'typescript', 'sql']
        valid_frameworks = ['dotnet8', 'angular', 'mssql']
        
        if language not in valid_languages:
            return jsonify({
                'error': f'Invalid language. Must be one of: {", ".join(valid_languages)}'
            }), 400
        
        if framework not in valid_frameworks:
            return jsonify({
                'error': f'Invalid framework. Must be one of: {", ".join(valid_frameworks)}'
            }), 400
        
        # Generate code
        logger.info(f"Generating {language} code: {task[:50]}...")
        generated_code = model.generate(
            language=language,
            framework=framework,
            task=task,
            context=context,
            max_length=max_length,
            num_beams=num_beams,
            temperature=temperature
        )
        
        # Return response
        return jsonify({
            'code': generated_code,
            'language': language,
            'framework': framework,
            'task': task,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/batch-generate', methods=['POST'])
def batch_generate():
    """
    Generate code for multiple requests
    
    Request body:
    {
        "requests": [
            {
                "language": "csharp",
                "framework": "dotnet8",
                "task": "Task description",
                "context": "Optional context"
            },
            ...
        ]
    }
    
    Response:
    {
        "results": [
            {
                "code": "Generated code",
                "language": "csharp",
                "framework": "dotnet8",
                "task": "Task description"
            },
            ...
        ]
    }
    """
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        
        if 'requests' not in data:
            return jsonify({'error': 'Missing required field: requests'}), 400
        
        requests = data['requests']
        
        if not isinstance(requests, list):
            return jsonify({'error': 'requests must be a list'}), 400
        
        # Generate code for each request
        results = []
        for req in requests:
            try:
                code = model.generate(
                    language=req['language'],
                    framework=req['framework'],
                    task=req['task'],
                    context=req.get('context', '')
                )
                results.append({
                    'code': code,
                    'language': req['language'],
                    'framework': req['framework'],
                    'task': req['task']
                })
            except Exception as e:
                results.append({
                    'error': str(e),
                    'task': req.get('task', 'Unknown')
                })
        
        return jsonify({
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in batch generation: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/model-info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        info = model.get_model_info()
        return jsonify(info)
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Run the Flask app
    print("=" * 80)
    print("Coding Agent API Server")
    print("=" * 80)
    print(f"Model path: {MODEL_PATH}")
    print(f"Model loaded: {model is not None}")
    print("\nAvailable endpoints:")
    print("  GET  /health          - Health check")
    print("  POST /generate        - Generate code")
    print("  POST /batch-generate  - Batch generate code")
    print("  GET  /model-info      - Get model information")
    print("\nStarting server on http://localhost:5000")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

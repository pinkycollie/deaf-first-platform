"""
Main entry point for the ASL Model Training Hub Flask application
"""
from flask import Flask, jsonify, send_from_directory
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('asl_training_hub')

def create_app():
    """Create and configure the Flask application"""
    # Create the Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        OLLAMA_API=os.environ.get('OLLAMA_API', 'http://localhost:11434'),
        UPLOAD_FOLDER=os.path.abspath('./uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16 MB max upload size
    )
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from .routes.training import training_bp
    from .routes.models import models_bp
    from .routes.inference import inference_bp
    
    app.register_blueprint(training_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(inference_bp)
    
    # Add a health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "api_version": "0.1.0"
        })
    
    # Add a root endpoint with API documentation
    @app.route('/')
    def home():
        return jsonify({
            "name": "ASL Model Training Hub API",
            "version": "0.1.0",
            "description": "API for training and deploying ASL models with Ollama",
            "endpoints": [
                {"path": "/", "method": "GET", "description": "API documentation"},
                {"path": "/health", "method": "GET", "description": "Health check"},
                
                # Model Management
                {"path": "/models", "method": "GET", "description": "List available models"},
                {"path": "/models/recommended", "method": "GET", "description": "Get recommended ASL models"},
                {"path": "/models/search", "method": "GET", "description": "Search for models on Hugging Face"},
                {"path": "/models/download", "method": "POST", "description": "Download a model from Hugging Face"},
                {"path": "/models/export", "method": "POST", "description": "Export a model to Ollama"},
                {"path": "/models/start", "method": "POST", "description": "Start an Ollama model"},
                {"path": "/models/stop", "method": "POST", "description": "Stop an Ollama model"},
                
                # Training Management
                {"path": "/training/start", "method": "POST", "description": "Start model training"},
                {"path": "/training/status", "method": "GET", "description": "Check training status"},
                {"path": "/training/cancel", "method": "POST", "description": "Cancel training job"},
                {"path": "/training/logs", "method": "GET", "description": "Get training job logs"},
                {"path": "/training/customer-support", "method": "POST", "description": "Create a specialized customer support ASL model"},
                
                # Inference
                {"path": "/inference", "method": "POST", "description": "Run inference with text or image input"},
                {"path": "/inference/upload", "method": "POST", "description": "Upload an image for inference"}
            ]
        })
    
    # Serve static files
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(os.path.join(app.root_path, 'static'), filename)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

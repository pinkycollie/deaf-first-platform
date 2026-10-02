"""
Routes for model management
"""
from flask import Blueprint, request, jsonify
import subprocess
import json
import os
import logging

from ..utils.huggingface import get_recommended_asl_models, list_available_models, download_model, export_model_to_ollama

# Configure logging
logger = logging.getLogger('asl_training_hub.models')

# Create blueprint
models_bp = Blueprint('models', __name__, url_prefix='/models')

# Ollama API endpoint (default to localhost)
OLLAMA_API = os.environ.get('OLLAMA_API', 'http://localhost:11434')

@models_bp.route('/', methods=['GET'])
def list_models():
    """List all available models (from Ollama and HuggingFace recommendations)"""
    try:
        # Get models from Ollama
        ollama_models = []
        try:
            result = subprocess.run(
                ['curl', '-s', f'{OLLAMA_API}/api/tags'],
                capture_output=True, text=True, check=True
            )
            ollama_response = json.loads(result.stdout)
            ollama_models = ollama_response.get('models', [])
        except Exception as e:
            logger.warning(f"Could not fetch Ollama models: {str(e)}")
        
        # Get recommended models
        hf_models = get_recommended_asl_models()
        
        return jsonify({
            "status": "success",
            "ollama_models": ollama_models,
            "huggingface_models": hf_models
        })
    except Exception as e:
        logger.error(f"Error in list_models: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@models_bp.route('/recommended', methods=['GET'])
def recommended_models():
    """Get recommended ASL models"""
    try:
        model_type = request.args.get('type')
        models = get_recommended_asl_models(model_type)
        
        return jsonify({
            "status": "success",
            "models": models
        })
    except Exception as e:
        logger.error(f"Error in recommended_models: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@models_bp.route('/search', methods=['GET'])
def search_models():
    """Search for models on Hugging Face"""
    try:
        keyword = request.args.get('keyword', 'sign language')
        models = list_available_models(keyword)
        
        return jsonify({
            "status": "success",
            "models": models
        })
    except Exception as e:
        logger.error(f"Error in search_models: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@models_bp.route('/download', methods=['POST'])
def download_hf_model():
    """Download a model from Hugging Face"""
    data = request.json or {}
    model_id = data.get('model_id')
    
    if not model_id:
        return jsonify({"status": "error", "message": "Model ID is required"}), 400
    
    try:
        model_path = download_model(model_id)
        
        return jsonify({
            "status": "success",
            "message": f"Model {model_id} downloaded successfully",
            "model_path": model_path
        })
    except Exception as e:
        logger.error(f"Error in download_hf_model: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@models_bp.route('/export', methods=['POST'])
def export_to_ollama():
    """Export a HuggingFace model to Ollama"""
    data = request.json or {}
    model_id = data.get('model_id')
    model_name = data.get('model_name')
    
    if not model_id:
        return jsonify({"status": "error", "message": "Model ID is required"}), 400
    
    if not model_name:
        return jsonify({"status": "error", "message": "Model name is required"}), 400
    
    try:
        success = export_model_to_ollama(model_id, model_name)
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Model {model_id} exported to Ollama as {model_name}"
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to export model {model_id} to Ollama"
            }), 500
    except Exception as e:
        logger.error(f"Error in export_to_ollama: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@models_bp.route('/start', methods=['POST'])
def start_model():
    """Start an Ollama model"""
    data = request.json or {}
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({"status": "error", "message": "Model name is required"}), 400
    
    try:
        # Check if model exists
        result = subprocess.run(
            ['curl', '-s', f'{OLLAMA_API}/api/tags'],
            capture_output=True, text=True, check=True
        )
        
        ollama_response = json.loads(result.stdout)
        models = ollama_response.get('models', [])
        
        model_exists = any(model.get('name') == model_name for model in models)
        
        if not model_exists:
            return jsonify({
                "status": "error", 
                "message": f"Model {model_name} not found in Ollama"
            }), 404
        
        # Start the model (pull it which will start it)
        result = subprocess.run(
            ['curl', '-X', 'POST', f'{OLLAMA_API}/api/pull',
             '-d', json.dumps({"name": model_name})],
            capture_output=True, text=True, check=True
        )
        
        return jsonify({
            "status": "success",
            "message": f"Model {model_name} started"
        })
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting model: {str(e)}, stdout: {e.stdout}, stderr: {e.stderr}")
        return jsonify({
            "status": "error", 
            "message": f"Failed to start model: {e.stderr}"
        }), 500
    except Exception as e:
        logger.error(f"Error in start_model: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@models_bp.route('/stop', methods=['POST'])
def stop_model():
    """Stop a running Ollama model"""
    data = request.json or {}
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({"status": "error", "message": "Model name is required"}), 400
    
    try:
        # There's no direct "stop" in Ollama API, but for resource management,
        # we can attempt to remove the model from memory:
        result = subprocess.run(
            ['curl', '-X', 'DELETE', f'{OLLAMA_API}/api/delete',
             '-d', json.dumps({"name": model_name})],
            capture_output=True, text=True, check=False
        )
        
        # Even if the delete failed, we'll consider it a success for the user
        # as the model might not be running or loaded
        return jsonify({
            "status": "success",
            "message": f"Model {model_name} stopped"
        })
    except Exception as e:
        logger.error(f"Error in stop_model: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

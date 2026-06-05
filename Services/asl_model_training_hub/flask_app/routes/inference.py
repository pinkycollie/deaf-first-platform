"""
Routes for ASL inference and recognition
"""
from flask import Blueprint, request, jsonify
import os
import base64
import time
import logging
import json
import subprocess
import uuid
from werkzeug.utils import secure_filename

from ..utils.tensorflow_model import ASLModelInference

# Configure logging
logger = logging.getLogger('asl_training_hub.inference')

# Create blueprint
inference_bp = Blueprint('inference', __name__, url_prefix='/inference')

# Ollama API endpoint (default to localhost)
OLLAMA_API = os.environ.get('OLLAMA_API', 'http://localhost:11434')

# Create upload directory for temporary image storage
UPLOAD_DIR = os.path.abspath("./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@inference_bp.route('/', methods=['POST'])
def run_inference():
    """Run inference with a model"""
    data = request.json or {}
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
        
    model = data.get("model", "asl-model")
    prompt = data.get("prompt")
    image_data = data.get("image")  # Base64 encoded image data
    
    if not prompt and not image_data:
        return jsonify({"status": "error", "message": "Either prompt or image data is required"}), 400
    
    try:
        # Determine if we should use Ollama or local TensorFlow model
        use_ollama = data.get("use_ollama", True)
        
        if use_ollama:
            return run_ollama_inference(model, prompt, image_data)
        else:
            return run_tensorflow_inference(model, image_data)
            
    except Exception as e:
        logger.error(f"Error in run_inference: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def run_ollama_inference(model, prompt, image_data):
    """Run inference using Ollama"""
    try:
        # Construct the API call to Ollama
        payload = {
            "model": model,
            "prompt": prompt or "",
            "stream": False
        }
        
        # If image is provided, add it to the messages
        if image_data:
            payload["messages"] = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt or "Interpret this sign language image"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }
            ]
        
        # Call Ollama API
        result = subprocess.run(
            ['curl', '-X', 'POST', f'{OLLAMA_API}/api/generate', 
             '-d', json.dumps(payload)],
            capture_output=True, text=True, check=True
        )
        
        # Parse and return the response
        response = json.loads(result.stdout)
        return jsonify({
            "status": "success",
            "model": model,
            "response": response.get("response", ""),
            "metadata": {
                "total_duration": response.get("total_duration", 0),
                "load_duration": response.get("load_duration", 0),
                "prompt_eval_count": response.get("prompt_eval_count", 0),
                "eval_count": response.get("eval_count", 0),
                "eval_duration": response.get("eval_duration", 0)
            }
        })
    except subprocess.CalledProcessError as e:
        logger.error(f"Inference error: {str(e)}, stdout: {e.stdout}, stderr: {e.stderr}")
        return jsonify({
            "status": "error", 
            "message": f"Inference failed: {e.stderr}"
        }), 500
    except Exception as e:
        logger.error(f"Error in run_ollama_inference: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def run_tensorflow_inference(model_name, image_data):
    """Run inference using local TensorFlow model"""
    try:
        # Save base64 image to a temporary file
        image_filename = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(UPLOAD_DIR, image_filename)
        
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_data))
        
        # Find model path
        model_path = os.path.abspath(f"./models/{model_name}/{model_name}.h5")
        
        if not os.path.exists(model_path):
            return jsonify({
                "status": "error", 
                "message": f"Model {model_name} not found at {model_path}"
            }), 404
        
        # Create inference engine and run prediction
        inference_engine = ASLModelInference(model_path)
        result = inference_engine.predict(image_path)
        
        # Clean up temporary image
        try:
            os.remove(image_path)
        except:
            pass
        
        # Return prediction
        return jsonify({
            "status": "success",
            "model": model_name,
            "prediction": result.get("prediction"),
            "confidence": result.get("confidence"),
            "alternatives": result.get("top3"),
            "metadata": {
                "inference_time": result.get("inference_time")
            }
        })
    except ImportError as e:
        return jsonify({
            "status": "error", 
            "message": f"TensorFlow not installed: {str(e)}"
        }), 500
    except Exception as e:
        logger.error(f"Error in run_tensorflow_inference: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@inference_bp.route('/upload', methods=['POST'])
def upload_image():
    """Upload an image for inference"""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)
        
        # Get model name from request
        model_name = request.form.get('model', 'asl-model')
        use_ollama = request.form.get('use_ollama', 'true').lower() == 'true'
        
        try:
            # Read the image and convert to base64
            with open(filepath, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Run inference
            if use_ollama:
                prompt = request.form.get('prompt', 'Interpret this sign language image')
                result = run_ollama_inference(model_name, prompt, image_data)
            else:
                result = run_tensorflow_inference(model_name, image_data)
            
            # Clean up
            try:
                os.remove(filepath)
            except:
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing uploaded image: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

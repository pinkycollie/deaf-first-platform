from flask import Flask, request, jsonify, render_template
import subprocess
import os
import json
import time
import logging
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('asl_training_hub')

app = Flask(__name__)

# Store active tasks
active_tasks = {}

# Ollama API endpoint (default to localhost)
OLLAMA_API = os.environ.get('OLLAMA_API', 'http://localhost:11434')

@app.route('/')
def home():
    """Home page with API documentation"""
    return jsonify({
        "name": "ASL Model Training Hub API",
        "version": "0.1.0",
        "description": "API for training and deploying ASL models with Ollama",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "API documentation"},
            {"path": "/models", "method": "GET", "description": "List available models"},
            {"path": "/model/start", "method": "POST", "description": "Start a model"},
            {"path": "/model/stop", "method": "POST", "description": "Stop a model"},
            {"path": "/inference", "method": "POST", "description": "Run inference with a model"},
            {"path": "/training/start", "method": "POST", "description": "Start model training"},
            {"path": "/training/status", "method": "GET", "description": "Check training status"}
        ]
    })

@app.route('/models', methods=['GET'])
def list_models():
    """List all available models from Ollama"""
    try:
        result = subprocess.run(
            ['curl', f'{OLLAMA_API}/api/tags'],
            capture_output=True, text=True, check=True
        )
        return jsonify(json.loads(result.stdout))
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list models: {str(e)}")
        return jsonify({"status": "error", "message": f"Failed to list models: {str(e)}"}), 500
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid response from Ollama API"}), 500

@app.route('/model/start', methods=['POST'])
def start_model():
    """Start an Ollama model"""
    data = request.json or {}
    model_name = data.get("model", "asl-model")
    
    try:
        # Check if model exists
        check_result = subprocess.run(
            ['curl', '-s', f'{OLLAMA_API}/api/tags'],
            capture_output=True, text=True, check=True
        )
        models = json.loads(check_result.stdout).get('models', [])
        model_exists = any(model.get('name') == model_name for model in models)
        
        if not model_exists:
            # Try to pull the model
            subprocess.run(
                ['ollama', 'pull', model_name],
                capture_output=True, check=True
            )
        
        # Start the model
        subprocess.Popen(["ollama", "run", model_name])
        return jsonify({"status": "started", "model": model_name})
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start model {model_name}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        logger.error(f"Error in start_model: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/model/stop', methods=['POST'])
def stop_model():
    """Stop a running Ollama model"""
    data = request.json or {}
    model_name = data.get("model", "asl-model")
    
    try:
        subprocess.run(["pkill", "-f", f"ollama run {model_name}"])
        return jsonify({"status": "stopped", "model": model_name})
    except Exception as e:
        logger.error(f"Error in stop_model: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/inference', methods=['POST'])
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
        logger.error(f"Error in run_inference: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def run_training_job(task_id, model_name, training_data, params):
    """Training job to be run in a separate thread"""
    try:
        active_tasks[task_id]["status"] = "running"
        
        # Simulate training process (replace with actual Ollama training)
        logger.info(f"Starting training for model {model_name} with task ID {task_id}")
        
        # Example training steps
        steps = ["Preparing data", "Initializing model", "Training", "Saving model"]
        for i, step in enumerate(steps):
            active_tasks[task_id]["progress"] = (i + 1) / len(steps) * 100
            active_tasks[task_id]["current_step"] = step
            logger.info(f"Task {task_id}: {step} - {active_tasks[task_id]['progress']:.2f}%")
            time.sleep(2)  # Simulate work
        
        # Mark as completed
        active_tasks[task_id]["status"] = "completed"
        active_tasks[task_id]["progress"] = 100
        active_tasks[task_id]["result"] = {
            "model_name": model_name,
            "completed_at": time.time(),
            "metrics": {
                "accuracy": 0.85,
                "loss": 0.15
            }
        }
        logger.info(f"Task {task_id} completed")
    except Exception as e:
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = str(e)
        logger.error(f"Task {task_id} failed: {str(e)}")

@app.route('/training/start', methods=['POST'])
def start_training():
    """Start model training"""
    data = request.json or {}
    model_name = data.get("model_name", "asl-model")
    training_data = data.get("training_data", [])
    params = data.get("parameters", {})
    
    if not training_data:
        return jsonify({"status": "error", "message": "No training data provided"}), 400
    
    # Generate a task ID
    task_id = f"train_{int(time.time())}"
    
    # Initialize the task
    active_tasks[task_id] = {
        "id": task_id,
        "type": "training",
        "model_name": model_name,
        "status": "initializing",
        "created_at": time.time(),
        "progress": 0,
        "current_step": "Initializing"
    }
    
    # Start training in a separate thread
    Thread(
        target=run_training_job, 
        args=(task_id, model_name, training_data, params)
    ).start()
    
    return jsonify({
        "status": "started",
        "task_id": task_id,
        "model_name": model_name
    })

@app.route('/training/status', methods=['GET'])
def training_status():
    """Get status of training jobs"""
    task_id = request.args.get('task_id')
    
    if task_id:
        # Get specific task
        task = active_tasks.get(task_id)
        if not task:
            return jsonify({"status": "error", "message": f"Task {task_id} not found"}), 404
        return jsonify({"status": "success", "task": task})
    else:
        # List all tasks
        return jsonify({
            "status": "success",
            "tasks": list(active_tasks.values())
        })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    # Check Ollama availability
    try:
        result = subprocess.run(
            ['curl', '-s', f'{OLLAMA_API}/api/tags'],
            capture_output=True, text=True, check=False
        )
        ollama_available = result.returncode == 0
    except Exception:
        ollama_available = False
    
    return jsonify({
        "status": "healthy",
        "ollama_available": ollama_available,
        "api_version": "0.1.0"
    })

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Get or update configuration"""
    if request.method == 'POST':
        data = request.json or {}
        new_api_endpoint = data.get('ollama_api')
        
        if new_api_endpoint:
            global OLLAMA_API
            OLLAMA_API = new_api_endpoint
            return jsonify({
                "status": "success", 
                "message": "Configuration updated", 
                "ollama_api": OLLAMA_API
            })
        return jsonify({"status": "error", "message": "No configuration changes provided"}), 400
    else:
        return jsonify({
            "ollama_api": OLLAMA_API
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
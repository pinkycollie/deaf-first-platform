"""
Routes for training model management
"""
from flask import Blueprint, request, jsonify
from threading import Thread
import time
import logging
import os
import json

from ..models.training_job import job_manager, JobStatus
from ..utils.tensorflow_model import ASLModelTrainer, create_customer_support_model

# Configure logging
logger = logging.getLogger('asl_training_hub.training')

# Create blueprint
training_bp = Blueprint('training', __name__, url_prefix='/training')

def run_training_job(job_id):
    """Background thread for model training"""
    job = job_manager.get_job(job_id)
    if not job:
        logger.error(f"Job {job_id} not found")
        return
    
    try:
        # Start the job
        job.start()
        
        # Training parameters from job
        model_name = job.model_name
        dataset = job.dataset
        params = job.params
        
        # Check if this is a customer support model
        is_customer_support = params.get('model_type') == 'customer_support'
        
        job.update_progress(10, "Preparing dataset")
        
        # Ensure dataset path exists
        dataset_path = os.path.abspath(f"./data/{dataset}")
        if not os.path.exists(dataset_path):
            # For demo purposes, we'll just create a dummy path
            # In production, this would be a real dataset path
            os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
            
            # Log the issue but continue for demonstration
            job.log(f"Dataset path {dataset_path} not found. Using simulated training.")
        
        job.update_progress(20, "Initializing model")
        
        # Create a callback to update job progress
        class ProgressCallback:
            def __init__(self, job):
                self.job = job
                self.epoch = 0
                self.max_epochs = params.get('epochs', 10)
            
            def on_epoch_end(self, epoch, logs=None):
                self.epoch = epoch
                progress = 20 + (70 * (epoch + 1) / self.max_epochs)  # 20-90% during training
                self.job.update_progress(progress, f"Training - Epoch {epoch + 1}/{self.max_epochs}")
                
                # Log metrics
                if logs:
                    metrics_str = ", ".join([f"{k}: {v:.4f}" for k, v in logs.items()])
                    self.job.log(f"Epoch {epoch + 1} - {metrics_str}")
        
        # Create progress callback
        progress_callback = ProgressCallback(job)
        
        # Train the model
        try:
            if is_customer_support:
                job.log("Training specialized customer support ASL model")
                result = create_customer_support_model(model_name, dataset_path, params)
                metrics = result.get('metrics', {})
            else:
                job.log("Training standard ASL recognition model")
                trainer = ASLModelTrainer(model_name, dataset_path, params)
                metrics = trainer.train_model(callbacks=[progress_callback])
            
            job.update_progress(90, "Saving model")
            
            # Export to Ollama if requested
            if params.get('export_to_ollama', False):
                job.update_progress(95, "Exporting to Ollama")
                if is_customer_support:
                    export_success = result.get('exported_to_ollama', False)
                else:
                    trainer = ASLModelTrainer(model_name, dataset_path, params)
                    export_success = trainer.export_to_ollama()
                
                if export_success:
                    job.log("Model successfully exported to Ollama")
                else:
                    job.log("Failed to export model to Ollama")
            
            # Complete the job with metrics
            job.complete(metrics)
            
        except ImportError as e:
            job.log(f"Missing dependency: {str(e)}")
            job.log("Note: TensorFlow is required for model training.")
            job.fail(f"Missing dependency: {str(e)}")
        except Exception as e:
            job.log(f"Error during training: {str(e)}")
            job.fail(str(e))
            
    except Exception as e:
        logger.error(f"Error in training job {job_id}: {str(e)}")
        job.fail(str(e))

@training_bp.route('/start', methods=['POST'])
def start_training():
    """Start a new training job"""
    data = request.json or {}
    model_name = data.get("model_name", "asl-model")
    dataset = data.get("dataset", "sign-language-mnist")
    params = data.get("parameters", {})
    
    if not model_name:
        return jsonify({"status": "error", "message": "Model name is required"}), 400
    
    if not dataset:
        return jsonify({"status": "error", "message": "Dataset is required"}), 400
    
    # Create and initialize the job
    job = job_manager.create_job(model_name, dataset, params)
    
    # Start training in a background thread
    Thread(target=run_training_job, args=(job.id,)).start()
    
    return jsonify({
        "status": "success",
        "message": "Training job started",
        "job_id": job.id,
        "job": job.to_dict()
    })

@training_bp.route('/status', methods=['GET'])
def training_status():
    """Get the status of training jobs"""
    job_id = request.args.get('job_id')
    
    if job_id:
        # Get specific job
        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({"status": "error", "message": f"Job {job_id} not found"}), 404
        
        return jsonify({
            "status": "success",
            "job": job.to_dict()
        })
    else:
        # List all jobs
        jobs = job_manager.list_jobs()
        return jsonify({
            "status": "success",
            "jobs": [job.to_dict() for job in jobs]
        })

@training_bp.route('/cancel', methods=['POST'])
def cancel_training():
    """Cancel a training job"""
    data = request.json or {}
    job_id = data.get("job_id")
    
    if not job_id:
        return jsonify({"status": "error", "message": "Job ID is required"}), 400
    
    success = job_manager.cancel_job(job_id)
    if success:
        return jsonify({
            "status": "success",
            "message": f"Job {job_id} cancelled"
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"Could not cancel job {job_id}"
        }), 400

@training_bp.route('/logs', methods=['GET'])
def training_logs():
    """Get logs for a training job"""
    job_id = request.args.get('job_id')
    
    if not job_id:
        return jsonify({"status": "error", "message": "Job ID is required"}), 400
    
    job = job_manager.get_job(job_id)
    if not job:
        return jsonify({"status": "error", "message": f"Job {job_id} not found"}), 404
    
    try:
        with open(job.log_file, 'r') as f:
            logs = f.readlines()
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "logs": logs
        })
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "message": f"Log file for job {job_id} not found"
        }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error reading logs: {str(e)}"
        }), 500

@training_bp.route('/customer-support', methods=['POST'])
def create_customer_support():
    """Create a specialized customer support ASL model"""
    data = request.json or {}
    model_name = data.get("model_name", "asl-customer-support")
    dataset = data.get("dataset")
    params = data.get("parameters", {})
    
    # Add customer support model type
    params['model_type'] = 'customer_support'
    
    # Create and initialize the job
    job = job_manager.create_job(model_name, dataset or "customer-support-asl", params)
    
    # Start training in a background thread
    Thread(target=run_training_job, args=(job.id,)).start()
    
    return jsonify({
        "status": "success",
        "message": "Customer support model training started",
        "job_id": job.id,
        "job": job.to_dict()
    })

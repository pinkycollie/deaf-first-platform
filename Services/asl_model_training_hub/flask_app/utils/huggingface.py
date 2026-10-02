"""
Utility functions for working with Hugging Face models and datasets
"""
import os
import logging
import json
import time
from typing import List, Dict, Any, Optional

# Configure logging
logger = logging.getLogger('asl_training_hub.huggingface')

# Hugging Face API token (if available)
HF_TOKEN = os.environ.get('HF_TOKEN')

# Directory for downloaded models and datasets
MODELS_DIR = os.path.abspath("./models")
DATASETS_DIR = os.path.abspath("./data")

# Create directories if they don't exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATASETS_DIR, exist_ok=True)

# Curated list of recommended ASL models
RECOMMENDED_ASL_MODELS = [
    {
        "id": "RavenOnur/Sign-Language",
        "name": "Sign-Language",
        "description": "Image classification model trained to recognize ASL letters A to Z.",
        "type": "image-classification",
        "task": "asl-recognition",
        "url": "https://huggingface.co/RavenOnur/Sign-Language",
    },
    {
        "id": "Heem2/sign-language-classification",
        "name": "sign-language-classification",
        "description": "Fine-tuned version of Google's ViT model for ASL classification.",
        "type": "image-classification",
        "task": "asl-recognition",
        "url": "https://huggingface.co/Heem2/sign-language-classification",
    },
    {
        "id": "atalaydenknalbant/asl-yolo-models",
        "name": "asl-yolo-models",
        "description": "YOLOv8 models trained to identify ASL letters A to Y (excluding J and Z).",
        "type": "object-detection",
        "task": "asl-detection",
        "url": "https://huggingface.co/atalaydenknalbant/asl-yolo-models",
    },
    {
        "id": "Niharmahesh/Sign_language_recognition_v1",
        "name": "Sign_language_recognition_v1",
        "description": "ASL recognition model utilizing hand landmark detection and machine learning.",
        "type": "multimodal",
        "task": "asl-recognition",
        "url": "https://huggingface.co/Niharmahesh/Sign_language_recognition_v1",
    },
    {
        "id": "sayakpaul/convnext-tiny-finetuned-sign-mnist",
        "name": "ConvNeXt-Tiny ASL",
        "description": "ConvNeXt-Tiny model fine-tuned on the Sign MNIST dataset for ASL digit recognition.",
        "type": "image-classification",
        "task": "asl-recognition",
        "url": "https://huggingface.co/sayakpaul/convnext-tiny-finetuned-sign-mnist",
    }
]

# Curated list of recommended ASL datasets
RECOMMENDED_ASL_DATASETS = [
    {
        "id": "sign-language-mnist",
        "name": "Sign Language MNIST",
        "description": "MNIST-like dataset of hand gestures representing the ASL alphabet.",
        "type": "image-classification",
        "task": "asl-recognition",
        "url": "https://huggingface.co/datasets/sign-language-mnist",
    },
    {
        "id": "robertgove/asl-fingerspelling",
        "name": "ASL Fingerspelling",
        "description": "Dataset of videos of people using American Sign Language (ASL) fingerspelling.",
        "type": "video-classification",
        "task": "asl-fingerspelling",
        "url": "https://huggingface.co/datasets/robertgove/asl-fingerspelling",
    },
    {
        "id": "NVIDIA/MSASL",
        "name": "MS-ASL",
        "description": "Large-scale, American Sign Language (ASL) video dataset collected from YouTube.",
        "type": "video-classification",
        "task": "asl-translation",
        "url": "https://huggingface.co/datasets/NVIDIA/MSASL",
    }
]

def list_available_datasets(keyword: str = "sign language") -> List[Dict[str, Any]]:
    """
    List datasets available from Hugging Face that match the keyword
    
    Args:
        keyword: Search term for datasets
        
    Returns:
        List of dataset information dictionaries
    """
    try:
        # In a real implementation, this would use the Hugging Face API or huggingface_hub library
        # For simplicity, we'll just return the curated list for now
        logger.info(f"Listing datasets matching '{keyword}'")
        
        # For demo, just return recommended datasets
        datasets = RECOMMENDED_ASL_DATASETS
        
        logger.info(f"Found {len(datasets)} datasets matching '{keyword}'")
        
        return datasets
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        return []

def download_dataset(dataset_id: str, subset: Optional[str] = None) -> str:
    """
    Download a dataset from Hugging Face
    
    Args:
        dataset_id: ID of the dataset on Hugging Face
        subset: Optional subset/config name
        
    Returns:
        Path to the downloaded dataset
    """
    try:
        # In a real implementation, this would use the huggingface_hub or datasets library
        # For now, just create a directory and simulate the download
        logger.info(f"Downloading dataset {dataset_id}")
        
        # Create a directory for the dataset
        dataset_dir = os.path.join(DATASETS_DIR, dataset_id.split('/')[-1])
        os.makedirs(dataset_dir, exist_ok=True)
        
        # Create a metadata file
        metadata = {
            "id": dataset_id,
            "subset": subset,
            "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "download_status": "completed"
        }
        
        with open(os.path.join(dataset_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Dataset {dataset_id} downloaded to {dataset_dir}")
        
        return dataset_dir
    except Exception as e:
        logger.error(f"Error downloading dataset: {str(e)}")
        raise Exception(f"Failed to download dataset: {str(e)}")

def get_recommended_asl_models(model_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get recommended ASL models from the curated list
    
    Args:
        model_type: Optional filter by model type (image-classification, object-detection, multimodal)
        
    Returns:
        List of recommended model information dictionaries
    """
    try:
        logger.info(f"Getting recommended ASL models (type={model_type})")
        
        if model_type:
            # Filter by model type
            models = [model for model in RECOMMENDED_ASL_MODELS if model.get('type') == model_type]
        else:
            # Return all
            models = RECOMMENDED_ASL_MODELS
        
        logger.info(f"Found {len(models)} recommended models")
        
        return models
    except Exception as e:
        logger.error(f"Error getting recommended models: {str(e)}")
        return []

def list_available_models(keyword: str = "sign language") -> List[Dict[str, Any]]:
    """
    List models available from Hugging Face that match the keyword
    
    Args:
        keyword: Search term for models
        
    Returns:
        List of model information dictionaries
    """
    try:
        # In a real implementation, this would use the Hugging Face API or huggingface_hub library
        # For simplicity, we'll just return the curated list for now
        logger.info(f"Listing models matching '{keyword}'")
        
        # For demo, just return recommended models
        models = RECOMMENDED_ASL_MODELS
        
        logger.info(f"Found {len(models)} models matching '{keyword}'")
        
        return models
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return []

def download_model(model_id: str) -> str:
    """
    Download a model from Hugging Face
    
    Args:
        model_id: ID of the model on Hugging Face
        
    Returns:
        Path to the downloaded model
    """
    try:
        # In a real implementation, this would use the huggingface_hub or transformers library
        # For now, just create a directory and simulate the download
        logger.info(f"Downloading model {model_id}")
        
        # Create a directory for the model
        model_name = model_id.split('/')[-1]
        model_dir = os.path.join(MODELS_DIR, model_name)
        os.makedirs(model_dir, exist_ok=True)
        
        # Create a metadata file
        metadata = {
            "id": model_id,
            "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "download_status": "completed"
        }
        
        with open(os.path.join(model_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Create a mock model file
        with open(os.path.join(model_dir, f"{model_name}.bin"), "w") as f:
            f.write("This is a placeholder for the model file")
        
        logger.info(f"Model {model_id} downloaded to {model_dir}")
        
        return model_dir
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        raise Exception(f"Failed to download model: {str(e)}")

def export_model_to_ollama(model_id: str, model_name: str) -> bool:
    """
    Export a Hugging Face model to Ollama format
    
    Args:
        model_id: ID of the model on Hugging Face
        model_name: Name to use for the Ollama model
        
    Returns:
        Success status
    """
    try:
        # In a real implementation, this would convert the model to Ollama format
        # For now, just create a modelfile
        logger.info(f"Exporting model {model_id} to Ollama as {model_name}")
        
        # Download the model if it doesn't already exist
        model_dir = os.path.join(MODELS_DIR, model_id.split('/')[-1])
        if not os.path.exists(model_dir):
            model_dir = download_model(model_id)
        
        # Create a Modelfile for Ollama
        modelfile_path = os.path.join(model_dir, "Modelfile")
        with open(modelfile_path, "w") as f:
            f.write(f"""
FROM llama2
TEMPLATE "{{.System}}\n\n{{.Prompt}}"
SYSTEM "This is an ASL (American Sign Language) recognition model named {model_name}, originally from {model_id}. It can recognize sign language from images."
PARAMETER stop "<|im_end|>"
PARAMETER temperature 0.7
PARAMETER seed 42
            """)
        
        logger.info(f"Created Modelfile at {modelfile_path}")
        
        # In a real implementation, we would execute:
        # ollama create {model_name} -f {modelfile_path}
        # For now, just log a success message
        logger.info(f"Model {model_id} successfully exported to Ollama as {model_name}")
        
        return True
    except Exception as e:
        logger.error(f"Error exporting model to Ollama: {str(e)}")
        return False

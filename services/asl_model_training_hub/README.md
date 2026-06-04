# ASL Model Training Hub

A powerful API for managing, training, and deploying American Sign Language (ASL) recognition models with Ollama integration.

## Features

- Browse and search recommended ASL models from Hugging Face
- Easily download and prepare models for ASL recognition
- Train and fine-tune models on custom ASL datasets
- Deploy models locally with Ollama for efficient inference
- Specialized support for customer service ASL recognition
- Real-time sign language interpretation via API

## Supported ASL Models

The hub includes direct integration with top ASL recognition models:

1. **Sign-Language by RavenOnur**: Image classification model trained to recognize ASL letters A to Z.
2. **sign-language-classification by Heem2**: A fine-tuned version of Google's ViT model, achieving high accuracy in ASL classification.
3. **asl-yolo-models by atalaydenknalbant**: Object detection models trained to identify ASL letters A to Y (excluding J and Z).
4. **Sign_language_recognition_v1 by Niharmahesh**: Utilizes hand landmark detection and machine learning for ASL recognition.
5. **Sign Language Translator (SLT-AI)**: A Python library and framework for building custom translators between Sign Language and Text.

## Customer Support Integration

The ASL Model Training Hub now supports specialized models for customer service applications:

- Enhanced vocabulary for common customer support terms
- Optimized for customer service interactions
- Dedicated API endpoints for customer support models
- Seamless integration with existing support platforms

## API Endpoints

### Main Endpoints
- `GET /`: API documentation
- `GET /health`: Health check

### Model Management
- `GET /models`: List available models (both from Ollama and Hugging Face)
- `GET /models/recommended`: Get recommended ASL models
- `GET /models/search`: Search for models on Hugging Face
- `POST /models/download`: Download a model from Hugging Face
- `POST /models/export`: Export a model to Ollama
- `POST /models/start`: Start an Ollama model
- `POST /models/stop`: Stop an Ollama model

### Training Management
- `POST /training/start`: Start model training
- `GET /training/status`: Check training status
- `POST /training/cancel`: Cancel training job
- `GET /training/logs`: Get training job logs
- `POST /training/customer-support`: Create a specialized customer support ASL model

### Inference
- `POST /inference`: Run inference with text or image input
- `POST /inference/upload`: Upload an image for inference

## Getting Started

1. Clone this repository
2. Install required dependencies
3. Make sure Ollama is installed and running
4. Run the application:
   ```
   python run.py
   ```

## Dependencies

- Flask
- TensorFlow & Keras for model training and inference
- OpenCV for image processing
- Hugging Face transformers and datasets libraries
- Ollama (for local model execution)

## Configuration

Environment variables:
- `OLLAMA_API`: URL for the Ollama API (default: http://localhost:11434)
- `SECRET_KEY`: Secret key for Flask (default: dev)

## License

MIT

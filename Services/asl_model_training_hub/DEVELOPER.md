# ASL Model Training Hub - Developer Documentation

This document provides technical details for developers working on the ASL Model Training Hub.

## Architecture

The ASL Model Training Hub follows a modular design with the following components:

```
asl_model_training_hub/
├── flask_app/             # Main Flask application
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Application creation and configuration
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   └── training_job.py # Training job management
│   ├── routes/            # API routes
│   │   ├── __init__.py
│   │   ├── inference.py   # Inference endpoints
│   │   ├── models.py      # Model management
│   │   └── training.py    # Training endpoints
│   └── utils/             # Utility functions
│       ├── __init__.py
│       ├── huggingface.py # HuggingFace integration
│       └── tensorflow_model.py # TensorFlow model management
├── data/                  # Dataset storage
├── logs/                  # Log files
├── models/                # Model storage
├── uploads/               # Temporary upload storage
├── README.md              # Project documentation
└── run.py                 # Application entry point
```

## Core Components

### Flask API Server

The Flask server provides RESTful endpoints for model management, training, and inference.

- **Main Entry Point**: `run.py` creates and runs the Flask application
- **API Routes**: Defined in the `flask_app/routes/` directory
- **Data Models**: Defined in the `flask_app/models/` directory
- **Utilities**: Helper functions in the `flask_app/utils/` directory

### Training Job Management

Training jobs are managed through the `JobManager` class in `flask_app/models/training_job.py`:

- Jobs have unique IDs and statuses (INITIALIZING, QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED)
- Progress, logs, and metrics are tracked for each job
- Background threads handle the actual training process

### Model Integration

Models are sourced from:

1. **HuggingFace**: Pre-trained models can be downloaded and used
2. **Local TensorFlow Models**: Custom ASL models trained within the hub
3. **Ollama**: Local LLM deployment for inference

### TensorFlow Model Management

The TensorFlow utilities in `flask_app/utils/tensorflow_model.py` provide:

- ASL model creation and training
- Image preprocessing
- Inference capabilities
- Model export to Ollama

## API Reference

### Model Management Endpoints

- `GET /models`: List available models
- `GET /models/recommended`: Get recommended ASL models
- `GET /models/search`: Search for models on HuggingFace
- `POST /models/download`: Download a model from HuggingFace
- `POST /models/export`: Export a model to Ollama
- `POST /models/start`: Start an Ollama model
- `POST /models/stop`: Stop an Ollama model

### Training Endpoints

- `POST /training/start`: Start model training
- `GET /training/status`: Check training status
- `POST /training/cancel`: Cancel training job
- `GET /training/logs`: Get training job logs
- `POST /training/customer-support`: Create a specialized customer support ASL model

### Inference Endpoints

- `POST /inference`: Run inference with text or image input
- `POST /inference/upload`: Upload an image for inference

## Development Workflow

### Setting Up the Environment

1. Clone the repository
2. Install dependencies
3. Install Ollama if using local LLM capabilities
4. Run the Flask application with `python run.py`

### Adding a New Endpoint

1. Create a new route function in the appropriate route file
2. Add the endpoint to the API documentation in `main.py`
3. Update the README.md with the new endpoint details
4. Write tests for the new endpoint

### Adding a New Model Type

1. Add the model details to the `RECOMMENDED_ASL_MODELS` list in `huggingface.py`
2. Implement model-specific training logic in `tensorflow_model.py`
3. Add inference support in the `inference.py` routes

## Automated Documentation

The API documentation is automatically generated from the endpoint definitions in `main.py`. When adding new endpoints, make sure to:

1. Add the endpoint with accurate method, path, and description
2. Include the endpoint in the README.md
3. Add detailed parameter documentation in the function docstring

## Continuous Integration

The project uses GitHub Actions for continuous integration:

1. **Linting**: flake8 for Python code quality checks
2. **Testing**: pytest for running the test suite
3. **Documentation**: Automated generation and deployment of API docs
4. **Deployment**: Automated deployment to staging environments

## Performance Considerations

- Use background threads for long-running operations like training
- Implement proper error handling and job status tracking
- Consider using a task queue (like Celery) for production deployments
- Implement proper caching for frequently requested data

## Security Notes

- API keys and secrets should be stored as environment variables
- Implement proper request validation
- Set up CORS correctly for production
- Implement rate limiting for public endpoints

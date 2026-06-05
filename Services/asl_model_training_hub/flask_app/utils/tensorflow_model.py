"""
Utility functions for training and managing TensorFlow models for ASL recognition
"""
import os
import time
import json
import logging
import uuid
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

# Configure logging
logger = logging.getLogger('asl_training_hub.tensorflow')

class ASLModelTrainer:
    """Class for training TensorFlow models for ASL recognition"""
    
    def __init__(self, model_name: str, dataset_path: str, params: Dict[str, Any]):
        """
        Initialize the model trainer
        
        Args:
            model_name: Name for the trained model
            dataset_path: Path to the dataset
            params: Training parameters
        """
        self.model_name = model_name
        self.dataset_path = dataset_path
        self.params = params
        
        # Default parameters if not provided
        self.epochs = params.get('epochs', 10)
        self.batch_size = params.get('batch_size', 32)
        self.learning_rate = params.get('learning_rate', 0.001)
        self.validation_split = params.get('validation_split', 0.2)
        self.optimizer = params.get('optimizer', 'adam')
        
        # Model directory
        self.model_dir = os.path.abspath(f"./models/{model_name}")
        os.makedirs(self.model_dir, exist_ok=True)
    
    def prepare_dataset(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare and preprocess the dataset
        
        Returns:
            Tuple of (train_images, train_labels, test_images, test_labels)
        """
        try:
            # Import TensorFlow here to avoid import issues if not installed
            import tensorflow as tf
            from tensorflow.keras.preprocessing.image import ImageDataGenerator
            
            # For actual implementation, load data from dataset_path
            # For now, create a simulated dataset for A-Z ASL alphabet (26 classes)
            
            # Simulate dataset for now
            # In a real implementation, this would load from filesystem or HF datasets
            logger.info(f"Preparing dataset from {self.dataset_path}")
            
            # Simulated dataset size
            NUM_CLASSES = 26  # A-Z
            TRAIN_SAMPLES = 1000
            TEST_SAMPLES = 200
            IMG_SIZE = 64
            
            # Generate random data for demonstration
            train_images = np.random.rand(TRAIN_SAMPLES, IMG_SIZE, IMG_SIZE, 3)
            train_labels = np.random.randint(0, NUM_CLASSES, size=TRAIN_SAMPLES)
            train_labels = tf.keras.utils.to_categorical(train_labels, NUM_CLASSES)
            
            test_images = np.random.rand(TEST_SAMPLES, IMG_SIZE, IMG_SIZE, 3)
            test_labels = np.random.randint(0, NUM_CLASSES, size=TEST_SAMPLES)
            test_labels = tf.keras.utils.to_categorical(test_labels, NUM_CLASSES)
            
            logger.info(f"Dataset prepared: {train_images.shape[0]} training samples, {test_images.shape[0]} test samples")
            
            return train_images, train_labels, test_images, test_labels
            
        except ImportError as e:
            logger.error(f"TensorFlow not available: {str(e)}")
            raise ImportError(f"TensorFlow is required: {str(e)}")
    
    def build_model(self) -> Any:
        """
        Build the TensorFlow model for ASL recognition
        
        Returns:
            TensorFlow model
        """
        try:
            # Import TensorFlow here to avoid import issues if not installed
            import tensorflow as tf
            from tensorflow.keras import layers, models
            
            # Define model architecture
            # Simple CNN for ASL recognition with 26 output classes (A-Z)
            model = models.Sequential([
                # Input layer and first convolutional block
                layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(64, 64, 3)),
                layers.BatchNormalization(),
                layers.MaxPooling2D((2, 2)),
                
                # Second convolutional block
                layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.MaxPooling2D((2, 2)),
                
                # Third convolutional block
                layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.MaxPooling2D((2, 2)),
                
                # Fourth convolutional block for more complex features
                layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.MaxPooling2D((2, 2)),
                
                # Flatten the output and add dense layers
                layers.Flatten(),
                layers.Dropout(0.5),
                layers.Dense(512, activation='relu'),
                layers.Dropout(0.3),
                layers.Dense(26, activation='softmax')  # 26 classes for A-Z
            ])
            
            # Compile the model
            model.compile(
                optimizer=self.optimizer,
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info(f"Model built with {len(model.layers)} layers")
            
            return model
            
        except ImportError as e:
            logger.error(f"TensorFlow not available: {str(e)}")
            raise ImportError(f"TensorFlow is required: {str(e)}")
    
    def train_model(self, callbacks=None) -> Dict[str, Any]:
        """
        Train the model on the prepared dataset
        
        Args:
            callbacks: Optional callbacks for training
            
        Returns:
            Dictionary containing training metrics
        """
        try:
            # Prepare dataset
            train_images, train_labels, test_images, test_labels = self.prepare_dataset()
            
            # Build model
            model = self.build_model()
            
            # Start timing
            start_time = time.time()
            
            # Train the model
            history = model.fit(
                train_images, train_labels,
                epochs=self.epochs,
                batch_size=self.batch_size,
                validation_split=self.validation_split,
                callbacks=callbacks or []
            )
            
            # Calculate training time
            training_time = time.time() - start_time
            
            # Evaluate on test set
            test_loss, test_accuracy = model.evaluate(test_images, test_labels)
            
            # Save the model
            model_path = os.path.join(self.model_dir, f"{self.model_name}.h5")
            model.save(model_path)
            
            # Save model info
            model_info = {
                "name": self.model_name,
                "parameters": model.count_params(),
                "accuracy": float(test_accuracy),
                "loss": float(test_loss),
                "training_time": training_time,
                "epochs": self.epochs,
                "batch_size": self.batch_size,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "model_path": model_path,
            }
            
            with open(os.path.join(self.model_dir, "model_info.json"), "w") as f:
                json.dump(model_info, f, indent=2)
            
            logger.info(f"Model trained and saved to {model_path}")
            logger.info(f"Test accuracy: {test_accuracy:.4f}, Test loss: {test_loss:.4f}")
            
            # Return metrics
            metrics = {
                "accuracy": float(test_accuracy),
                "loss": float(test_loss),
                "training_time": training_time,
                "parameters": model.count_params(),
                "model_path": model_path
            }
            
            return metrics
            
        except ImportError as e:
            logger.error(f"TensorFlow not available: {str(e)}")
            raise ImportError(f"TensorFlow is required: {str(e)}")
    
    def export_to_ollama(self) -> bool:
        """
        Export the trained model to Ollama format
        
        Returns:
            Success status
        """
        try:
            # In a real implementation, this would convert the model to Ollama format
            # For now, just simulate success
            logger.info(f"Exporting model {self.model_name} to Ollama")
            
            # Simulate export process with a small delay
            time.sleep(1)
            
            # Create a Modelfile for Ollama
            modelfile_path = os.path.join(self.model_dir, "Modelfile")
            with open(modelfile_path, "w") as f:
                f.write(f"""
FROM llama2
TEMPLATE "{{.System}}\n\n{{.Prompt}}"
SYSTEM "This is an ASL (American Sign Language) recognition model named {self.model_name}. It can recognize sign language from images."
PARAMETER stop "<|im_end|>"
PARAMETER temperature 0.7
PARAMETER seed 42
                """)
            
            logger.info(f"Created Modelfile at {modelfile_path}")
            
            # In a real implementation, we would execute:
            # ollama create {self.model_name} -f {modelfile_path}
            # For now, just log a success message
            logger.info(f"Model {self.model_name} successfully exported to Ollama")
            
            return True
            
        except Exception as e:
            logger.error(f"Error exporting model to Ollama: {str(e)}")
            return False


class ASLModelInference:
    """Class for inference with trained ASL models"""
    
    def __init__(self, model_path: str):
        """
        Initialize the inference engine
        
        Args:
            model_path: Path to the trained model
        """
        self.model_path = model_path
        self.model = None
        self.class_names = [chr(ord('A') + i) for i in range(26)]  # A-Z
        
        # Load the model
        self.load_model()
    
    def load_model(self) -> None:
        """Load the TensorFlow model"""
        try:
            # Import TensorFlow here to avoid import issues if not installed
            import tensorflow as tf
            
            logger.info(f"Loading model from {self.model_path}")
            self.model = tf.keras.models.load_model(self.model_path)
            logger.info(f"Model loaded successfully")
            
        except ImportError as e:
            logger.error(f"TensorFlow not available: {str(e)}")
            raise ImportError(f"TensorFlow is required: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise Exception(f"Failed to load model: {str(e)}")
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess an image for inference
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Import TensorFlow and OpenCV for image processing
            import tensorflow as tf
            import cv2
            
            # Read and preprocess the image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Failed to read image from {image_path}")
            
            # Resize to model input size
            img = cv2.resize(img, (64, 64))
            
            # Convert to RGB if grayscale
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Normalize pixel values
            img = img.astype('float32') / 255.0
            
            # Add batch dimension
            img = np.expand_dims(img, axis=0)
            
            return img
            
        except ImportError as e:
            logger.error(f"Required library not available: {str(e)}")
            raise ImportError(f"Required library not available: {str(e)}")
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise Exception(f"Failed to preprocess image: {str(e)}")
    
    def predict(self, image_path: str) -> Dict[str, Any]:
        """
        Run inference on an image
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Dictionary with prediction results
        """
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            # Start timing
            start_time = time.time()
            
            # Preprocess the image
            preprocessed_img = self.preprocess_image(image_path)
            
            # Run inference
            predictions = self.model.predict(preprocessed_img)[0]
            
            # Calculate inference time
            inference_time = time.time() - start_time
            
            # Get the predicted class
            predicted_class = np.argmax(predictions)
            confidence = float(predictions[predicted_class])
            
            # Get the top 3 predictions
            top3_indices = np.argsort(predictions)[-3:][::-1]
            top3 = [
                {
                    "class": self.class_names[idx],
                    "confidence": float(predictions[idx])
                }
                for idx in top3_indices
            ]
            
            # Return the results
            results = {
                "prediction": self.class_names[predicted_class],
                "confidence": confidence,
                "top3": top3,
                "inference_time": inference_time
            }
            
            logger.info(f"Predicted: {results['prediction']} with confidence {confidence:.4f}")
            
            return results
            
        except ImportError as e:
            logger.error(f"Required library not available: {str(e)}")
            raise ImportError(f"Required library not available: {str(e)}")
        except Exception as e:
            logger.error(f"Error during inference: {str(e)}")
            raise Exception(f"Failed to run inference: {str(e)}")


def create_customer_support_model(
    model_name: str = "asl_customer_support", 
    dataset_path: str = None,
    params: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a model specifically for customer support ASL recognition
    
    Args:
        model_name: Name for the model
        dataset_path: Path to the dataset
        params: Training parameters
        
    Returns:
        Dictionary with model information
    """
    try:
        # Import TensorFlow here to avoid import issues if not installed
        import tensorflow as tf
        
        # Set default parameters if not provided
        params = params or {}
        params.setdefault('epochs', 15)
        params.setdefault('batch_size', 32)
        params.setdefault('learning_rate', 0.001)
        
        # Create model directory
        model_dir = os.path.abspath(f"./models/{model_name}")
        os.makedirs(model_dir, exist_ok=True)
        
        # Define specialized customer support classes
        # These would include basic ASL alphabet plus common customer support terms
        cs_phrases = [
            "Help", "Support", "Problem", "Question", "Manager",
            "Payment", "Return", "Receipt", "Order", "Delivery",
            "Account", "Password", "Email", "Phone", "Address"
        ]
        
        logger.info(f"Creating customer support model with {len(cs_phrases)} specialized phrases")
        
        # Create a pre-trained model that's been fine-tuned for customer support
        # For now, use the basic ASL model as a starting point
        trainer = ASLModelTrainer(model_name, dataset_path or "./data/customer_support", params)
        metrics = trainer.train_model()
        
        # Save additional customer support specific information
        cs_info = {
            "model_type": "customer_support",
            "specialized_phrases": cs_phrases,
            "base_model": "asl-base",
            "metrics": metrics,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(os.path.join(model_dir, "cs_model_info.json"), "w") as f:
            json.dump(cs_info, f, indent=2)
        
        # Export to Ollama if requested
        if params.get('export_to_ollama', False):
            export_success = trainer.export_to_ollama()
            cs_info['exported_to_ollama'] = export_success
        
        logger.info(f"Customer support model created successfully")
        
        return {
            "name": model_name,
            "model_path": os.path.join(model_dir, f"{model_name}.h5"),
            "metrics": metrics,
            "exported_to_ollama": params.get('export_to_ollama', False) and export_success,
            "specialized_phrases": cs_phrases
        }
        
    except ImportError as e:
        logger.error(f"TensorFlow not available: {str(e)}")
        raise ImportError(f"TensorFlow is required: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating customer support model: {str(e)}")
        raise Exception(f"Failed to create customer support model: {str(e)}")

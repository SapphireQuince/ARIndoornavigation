import os
import json
import numpy as np
import cv2
from PIL import Image

# Gracefully handle missing TensorFlow
try:
    import tensorflow as tf
except ImportError:
    tf = None
    print("TensorFlow not installed. H5 and TFLite models will be bypassed.")

class ModelHandler:
    def __init__(self, model_path='models'):
        self.model_path = model_path
        self.model = None
        self.labels = {}
        self.model_type = None
        
        # Try to load the best available model
        self.load_model()
        self.load_labels()
        
    def load_model(self):
        """Load the best available model format"""
        try:
            # Try H5 model first (only if TensorFlow is installed)
            h5_path = os.path.join(self.model_path, 'Indoor_model.h5')
            if os.path.exists(h5_path) and tf is not None:
                self.model = tf.keras.models.load_model(h5_path)
                self.model_type = 'h5'
                print(f"Successfully loaded H5 model from {h5_path}")
                return
            
            # Try TensorFlow Lite model (only if TensorFlow is installed)
            tflite_path = os.path.join(self.model_path, 'Indoor_model.tflite')
            if os.path.exists(tflite_path) and tf is not None:
                self.model = tf.lite.Interpreter(model_path=tflite_path)
                self.model.allocate_tensors()
                self.model_type = 'tflite'
                print(f"Successfully loaded TFLite model from {tflite_path}")
                return
            
            # Try ONNX model (requires onnxruntime)
            try:
                import onnxruntime as ort
                onnx_path = os.path.join(self.model_path, 'Indoor_model.onnx')
                if os.path.exists(onnx_path):
                    self.model = ort.InferenceSession(onnx_path)
                    self.model_type = 'onnx'
                    print(f"Successfully loaded ONNX model from {onnx_path}")
                    return
            except ImportError:
                print("ONNX Runtime not installed.")
                pass
            
            raise FileNotFoundError("No compatible model found or required libraries are missing.")
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.model = None
    
    def load_labels(self):
        """Load the labels from JSON file"""
        try:
            labels_path = os.path.join(self.model_path, 'labels.json')
            if os.path.exists(labels_path):
                with open(labels_path, 'r') as f:
                    self.labels = json.load(f)
                print(f"Successfully loaded labels: {list(self.labels.keys())}")
            else:
                # Default labels if file doesn't exist
                self.labels = {
                    "0": "hallway_straight",
                    "1": "hallway_left_turn", 
                    "2": "hallway_right_turn",
                    "3": "door_main_office",
                    "4": "door_computer_lab",
                    "5": "door_library",
                    "6": "door_cafeteria",
                    "7": "stairs_up",
                    "8": "stairs_down",
                    "9": "intersection"
                }
                print("Using default labels")
        except Exception as e:
            print(f"Error loading labels: {str(e)}")
            self.labels = {}
    
    def preprocess_image(self, image):
        """Preprocess image for model prediction"""
        try:
            # Convert to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize to model input size (assuming 224x224, adjust if different)
            if self.model_type == 'h5':
                input_shape = self.model.input_shape[1:3]
            elif self.model_type == 'tflite':
                input_details = self.model.get_input_details()
                input_shape = input_details[0]['shape'][1:3]
            else:
                # Default to 224x224 for ONNX
                input_shape = (224, 224)
            
            image = cv2.resize(image, input_shape)
            
            # Normalize pixel values
            image = image.astype(np.float32) / 255.0
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            return image
            
        except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
            return None
    
    def predict(self, image):
        """Make prediction on preprocessed image"""
        if self.model is None:
            return None, 0.0
        
        try:
            processed_image = self.preprocess_image(image)
            if processed_image is None:
                return None, 0.0
            
            if self.model_type == 'h5':
                predictions = self.model.predict(processed_image)
                predicted_class = np.argmax(predictions[0])
                confidence = float(np.max(predictions[0]))
                
            elif self.model_type == 'tflite':
                input_details = self.model.get_input_details()
                output_details = self.model.get_output_details()
                
                self.model.set_tensor(input_details[0]['index'], processed_image)
                self.model.invoke()
                
                predictions = self.model.get_tensor(output_details[0]['index'])
                predicted_class = np.argmax(predictions[0])
                confidence = float(np.max(predictions[0]))
                
            elif self.model_type == 'onnx':
                input_name = self.model.get_inputs()[0].name
                predictions = self.model.run(None, {input_name: processed_image})
                predicted_class = np.argmax(predictions[0])
                confidence = float(np.max(predictions[0]))
            
            # Get label for predicted class
            predicted_label = self.labels.get(str(predicted_class), f"class_{predicted_class}")
            
            return predicted_label, confidence
            
        except Exception as e:
            print(f"Error during prediction: {str(e)}")
            return None, 0.0
    
    def get_navigation_instruction(self, predicted_class, destination, current_location=None):
        """Convert model prediction to navigation instruction"""
        navigation_map = {
            "hallway_straight": {"action": "continue_straight", "message": "Continue straight ahead"},
            "hallway_left_turn": {"action": "turn_left", "message": "Turn left here"},
            "hallway_right_turn": {"action": "turn_right", "message": "Turn right here"},
            "door_main_office": {"action": "destination_reached", "message": "Main Office - You've arrived!"},
            "door_computer_lab": {"action": "destination_reached", "message": "Computer Lab - You've arrived!"},
            "door_library": {"action": "destination_reached", "message": "Library - You've arrived!"},
            "door_cafeteria": {"action": "destination_reached", "message": "Cafeteria - You've arrived!"},
            "stairs_up": {"action": "go_upstairs", "message": "Go upstairs"},
            "stairs_down": {"action": "go_downstairs", "message": "Go downstairs"},
            "intersection": {"action": "choose_direction", "message": "Choose your direction at the intersection"}
        }
        
        # FIXED: Ensure default action maps perfectly to the frontend's expected string
        return navigation_map.get(predicted_class, {
            "action": "continue_straight", 
            "message": "Continue following the path"
        })
    
    def is_model_loaded(self):
        """Check if model is successfully loaded"""
        return self.model is not None
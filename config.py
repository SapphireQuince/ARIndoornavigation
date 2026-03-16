import os
import json

class Config:
    # Basic Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'indoor-nav-secret-key-2024')
    
    # Network Configuration
    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = True
    
    # Model Configuration
    MODEL_PATH = 'models'
    H5_MODEL = 'Indoor_model.h5'
    ONNX_MODEL = 'Indoor_model.onnx'
    TFLITE_MODEL = 'Indoor_model.tflite'
    LABELS_FILE = 'labels.json'
    
    # QR Code Configuration
    QR_BASE_URL = f"https://192.168.1.100:{PORT}" # Updated to HTTPS
    ENTRANCE_COUNT = 5
    
    # Camera Configuration
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480

    # Pre-load Map Data into Memory (Fixes disk read bottleneck)
    MAP_DATA = {}
    try:
        with open('map.json', 'r') as f:
            MAP_DATA = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load map.json during startup: {e}")
    
    # Navigation Configuration - updated destinations
    DESTINATIONS = [
        "501", "501_stairs", "502A", "502B_502C", "502_stairs", 
        "506A", "507A", "507B", "508", "509 GENTS' TOILET", 
        "510_stairs", "511A", "511B", "512", "513A", "513B", 
        "514", "515", "516A", "516B", "516_stairs", "517", 
        "518", "519", "520", "521 GENTS' TOILET", "522", 
        "523 Girls Common Room", "524", "525", "526", "527", 
        "527_501_lecturehall_stairs", "Examination Cell", "HOD", 
        "Lift1", "Lift2", "Main_entrance"
    ]
    
    # Entrance locations
    ENTRANCES = {
        1: {"name": "Main Entrance", "description": "Primary building entrance"},
        2: {"name": "Side Entrance A", "description": "Left side entrance"},
        3: {"name": "Side Entrance B", "description": "Right side entrance"},
        4: {"name": "Back Entrance", "description": "Rear building entrance"},
        5: {"name": "Emergency Exit", "description": "Emergency/fire exit"}
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
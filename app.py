import os
import sys
from flask import Flask, current_app
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import cv2
import numpy as np
import base64

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'routes'))

from config import DevelopmentConfig, ProductionConfig
from model_handler import ModelHandler
from qr_generator import generate_qr_codes, generate_qr_code_html
from main_routes import main_bp
from api_routes import api_bp

config = {'development': DevelopmentConfig, 'production': ProductionConfig, 'default': DevelopmentConfig}

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    CORS(app, origins="*")
    
    # Threading mode prevents WebSocket crashes
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    app.model_handler = ModelHandler(app.config['MODEL_PATH'])
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @socketio.on('connect')
    def handle_connect():
        emit('status', {'msg': 'Connected to navigation server'})

    @socketio.on('process_frame')
    def handle_frame(data):
        try:
            frame_data = data.get('frame')
            destination = data.get('destination', 'Unknown')
            
            if not frame_data: return
            frame_bytes = base64.b64decode(frame_data.split(',')[1])
            frame_array = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

            predicted_class, confidence = app.model_handler.predict(frame)
            if predicted_class is None: return

            navigation_instruction = app.model_handler.get_navigation_instruction(predicted_class, destination)

            emit('navigation_result', {
                'predicted_class': predicted_class,
                'confidence': float(confidence),
                'navigation': navigation_instruction,
                'destination': destination
            })
        except Exception as e:
            print(f"Error processing frame: {str(e)}")

    return app, socketio

def main():
    app, socketio = create_app()
    print("="*60)
    print("INDOOR NAVIGATION SYSTEM - STARTUP")
    print(f"Model loaded: {app.model_handler.is_model_loaded()} | Type: {app.model_handler.model_type}")
    print("="*60)
    socketio.run(app, host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'], use_reloader=False)

if __name__ == '__main__':
    main()
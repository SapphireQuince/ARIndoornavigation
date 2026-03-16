# Create the complete project directory structure
import os

project_structure = """
indoor_navigation_webapp/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── config.py                       # Configuration settings
├── models/                         # Model files directory
│   ├── Indoor_model.h5
│   ├── Indoor_model.onnx
│   ├── Indoor_model.tflite
│   └── labels.json
├── static/                         # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── main.js
│   │   ├── camera.js
│   │   └── ar-navigation.js
│   └── images/
│       └── icons/
├── templates/                      # HTML templates
│   ├── index.html
│   ├── navigation.html
│   └── destination_select.html
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── model_handler.py
│   └── qr_generator.py
├── routes/                         # Route handlers
│   ├── __init__.py
│   ├── main_routes.py
│   └── api_routes.py
├── qr_codes/                       # Generated QR codes
│   ├── entrance_1.png
│   ├── entrance_2.png
│   ├── entrance_3.png
│   ├── entrance_4.png
│   └── entrance_5.png
└── deployment/                     # Deployment scripts
    ├── setup.bat
    ├── start_server.bat
    └── network_config.py
"""

print("Project Directory Structure:")
print(project_structure)
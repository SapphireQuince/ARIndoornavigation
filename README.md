# Indoor Navigation WebApp

## Overview
This project is an AR-based Indoor Navigation System designed to help users navigate complex indoor environments such as college buildings. It uses machine learning models to process camera frames and provide real-time navigation instructions. The system also generates QR codes for entrances to facilitate easy access.

## Features
- Real-time indoor navigation using camera input and machine learning models.
- Supports multiple model formats: TensorFlow (.h5), ONNX, and TensorFlow Lite (.tflite).
- QR code generation for multiple entrances.
- Web-based interface with Flask backend and SocketIO for real-time communication.
- Configurable destinations and entrances.
- Cross-origin resource sharing enabled for flexible deployment.

## Installation

### Prerequisites
- Python 3.7 or higher
- Windows OS (tested)
- College WiFi or local network for deployment

### Dependencies
Install required Python packages using:
```bash
pip install -r requirements.txt
```

## Configuration
Configuration settings are located in `config.py`:
- Network settings (host, port)
- Model paths and filenames
- QR code base URL and entrance count
- Camera resolution settings
- List of available destinations and entrance metadata

Modify these settings as needed for your environment.

## Running the Application

### Quick Start
Run the server with:
```bash
python app.py
```
The server will:
- Load the machine learning model
- Generate QR codes for entrances
- Start the Flask-SocketIO server

Access the application at: [http://localhost:5000](http://localhost:5000)

### Deployment
Refer to `DEPLOYMENT_GUIDE.md` for detailed deployment instructions including network configuration, QR code printing, and production deployment options.

## Project Structure
```
indoor_navigation_webapp/
├── app.py                  # Main Flask application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── models/                 # Machine learning model files and labels
├── qr_codes/               # Generated QR codes for entrances
├── routes/                 # Flask route handlers
├── static/                 # Static assets (CSS, JS, images)
├── templates/              # HTML templates for UI
├── utils/                  # Utility modules (model handling, QR code generation)
├── deployment/             # Deployment scripts and network config
├── map.json                # Indoor map connectivity data
└── README.md               # This file
```

## Usage
- Open the web app in a browser on a device connected to the same network.
- Select your destination from the list.
- Allow camera access for real-time navigation.
- Scan QR codes placed at building entrances to start navigation from that point.

## Troubleshooting
- Ensure camera permissions are granted in the browser.
- Verify model files exist in the `models/` directory.
- Confirm all devices are on the same network.
- Check server logs for errors.
- Use debug mode by double-tapping the navigation screen.

## Support
For issues, check:
- Server console logs
- Browser developer console for JavaScript errors
- Model file integrity and formats

## License
This project is provided as-is for educational and deployment purposes.

---

For detailed deployment and customization instructions, see `DEPLOYMENT_GUIDE.md`.

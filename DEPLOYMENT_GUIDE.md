# Indoor Navigation System - Complete Deployment Guide

## Overview
This guide will help you deploy your AR-based indoor navigation system on your college WiFi network using your trained model files.

## Prerequisites
- Windows computer with Python 3.7+
- Your trained model files:
  - `Indoor_model.h5`
  - `Indoor_model.onnx` 
  - `Indoor_model.tflite`
  - `labels.json`
- College WiFi network access
- Mobile devices for testing

## Quick Start (5 Minutes)

### Step 1: Setup Project Structure
1. Create a new folder called `indoor_navigation_webapp`
2. Extract all provided files to this folder
3. Copy your model files to the `models/` directory

### Step 2: Install Dependencies
Open Command Prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 3: Configure Network
Run the network configuration script:
```bash
python deployment/network_config.py
```

### Step 4: Start the Server
```bash
python app.py
```

### Step 5: Generate QR Codes
QR codes are automatically generated in the `qr_codes/` folder. Print them and place at entrances.

## Detailed Setup Instructions

### File Structure
Ensure your project has this structure:
```
indoor_navigation_webapp/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── config.py                       # Configuration settings
├── models/                         # YOUR MODEL FILES GO HERE
│   ├── Indoor_model.h5            # Your trained H5 model
│   ├── Indoor_model.onnx          # Your trained ONNX model
│   ├── Indoor_model.tflite        # Your trained TFLite model
│   └── labels.json                # Your model labels
├── static/                         # Static files
│   ├── css/style.css
│   └── js/
│       ├── main.js
│       ├── camera.js
│       └── ar-navigation.js
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
├── qr_codes/                       # Generated QR codes (auto-created)
└── deployment/                     # Deployment scripts
    ├── setup.bat
    ├── start_server.bat
    └── network_config.py
```

### Model Integration
Your trained model files should be placed in the `models/` directory:

1. **Indoor_model.h5** - TensorFlow/Keras model (recommended)
2. **Indoor_model.onnx** - ONNX model (alternative)
3. **Indoor_model.tflite** - TensorFlow Lite model (mobile optimized)
4. **labels.json** - Model class labels

The system will automatically load the best available model format.

#### Example labels.json format:
```json
{
  "0": "hallway_straight",
  "1": "hallway_left_turn", 
  "2": "hallway_right_turn",
  "3": "door_main_office",
  "4": "door_computer_lab",
  "5": "door_library",
  "6": "stairs_up",
  "7": "intersection"
}
```

### Network Configuration

#### For College WiFi:
1. Connect your computer to the college WiFi
2. Run `python deployment/network_config.py` to get your IP address
3. The system will automatically configure network settings
4. QR codes will be generated with the correct IP address

#### Manual IP Configuration:
If you need to manually set the IP address, edit `config.py`:
```python
HOST = "YOUR_IP_ADDRESS"  # Replace with your actual IP
PORT = 5000
```

### Security Considerations
- The system uses HTTP (not HTTPS) for local network deployment
- Ensure your college network allows device-to-device communication
- Consider using a VPN or isolated network for sensitive deployments

## Running the Application

### Option 1: Windows Batch Files
```bash
# Setup (run once)
setup.bat

# Start server
start_server.bat
```

### Option 2: Python Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python app.py
```

### Option 3: Production Deployment
For production use with multiple users:
```bash
# Install Gunicorn
pip install gunicorn

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## QR Code Deployment

### Generating QR Codes
QR codes are automatically generated when the server starts. Find them in:
- `qr_codes/entrance_1.png`
- `qr_codes/entrance_2.png`
- etc.

### Printing and Placement
1. Open `qr_codes/qr_codes_print.html` in a browser
2. Print the page (optimized for A4 paper)
3. Cut out individual QR codes
4. Laminate for durability (recommended)
5. Place at designated entrances

### QR Code URLs
Each QR code links to:
- Entrance 1: `http://YOUR_IP:5000/?entrance=1`
- Entrance 2: `http://YOUR_IP:5000/?entrance=2`
- etc.

## Customization

### Adding/Removing Destinations
Edit `config.py`:
```python
DESTINATIONS = [
    "Main Office",
    "Computer Lab", 
    "Library",
    "Your Custom Location",  # Add here
    # Remove unwanted locations
]
```

### Modifying Entrance Information
Edit `config.py`:
```python
ENTRANCES = {
    1: {"name": "Main Entrance", "description": "Front door"},
    2: {"name": "Side Entrance", "description": "Near parking lot"},
    # Modify as needed
}
```

### UI Customization
- Edit `static/css/style.css` for styling
- Modify HTML templates in `templates/` folder
- Update icons and emojis in the templates

## Testing the System

### Local Testing
1. Start the server: `python app.py`
2. Open browser: `http://127.0.0.1:5000`
3. Test destination selection and camera access

### Mobile Testing
1. Connect mobile device to same WiFi network
2. Scan a QR code or visit `http://YOUR_IP:5000`
3. Allow camera permissions when prompted
4. Test AR navigation functionality

### Model Testing
1. Check server logs for model loading status
2. Use debug mode (double-tap screen in navigation)
3. Monitor prediction confidence levels
4. Verify navigation instructions match your labels

## Troubleshooting

### Common Issues

#### 1. Camera Not Working
- Ensure HTTPS or localhost access
- Check browser permissions
- Try different browsers (Chrome recommended)

#### 2. Model Not Loading
- Verify model files exist in `models/` directory
- Check file permissions
- Review server logs for error messages

#### 3. Network Connection Issues
- Confirm all devices on same WiFi network
- Check Windows Firewall settings
- Try disabling antivirus temporarily

#### 4. QR Codes Not Working
- Verify IP address in QR codes matches server IP
- Check that server is running
- Test direct URL access first

### Debug Mode
- Double-tap the navigation screen to show debug information
- Monitor prediction accuracy and frame rate
- Check server logs for detailed error messages

### Performance Optimization
- Use TensorFlow Lite model for better mobile performance
- Reduce frame processing rate if needed (edit `ar-navigation.js`)
- Consider model quantization for faster inference

## Deployment Checklist

- [ ] Python 3.7+ installed
- [ ] All project files in correct structure
- [ ] Model files copied to `models/` directory
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Network configuration completed
- [ ] QR codes generated and printed
- [ ] Server starts without errors
- [ ] Mobile devices can access via WiFi
- [ ] Camera permissions working
- [ ] Model predictions functioning
- [ ] Navigation instructions displaying correctly

## Maintenance

### Regular Tasks
- Monitor server performance and logs
- Update model files if retrained
- Replace damaged QR codes
- Check camera functionality on different devices

### Updates
- Keep Python dependencies updated
- Monitor for security patches
- Consider HTTPS upgrade for production use

## Support
For technical issues:
1. Check server logs in the console
2. Use browser developer tools for JavaScript errors
3. Verify model file formats and sizes
4. Test with different mobile devices and browsers

This system is designed to work offline once loaded, making it perfect for college deployments with limited internet connectivity.
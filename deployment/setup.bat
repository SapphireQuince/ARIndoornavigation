@echo off
echo ========================================
echo Indoor Navigation System Setup
echo ========================================
echo.

echo Installing required Python packages...
pip install -r requirements.txt

echo.
echo Creating directory structure...
if not exist "models" mkdir models
if not exist "qr_codes" mkdir qr_codes
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\images\icons" mkdir static\images\icons
if not exist "templates" mkdir templates
if not exist "utils" mkdir utils
if not exist "routes" mkdir routes

echo.
echo Creating __init__.py files...
echo. > utils\__init__.py
echo. > routes\__init__.py

echo.
echo Setup complete!
echo.
echo IMPORTANT: Please copy your model files to the 'models' directory:
echo   - Indoor_model.h5
echo   - Indoor_model.onnx
echo   - Indoor_model.tflite
echo   - labels.json
echo.
echo To start the server, run: start_server.bat
echo.
pause
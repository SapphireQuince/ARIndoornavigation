@echo off
echo ========================================
echo Starting Indoor Navigation System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "app.py" (
    echo ERROR: app.py not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

if not exist "models" (
    echo ERROR: models directory not found
    echo Please create models directory and add your model files
    pause
    exit /b 1
)

echo Checking model files...
if not exist "models\Indoor_model.h5" (
    if not exist "models\Indoor_model.onnx" (
        if not exist "models\Indoor_model.tflite" (
            echo WARNING: No model files found in models directory
            echo Please add at least one model file:
            echo   - Indoor_model.h5
            echo   - Indoor_model.onnx
            echo   - Indoor_model.tflite
            echo.
        )
    )
)

if not exist "models\labels.json" (
    echo WARNING: labels.json not found in models directory
    echo The system will use default labels
    echo.
)

REM Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do set "ip=%%a"
set ip=%ip: =%
set ip=%ip:~0,-1%

echo Starting server...
echo.
echo ========================================
echo Server will be available at:
echo   Local:    http://127.0.0.1:5000
echo   Network:  http://%ip%:5000
echo ========================================
echo.
echo QR codes will be generated automatically
echo Check the 'qr_codes' folder for printable QR codes
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the Flask application
python app.py
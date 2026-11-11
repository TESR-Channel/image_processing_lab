@echo off
REM TESR ROI Studio v1.10.0 - terminal_qc_config.json - one-click installer (Windows)
REM Makes venv\ in THIS folder (next to the config) and installs only what this project needs.
setlocal
cd /d "%~dp0"
set "PY=python"
py -3 -c "print()" >nul 2>nul && set "PY=py -3"
echo Using: %PY%
%PY% -m venv venv || goto err
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install opencv-python numpy onnxruntime paho-mqtt || goto err
python -c "import cv2, numpy, onnxruntime; print('OK - OpenCV', cv2.__version__)" || goto err
echo.
echo ============================================
echo  Done! Every time you open a new window:
echo    venv\Scripts\activate
echo    cd /d %~dp0
echo    python tesr_vision_runner.py --config terminal_qc_config.json --image photo.jpg --once
echo    python tesr_vision_runner.py --config terminal_qc_config.json --image my_photos
echo    python tesr_vision_runner.py --config terminal_qc_config.json --camera usb --source 0
echo    python tesr_vision_runner.py --config terminal_qc_config.json --camera usb --source 0 --broker 192.168.1.50
echo    (another webcam: --source 1, 2 ; network camera: --camera ip --source rtsp://...)
echo ============================================
pause
exit /b 0
:err
echo.
echo Install failed - you need Python 3.8 or newer from python.org (tick Add to PATH).
pause
exit /b 1

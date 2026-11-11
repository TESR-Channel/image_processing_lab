#!/usr/bin/env bash
# TESR ROI Studio v1.10.0 - ssr_qc_config.json - installer for a Linux / macOS PC
# Raspberry Pi -> install_pi.sh    Jetson -> install_jetson.sh    Windows -> install_windows.bat
# Makes venv/ in THIS folder (next to the config) and installs only what this project needs.
set -e
cd "$(dirname "$0")"
python3 -m venv venv
. venv/bin/activate
python -m pip install --upgrade pip
pip install opencv-python numpy onnxruntime paho-mqtt
python -c "import cv2, numpy, onnxruntime; print('OK - OpenCV', cv2.__version__)"
echo
echo "Done! Every time you open a new terminal:"
echo "  source venv/bin/activate"
echo "  cd $(pwd)"
echo "  python tesr_vision_runner.py --config ssr_qc_config.json --image photo.jpg --once"
echo "  python tesr_vision_runner.py --config ssr_qc_config.json --image my_photos"
echo "  python tesr_vision_runner.py --config ssr_qc_config.json --camera usb --source 0"
echo "  python tesr_vision_runner.py --config ssr_qc_config.json --camera usb --source 0 --broker 192.168.1.50"
echo "  (another webcam: --source 1, 2 ; ribbon camera: --camera csi ; network: --camera ip --source rtsp://...)"

#!/usr/bin/env bash
# TESR ROI Studio v1.10.0 - ssr_qc_config.json - installer for Raspberry Pi 5 (Raspberry Pi OS 64-bit)
# OpenCV, NumPy and Picamera2 come from apt (Picamera2 cannot be pip-installed); the venv sees
# them through --system-site-packages. Never "sudo pip3 install" - Bookworm refuses (PEP 668).
set -e
cd "$(dirname "$0")"
[ "$(uname -m)" = "aarch64" ] || echo "WARNING: not a 64-bit OS ($(uname -m)) - onnxruntime needs 64-bit Raspberry Pi OS"
sudo apt update
sudo apt install -y python3-venv python3-opencv python3-numpy python3-picamera2
python3 -m venv --system-site-packages venv
. venv/bin/activate
pip install --upgrade pip
pip install onnxruntime paho-mqtt
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

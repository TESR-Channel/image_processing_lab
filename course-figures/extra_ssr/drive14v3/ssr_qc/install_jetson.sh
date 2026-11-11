#!/usr/bin/env bash
# TESR ROI Studio v1.10.0 - ssr_qc_config.json - installer for NVIDIA Jetson (Orin Nano / Orin NX / AGX Orin)
# Uses the system OpenCV (it has GStreamer, which a CSI camera needs) through --system-site-packages.
# pip's onnxruntime is a CPU build: measure it on the device first. A Jetson Nano is more limited
# than an Orin Nano (older JetPack, fewer builds) - expect to pin older versions there.
set -e
cd "$(dirname "$0")"
[ -f /etc/nv_tegra_release ] && echo "L4T: $(head -n1 /etc/nv_tegra_release)"
sudo apt update
sudo apt install -y python3-venv python3-pip python3-numpy
python3 -c "import cv2" 2>/dev/null || sudo apt install -y python3-opencv
python3 -m venv --system-site-packages venv
. venv/bin/activate
pip install --upgrade pip
pip install onnxruntime paho-mqtt || { echo "pip could not install this for $(python3 -V): install the Jetson build of onnxruntime for your JetPack, then run again"; exit 1; }
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

#!/usr/bin/env bash
# ==== TESR extra part - QC with two AIs - installer for Raspberry Pi 5 (Raspberry Pi OS 64-bit) ====
# OpenCV, NumPy and Picamera2 come from apt (Picamera2 cannot be pip-installed);
# the venv sees them through --system-site-packages, and pip adds onnxruntime
# and paho-mqtt.
#
# Never "sudo pip3 install" - Pi OS Bookworm marks the system Python as
# externally managed (PEP 668) and refuses. The venv below is how you get past
# that without fighting it.
set -e
cd "$(dirname "$0")/.."      # the chapter folder: venv/ is made there
if [ "$(uname -m)" != "aarch64" ]; then
  echo "WARNING: this is not a 64-bit OS ($(uname -m)). onnxruntime needs 64-bit Raspberry Pi OS."
fi
sudo apt update
sudo apt install -y python3-venv python3-opencv python3-numpy python3-picamera2
python3 -m venv --system-site-packages venv
. venv/bin/activate
pip install --upgrade pip
pip install onnxruntime paho-mqtt
python -c "import onnxruntime, cv2; print('onnxruntime', onnxruntime.__version__, '| OpenCV', cv2.__version__)"
echo
echo "Done! Then:"
echo "  source venv/bin/activate"
echo "  cd terminal_qc"
echo "  python tesr_vision_runner.py --config terminal_qc_config.json --image ../image/Terminal/ng"
echo "  python tesr_vision_runner.py --config terminal_qc_config.json --camera usb --source 0"
echo "      (another webcam: --source 1, 2 ; the relay: cd ../ssr_qc, config ssr_qc_config.json)"

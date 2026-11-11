#!/usr/bin/env bash
# ==== TESR extra part - QC with two AIs - installer for NVIDIA Jetson (Orin Nano / Orin NX / AGX Orin) ====
# Uses the system OpenCV (it has GStreamer, which a CSI camera needs; pip's
# opencv-python does not) through a venv with --system-site-packages.
#
# The onnxruntime pip hands you here is a CPU build, and it is the right place
# to start. For the GPU you need NVIDIA's own wheel for YOUR JetPack version -
# not the one on PyPI. Measure the CPU build on the device before deciding you
# need anything else. The final challenge is the right moment to measure
# rather than guess: it is your own line, your own model and your own frame
# rate, and nobody else's figure applies to it.
#
# A Jetson Nano is considerably more limited than a Jetson Orin Nano: less
# memory, an older JetPack, and newer packages often have no build for it at
# all. On a Nano, expect to pin older versions.
set -e
cd "$(dirname "$0")/.."      # the chapter folder: venv/ is made there
[ -f /etc/nv_tegra_release ] && echo "L4T: $(head -n1 /etc/nv_tegra_release)"
sudo apt update
sudo apt install -y python3-venv python3-pip python3-numpy
python3 -c "import cv2" 2>/dev/null || sudo apt install -y python3-opencv
python3 -m venv --system-site-packages venv
. venv/bin/activate
pip install --upgrade pip
pip install onnxruntime paho-mqtt || {
  echo "pip could not install onnxruntime for this Python ($(python3 -V))."
  echo "Install the Jetson build of onnxruntime for your JetPack, then re-run."
  exit 1; }
python -c "import onnxruntime as o, cv2; print('onnxruntime', o.__version__, o.get_available_providers())"
echo
echo "Done! Then:"
echo "  source venv/bin/activate"
echo "  cd terminal_qc"
echo "  python tesr_vision_runner.py --config terminal_qc_config.json --image ../image/Terminal/ng"
echo "  python tesr_vision_runner.py --config terminal_qc_config.json --camera usb --source 0"
echo "      (another webcam: --source 1, 2 ; the relay: cd ../ssr_qc, config ssr_qc_config.json)"

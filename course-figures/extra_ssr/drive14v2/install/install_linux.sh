#!/usr/bin/env bash
# ==== TESR extra part - QC with two AIs - installer for a Linux / macOS PC ====
# Raspberry Pi -> install_pi.sh    Jetson -> install_jetson.sh
set -e
cd "$(dirname "$0")/.."      # the chapter folder: venv/ is made there
python3 -m venv venv
. venv/bin/activate
python -m pip install --upgrade pip
pip install -r install/requirements.txt
echo
echo "Done! Then:"
echo "  source venv/bin/activate"
echo "  cd terminal_qc"
echo "  python tesr_vision_runner.py --config terminal_qc_config.json --image ../image/Terminal/ng"
echo "  python tesr_vision_runner.py --config terminal_qc_config.json --camera usb --source 0"
echo "      (another webcam: --source 1, 2 ; the relay: cd ../ssr_qc, config ssr_qc_config.json)"

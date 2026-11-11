TESR ROI Studio - project file
==============================
Saved by Studio v1.9.1 on 2026-11-11 05:07:09

TO CARRY ON EDITING
  Open https://tesr-channel.github.io/AI_ROI_Designer/
  press Import config, and choose this .zip - or, once unzipped, pick
  ssr_qc_config.json, project.json and the .onnx file(s) together
  (hold Ctrl), or drop them on the picture. The regions, the reference
  image, the models and each camera's detector all come back attached:
  nothing to add again, edit and export as before.

TO RUN IT
  Unzip the whole thing into one folder, cd into it and run from there.
  The model path in the config is relative, and the runner opens it from
  the folder you RUN the command in (the current directory) - not from
  the runner's folder and not from the config's folder. Logs and captures
  are written relative to that folder too.

    python tesr_vision_runner.py --config ssr_qc_config.json --camera usb --source 0 --test
    python tesr_vision_runner.py --config ssr_qc_config.json --image photo.jpg --once
    python tesr_vision_runner.py --config ssr_qc_config.json --image my_photos
      (a folder: every picture once, a labelled copy of each + log.csv in records/)
    python tesr_vision_runner.py --config ssr_qc_config.json --headless
    python tesr_vision_runner.py --config ssr_qc_config.json --camera usb --source 2 --broker 192.168.1.50
      (--broker = send every reading over MQTT to that computer, e.g. Node-RED)

  python3 rather than python on a Raspberry Pi or a Jetson.
  A ribbon camera is --camera csi, a network camera is
  --camera ip --source rtsp://...

WHAT IS IN HERE
  ssr_qc_config.json   the regions, their parameters and the reference image
  tesr_vision_runner.py
  project.json           the Studio's own notes, so it can put everything back
  ssr_finder.onnx   detect, 1 classes: ssr, imgsz 416
  screw_checker.onnx   detect, 1 classes: screw, imgsz 320

Install once:  pip install opencv-python numpy onnxruntime

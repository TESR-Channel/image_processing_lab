@echo off
REM ==== TESR extra part - QC with two AIs - one-click installer (Windows) ====
setlocal
REM work in the chapter folder (one up from install\): venv\ is made there
cd /d "%~dp0.."
set "PY=python"
py -3 -c "print()" >nul 2>nul && set "PY=py -3"
echo Using: %PY%
%PY% -m venv venv || goto err
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r install\requirements.txt || goto err
echo.
echo ============================================
echo  Done! 
echo.
echo  Then:
echo    venv\Scripts\activate
echo    cd terminal_qc
echo    python tesr_vision_runner.py --config terminal_qc_config.json --image ..\image\Terminal\ng
echo    python tesr_vision_runner.py --config terminal_qc_config.json --camera usb --source 0
echo        (another webcam: --source 1, 2 ; the relay: cd ..\ssr_qc, config ssr_qc_config.json)
echo ============================================
pause
exit /b 0
:err
echo.
echo Install failed - you need Python 3.8 or newer from python.org.
pause
exit /b 1

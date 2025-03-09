@echo off
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Building executable...
python build_exe.py

echo.
echo Build complete! Press any key to exit...
pause 
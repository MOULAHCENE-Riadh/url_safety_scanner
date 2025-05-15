@echo off
echo Starting URL Safety Checker Server...
echo.
echo -----------------------------------
echo     NETWORK INFORMATION
echo -----------------------------------
ipconfig | findstr /i "IPv4"
echo.
echo Server will be available at:
echo  - http://localhost:8000
echo  - http://YOUR_IP_ADDRESS:8000 (see above)
echo  - http://10.0.2.2:8000 (for Android emulator)
echo.
echo -----------------------------------
echo     STARTING SERVER
echo -----------------------------------
echo The server is starting now. Press Ctrl+C to stop it.
echo.

python app.py

pause 
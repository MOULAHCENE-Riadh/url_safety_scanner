# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the QR Scanner Safety Check application.

## Connection Issues

### "Error connecting to server" or timeout errors

If you're seeing errors like:

```
API error: ClientException with SocketException: Connection timed out
```

Try these steps in order:

1. **Check if the server is running**
   - Open a web browser on your computer and navigate to http://localhost:8000/api/health
   - If you see a JSON response, the server is running
   - If not, start the server by running `python app.py` or use the `start_server.bat` file

2. **Check firewall settings**
   - Windows Firewall might be blocking connections to your Flask server
   - Run the `setup_firewall.ps1` script with administrator rights (right-click -> Run with PowerShell)
   - This adds an exception for port 8000 in your firewall

3. **Check network connectivity**
   - Make sure your phone is on the same WiFi network as your computer
   - Run the diagnostic tool: `python network_test.py`
   - Note your computer's actual IP address from the output

4. **Update the server IP in the Flutter app**
   - The latest version should automatically discover the server IP
   - If it doesn't, update the IP address in `lib/services/url_checker_service.dart`
   - Look for the line with `http://192.168.1.89:8000` and change it to your computer's IP

5. **Try in an emulator**
   - If using an Android emulator, it should automatically connect to the server via 10.0.2.2:8000
   - This is a special IP that maps to the host computer's localhost

## Server Issues

### "Model not loaded" error

If you're seeing the fallback heuristic being used because the model is not loaded:

1. **Check if the model file exists**
   - Look for `url_classifier_model.joblib` in the Malicious-URL-Detection directory
   - If it's missing, try retraining the model using the notebook `Malicious-URL-Detection/Code/phisingPredictor.ipynb`

2. **Check Python version and compatibility**
   - Some scikit-learn versions are not compatible with models saved in other versions
   - Try installing matching versions: `pip install scikit-learn==1.2.2 joblib==1.2.0`

### Server crashes or doesn't start

1. **Check logs for errors**
   - Look for error messages in the terminal where you started the server
   - Common issues involve missing dependencies or port conflicts

2. **Install required packages**
   - Run `pip install -r requirements.txt` to install all dependencies
   - If you see version conflicts, try creating a new virtual environment

3. **Port conflict**
   - If port 8000 is already in use, change the port in `app.py` and update the app accordingly

## Mobile App Issues

### App crashes when scanning

1. **Check app logs**
   - Connect your device to your computer and view logs in Android Studio or Flutter DevTools
   - Look for specific error messages

2. **Update dependencies**
   - Make sure all Flutter dependencies are up to date
   - Run `flutter pub get` in the scanner_safe_flutter directory

### "Safe" or "Unsafe" result doesn't match expectations

1. **Check if using the model or fallback**
   - The app logs will indicate if it's using the ML model or the local heuristic fallback
   - The local fallback is less accurate, so try to get the server connection working

2. **Verify the URL**
   - Some URLs redirect to different domains
   - The app checks the initial URL, not the redirected one

## Running the Network Diagnostic Tool

For a comprehensive diagnosis, run:

```
python network_test.py
```

This will:
- Display all your network interfaces
- Test connectivity to the Flask server from various IPs
- Check if port 8000 is open and listening
- Check your firewall status
- Provide recommendations based on the results 
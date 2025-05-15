# QR Scanner Safety Check

This project combines a malicious URL detection model with a QR code scanner mobile app to create a system that lets users safely scan QR codes and check if the associated websites are safe to visit.

## Components

1. **URL Safety Model** - A machine learning model that classifies URLs as safe or potentially malicious
2. **Flask API Backend** - A REST API that serves the URL classification model
3. **Flutter Mobile App** - A cross-platform mobile app that scans QR codes and checks URL safety

## Getting Started

### Prerequisites

- Python 3.8+ for the backend
- Flutter SDK for the mobile app
- Android Studio/XCode for mobile app development

### Setting Up the Backend

1. Clone this repository
```
git clone <repository-url>
cd scanner_safe2
```

2. Set up a Python virtual environment (recommended)
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies
```
pip install -r requirements.txt
```

4. Run the Flask API
```
python app.py
```
The API will be available at http://localhost:8000

### Setting Up the Mobile App

1. Navigate to the Flutter app directory
```
cd scanner_safe_flutter
```

2. Install Flutter dependencies
```
flutter pub get
```

3. Update API endpoint (if needed)
   - Open `lib/services/url_checker_service.dart`
   - Modify the `baseUrl` getter to point to your Flask API

4. Run the app
```
flutter run
```

## API Usage

The backend API exposes the following endpoint:

- **URL**: `/api/v1/check-url`
- **Methods**: `POST`, `GET`
- **Parameters**:
  - For POST: JSON body with `{ "url": "https://example.com" }`
  - For GET: Query parameter `?url=https://example.com`
- **Response**: JSON with `{ "safe": true/false, "message": "..." }`

## How It Works

1. The user scans a QR code with the mobile app
2. The app extracts the URL from the QR code
3. The app sends the URL to the Flask API
4. The API uses the machine learning model to classify the URL
5. The classification result is returned to the app
6. The app displays the safety status to the user

## Attribution

The URL safety classification model is based on [Malicious-URL-Detection](https://github.com/vasudhamadhavan/Malicious-URL-Detection) that uses machine learning techniques to identify potential phishing and malicious websites. 
import os
import re
import numpy as np
import socket
import platform
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import urlparse
from joblib import load
import logging
import traceback

# Configure logging - more detailed format
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # Enable CORS for all routes with more permissive settings

# Get server network info for debugging
def get_network_info():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Get all network interfaces
    all_ips = []
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None):
            all_ips.append(info[4][0])
        all_ips = list(set(all_ips))  # Remove duplicates
    except Exception as e:
        logger.error(f"Error getting all IPs: {e}")
    
    return {
        "hostname": hostname,
        "local_ip": local_ip,
        "all_ips": all_ips,
        "platform": platform.platform()
    }

# Print network info at startup
network_info = get_network_info()
logger.info(f"Server starting with network configuration:")
logger.info(f"Hostname: {network_info['hostname']}")
logger.info(f"Local IP: {network_info['local_ip']}")
logger.info(f"All IPs: {network_info['all_ips']}")
logger.info(f"Platform: {network_info['platform']}")

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
logger.info(f"Working directory: {current_dir}")

# Load the model and scaler
try:
    MODEL_PATH = os.path.join(current_dir, 'Malicious-URL-Detection', 'url_classifier_model.joblib')
    SCALER_PATH = os.path.join(current_dir, 'Malicious-URL-Detection', 'scaler.joblib')
    
    logger.info(f"Loading model from: {MODEL_PATH}")
    logger.info(f"Loading scaler from: {SCALER_PATH}")
    
    model = load(MODEL_PATH)
    scaler = load(SCALER_PATH)
    logger.info("Model and scaler loaded successfully")
except Exception as e:
    logger.error(f"Error loading model or scaler: {e}")
    logger.error(traceback.format_exc())
    model = None
    scaler = None

# Request logging middleware
@app.before_request
def log_request_info():
    logger.debug('Request Headers: %s', request.headers)
    logger.debug('Request Body: %s', request.get_data())
    logger.info(f"Request from: {request.remote_addr} to {request.path} [{request.method}]")

# After request logging
@app.after_request
def log_response_info(response):
    logger.info(f"Response status: {response.status_code}")
    logger.debug(f"Response headers: {response.headers}")
    return response

# Add a simple health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    logger.info(f"Health check request received from: {request.remote_addr}")
    
    # Get server networking details for debugging
    network_info = get_network_info()
    
    # Return detailed system info for debugging connection issues
    return jsonify({
        "status": "ok",
        "message": "Server is running",
        "model_loaded": model is not None and scaler is not None,
        "server_info": network_info,
        "request_ip": request.remote_addr,
        "request_headers": dict(request.headers)
    })

# Add a connectivity test endpoint
@app.route('/api/ping', methods=['GET'])
def ping():
    logger.info(f"Ping request received from: {request.remote_addr}")
    return jsonify({"message": "pong"})

def extract_features(url):
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname if parsed_url.hostname else ''
        path = parsed_url.path if parsed_url.path else ''

        features = {
            'length_url': len(url),
            'length_hostname': len(hostname),
            'ip': int(bool(re.match(r'\d+\.\d+\.\d+\.\d+', hostname))),
            'nb_dots': url.count('.'),
            'nb_hyphens': url.count('-'),
            'nb_at': url.count('@'),
            'nb_qm': url.count('?'),
            'nb_and': url.count('&'),
            'nb_or': url.count('|'),
            'nb_eq': url.count('='),
            'nb_underscore': url.count('_'),
            'nb_tilde': url.count('~'),
            'nb_percent': url.count('%'),
            'nb_slash': url.count('/'),
            'nb_star': url.count('*'),
            'nb_colon': url.count(':'),
            'nb_comma': url.count(','),
            'nb_semicolon': url.count(';'),
            'nb_dollar': url.count('$'),
            'nb_space': url.count(' '),
            'nb_www': url.count('www'),
            'nb_com': url.count('.com'),
            'nb_dslash': url.count('//'),
            'http_in_path': int('http' in path.lower()),
            'https_token': int('https' in path.lower()),
            'ratio_digits_url': sum(c.isdigit() for c in url) / len(url),
            'ratio_digits_host': sum(c.isdigit() for c in hostname) / len(hostname) if hostname else 0,
            'nb_redirection': url.count('//'),
            'length_words_raw': len(re.findall(r'\w+', url)),
            'char_repeat': max([len(m.group(0)) for m in re.finditer(r'(.)\1*', url)], default=0),
            'shortest_word_length': min([len(word) for word in re.findall(r'\w+', url)], default=0),
            'longest_word_length': max([len(word) for word in re.findall(r'\w+', url)], default=0),
            'avg_word_length': np.mean([len(word) for word in re.findall(r'\w+', url)]) if re.findall(r'\w+', url) else 0
        }

        feature_order = [
            'length_url', 'length_hostname', 'ip', 'nb_dots', 'nb_hyphens', 'nb_at', 'nb_qm', 'nb_and', 'nb_or', 'nb_eq',
            'nb_underscore', 'nb_tilde', 'nb_percent', 'nb_slash', 'nb_star', 'nb_colon', 'nb_comma', 'nb_semicolon', 'nb_dollar',
            'nb_space', 'nb_www', 'nb_com', 'nb_dslash', 'http_in_path', 'https_token', 'ratio_digits_url', 'ratio_digits_host',
            'nb_redirection', 'length_words_raw', 'char_repeat', 'shortest_word_length', 'longest_word_length', 'avg_word_length'
        ]

        return [features[feature] for feature in feature_order]
    except Exception as e:
        logger.error(f"Error extracting features from URL {url}: {e}")
        raise

def predict_url_safety(url):
    try:
        # Check if URL is properly formatted
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Extract features
        features = extract_features(url)
        logger.info(f"Extracted {len(features)} features from URL: {url}")

        # Scale features
        features_scaled = scaler.transform([features])

        # Predict
        prediction = model.predict(features_scaled)
        probabilities = model.predict_proba(features_scaled)[0]
        is_malicious = prediction[0] == 1  # Fixed: use == 1 instead of bool()
        logger.info(f"Model prediction: {prediction[0]}, probabilities: safe={probabilities[0]:.2f}, unsafe={probabilities[1]:.2f}")

        # Format response to match what Flutter expects
        return {
            "url": url,
            "is_safe": not is_malicious,  # Changed "safe" to "is_safe"
            "confidence": float(probabilities[0] if not is_malicious else probabilities[1]),
            "details": "This URL appears to be safe." if not is_malicious else "This URL was flagged as potentially malicious. Proceed with caution."
        }
    except Exception as e:
        logger.error(f"Error predicting URL safety: {e}")
        return {
            "url": url,
            "is_safe": False,
            "confidence": 0.0,
            "details": f"Unable to analyze URL: {str(e)}"
        }

@app.route('/api/v1/check-url', methods=['POST', 'GET'])
def check_url():
    try:
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                url = data.get('url')
                logger.info(f"Received POST request to check URL: {url}")
            else:
                # Handle form data
                url = request.form.get('url')
                if not url:
                    return jsonify({"error": "No URL provided in form data"}), 400
        else:  # GET request
            url = request.args.get('url')
            logger.info(f"Received GET request to check URL: {url}")

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        if model is None or scaler is None:
            logger.warning("Model not available, using fallback heuristic checks")
            # Fallback to basic heuristic checks if model is not available
            return heuristic_url_check(url)

        result = predict_url_safety(url)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in check_url endpoint: {e}")
        return jsonify({
            "safe": False,
            "message": f"Server error: {str(e)}"
        }), 500

def heuristic_url_check(url):
    """Basic heuristic check for URL safety when model is unavailable"""
    try:
        # Common safe domains
        safe_domains = [
            'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'youtube.com', 'github.com', 'stackoverflow.com', 'wikipedia.org'
        ]
        
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname if parsed_url.hostname else ''
        
        # Check for IP address in hostname (suspicious)
        ip_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
        has_ip = bool(ip_pattern.match(hostname))
        
        # Check for excessive subdomains (suspicious)
        subdomain_count = hostname.count('.')
        
        # Check for common safe domains
        is_common_safe = any(hostname.endswith('.' + domain) or hostname == domain for domain in safe_domains)
        
        # Check for suspicious keywords in URL
        suspicious_keywords = ['free', 'win', 'lucky', 'prize', 'money', 'loan', 'password', 'login', 'bank']
        has_suspicious_keywords = any(keyword in url.lower() for keyword in suspicious_keywords)
        
        # Make decision based on heuristics
        if is_common_safe and not has_suspicious_keywords:
            confidence = 0.8
            details = "This appears to be a commonly trusted website (fallback check)."
            is_safe = True
        elif has_ip or subdomain_count > 3 or has_suspicious_keywords:
            confidence = 0.7
            details = "This URL has suspicious characteristics. Proceed with caution (fallback check)."
            is_safe = False
        else:
            confidence = 0.5
            details = "Could not verify safety with full model. Proceed with caution (fallback check)."
            is_safe = False
            
        return jsonify({
            "url": url,
            "is_safe": is_safe,
            "confidence": confidence,
            "details": details
        })
            
    except Exception as e:
        logger.error(f"Error in heuristic check: {e}")
        return jsonify({
            "url": url,
            "is_safe": False,
            "confidence": 0.0,
            "details": "Error analyzing URL safety"
        })

if __name__ == '__main__':
    # Get all available IPs for logging
    network_info = get_network_info()
    logger.info(f"Starting server - available on the following IPs:")
    for ip in network_info['all_ips']:
        logger.info(f"  http://{ip}:8000")
    
    # Log special Android emulator address
    logger.info(f"Android emulator can access via: http://10.0.2.2:8000")
    
    # Add explicit cors headers for troubleshooting
    @app.after_request
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Enable debug mode for more useful error messages
    app.debug = True
    
    # Run the app - bind to all network interfaces explicitly
    app.run(host='0.0.0.0', port=8000, threaded=True) 
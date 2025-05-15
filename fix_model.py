import os
import numpy as np
from joblib import load, dump

# Load the model
MODEL_PATH = os.path.join('Malicious-URL-Detection', 'url_classifier_model.joblib')
model = load(MODEL_PATH)

# Examine how the model is predicting
print("Loading model from:", MODEL_PATH)
print(f"Model class labels (classes_): {model.classes_}")

# Flip the prediction logic in the app.py file
# This is a quick fix without needing to retrain the model

def test_with_examples():
    from urllib.parse import urlparse
    import re
    
    def extract_features(url):
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
            'ratio_digits_url': sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0,
            'ratio_digits_host': sum(c.isdigit() for c in hostname) / len(hostname) if len(hostname) > 0 else 0,
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
    
    # Load the scaler
    SCALER_PATH = os.path.join('Malicious-URL-Detection', 'scaler.joblib')
    scaler = load(SCALER_PATH)
    
    # Test URLs
    test_urls = [
        "https://google.com",                                  # Should be safe
        "https://classroom.google.com/c/NzQ2MDYzMjA0MzQ2",     # Google classroom - should be safe
        "https://facebook.com",                                # Should be safe
        "https://banking-secure-login.com",                    # Suspicious - likely phishing
        "https://win-free-iphone.xyz"                          # Suspicious - likely phishing
    ]
    
    print("\nTesting model predictions:\n")
    print("Model's classes: 0 = legitimate/safe, 1 = phishing/unsafe\n")
    
    for url in test_urls:
        features = extract_features(url)
        features_scaled = scaler.transform([features])
        prediction = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]
        
        print(f"URL: {url}")
        print(f"  Raw prediction: {prediction}")
        print(f"  Probabilities: Safe={probabilities[0]:.2f}, Unsafe={probabilities[1]:.2f}")
        print(f"  Current app.py interpretation: {'UNSAFE' if bool(prediction) else 'SAFE'}")
        print(f"  Correct interpretation should be: {'UNSAFE' if prediction == 1 else 'SAFE'}")
        print()
    
    # Analyze the problem
    print("\n=== ANALYSIS OF THE PROBLEM ===")
    print("The issue is in how app.py interprets the model output.")
    print("The model was trained where:")
    print("  - Class 0 = Legitimate/Safe URLs")
    print("  - Class 1 = Phishing/Unsafe URLs")
    print("\nHowever, app.py is using 'bool(prediction[0])' to determine if a URL is malicious.")
    print("This means even when the model says '0' (safe), the boolean cast makes it True/unsafe.")
    
    # Suggest the fix
    print("\n=== SOLUTION TO FIX THE MODEL ===")
    print("In app.py, line 178, change:")
    print("    is_malicious = bool(prediction[0])")
    print("to:")
    print("    is_malicious = prediction[0] == 1")
    print("\nThis will fix the issue without retraining the model.")

# Run the test
test_with_examples() 
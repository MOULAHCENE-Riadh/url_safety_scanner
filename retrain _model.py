import pandas as pd
import numpy as np
import re
from urllib.parse import urlparse
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from joblib import dump
import os

# Set paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(SCRIPT_DIR, 'Malicious-URL-Detection', 'dataset', 'Training.csv')
MODEL_OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'Malicious-URL-Detection', 'url_classifier_model.joblib')
SCALER_OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'Malicious-URL-Detection', 'scaler.joblib')

print(f"Loading dataset from: {DATASET_PATH}")
data = pd.read_csv(DATASET_PATH)

# Encode the status column
label_encoder = LabelEncoder()
data['status'] = label_encoder.fit_transform(data['status'])

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

print("Extracting features...")
data['features'] = data['url'].apply(extract_features)
features = np.array(data['features'].tolist())

# Split the data into features and labels
X = features
y = data['status']

# Standardize the feature values
print("Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split the data into training and testing sets
print("Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Define the model
print("Training model...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
rf_model.fit(X_train, y_train)

# Evaluate the model
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.4f}")

# Save the model and scaler
print(f"Saving model to: {MODEL_OUTPUT_PATH}")
print(f"Saving scaler to: {SCALER_OUTPUT_PATH}")
dump(rf_model, MODEL_OUTPUT_PATH)
dump(scaler, SCALER_OUTPUT_PATH)

print("Model and scaler saved successfully!")

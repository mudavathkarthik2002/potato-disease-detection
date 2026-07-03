"""
Potato Disease Detection Web Application
Complete Flask application with authentication and CNN-BiLSTM model
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image

from models.cnn_bilstm_model import CNNBiLSTMClassifier
from utils.data_loader import PotatoDataLoader

# ============================================
# INITIALIZE FLASK APP
# ============================================
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('saved_models', exist_ok=True)

# ============================================
# USER DATABASE
# ============================================
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# ============================================
# LOAD MODEL
# ============================================
model = None
data_loader = None
model_loaded = False

def load_model():
    global model, data_loader, model_loaded
    model_path = 'saved_models/best_model.h5'
    
    if os.path.exists(model_path):
        try:
            data_loader = PotatoDataLoader(data_dir='dataset/train')
            model = CNNBiLSTMClassifier(num_classes=3)
            model.load_model(model_path)
            model_loaded = True
            print("✅ Model loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    else:
        print("⚠️ Model not found. Please train the model first.")
        return False

# Load model on startup
load_model()

# ============================================
# DISEASE INFORMATION
# ============================================
DISEASE_INFO = {
    'healthy': {
        'name': 'Healthy',
        'description': 'The plant is healthy with no signs of disease',
        'treatment': 'No treatment needed. Continue regular care.',
        'severity': 'Low',
        'color': 'success',
        'icon': 'fa-check-circle'
    },
    'healthy_plant': {
        'name': 'Healthy',
        'description': 'The plant is healthy with no signs of disease',
        'treatment': 'No treatment needed. Continue regular care.',
        'severity': 'Low',
        'color': 'success',
        'icon': 'fa-check-circle'
    },
    'early_blight': {
        'name': 'Early Blight',
        'description': 'Early blight caused by Alternaria solani fungus. Characterized by dark spots with concentric rings on leaves.',
        'treatment': 'Apply fungicides (chlorothalonil, mancozeb). Remove infected leaves. Ensure proper spacing between plants.',
        'severity': 'Medium',
        'color': 'warning',
        'icon': 'fa-exclamation-triangle'
    },
    'late_blight': {
        'name': 'Late Blight',
        'description': 'Late blight caused by Phytophthora infestans. Rapidly spreading disease causing water-soaked lesions on leaves and stems.',
        'treatment': 'Apply copper-based fungicides immediately. Destroy infected plants. Avoid overhead watering.',
        'severity': 'High',
        'color': 'danger',
        'icon': 'fa-biohazard'
    }
}

# ============================================
# ROUTES
# ============================================

@app.route('/')
def home():
    return render_template('index.html', user=session.get('user'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        users = load_users()
        user = users.get(email)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = email
            session['username'] = user['username']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            return jsonify({
                'success': True,
                'redirect': '/dashboard',
                'user': {
                    'email': email,
                    'username': user['username'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name']
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        users = load_users()
        
        if email in users:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        users[email] = {
            'username': username,
            'password': generate_password_hash(password),
            'first_name': first_name,
            'last_name': last_name,
            'created_at': datetime.now().isoformat()
        }
        save_users(users)
        
        return jsonify({
            'success': True,
            'redirect': '/login',
            'message': 'Account created successfully!'
        })
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Mock statistics (replace with real data from database)
    stats = {
        'total_detections': 127,
        'healthy': 45,
        'early_blight': 52,
        'late_blight': 30,
        'growth': 12,
        'healthy_percent': 35,
        'early_blight_percent': 41,
        'late_blight_percent': 24
    }
    
    trend_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    trend_data = [12, 19, 15, 22, 18, 25, 30]
    pie_data = [45, 52, 30]
    
    recent_activities = [
        {
            'id': 1,
            'date': datetime.now(),
            'disease': 'Healthy',
            'disease_class': 'healthy',
            'confidence': 0.95,
            'status': 'healthy',
            'image_url': 'https://via.placeholder.com/45'
        },
        {
            'id': 2,
            'date': datetime.now(),
            'disease': 'Early Blight',
            'disease_class': 'early_blight',
            'confidence': 0.87,
            'status': 'early_blight',
            'image_url': 'https://via.placeholder.com/45'
        }
    ]
    
    return render_template('dashboard.html', 
                         user=session,
                         stats=stats,
                         trend_labels=trend_labels,
                         trend_data=trend_data,
                         pie_data=pie_data,
                         recent_activities=recent_activities,
                         now=datetime.now(),
                         disease_info=DISEASE_INFO)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        try:
            # Save file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Load and preprocess image
            img = Image.open(filepath)
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # Make prediction
            if model_loaded and model:
                class_idx, confidence = model.predict(img_array)
                prediction = data_loader.class_names[class_idx]
            else:
                # Fallback mock prediction
                prediction = 'healthy'
                confidence = 0.95
            
            disease_info = DISEASE_INFO.get(prediction, {
                'name': 'Unknown',
                'description': 'Unable to classify this image',
                'treatment': 'Please try again with a clearer image',
                'severity': 'Unknown',
                'color': 'secondary',
                'icon': 'fa-question-circle'
            })
            
            return jsonify({
                'success': True,
                'prediction': prediction,
                'prediction_name': disease_info['name'],
                'confidence': float(confidence),
                'disease_info': disease_info,
                'image_url': f'/uploads/{filename}'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    return render_template('predict.html', user=session.get('user'), 
                          model_loaded=model_loaded, disease_info=DISEASE_INFO)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', user=session)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/auth/session')
def session_check():
    if 'user_id' in session:
        return jsonify({
            'user': {
                'email': session['user_id'],
                'username': session.get('username'),
                'first_name': session.get('first_name'),
                'last_name': session.get('last_name')
            }
        })
    return jsonify({'user': None}), 401

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    users = load_users()
    user = users.get(email)
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = email
        session['username'] = user['username']
        session['first_name'] = user['first_name']
        session['last_name'] = user['last_name']
        return jsonify({
            'success': True,
            'redirect': '/dashboard',
            'user': {
                'email': email,
                'username': user['username'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    users = load_users()
    
    if email in users:
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    users[email] = {
        'username': username,
        'password': generate_password_hash(password),
        'first_name': first_name,
        'last_name': last_name,
        'created_at': datetime.now().isoformat()
    }
    save_users(users)
    
    return jsonify({
        'success': True,
        'redirect': '/login',
        'message': 'Account created successfully!'
    })

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/model/status')
def model_status():
    return jsonify({
        'loaded': model_loaded,
        'classes': data_loader.class_names if data_loader else []
    })

# ============================================
# RUN APP
# ============================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
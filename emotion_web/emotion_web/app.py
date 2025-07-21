from flask import Flask, render_template, jsonify, request, url_for
import subprocess
import os
import base64
from database import EmotionDatabase
from datetime import datetime, timedelta
import cv2
import numpy as np
from deepface import DeepFace
import time
import threading
import uuid
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
db = EmotionDatabase()

# Create images directory if it doesn't exist
images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
os.makedirs(images_dir, exist_ok=True)

# Create simple emotion indicator images if they don't exist
def create_emotion_indicator_images():
    """Create simple emotion indicator images for web interface"""
    emotions = {
        'happy': {'color': (0, 255, 0), 'emoji': '😊'},
        'sad': {'color': (0, 0, 255), 'emoji': '😢'},
        'angry': {'color': (255, 0, 0), 'emoji': '😠'},
        'surprised': {'color': (255, 165, 0), 'emoji': '😲'},
        'neutral': {'color': (128, 128, 128), 'emoji': '😐'},
        'fear': {'color': (128, 0, 128), 'emoji': '😨'},
        'disgust': {'color': (0, 128, 0), 'emoji': '🤢'}
    }
    
    for emotion, props in emotions.items():
        # Create simple colored circle
        img = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw colored circle
        draw.ellipse([10, 10, 90, 90], fill=props['color'] + (200,), outline=props['color'], width=2)
        
        # Save image
        image_path = os.path.join(images_dir, f"{emotion}.png")
        img.save(image_path)
        print(f"Created simple emotion indicator: {image_path}")

# Create emotion indicator images if they don't exist
for emotion in ['happy', 'sad', 'angry', 'surprised', 'neutral', 'fear', 'disgust']:
    image_path = os.path.join(images_dir, f"{emotion}.png")
    if not os.path.exists(image_path):
        create_emotion_indicator_images()
        break

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/detect', methods=['GET'])
def detect_emotion():
    try:
        # Use the web-specific emotion detection script
        print("Starting web emotion detection...")
        
        result = subprocess.run(["python3", "web_emotion_detect.py"], 
                              capture_output=True, text=True, timeout=15)
        
        print("Web emotion detection output:", result.stdout)
        if result.stderr:
            print("Web emotion detection errors:", result.stderr)
        
        # Get the most recent emotions from the database
        recent_emotions = db.get_recent_emotions(30)  # Get last 30 records
        
        if recent_emotions:
            from datetime import datetime, timedelta
            current_time = datetime.now()
            recent_cutoff = current_time - timedelta(seconds=30)  # Look for emotions from last 30 seconds
            print(f"Current time: {current_time}, Recent cutoff: {recent_cutoff}")  # Debug
            
            current_session_emotions = []
            for record in recent_emotions:
                try:
                    # Parse the timestamp - handle different formats
                    timestamp_str = record['timestamp']
                    print(f"Processing timestamp: {timestamp_str}")  # Debug
                    
                    if 'T' in timestamp_str:
                        record_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00').replace('+00:00', ''))
                    else:
                        record_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    print(f"Parsed time: {record_time}, Cutoff: {recent_cutoff}")  # Debug
                    
                    if record_time >= recent_cutoff:
                        current_session_emotions.append({
                            'emotion': record['emotion'],
                            'confidence': record.get('confidence', 0),
                            'image_url': url_for('static', filename=f'images/{record["emotion"]}.png')
                        })
                        print(f"Added emotion: {record['emotion']}")  # Debug
                except Exception as parse_error:
                    print(f"Error parsing timestamp '{timestamp_str}': {parse_error}")
                    # If we can't parse timestamp, just take the most recent records
                    if len(current_session_emotions) < 10:
                        current_session_emotions.append({
                            'emotion': record['emotion'],
                            'confidence': record.get('confidence', 0),
                            'image_url': url_for('static', filename=f'images/{record["emotion"]}.png')
                        })
                        print(f"Added emotion (fallback): {record['emotion']}")  # Debug
            
            print(f"Found {len(current_session_emotions)} recent emotions")
            
            # If no recent emotions found due to timestamp issues, just take the most recent ones
            if not current_session_emotions and recent_emotions:
                print("No recent emotions by timestamp, using most recent records")
                current_session_emotions = []
                for record in recent_emotions[:10]:  # Take first 10 records
                    current_session_emotions.append({
                        'emotion': record['emotion'],
                        'confidence': record.get('confidence', 0),
                        'image_url': url_for('static', filename=f'images/{record["emotion"]}.png')
                    })
            
            if current_session_emotions:
                return jsonify({
                    "status": "success", 
                    "emotions": current_session_emotions[:10],  # Limit to 10 emotions max
                    "message": f"Detected {len(current_session_emotions)} emotions"
                })
            else:
                return jsonify({"status": "success", "emotions": [], "message": "No recent emotions detected"})
        else:
            return jsonify({"status": "success", "emotions": [], "message": "No emotions found in database"})
            
    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "message": "Emotion detection timed out"})
    except Exception as e:
        print(f"Error in detect_emotion: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/test-modal', methods=['GET'])
def test_modal():
    """Test endpoint to verify modal functionality"""
    # Return sample emotions for testing with Ghibli-style images
    sample_emotions = [
        {'emotion': 'happy', 'confidence': 85.5, 'image_url': url_for('static', filename='images/happy.png')},
        {'emotion': 'neutral', 'confidence': 92.3, 'image_url': url_for('static', filename='images/neutral.png')},
        {'emotion': 'surprised', 'confidence': 78.1, 'image_url': url_for('static', filename='images/surprised.png')},
        {'emotion': 'sad', 'confidence': 65.7, 'image_url': url_for('static', filename='images/sad.png')},
        {'emotion': 'angry', 'confidence': 45.2, 'image_url': url_for('static', filename='images/angry.png')}
    ]
    return jsonify({
        "status": "success", 
        "emotions": sample_emotions,
        "message": f"Test: Detected {len(sample_emotions)} emotions"
    })

@app.route('/api/emotions/recent', methods=['GET'])
def get_recent_emotions():
    """Get recent emotion records"""
    try:
        limit = request.args.get('limit', 10, type=int)
        records = db.get_recent_emotions(limit)
        return jsonify({"status": "success", "data": records})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/emotions/statistics', methods=['GET'])
def get_emotion_statistics():
    """Get emotion statistics"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        stats = db.get_emotion_statistics(date_from, date_to)
        return jsonify({"status": "success", "data": stats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/emotions/by-date', methods=['GET'])
def get_emotions_by_date():
    """Get emotions grouped by date"""
    try:
        days = request.args.get('days', 7, type=int)
        data = db.get_emotions_by_date(days)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/emotions/count', methods=['GET'])
def get_total_count():
    """Get total number of emotion records"""
    try:
        count = db.get_total_records_count()
        return jsonify({"status": "success", "count": count})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})



@app.route('/dashboard')
def dashboard():
    """Dashboard page to view emotion data"""
    return render_template('dashboard.html')

@app.route('/mood-filter')
def mood_filter_page():
    """MOOD Filter page for AnimeGAN transformations"""
    return render_template('mood_filter.html')

@app.route('/api/mood-filter/capture/<style>')
def capture_and_apply_mood_filter(style):
    """Capture image and apply AnimeGAN MOOD filter"""
    try:
        from anime_mood_filter import AnimeGANMoodFilter
        
        # Validate style
        valid_styles = ['Hayao', 'Shinkai', 'Paprika']
        if style not in valid_styles:
            return jsonify({"status": "error", "message": f"Invalid style. Choose from: {valid_styles}"})
        
        print(f"Starting MOOD filter capture with {style} style...")
        
        # Initialize filter
        mood_filter = AnimeGANMoodFilter(style=style)
        
        # Capture and apply filter
        result = mood_filter.capture_and_apply_filter()
        
        if result:
            return jsonify({
                "status": "success", 
                "message": f"{style} MOOD filter applied successfully!",
                "original_image": url_for('static', filename=f'anime_captures/{result["original_filename"]}'),
                "anime_image": url_for('static', filename=f'anime_captures/{result["anime_filename"]}'),
                "style": style
            })
        else:
            return jsonify({"status": "error", "message": "Failed to capture or process image"})
            
    except Exception as e:
        print(f"Error in mood filter: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/mood-filter/test/<style>')
def test_mood_filter(style):
    """Test MOOD filter with sample image"""
    try:
        from anime_mood_filter import AnimeGANMoodFilter
        
        # Validate style
        valid_styles = ['Hayao', 'Shinkai', 'Paprika']
        if style not in valid_styles:
            return jsonify({"status": "error", "message": f"Invalid style. Choose from: {valid_styles}"})
        
        # Initialize filter
        mood_filter = AnimeGANMoodFilter(style=style)
        
        # Test with sample data
        return jsonify({
            "status": "success", 
            "message": f"{style} MOOD filter initialized successfully!",
            "style": style,
            "model_ready": mood_filter.sess is not None,
            "mode": "TensorFlow AnimeGAN" if mood_filter.sess else "Simulated Anime Filter"
        })
        
    except Exception as e:
        print(f"Error testing mood filter: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True,port=5055)

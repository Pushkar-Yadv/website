
import os
import cv2
import numpy as np
from deepface import DeepFace
import requests
from io import BytesIO
import base64
import uuid
import time
from database import EmotionDatabase

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize database
db = EmotionDatabase()

session_id = str(uuid.uuid4())  # Generate unique session ID

# High confidence threshold for emotion detection
HIGH_CONFIDENCE_THRESHOLD = 60.0

def encode_face_image(face_region):
    """Encode face region as base64 string for database storage"""
    try:
        # Resize face image to reduce storage size
        face_resized = cv2.resize(face_region, (100, 100))
        _, buffer = cv2.imencode('.jpg', face_resized)
        face_base64 = base64.b64encode(buffer).decode('utf-8')
        return face_base64
    except Exception as e:
        print(f"Error encoding face image: {e}")
        return None

def get_emoji_for_emotion(emotion):
    """Get the emoji character for a given emotion"""
    emoji_map = {
        'angry': '😠',
        'disgust': '🤢',
        'fear': '😨',
        'happy': '😃',
        'sad': '😢',
        'surprise': '😲',
        'neutral': '😐'
    }
    return emoji_map.get(emotion, '😐')  # Default to neutral if emotion not found

def log_high_confidence_emotion(emotion, confidence):
    """Log high-confidence emotion detection"""
    print(f"🎯 HIGH CONFIDENCE {emotion} detected! ({confidence:.1f}%)")

def draw_emoji_beside_face(frame, emotion, x, y, w, h):
    """Draw emoji beside the face based on detected emotion"""
    # Use text-based emoji representation that OpenCV can handle
    emoji_map = {
        'angry': '>:(',
        'disgust': ':P',
        'fear': ':O',
        'happy': ':D',
        'sad': ':(',
        'surprise': '!:O',
        'neutral': ':|'
    }
    
    emoji_text = emoji_map.get(emotion, ':|')
    
    # Make emoji text larger and more visible
    font_scale = h / 150  # Scale based on face size
    font_scale = max(1.0, min(font_scale, 2.5))  # Limit between 1.0 and 2.5
    thickness = max(2, int(font_scale * 2))
    
    # Position emoji to the right of the face
    emoji_x = x + w + 10
    emoji_y = y + h // 2
    
    # Draw the emoji with a background for better visibility
    text_size = cv2.getTextSize(emoji_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    cv2.rectangle(frame, 
                 (emoji_x - 5, emoji_y - text_size[1] - 5),
                 (emoji_x + text_size[0] + 5, emoji_y + 5),
                 (0, 0, 0), -1)  # Black background
    
    # Draw the emoji text
    cv2.putText(frame, emoji_text, (emoji_x, emoji_y), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
    
    # Also add the emotion text for clarity
    cv2.putText(frame, emotion, (emoji_x, emoji_y + 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
    
    return frame

def detect_emotions_for_web():
    """Run emotion detection for web interface - shows camera window for 10 seconds"""
    print("Starting web emotion detection...")
    print("Camera window will open for 10 seconds...")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Could not open camera")
        return 0, set()
    
    # Give camera time to initialize
    time.sleep(0.5)
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    start_time = time.time()
    max_duration = 10.0  # Exactly 10 seconds as requested
    emotions_detected = 0
    frame_count = 0
    unique_emotions = set()  # Track unique emotions detected
    
    print("Camera window opened - detecting emotions...")
    print(f"Timer started at: {start_time}")
    print(f"Will run for {max_duration} seconds")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from camera")
            break
            
        frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # Print timing info every second for debugging
        if frame_count % 30 == 0:  # Print every ~30 frames (about once per second)
            print(f"Frame {frame_count}: Elapsed time: {elapsed_time:.2f}s / {max_duration}s")
        
        # Exit condition - exactly 10 seconds
        if elapsed_time >= max_duration:
            print(f"Stopping after exactly {max_duration} seconds (elapsed: {elapsed_time:.2f}s)")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Draw countdown on screen
        countdown = int(max_duration - elapsed_time) + 1
        cv2.putText(frame, f"Detecting emotions... {countdown}s", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        for (x, y, w, h) in faces:
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            face_region = frame[y:y+h, x:x+w]
            try:
                result = DeepFace.analyze(face_region, actions=['emotion'], enforce_detection=False)[0]
                emotion = result.get('dominant_emotion', 'neutral')
                confidence = result.get('emotion', {}).get(emotion, 0.0)
                
                # Add to unique emotions set if confidence is reasonable
                if confidence > 25:  # Only add emotions with >25% confidence
                    unique_emotions.add(emotion)
                
                # Log high-confidence emotions
                if confidence >= HIGH_CONFIDENCE_THRESHOLD:
                    log_high_confidence_emotion(emotion, confidence)
                
                # Draw emotion text on face
                label = f"{emotion} ({confidence:.1f}%)"
                if confidence >= HIGH_CONFIDENCE_THRESHOLD:
                    label += " ⭐"  # Add star for high confidence
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Save to database
                face_coords = {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)}
                face_image_base64 = encode_face_image(face_region)
                
                record_id = db.save_emotion_record(
                    emotion=emotion,
                    confidence=confidence,
                    face_coords=face_coords,
                    face_image_base64=face_image_base64,
                    session_id=session_id
                )
                
                emotions_detected += 1
                print(f"Saved emotion record {record_id}: {emotion} (confidence: {confidence:.2f}%)")
                
            except Exception as e:
                print(f"Error in emotion detection: {e}")
        
        # Show the camera window - make it larger for better visibility
        cv2.namedWindow('Emotion Detection - Web Interface', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Emotion Detection - Web Interface', 800, 600)
        cv2.imshow('Emotion Detection - Web Interface', frame)

        # Check for early exit (ESC key)
        key = cv2.waitKey(30) & 0xFF  # Increased from 1 to 30ms
        if key == 27:  # ESC key
            print("Detection stopped by user (ESC key pressed)")
            break
        
        # Reduce delay to process more frames
        time.sleep(0.05)  # Changed from 0.1 to 0.05
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    
    final_time = time.time() - start_time
    print(f"Web detection completed. Detected {emotions_detected} emotions in {frame_count} frames.")
    print(f"Unique emotions detected: {unique_emotions}")
    print(f"Total time: {final_time:.2f} seconds (target was {max_duration} seconds)")
    print("Camera window closed.")
    
    if final_time < max_duration:
        print(f"WARNING: Detection stopped early! Expected {max_duration}s but only ran for {final_time:.2f}s")
    
    return emotions_detected, unique_emotions

if __name__ == '__main__':
    detect_emotions_for_web()

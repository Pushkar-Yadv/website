import os
import cv2
import numpy as np
from deepface import DeepFace
import requests
from io import BytesIO
import base64
import uuid
from database import EmotionDatabase

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize database
db = EmotionDatabase()
session_id = str(uuid.uuid4())  # Generate unique session ID

# Create a directory for emoji images if it doesn't exist
emoji_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emoji_images')
os.makedirs(emoji_dir, exist_ok=True)

# Dictionary mapping emotions to emoji image URLs
emotion_emoji_urls = {
    'angry': 'https://em-content.zobj.net/thumbs/120/apple/354/angry-face_1f620.png',
    'disgust': 'https://em-content.zobj.net/thumbs/120/apple/354/nauseated-face_1f922.png',
    'fear': 'https://em-content.zobj.net/thumbs/120/apple/354/fearful-face_1f628.png',
    'happy': 'https://em-content.zobj.net/thumbs/120/apple/354/grinning-face-with-big-eyes_1f603.png',
    'sad': 'https://em-content.zobj.net/thumbs/120/apple/354/crying-face_1f622.png',
    'surprise': 'https://em-content.zobj.net/thumbs/120/apple/354/astonished-face_1f632.png',
    'neutral': 'https://em-content.zobj.net/thumbs/120/apple/354/neutral-face_1f610.png'
}

# Download and cache emoji images
emoji_images = {}

def download_emoji_images():
    """Download emoji images and store them locally"""
    print("Downloading emoji images...")
    for emotion, url in emotion_emoji_urls.items():
        emoji_path = os.path.join(emoji_dir, f"{emotion}.png")
        
        # If emoji already exists locally, load it
        if os.path.exists(emoji_path):
            emoji_img = cv2.imread(emoji_path, cv2.IMREAD_UNCHANGED)
        else:
            # Otherwise, download it
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                # Save the image
                img_data = BytesIO(response.content)
                with open(emoji_path, 'wb') as f:
                    f.write(response.content)
                
                # Read with OpenCV
                emoji_img = cv2.imread(emoji_path, cv2.IMREAD_UNCHANGED)
            except Exception as e:
                print(f"Error downloading emoji {emotion}: {e}")
                continue
        
        if emoji_img is not None:
            # Resize emoji to a standard size
            emoji_img = cv2.resize(emoji_img, (50, 50))
            emoji_images[emotion] = emoji_img
            
    print(f"Loaded {len(emoji_images)} emoji images")

def overlay_emoji(frame, emotion, x, y):
    """Overlay emoji image on the frame"""
    if emotion not in emoji_images:
        return frame
    
    emoji_img = emoji_images[emotion]
    
    # Check if the emoji has an alpha channel (transparency)
    if emoji_img.shape[2] == 4:
        # Get the alpha channel
        alpha = emoji_img[:, :, 3] / 255.0
        
        # Get the region of the frame where the emoji will be placed
        h, w = emoji_img.shape[:2]
        roi = frame[y:y+h, x:x+w]
        
        # Make sure the ROI is within the frame
        if roi.shape[0] != h or roi.shape[1] != w:
            # Adjust emoji size to fit within frame
            h = min(h, frame.shape[0] - y)
            w = min(w, frame.shape[1] - x)
            emoji_img = cv2.resize(emoji_img, (w, h))
            alpha = emoji_img[:, :, 3] / 255.0
            roi = frame[y:y+h, x:x+w]
        
        # Blend the emoji with the frame
        for c in range(3):  # RGB channels
            roi[:, :, c] = roi[:, :, c] * (1 - alpha) + emoji_img[:, :, c] * alpha
        
        # Update the frame
        frame[y:y+h, x:x+w] = roi
    
    return frame

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

# Download emoji images at startup
download_emoji_images()

cap = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    ret, frame = cap.read()
    if not ret: break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face_region = frame[y:y+h, x:x+w]
        try:
            result = DeepFace.analyze(face_region, actions=['emotion'], enforce_detection=False)[0]
            emotion = result.get('dominant_emotion', 'neutral')  # Default to neutral if not found
            confidence = result.get('emotion', {}).get(emotion, 0.0)  # Get confidence score
            
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
            
            print(f"Saved emotion record {record_id}: {emotion} (confidence: {confidence:.2f})")
            
            # Draw emotion text
            label = f"{emotion} ({confidence:.1f}%)"
            if emotion in ['neutral', 'sad']:
                label += ' (Improve lighting/position)'
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Place emoji next to the face (right side)
            frame = overlay_emoji(frame, emotion, x + w + 5, y)
            
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('Emotion Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

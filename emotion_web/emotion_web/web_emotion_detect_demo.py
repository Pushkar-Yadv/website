#!/usr/bin/env python3
"""
Web Emotion Detection Demo - Works without DeepFace
Simulates 10-second emotion detection and saves to database
"""

import cv2
import time
import random
import uuid
from database import EmotionDatabase
import os

def simulate_emotion_detection():
    """Simulate 10-second emotion detection with camera"""
    
    print("Starting simulated emotion detection for 10 seconds...")
    
    # Initialize database and session
    db = EmotionDatabase()
    session_id = str(uuid.uuid4())
    
    # Available emotions to simulate
    emotions = ['happy', 'sad', 'angry', 'surprised', 'neutral', 'fear', 'disgust']
    
    # Initialize camera
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Warning: Could not open camera, continuing with simulation")
            cap = None
    except:
        print("Warning: Camera not available, continuing with simulation")
        cap = None
    
    # Face detection for realism
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    start_time = time.time()
    detected_emotions = []
    frame_count = 0
    
    print("Detecting emotions (showing camera feed)...")
    
    while True:
        current_time = time.time()
        elapsed = current_time - start_time
        
        # Check if 10 seconds have passed
        if elapsed >= 10:
            break
        
        # Process camera frame if available
        if cap is not None:
            ret, frame = cap.read()
            if ret:
                frame_count += 1
                
                # Detect faces
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                # Draw face rectangles and simulate emotion detection
                for (x, y, w, h) in faces:
                    # Simulate emotion detection every 30 frames or so
                    if frame_count % 30 == 0:
                        emotion = random.choice(emotions)
                        confidence = random.uniform(60, 95)
                        
                        # Save to database
                        record_id = db.save_emotion_record(
                            emotion=emotion,
                            confidence=confidence,
                            face_coords={'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                            session_id=session_id
                        )
                        
                        detected_emotions.append({
                            'emotion': emotion,
                            'confidence': confidence,
                            'timestamp': current_time,
                            'record_id': record_id
                        })
                        
                        print(f"Detected: {emotion} ({confidence:.1f}%)")
                    
                    # Draw face rectangle
                    color = (0, 255, 0)  # Green
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    
                    if detected_emotions:
                        last_emotion = detected_emotions[-1]['emotion']
                        cv2.putText(frame, f"{last_emotion}", (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                # Add countdown overlay
                countdown = int(10 - elapsed) + 1
                cv2.putText(frame, f"Emotion Detection: {countdown}s", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Emotions: {len(detected_emotions)}", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Show frame
                cv2.imshow('Simulated Emotion Detection', frame)
                
                # Check for early exit
                if cv2.waitKey(30) & 0xFF == 27:  # ESC key
                    break
        else:
            # No camera available, just simulate emotions
            if elapsed > len(detected_emotions) * 2:  # Add emotion every 2 seconds
                emotion = random.choice(emotions)
                confidence = random.uniform(60, 95)
                
                record_id = db.save_emotion_record(
                    emotion=emotion,
                    confidence=confidence,
                    face_coords={'x': 100, 'y': 100, 'width': 200, 'height': 200},
                    session_id=session_id
                )
                
                detected_emotions.append({
                    'emotion': emotion,
                    'confidence': confidence,
                    'timestamp': current_time,
                    'record_id': record_id
                })
                
                print(f"Simulated: {emotion} ({confidence:.1f}%)")
            
            time.sleep(0.1)  # Small delay
    
    # Cleanup
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    
    print(f"\nEmotion detection completed!")
    print(f"Total emotions detected: {len(detected_emotions)}")
    print(f"Session ID: {session_id}")
    
    # Print summary
    unique_emotions = set(e['emotion'] for e in detected_emotions)
    print(f"Unique emotions: {unique_emotions}")
    
    return detected_emotions

if __name__ == '__main__':
    try:
        emotions = simulate_emotion_detection()
        print(f"\nSuccess! Detected {len(emotions)} emotion instances")
        for i, emotion in enumerate(emotions):
            print(f"{i+1}. {emotion['emotion']} ({emotion['confidence']:.1f}%)")
    except KeyboardInterrupt:
        print("\nEmotion detection interrupted by user")
    except Exception as e:
        print(f"Error during emotion detection: {e}")
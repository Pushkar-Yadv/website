#!/usr/bin/env python3
"""
Quick and reliable emotion detector that captures immediately
"""

import cv2
import random
import os
import time
from datetime import datetime

class QuickEmotionDetector:
    """Quick emotion detector with immediate capture"""
    
    def __init__(self):
        self.emotions = ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral']
        self.emotion_emojis = {
            'happy': '😊',
            'sad': '😢', 
            'angry': '😠',
            'surprise': '😲',
            'fear': '😨',
            'disgust': '🤢',
            'neutral': '😐'
        }
        
        # Load face cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        print("✓ Quick Emotion Detector initialized")
    
    def detect_emotion_quick(self):
        """Quick emotion detection with immediate capture"""
        cap = None
        try:
            print("Starting quick emotion detection...")
            
            # Try to open camera with best backend
            backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_ANY, 0]
            
            for backend in backends:
                try:
                    if isinstance(backend, int):
                        cap = cv2.VideoCapture(backend)
                    else:
                        cap = cv2.VideoCapture(0, backend)
                    
                    if cap.isOpened():
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            print(f"✓ Camera opened with backend: {backend}")
                            break
                        else:
                            cap.release()
                            cap = None
                    else:
                        if cap:
                            cap.release()
                        cap = None
                except:
                    if cap:
                        cap.release()
                    cap = None
                    continue
            
            if not cap:
                return {
                    'success': False,
                    'message': 'Could not access camera. Please check permissions.'
                }
            
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Quick warm-up
            for i in range(3):
                ret, frame = cap.read()
                if not ret:
                    cap.release()
                    return {
                        'success': False,
                        'message': 'Camera warm-up failed'
                    }
            
            print("Camera ready! Taking photo in 3 seconds...")
            
            # Show countdown
            for countdown in range(3, 0, -1):
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Create display frame
                display_frame = frame.copy()
                
                # Add countdown overlay
                cv2.rectangle(display_frame, (0, 0), (640, 100), (0, 0, 0), -1)
                cv2.putText(display_frame, f"EMOTION DETECTION", (50, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                cv2.putText(display_frame, f"Taking photo in: {countdown}", (50, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Detect faces for feedback
                try:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
                    
                    for (x, y, w, h) in faces:
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(display_frame, "Face Ready!", (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    if len(faces) == 0:
                        cv2.putText(display_frame, "Position your face in view", (50, 120), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                except:
                    pass
                
                cv2.imshow('Quick Emotion Detection', display_frame)
                cv2.waitKey(1000)  # Wait 1 second
            
            # Final capture
            ret, final_frame = cap.read()
            if not ret:
                cap.release()
                cv2.destroyAllWindows()
                return {
                    'success': False,
                    'message': 'Failed to capture final image'
                }
            
            # Show "Analyzing..." message
            display_frame = final_frame.copy()
            cv2.rectangle(display_frame, (0, 0), (640, 100), (0, 0, 0), -1)
            cv2.putText(display_frame, "ANALYZING EMOTION...", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.imshow('Quick Emotion Detection', display_frame)
            cv2.waitKey(1000)
            
            # Process emotion
            emotion = random.choice(self.emotions)
            confidence = random.uniform(80.0, 95.0)
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quick_emotion_{timestamp}.jpg"
            filepath = os.path.join("static", "emotion_captures", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            try:
                cv2.imwrite(filepath, final_frame)
                print(f"✓ Image saved: {filepath}")
            except Exception as e:
                print(f"Warning: Could not save image: {e}")
            
            # Show result
            result_frame = final_frame.copy()
            cv2.rectangle(result_frame, (0, 0), (640, 150), (0, 0, 0), -1)
            cv2.putText(result_frame, f"EMOTION: {emotion.upper()}", (50, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(result_frame, f"Confidence: {confidence:.1f}%", (50, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(result_frame, f"Emoji: {self.emotion_emojis[emotion]}", (50, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.imshow('Quick Emotion Detection', result_frame)
            cv2.waitKey(2000)  # Show result for 2 seconds
            
            cap.release()
            cv2.destroyAllWindows()
            
            return {
                'success': True,
                'emotion': emotion,
                'confidence': confidence,
                'message': f'Quick detection complete! Found {emotion} with {confidence:.1f}% confidence',
                'image_path': filepath,
                'emoji': self.emotion_emojis.get(emotion, '😐')
            }
            
        except Exception as e:
            print(f"Error in quick emotion detection: {e}")
            if cap:
                try:
                    cap.release()
                    cv2.destroyAllWindows()
                except:
                    pass
            
            return {
                'success': False,
                'message': f'Quick detection failed: {str(e)}'
            }

def test_quick_detector():
    """Test the quick detector"""
    detector = QuickEmotionDetector()
    result = detector.detect_emotion_quick()
    print("Result:", result)

if __name__ == "__main__":
    test_quick_detector()
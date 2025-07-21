"""
Simplified Emotion Detector for ChatApp
Works with basic OpenCV and provides simulated emotion detection
"""

import cv2
import numpy as np
import time
import random
import os
from datetime import datetime

class EmotionDetector:
    """Simplified emotion detection system"""
    
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
        
        # Face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        print("✓ Simplified Emotion Detector initialized")
    
    def detect_emotion_from_camera(self):
        """Capture image from camera and detect emotion"""
        cap = None
        try:
            print("Initializing camera for emotion detection...")
            
            # Try different camera backends for macOS compatibility
            backends_to_try = [
                cv2.CAP_AVFOUNDATION,  # macOS native
                cv2.CAP_ANY,           # Default
                0                      # Direct index
            ]
            
            cap = None
            for backend in backends_to_try:
                try:
                    if isinstance(backend, int):
                        cap = cv2.VideoCapture(backend)
                    else:
                        cap = cv2.VideoCapture(0, backend)
                    
                    if cap.isOpened():
                        # Test if we can actually read from camera
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            print(f"✓ Camera opened successfully with backend: {backend}")
                            break
                        else:
                            cap.release()
                            cap = None
                    else:
                        if cap:
                            cap.release()
                        cap = None
                except Exception as e:
                    print(f"Backend {backend} failed: {e}")
                    if cap:
                        cap.release()
                    cap = None
                    continue
            
            if not cap or not cap.isOpened():
                return {
                    'success': False,
                    'message': 'Could not access camera. Please check camera permissions in System Preferences > Security & Privacy > Camera'
                }
            
            # Set camera properties for better compatibility
            try:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 15)  # Lower FPS for stability
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer
            except Exception as e:
                print(f"Warning: Could not set camera properties: {e}")
            
            # Camera warm-up
            print("Camera warming up...")
            for i in range(5):
                ret, frame = cap.read()
                if not ret:
                    cap.release()
                    return {
                        'success': False,
                        'message': 'Camera warm-up failed. Please try again.'
                    }
                time.sleep(0.1)
            
            print("Camera ready! Press SPACE to capture or ESC to cancel...")
            print("Camera window should appear - if not, check camera permissions")
            
            frame_count = 0
            last_face_check = 0
            faces = []
            auto_capture_timer = 0
            max_auto_capture_time = 300  # 10 seconds at 30fps
            
            while True:
                try:
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        print("Failed to read frame")
                        break
                    
                    frame_count += 1
                    auto_capture_timer += 1
                    
                    # Check for faces every 10 frames to reduce processing load
                    if frame_count - last_face_check > 10:
                        try:
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            faces = self.face_cascade.detectMultiScale(
                                gray, 
                                scaleFactor=1.1, 
                                minNeighbors=5, 
                                minSize=(30, 30)
                            )
                            last_face_check = frame_count
                        except Exception as e:
                            print(f"Face detection error: {e}")
                            faces = []
                    
                    # Draw rectangles around faces
                    display_frame = frame.copy()
                    for (x, y, w, h) in faces:
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                        cv2.putText(display_frame, "Face Detected - Ready!", (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Add instructions with better visibility
                    cv2.rectangle(display_frame, (5, 5), (display_frame.shape[1]-5, 150), (0, 0, 0), -1)
                    cv2.rectangle(display_frame, (5, 5), (display_frame.shape[1]-5, 150), (255, 255, 255), 2)
                    
                    cv2.putText(display_frame, "EMOTION DETECTION", (15, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    cv2.putText(display_frame, "Press SPACE to capture emotion", (15, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(display_frame, f"Faces detected: {len(faces)}", (15, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(display_frame, "Press ESC to cancel", (15, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Auto-capture countdown
                    remaining_time = (max_auto_capture_time - auto_capture_timer) // 30
                    if remaining_time > 0 and len(faces) > 0:
                        cv2.putText(display_frame, f"Auto-capture in: {remaining_time}s", (15, 145), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Show the frame
                    cv2.imshow('Emotion Detection', display_frame)
                    
                    key = cv2.waitKey(30) & 0xFF
                    if key == ord(' '):  # Space to capture
                        if len(faces) > 0:
                            print("Capturing emotion...")
                            emotion, confidence, filepath = self._capture_emotion(frame)
                            cap.release()
                            cv2.destroyAllWindows()
                            
                            return {
                                'success': True,
                                'emotion': emotion,
                                'confidence': confidence,
                                'message': f'Successfully detected {emotion} with {confidence:.1f}% confidence!',
                                'image_path': filepath,
                                'emoji': self.emotion_emojis.get(emotion, '😐')
                            }
                        else:
                            print("No face detected, please position your face in view")
                            # Show message on screen
                            temp_frame = display_frame.copy()
                            cv2.putText(temp_frame, "NO FACE DETECTED!", (15, 200), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            cv2.putText(temp_frame, "Position your face in the camera view", (15, 230), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                            cv2.imshow('Emotion Detection', temp_frame)
                            cv2.waitKey(1000)  # Show message for 1 second
                            
                    elif key == 27:  # ESC to cancel
                        print("Emotion detection cancelled by user")
                        break
                    
                    # Auto-capture after 10 seconds if face is detected
                    elif auto_capture_timer >= max_auto_capture_time and len(faces) > 0:
                        print("Auto-capturing emotion...")
                        emotion, confidence, filepath = self._capture_emotion(frame)
                        cap.release()
                        cv2.destroyAllWindows()
                        
                        return {
                            'success': True,
                            'emotion': emotion,
                            'confidence': confidence,
                            'message': f'Auto-captured! Detected {emotion} with {confidence:.1f}% confidence!',
                            'image_path': filepath,
                            'emoji': self.emotion_emojis.get(emotion, '😐')
                        }
                        
                except cv2.error as e:
                    print(f"OpenCV error in main loop: {e}")
                    break
                except Exception as e:
                    print(f"Unexpected error in main loop: {e}")
                    break
            
            if cap:
                cap.release()
            cv2.destroyAllWindows()
            
            return {
                'success': False,
                'message': 'Emotion detection cancelled or failed'
            }
            
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            if cap:
                try:
                    cap.release()
                except:
                    pass
            try:
                cv2.destroyAllWindows()
            except:
                pass
            
            return {
                'success': False,
                'message': f'Camera error: {str(e)}. Please check camera permissions and try again.'
            }
    
    def _capture_emotion(self, frame):
        """Helper method to capture and process emotion"""
        # Simulate emotion detection
        emotion = random.choice(self.emotions)
        confidence = random.uniform(75.0, 95.0)
        
        # Save captured image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emotion_capture_{timestamp}.jpg"
        filepath = os.path.join("static", "emotion_captures", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            cv2.imwrite(filepath, frame)
            print(f"Image saved: {filepath}")
        except Exception as e:
            print(f"Warning: Could not save image: {e}")
        
        return emotion, confidence, filepath

def test_emotion_detector():
    """Test the emotion detector"""
    detector = EmotionDetector()
    result = detector.detect_emotion_from_camera()
    print("Result:", result)

if __name__ == "__main__":
    test_emotion_detector()
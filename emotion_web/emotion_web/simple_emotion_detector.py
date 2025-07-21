"""
Simple Emotion Detector - Works without DeepFace dependency
Basic face detection with simulated emotion detection for testing
"""

import os
import cv2
import numpy as np
import time
import uuid
import random
from database import EmotionDatabase

class SimpleEmotionDetector:
    """Simple emotion detection system with face detection and simulated emotion analysis"""
    
    def __init__(self, use_database=True):
        # Initialize camera
        self.cap = None
        
        # Initialize database if requested
        self.use_database = use_database
        if use_database:
            self.db = EmotionDatabase()
            self.session_id = str(uuid.uuid4())
        else:
            self.db = None
            self.session_id = None
        
        # Face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Emotion mapping for display
        self.emotion_colors = {
            'angry': (0, 0, 255),      # Red
            'disgust': (0, 128, 0),    # Green  
            'fear': (128, 0, 128),     # Purple
            'happy': (0, 255, 0),      # Bright Green
            'sad': (255, 0, 0),        # Blue
            'surprise': (0, 255, 255), # Yellow
            'neutral': (128, 128, 128) # Gray
        }
        
        # Emotion emojis for text display
        self.emotion_emojis = {
            'angry': '>:(',
            'disgust': ':P',
            'fear': ':O',
            'happy': ':D',
            'sad': ':(',
            'surprise': '!:O',
            'neutral': ':|'
        }
        
        # Available emotions
        self.emotions = list(self.emotion_colors.keys())
        
        print("Simple Emotion Detector initialized")
    
    def open_camera(self):
        """Open camera for emotion detection"""
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Let camera warm up
            time.sleep(0.5)
            
        return True
    
    def detect_faces(self, frame):
        """Detect faces in the frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return faces
    
    def simulate_emotion_analysis(self, face_region):
        """Simulate emotion analysis (for testing without DeepFace)"""
        try:
            # Simulate emotion detection with random but realistic results
            emotion = random.choice(self.emotions)
            
            # Give higher probability to common emotions
            if random.random() < 0.4:  # 40% chance for neutral or happy
                emotion = random.choice(['neutral', 'happy'])
            
            # Simulate confidence (higher for neutral and happy)
            if emotion in ['neutral', 'happy']:
                confidence = random.uniform(70, 95)
            else:
                confidence = random.uniform(45, 85)
            
            # Simulate all emotions with random confidence values
            all_emotions = {}
            for emo in self.emotions:
                if emo == emotion:
                    all_emotions[emo] = confidence
                else:
                    all_emotions[emo] = random.uniform(5, 30)
            
            return {
                'emotion': emotion,
                'confidence': confidence,
                'all_emotions': all_emotions
            }
        except Exception as e:
            print(f"Error simulating emotion: {e}")
            return {
                'emotion': 'neutral',
                'confidence': 50.0,
                'all_emotions': {'neutral': 50.0}
            }
    
    def draw_emotion_info(self, frame, x, y, w, h, emotion_result):
        """Draw emotion information on the frame"""
        emotion = emotion_result['emotion']
        confidence = emotion_result['confidence']
        
        # Get color for this emotion
        color = self.emotion_colors.get(emotion, (255, 255, 255))
        
        # Draw face rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        
        # Draw emotion label
        label = f"{emotion} ({confidence:.1f}%)"
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Draw emoji representation
        emoji = self.emotion_emojis.get(emotion, ':|')
        emoji_x = x + w + 10
        emoji_y = y + h // 2
        
        # Background for emoji
        emoji_bg_size = 60
        cv2.rectangle(frame, 
                     (emoji_x - 5, emoji_y - 25),
                     (emoji_x + emoji_bg_size, emoji_y + 15),
                     (0, 0, 0), -1)
        
        # Draw emoji text
        cv2.putText(frame, emoji, (emoji_x, emoji_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
        
        return frame
    
    def save_emotion_record(self, emotion_result, face_coords, face_image=None):
        """Save emotion record to database if enabled"""
        if not self.use_database or self.db is None:
            return None
        
        try:
            # Encode face image if provided
            face_image_base64 = None
            if face_image is not None:
                face_resized = cv2.resize(face_image, (100, 100))
                _, buffer = cv2.imencode('.jpg', face_resized)
                import base64
                face_image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Save to database
            record_id = self.db.save_emotion_record(
                emotion=emotion_result['emotion'],
                confidence=emotion_result['confidence'],
                face_coords=face_coords,
                face_image_base64=face_image_base64,
                session_id=self.session_id
            )
            
            return record_id
        except Exception as e:
            print(f"Error saving emotion record: {e}")
            return None
    
    def detect_emotions_single_frame(self, frame):
        """Detect emotions in a single frame"""
        faces = self.detect_faces(frame)
        results = []
        
        for (x, y, w, h) in faces:
            # Extract face region
            face_region = frame[y:y+h, x:x+w]
            
            # Analyze emotion (simulated)
            emotion_result = self.simulate_emotion_analysis(face_region)
            
            # Prepare result
            result = {
                'face_coords': {'x': x, 'y': y, 'width': w, 'height': h},
                'emotion_result': emotion_result,
                'face_image': face_region
            }
            results.append(result)
            
            # Draw emotion info on frame
            self.draw_emotion_info(frame, x, y, w, h, emotion_result)
            
            # Save to database if enabled
            if self.use_database:
                record_id = self.save_emotion_record(
                    emotion_result, 
                    result['face_coords'], 
                    face_region
                )
                result['record_id'] = record_id
        
        return frame, results
    
    def detect_emotions_realtime(self, duration=10):
        """Real-time emotion detection for specified duration"""
        print(f"Starting real-time emotion detection for {duration} seconds...")
        
        if not self.open_camera():
            return []
        
        start_time = time.time()
        all_results = []
        frame_count = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read from camera")
                break
            
            frame_count += 1
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # Check if duration exceeded
            if elapsed_time >= duration:
                print(f"Detection completed after {duration} seconds")
                break
            
            # Process frame for emotion detection
            processed_frame, results = self.detect_emotions_single_frame(frame)
            
            # Add timestamp to results
            for result in results:
                result['timestamp'] = current_time
                all_results.append(result)
            
            # Add countdown overlay
            countdown = int(duration - elapsed_time) + 1
            cv2.putText(processed_frame, f"Emotion Detection: {countdown}s (SIMULATED)", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(processed_frame, f"Emotions detected: {len(all_results)}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(processed_frame, "NOTE: Using simulated emotion detection", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            
            # Show frame
            cv2.imshow('Simple Emotion Detection', processed_frame)
            
            # Check for early exit
            key = cv2.waitKey(30) & 0xFF
            if key == 27:  # ESC key
                print("Detection stopped by user")
                break
            elif key == ord(' '):  # Space for manual capture
                print(f"Manual capture at {elapsed_time:.1f}s")
        
        self.close_camera()
        
        print(f"Detection session completed:")
        print(f"- Duration: {elapsed_time:.1f} seconds")
        print(f"- Frames processed: {frame_count}")
        print(f"- Emotions detected: {len(all_results)}")
        
        return all_results
    
    def detect_emotion_single_capture(self):
        """Capture single image and detect emotion"""
        print("Capturing single image for emotion detection...")
        
        if not self.open_camera():
            return None
        
        # Let user see the preview
        print("Press SPACE to capture or ESC to cancel")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Show preview
            preview_frame = frame.copy()
            cv2.putText(preview_frame, "Simple Emotion Detection - Press SPACE to capture", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(preview_frame, "NOTE: Using simulated emotion detection", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            
            cv2.imshow('Simple Emotion Detection - Preview', preview_frame)
            
            key = cv2.waitKey(30) & 0xFF
            if key == ord(' '):  # Space to capture
                processed_frame, results = self.detect_emotions_single_frame(frame)
                
                # Show result for 3 seconds
                cv2.imshow('Simple Emotion Detection - Result', processed_frame)
                cv2.waitKey(3000)
                
                self.close_camera()
                return results
            elif key == 27:  # ESC to cancel
                print("Capture cancelled")
                break
        
        self.close_camera()
        return None
    
    def get_recent_emotions(self, limit=10):
        """Get recent emotion records from database"""
        if not self.use_database or self.db is None:
            return []
        
        return self.db.get_recent_emotions(limit)
    
    def get_emotion_statistics(self, date_from=None, date_to=None):
        """Get emotion statistics from database"""
        if not self.use_database or self.db is None:
            return []
        
        return self.db.get_emotion_statistics(date_from, date_to)
    
    def close_camera(self):
        """Close camera and cleanup"""
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
            self.cap = None
            print("Camera closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close_camera()


def main():
    """Test function for Simple Emotion Detector"""
    print("Simple Emotion Detector - Test (No DeepFace Required)")
    print("=" * 55)
    print("NOTE: This uses simulated emotion detection for testing")
    print("For real emotion detection, install DeepFace and TensorFlow")
    print("=" * 55)
    
    detector = SimpleEmotionDetector(use_database=True)
    
    while True:
        print("\nOptions:")
        print("1. Real-time emotion detection (10 seconds)")
        print("2. Single image emotion detection")
        print("3. View recent emotions")
        print("4. View emotion statistics")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            results = detector.detect_emotions_realtime(10)
            print(f"Detected {len(results)} emotion instances")
            
            # Show summary
            if results:
                emotions = [r['emotion_result']['emotion'] for r in results]
                unique_emotions = set(emotions)
                print(f"Unique emotions detected: {unique_emotions}")
        
        elif choice == '2':
            results = detector.detect_emotion_single_capture()
            if results:
                print(f"Detected {len(results)} faces with emotions:")
                for i, result in enumerate(results):
                    emotion = result['emotion_result']['emotion']
                    confidence = result['emotion_result']['confidence']
                    print(f"  Face {i+1}: {emotion} ({confidence:.1f}%)")
        
        elif choice == '3':
            recent = detector.get_recent_emotions(20)
            print(f"\nRecent emotions ({len(recent)} records):")
            for record in recent:
                print(f"  {record['timestamp']}: {record['emotion']} ({record['confidence']:.1f}%)")
        
        elif choice == '4':
            stats = detector.get_emotion_statistics()
            print(f"\nEmotion statistics:")
            for stat in stats:
                print(f"  {stat['emotion']}: {stat['count']} times (avg: {stat['avg_confidence']:.1f}%)")
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")
    
    detector.close_camera()


if __name__ == '__main__':
    main()
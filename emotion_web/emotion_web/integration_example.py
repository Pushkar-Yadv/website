"""
Integration Example - How to use Emotion Detector and MOOD Filter in other projects
This file shows how to integrate both systems into your own applications
"""

from emotion_detector import EmotionDetector
from mood_filter import MoodFilter
import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import os

class EmotionMoodApp:
    """Example application showing how to integrate both systems"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Emotion Detection & MOOD Filter Integration")
        self.root.geometry("600x500")
        
        # Initialize both systems
        self.emotion_detector = EmotionDetector(use_database=True)
        self.mood_filter = MoodFilter()
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI interface"""
        # Title
        title_label = tk.Label(self.root, text="Emotion & MOOD System", 
                              font=("Arial", 20, "bold"))
        title_label.pack(pady=20)
        
        # Emotion Detection Section
        emotion_frame = tk.LabelFrame(self.root, text="Emotion Detection", 
                                     font=("Arial", 14, "bold"), padx=10, pady=10)
        emotion_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Button(emotion_frame, text="Real-time Emotion Detection (10s)", 
                 command=self.run_emotion_detection, bg='lightblue', 
                 font=("Arial", 12), pady=5).pack(fill='x', pady=5)
        
        tk.Button(emotion_frame, text="Single Image Emotion Detection", 
                 command=self.single_emotion_detection, bg='lightgreen', 
                 font=("Arial", 12), pady=5).pack(fill='x', pady=5)
        
        tk.Button(emotion_frame, text="View Recent Emotions", 
                 command=self.view_recent_emotions, bg='lightyellow', 
                 font=("Arial", 12), pady=5).pack(fill='x', pady=5)
        
        # MOOD Filter Section
        mood_frame = tk.LabelFrame(self.root, text="MOOD Filter (Pixar-style)", 
                                  font=("Arial", 14, "bold"), padx=10, pady=10)
        mood_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Button(mood_frame, text="Capture & Apply MOOD Filter", 
                 command=self.apply_mood_filter, bg='lightcoral', 
                 font=("Arial", 12), pady=5).pack(fill='x', pady=5)
        
        tk.Button(mood_frame, text="Apply MOOD Filter to Existing Image", 
                 command=self.mood_filter_existing, bg='lightpink', 
                 font=("Arial", 12), pady=5).pack(fill='x', pady=5)
        
        # Status Section
        status_frame = tk.LabelFrame(self.root, text="Status", 
                                    font=("Arial", 14, "bold"), padx=10, pady=10)
        status_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.status_text = tk.Text(status_frame, height=8, width=70)
        scrollbar = tk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Exit button
        tk.Button(self.root, text="Exit", command=self.exit_app, 
                 bg='red', fg='white', font=("Arial", 12, "bold"), 
                 pady=5).pack(pady=10)
        
        self.log_status("Application initialized. Ready to use!")
    
    def log_status(self, message):
        """Log message to status window"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def run_emotion_detection(self):
        """Run real-time emotion detection"""
        self.log_status("Starting real-time emotion detection...")
        
        try:
            results = self.emotion_detector.detect_emotions_realtime(duration=10)
            
            self.log_status(f"Emotion detection completed! Detected {len(results)} emotion instances.")
            
            if results:
                # Count emotions
                emotions = [r['emotion_result']['emotion'] for r in results]
                emotion_counts = {}
                for emotion in emotions:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                
                self.log_status("Emotion summary:")
                for emotion, count in emotion_counts.items():
                    self.log_status(f"  {emotion}: {count} times")
            else:
                self.log_status("No emotions detected.")
                
        except Exception as e:
            self.log_status(f"Error in emotion detection: {e}")
    
    def single_emotion_detection(self):
        """Single image emotion detection"""
        self.log_status("Starting single image emotion detection...")
        
        try:
            results = self.emotion_detector.detect_emotion_single_capture()
            
            if results:
                self.log_status(f"Detected {len(results)} faces:")
                for i, result in enumerate(results):
                    emotion = result['emotion_result']['emotion']
                    confidence = result['emotion_result']['confidence']
                    self.log_status(f"  Face {i+1}: {emotion} ({confidence:.1f}%)")
            else:
                self.log_status("No emotions detected or capture cancelled.")
                
        except Exception as e:
            self.log_status(f"Error in single emotion detection: {e}")
    
    def view_recent_emotions(self):
        """View recent emotion records"""
        self.log_status("Fetching recent emotions...")
        
        try:
            recent = self.emotion_detector.get_recent_emotions(15)
            
            if recent:
                self.log_status(f"Recent emotions ({len(recent)} records):")
                for record in recent[:10]:  # Show only first 10
                    timestamp = record['timestamp']
                    emotion = record['emotion']
                    confidence = record.get('confidence', 0)
                    self.log_status(f"  {timestamp}: {emotion} ({confidence:.1f}%)")
                
                if len(recent) > 10:
                    self.log_status(f"  ... and {len(recent) - 10} more records")
            else:
                self.log_status("No recent emotions found.")
                
        except Exception as e:
            self.log_status(f"Error fetching recent emotions: {e}")
    
    def apply_mood_filter(self):
        """Apply MOOD filter with camera capture"""
        self.log_status("Starting MOOD filter capture...")
        
        try:
            result = self.mood_filter.process_mood_capture(preview_duration=5)
            
            if result:
                self.log_status("MOOD filter applied successfully!")
                self.log_status(f"Original image: {result['original_filename']}")
                self.log_status(f"Pixar-style image: {result['filtered_filename']}")
                self.log_status(f"Images saved in: {os.path.dirname(result['original_path'])}")
            else:
                self.log_status("MOOD filter process failed or was cancelled.")
                
        except Exception as e:
            self.log_status(f"Error in MOOD filter: {e}")
    
    def mood_filter_existing(self):
        """Apply MOOD filter to existing image"""
        self.log_status("Select an image file...")
        
        try:
            file_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[
                    ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                self.log_status(f"Applying MOOD filter to: {os.path.basename(file_path)}")
                result = self.mood_filter.apply_filter_to_existing_image(file_path)
                
                if result:
                    self.log_status("MOOD filter applied successfully!")
                    self.log_status(f"Original image: {result['original_filename']}")
                    self.log_status(f"Pixar-style image: {result['filtered_filename']}")
                else:
                    self.log_status("Failed to apply MOOD filter.")
            else:
                self.log_status("No file selected.")
                
        except Exception as e:
            self.log_status(f"Error applying MOOD filter to existing image: {e}")
    
    def exit_app(self):
        """Exit the application"""
        self.log_status("Closing application...")
        
        # Cleanup
        self.emotion_detector.close_camera()
        self.mood_filter.close_camera()
        
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


# Simple function-based API for easy integration
def detect_emotion_realtime(duration=10, use_database=True):
    """Simple function to detect emotions in real-time"""
    detector = EmotionDetector(use_database=use_database)
    results = detector.detect_emotions_realtime(duration)
    detector.close_camera()
    return results

def detect_emotion_single():
    """Simple function to detect emotion from single capture"""
    detector = EmotionDetector(use_database=True)
    results = detector.detect_emotion_single_capture()
    detector.close_camera()
    return results

def apply_mood_filter_capture(preview_duration=5):
    """Simple function to capture and apply MOOD filter"""
    mood_filter = MoodFilter()
    result = mood_filter.process_mood_capture(preview_duration)
    mood_filter.close_camera()
    return result

def apply_mood_filter_to_file(image_path):
    """Simple function to apply MOOD filter to existing image"""
    mood_filter = MoodFilter()
    result = mood_filter.apply_filter_to_existing_image(image_path)
    return result


# Example usage patterns
def example_usage():
    """Example usage patterns for integration"""
    print("Example Usage Patterns")
    print("=" * 30)
    
    # Example 1: Simple emotion detection
    print("\n1. Simple emotion detection:")
    print("from integration_example import detect_emotion_realtime")
    print("results = detect_emotion_realtime(duration=10)")
    print("print(f'Detected {len(results)} emotions')")
    
    # Example 2: Simple MOOD filter
    print("\n2. Simple MOOD filter:")
    print("from integration_example import apply_mood_filter_capture")
    print("result = apply_mood_filter_capture()")
    print("if result:")
    print("    print(f'Saved: {result[\"filtered_filename\"]}')")
    
    # Example 3: Class-based integration
    print("\n3. Class-based integration:")
    print("from emotion_detector import EmotionDetector")
    print("from mood_filter import MoodFilter")
    print("")
    print("detector = EmotionDetector()")
    print("mood = MoodFilter()")
    print("")
    print("# Use them as needed")
    print("emotions = detector.detect_emotions_realtime(10)")
    print("mood_result = mood.process_mood_capture()")


if __name__ == '__main__':
    print("Emotion Detection & MOOD Filter Integration")
    print("=" * 50)
    print("\nChoose an option:")
    print("1. Run GUI Application")
    print("2. Show Example Usage Patterns")
    print("3. Test Emotion Detection")
    print("4. Test MOOD Filter")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == '1':
        app = EmotionMoodApp()
        app.run()
    elif choice == '2':
        example_usage()
    elif choice == '3':
        print("Testing Emotion Detection...")
        results = detect_emotion_realtime(10)
        print(f"Test completed. Detected {len(results)} emotions.")
    elif choice == '4':
        print("Testing MOOD Filter...")
        result = apply_mood_filter_capture()
        if result:
            print(f"Test completed. Generated: {result['filtered_filename']}")
        else:
            print("Test failed or cancelled.")
    else:
        print("Invalid choice.")
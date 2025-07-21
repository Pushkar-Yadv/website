import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from deepface import DeepFace
import time
import threading
from PIL import Image, ImageTk
import os
from database import EmotionDatabase
import uuid
import base64

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class EmotionDetectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotion Detection Chatbot")
        self.root.geometry("800x600")
        
        # Initialize database
        self.db = EmotionDatabase()
        self.session_id = str(uuid.uuid4())
        
        # Emotion detection variables
        self.detected_emotions = set()
        self.is_detecting = False
        self.cap = None
        
        # Create GUI elements
        self.setup_gui()
        
        # Ensure images directory exists
        self.images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Create placeholder Ghibli-style images if they don't exist
        self.create_placeholder_images()
    
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Emotion Detection Chatbot", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Detect Emotion Button
        self.detect_button = ttk.Button(main_frame, text="Detect Emotion", 
                                       command=self.start_emotion_detection,
                                       style="Accent.TButton")
        self.detect_button.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to detect emotions")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate', length=300)
        self.progress.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        # Chat area
        chat_frame = ttk.LabelFrame(main_frame, text="Chat", padding="10")
        chat_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = tk.Text(chat_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        chat_scrollbar = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=chat_scrollbar.set)
        
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        # Text input
        self.text_input = ttk.Entry(input_frame, font=("Arial", 10))
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.text_input.bind("<Return>", self.send_message)
        
        # Send button
        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.grid(row=0, column=1)
        
        # Add welcome message
        self.add_message("System", "Welcome! Click 'Detect Emotion' to start emotion detection.")
    
    def create_placeholder_images(self):
        """Create placeholder Ghibli-style emotion images if they don't exist"""
        emotions = ['happy', 'sad', 'angry', 'surprised', 'neutral', 'fear', 'disgust']
        colors = {
            'happy': (255, 223, 0),      # Golden yellow
            'sad': (70, 130, 180),       # Steel blue
            'angry': (220, 20, 60),      # Crimson
            'surprised': (255, 165, 0),   # Orange
            'neutral': (169, 169, 169),   # Dark gray
            'fear': (138, 43, 226),      # Blue violet
            'disgust': (107, 142, 35)    # Olive drab
        }
        
        for emotion in emotions:
            image_path = os.path.join(self.images_dir, f"{emotion}.png")
            if not os.path.exists(image_path):
                # Create a simple colored circle as placeholder
                img = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                
                # Draw circle
                color = colors.get(emotion, (128, 128, 128))
                draw.ellipse([20, 20, 180, 180], fill=color + (255,), outline=(0, 0, 0, 255), width=3)
                
                # Add emotion text
                try:
                    font = ImageFont.truetype("Arial", 24)
                except:
                    font = ImageFont.load_default()
                
                text_bbox = draw.textbbox((0, 0), emotion.title(), font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = (200 - text_width) // 2
                text_y = (200 - text_height) // 2
                
                draw.text((text_x, text_y), emotion.title(), fill=(255, 255, 255, 255), font=font)
                
                img.save(image_path)
    
    def detect_emotion_from_frame(self, frame):
        """Extract emotion from a single frame using DeepFace"""
        try:
            # Convert frame to RGB for DeepFace
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces first
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            emotions_in_frame = []
            
            for (x, y, w, h) in faces:
                face_region = frame[y:y+h, x:x+w]
                
                # Use DeepFace to analyze emotion
                result = DeepFace.analyze(face_region, actions=['emotion'], enforce_detection=False)[0]
                emotion = result.get('dominant_emotion', 'neutral')
                confidence = result.get('emotion', {}).get(emotion, 0.0)
                
                # Only add emotions with reasonable confidence
                if confidence > 30:  # 30% confidence threshold
                    emotions_in_frame.append(emotion)
                    
                    # Save to database
                    face_coords = {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)}
                    face_image_base64 = self.encode_face_image(face_region)
                    
                    self.db.save_emotion_record(
                        emotion=emotion,
                        confidence=confidence,
                        face_coords=face_coords,
                        face_image_base64=face_image_base64,
                        session_id=self.session_id
                    )
            
            return emotions_in_frame
            
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            return []
    
    def encode_face_image(self, face_region):
        """Encode face region as base64 string for database storage"""
        try:
            face_resized = cv2.resize(face_region, (100, 100))
            _, buffer = cv2.imencode('.jpg', face_resized)
            face_base64 = base64.b64encode(buffer).decode('utf-8')
            return face_base64
        except Exception as e:
            print(f"Error encoding face image: {e}")
            return None
    
    def start_emotion_detection(self):
        """Start the emotion detection process in a separate thread"""
        if self.is_detecting:
            return
        
        self.is_detecting = True
        self.detected_emotions.clear()
        self.detect_button.config(state='disabled')
        self.status_label.config(text="Initializing camera...")
        
        # Start detection in a separate thread
        detection_thread = threading.Thread(target=self.run_emotion_detection)
        detection_thread.daemon = True
        detection_thread.start()
    
    def run_emotion_detection(self):
        """Run emotion detection for 10 seconds"""
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                self.root.after(0, lambda: self.show_error("Could not open camera"))
                return
            
            # Give camera time to initialize
            time.sleep(0.5)
            
            start_time = time.time()
            max_duration = 10  # 10 seconds
            frame_count = 0
            
            self.root.after(0, lambda: self.status_label.config(text="Detecting emotions... Please look at the camera"))
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame_count += 1
                current_time = time.time()
                elapsed_time = current_time - start_time
                
                # Update progress bar
                progress_value = (elapsed_time / max_duration) * 100
                self.root.after(0, lambda p=progress_value: self.progress.config(value=p))
                
                # Update status with countdown
                countdown = int(max_duration - elapsed_time) + 1
                if countdown > 0:
                    self.root.after(0, lambda c=countdown: self.status_label.config(
                        text=f"Detecting emotions... {c}s remaining"))
                
                # Exit condition - exactly 10 seconds
                if elapsed_time >= max_duration:
                    break
                
                # Detect emotions in current frame
                emotions_in_frame = self.detect_emotion_from_frame(frame)
                for emotion in emotions_in_frame:
                    self.detected_emotions.add(emotion)
                
                # Display the frame with countdown
                countdown_display = int(max_duration - elapsed_time) + 1
                cv2.putText(frame, f"Detecting emotions... {countdown_display}s", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Show camera window
                cv2.namedWindow('Emotion Detection', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Emotion Detection', 640, 480)
                cv2.imshow('Emotion Detection', frame)
                
                # Check for early exit (ESC key)
                key = cv2.waitKey(30) & 0xFF
                if key == 27:  # ESC key
                    break
                
                time.sleep(0.03)  # Small delay to prevent excessive CPU usage
            
            # Clean up camera
            self.cap.release()
            cv2.destroyAllWindows()
            
            # Show emotion selection dialog
            self.root.after(0, self.show_emotion_selection)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Error during detection: {str(e)}"))
        finally:
            self.is_detecting = False
            self.root.after(0, lambda: self.detect_button.config(state='normal'))
            self.root.after(0, lambda: self.progress.config(value=0))
    
    def show_emotion_selection(self):
        """Show Ghibli-style emotion selection dialog"""
        if not self.detected_emotions:
            self.status_label.config(text="No emotions detected. Please try again.")
            messagebox.showinfo("No Emotions", "No emotions were detected. Please try again with better lighting.")
            return
        
        self.status_label.config(text=f"Detected {len(self.detected_emotions)} unique emotions. Select one:")
        
        # Create emotion selection window
        emotion_window = tk.Toplevel(self.root)
        emotion_window.title("Select Your Emotion")
        emotion_window.geometry("600x400")
        emotion_window.transient(self.root)
        emotion_window.grab_set()
        
        # Center the window
        emotion_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Title
        title_label = ttk.Label(emotion_window, text="Choose Your Emotion", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Create frame for emotion images
        emotions_frame = ttk.Frame(emotion_window)
        emotions_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Load and display emotion images
        self.load_emotion_images(emotions_frame, emotion_window)
    
    def load_emotion_images(self, parent_frame, emotion_window):
        """Load and display clickable emotion images"""
        # Calculate grid layout
        emotions_list = list(self.detected_emotions)
        cols = min(3, len(emotions_list))  # Max 3 columns
        rows = (len(emotions_list) + cols - 1) // cols
        
        for i, emotion in enumerate(emotions_list):
            row = i // cols
            col = i % cols
            
            # Create frame for each emotion
            emotion_frame = ttk.Frame(parent_frame)
            emotion_frame.grid(row=row, column=col, padx=10, pady=10)
            
            try:
                # Load image
                image_path = os.path.join(self.images_dir, f"{emotion}.png")
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    img = img.resize((120, 120), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    # Create clickable button with image
                    btn = tk.Button(emotion_frame, image=photo, 
                                   command=lambda e=emotion, w=emotion_window: self.select_emotion(e, w),
                                   relief='raised', borderwidth=2)
                    btn.image = photo  # Keep a reference
                    btn.pack()
                    
                    # Add emotion label
                    label = ttk.Label(emotion_frame, text=emotion.title(), 
                                     font=("Arial", 12, "bold"))
                    label.pack(pady=(5, 0))
                    
                    # Add hover effects
                    def on_enter(event, button=btn):
                        button.config(relief='sunken')
                    
                    def on_leave(event, button=btn):
                        button.config(relief='raised')
                    
                    btn.bind("<Enter>", on_enter)
                    btn.bind("<Leave>", on_leave)
                
            except Exception as e:
                print(f"Error loading image for {emotion}: {e}")
                # Fallback to text button
                btn = ttk.Button(emotion_frame, text=emotion.title(),
                                command=lambda e=emotion, w=emotion_window: self.select_emotion(e, w))
                btn.pack()
        
        # Configure grid weights
        for i in range(cols):
            parent_frame.columnconfigure(i, weight=1)
        for i in range(rows):
            parent_frame.rowconfigure(i, weight=1)
    
    def select_emotion(self, emotion, emotion_window):
        """Handle emotion selection"""
        # Close the emotion selection window
        emotion_window.destroy()
        
        # Insert emotion into chat
        emotion_text = f"[Emotion: {emotion.title()} {self.get_emoji_for_emotion(emotion)}]"
        self.text_input.delete(0, tk.END)
        self.text_input.insert(0, emotion_text)
        
        # Add message to chat
        self.add_message("You", f"Selected emotion: {emotion.title()} {self.get_emoji_for_emotion(emotion)}")
        
        # Update status
        self.status_label.config(text=f"Selected emotion: {emotion.title()}")
    
    def get_emoji_for_emotion(self, emotion):
        """Get emoji for emotion"""
        emoji_map = {
            'angry': '😠',
            'disgust': '🤢',
            'fear': '😨',
            'happy': '😃',
            'sad': '😢',
            'surprise': '😲',
            'surprised': '😲',
            'neutral': '😐'
        }
        return emoji_map.get(emotion, '😐')
    
    def send_message(self, event=None):
        """Send message from input field"""
        message = self.text_input.get().strip()
        if message:
            self.add_message("You", message)
            self.text_input.delete(0, tk.END)
            
            # Simple bot response
            self.add_message("Bot", f"I see you said: {message}")
    
    def add_message(self, sender, message):
        """Add message to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def show_error(self, error_message):
        """Show error message"""
        self.status_label.config(text="Error occurred")
        messagebox.showerror("Error", error_message)

def main():
    root = tk.Tk()
    app = EmotionDetectionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
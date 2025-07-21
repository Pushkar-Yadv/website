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

class EmotionChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotion Detection Chatbot")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
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
        if not os.path.exists(self.images_dir):
            messagebox.showwarning("Images Missing", 
                                 f"Ghibli-style images not found in {self.images_dir}.\n"
                                 "Please run create_ghibli_images.py first.")
    
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title section
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="🎭 Emotion Detection Chatbot", 
                               font=("Arial", 20, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Detect your emotions and express them with Ghibli-style art!", 
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(5, 0))
        
        # Control section
        control_frame = ttk.LabelFrame(main_container, text="Emotion Detection", padding="15")
        control_frame.pack(fill='x', pady=(0, 20))
        
        # Detect button
        self.detect_button = ttk.Button(control_frame, text="🎥 Detect Emotion", 
                                       command=self.start_emotion_detection,
                                       style="Accent.TButton")
        self.detect_button.pack(pady=(0, 10))
        
        # Status and progress
        self.status_label = ttk.Label(control_frame, text="Ready to detect emotions", 
                                     font=("Arial", 11))
        self.status_label.pack(pady=(0, 10))
        
        self.progress = ttk.Progressbar(control_frame, mode='determinate', length=400)
        self.progress.pack(pady=(0, 10))
        
        # Instructions
        instructions = ("Instructions: Click 'Detect Emotion' to start 10-second emotion detection. "
                       "The webcam will open and run for exactly 10 seconds. "
                       "Look at your camera and show different emotions. After 10 seconds, "
                       "the webcam will close automatically and you can select your favorite "
                       "detected emotion from the Ghibli-style art gallery!")
        instruction_label = ttk.Label(control_frame, text=instructions, 
                                     font=("Arial", 10), wraplength=600)
        instruction_label.pack()
        
        # Chat section
        chat_frame = ttk.LabelFrame(main_container, text="💬 Chat", padding="15")
        chat_frame.pack(fill='both', expand=True)
        
        # Chat display with scrollbar
        chat_container = ttk.Frame(chat_frame)
        chat_container.pack(fill='both', expand=True, pady=(0, 15))
        
        self.chat_display = tk.Text(chat_container, height=15, wrap=tk.WORD, 
                                   state=tk.DISABLED, font=("Arial", 11),
                                   bg='white', relief='sunken', borderwidth=2)
        chat_scrollbar = ttk.Scrollbar(chat_container, orient=tk.VERTICAL, 
                                      command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=chat_scrollbar.set)
        
        self.chat_display.pack(side='left', fill='both', expand=True)
        chat_scrollbar.pack(side='right', fill='y')
        
        # Input section
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill='x')
        
        self.text_input = ttk.Entry(input_frame, font=("Arial", 11))
        self.text_input.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.text_input.bind("<Return>", self.send_message)
        
        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side='right')
        
        # Add welcome message
        self.add_message("🤖 Chatbot", "Welcome! I'm your emotion-aware chatbot. Click 'Detect Emotion' to start!")
        self.add_message("🤖 Chatbot", "I'll analyze your emotions for 10 seconds, then you can choose your favorite emotion art to express yourself!")
    
    def detect_emotion_from_frame(self, frame):
        """Extract emotion from a single frame using DeepFace"""
        try:
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
                if confidence > 25:  # 25% confidence threshold
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
        self.status_label.config(text="🎥 Initializing camera...")
        self.add_message("🤖 Chatbot", "Starting emotion detection! Please look at your camera and show different emotions.")
        self.add_message("🤖 Chatbot", "The camera will run for exactly 10 seconds and then automatically close.")
        
        # Start detection in a separate thread
        detection_thread = threading.Thread(target=self.run_emotion_detection)
        detection_thread.daemon = True
        detection_thread.start()
    
    def run_emotion_detection(self):
        """Run emotion detection for exactly 10 seconds"""
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                self.root.after(0, lambda: self.show_error("Could not open camera. Please check your camera connection."))
                return
            
            # Give camera time to initialize
            time.sleep(0.5)
            
            start_time = time.time()
            max_duration = 10.0  # 10 seconds exactly
            frame_count = 0
            emotions_count = 0
            
            self.root.after(0, lambda: self.status_label.config(text="🎭 Detecting emotions... Show your feelings!"))
            
            # Create a set to collect unique emotions
            self.detected_emotions.clear()
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read from camera")
                    break
                
                frame_count += 1
                current_time = time.time()
                elapsed_time = current_time - start_time
                
                # Update progress bar
                progress_value = (elapsed_time / max_duration) * 100
                self.root.after(0, lambda p=min(100, progress_value): self.progress.config(value=p))
                
                # Update status with countdown
                countdown = max(0, int(max_duration - elapsed_time))
                if countdown > 0:
                    self.root.after(0, lambda c=countdown: self.status_label.config(
                        text=f"🎭 Detecting emotions... {c}s remaining"))
                
                # Exit condition - exactly 10 seconds
                if elapsed_time >= max_duration:
                    print(f"Stopping after exactly {max_duration} seconds (elapsed: {elapsed_time:.2f}s)")
                    break
                
                # Detect emotions in current frame
                emotions_in_frame = self.detect_emotion_from_frame(frame)
                for emotion in emotions_in_frame:
                    if emotion not in self.detected_emotions:
                        emotions_count += 1
                        print(f"New emotion detected: {emotion}")
                    self.detected_emotions.add(emotion)
                
                # Display the frame with countdown and info
                countdown_display = max(0, int(max_duration - elapsed_time))
                cv2.putText(frame, f"Emotion Detection: {countdown_display}s", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                if self.detected_emotions:
                    emotions_text = f"Detected: {', '.join(self.detected_emotions)}"
                    cv2.putText(frame, emotions_text, (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                # Show camera window
                cv2.namedWindow('Emotion Detection - 10 Second Capture', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Emotion Detection - 10 Second Capture', 640, 480)
                cv2.imshow('Emotion Detection - 10 Second Capture', frame)
                
                # Check for early exit (ESC key)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC key
                    print("Detection stopped by user (ESC key pressed)")
                    break
            
            # Clean up camera
            self.cap.release()
            cv2.destroyAllWindows()
            
            final_time = time.time() - start_time
            print(f"Detection completed. Detected {len(self.detected_emotions)} unique emotions in {frame_count} frames.")
            print(f"Total time: {final_time:.2f} seconds")
            
            # Show emotion selection dialog with Ghibli-style images
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
            self.status_label.config(text="❌ No emotions detected")
            self.add_message("🤖 Chatbot", "No emotions were detected. Please try again with better lighting and make sure your face is visible!")
            messagebox.showinfo("No Emotions Detected", 
                              "No emotions were detected during the 10-second capture.\n\n"
                              "Tips:\n• Ensure good lighting\n• Look directly at the camera\n"
                              "• Show clear facial expressions\n• Try again!")
            return
        
        self.status_label.config(text=f"✨ Detected {len(self.detected_emotions)} emotions! Choose your favorite:")
        self.add_message("🤖 Chatbot", f"Great! I detected {len(self.detected_emotions)} different emotions: {', '.join(self.detected_emotions)}. Choose your favorite from the gallery!")
        
        # Create emotion selection window
        emotion_window = tk.Toplevel(self.root)
        emotion_window.title("🎨 Ghibli Emotion Gallery - Choose Your Feeling")
        emotion_window.geometry("700x500")
        emotion_window.transient(self.root)
        emotion_window.grab_set()
        emotion_window.configure(bg='#f5f5f5')
        
        # Center the window
        emotion_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Title section
        title_frame = ttk.Frame(emotion_window)
        title_frame.pack(pady=20)
        
        title_label = ttk.Label(title_frame, text="🎨 Choose Your Emotion", 
                               font=("Arial", 18, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Click on your favorite Ghibli-style emotion art to express yourself!", 
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(5, 0))
        
        # Create scrollable frame for emotion images
        canvas = tk.Canvas(emotion_window, bg='#f5f5f5')
        scrollbar = ttk.Scrollbar(emotion_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Load and display emotion images
        self.load_emotion_images(scrollable_frame, emotion_window)
        
        # Close button
        close_frame = ttk.Frame(emotion_window)
        close_frame.pack(pady=10)
        
        close_button = ttk.Button(close_frame, text="Cancel", 
                                 command=emotion_window.destroy)
        close_button.pack()
    
    def load_emotion_images(self, parent_frame, emotion_window):
        """Load and display clickable emotion images in a grid"""
        emotions_list = list(self.detected_emotions)
        cols = min(3, len(emotions_list))  # Max 3 columns
        rows = (len(emotions_list) + cols - 1) // cols
        
        # Check if images directory exists
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir, exist_ok=True)
            # If images don't exist, try to create them
            try:
                import sys
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                from create_ghibli_images import create_ghibli_style_images
                create_ghibli_style_images()
                print("Created Ghibli-style emotion images")
            except Exception as e:
                print(f"Error creating Ghibli images: {e}")
        
        for i, emotion in enumerate(emotions_list):
            row = i // cols
            col = i % cols
            
            # Create frame for each emotion
            emotion_frame = ttk.Frame(parent_frame, relief='raised', borderwidth=2)
            emotion_frame.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
            
            try:
                # Load image
                image_path = os.path.join(self.images_dir, f"{emotion}.png")
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    img = img.resize((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    # Create clickable button with image
                    btn = tk.Button(emotion_frame, image=photo, 
                                   command=lambda e=emotion, w=emotion_window: self.select_emotion(e, w),
                                   relief='flat', borderwidth=0, cursor='hand2')
                    btn.image = photo  # Keep a reference
                    btn.pack(pady=10)
                    
                    # Add emotion label
                    label = ttk.Label(emotion_frame, text=f"{emotion.title()} {self.get_emoji_for_emotion(emotion)}", 
                                     font=("Arial", 14, "bold"))
                    label.pack(pady=(0, 10))
                    
                    # Make the entire frame clickable
                    emotion_frame.bind("<Button-1>", lambda event, e=emotion, w=emotion_window: self.select_emotion(e, w))
                    label.bind("<Button-1>", lambda event, e=emotion, w=emotion_window: self.select_emotion(e, w))
                    
                    # Add hover effects
                    def on_enter(event, frame=emotion_frame):
                        frame.config(relief='sunken')
                    
                    def on_leave(event, frame=emotion_frame):
                        frame.config(relief='raised')
                    
                    emotion_frame.bind("<Enter>", on_enter)
                    emotion_frame.bind("<Leave>", on_leave)
                    btn.bind("<Enter>", on_enter)
                    btn.bind("<Leave>", on_leave)
                    label.bind("<Enter>", on_enter)
                    label.bind("<Leave>", on_leave)
                
                else:
                    print(f"Warning: Image file not found for emotion '{emotion}' at {image_path}")
                    # Fallback to text button if image doesn't exist
                    btn = ttk.Button(emotion_frame, text=f"{emotion.title()}\n{self.get_emoji_for_emotion(emotion)}",
                                    command=lambda e=emotion, w=emotion_window: self.select_emotion(e, w))
                    btn.pack(pady=20)
                
            except Exception as e:
                print(f"Error loading image for {emotion}: {e}")
                # Fallback to text button
                btn = ttk.Button(emotion_frame, text=f"{emotion.title()}\n{self.get_emoji_for_emotion(emotion)}",
                                command=lambda e=emotion, w=emotion_window: self.select_emotion(e, w))
                btn.pack(pady=20)
        
        # Configure grid weights for responsive layout
        for i in range(cols):
            parent_frame.columnconfigure(i, weight=1)
        for i in range(rows):
            parent_frame.rowconfigure(i, weight=1)
    
    def select_emotion(self, emotion, emotion_window):
        """Handle emotion selection"""
        # Close the emotion selection window
        emotion_window.destroy()
        
        # Create emotion text with emoji
        emotion_emoji = self.get_emoji_for_emotion(emotion)
        emotion_text = f"[{emotion.title()} {emotion_emoji}]"
        
        # Insert emotion into chat input
        self.text_input.delete(0, tk.END)
        self.text_input.insert(0, emotion_text)
        
        # Add message to chat
        self.add_message("😊 You", f"I'm feeling {emotion.title()} {emotion_emoji}")
        
        # Personalized responses based on emotion
        responses = {
            'happy': f"I'm glad you're feeling happy! {emotion_emoji} Your positive energy is contagious. How can I make your day even better?",
            'sad': f"I understand you're feeling sad {emotion_emoji}. It's okay to feel this way sometimes. Would you like to talk about what's on your mind?",
            'angry': f"I see you're feeling angry {emotion_emoji}. Taking deep breaths can help. Would you like to discuss what's bothering you?",
            'surprised': f"Wow! You're surprised {emotion_emoji}! Did something unexpected happen? I'd love to hear about it.",
            'fear': f"I notice you're feeling fearful {emotion_emoji}. Remember that you're safe here. Would you like to talk about your concerns?",
            'disgust': f"I see you're feeling disgusted {emotion_emoji}. Sometimes things can be unpleasant. Would you like to talk about it?",
            'neutral': f"You seem to be feeling neutral {emotion_emoji}. That's perfectly fine! How can I assist you today?"
        }
        
        # Get personalized response or use default
        response = responses.get(emotion, f"I can see you're feeling {emotion.title()}! {emotion_emoji} That's a valid emotion. How can I help you today?")
        self.add_message("🤖 Chatbot", response)
        
        # Update status
        self.status_label.config(text=f"✨ Selected: {emotion.title()} {emotion_emoji}")
        
        # Focus on text input
        self.text_input.focus()
    
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
            self.add_message("😊 You", message)
            self.text_input.delete(0, tk.END)
            
            # Simple bot response based on emotion context
            if any(emotion in message.lower() for emotion in ['happy', 'joy', 'excited']):
                response = "That's wonderful! I'm glad you're feeling positive! 😊"
            elif any(emotion in message.lower() for emotion in ['sad', 'down', 'upset']):
                response = "I understand you're going through a tough time. I'm here to listen. 💙"
            elif any(emotion in message.lower() for emotion in ['angry', 'frustrated', 'mad']):
                response = "It sounds like you're feeling frustrated. Take a deep breath. 🌸"
            else:
                response = f"Thanks for sharing: {message} 💭"
            
            self.add_message("🤖 Chatbot", response)
    
    def add_message(self, sender, message):
        """Add message to chat display with nice formatting"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        # Format message
        formatted_message = f"[{timestamp}] {sender}: {message}\n"
        
        self.chat_display.insert(tk.END, formatted_message)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def show_error(self, error_message):
        """Show error message"""
        self.status_label.config(text="❌ Error occurred")
        self.add_message("🤖 Chatbot", f"Sorry, there was an error: {error_message}")
        messagebox.showerror("Error", error_message)

def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    # Set window icon (if available)
    try:
        # You can add an icon file here if you have one
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    app = EmotionChatbotGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_detecting:
            if messagebox.askokcancel("Quit", "Emotion detection is running. Do you want to quit?"):
                if app.cap:
                    app.cap.release()
                cv2.destroyAllWindows()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from PIL import Image, ImageTk
import os
import time
from web_emotion_detect import detect_emotions_for_web
from database import EmotionDatabase
import uuid

class IntegratedEmotionGUI:
    """
    Integrated GUI that uses your existing detect_emotions_for_web() function
    and adds the Ghibli-style emotion selection dialog.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Emotion Detection Chatbot - Integrated")
        self.root.geometry("800x600")
        
        # Initialize database
        self.db = EmotionDatabase()
        self.session_id = str(uuid.uuid4())
        
        # Variables
        self.is_detecting = False
        self.detected_emotions = set()
        
        # Setup GUI
        self.setup_gui()
        
        # Ensure images directory exists
        self.images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
        if not os.path.exists(self.images_dir):
            messagebox.showwarning("Images Missing", 
                                 f"Ghibli-style images not found in {self.images_dir}.\n"
                                 "Please run create_ghibli_images.py first.")
    
    def setup_gui(self):
        """Setup the main GUI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎭 Emotion Detection Chatbot", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = ("Click 'Detect Emotion' to start 10-second webcam emotion detection.\n"
                    "After detection, choose your favorite emotion from the Ghibli art gallery!")
        desc_label = ttk.Label(main_frame, text=desc_text, font=("Arial", 11), 
                              justify='center')
        desc_label.pack(pady=(0, 20))
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Emotion Detection", padding="15")
        control_frame.pack(fill='x', pady=(0, 20))
        
        # Detect button
        self.detect_button = ttk.Button(control_frame, text="🎥 Detect Emotion (10 seconds)", 
                                       command=self.start_detection,
                                       style="Accent.TButton")
        self.detect_button.pack(pady=(0, 10))
        
        # Status
        self.status_label = ttk.Label(control_frame, text="Ready to detect emotions")
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate', length=400)
        self.progress.pack()
        
        # Chat area
        chat_frame = ttk.LabelFrame(main_frame, text="💬 Chat", padding="15")
        chat_frame.pack(fill='both', expand=True)
        
        # Chat display
        self.chat_display = tk.Text(chat_frame, height=12, wrap=tk.WORD, 
                                   state=tk.DISABLED, font=("Arial", 10))
        chat_scrollbar = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, 
                                      command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=chat_scrollbar.set)
        
        self.chat_display.pack(side='left', fill='both', expand=True)
        chat_scrollbar.pack(side='right', fill='y')
        
        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill='x', pady=(10, 0))
        
        self.text_input = ttk.Entry(input_frame, font=("Arial", 10))
        self.text_input.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.text_input.bind("<Return>", self.send_message)
        
        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side='right')
        
        # Welcome message
        self.add_message("🤖 Bot", "Welcome! Click 'Detect Emotion' to analyze your emotions for 10 seconds.")
    
    def start_detection(self):
        """Start emotion detection using your existing function"""
        if self.is_detecting:
            return
        
        self.is_detecting = True
        self.detect_button.config(state='disabled')
        self.status_label.config(text="🎥 Starting emotion detection...")
        self.progress.start()
        
        self.add_message("🤖 Bot", "Starting 10-second emotion detection! Look at your camera and show different emotions.")
        
        # Start detection in separate thread
        detection_thread = threading.Thread(target=self.run_detection)
        detection_thread.daemon = True
        detection_thread.start()
    
    def run_detection(self):
        """Run the detection using your existing function"""
        try:
            self.root.after(0, lambda: self.status_label.config(text="🎭 Detecting emotions... (10 seconds)"))
            
            # Run your existing detection function (now returns emotions too)
            emotions_count, detected_emotions = detect_emotions_for_web()
            
            # Use the emotions returned from the detection function
            self.detected_emotions = detected_emotions
            
            self.root.after(0, self.detection_completed)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Detection error: {str(e)}"))
        finally:
            self.is_detecting = False
            self.root.after(0, lambda: self.detect_button.config(state='normal'))
            self.root.after(0, lambda: self.progress.stop())
    
    def get_recent_emotions(self):
        """Get recently detected emotions from database"""
        try:
            # Get recent emotion records (last 30 seconds)
            import time
            recent_time = time.time() - 30  # Last 30 seconds
            
            # This is a simplified approach - you might need to modify your database
            # to have a method to get recent emotions by session
            emotions = set()
            
            # For now, we'll simulate some detected emotions
            # In a real implementation, you'd query the database
            sample_emotions = ['happy', 'neutral', 'surprised']  # Fallback
            emotions.update(sample_emotions)
            
            return emotions
        except Exception as e:
            print(f"Error getting recent emotions: {e}")
            return {'neutral'}  # Fallback
    
    def detection_completed(self):
        """Handle completion of emotion detection"""
        self.status_label.config(text="✅ Detection completed!")
        
        if self.detected_emotions:
            self.add_message("🤖 Bot", f"Detection complete! Found {len(self.detected_emotions)} emotions: {', '.join(self.detected_emotions)}")
            self.show_emotion_selection()
        else:
            self.add_message("🤖 Bot", "No emotions detected. Please try again with better lighting.")
            messagebox.showinfo("No Emotions", "No emotions were detected. Please try again.")
    
    def show_emotion_selection(self):
        """Show the Ghibli-style emotion selection dialog"""
        # Create emotion selection window
        emotion_window = tk.Toplevel(self.root)
        emotion_window.title("🎨 Choose Your Emotion")
        emotion_window.geometry("600x400")
        emotion_window.transient(self.root)
        emotion_window.grab_set()
        
        # Center window
        emotion_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 100,
            self.root.winfo_rooty() + 100
        ))
        
        # Title
        title_label = ttk.Label(emotion_window, text="🎨 Choose Your Favorite Emotion", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Emotions grid
        emotions_frame = ttk.Frame(emotion_window)
        emotions_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.create_emotion_grid(emotions_frame, emotion_window)
    
    def create_emotion_grid(self, parent, emotion_window):
        """Create grid of emotion images"""
        emotions_list = list(self.detected_emotions)
        cols = min(3, len(emotions_list))
        
        for i, emotion in enumerate(emotions_list):
            row = i // cols
            col = i % cols
            
            # Create frame for emotion
            emotion_frame = ttk.Frame(parent, relief='raised', borderwidth=2)
            emotion_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            try:
                # Load image
                image_path = os.path.join(self.images_dir, f"{emotion}.png")
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    img = img.resize((120, 120), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    # Create button
                    btn = tk.Button(emotion_frame, image=photo,
                                   command=lambda e=emotion, w=emotion_window: self.select_emotion(e, w),
                                   relief='flat', cursor='hand2')
                    btn.image = photo
                    btn.pack(pady=10)
                    
                    # Label
                    label = ttk.Label(emotion_frame, text=f"{emotion.title()} {self.get_emoji(emotion)}", 
                                     font=("Arial", 12, "bold"))
                    label.pack(pady=(0, 10))
                    
                else:
                    # Fallback button
                    btn = ttk.Button(emotion_frame, text=f"{emotion.title()}\n{self.get_emoji(emotion)}",
                                    command=lambda e=emotion, w=emotion_window: self.select_emotion(e, w))
                    btn.pack(pady=20)
                    
            except Exception as e:
                print(f"Error creating emotion button for {emotion}: {e}")
                btn = ttk.Button(emotion_frame, text=emotion.title(),
                                command=lambda e=emotion, w=emotion_window: self.select_emotion(e, w))
                btn.pack(pady=20)
        
        # Configure grid
        for i in range(cols):
            parent.columnconfigure(i, weight=1)
    
    def select_emotion(self, emotion, emotion_window):
        """Handle emotion selection"""
        emotion_window.destroy()
        
        # Insert into text input
        emotion_text = f"[{emotion.title()} {self.get_emoji(emotion)}]"
        self.text_input.delete(0, tk.END)
        self.text_input.insert(0, emotion_text)
        
        # Add to chat
        self.add_message("😊 You", f"I'm feeling {emotion.title()} {self.get_emoji(emotion)}")
        self.add_message("🤖 Bot", f"I can see you're feeling {emotion.title()}! How can I help you today?")
        
        # Update status
        self.status_label.config(text=f"✨ Selected: {emotion.title()}")
    
    def get_emoji(self, emotion):
        """Get emoji for emotion"""
        emoji_map = {
            'angry': '😠', 'disgust': '🤢', 'fear': '😨', 'happy': '😃',
            'sad': '😢', 'surprise': '😲', 'surprised': '😲', 'neutral': '😐'
        }
        return emoji_map.get(emotion, '😐')
    
    def send_message(self, event=None):
        """Send message"""
        message = self.text_input.get().strip()
        if message:
            self.add_message("😊 You", message)
            self.text_input.delete(0, tk.END)
            
            # Simple response
            self.add_message("🤖 Bot", f"Thanks for sharing: {message}")
    
    def add_message(self, sender, message):
        """Add message to chat"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def show_error(self, error_message):
        """Show error"""
        self.status_label.config(text="❌ Error")
        self.add_message("🤖 Bot", f"Error: {error_message}")
        messagebox.showerror("Error", error_message)

def main():
    root = tk.Tk()
    app = IntegratedEmotionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
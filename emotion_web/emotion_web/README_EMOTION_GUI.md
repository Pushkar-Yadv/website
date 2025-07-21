# 🎭 Emotion Detection Chatbot with Ghibli-Style Art

A beautiful emotion detection system that captures your emotions through webcam for exactly 10 seconds, then lets you choose from Ghibli-style emotion art to express yourself in a chatbot interface.

## ✨ Features

- **10-Second Emotion Detection**: Webcam opens for exactly 10 seconds to capture emotions
- **Real-time Emotion Analysis**: Uses DeepFace for accurate emotion detection
- **Ghibli-Style Art Gallery**: Beautiful emotion art for each detected emotion
- **Interactive Chatbot**: Express yourself using selected emotion art
- **Database Storage**: All emotions are saved to database with timestamps
- **Threading**: Non-blocking GUI with responsive interface

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install opencv-python deepface pillow tkinter
```

### 2. Create Ghibli-Style Images
```bash
python3 create_ghibli_images.py
```

### 3. Run the Application
```bash
python3 run_emotion_chatbot.py
```

## 📁 Files Overview

### Main Applications
- **`emotion_chatbot_gui.py`** - Full-featured chatbot with custom emotion detection
- **`integrated_emotion_gui.py`** - Uses your existing `detect_emotions_for_web()` function
- **`run_emotion_chatbot.py`** - Simple launcher script

### Supporting Files
- **`create_ghibli_images.py`** - Creates beautiful Ghibli-style emotion images
- **`web_emotion_detect.py`** - Modified to return detected emotions (enhanced)

### Generated Content
- **`images/`** - Directory containing Ghibli-style emotion art:
  - `happy.png` - Golden joy and happiness
  - `sad.png` - Blue melancholy and sadness  
  - `angry.png` - Red anger and frustration
  - `surprised.png` - Orange surprise and wonder
  - `neutral.png` - Gray calm and neutral
  - `fear.png` - Purple fear and anxiety
  - `disgust.png` - Green disgust and distaste

## 🎯 How It Works

### 1. Click "Detect Emotion" Button
- Webcam window opens automatically
- Timer shows exactly 10 seconds countdown
- Real-time emotion detection runs continuously

### 2. Show Your Emotions
- Look at the camera and express different emotions
- System detects: happy, sad, angry, surprised, neutral, fear, disgust
- All unique emotions are collected (no duplicates)

### 3. Choose Your Favorite
- After 10 seconds, webcam closes automatically
- Ghibli-style art gallery opens with detected emotions
- Click on your favorite emotion art

### 4. Express Yourself
- Selected emotion is inserted into chatbot
- Continue chatting with emotion context
- All interactions are saved to database

## 🎨 Ghibli-Style Art Features

Each emotion has a unique artistic style:
- **Circular Design**: Beautiful gradient circles with decorative elements
- **Color Psychology**: Each emotion has its own color palette
- **Typography**: Clean, readable emotion labels
- **Hover Effects**: Interactive visual feedback
- **Scalable**: Works on different screen sizes

## 🔧 Technical Details

### Emotion Detection
- **Library**: DeepFace with OpenCV
- **Confidence Threshold**: 25% minimum for reliable detection
- **Face Detection**: Haar Cascade classifier
- **Processing**: Real-time frame analysis

### GUI Framework
- **Main GUI**: Tkinter with ttk styling
- **Image Handling**: PIL/Pillow for image processing
- **Threading**: Separate thread for camera operations
- **Responsive**: Non-blocking interface

### Database Integration
- **Storage**: SQLite database via your existing `database.py`
- **Session Tracking**: Unique session IDs for each detection
- **Metadata**: Face coordinates, confidence scores, timestamps

## 🎮 Usage Examples

### Basic Usage
```python
from emotion_chatbot_gui import main
main()  # Launches full application
```

### Using Existing Detection Function
```python
from integrated_emotion_gui import main
main()  # Uses your detect_emotions_for_web() function
```

### Custom Integration
```python
from web_emotion_detect import detect_emotions_for_web

# Now returns both count and unique emotions
count, emotions = detect_emotions_for_web()
print(f"Detected {count} total emotions")
print(f"Unique emotions: {emotions}")
```

## 🛠️ Customization

### Adding New Emotions
1. Add emotion to `create_ghibli_images.py`
2. Update emoji mappings in GUI files
3. Regenerate images: `python3 create_ghibli_images.py`

### Changing Detection Duration
```python
max_duration = 15  # Change from 10 to 15 seconds
```

### Modifying Art Style
Edit the `create_ghibli_images.py` file to change:
- Colors and gradients
- Image size and layout
- Typography and fonts
- Decorative elements

### Custom Responses
Modify the chatbot responses in the `send_message()` method:
```python
def send_message(self, event=None):
    message = self.text_input.get().strip()
    if message:
        # Add custom emotion-based responses here
        if 'happy' in message.lower():
            response = "Your custom happy response!"
```

## 🐛 Troubleshooting

### Camera Issues
- **Error**: "Could not open camera"
- **Solution**: Check camera permissions and ensure no other apps are using it

### Missing Images
- **Error**: "Images not found"
- **Solution**: Run `python3 create_ghibli_images.py` first

### Import Errors
- **Error**: Module not found
- **Solution**: Install dependencies: `pip install opencv-python deepface pillow`

### Performance Issues
- **Issue**: Slow emotion detection
- **Solution**: Ensure good lighting and clear face visibility

## 📊 Detection Tips

### For Best Results:
- **Lighting**: Use good, even lighting on your face
- **Position**: Look directly at the camera
- **Distance**: Sit 2-3 feet from camera
- **Expressions**: Make clear, distinct facial expressions
- **Movement**: Keep head relatively still

### Supported Emotions:
- 😃 **Happy**: Smiles, joy, laughter
- 😢 **Sad**: Frowns, tears, melancholy  
- 😠 **Angry**: Furrowed brows, scowls
- 😲 **Surprised**: Wide eyes, open mouth
- 😐 **Neutral**: Relaxed, calm expression
- 😨 **Fear**: Worried, anxious expression
- 🤢 **Disgust**: Wrinkled nose, distaste

## 🔮 Future Enhancements

- **Voice Integration**: Add speech emotion detection
- **Multiple Faces**: Support for multiple people
- **Emotion History**: Track emotion patterns over time
- **Custom Art**: Upload your own emotion images
- **Social Features**: Share emotions with friends
- **Analytics**: Emotion statistics and insights

## 📝 License

This project builds upon your existing emotion detection system and adds the GUI and art gallery features. Feel free to modify and extend as needed!

## 🤝 Contributing

To add new features:
1. Fork the repository
2. Create a feature branch
3. Add your enhancements
4. Test thoroughly
5. Submit a pull request

---

**Enjoy expressing your emotions with beautiful Ghibli-style art! 🎨✨**
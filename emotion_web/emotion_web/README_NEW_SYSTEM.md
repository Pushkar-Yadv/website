# Emotion Detection & MOOD Filter System

A complete emotion detection and image filtering system with separate, modular components for easy integration into other projects.

## Features

### 1. Emotion Detection
- Real-time emotion detection using webcam
- Face detection and emotion analysis using DeepFace
- Database storage of emotion records
- Clean, modular API for easy integration

### 2. MOOD Filter
- High-quality Pixar-style 3D cartoon image conversion
- Advanced image processing with multiple enhancement stages
- Skin smoothing and 3D effects
- Supports both camera capture and existing image processing

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

#### Emotion Detection
```python
from emotion_detector import EmotionDetector

# Initialize detector
detector = EmotionDetector(use_database=True)

# Real-time detection
results = detector.detect_emotions_realtime(duration=10)

# Single capture
results = detector.detect_emotion_single_capture()

# Cleanup
detector.close_camera()
```

#### MOOD Filter
```python
from mood_filter import MoodFilter

# Initialize MOOD filter
mood_filter = MoodFilter()

# Capture and apply filter
result = mood_filter.process_mood_capture(preview_duration=5)

# Apply to existing image
result = mood_filter.apply_filter_to_existing_image("path/to/image.jpg")

# Cleanup
mood_filter.close_camera()
```

### Integration Example

Run the complete integration example:

```bash
python integration_example.py
```

This provides:
- GUI application with both systems
- Simple function-based API
- Example usage patterns

## File Structure

```
emotion_web/
├── emotion_detector.py     # Main emotion detection module
├── mood_filter.py          # Pixar-style image filter
├── integration_example.py  # Integration examples and GUI
├── database.py            # Database operations
├── app.py                 # Web interface (Flask)
├── web_emotion_detect.py  # Web-specific emotion detection
├── static/
│   ├── images/            # Emotion indicator images
│   └── mood_captures/     # MOOD filter output images
└── requirements.txt       # Dependencies
```

## API Reference

### EmotionDetector Class

#### Methods
- `__init__(use_database=True)` - Initialize detector
- `detect_emotions_realtime(duration=10)` - Real-time detection
- `detect_emotion_single_capture()` - Single image capture
- `get_recent_emotions(limit=10)` - Get recent records
- `close_camera()` - Cleanup

#### Returns
Emotion results with:
- `emotion`: Detected emotion name
- `confidence`: Confidence percentage
- `face_coords`: Face bounding box
- `timestamp`: Detection time

### MoodFilter Class

#### Methods
- `__init__()` - Initialize filter
- `process_mood_capture(preview_duration=5)` - Capture and filter
- `apply_filter_to_existing_image(image_path)` - Filter existing image
- `close_camera()` - Cleanup

#### Returns
File paths for:
- `original_path`: Original image
- `filtered_path`: Pixar-style filtered image
- `original_filename`: Original filename
- `filtered_filename`: Filtered filename

## Integration in Other Projects

### Option 1: Simple Functions
```python
from integration_example import detect_emotion_realtime, apply_mood_filter_capture

# Detect emotions
emotions = detect_emotion_realtime(duration=10)

# Apply MOOD filter
result = apply_mood_filter_capture()
```

### Option 2: Class-based Integration
```python
from emotion_detector import EmotionDetector
from mood_filter import MoodFilter

class MyApp:
    def __init__(self):
        self.emotion_detector = EmotionDetector()
        self.mood_filter = MoodFilter()
    
    def detect_emotion_button_clicked(self):
        results = self.emotion_detector.detect_emotions_realtime(10)
        # Process results...
    
    def mood_filter_button_clicked(self):
        result = self.mood_filter.process_mood_capture()
        # Process result...
```

### Option 3: Web API Integration
```python
# Run the Flask app
python app.py

# Use HTTP endpoints:
# GET /detect - Emotion detection
# POST /api/emotions/recent - Get recent emotions
```

## Configuration

### Emotion Detection
- Confidence threshold: Modify `HIGH_CONFIDENCE_THRESHOLD` in web_emotion_detect.py
- Camera settings: Adjust resolution and FPS in `open_camera()` methods
- Database: Configure in `database.py`

### MOOD Filter
- Filter quality: Adjust bilateral filter parameters in `mood_filter.py`
- Output quality: Modify JPEG quality in `save_mood_image()`
- Color enhancement: Tune values in `enhance_colors_pixar_style()`

## Troubleshooting

### Camera Issues
- Ensure camera is not being used by other applications
- Check camera permissions
- Try different camera indices if default doesn't work

### Performance
- Reduce image resolution for faster processing
- Adjust confidence thresholds for better accuracy
- Use GPU acceleration for TensorFlow if available

### Dependencies
- Install Microsoft Visual C++ Redistributable for Windows
- Update graphics drivers for better OpenCV performance
- Use Python 3.8+ for best compatibility

## Examples

See `integration_example.py` for complete working examples including:
- GUI application with both systems
- Simple command-line interfaces
- Error handling and cleanup
- Real-world usage patterns

## License

This project is provided as-is for educational and development purposes.
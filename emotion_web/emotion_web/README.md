# Emotion Detection Web Application with Database Integration

This application performs real-time emotion detection using computer vision and stores the results in a SQL database with timestamps and face capture information.

## Features

### Core Functionality
- Real-time emotion detection using webcam
- Face detection and emotion classification
- Emoji overlay on detected faces
- Chatbot integration

### Database Integration
- **SQLite Database**: Stores emotion detection results
- **Timestamp Tracking**: Records when each emotion was detected
- **Face Coordinates**: Stores face position data (x, y, width, height)
- **Face Images**: Stores base64-encoded face images (resized to 100x100)
- **Session Tracking**: Groups detections by session ID
- **Confidence Scores**: Stores emotion detection confidence levels

### Dashboard & Analytics
- **Real-time Dashboard**: View emotion detection statistics
- **Recent Emotions**: See the latest emotion detections
- **Statistics**: Emotion counts and average confidence scores
- **Date-based Filtering**: Filter data by date ranges
- **Auto-refresh**: Dashboard updates every 30 seconds

## Database Schema

### emotion_records table
```sql
CREATE TABLE emotion_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emotion TEXT NOT NULL,
    confidence REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    face_coordinates TEXT,
    face_image_base64 TEXT,
    session_id TEXT
);
```

### emotion_summary table
```sql
CREATE TABLE emotion_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    emotion TEXT,
    count INTEGER,
    avg_confidence REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### GET /api/emotions/recent
Get recent emotion records
- **Parameters**: `limit` (optional, default: 10)
- **Response**: List of recent emotion detections with timestamps

### GET /api/emotions/statistics
Get emotion statistics
- **Parameters**: `date_from`, `date_to` (optional)
- **Response**: Emotion counts and average confidence scores

### GET /api/emotions/by-date
Get emotions grouped by date
- **Parameters**: `days` (optional, default: 7)
- **Response**: Emotion counts per date

### GET /api/emotions/count
Get total number of emotion records
- **Response**: Total count of all emotion records

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test Database**:
   ```bash
   python3 test_database.py
   ```

3. **Run Application**:
   ```bash
   python3 app.py
   ```

4. **Access Application**:
   - Main App: http://localhost:5054/
   - Dashboard: http://localhost:5054/dashboard

## Usage

### Emotion Detection
1. Click the camera button in the main interface
2. Allow webcam access when prompted
3. Emotions will be detected and saved to database automatically
4. Press 'q' to stop emotion detection

### Viewing Data
1. Visit the dashboard at `/dashboard`
2. View real-time statistics and recent detections
3. Data refreshes automatically every 30 seconds
4. Use the refresh button for manual updates

## Data Storage

- **Database File**: `emotion_data.db` (SQLite)
- **Face Images**: Stored as base64-encoded strings in database
- **Coordinates**: Face bounding box coordinates stored as JSON strings
- **Sessions**: Each emotion detection session gets a unique ID

## Database Operations

### Saving Emotion Records
```python
from database import EmotionDatabase

db = EmotionDatabase()
record_id = db.save_emotion_record(
    emotion='happy',
    confidence=0.85,
    face_coords={'x': 100, 'y': 50, 'width': 80, 'height': 80},
    face_image_base64='base64_encoded_image',
    session_id='unique_session_id'
)
```

### Retrieving Data
```python
# Get recent emotions
recent = db.get_recent_emotions(limit=10)

# Get statistics
stats = db.get_emotion_statistics()

# Get emotions by date
by_date = db.get_emotions_by_date(days=7)

# Get total count
total = db.get_total_records_count()
```

## File Structure

```
emotion_web/
├── app.py                 # Flask application with API endpoints
├── emotion.py            # Emotion detection with database integration
├── database.py           # Database operations and schema
├── test_database.py      # Database testing script
├── requirements.txt      # Python dependencies
├── emotion_data.db       # SQLite database file (created automatically)
├── templates/
│   ├── index.html        # Main application interface
│   └── dashboard.html    # Analytics dashboard
├── static/
│   └── style.css         # Application styles
└── emoji_images/         # Downloaded emoji images
```

## Technical Details

### Emotion Detection
- Uses DeepFace library for emotion classification
- Supports 7 emotions: happy, sad, angry, fear, surprise, disgust, neutral
- OpenCV for face detection and video processing
- Real-time processing with webcam input

### Database Features
- Automatic database initialization
- Transaction safety
- Efficient querying with indexes
- Data cleanup utilities
- Session-based grouping

### Web Interface
- Responsive design
- Real-time updates
- Error handling
- Loading states
- Auto-refresh functionality

## Troubleshooting

### Common Issues
1. **Camera Access**: Ensure webcam permissions are granted
2. **Dependencies**: Install all requirements from requirements.txt
3. **Database**: Database file is created automatically on first run
4. **Port Conflicts**: Application runs on port 5054 by default

### Testing
Run the database test script to verify functionality:
```bash
python3 test_database.py
```

## Future Enhancements

- Export data to CSV/JSON
- Advanced analytics and charts
- User authentication
- Multiple camera support
- Cloud database integration
- Real-time notifications
- Emotion trend analysis
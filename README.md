# 🚀 ChatApp with AI Features

A modern real-time chat application with advanced AI features including emotion detection and anime-style mood filters.

![ChatApp Banner](https://via.placeholder.com/800x300/0c0c0c/64FFDA?text=ChatApp+with+AI+Features)

## ✨ Features

### 🔐 Core Features
- **Real-time Chat**: Instant messaging with Socket.IO
- **User Authentication**: Secure login and registration system
- **Online Status**: Live user presence indicators
- **Profile Management**: Customizable profiles with avatar upload
- **Dark Theme UI**: Beautiful gradient-based dark interface with animations

### 🤖 AI Features
- **Emotion Detection**: Real-time facial emotion recognition using DeepFace
- **AnimeGAN Mood Filters**: Transform photos with three anime styles:
  - Shinkai Style (vibrant, cinematic)
  - Hayao Style (Miyazaki-inspired, warm)
  - Paprika Style (psychedelic, intense)

### 🎨 UI/UX Features
- **Animated Particles Background**: Dynamic particle system
- **Smooth Animations**: CSS3 transitions and keyframe animations
- **Responsive Design**: Mobile-friendly responsive layout
- **Real-time Notifications**: Live chat and user status updates
- **Gradient Themes**: Beautiful color gradients throughout

## 📋 Requirements

- Python 3.8 or higher
- Webcam (for AI features)
- Modern web browser
- 4GB+ RAM (for AI models)

## 🛠️ Installation

### Quick Setup
1. **Clone or download** this repository
2. **Run the setup script**:
   ```bash
   python setup.py
   ```
3. **Start the application**:
   ```bash
   python app.py
   ```
4. **Open your browser** and go to `http://localhost:5000`

### Manual Setup
If you prefer manual installation:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create directories**:
   ```bash
   mkdir -p static/{uploads,profiles,anime_captures,emotion_captures}
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

## 📁 Project Structure

```
ChatApp/
├── app.py                          # Main Flask application
├── setup.py                        # Setup script
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── run.py                          # Quick start script
├── chat_app.db                     # SQLite database (created automatically)
├── static/                         # Static files
│   ├── default_avatar.png          # Default profile picture
│   ├── uploads/                    # User file uploads
│   ├── profiles/                   # Profile pictures
│   ├── anime_captures/            # Mood filter results
│   └── emotion_captures/          # Emotion detection results
├── templates/                      # HTML templates
│   ├── base.html                  # Base template with styling
│   ├── index.html                 # Landing page
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   ├── dashboard.html             # Main chat interface
│   └── profile.html               # Profile management
└── emotion_web/                   # AI components (your existing folder)
    └── emotion_web/
        ├── emotion_detector.py    # Emotion detection module
        ├── anime_mood_filter.py   # AnimeGAN filter module
        └── AnimeGANv2/           # AnimeGAN model files
```

## 🎯 How to Use

### 1. Getting Started
1. **Create Account**: Register with username, email, and password
2. **Login**: Sign in to access the chat interface
3. **Profile Setup**: Upload a profile picture and customize your profile

### 2. Chat Features
- **Send Messages**: Type and press Enter to send messages
- **Real-time Updates**: See new messages instantly
- **Online Users**: View who's currently online in the left sidebar
- **User Status**: Get notifications when users join or leave

### 3. AI Features

#### Emotion Detection
1. Click **"Detect Emotion"** button in the right sidebar
2. Allow camera access when prompted
3. Position your face in the camera view
4. Press SPACE to capture or wait for auto-capture
5. View your detected emotion with confidence percentage

#### MOOD Filters
1. Select an anime style from the dropdown:
   - **Shinkai**: Vibrant, cinematic style
   - **Hayao**: Miyazaki-inspired, warm colors
   - **Paprika**: Psychedelic, intense colors
2. Click **"Apply MOOD Filter"**
3. Allow camera access and position yourself
4. Press SPACE to capture or wait for countdown
5. View your anime-transformed image

## 🔧 Configuration

### Database
The application uses SQLite by default. The database is created automatically on first run with these tables:
- `users` - User accounts and profiles
- `messages` - Chat messages
- `emotion_records` - Emotion detection history
- `mood_filter_records` - Mood filter history

### AI Models
The emotion detection uses:
- **DeepFace**: For facial emotion recognition
- **AnimeGANv2**: For anime-style image transformation
- **OpenCV**: For camera capture and image processing

### Customization
You can customize the application by modifying:
- **Colors**: Edit CSS variables in `base.html`
- **Animations**: Modify keyframe animations in templates
- **AI Settings**: Adjust parameters in emotion detection modules

## 🚨 Troubleshooting

### Common Issues

**1. Camera Not Working**
- Ensure your browser allows camera access
- Check if camera is being used by other applications
- Try refreshing the page

**2. AI Features Not Available**
- Verify that emotion detection files are present
- Install required Python packages: `pip install deepface tensorflow opencv-python`
- Check that your system has sufficient RAM (4GB+)

**3. Installation Errors**
- Update pip: `python -m pip install --upgrade pip`
- Install Visual C++ Build Tools (Windows)
- Try installing packages one by one

**4. Performance Issues**
- Close other applications to free up RAM
- Use a dedicated GPU for better AI performance
- Reduce image resolution in AI modules

### Error Messages

**"Emotion detection not available"**
- The emotion detection modules are not properly installed
- Run setup script or manually install AI dependencies

**"Could not open camera"**
- Camera is in use by another application
- Camera drivers are not properly installed
- Try restarting the browser or computer

## 🛡️ Security Features

- **Password Hashing**: Secure bcrypt password hashing
- **Session Management**: Flask session handling
- **Input Validation**: Form validation and sanitization
- **File Upload Security**: Secure file handling with type checking
- **CSRF Protection**: Built-in CSRF protection

## 🌐 Browser Support

- **Chrome**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support
- **Mobile**: Responsive design works on mobile browsers

## 📈 Performance

### System Requirements
- **CPU**: Multi-core processor recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Stable internet connection for real-time features

### Optimization Tips
- Use a modern browser with hardware acceleration
- Close unnecessary browser tabs
- Ensure stable internet connection
- Use a dedicated GPU if available

## 🤝 Contributing

Feel free to contribute to this project by:
1. Reporting bugs
2. Suggesting new features
3. Improving documentation
4. Submitting pull requests

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the error logs in the console
3. Ensure all dependencies are properly installed
4. Verify that your system meets the requirements

## 🔮 Future Features

Planned enhancements:
- [ ] Video chat support
- [ ] File sharing capabilities
- [ ] Custom emoji reactions
- [ ] Chat rooms and channels
- [ ] Message encryption
- [ ] Mobile app version
- [ ] Advanced AI features
- [ ] Theme customization

---

**Made with ❤️ using Flask, Socket.IO, and AI**

Enjoy chatting with AI-powered features! 🚀
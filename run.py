#!/usr/bin/env python3
"""
Run script for Real-Time Chat Website
"""

from app import app, socketio, init_db, EMOTION_AVAILABLE

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    print("=" * 50)
    print("🚀 Real-Time Chat Website Starting...")
    print("=" * 50)
    print("Features available:")
    print("✓ Real-time chat with Socket.IO")
    print("✓ User authentication & registration") 
    print("✓ Online user status")
    print("✓ Profile management")
    if EMOTION_AVAILABLE:
        print("✓ Emotion detection with camera")
        print("✓ AnimeGAN mood filters")
    else:
        print("⚠ Emotion detection disabled (will work on basic features)")
    print("✓ Dark themed UI with animations")
    print("=" * 50)
    print("🌐 Server running on: http://localhost:8080")
    print("🌐 Also accessible at: http://0.0.0.0:8080")
    print("=" * 50)
    
    # Run the application
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
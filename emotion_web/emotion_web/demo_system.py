#!/usr/bin/env python3
"""
Complete System Demo - Demonstrates both Emotion Detection and MOOD Filter
Works with or without heavy dependencies (TensorFlow, DeepFace)
"""

import os
import sys
import time
import subprocess
import webbrowser
from threading import Thread

def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("🎭 COMPLETE EMOTION DETECTION & MOOD FILTER SYSTEM 🎨")
    print("=" * 70)
    print("Features:")
    print("✅ Real-time Emotion Detection (10-second capture)")
    print("✅ AnimeGAN MOOD Filter (3 artistic styles)")
    print("✅ Web Interface with Chat Bot")
    print("✅ Analytics Dashboard")
    print("✅ Beautiful Ghibli-style Art Gallery")
    print("=" * 70)

def check_dependencies():
    """Check which dependencies are available"""
    print("\n🔍 Checking Dependencies...")
    
    deps = {
        'opencv-python': False,
        'flask': False,
        'deepface': False,
        'tensorflow': False,
        'numpy': False,
        'pillow': False
    }
    
    # Check each dependency
    for dep in deps:
        try:
            if dep == 'opencv-python':
                import cv2
                deps[dep] = True
                print(f"✅ OpenCV: {cv2.__version__}")
            elif dep == 'flask':
                import flask
                deps[dep] = True
                print(f"✅ Flask: {flask.__version__}")
            elif dep == 'deepface':
                from deepface import DeepFace
                deps[dep] = True
                print("✅ DeepFace: Available")
            elif dep == 'tensorflow':
                import tensorflow as tf
                deps[dep] = True
                print(f"✅ TensorFlow: {tf.__version__}")
            elif dep == 'numpy':
                import numpy as np
                deps[dep] = True
                print(f"✅ NumPy: {np.__version__}")
            elif dep == 'pillow':
                import PIL
                deps[dep] = True
                print(f"✅ Pillow: {PIL.__version__}")
        except ImportError:
            print(f"❌ {dep}: Not available")
    
    return deps

def test_camera():
    """Test camera availability"""
    print("\n📷 Testing Camera...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera is available")
            cap.release()
            return True
        else:
            print("❌ Camera not available")
            return False
    except:
        print("❌ Cannot test camera (OpenCV not available)")
        return False

def test_components(deps):
    """Test individual components"""
    print("\n🧪 Testing Components...")
    
    # Test database
    try:
        from database import EmotionDatabase
        db = EmotionDatabase()
        print("✅ Database: Working")
    except Exception as e:
        print(f"❌ Database: {e}")
    
    # Test emotion detector
    if deps['opencv-python']:
        try:
            if deps['deepface']:
                from emotion_detector import EmotionDetector
                detector = EmotionDetector(use_database=False)
                print("✅ Emotion Detector: Full functionality")
            else:
                from simple_emotion_detector import SimpleEmotionDetector
                detector = SimpleEmotionDetector(use_database=False)
                print("✅ Emotion Detector: Simulated mode (no DeepFace)")
        except Exception as e:
            print(f"❌ Emotion Detector: {e}")
    
    # Test MOOD filter
    try:
        from anime_mood_filter import AnimeGANMoodFilter
        mood_filter = AnimeGANMoodFilter(style='Hayao')
        if deps['tensorflow']:
            print("✅ MOOD Filter: Full AnimeGAN functionality")
        else:
            print("✅ MOOD Filter: Simulated anime effects")
    except Exception as e:
        print(f"❌ MOOD Filter: {e}")

def start_web_server():
    """Start the Flask web server"""
    print("\n🌐 Starting Web Server...")
    try:
        # Import and run Flask app
        from app import app
        app.run(debug=False, port=5055, use_reloader=False)
    except Exception as e:
        print(f"❌ Failed to start web server: {e}")

def open_browser():
    """Open browser to the application"""
    time.sleep(2)  # Wait for server to start
    print("🚀 Opening browser...")
    try:
        webbrowser.open('http://localhost:5055/')
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print("   Please manually visit: http://localhost:5055/")

def show_usage_guide():
    """Show how to use the system"""
    print("\n📚 USAGE GUIDE:")
    print("=" * 50)
    print("\n🎭 EMOTION DETECTION:")
    print("1. Go to: http://localhost:5055/")
    print("2. Click the camera button in the chat")
    print("3. Show expressions for 10 seconds")
    print("4. Select from Ghibli-style emotion gallery")
    print("5. Chat with the bot about your emotions!")
    
    print("\n🎨 MOOD FILTER (AnimeGAN):")
    print("1. Go to: http://localhost:5055/mood-filter")
    print("2. Choose a style:")
    print("   🌿 Hayao - Ghibli-inspired warm tones")
    print("   🌟 Shinkai - Vibrant cinematic style")
    print("   🎭 Paprika - Psychedelic dream effects")
    print("3. Test the filter first")
    print("4. Capture and transform your image!")
    
    print("\n📊 ANALYTICS:")
    print("• Visit: http://localhost:5055/dashboard")
    print("• View emotion statistics and patterns")
    
    print("\n💡 TIPS:")
    print("• Ensure good lighting for better detection")
    print("• Try different expressions during capture")
    print("• Each style creates unique artistic effects")
    print("=" * 50)

def main():
    """Main demo function"""
    print_banner()
    
    # Check dependencies
    deps = check_dependencies()
    
    # Test camera
    camera_available = test_camera()
    
    # Test components
    test_components(deps)
    
    # Check if we can run the web app
    if not deps['flask']:
        print("\n❌ Cannot start web interface (Flask not available)")
        print("   Install Flask: pip install flask")
        return
    
    if not deps['opencv-python']:
        print("\n⚠️  OpenCV not available - some features may not work")
        print("   Install OpenCV: pip install opencv-python")
    
    print("\n🎉 SYSTEM READY!")
    
    # Show what will work
    print("\n🔧 Available Features:")
    if deps['flask']:
        print("✅ Web Interface")
    if deps['opencv-python'] and camera_available:
        print("✅ Camera Capture")
    if deps['deepface']:
        print("✅ Real Emotion Detection")
    else:
        print("⚠️  Simulated Emotion Detection (install deepface for real detection)")
    if deps['tensorflow']:
        print("✅ Real AnimeGAN Transformations")
    else:
        print("⚠️  Simulated Anime Filters (install tensorflow for AnimeGAN)")
    
    # Ask user if they want to continue
    print("\n" + "=" * 50)
    choice = input("🚀 Start the web application? (y/n): ").lower().strip()
    
    if choice in ['y', 'yes']:
        show_usage_guide()
        
        print("\n🌐 Starting the application...")
        print("   Web Server: http://localhost:5055/")
        print("   Press Ctrl+C to stop")
        
        # Start browser in a separate thread
        Thread(target=open_browser, daemon=True).start()
        
        # Start web server (this will block)
        try:
            start_web_server()
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user")
        except Exception as e:
            print(f"\n❌ Application error: {e}")
    else:
        print("\n👋 Demo cancelled. Run again when ready!")
        
    print("\n📝 To install missing dependencies:")
    if not deps['deepface']:
        print("   pip install deepface")
    if not deps['tensorflow']:
        print("   pip install tensorflow")
    if not deps['opencv-python']:
        print("   pip install opencv-python")
    
    print("\n✨ Thank you for trying the Emotion Detection & MOOD Filter System!")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Emotion Detection Chatbot Launcher
Run this script to start the emotion detection chatbot with Ghibli-style emotion selection.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from emotion_chatbot_gui import main
    print("🎭 Starting Emotion Detection Chatbot...")
    print("📋 Features:")
    print("   • 10-second emotion detection")
    print("   • Ghibli-style emotion art gallery")
    print("   • Interactive chatbot interface")
    print("   • Database storage of emotions")
    print("\n🚀 Launching application...")
    main()
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Please make sure all dependencies are installed:")
    print("   pip install opencv-python deepface pillow tkinter")
except Exception as e:
    print(f"❌ Error starting application: {e}")
    input("Press Enter to exit...")
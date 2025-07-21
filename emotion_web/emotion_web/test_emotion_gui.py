#!/usr/bin/env python3
"""
Test script for the Emotion Detection GUI system
Run this to verify all components are working correctly.
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import tkinter as tk
        print("✅ Tkinter available")
    except ImportError:
        print("❌ Tkinter not available")
        return False
    
    try:
        import cv2
        print("✅ OpenCV available")
    except ImportError:
        print("❌ OpenCV not available - install with: pip install opencv-python")
        return False
    
    try:
        from PIL import Image, ImageTk
        print("✅ PIL/Pillow available")
    except ImportError:
        print("❌ PIL/Pillow not available - install with: pip install pillow")
        return False
    
    try:
        from deepface import DeepFace
        print("✅ DeepFace available")
    except ImportError:
        print("❌ DeepFace not available - install with: pip install deepface")
        return False
    
    try:
        from database import EmotionDatabase
        print("✅ Database module available")
    except ImportError:
        print("❌ Database module not available - check database.py")
        return False
    
    return True

def test_camera():
    """Test if camera is accessible"""
    print("\n📹 Testing camera access...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            print("✅ Camera accessible")
            ret, frame = cap.read()
            if ret:
                print("✅ Camera can capture frames")
                print(f"   Frame size: {frame.shape}")
            else:
                print("❌ Camera cannot capture frames")
            cap.release()
            return True
        else:
            print("❌ Camera not accessible")
            return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_images():
    """Test if Ghibli-style images exist"""
    print("\n🎨 Testing Ghibli-style images...")
    
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
    emotions = ['happy', 'sad', 'angry', 'surprised', 'neutral', 'fear', 'disgust']
    
    if not os.path.exists(images_dir):
        print(f"❌ Images directory not found: {images_dir}")
        print("   Run: python3 create_ghibli_images.py")
        return False
    
    missing_images = []
    for emotion in emotions:
        image_path = os.path.join(images_dir, f"{emotion}.png")
        if os.path.exists(image_path):
            print(f"✅ {emotion}.png exists")
        else:
            print(f"❌ {emotion}.png missing")
            missing_images.append(emotion)
    
    if missing_images:
        print(f"❌ Missing images: {missing_images}")
        print("   Run: python3 create_ghibli_images.py")
        return False
    
    return True

def test_gui_creation():
    """Test if GUI can be created without errors"""
    print("\n🖥️  Testing GUI creation...")
    
    try:
        import tkinter as tk
        from emotion_chatbot_gui import EmotionChatbotGUI
        
        # Create a test root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Try to create the GUI
        app = EmotionChatbotGUI(root)
        print("✅ GUI created successfully")
        
        # Clean up
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI creation failed: {e}")
        return False

def test_detection_function():
    """Test if the detection function can be imported and has correct signature"""
    print("\n🧠 Testing detection function...")
    
    try:
        from web_emotion_detect import detect_emotions_for_web
        print("✅ Detection function imported")
        
        # Check if function signature is updated (should return tuple)
        import inspect
        sig = inspect.signature(detect_emotions_for_web)
        print(f"✅ Function signature: {sig}")
        
        return True
        
    except Exception as e:
        print(f"❌ Detection function test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🎭 Emotion Detection GUI - System Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Camera", test_camera),
        ("Images", test_images),
        ("GUI Creation", test_gui_creation),
        ("Detection Function", test_detection_function)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! You're ready to run the emotion detection GUI!")
        print("\nTo start the application:")
        print("   python3 run_emotion_chatbot.py")
        print("   or")
        print("   python3 emotion_chatbot_gui.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before running the application.")
        
        # Provide specific guidance
        if not any(name == "Images" and result for name, result in results):
            print("\n💡 To create missing images:")
            print("   python3 create_ghibli_images.py")
        
        if not any(name == "Imports" and result for name, result in results):
            print("\n💡 To install missing packages:")
            print("   pip install opencv-python deepface pillow")

if __name__ == "__main__":
    run_all_tests()
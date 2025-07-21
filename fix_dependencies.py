#!/usr/bin/env python3
"""
Dependency Fix Script for Real-Time Chat Website
This script checks and fixes AI feature dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✓ {module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"✗ {module_name} import failed: {e}")
        if package_name:
            print(f"  Attempting to install {package_name}...")
            if install_package(package_name):
                try:
                    __import__(module_name)
                    print(f"✓ {module_name} imported successfully after installation")
                    return True
                except ImportError:
                    print(f"✗ {module_name} still not working after installation")
        return False
    except Exception as e:
        print(f"✗ {module_name} import error: {e}")
        return False

def main():
    """Main dependency check and fix function"""
    print("=" * 60)
    print("🔧 AI Features Dependency Fix")
    print("=" * 60)
    
    # Check basic dependencies
    basic_deps = [
        ("cv2", "opencv-python"),
        ("numpy", "numpy"),
        ("PIL", "Pillow"),
        ("flask", "Flask"),
        ("flask_socketio", "Flask-SocketIO"),
        ("bcrypt", "bcrypt")
    ]
    
    print("\n📦 Checking basic dependencies:")
    basic_ok = True
    for module, package in basic_deps:
        if not test_import(module, package):
            basic_ok = False
    
    # Check AI dependencies
    print("\n🤖 Checking AI dependencies:")
    
    # Test TensorFlow/DeepFace
    tf_works = test_import("tensorflow", "tensorflow")
    if tf_works:
        deepface_works = test_import("deepface", "deepface")
    else:
        print("⚠ Skipping DeepFace due to TensorFlow issues")
        deepface_works = False
    
    # Test OpenCV camera access
    print("\n📹 Testing camera access:")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ Camera access working")
            cap.release()
            camera_ok = True
        else:
            print("✗ Camera not accessible")
            camera_ok = False
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        camera_ok = False
    
    # Generate configuration
    print("\n📝 Generating configuration:")
    
    config = {
        'basic_deps_ok': basic_ok,
        'tensorflow_available': tf_works,
        'deepface_available': deepface_works,
        'camera_available': camera_ok,
        'emotion_mode': 'advanced' if deepface_works else 'simple' if camera_ok else 'disabled',
        'anime_filter_available': camera_ok and basic_ok
    }
    
    # Create config file
    with open('ai_config.py', 'w') as f:
        f.write("# AI Configuration - Auto-generated\n")
        f.write("# This file is created by fix_dependencies.py\n\n")
        for key, value in config.items():
            f.write(f"{key.upper()} = {repr(value)}\n")
    
    print("✓ Configuration saved to ai_config.py")
    
    # Show summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print("=" * 60)
    
    if config['basic_deps_ok']:
        print("✓ Basic dependencies: WORKING")
    else:
        print("✗ Basic dependencies: ISSUES - Please install missing packages")
    
    if config['emotion_mode'] == 'advanced':
        print("✓ Emotion Detection: ADVANCED (with DeepFace)")
    elif config['emotion_mode'] == 'simple':
        print("⚠ Emotion Detection: SIMPLIFIED (without DeepFace)")
    else:
        print("✗ Emotion Detection: DISABLED")
    
    if config['anime_filter_available']:
        print("✓ Anime Mood Filter: WORKING")
    else:
        print("✗ Anime Mood Filter: DISABLED")
    
    if config['camera_available']:
        print("✓ Camera Access: WORKING")
    else:
        print("✗ Camera Access: NOT AVAILABLE")
    
    print("\n🚀 Ready to start the application!")
    print("Run: python3 run.py")
    
    return config

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test camera fixes for emotion detection and mood filter
"""

import cv2
import time

def test_camera_backends():
    """Test different camera backends"""
    print("Testing camera backends...")
    
    backends_to_try = [
        (cv2.CAP_AVFOUNDATION, "AVFoundation (macOS native)"),
        (cv2.CAP_ANY, "Default backend"),
        (0, "Direct index")
    ]
    
    working_backends = []
    
    for backend, name in backends_to_try:
        try:
            print(f"\nTesting {name}...")
            
            if isinstance(backend, int):
                cap = cv2.VideoCapture(backend)
            else:
                cap = cv2.VideoCapture(0, backend)
            
            if cap.isOpened():
                # Test if we can actually read from camera
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✓ {name} - SUCCESS")
                    print(f"  Frame shape: {frame.shape}")
                    working_backends.append((backend, name))
                else:
                    print(f"✗ {name} - Can't read frames")
                cap.release()
            else:
                print(f"✗ {name} - Can't open camera")
                
        except Exception as e:
            print(f"✗ {name} - Error: {e}")
    
    return working_backends

def test_emotion_detector():
    """Test the updated emotion detector"""
    print("\n" + "="*50)
    print("Testing Updated Emotion Detector")
    print("="*50)
    
    try:
        from simple_emotion_detector import EmotionDetector
        detector = EmotionDetector()
        print("✓ Emotion detector initialized")
        
        # Test without actually opening camera window (just initialization)
        print("✓ Emotion detector is ready for use")
        return True
        
    except Exception as e:
        print(f"✗ Emotion detector failed: {e}")
        return False

def test_mood_filter():
    """Test the updated mood filter"""
    print("\n" + "="*50)
    print("Testing Updated Mood Filter")
    print("="*50)
    
    try:
        from anime_mood_filter import AnimeMoodFilter
        filter_app = AnimeMoodFilter('Shinkai')
        print("✓ Mood filter initialized")
        
        # Test camera opening (without full capture)
        cap = filter_app.open_camera()
        if cap:
            print("✓ Camera can be opened for mood filter")
            cap.release()
            return True
        else:
            print("✗ Camera cannot be opened for mood filter")
            return False
            
    except Exception as e:
        print(f"✗ Mood filter failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Camera Fix Test Suite")
    print("="*50)
    
    # Test camera backends
    working_backends = test_camera_backends()
    
    if working_backends:
        print(f"\n✅ Found {len(working_backends)} working camera backend(s):")
        for backend, name in working_backends:
            print(f"  - {name}")
    else:
        print("\n❌ No working camera backends found!")
        print("Please check:")
        print("1. Camera permissions in System Preferences > Security & Privacy > Camera")
        print("2. No other applications are using the camera")
        print("3. Camera is properly connected")
        exit(1)
    
    # Test emotion detector
    emotion_ok = test_emotion_detector()
    
    # Test mood filter
    mood_ok = test_mood_filter()
    
    print("\n" + "="*50)
    print("📋 Test Results Summary")
    print("="*50)
    
    if working_backends and emotion_ok and mood_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✓ Camera backends working")
        print("✓ Emotion detector ready")
        print("✓ Mood filter ready")
        print("\nThe camera fixes should resolve the OpenCV C++ exception error.")
        print("You can now try the emotion detection and mood filter features!")
    else:
        print("⚠ Some issues found:")
        if not working_backends:
            print("✗ Camera access issues")
        if not emotion_ok:
            print("✗ Emotion detector issues")
        if not mood_ok:
            print("✗ Mood filter issues")
    
    print("="*50)
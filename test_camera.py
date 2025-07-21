#!/usr/bin/env python3
"""
Quick camera diagnostic test
"""

import cv2
import sys

def test_camera():
    """Test camera access with different backends"""
    print("🔍 Camera Diagnostic Test")
    print("=" * 40)
    
    backends = [
        (cv2.CAP_AVFOUNDATION, "AVFoundation (macOS)"),
        (cv2.CAP_ANY, "Default backend"),
        (0, "Direct camera access"),
        (1, "Secondary camera")
    ]
    
    working_cameras = []
    
    for backend, name in backends:
        try:
            print(f"Testing {name}...")
            
            if isinstance(backend, int):
                cap = cv2.VideoCapture(backend)
            else:
                cap = cv2.VideoCapture(0, backend)
            
            if cap and cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    print(f"✅ {name} - WORKING")
                    working_cameras.append((backend, name))
                    
                    # Get camera info
                    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    print(f"   Resolution: {int(width)}x{int(height)}")
                    print(f"   FPS: {fps}")
                else:
                    print(f"❌ {name} - Can't read frames")
                
                cap.release()
            else:
                print(f"❌ {name} - Can't open")
                
        except Exception as e:
            print(f"❌ {name} - Error: {e}")
    
    print("=" * 40)
    if working_cameras:
        print(f"✅ Found {len(working_cameras)} working camera(s)")
        for backend, name in working_cameras:
            print(f"   - {name}")
        print("\n💡 Mood filter should work with these cameras")
    else:
        print("❌ No working cameras found")
        print("\n💡 Possible solutions:")
        print("   - Check System Preferences > Security & Privacy > Camera")
        print("   - Close other apps using camera (Zoom, Skype, etc.)")
        print("   - Use Browser Camera or Simulate options instead")
    
    return len(working_cameras) > 0

if __name__ == "__main__":
    test_camera()
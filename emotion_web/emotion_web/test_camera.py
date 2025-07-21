import cv2
import time
import sys

print("Testing camera access...")

try:
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Could not open camera")
        sys.exit(1)
    
    print("Camera opened successfully")
    
    # Test reading a few frames
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"Frame {i+1}: {frame.shape}")
        else:
            print(f"Failed to read frame {i+1}")
        time.sleep(0.5)
    
    cap.release()
    print("Camera test completed successfully")
    
except Exception as e:
    print(f"Error: {e}")
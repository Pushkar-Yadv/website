"""
Professional Anime MOOD Filter for ChatApp
Uses advanced image processing techniques to create anime-style transformations
"""

import os
import cv2
import numpy as np
import time
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter
import random

class AnimeMoodFilter:
    """Professional anime-style filter with multiple styles"""
    
    def __init__(self, style='Hayao'):
        """
        Initialize Anime MOOD Filter
        
        Args:
            style (str): Animation style - 'Hayao', 'Shinkai', or 'Paprika'
        """
        self.style = style
        self.output_dir = os.path.join("static", "anime_captures")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Style configurations
        self.style_configs = {
            'Hayao': {
                'name': 'Studio Ghibli Style',
                'description': 'Warm, soft colors inspired by Miyazaki films',
                'color_temp': 1.1,
                'saturation': 1.0,
                'edge_strength': 0.1
            },
            'Shinkai': {
                'name': 'Makoto Shinkai Style', 
                'description': 'Vibrant, saturated colors with dramatic lighting',
                'color_temp': 1.0,
                'saturation': 1.3,
                'edge_strength': 0.15
            },
            'Paprika': {
                'name': 'Satoshi Kon Style',
                'description': 'Psychedelic, intense colors with surreal effects',
                'color_temp': 0.9,
                'saturation': 1.4,
                'edge_strength': 0.2
            }
        }
        
        print(f"✓ Anime MOOD Filter initialized with {style} style")
        print(f"Style: {self.style_configs[style]['name']}")
    
    def open_camera(self):
        """Open camera for capture with macOS compatibility"""
        try:
            print("Initializing camera for mood filter...")
            
            # Try different camera backends for macOS compatibility
            backends_to_try = [
                cv2.CAP_AVFOUNDATION,  # macOS native
                cv2.CAP_ANY,           # Default
                0                      # Direct index
            ]
            
            cap = None
            for backend in backends_to_try:
                try:
                    if isinstance(backend, int):
                        cap = cv2.VideoCapture(backend)
                    else:
                        cap = cv2.VideoCapture(0, backend)
                    
                    if cap.isOpened():
                        # Test if we can actually read from camera
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            print(f"✓ Camera opened successfully with backend: {backend}")
                            break
                        else:
                            cap.release()
                            cap = None
                    else:
                        if cap:
                            cap.release()
                        cap = None
                except Exception as e:
                    print(f"Backend {backend} failed: {e}")
                    if cap:
                        cap.release()
                    cap = None
                    continue
            
            if not cap or not cap.isOpened():
                print("Could not access camera")
                return None
            
            # Set camera properties for better compatibility
            try:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 15)  # Lower FPS for stability
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer
            except Exception as e:
                print(f"Warning: Could not set camera properties: {e}")
            
            # Camera warm-up
            print("Camera warming up...")
            for i in range(3):
                ret, frame = cap.read()
                if not ret:
                    cap.release()
                    return None
                time.sleep(0.1)
            
            return cap
            
        except Exception as e:
            print(f"Error opening camera: {e}")
            return None
    
    def capture_image_with_preview(self, preview_duration=5):
        """Capture image with preview"""
        print(f"Opening camera preview for {preview_duration} seconds...")
        
        cap = self.open_camera()
        if not cap:
            return None
        
        start_time = time.time()
        captured_frame = None
        
        print("Press SPACE to capture or wait for auto-capture")
        
        try:
            while True:
                try:
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        print("Failed to read from camera")
                        break
                    
                    elapsed_time = time.time() - start_time
                    remaining_time = preview_duration - elapsed_time
                    
                    # Add preview overlay
                    preview_frame = frame.copy()
                    
                    # Style info
                    style_info = self.style_configs[self.style]
                    cv2.putText(preview_frame, f"Anime Filter: {style_info['name']}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    cv2.putText(preview_frame, style_info['description'][:50], (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    
                    # Countdown
                    if remaining_time > 0:
                        cv2.putText(preview_frame, f"Capture in: {max(0, int(remaining_time))}s", (10, 100), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    else:
                        cv2.putText(preview_frame, "Auto-capturing...", (10, 100), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    cv2.putText(preview_frame, "Press SPACE to capture now", (10, 130), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                    cv2.putText(preview_frame, "Press ESC to cancel", (10, 160), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                    
                    cv2.imshow(f'Anime Filter Preview - {self.style}', preview_frame)
                    
                    key = cv2.waitKey(30) & 0xFF
                    if key == ord(' '):  # Space bar
                        captured_frame = frame.copy()
                        print("Image captured by user!")
                        break
                    elif key == 27:  # Escape
                        print("Capture cancelled")
                        break
                    elif elapsed_time >= preview_duration:
                        captured_frame = frame.copy()
                        print("Auto-captured after countdown!")
                        break
                        
                except cv2.error as e:
                    print(f"OpenCV error in preview loop: {e}")
                    break
                except Exception as e:
                    print(f"Unexpected error in preview loop: {e}")
                    break
        
        except Exception as e:
            print(f"Error in capture preview: {e}")
        finally:
            try:
                cap.release()
                cv2.destroyAllWindows()
            except:
                pass
        
        return captured_frame
    
    def apply_anime_filter(self, image):
        """Apply anime-style filter to image using advanced image processing"""
        try:
            print(f"Applying {self.style} anime filter...")
            start_time = time.time()
            
            # Get style configuration
            config = self.style_configs[self.style]
            
            # Start with the original image
            anime_image = image.copy()
            
            # Step 1: Bilateral Filter for smoothing while preserving edges
            anime_image = cv2.bilateralFilter(anime_image, 15, 200, 200)
            anime_image = cv2.bilateralFilter(anime_image, 15, 200, 200)  # Apply twice for stronger effect
            
            # Step 2: Color quantization to reduce color palette (anime-like effect)
            data = anime_image.reshape((-1, 3))
            data = np.float32(data)
            
            # K-means clustering for color reduction
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            k = 12 if self.style == 'Paprika' else 8  # More colors for Paprika style
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to uint8
            centers = np.uint8(centers)
            quantized = centers[labels.flatten()]
            anime_image = quantized.reshape(image.shape)
            
            # Step 3: Edge detection and enhancement
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 10)
            edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
            # Step 4: Style-specific adjustments
            if self.style == 'Hayao':
                # Miyazaki style - warm, soft colors
                anime_image = self._adjust_color_temperature(anime_image, config['color_temp'])
                anime_image = cv2.addWeighted(anime_image, 0.9, edges, config['edge_strength'], 0)
                
            elif self.style == 'Shinkai':
                # Shinkai style - vibrant, saturated colors
                anime_image = self._enhance_saturation(anime_image, config['saturation'])
                anime_image = cv2.addWeighted(anime_image, 0.85, edges, config['edge_strength'], 0)
                
            elif self.style == 'Paprika':
                # Paprika style - psychedelic, intense colors
                anime_image = self._apply_color_shift(anime_image)
                anime_image = self._enhance_saturation(anime_image, config['saturation'])
                anime_image = cv2.addWeighted(anime_image, 0.8, edges, config['edge_strength'], 0)
            
            # Step 5: Final smoothing and enhancement
            anime_image = cv2.bilateralFilter(anime_image, 9, 300, 300)
            
            # Step 6: Brightness and contrast adjustment
            anime_image = self._adjust_brightness_contrast(anime_image, brightness=10, contrast=1.1)
            
            process_time = time.time() - start_time
            print(f"✓ {self.style} anime filter applied successfully in {process_time:.2f} seconds!")
            
            return anime_image
            
        except Exception as e:
            print(f"Error applying anime filter: {e}")
            return None
    
    def _adjust_color_temperature(self, image, factor):
        """Adjust color temperature of image"""
        try:
            # Convert to float for processing
            img_float = image.astype(np.float32)
            
            # Adjust blue and red channels
            if factor > 1.0:  # Warmer
                img_float[:, :, 0] *= 0.9  # Reduce blue
                img_float[:, :, 2] *= factor  # Increase red
            else:  # Cooler
                img_float[:, :, 0] *= (2.0 - factor)  # Increase blue
                img_float[:, :, 2] *= factor  # Reduce red
            
            # Clip values and convert back
            img_float = np.clip(img_float, 0, 255)
            return img_float.astype(np.uint8)
            
        except Exception as e:
            print(f"Error adjusting color temperature: {e}")
            return image
    
    def _enhance_saturation(self, image, factor):
        """Enhance saturation of image"""
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hsv = hsv.astype(np.float32)
            
            # Enhance saturation
            hsv[:, :, 1] *= factor
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
            
            # Convert back to BGR
            hsv = hsv.astype(np.uint8)
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
        except Exception as e:
            print(f"Error enhancing saturation: {e}")
            return image
    
    def _apply_color_shift(self, image):
        """Apply psychedelic color shift for Paprika style"""
        try:
            # Convert to HSV for hue manipulation
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hsv = hsv.astype(np.float32)
            
            # Apply random hue shift to different regions
            h, w = hsv.shape[:2]
            
            # Create gradient hue shift
            hue_shift = np.zeros((h, w), dtype=np.float32)
            for i in range(h):
                for j in range(w):
                    # Create wave pattern for hue shift
                    shift = 30 * np.sin(i * 0.01) * np.cos(j * 0.01)
                    hue_shift[i, j] = shift
            
            # Apply hue shift
            hsv[:, :, 0] += hue_shift
            hsv[:, :, 0] = np.mod(hsv[:, :, 0], 180)  # Wrap around hue values
            
            # Convert back to BGR
            hsv = hsv.astype(np.uint8)
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
        except Exception as e:
            print(f"Error applying color shift: {e}")
            return image
    
    def _adjust_brightness_contrast(self, image, brightness=0, contrast=1.0):
        """Adjust brightness and contrast"""
        try:
            # Apply brightness and contrast
            adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
            return adjusted
            
        except Exception as e:
            print(f"Error adjusting brightness/contrast: {e}")
            return image
    
    def capture_image_improved(self, web_mode=True):
        """Improved camera capture with multiple backends and web server compatibility"""
        cap = None
        try:
            print("🎨 Starting mood filter camera capture...")
            
            # Try multiple camera backends with more options
            backends = [
                (cv2.CAP_AVFOUNDATION, "AVFoundation (macOS)"),
                (cv2.CAP_ANY, "Default backend"),
                (0, "Direct camera access"),
                (1, "Secondary camera")
            ]
            
            for backend, name in backends:
                try:
                    print(f"Trying {name}...")
                    if isinstance(backend, int):
                        cap = cv2.VideoCapture(backend)
                    else:
                        cap = cv2.VideoCapture(0, backend)
                    
                    if cap and cap.isOpened():
                        # Test if we can actually read frames
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None and test_frame.size > 0:
                            print(f"✅ Camera working with {name}")
                            break
                        else:
                            print(f"❌ {name} - can't read frames")
                            cap.release()
                            cap = None
                    else:
                        print(f"❌ {name} - can't open camera")
                        if cap:
                            cap.release()
                        cap = None
                except Exception as e:
                    print(f"❌ {name} - error: {e}")
                    if cap:
                        try:
                            cap.release()
                        except:
                            pass
                    cap = None
                    continue
            
            if not cap or not cap.isOpened():
                print("❌ Could not access camera with any backend")
                print("💡 Possible solutions:")
                print("   - Check camera permissions in System Preferences")
                print("   - Close other apps using camera (Zoom, Skype, etc.)")
                print("   - Try the Browser Camera option instead")
                return None
            
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Warm up camera
            for i in range(5):
                ret, frame = cap.read()
                if not ret:
                    cap.release()
                    return None
                time.sleep(0.1)
            
            print("Camera ready! Taking photo in 3 seconds...")
            
            # Show countdown
            for countdown in range(3, 0, -1):
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Create display frame
                display_frame = frame.copy()
                style_info = self.style_configs[self.style]
                
                # Add overlay
                cv2.rectangle(display_frame, (0, 0), (640, 120), (0, 0, 0), -1)
                cv2.putText(display_frame, f"MOOD FILTER: {style_info['name']}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (233, 30, 99), 2)
                cv2.putText(display_frame, f"Taking photo in: {countdown}", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(display_frame, style_info['description'], (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # Only show preview if not in web mode
                if not web_mode:
                    try:
                        cv2.imshow('Mood Filter Capture', display_frame)
                        cv2.waitKey(1000)  # Wait 1 second
                    except:
                        pass
                else:
                    print(f"📸 Taking photo in {countdown} seconds...")
                    time.sleep(1)
            
            # Final capture
            ret, final_frame = cap.read()
            if not ret:
                cap.release()
                cv2.destroyAllWindows()
                return None
            
            # Show "Processing..." message
            display_frame = final_frame.copy()
            cv2.rectangle(display_frame, (0, 0), (640, 80), (0, 0, 0), -1)
            cv2.putText(display_frame, "PROCESSING MOOD FILTER...", (10, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            # Only show processing message if not in web mode
            if not web_mode:
                try:
                    cv2.imshow('Mood Filter Capture', display_frame)
                    cv2.waitKey(1000)
                    cv2.destroyAllWindows()
                except:
                    pass
            else:
                print("🎨 Processing mood filter...")
                time.sleep(1)
            
            cap.release()
            
            print("✓ Image captured successfully!")
            return final_frame
            
        except Exception as e:
            print(f"Camera capture error: {e}")
            if cap:
                try:
                    cap.release()
                    if not web_mode:
                        cv2.destroyAllWindows()
                except:
                    pass
            return None
    
    def apply_mood_filter(self):
        """Main function to apply mood filter with camera capture"""
        try:
            print(f"Starting {self.style} MOOD Filter...")
            
            # Try improved camera capture (web server mode)
            captured_image = self.capture_image_improved(web_mode=True)
            if captured_image is None:
                return {
                    'success': False,
                    'message': 'Camera not accessible. Try: 1) Check camera permissions 2) Close other camera apps 3) Use Browser Camera button instead',
                    'suggestions': [
                        'Check System Preferences > Security & Privacy > Camera',
                        'Close apps like Zoom, Skype, or FaceTime',
                        'Try the "Browser Camera" button instead',
                        'Use "Simulate Filter" for instant results'
                    ]
                }
            
            # Apply anime filter
            filtered_image = self.apply_anime_filter(captured_image)
            if filtered_image is None:
                return {
                    'success': False,
                    'message': 'Failed to apply anime filter'
                }
            
            # Save both original and filtered images
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save original
            original_filename = f"original_{timestamp}.jpg"
            original_path = os.path.join(self.output_dir, original_filename)
            cv2.imwrite(original_path, captured_image)
            
            # Save filtered
            filtered_filename = f"anime_{self.style.lower()}_{timestamp}.jpg"
            filtered_path = os.path.join(self.output_dir, filtered_filename)
            cv2.imwrite(filtered_path, filtered_image)
            
            # Show result for 3 seconds
            result_display = np.hstack([
                cv2.resize(captured_image, (400, 300)),
                cv2.resize(filtered_image, (400, 300))
            ])
            
            cv2.putText(result_display, "Original", (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(result_display, f"{self.style} Style", (450, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Only show result if not in web mode
            try:
                cv2.imshow(f'Anime Filter Result - {self.style}', result_display)
                cv2.waitKey(3000)
                cv2.destroyAllWindows()
            except:
                # Skip display in web server mode
                print(f"✅ {self.style} anime filter applied successfully!")
                print("📸 Filtered image saved and ready for sharing")
            
            style_info = self.style_configs[self.style]
            
            # Convert filtered image to base64 for chat sharing
            import base64
            _, buffer = cv2.imencode('.jpg', filtered_image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                'success': True,
                'style': self.style,
                'style_name': style_info['name'],
                'message': f'Successfully applied {style_info["name"]} filter!',
                'original_path': original_path,
                'filtered_path': filtered_path,
                'image_url': f'/static/anime_captures/{filtered_filename}',
                'image_data': image_base64,  # Base64 for chat sharing
                'description': style_info['description']
            }
            
        except Exception as e:
            print(f"Error in mood filter: {e}")
            return {
                'success': False,
                'message': f'Error applying mood filter: {str(e)}'
            }

def test_anime_filter():
    """Test the anime filter"""
    styles = ['Hayao', 'Shinkai', 'Paprika']
    
    print("Available styles:")
    for i, style in enumerate(styles, 1):
        print(f"{i}. {style}")
    
    choice = input("Choose style (1-3): ").strip()
    
    if choice in ['1', '2', '3']:
        style = styles[int(choice) - 1]
        filter_app = AnimeMoodFilter(style)
        result = filter_app.apply_mood_filter()
        print("Result:", result)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    test_anime_filter()
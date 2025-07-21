"""
Ultra-High Quality MOOD Filter using AnimeGANv2
Professional anime-style transformation with TensorFlow
"""

import os
import cv2
import numpy as np
import time
import uuid
from PIL import Image, ImageEnhance, ImageFilter
import math

# TensorFlow and AnimeGAN imports
try:
    import tensorflow.compat.v1 as tf
    tf.disable_v2_behavior()
    
    # Import AnimeGAN modules
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), 'AnimeGANv2'))
    from net import generator
    from tools.utils import load_test_data, check_folder
    
    TF_AVAILABLE = True
    print("✓ TensorFlow and AnimeGAN modules loaded successfully")
except ImportError as e:
    print(f"⚠ TensorFlow or AnimeGAN modules not available: {e}")
    print("Falling back to CPU-based anime filter simulation")
    TF_AVAILABLE = False

class AnimeGANMoodFilter:
    """Ultra-high quality anime-style filter using AnimeGANv2"""
    
    def __init__(self, style='Hayao'):
        """
        Initialize AnimeGAN MOOD Filter
        
        Args:
            style (str): Animation style - 'Hayao', 'Shinkai', or 'Paprika'
        """
        self.style = style
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'anime_captures')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Camera
        self.cap = None
        
        # AnimeGAN Model paths
        self.animegan_dir = os.path.join(os.path.dirname(__file__), 'AnimeGANv2')
        self.checkpoint_dir = os.path.join(self.animegan_dir, 'checkpoint', f'generator_{style}_weight')
        
        # TensorFlow session and model
        self.sess = None
        self.test_real = None
        self.test_generated = None
        
        # Processing parameters
        self.img_size = [512, 512]  # Higher resolution for better quality
        self.adjust_brightness = True
        
        print(f"AnimeGAN MOOD Filter initialized with {style} style")
        print(f"Checkpoint directory: {self.checkpoint_dir}")
        
        # Initialize the model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the AnimeGAN model"""
        if not TF_AVAILABLE:
            print("Using simulated anime filter (TensorFlow not available)")
            self.sess = None
            return
        
        try:
            print("Initializing AnimeGAN model...")
            
            # Reset default graph
            tf.reset_default_graph()
            
            # Create placeholder for input image
            self.test_real = tf.placeholder(tf.float32, [1, None, None, 3], name='test')
            
            # Create generator
            with tf.variable_scope("generator", reuse=False):
                self.test_generated = generator.G_net(self.test_real).fake
            
            # Create saver
            saver = tf.train.Saver()
            
            # Configure GPU
            gpu_options = tf.GPUOptions(allow_growth=True)
            config = tf.ConfigProto(allow_soft_placement=True, gpu_options=gpu_options)
            
            # Create session
            self.sess = tf.Session(config=config)
            
            # Load model weights
            ckpt = tf.train.get_checkpoint_state(self.checkpoint_dir)
            if ckpt and ckpt.model_checkpoint_path:
                ckpt_name = os.path.basename(ckpt.model_checkpoint_path)
                saver.restore(self.sess, os.path.join(self.checkpoint_dir, ckpt_name))
                print(f"✓ Successfully loaded {self.style} model: {ckpt_name}")
            else:
                raise Exception(f"Failed to find checkpoint in {self.checkpoint_dir}")
                
        except Exception as e:
            print(f"Error initializing model: {e}")
            print("Falling back to simulated anime filter...")
            self.sess = None
    
    def open_camera(self):
        """Open camera for capture"""
        try:
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise Exception("Could not open camera")
                
                # Set high-quality camera properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)
                self.cap.set(cv2.CAP_PROP_CONTRAST, 0.5)
                self.cap.set(cv2.CAP_PROP_SATURATION, 0.5)
                
                # Camera warm-up
                time.sleep(1.0)
                
            return True
        except Exception as e:
            print(f"Error opening camera: {e}")
            return False
    
    def capture_image(self, preview_duration=5):
        """Capture image with preview"""
        print(f"Opening camera preview for {preview_duration} seconds...")
        
        if not self.open_camera():
            return None
        
        start_time = time.time()
        captured_frame = None
        
        print("Press SPACE to capture or wait for auto-capture")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read from camera")
                break
            
            elapsed_time = time.time() - start_time
            remaining_time = preview_duration - elapsed_time
            
            # Add preview overlay
            preview_frame = frame.copy()
            cv2.putText(preview_frame, f"AnimeGAN {self.style} Style Preview", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(preview_frame, f"Capture in: {max(0, int(remaining_time))}s", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(preview_frame, "Press SPACE to capture now", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.imshow(f'AnimeGAN {self.style} Preview', preview_frame)
            
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
        
        cv2.destroyAllWindows()
        return captured_frame
    
    def apply_anime_filter(self, image):
        """Apply AnimeGAN filter to image"""
        if self.sess is None:
            print("Using simulated anime filter...")
            return self._apply_simulated_anime_filter(image)
        
        try:
            print(f"Applying {self.style} anime filter...")
            
            # Prepare image for processing
            if isinstance(image, str):
                # Load from file path
                processed_image = np.asarray(load_test_data(image, self.img_size))
            else:
                # Process numpy array
                # Convert BGR to RGB for processing
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Resize to processing size while maintaining aspect ratio
                h, w = rgb_image.shape[:2]
                target_h, target_w = self.img_size
                
                # Calculate scaling to fit within target size
                scale = min(target_w / w, target_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
                
                # Resize
                resized = cv2.resize(rgb_image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                
                # Pad to target size
                pad_w = (target_w - new_w) // 2
                pad_h = (target_h - new_h) // 2
                
                processed_image = np.pad(resized, 
                                       ((pad_h, target_h - new_h - pad_h), 
                                        (pad_w, target_w - new_w - pad_w), 
                                        (0, 0)), 
                                       mode='constant', constant_values=255)
                
                # Normalize to [-1, 1] range
                processed_image = (processed_image.astype(np.float32) / 127.5) - 1.0
                processed_image = np.expand_dims(processed_image, axis=0)
            
            # Generate anime-style image
            start_time = time.time()
            fake_img = self.sess.run(self.test_generated, 
                                   feed_dict={self.test_real: processed_image})
            process_time = time.time() - start_time
            
            print(f"Processing completed in {process_time:.2f} seconds")
            
            # Post-process result
            result = fake_img[0]
            
            # Convert back to [0, 255] range
            result = ((result + 1.0) * 127.5).astype(np.uint8)
            
            # Convert RGB back to BGR for OpenCV
            result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
            
            # If we padded the image, crop it back
            if not isinstance(image, str):
                if pad_h > 0 or pad_w > 0:
                    result = result[pad_h:pad_h+new_h, pad_w:pad_w+new_w]
                
                # Resize back to original dimensions
                result = cv2.resize(result, (w, h), interpolation=cv2.INTER_LANCZOS4)
            
            # Optional brightness adjustment
            if self.adjust_brightness and not isinstance(image, str):
                result = self._adjust_brightness(result, image)
            
            print(f"✓ {self.style} anime filter applied successfully!")
            return result
            
        except Exception as e:
            print(f"Error applying anime filter: {e}")
            return None
    
    def _adjust_brightness(self, anime_image, original_image):
        """Adjust brightness of anime image to match original"""
        try:
            # Convert to LAB color space for better brightness analysis
            original_lab = cv2.cvtColor(original_image, cv2.COLOR_BGR2LAB)
            anime_lab = cv2.cvtColor(anime_image, cv2.COLOR_BGR2LAB)
            
            # Calculate mean brightness
            orig_brightness = np.mean(original_lab[:, :, 0])
            anime_brightness = np.mean(anime_lab[:, :, 0])
            
            # Adjust brightness
            brightness_ratio = orig_brightness / anime_brightness if anime_brightness > 0 else 1.0
            brightness_ratio = np.clip(brightness_ratio, 0.7, 1.3)  # Limit adjustment range
            
            anime_lab[:, :, 0] = np.clip(anime_lab[:, :, 0] * brightness_ratio, 0, 255)
            
            # Convert back to BGR
            adjusted = cv2.cvtColor(anime_lab, cv2.COLOR_LAB2BGR)
            return adjusted
            
        except Exception as e:
            print(f"Error adjusting brightness: {e}")
            return anime_image
    
    def _apply_simulated_anime_filter(self, image):
        """Apply a simulated anime filter using OpenCV techniques"""
        try:
            print(f"Applying simulated {self.style} anime filter...")
            
            # Start with the original image
            anime_image = image.copy()
            
            # 1. Bilateral Filter for smoothing while preserving edges
            anime_image = cv2.bilateralFilter(anime_image, 15, 200, 200)
            
            # 2. Color quantization to reduce color palette (anime-like effect)
            data = anime_image.reshape((-1, 3))
            data = np.float32(data)
            
            # K-means clustering for color reduction
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            k = 8  # Number of colors
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to uint8
            centers = np.uint8(centers)
            quantized = centers[labels.flatten()]
            anime_image = quantized.reshape(image.shape)
            
            # 3. Edge detection and enhancement
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 10)
            edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
            # 4. Style-specific adjustments
            if self.style == 'Hayao':
                # Miyazaki style - warm, soft colors
                anime_image = self._adjust_color_temperature(anime_image, 1.1)
                anime_image = cv2.addWeighted(anime_image, 0.9, edges, 0.1, 0)
                
            elif self.style == 'Shinkai':
                # Shinkai style - vibrant, saturated colors
                anime_image = self._enhance_saturation(anime_image, 1.3)
                anime_image = cv2.addWeighted(anime_image, 0.85, edges, 0.15, 0)
                
            elif self.style == 'Paprika':
                # Paprika style - psychedelic, intense colors
                anime_image = self._apply_color_shift(anime_image)
                anime_image = cv2.addWeighted(anime_image, 0.8, edges, 0.2, 0)
            
            # 5. Final smoothing
            anime_image = cv2.GaussianBlur(anime_image, (3, 3), 0)
            
            print(f"✓ Simulated {self.style} anime filter applied successfully!")
            return anime_image
            
        except Exception as e:
            print(f"Error applying simulated anime filter: {e}")
            return image
    
    def _adjust_color_temperature(self, image, factor):
        """Adjust color temperature for warmer/cooler look"""
        result = image.copy().astype(np.float32)
        result[:, :, 2] *= factor  # Increase red channel
        result[:, :, 0] *= (2.0 - factor)  # Decrease blue channel
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def _enhance_saturation(self, image, factor):
        """Enhance color saturation"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] *= factor  # Increase saturation
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def _apply_color_shift(self, image):
        """Apply psychedelic color shift for Paprika style"""
        result = image.copy()
        # Shift color channels for psychedelic effect
        temp = result[:, :, 0].copy()
        result[:, :, 0] = result[:, :, 1]
        result[:, :, 1] = result[:, :, 2]
        result[:, :, 2] = temp
        
        # Enhance contrast
        result = cv2.convertScaleAbs(result, alpha=1.2, beta=10)
        return result
    
    def save_results(self, original_image, anime_image):
        """Save original and anime-processed images"""
        try:
            timestamp = int(time.time())
            unique_id = str(uuid.uuid4())[:8]
            
            # Save with maximum quality (PNG for lossless)
            original_filename = f"anime_original_{self.style}_{timestamp}_{unique_id}.png"
            original_path = os.path.join(self.output_dir, original_filename)
            cv2.imwrite(original_path, original_image, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            
            anime_filename = f"anime_{self.style}_{timestamp}_{unique_id}.png"
            anime_path = os.path.join(self.output_dir, anime_filename)
            cv2.imwrite(anime_path, anime_image, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            
            print(f"Original saved: {original_path}")
            print(f"Anime-style saved: {anime_path}")
            
            return {
                'original_path': original_path,
                'anime_path': anime_path,
                'original_filename': original_filename,
                'anime_filename': anime_filename
            }
            
        except Exception as e:
            print(f"Error saving results: {e}")
            return None
    
    def capture_and_apply_filter(self):
        """Complete capture and filter application process"""
        print("Starting AnimeGAN MOOD capture process...")
        
        # Capture image
        original_image = self.capture_image()
        if original_image is None:
            print("No image captured")
            return None
        
        print("Processing captured image...")
        
        # Apply anime filter
        anime_image = self.apply_anime_filter(original_image)
        if anime_image is None:
            print("Failed to apply anime filter")
            return None
        
        # Save results
        result = self.save_results(original_image, anime_image)
        if result:
            print("AnimeGAN MOOD process completed successfully!")
        
        self.close_camera()
        return result
    
    def apply_filter_to_existing_image(self, image_path):
        """Apply anime filter to existing image file"""
        try:
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                return None
            
            print(f"Loading image: {image_path}")
            original_image = cv2.imread(image_path)
            if original_image is None:
                print("Failed to load image")
                return None
            
            print(f"Applying {self.style} anime filter to existing image...")
            anime_image = self.apply_anime_filter(original_image)
            
            if anime_image is not None:
                result = self.save_results(original_image, anime_image)
                if result:
                    print("AnimeGAN filter applied to existing image successfully!")
                return result
            else:
                print("Failed to apply anime filter")
                return None
                
        except Exception as e:
            print(f"Error processing existing image: {e}")
            return None
    
    def close_camera(self):
        """Close camera and cleanup"""
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
            self.cap = None
        print("Camera closed")
    
    def close_session(self):
        """Close TensorFlow session"""
        if self.sess is not None:
            self.sess.close()
            self.sess = None
        print("TensorFlow session closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close_camera()
        self.close_session()


def main():
    """Test function for AnimeGAN MOOD Filter"""
    print("AnimeGAN Ultra-High Quality MOOD Filter")
    print("=" * 45)
    
    # Available styles
    styles = ['Hayao', 'Shinkai', 'Paprika']
    
    while True:
        print("\nAvailable Anime Styles:")
        for i, style in enumerate(styles, 1):
            print(f"{i}. {style}")
        
        style_choice = input("Choose anime style (1-3): ").strip()
        
        try:
            style_idx = int(style_choice) - 1
            if 0 <= style_idx < len(styles):
                selected_style = styles[style_idx]
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Initialize filter with selected style
    mood_filter = AnimeGANMoodFilter(style=selected_style)
    
    while True:
        print(f"\nAnimeGAN {selected_style} MOOD Filter Options:")
        print("1. Capture and apply anime filter")
        print("2. Apply filter to existing image")
        print("3. Change anime style")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            result = mood_filter.capture_and_apply_filter()
            if result:
                print("Success! Files saved:")
                print(f"Original: {result['original_filename']}")
                print(f"Anime-style: {result['anime_filename']}")
        
        elif choice == '2':
            image_path = input("Enter path to image file: ").strip()
            result = mood_filter.apply_filter_to_existing_image(image_path)
            if result:
                print("Success! Files saved:")
                print(f"Original: {result['original_filename']}")
                print(f"Anime-style: {result['anime_filename']}")
        
        elif choice == '3':
            # Close current filter
            mood_filter.close_session()
            
            # Select new style
            print("\nAvailable Anime Styles:")
            for i, style in enumerate(styles, 1):
                print(f"{i}. {style}")
            
            style_choice = input("Choose new anime style (1-3): ").strip()
            
            try:
                style_idx = int(style_choice) - 1
                if 0 <= style_idx < len(styles):
                    selected_style = styles[style_idx]
                    mood_filter = AnimeGANMoodFilter(style=selected_style)
                    print(f"Switched to {selected_style} style")
                else:
                    print("Invalid choice. Keeping current style.")
            except ValueError:
                print("Invalid input. Keeping current style.")
        
        elif choice == '4':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")
    
    mood_filter.close_session()


if __name__ == '__main__':
    main()
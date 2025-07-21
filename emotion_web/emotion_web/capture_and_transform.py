#!/usr/bin/env python3
"""
🎨 MOOD Filter Image Capture & Transform
Direct image capture and anime transformation
"""

from anime_mood_filter import AnimeGANMoodFilter
import cv2
import time
import os

def capture_and_transform_image(style='Hayao'):
    """Capture image from camera and apply MOOD filter"""
    
    print(f"🎨 Starting MOOD Filter with {style} style...")
    print("="*50)
    
    # Initialize the MOOD filter
    try:
        mood_filter = AnimeGANMoodFilter(style=style)
        print(f"✅ {style} MOOD filter initialized successfully!")
        
        if mood_filter.sess:
            print("🚀 Using real AnimeGAN transformation")
        else:
            print("🔄 Using simulated anime filter (TensorFlow not available)")
            
    except Exception as e:
        print(f"❌ Error initializing MOOD filter: {e}")
        return
    
    print(f"\n📷 Camera will open for image capture...")
    print("Instructions:")
    print("  • Position yourself in good lighting")
    print("  • Wait 5 seconds or press SPACE to capture")
    print("  • Press ESC to cancel")
    print("  • The image will be automatically transformed!")
    
    input("\nPress ENTER to start camera capture...")
    
    # Capture and apply filter
    try:
        result = mood_filter.capture_and_apply_filter()
        
        if result:
            print(f"\n🎉 SUCCESS! Image transformed with {style} style!")
            print("="*50)
            print(f"📁 Original image: {result['original_filename']}")
            print(f"🎨 Anime image: {result['anime_filename']}")
            print(f"📂 Location: {mood_filter.output_dir}")
            
            # Try to open the result images
            original_path = os.path.join(mood_filter.output_dir, result['original_filename'])
            anime_path = os.path.join(mood_filter.output_dir, result['anime_filename'])
            
            if os.path.exists(original_path) and os.path.exists(anime_path):
                print(f"\n🖼️  Opening transformed images...")
                
                # Show both images side by side
                try:
                    original = cv2.imread(original_path)
                    anime = cv2.imread(anime_path)
                    
                    if original is not None and anime is not None:
                        # Resize for display
                        height = 400
                        original_resized = cv2.resize(original, (int(original.shape[1] * height / original.shape[0]), height))
                        anime_resized = cv2.resize(anime, (int(anime.shape[1] * height / anime.shape[0]), height))
                        
                        # Create side-by-side comparison
                        combined = cv2.hconcat([original_resized, anime_resized])
                        
                        # Add labels
                        cv2.putText(combined, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.putText(combined, f"{style} Anime Style", (original_resized.shape[1] + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                        
                        cv2.imshow(f'{style} MOOD Filter - Before & After', combined)
                        print("👀 Displaying transformed image...")
                        print("   Press any key to close the image viewer")
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()
                    else:
                        print("⚠️  Could not load images for display")
                        
                except Exception as e:
                    print(f"⚠️  Could not display images: {e}")
                    
            print(f"\n✨ Your {style}-style anime transformation is complete!")
            print(f"📂 Files saved in: {mood_filter.output_dir}")
            
        else:
            print("❌ Failed to capture or transform image")
            
    except Exception as e:
        print(f"❌ Error during capture and transform: {e}")
    
    finally:
        # Cleanup
        mood_filter.cleanup()

def main():
    """Main function with style selection"""
    
    print("🎨 MOOD Filter - Image Capture & Transform")
    print("="*50)
    print("\nAvailable anime styles:")
    print("1. 🌿 Hayao - Studio Ghibli-inspired warm, natural tones")
    print("2. 🌟 Shinkai - Vibrant, cinematic anime aesthetics")  
    print("3. 🎭 Paprika - Psychedelic, dream-like transformations")
    
    while True:
        try:
            choice = input("\nSelect style (1-3) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                capture_and_transform_image('Hayao')
                break
            elif choice == '2':
                capture_and_transform_image('Shinkai')
                break
            elif choice == '3':
                capture_and_transform_image('Paprika')
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 'q'")
                
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
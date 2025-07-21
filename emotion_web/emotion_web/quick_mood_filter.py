#!/usr/bin/env python3
"""
Quick MOOD Filter - Automatic image capture and transformation
"""

from anime_mood_filter import AnimeGANMoodFilter
import cv2
import os
import time

def quick_transform(style='Hayao'):
    """Quick automatic image capture and transform"""
    
    print(f"🎨 Quick MOOD Filter - {style} Style")
    print("="*50)
    
    # Initialize filter
    try:
        mood_filter = AnimeGANMoodFilter(style=style)
        print(f"✅ {style} MOOD filter initialized!")
        
        if mood_filter.sess:
            print("🚀 Using real AnimeGAN transformation")
        else:
            print("🔄 Using simulated anime filter")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print(f"\n📷 Starting automatic image capture...")
    print("   • Camera will open in 3 seconds")
    print("   • Image will be captured automatically after 3 seconds")
    print("   • Or press SPACE to capture early")
    print("   • Press ESC to cancel")
    
    time.sleep(3)
    
    try:
        # Automatic capture and transform
        result = mood_filter.capture_and_apply_filter()
        
        if result:
            print(f"\n🎉 SUCCESS!")
            print(f"📁 Original: {result['original_filename']}")
            print(f"🎨 Transformed: {result['anime_filename']}")
            print(f"📂 Location: {mood_filter.output_dir}")
            
            # Try to show the results
            original_path = result['original_path']
            anime_path = result['anime_path']
            
            if os.path.exists(original_path) and os.path.exists(anime_path):
                try:
                    # Load and display images
                    original = cv2.imread(original_path)
                    anime = cv2.imread(anime_path)
                    
                    if original is not None and anime is not None:
                        # Resize for display
                        h, w = 300, 400
                        original_resized = cv2.resize(original, (w, h))
                        anime_resized = cv2.resize(anime, (w, h))
                        
                        # Show side by side
                        combined = cv2.hconcat([original_resized, anime_resized])
                        
                        # Add titles
                        cv2.putText(combined, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(combined, f"{style} Style", (w + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
                        
                        cv2.imshow(f'{style} MOOD Filter Result', combined)
                        print("\n👀 Displaying transformation result...")
                        print("   Press any key to close")
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()
                        
                except Exception as e:
                    print(f"⚠️  Display error: {e}")
                    
            print(f"\n✨ {style} anime transformation complete!")
            
        else:
            print("❌ Failed to capture or transform image")
            
    except Exception as e:
        print(f"❌ Error during capture: {e}")
    
    finally:
        mood_filter.close_camera()
        mood_filter.close_session()

if __name__ == '__main__':
    print("🎨 Quick MOOD Filter")
    print("Available styles:")
    print("1. Hayao - Studio Ghibli warm tones")
    print("2. Shinkai - Vibrant cinematic style") 
    print("3. Paprika - Psychedelic dream effects")
    
    # Use Hayao style by default for quick demo
    print("\n🌿 Using Hayao style for quick demo...")
    quick_transform('Hayao')
#!/usr/bin/env python3
"""
Camera fallback system for when camera access is denied
"""

import random
import os
from datetime import datetime

class CameraFallback:
    """Fallback system when camera is not available"""
    
    def __init__(self):
        self.emotions = ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral']
        self.emotion_emojis = {
            'happy': '😊',
            'sad': '😢', 
            'angry': '😠',
            'surprise': '😲',
            'fear': '😨',
            'disgust': '🤢',
            'neutral': '😐'
        }
        
        self.anime_styles = {
            'Shinkai': {
                'name': 'Makoto Shinkai Style',
                'description': 'Vibrant, saturated colors with dramatic lighting'
            },
            'Hayao': {
                'name': 'Studio Ghibli Style',
                'description': 'Warm, soft colors inspired by Miyazaki films'
            },
            'Paprika': {
                'name': 'Satoshi Kon Style',
                'description': 'Psychedelic, intense colors with surreal effects'
            }
        }
    
    def simulate_emotion_detection(self):
        """Simulate emotion detection when camera is not available"""
        emotion = random.choice(self.emotions)
        confidence = random.uniform(75.0, 95.0)
        
        return {
            'success': True,
            'emotion': emotion,
            'confidence': confidence,
            'message': f'Simulated emotion detection: {emotion} with {confidence:.1f}% confidence (Camera not available)',
            'emoji': self.emotion_emojis.get(emotion, '😐'),
            'fallback': True
        }
    
    def simulate_mood_filter(self, style='Shinkai'):
        """Simulate mood filter when camera is not available"""
        style_info = self.anime_styles.get(style, self.anime_styles['Shinkai'])
        
        # Create a placeholder image path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulated_{style.lower()}_{timestamp}.jpg"
        
        return {
            'success': True,
            'style': style,
            'style_name': style_info['name'],
            'message': f'✨ {style_info["name"]} simulation complete! Try "Browser Camera" for real photo capture.',
            'image_url': f'/static/anime_captures/{filename}',
            'description': style_info['description'],
            'fallback': True
        }
    
    def get_camera_help_message(self):
        """Get help message for camera issues"""
        return """
        Camera access is not available. This could be due to:
        
        1. Camera permissions not granted
           → Go to System Preferences > Security & Privacy > Camera
           → Enable camera access for your browser or Python
        
        2. Camera is being used by another application
           → Close other apps that might be using the camera
           → Try refreshing the page
        
        3. No camera connected
           → Make sure your camera is properly connected
           → Try using a different camera if available
        
        For now, you can use the simulated AI features to test the functionality.
        """
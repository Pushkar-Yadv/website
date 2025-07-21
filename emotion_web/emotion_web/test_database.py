#!/usr/bin/env python3
"""
Test script for the emotion database functionality
"""

from database import EmotionDatabase
import json
from datetime import datetime

def test_database():
    """Test database operations"""
    print("Testing Emotion Database...")
    
    # Initialize database
    db = EmotionDatabase()
    print("✓ Database initialized")
    
    # Test saving emotion records
    print("\nTesting emotion record saving...")
    
    test_records = [
        {'emotion': 'happy', 'confidence': 0.85, 'face_coords': {'x': 100, 'y': 50, 'width': 80, 'height': 80}},
        {'emotion': 'sad', 'confidence': 0.72, 'face_coords': {'x': 200, 'y': 100, 'width': 75, 'height': 75}},
        {'emotion': 'neutral', 'confidence': 0.68, 'face_coords': {'x': 150, 'y': 75, 'width': 85, 'height': 85}},
        {'emotion': 'angry', 'confidence': 0.91, 'face_coords': {'x': 120, 'y': 60, 'width': 90, 'height': 90}},
        {'emotion': 'surprise', 'confidence': 0.78, 'face_coords': {'x': 180, 'y': 90, 'width': 70, 'height': 70}},
    ]
    
    session_id = "test_session_001"
    
    for record in test_records:
        record_id = db.save_emotion_record(
            emotion=record['emotion'],
            confidence=record['confidence'],
            face_coords=record['face_coords'],
            session_id=session_id
        )
        print(f"✓ Saved record {record_id}: {record['emotion']} ({record['confidence']:.2f})")
    
    # Test retrieving recent emotions
    print("\nTesting recent emotions retrieval...")
    recent = db.get_recent_emotions(3)
    print(f"✓ Retrieved {len(recent)} recent records:")
    for record in recent:
        print(f"  - {record['emotion']} at {record['timestamp']} (confidence: {record['confidence']})")
    
    # Test emotion statistics
    print("\nTesting emotion statistics...")
    stats = db.get_emotion_statistics()
    print(f"✓ Retrieved statistics for {len(stats)} emotions:")
    for stat in stats:
        print(f"  - {stat['emotion']}: {stat['count']} times, avg confidence: {stat['avg_confidence']:.2f}")
    
    # Test emotions by date
    print("\nTesting emotions by date...")
    by_date = db.get_emotions_by_date(7)
    print(f"✓ Retrieved {len(by_date)} date-emotion combinations")
    
    # Test total count
    print("\nTesting total count...")
    total = db.get_total_records_count()
    print(f"✓ Total records in database: {total}")
    
    print("\n🎉 All database tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
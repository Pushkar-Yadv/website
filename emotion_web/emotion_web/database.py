import sqlite3
import os
from datetime import datetime
import base64

class EmotionDatabase:
    def __init__(self, db_path='emotion_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create emotion_records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotion_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emotion TEXT NOT NULL,
                confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                face_coordinates TEXT,
                face_image_base64 TEXT,
                session_id TEXT
            )
        ''')
        
        # Database schema is now clean without Ghibli references
        
        # Create emotion_summary table for aggregated data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotion_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                emotion TEXT,
                count INTEGER,
                avg_confidence REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_emotion_record(self, emotion, confidence=None, face_coords=None, face_image_base64=None, session_id=None):
        """Save an emotion detection record to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert face coordinates to string if provided
        face_coords_str = str(face_coords) if face_coords else None
        
        cursor.execute('''
            INSERT INTO emotion_records 
            (emotion, confidence, face_coordinates, face_image_base64, session_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (emotion, confidence, face_coords_str, face_image_base64, session_id))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_recent_emotions(self, limit=10):
        """Get recent emotion records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, emotion, confidence, timestamp, face_coordinates, session_id
            FROM emotion_records 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        records = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': record[0],
                'emotion': record[1],
                'confidence': record[2],
                'timestamp': record[3],
                'face_coordinates': record[4],
                'session_id': record[5]
            }
            for record in records
        ]
    
    def get_emotion_statistics(self, date_from=None, date_to=None):
        """Get emotion statistics for a date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT emotion, COUNT(*) as count, AVG(confidence) as avg_confidence
            FROM emotion_records 
        '''
        params = []
        
        if date_from or date_to:
            query += ' WHERE '
            conditions = []
            if date_from:
                conditions.append('DATE(timestamp) >= ?')
                params.append(date_from)
            if date_to:
                conditions.append('DATE(timestamp) <= ?')
                params.append(date_to)
            query += ' AND '.join(conditions)
        
        query += ' GROUP BY emotion ORDER BY count DESC'
        
        cursor.execute(query, params)
        records = cursor.fetchall()
        conn.close()
        
        return [
            {
                'emotion': record[0],
                'count': record[1],
                'avg_confidence': record[2]
            }
            for record in records
        ]
    
    def get_emotions_by_date(self, days=7):
        """Get emotion counts grouped by date for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DATE(timestamp) as date, emotion, COUNT(*) as count
            FROM emotion_records 
            WHERE timestamp >= datetime('now', '-{} days')
            GROUP BY DATE(timestamp), emotion
            ORDER BY date DESC, count DESC
        '''.format(days))
        
        records = cursor.fetchall()
        conn.close()
        
        return [
            {
                'date': record[0],
                'emotion': record[1],
                'count': record[2]
            }
            for record in records
        ]
    
    def get_total_records_count(self):
        """Get total number of emotion records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM emotion_records')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def delete_old_records(self, days_to_keep=30):
        """Delete records older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM emotion_records 
            WHERE timestamp < datetime('now', '-{} days')
        '''.format(days_to_keep))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    

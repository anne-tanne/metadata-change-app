import sqlite3
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create metadata learning table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metadata_learning (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        field_name TEXT NOT NULL,
                        field_value TEXT NOT NULL,
                        usage_count INTEGER DEFAULT 1,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create user preferences table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        preference_key TEXT UNIQUE NOT NULL,
                        preference_value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create recent folders table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS recent_folders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        folder_path TEXT UNIQUE NOT NULL,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        access_count INTEGER DEFAULT 1
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_field_name ON metadata_learning(field_name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_count ON metadata_learning(usage_count)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_used ON metadata_learning(last_used)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def save_metadata_value(self, field_name, field_value):
        """Save a metadata field value for learning"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if this field-value combination already exists
                cursor.execute('''
                    SELECT id, usage_count FROM metadata_learning 
                    WHERE field_name = ? AND field_value = ?
                ''', (field_name, field_value))
                
                result = cursor.fetchone()
                
                if result:
                    # Update existing record
                    record_id, current_count = result
                    cursor.execute('''
                        UPDATE metadata_learning 
                        SET usage_count = ?, last_used = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (current_count + 1, record_id))
                else:
                    # Insert new record
                    cursor.execute('''
                        INSERT INTO metadata_learning (field_name, field_value, usage_count)
                        VALUES (?, ?, 1)
                    ''', (field_name, field_value))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving metadata value: {str(e)}")
            return False
    
    def get_field_suggestions(self, field_name, limit=10):
        """Get suggestions for a specific field based on learning data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT field_value, usage_count, last_used
                    FROM metadata_learning 
                    WHERE field_name = ?
                    ORDER BY usage_count DESC, last_used DESC
                    LIMIT ?
                ''', (field_name, limit))
                
                results = cursor.fetchall()
                
                suggestions = []
                for field_value, usage_count, last_used in results:
                    suggestions.append({
                        'value': field_value,
                        'usage_count': usage_count,
                        'last_used': last_used
                    })
                
                return suggestions
                
        except Exception as e:
            logger.error(f"Error getting field suggestions: {str(e)}")
            return []
    
    def get_all_suggestions(self):
        """Get all learned metadata values grouped by field"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT field_name, field_value, usage_count, last_used
                    FROM metadata_learning 
                    ORDER BY field_name, usage_count DESC, last_used DESC
                ''')
                
                results = cursor.fetchall()
                
                suggestions = {}
                for field_name, field_value, usage_count, last_used in results:
                    if field_name not in suggestions:
                        suggestions[field_name] = []
                    
                    suggestions[field_name].append({
                        'value': field_value,
                        'usage_count': usage_count,
                        'last_used': last_used
                    })
                
                return suggestions
                
        except Exception as e:
            logger.error(f"Error getting all suggestions: {str(e)}")
            return {}
    
    def save_user_preference(self, key, value):
        """Save a user preference"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_preferences (preference_key, preference_value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, json.dumps(value) if isinstance(value, (dict, list)) else str(value)))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving user preference: {str(e)}")
            return False
    
    def get_user_preference(self, key, default=None):
        """Get a user preference"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT preference_value FROM user_preferences 
                    WHERE preference_key = ?
                ''', (key,))
                
                result = cursor.fetchone()
                
                if result:
                    try:
                        return json.loads(result[0])
                    except json.JSONDecodeError:
                        return result[0]
                else:
                    return default
                
        except Exception as e:
            logger.error(f"Error getting user preference: {str(e)}")
            return default
    
    def save_recent_folder(self, folder_path):
        """Save a recently accessed folder"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if folder already exists
                cursor.execute('''
                    SELECT id, access_count FROM recent_folders 
                    WHERE folder_path = ?
                ''', (folder_path,))
                
                result = cursor.fetchone()
                
                if result:
                    # Update existing record
                    record_id, current_count = result
                    cursor.execute('''
                        UPDATE recent_folders 
                        SET access_count = ?, last_accessed = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (current_count + 1, record_id))
                else:
                    # Insert new record
                    cursor.execute('''
                        INSERT INTO recent_folders (folder_path, access_count)
                        VALUES (?, 1)
                    ''', (folder_path,))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving recent folder: {str(e)}")
            return False
    
    def get_recent_folders(self, limit=10):
        """Get recently accessed folders"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT folder_path, access_count, last_accessed
                    FROM recent_folders 
                    ORDER BY last_accessed DESC
                    LIMIT ?
                ''', (limit,))
                
                results = cursor.fetchall()
                
                folders = []
                for folder_path, access_count, last_accessed in results:
                    folders.append({
                        'path': folder_path,
                        'access_count': access_count,
                        'last_accessed': last_accessed
                    })
                
                return folders
                
        except Exception as e:
            logger.error(f"Error getting recent folders: {str(e)}")
            return []
    
    def cleanup_old_data(self, days=30):
        """Clean up old learning data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM metadata_learning 
                    WHERE last_used < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old metadata learning records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")
            return 0 
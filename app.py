from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sqlite3
from pathlib import Path
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import logging

# Import our modules
from modules.metadata_handler import MetadataHandler
from modules.learning_engine import LearningEngine
from modules.file_processor import FileProcessor
from modules.database import Database

# Load configuration
def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / 'config.json'
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("config.json not found, using defaults")
        return {
            "backend": {
                "host": "0.0.0.0",
                "default_port": 5000,
                "debug": False,
                "max_file_size_mb": 16,
                "upload_folder": "uploads",
                "database_path": "data/metadata_editor.db"
            }
        }

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = load_config()

app = Flask(__name__)
CORS(app)

# Configuration from config.json
app.config['MAX_CONTENT_LENGTH'] = config['backend']['max_file_size_mb'] * 1024 * 1024
app.config['UPLOAD_FOLDER'] = config['backend']['upload_folder']
app.config['DATABASE_PATH'] = config['backend']['database_path']

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Initialize modules
db = Database(app.config['DATABASE_PATH'])
metadata_handler = MetadataHandler()
learning_engine = LearningEngine(db)
file_processor = FileProcessor()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/folder/scan', methods=['POST'])
def scan_folder():
    """Scan a folder for images and return their metadata"""
    try:
        data = request.get_json()
        folder_path = data.get('folder_path')
        
        logger.info(f"Received folder scan request for: {folder_path}")
        
        if not folder_path:
            logger.error("No folder path provided")
            return jsonify({'error': 'No folder path provided'}), 400
        
        if not os.path.exists(folder_path):
            logger.error(f"Folder path does not exist: {folder_path}")
            return jsonify({'error': f'Folder path does not exist: {folder_path}'}), 400
        
        if not os.path.isdir(folder_path):
            logger.error(f"Path is not a directory: {folder_path}")
            return jsonify({'error': f'Path is not a directory: {folder_path}'}), 400
        
        logger.info(f"Scanning folder: {folder_path}")
        
        # Scan for images
        images = file_processor.scan_folder(folder_path)
        
        logger.info(f"Found {len(images)} images in folder")
        
        # Get metadata for each image
        image_data = []
        for image_path in images:
            try:
                metadata = metadata_handler.get_metadata(image_path)
                image_data.append({
                    'path': image_path,
                    'filename': os.path.basename(image_path),
                    'metadata': metadata,
                    'size': os.path.getsize(image_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(image_path)).isoformat()
                })
            except Exception as e:
                logger.error(f"Error processing image {image_path}: {str(e)}")
                continue
        
        logger.info(f"Successfully processed {len(image_data)} images")
        
        return jsonify({
            'images': image_data,
            'total_count': len(image_data)
        })
    
    except Exception as e:
        logger.error(f"Error scanning folder: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metadata/<path:image_path>', methods=['GET'])
def get_metadata(image_path):
    """Get metadata for a specific image"""
    try:
        # Decode the path
        image_path = image_path.replace('|', '/')
        
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404
        
        metadata = metadata_handler.get_metadata(image_path)
        suggestions = learning_engine.get_suggestions(metadata)
        
        return jsonify({
            'metadata': metadata,
            'suggestions': suggestions
        })
    
    except Exception as e:
        logger.error(f"Error getting metadata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metadata/<path:image_path>', methods=['PUT'])
def update_metadata(image_path):
    """Update metadata for a specific image"""
    try:
        # Decode the path
        image_path = image_path.replace('|', '/')
        data = request.get_json()
        new_metadata = data.get('metadata', {})
        
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404
        
        # Update metadata
        success = metadata_handler.update_metadata(image_path, new_metadata)
        
        if success:
            # Learn from the new metadata
            learning_engine.learn_from_metadata(new_metadata)
            
            return jsonify({
                'success': True,
                'message': 'Metadata updated successfully'
            })
        else:
            return jsonify({'error': 'Failed to update metadata'}), 500
    
    except Exception as e:
        logger.error(f"Error updating metadata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch/update', methods=['POST'])
def batch_update():
    """Update metadata for multiple images"""
    try:
        data = request.get_json()
        updates = data.get('updates', [])
        
        results = []
        for update in updates:
            image_path = update['path']
            new_metadata = update['metadata']
            
            try:
                success = metadata_handler.update_metadata(image_path, new_metadata)
                if success:
                    learning_engine.learn_from_metadata(new_metadata)
                
                results.append({
                    'path': image_path,
                    'success': success,
                    'error': None if success else 'Failed to update'
                })
            except Exception as e:
                results.append({
                    'path': image_path,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'total': len(results),
            'successful': len([r for r in results if r['success']])
        })
    
    except Exception as e:
        logger.error(f"Error in batch update: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get learning suggestions for metadata fields"""
    try:
        field = request.args.get('field', '')
        suggestions = learning_engine.get_field_suggestions(field)
        
        return jsonify({
            'field': field,
            'suggestions': suggestions
        })
    
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export_metadata():
    """Export metadata to various formats"""
    try:
        data = request.get_json()
        image_paths = data.get('image_paths', [])
        format_type = data.get('format', 'json')
        
        metadata_list = []
        for image_path in image_paths:
            if os.path.exists(image_path):
                metadata = metadata_handler.get_metadata(image_path)
                metadata_list.append({
                    'path': image_path,
                    'filename': os.path.basename(image_path),
                    'metadata': metadata
                })
        
        if format_type == 'json':
            return jsonify({
                'format': 'json',
                'data': metadata_list,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Unsupported format'}), 400
    
    except Exception as e:
        logger.error(f"Error exporting metadata: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database
    db.init_database()
    
    # Start the application
    app.run(debug=False, host='0.0.0.0', port=5001) 
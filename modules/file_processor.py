import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
import mimetypes

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self):
        self.supported_extensions = {
            '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp', 
            '.gif', '.heic', '.heif', '.raw', '.cr2', '.nef', '.arw'
        }
        
        # Initialize mimetypes
        mimetypes.init()
    
    def scan_folder(self, folder_path: str) -> List[str]:
        """Scan a folder for image files"""
        try:
            if not os.path.exists(folder_path):
                raise FileNotFoundError(f"Folder not found: {folder_path}")
            
            if not os.path.isdir(folder_path):
                raise NotADirectoryError(f"Path is not a directory: {folder_path}")
            
            image_files = []
            
            # Walk through the directory
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if self._is_image_file(file_path):
                        image_files.append(file_path)
            
            # Sort files by name for consistent ordering
            image_files.sort()
            
            logger.info(f"Found {len(image_files)} image files in {folder_path}")
            return image_files
            
        except Exception as e:
            logger.error(f"Error scanning folder {folder_path}: {str(e)}")
            return []
    
    def _is_image_file(self, file_path: str) -> bool:
        """Check if a file is an image based on extension and mimetype"""
        try:
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext in self.supported_extensions:
                return True
            
            # Check mimetype as fallback
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and mime_type.startswith('image/'):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if file is image: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict:
        """Get detailed information about an image file"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat = os.stat(file_path)
            path_obj = Path(file_path)
            
            return {
                'path': file_path,
                'filename': path_obj.name,
                'basename': path_obj.stem,
                'extension': path_obj.suffix.lower(),
                'size': stat.st_size,
                'size_formatted': self._format_file_size(stat.st_size),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK),
                'mime_type': mimetypes.guess_type(file_path)[0]
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return {}
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        try:
            if size_bytes == 0:
                return "0 B"
            
            size_names = ["B", "KB", "MB", "GB", "TB"]
            import math
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            
            return f"{s} {size_names[i]}"
            
        except Exception as e:
            logger.error(f"Error formatting file size: {str(e)}")
            return str(size_bytes)
    
    def get_folder_stats(self, folder_path: str) -> Dict:
        """Get statistics about images in a folder"""
        try:
            image_files = self.scan_folder(folder_path)
            
            if not image_files:
                return {
                    'total_files': 0,
                    'total_size': 0,
                    'total_size_formatted': '0 B',
                    'extensions': {},
                    'largest_file': None,
                    'smallest_file': None
                }
            
            # Calculate statistics
            total_size = 0
            extensions = {}
            file_sizes = []
            
            for file_path in image_files:
                file_info = self.get_file_info(file_path)
                file_size = file_info.get('size', 0)
                extension = file_info.get('extension', 'unknown')
                
                total_size += file_size
                file_sizes.append((file_path, file_size))
                extensions[extension] = extensions.get(extension, 0) + 1
            
            # Find largest and smallest files
            file_sizes.sort(key=lambda x: x[1])
            smallest_file = file_sizes[0][0] if file_sizes else None
            largest_file = file_sizes[-1][0] if file_sizes else None
            
            return {
                'total_files': len(image_files),
                'total_size': total_size,
                'total_size_formatted': self._format_file_size(total_size),
                'extensions': extensions,
                'largest_file': largest_file,
                'smallest_file': smallest_file,
                'average_size': total_size / len(image_files) if image_files else 0,
                'average_size_formatted': self._format_file_size(total_size / len(image_files)) if image_files else '0 B'
            }
            
        except Exception as e:
            logger.error(f"Error getting folder stats for {folder_path}: {str(e)}")
            return {}
    
    def validate_file_path(self, file_path: str) -> Dict:
        """Validate if a file path is accessible and is an image"""
        try:
            result = {
                'valid': False,
                'exists': False,
                'is_file': False,
                'is_image': False,
                'readable': False,
                'writable': False,
                'errors': []
            }
            
            # Check if file exists
            if not os.path.exists(file_path):
                result['errors'].append("File does not exist")
                return result
            
            result['exists'] = True
            
            # Check if it's a file
            if not os.path.isfile(file_path):
                result['errors'].append("Path is not a file")
                return result
            
            result['is_file'] = True
            
            # Check if it's an image
            if not self._is_image_file(file_path):
                result['errors'].append("File is not a supported image format")
                return result
            
            result['is_image'] = True
            
            # Check permissions
            if not os.access(file_path, os.R_OK):
                result['errors'].append("File is not readable")
            else:
                result['readable'] = True
            
            if not os.access(file_path, os.W_OK):
                result['errors'].append("File is not writable")
            else:
                result['writable'] = True
            
            # If no errors, file is valid
            if not result['errors']:
                result['valid'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating file path {file_path}: {str(e)}")
            return {
                'valid': False,
                'exists': False,
                'is_file': False,
                'is_image': False,
                'readable': False,
                'writable': False,
                'errors': [str(e)]
            }
    
    def get_recent_folders(self, limit: int = 10) -> List[Dict]:
        """Get list of recently accessed folders (placeholder for database integration)"""
        try:
            # This would typically query the database for recent folders
            # For now, return an empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting recent folders: {str(e)}")
            return []
    
    def create_backup(self, file_path: str, backup_dir: str = None) -> Optional[str]:
        """Create a backup of an image file before modification"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Create backup directory if not provided
            if backup_dir is None:
                backup_dir = os.path.join(os.path.dirname(file_path), '.backup')
            
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup filename
            original_name = os.path.basename(file_path)
            timestamp = int(os.path.getmtime(file_path))
            backup_name = f"{os.path.splitext(original_name)[0]}_{timestamp}{os.path.splitext(original_name)[1]}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # Copy file
            import shutil
            shutil.copy2(file_path, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup for {file_path}: {str(e)}")
            return None
    
    def cleanup_backups(self, backup_dir: str, max_age_days: int = 30) -> int:
        """Clean up old backup files"""
        try:
            if not os.path.exists(backup_dir):
                return 0
            
            import time
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            deleted_count = 0
            
            for filename in os.listdir(backup_dir):
                file_path = os.path.join(backup_dir, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old backup files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up backups: {str(e)}")
            return 0 
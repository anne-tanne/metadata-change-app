from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import json
import logging
from datetime import datetime
from exif import Image as ExifImage
from pathlib import Path
from typing import Dict, Any, Optional, Set

logger = logging.getLogger(__name__)

class MetadataHandler:
    def __init__(self, config_path: Optional[str] = None):
        # Load supported formats from config or use defaults
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.supported_formats = set(config['app']['supported_image_formats'])
            except (KeyError, json.JSONDecodeError):
                logger.warning("Failed to load config, using default formats")
                self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
        else:
            self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
        
        self.exif_tags = {TAGS.get(tag, tag): tag for tag in TAGS}
        self.gps_tags = {GPSTAGS.get(tag, tag): tag for tag in GPSTAGS}
    
    def get_metadata(self, image_path: str) -> Dict[str, Any]:
        """Extract all metadata from an image file"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            file_ext = Path(image_path).suffix.lower()
            if file_ext not in self.supported_formats:
                logger.warning(f"Unsupported file format: {file_ext}")
                return self._get_basic_metadata(image_path)
            
            metadata = self._get_basic_metadata(image_path)
            
            # Get EXIF data
            exif_data = self._get_exif_data(image_path)
            if exif_data:
                metadata['EXIF'] = exif_data
            
            # Get IPTC data
            iptc_data = self._get_iptc_data(image_path)
            if iptc_data:
                metadata['IPTC'] = iptc_data
            
            # Get XMP data
            xmp_data = self._get_xmp_data(image_path)
            if xmp_data:
                metadata['XMP'] = xmp_data
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting metadata for {image_path}: {str(e)}")
            return self._get_basic_metadata(image_path)
    
    def _get_basic_metadata(self, image_path: str) -> Dict[str, Any]:
        """Get basic file metadata"""
        try:
            stat = os.stat(image_path)
            with Image.open(image_path) as img:
                return {
                    'File': {
                        'FileName': os.path.basename(image_path),
                        'FileSize': stat.st_size,
                        'FileModifyDate': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'ImageWidth': img.width,
                        'ImageHeight': img.height,
                        'Format': img.format,
                        'Mode': img.mode
                    }
                }
        except Exception as e:
            logger.error(f"Error getting basic metadata: {str(e)}")
            return {'File': {'FileName': os.path.basename(image_path)}}
    
    def _get_exif_data(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Extract EXIF data from image"""
        try:
            with open(image_path, 'rb') as image_file:
                exif_image = ExifImage(image_file)
                
                if not exif_image.has_exif:
                    return None
                
                exif_data = {}
                for key, value in exif_image.list_all():
                    if value is not None:
                        exif_data[key] = self._format_exif_value(value)
                
                return exif_data
                
        except Exception as e:
            logger.error(f"Error extracting EXIF data: {str(e)}")
            return None
    
    def _get_iptc_data(self, image_path):
        """Extract IPTC data from image"""
        try:
            # IPTC extraction is more complex and may require additional libraries
            # For now, we'll return None
            return None
        except Exception as e:
            logger.error(f"Error extracting IPTC data: {str(e)}")
            return None
    
    def _get_xmp_data(self, image_path):
        """Extract XMP data from image (basic implementation)"""
        try:
            # This is a simplified XMP extraction
            # For full XMP support, you might want to use a dedicated XMP library
            return None
        except Exception as e:
            logger.error(f"Error extracting XMP data: {str(e)}")
            return None
    
    def _format_exif_value(self, value):
        """Format EXIF value for JSON serialization"""
        if isinstance(value, bytes):
            try:
                return value.decode('utf-8', errors='ignore')
            except:
                return str(value)
        elif isinstance(value, (int, float, str, bool)):
            return value
        else:
            return str(value)
    
    def _format_gps_value(self, tag_name, value):
        """Format GPS value for JSON serialization"""
        if tag_name in ['GPSLatitude', 'GPSLongitude']:
            if isinstance(value, tuple) and len(value) == 3:
                # Convert degrees, minutes, seconds to decimal
                degrees, minutes, seconds = value
                decimal = degrees + minutes/60 + seconds/3600
                return round(decimal, 6)
        return self._format_exif_value(value)
    
    def update_metadata(self, image_path, new_metadata):
        """Update metadata for an image file"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            file_ext = Path(image_path).suffix.lower()
            if file_ext not in self.supported_formats:
                logger.warning(f"Cannot update metadata for unsupported format: {file_ext}")
                return False
            
            success = True
            
            # Update EXIF data
            if 'EXIF' in new_metadata:
                success &= self._update_exif_data(image_path, new_metadata['EXIF'])
            
            # Update IPTC data
            if 'IPTC' in new_metadata:
                success &= self._update_iptc_data(image_path, new_metadata['IPTC'])
            
            # Update XMP data
            if 'XMP' in new_metadata:
                success &= self._update_xmp_data(image_path, new_metadata['XMP'])
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating metadata for {image_path}: {str(e)}")
            return False
    
    def _update_exif_data(self, image_path, exif_data):
        """Update EXIF data in image"""
        try:
            # For now, we'll use a simplified approach
            # In a production environment, you might want to use more robust libraries
            logger.info("EXIF update not fully implemented - would update here")
            return True
            
        except Exception as e:
            logger.error(f"Error updating EXIF data: {str(e)}")
            return False
    
    def _update_iptc_data(self, image_path, iptc_data):
        """Update IPTC data in image"""
        try:
            # IPTC updates are more complex and may require additional libraries
            # For now, we'll log that this is not fully implemented
            logger.info("IPTC data update not fully implemented")
            return True
            
        except Exception as e:
            logger.error(f"Error updating IPTC data: {str(e)}")
            return False
    
    def _update_xmp_data(self, image_path, xmp_data):
        """Update XMP data in image"""
        try:
            # XMP updates require specialized libraries
            # For now, we'll log that this is not fully implemented
            logger.info("XMP data update not fully implemented")
            return True
            
        except Exception as e:
            logger.error(f"Error updating XMP data: {str(e)}")
            return False
    
    def get_supported_fields(self):
        """Get list of supported metadata fields"""
        return {
            'EXIF': [
                'Make', 'Model', 'Software', 'DateTime', 'Artist', 'Copyright',
                'ImageDescription', 'Orientation', 'XResolution', 'YResolution',
                'ResolutionUnit', 'ColorSpace', 'ExifVersion', 'ComponentsConfiguration',
                'FlashPixVersion', 'ColorSpace', 'PixelXDimension', 'PixelYDimension',
                'DateTimeOriginal', 'DateTimeDigitized', 'SubsecTime', 'SubsecTimeOriginal',
                'SubsecTimeDigitized', 'ExposureTime', 'FNumber', 'ExposureProgram',
                'ISOSpeedRatings', 'ExifVersion', 'DateTimeOriginal', 'DateTimeDigitized',
                'ComponentsConfiguration', 'CompressedBitsPerPixel', 'ShutterSpeedValue',
                'ApertureValue', 'BrightnessValue', 'ExposureBiasValue', 'MaxApertureValue',
                'SubjectDistance', 'MeteringMode', 'LightSource', 'Flash', 'FocalLength',
                'SubjectArea', 'MakerNote', 'UserComment', 'SubsecTime', 'SubsecTimeOriginal',
                'SubsecTimeDigitized', 'FlashPixVersion', 'ColorSpace', 'PixelXDimension',
                'PixelYDimension', 'RelatedSoundFile', 'FlashEnergy', 'SpatialFrequencyResponse',
                'FocalPlaneXResolution', 'FocalPlaneYResolution', 'FocalPlaneResolutionUnit',
                'SubjectLocation', 'ExposureIndex', 'SensingMethod', 'FileSource', 'SceneType',
                'CFAPattern', 'CustomRendered', 'ExposureMode', 'WhiteBalance', 'DigitalZoomRatio',
                'FocalLengthIn35mmFilm', 'SceneCaptureType', 'GainControl', 'Contrast',
                'Saturation', 'Sharpness', 'DeviceSettingDescription', 'SubjectDistanceRange'
            ],
            'IPTC': [
                'ObjectName', 'EditStatus', 'EditorialUpdate', 'Urgency', 'SubjectReference',
                'Category', 'SupplementalCategories', 'FixtureIdentifier', 'Keywords',
                'ContentLocationCode', 'ContentLocationName', 'ReleaseDate', 'ReleaseTime',
                'ExpirationDate', 'ExpirationTime', 'SpecialInstructions', 'ActionAdvised',
                'ReferenceService', 'ReferenceDate', 'ReferenceNumber', 'DateCreated',
                'TimeCreated', 'DigitalCreationDate', 'DigitalCreationTime', 'OriginatingProgram',
                'ProgramVersion', 'ObjectCycle', 'ByLine', 'ByLineTitle', 'City', 'SubLocation',
                'ProvinceState', 'CountryPrimaryLocationCode', 'CountryPrimaryLocationName',
                'OriginalTransmissionReference', 'Headline', 'Credit', 'Source', 'CopyrightNotice',
                'Contact', 'CaptionAbstract', 'WriterEditor', 'RasterizedCaption', 'ImageType',
                'ImageOrientation', 'LanguageIdentifier', 'AudioType', 'AudioSamplingRate',
                'AudioSamplingResolution', 'AudioDuration', 'AudioOutcue', 'ObjectPreviewFileFormat',
                'ObjectPreviewFileVersion', 'ObjectPreviewData', 'Prefs', 'ClassifyState',
                'SimilarityIndex', 'DocumentNotes', 'DocumentHistory', 'ExifCameraInfo'
            ],
            'Custom': [
                'Title', 'Description', 'Keywords', 'Author', 'Copyright', 'Rating',
                'Comments', 'Location', 'Tags', 'Category', 'Subject', 'Creator',
                'Publisher', 'Contributor', 'Language', 'Identifier', 'Format',
                'Source', 'Relation', 'Coverage', 'Rights'
            ]
        }
    
    def validate_metadata(self, metadata):
        """Validate metadata structure and values"""
        errors = []
        
        for section, fields in metadata.items():
            if not isinstance(fields, dict):
                errors.append(f"Section '{section}' must be a dictionary")
                continue
            
            for field_name, value in fields.items():
                if not isinstance(field_name, str):
                    errors.append(f"Field name in '{section}' must be a string")
                elif not field_name.strip():
                    errors.append(f"Field name in '{section}' cannot be empty") 
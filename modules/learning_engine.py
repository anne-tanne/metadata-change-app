import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class LearningEngine:
    def __init__(self, database):
        self.db = database
        self.field_patterns = defaultdict(list)
        self.user_preferences = {}
    
    def learn_from_metadata(self, metadata):
        """Learn from metadata updates to improve future suggestions"""
        try:
            for section, fields in metadata.items():
                if not isinstance(fields, dict):
                    continue
                
                for field_name, field_value in fields.items():
                    if field_value and str(field_value).strip():
                        # Save to database for learning
                        self.db.save_metadata_value(field_name, str(field_value))
                        
                        # Update field patterns
                        self._update_field_patterns(field_name, field_value)
            
            logger.info("Successfully learned from metadata")
            return True
            
        except Exception as e:
            logger.error(f"Error learning from metadata: {str(e)}")
            return False
    
    def _update_field_patterns(self, field_name, field_value):
        """Update patterns for field values to improve suggestions"""
        try:
            value_str = str(field_value).lower().strip()
            
            # Extract common patterns
            patterns = []
            
            # Check for email patterns
            if '@' in value_str and '.' in value_str:
                patterns.append('email')
            
            # Check for date patterns
            if any(char.isdigit() for char in value_str):
                if len(value_str) >= 8:  # Potential date
                    patterns.append('date')
            
            # Check for location patterns
            location_keywords = ['street', 'avenue', 'road', 'lane', 'city', 'country', 'state']
            if any(keyword in value_str for keyword in location_keywords):
                patterns.append('location')
            
            # Check for name patterns
            name_keywords = ['mr', 'mrs', 'ms', 'dr', 'prof']
            if any(keyword in value_str for keyword in name_keywords):
                patterns.append('name')
            
            # Store patterns
            for pattern in patterns:
                self.field_patterns[field_name].append(pattern)
            
        except Exception as e:
            logger.error(f"Error updating field patterns: {str(e)}")
    
    def get_suggestions(self, current_metadata):
        """Get smart suggestions based on current metadata and learning data"""
        try:
            suggestions = {}
            
            # Get suggestions for each field that has a value
            for section, fields in current_metadata.items():
                if not isinstance(fields, dict):
                    continue
                
                for field_name, field_value in fields.items():
                    if field_value and str(field_value).strip():
                        field_suggestions = self.db.get_field_suggestions(field_name, limit=5)
                        if field_suggestions:
                            suggestions[field_name] = field_suggestions
            
            # Add contextual suggestions based on patterns
            contextual_suggestions = self._get_contextual_suggestions(current_metadata)
            suggestions.update(contextual_suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return {}
    
    def _get_contextual_suggestions(self, current_metadata):
        """Get contextual suggestions based on current metadata patterns"""
        try:
            contextual_suggestions = {}
            
            # Analyze current metadata for patterns
            patterns = self._analyze_metadata_patterns(current_metadata)
            
            # Suggest related fields based on patterns
            for pattern, fields in patterns.items():
                if pattern == 'camera_info':
                    # If we have camera info, suggest related fields
                    if 'Make' in fields and 'Model' not in current_metadata.get('EXIF', {}):
                        suggestions = self.db.get_field_suggestions('Model', limit=3)
                        if suggestions:
                            contextual_suggestions['Model'] = suggestions
                
                elif pattern == 'location_info':
                    # If we have location info, suggest related fields
                    if 'GPSLatitude' in fields and 'GPSLongitude' in fields:
                        suggestions = self.db.get_field_suggestions('Location', limit=3)
                        if suggestions:
                            contextual_suggestions['Location'] = suggestions
                
                elif pattern == 'author_info':
                    # If we have author info, suggest related fields
                    if 'Artist' in fields and 'Copyright' not in current_metadata.get('EXIF', {}):
                        suggestions = self.db.get_field_suggestions('Copyright', limit=3)
                        if suggestions:
                            contextual_suggestions['Copyright'] = suggestions
            
            return contextual_suggestions
            
        except Exception as e:
            logger.error(f"Error getting contextual suggestions: {str(e)}")
            return {}
    
    def _analyze_metadata_patterns(self, metadata):
        """Analyze metadata for common patterns"""
        try:
            patterns = defaultdict(list)
            
            for section, fields in metadata.items():
                if not isinstance(fields, dict):
                    continue
                
                for field_name, field_value in fields.items():
                    if not field_value:
                        continue
                    
                    # Camera information pattern
                    if field_name in ['Make', 'Model', 'Software', 'ExposureTime', 'FNumber']:
                        patterns['camera_info'].append(field_name)
                    
                    # Location information pattern
                    if field_name in ['GPSLatitude', 'GPSLongitude', 'GPSAltitude']:
                        patterns['location_info'].append(field_name)
                    
                    # Author information pattern
                    if field_name in ['Artist', 'Copyright', 'ByLine']:
                        patterns['author_info'].append(field_name)
                    
                    # Date information pattern
                    if 'Date' in field_name or 'Time' in field_name:
                        patterns['date_info'].append(field_name)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing metadata patterns: {str(e)}")
            return {}
    
    def get_field_suggestions(self, field_name, limit=10):
        """Get suggestions for a specific field"""
        try:
            return self.db.get_field_suggestions(field_name, limit)
        except Exception as e:
            logger.error(f"Error getting field suggestions: {str(e)}")
            return []
    
    def get_popular_values(self, limit=20):
        """Get most popular metadata values across all fields"""
        try:
            all_suggestions = self.db.get_all_suggestions()
            
            # Flatten and sort by usage count
            all_values = []
            for field_name, suggestions in all_suggestions.items():
                for suggestion in suggestions:
                    all_values.append({
                        'field': field_name,
                        'value': suggestion['value'],
                        'usage_count': suggestion['usage_count'],
                        'last_used': suggestion['last_used']
                    })
            
            # Sort by usage count and recency
            all_values.sort(key=lambda x: (x['usage_count'], x['last_used']), reverse=True)
            
            return all_values[:limit]
            
        except Exception as e:
            logger.error(f"Error getting popular values: {str(e)}")
            return []
    
    def get_recent_values(self, days=7, limit=20):
        """Get recently used metadata values"""
        try:
            all_suggestions = self.db.get_all_suggestions()
            
            # Filter by recent usage
            recent_values = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for field_name, suggestions in all_suggestions.items():
                for suggestion in suggestions:
                    try:
                        last_used = datetime.fromisoformat(suggestion['last_used'].replace('Z', '+00:00'))
                        if last_used >= cutoff_date:
                            recent_values.append({
                                'field': field_name,
                                'value': suggestion['value'],
                                'usage_count': suggestion['usage_count'],
                                'last_used': suggestion['last_used']
                            })
                    except:
                        continue
            
            # Sort by recency
            recent_values.sort(key=lambda x: x['last_used'], reverse=True)
            
            return recent_values[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent values: {str(e)}")
            return []
    
    def get_field_recommendations(self, current_metadata):
        """Get field recommendations based on current metadata"""
        try:
            recommendations = []
            
            # Check for missing common fields
            common_fields = {
                'EXIF': ['Artist', 'Copyright', 'ImageDescription'],
                'Custom': ['Title', 'Description', 'Keywords', 'Author']
            }
            
            for section, fields in common_fields.items():
                current_section = current_metadata.get(section, {})
                for field in fields:
                    if field not in current_section or not current_section[field]:
                        recommendations.append({
                            'section': section,
                            'field': field,
                            'priority': 'high' if field in ['Artist', 'Copyright'] else 'medium',
                            'reason': f'Missing {field} information'
                        })
            
            # Check for incomplete camera information
            exif_data = current_metadata.get('EXIF', {})
            if 'Make' in exif_data and not exif_data['Make']:
                recommendations.append({
                    'section': 'EXIF',
                    'field': 'Model',
                    'priority': 'medium',
                    'reason': 'Camera model information is incomplete'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting field recommendations: {str(e)}")
            return []
    
    def save_user_preference(self, key, value):
        """Save user preference for learning"""
        try:
            self.user_preferences[key] = value
            return self.db.save_user_preference(key, value)
        except Exception as e:
            logger.error(f"Error saving user preference: {str(e)}")
            return False
    
    def get_user_preference(self, key, default=None):
        """Get user preference"""
        try:
            if key in self.user_preferences:
                return self.user_preferences[key]
            
            value = self.db.get_user_preference(key, default)
            if value is not None:
                self.user_preferences[key] = value
            
            return value
        except Exception as e:
            logger.error(f"Error getting user preference: {str(e)}")
            return default 
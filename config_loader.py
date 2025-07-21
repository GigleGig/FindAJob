import json
import os
from typing import Dict, Any

class ConfigLoader:
    def __init__(self):
        self.user_config_path = 'user_config.json'
        self.user_config = self.load_user_config()
    
    def load_user_config(self) -> Dict[str, Any]:
        """Load user configuration from JSON file"""
        if not os.path.exists(self.user_config_path):
            raise FileNotFoundError(f"User config file not found: {self.user_config_path}")
        
        try:
            with open(self.user_config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
                print("User configuration loaded successfully")
                return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in user config file: {e}")
        except Exception as e:
            raise Exception(f"Error loading user config: {e}")
    
    def get_personal_info(self) -> Dict[str, str]:
        """Get personal information for job applications"""
        return self.user_config.get('personal_info', {})
    
    def get_preferred_locations(self) -> list:
        """Get preferred job locations"""
        return self.user_config.get('preferred_locations', [])
    
    def get_job_preferences(self) -> Dict[str, Any]:
        """Get job search preferences"""
        return self.user_config.get('job_preferences', {})
    
    def get_application_settings(self) -> Dict[str, Any]:
        """Get application automation settings"""
        return self.user_config.get('application_settings', {})
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present"""
        required_fields = {
            'personal_info': ['phone', 'email'],
            'preferred_locations': [],
        }
        
        missing_fields = []
        
        for section, fields in required_fields.items():
            if section not in self.user_config:
                missing_fields.append(section)
                continue
            
            if isinstance(fields, list) and fields:  # Check required fields in section
                for field in fields:
                    if field not in self.user_config[section] or not self.user_config[section][field]:
                        missing_fields.append(f"{section}.{field}")
        
        if missing_fields:
            print(f"Missing required configuration: {', '.join(missing_fields)}")
            return False
        
        if not self.get_preferred_locations():
            print("Warning: No preferred locations specified")
            return False
        
        return True
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration file with new values"""
        try:
            # Deep merge updates into existing config
            def deep_merge(base_dict, update_dict):
                for key, value in update_dict.items():
                    if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                        deep_merge(base_dict[key], value)
                    else:
                        base_dict[key] = value
            
            deep_merge(self.user_config, updates)
            
            # Save updated config
            with open(self.user_config_path, 'w', encoding='utf-8') as file:
                json.dump(self.user_config, file, indent=2, ensure_ascii=False)
            
            print("Configuration updated successfully")
            return True
            
        except Exception as e:
            print(f"Error updating configuration: {e}")
            return False
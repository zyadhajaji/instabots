"""
Configuration management for Instagram Bot
"""

import json
import os
from typing import Dict, List, Any


class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        default_config = {
            "message_templates": [
                {
                    "name": "Default Welcome",
                    "message": "Hi! Thanks for following. How can I help you today?"
                }
            ],
            "safety_settings": {
                "min_delay_seconds": 5,
                "max_delay_seconds": 10,
                "daily_message_limit": 50,
                "hourly_message_limit": 10
            },
            "bot_settings": {
                "headless": False,
                "save_session": True,
                "auto_connect": False,
                "debug_port": 9222,
                "connected_account": None
            },
            "contact_lists": {},
            "sent_messages_log": [],
            "collected_followers": {},
            "auto_followers_list": "All Followers"  # Default name for auto-populated list
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_config.update(loaded)
                    return default_config
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        config_to_save = config or self.config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_template(self, name: str) -> str:
        """Get message template by name"""
        for template in self.config.get('message_templates', []):
            if template.get('name') == name:
                return template.get('message', '')
        return ''
    
    def add_template(self, name: str, message: str):
        """Add a new message template"""
        if 'message_templates' not in self.config:
            self.config['message_templates'] = []
        
        # Check if template exists
        for template in self.config['message_templates']:
            if template.get('name') == name:
                template['message'] = message
                self.save_config()
                return
        
        # Add new template
        self.config['message_templates'].append({
            'name': name,
            'message': message
        })
        self.save_config()
    
    def delete_template(self, name: str):
        """Delete a message template"""
        self.config['message_templates'] = [
            t for t in self.config.get('message_templates', [])
            if t.get('name') != name
        ]
        self.save_config()
    
    def get_templates(self) -> List[Dict]:
        """Get all message templates"""
        return self.config.get('message_templates', [])
    
    def save_contact_list(self, name: str, usernames: List[str]):
        """Save a contact list"""
        if 'contact_lists' not in self.config:
            self.config['contact_lists'] = {}
        
        self.config['contact_lists'][name] = usernames
        self.save_config()
    
    def get_contact_list(self, name: str) -> List[str]:
        """Get a contact list by name"""
        return self.config.get('contact_lists', {}).get(name, [])
    
    def get_contact_lists(self) -> Dict[str, List[str]]:
        """Get all contact lists"""
        return self.config.get('contact_lists', {})
    
    def delete_contact_list(self, name: str):
        """Delete a contact list"""
        if 'contact_lists' in self.config:
            self.config['contact_lists'].pop(name, None)
            self.save_config()
    
    def log_message(self, username: str, message: str, status: str):
        """Log a sent message"""
        if 'sent_messages_log' not in self.config:
            self.config['sent_messages_log'] = []
        
        from datetime import datetime
        log_entry = {
            'username': username,
            'message': message,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        self.config['sent_messages_log'].append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.config['sent_messages_log']) > 1000:
            self.config['sent_messages_log'] = self.config['sent_messages_log'][-1000:]
        
        self.save_config()
    
    def get_safety_settings(self) -> Dict:
        """Get safety settings"""
        return self.config.get('safety_settings', {})
    
    def update_safety_settings(self, settings: Dict):
        """Update safety settings"""
        self.config['safety_settings'].update(settings)
        self.save_config()
    
    def get_bot_settings(self) -> Dict:
        """Get bot settings"""
        return self.config.get('bot_settings', {})
    
    def save_browser_connection(self, debug_port=9222, account_username=None, auto_connect=True):
        """Save browser connection settings"""
        if 'bot_settings' not in self.config:
            self.config['bot_settings'] = {}
        self.config['bot_settings']['debug_port'] = debug_port
        self.config['bot_settings']['auto_connect'] = auto_connect
        if account_username:
            self.config['bot_settings']['connected_account'] = account_username
        self.save_config()
    
    def get_browser_connection(self) -> Dict:
        """Get saved browser connection settings"""
        settings = self.config.get('bot_settings', {})
        return {
            'auto_connect': settings.get('auto_connect', False),
            'debug_port': settings.get('debug_port', 9222),
            'connected_account': settings.get('connected_account', None)
        }
    
    def save_auto_followers(self, account_username: str, followers: List[str]):
        """Save all followers for an account (auto-populated list)"""
        list_name = self.config.get('auto_followers_list', 'All Followers')
        self.save_contact_list(f"{list_name} ({account_username})", followers)
        
        # Also save to collected_followers for tracking
        if 'collected_followers' not in self.config:
            self.config['collected_followers'] = {}
        self.config['collected_followers'][account_username] = followers
        self.save_config()
    
    def get_auto_followers(self, account_username: str) -> List[str]:
        """Get auto-populated followers list for an account"""
        list_name = self.config.get('auto_followers_list', 'All Followers')
        return self.get_contact_list(f"{list_name} ({account_username})")
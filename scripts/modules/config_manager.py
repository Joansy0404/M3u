#!/usr/bin/env python3
"""
Configuration Manager Module
Handles loading and managing configuration settings
"""

import os
import json
import logging
from typing import List, Dict, Any


class ConfigManager:
    """Manages configuration settings for M3U Editor"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self.logger = logging.getLogger(__name__)
        self._config = {}
        self._load_default_config()
    
    def _load_default_config(self):
        """Load default configuration values"""
        self._config = {
            'providers': [],
            'epg_sources': [],
            'commands': [],
            'processing': {
                'max_concurrent_downloads': 5,
                'request_timeout': 30,
                'validate_streams': False,
                'remove_duplicates': True,
                'auto_group': True
            },
            'output': {
                'formats': ['m3u', 'json'],
                'group_separate_files': False,
                'include_logos': True,
                'include_epg': True
            },
            'filters': {
                'allowed_groups': [],
                'blocked_groups': [],
                'min_channels_per_group': 1
            }
        }
    
    def load_providers(self) -> List[str]:
        """Load M3U provider URLs from config file"""
        providers_file = os.path.join(self.config_dir, "providers.txt")
        providers = []
        
        try:
            with open(providers_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and line.startswith('http'):
                        providers.append(line)
            
            self.logger.info(f"Loaded {len(providers)} provider URLs")
            self._config['providers'] = providers
            
        except FileNotFoundError:
            self.logger.warning(f"Providers file not found: {providers_file}")
        except Exception as e:
            self.logger.error(f"Error loading providers: {e}")
        
        return providers
    
    def load_epg_sources(self) -> List[str]:
        """Load EPG source URLs from config file"""
        epg_file = os.path.join(self.config_dir, "epg_sources.txt")
        epg_sources = []
        
        try:
            with open(epg_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and line.startswith('http'):
                        epg_sources.append(line)
            
            self.logger.info(f"Loaded {len(epg_sources)} EPG sources")
            self._config['epg_sources'] = epg_sources
            
        except FileNotFoundError:
            self.logger.warning(f"EPG sources file not found: {epg_file}")
        except Exception as e:
            self.logger.error(f"Error loading EPG sources: {e}")
        
        return epg_sources
    
    def load_commands(self) -> List[str]:
        """Load processing commands from config file"""
        commands_file = os.path.join(self.config_dir, "commands.txt")
        commands = []
        
        try:
            with open(commands_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip().upper()
                    if line and not line.startswith('#'):
                        commands.append(line)
            
            self.logger.info(f"Loaded {len(commands)} processing commands")
            self._config['commands'] = commands
            
        except FileNotFoundError:
            self.logger.warning(f"Commands file not found: {commands_file}")
        except Exception as e:
            self.logger.error(f"Error loading commands: {e}")
        
        return commands
    
    def load_custom_mappings(self, mapping_type: str) -> Dict[str, str]:
        """Load custom mappings from file"""
        mapping_file = os.path.join(self.config_dir, f"{mapping_type}_mapping.txt")
        mappings = {}
        
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        mappings[key.strip()] = value.strip()
            
            self.logger.info(f"Loaded {len(mappings)} {mapping_type} mappings")
            
        except FileNotFoundError:
            self.logger.debug(f"Custom mappings file not found: {mapping_file}")
        except Exception as e:
            self.logger.error(f"Error loading {mapping_type} mappings: {e}")
        
        return mappings
    
    def save_config_json(self, filepath="config/settings.json"):
        """Save current configuration to JSON file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def load_config_json(self, filepath="config/settings.json"):
        """Load configuration from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # Update current config with loaded values
            self._config.update(loaded_config)
            self.logger.info(f"Configuration loaded from {filepath}")
            
        except FileNotFoundError:
            self.logger.debug(f"Config file not found: {filepath}")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
    
    def get_config(self, key: str = None):
        """Get configuration value or entire config"""
        if key:
            return self._config.get(key)
        return self._config
    
    def set_config(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing-specific configuration"""
        return self._config.get('processing', {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output-specific configuration"""
        return self._config.get('output', {})
    
    def get_filter_config(self) -> Dict[str, Any]:
        """Get filter-specific configuration"""
        return self._config.get('filters', {})
    
    def validate_config(self) -> bool:
        """Validate current configuration"""
        try:
            # Check required directories exist
            if not os.path.exists(self.config_dir):
                self.logger.error(f"Config directory not found: {self.config_dir}")
                return False
            
            # Validate provider URLs
            providers = self.load_providers()
            if not providers:
                self.logger.warning("No provider URLs configured")
            
            # Validate commands
            commands = self.load_commands()
            valid_commands = ['IMPORT', 'GROUP_BY_COUNTRY', 'APPLY_EPG', 'APPLY_LOGOS', 'EXPORT']
            for cmd in commands:
                if cmd not in valid_commands:
                    self.logger.warning(f"Unknown command: {cmd}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False

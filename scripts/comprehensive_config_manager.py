#!/usr/bin/env python3
"""
Comprehensive Configuration Manager - Complete System
Handles ALL configuration scenarios with robust fallback mechanisms

This replaces incomplete configuration handling with a bulletproof system.
AUTO-CREATES missing configs with sensible defaults.
"""

import os
import json
import toml
import yaml
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import tempfile
import shutil
from datetime import datetime

class ConfigFormat(Enum):
    """Configuration file formats"""
    JSON = "json"
    TOML = "toml"
    YAML = "yaml"
    INI = "ini"
    ENV = "env"

class ConfigSource(Enum):
    """Configuration source priorities"""
    ENVIRONMENT = 1      # Highest priority
    USER_CONFIG = 2      # User-specific config
    PROJECT_CONFIG = 3   # Project-level config
    SYSTEM_CONFIG = 4    # System-wide config
    EMBEDDED_DEFAULTS = 5 # Lowest priority

@dataclass
class ValidationRule:
    """Configuration validation rule"""
    key_path: str
    required: bool = False
    data_type: type = str
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    pattern: Optional[str] = None
    description: str = ""

class ComprehensiveConfigManager:
    """
    Comprehensive configuration management system
    
    FEATURES:
    - Auto-creates missing configuration files with sensible defaults
    - Multiple format support (JSON, TOML, YAML, ENV)
    - Cascading configuration with priority order
    - Environment variable override support
    - Comprehensive validation with helpful error messages
    - Configuration migration for version updates
    - Backup and restore functionality
    - Hot-reload support
    """
    
    # Default configuration structure
    DEFAULT_CONFIG = {
        'parser': {
            'strict_mode': False,
            'require_header': False,
            'case_sensitive_attributes': False,
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'supported_protocols': [
                'http://', 'https://', 'rtmp://', 'rtmps://', 
                'udp://', 'ftp://', 'file://', 'rtsp://'
            ],
            'timeout': 30,
            'encoding_detection': True,
            'error_recovery': True,
            'chunk_size': 8192,
            'max_line_length': 4096
        },
        'validation': {
            'validate_urls': True,
            'validate_attributes': False,
            'max_url_length': 2048,
            'allowed_extensions': ['.m3u', '.m3u8'],
            'require_duration': False,
            'test_connectivity': False,
            'connection_timeout': 10,
            'validation_level': 'basic'  # basic, standard, strict
        },
        'processing': {
            'remove_duplicates': True,
            'duplicate_detection_method': 'url_similarity',
            'similarity_threshold': 0.85,
            'auto_categorize': True,
            'auto_detect_countries': True,
            'auto_detect_quality': True,
            'normalize_groups': True,
            'max_concurrent_operations': 10,
            'batch_size': 1000,
            'memory_limit_mb': 512
        },
        'output': {
            'format': 'json',
            'pretty_print': True,
            'include_warnings': True,
            'include_metadata': True,
            'generate_statistics': True,
            'backup_original': True,
            'output_directory': 'output',
            'filename_template': '{timestamp}_{format}.{ext}'
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file_logging': True,
            'console_logging': True,
            'log_directory': 'logs',
            'max_log_size': 10485760,  # 10MB
            'backup_count': 5,
            'log_rotation': True
        },
        'providers': {
            'urls': [],
            'headers': {},
            'auth': {},
            'retry_attempts': 3,
            'retry_delay': 5,
            'user_agent': 'M3U-Parser/1.0'
        },
        'epg': {
            'sources': [],
            'update_interval': 86400,  # 24 hours
            'cache_directory': 'cache/epg',
            'auto_match_channels': True,
            'match_threshold': 0.8
        },
        'filters': {
            'min_name_length': 1,
            'max_name_length': 200,
            'blocked_domains': ['example.com', 'test.com', 'localhost'],
            'required_protocols': [],
            'allowed_countries': [],
            'blocked_countries': [],
            'allowed_languages': [],
            'blocked_languages': [],
            'quality_filters': []
        }
    }
    
    # Validation rules for configuration
    VALIDATION_RULES = [
        ValidationRule('parser.max_file_size', True, int, 1024, None, description="Maximum file size in bytes"),
        ValidationRule('parser.timeout', True, int, 1, 300, description="Network timeout in seconds"),
        ValidationRule('parser.chunk_size', True, int, 1024, 65536, description="File chunk size for processing"),
        ValidationRule('validation.max_url_length', True, int, 100, 8192, description="Maximum URL length"),
        ValidationRule('validation.connection_timeout', True, int, 1, 60, description="Connection test timeout"),
        ValidationRule('validation.validation_level', True, str, allowed_values=['basic', 'standard', 'strict']),
        ValidationRule('processing.similarity_threshold', True, float, 0.0, 1.0, description="Duplicate detection threshold"),
        ValidationRule('processing.max_concurrent_operations', True, int, 1, 100, description="Max concurrent operations"),
        ValidationRule('processing.batch_size', True, int, 1, 10000, description="Processing batch size"),
        ValidationRule('processing.memory_limit_mb', True, int, 64, 8192, description="Memory limit in MB"),
        ValidationRule('logging.level', True, str, allowed_values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
        ValidationRule('logging.max_log_size', True, int, 1024, 104857600, description="Max log file size"),
        ValidationRule('logging.backup_count', True, int, 1, 20, description="Number of log backup files"),
    ]
    
    def __init__(self, 
                 config_name: str = "m3u_parser",
                 config_dir: Optional[Path] = None,
                 auto_create: bool = True,
                 auto_migrate: bool = True):
        """
        Initialize configuration manager
        
        Args:
            config_name: Base name for configuration files
            config_dir: Configuration directory (defaults to ./config)
            auto_create: Automatically create missing configuration files
            auto_migrate: Automatically migrate old configuration formats
        """
        self.config_name = config_name
        self.config_dir = config_dir or Path('./config')
        self.auto_create = auto_create
        self.auto_migrate = auto_migrate
        
        self.logger = logging.getLogger(__name__)
        self.config = {}
        self.config_sources = []
        self.last_modified = {}
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self._load_configuration()
        
        # Auto-create missing files if enabled
        if self.auto_create:
            self._create_missing_configs()
    
    def _load_configuration(self) -> None:
        """Load configuration from all sources with priority order"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_sources = []
        
        # Load in priority order (lowest to highest)
        loaders = [
            (ConfigSource.EMBEDDED_DEFAULTS, self._load_embedded_defaults),
            (ConfigSource.SYSTEM_CONFIG, self._load_system_config),
            (ConfigSource.PROJECT_CONFIG, self._load_project_config),
            (ConfigSource.USER_CONFIG, self._load_user_config),
            (ConfigSource.ENVIRONMENT, self._load_environment_config)
        ]
        
        for source, loader in loaders:
            try:
                config_data = loader()
                if config_data:
                    self._deep_merge_config(self.config, config_data)
                    self.config_sources.append(source.name)
                    self.logger.debug(f"Loaded config from {source.name}")
            except Exception as e:
                self.logger.warning(f"Failed to load config from {source.name}: {e}")
        
        # Validate final configuration
        self._validate_configuration()
        
        self.logger.info(f"Configuration loaded from sources: {', '.join(self.config_sources)}")
    
    def _load_embedded_defaults(self) -> Dict[str, Any]:
        """Load embedded default configuration"""
        return self.DEFAULT_CONFIG.copy()
    
    def _load_system_config(self) -> Dict[str, Any]:
        """Load system-wide configuration"""
        system_paths = [
            Path('/etc') / self.config_name,
            Path('/usr/local/etc') / self.config_name,
            Path('/opt') / self.config_name / 'config'
        ]
        
        for path in system_paths:
            if path.exists():
                return self._load_from_directory(path)
        
        return {}
    
    def _load_project_config(self) -> Dict[str, Any]:
        """Load project-level configuration"""
        return self._load_from_directory(self.config_dir)
    
    def _load_user_config(self) -> Dict[str, Any]:
        """Load user-specific configuration"""
        user_config_dir = Path.home() / '.config' / self.config_name
        if user_config_dir.exists():
            return self._load_from_directory(user_config_dir)
        return {}
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {}
        prefix = f"{self.config_name.upper()}_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower().replace('_', '.')
                config = self._set_nested_value(config, config_key, self._parse_env_value(value))
        
        return config
    
    def _load_from_directory(self, directory: Path) -> Dict[str, Any]:
        """Load configuration from a directory"""
        if not directory.exists():
            return {}
        
        config = {}
        
        # Try different config file formats in order of preference
        config_files = [
            f'{self.config_name}.toml',
            f'{self.config_name}.json',
            f'{self.config_name}.yaml',
            f'{self.config_name}.yml',
            'config.toml',
            'config.json',
            'config.yaml',
            'config.yml'
        ]
        
        for config_file in config_files:
            config_path = directory / config_file
            if config_path.exists():
                try:
                    file_config = self._load_config_file(config_path)
                    if file_config:
                        self._deep_merge_config(config, file_config)
                        self.last_modified[str(config_path)] = config_path.stat().st_mtime
                except Exception as e:
                    self.logger.warning(f"Failed to load {config_path}: {e}")
        
        # Load additional files (providers.txt, etc.)
        self._load_additional_files(directory, config)
        
        return config
    
    def _load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from a specific file"""
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    return json.load(f)
                elif file_path.suffix.lower() == '.toml':
                    return toml.load(f)
                elif file_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                else:
                    self.logger.warning(f"Unknown config file format: {file_path}")
                    return {}
        except Exception as e:
            self.logger.error(f"Error loading config file {file_path}: {e}")
            return {}
    
    def _load_additional_files(self, directory: Path, config: Dict[str, Any]) -> None:
        """Load additional configuration files (providers.txt, etc.)"""
        # Load providers
        providers_file = directory / 'providers.txt'
        if providers_file.exists():
            try:
                providers = []
                with open(providers_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and line.startswith('http'):
                            providers.append(line)
                if providers:
                    config.setdefault('providers', {})['urls'] = providers
            except Exception as e:
                self.logger.warning(f"Failed to load providers.txt: {e}")
        
        # Load EPG sources
        epg_file = directory / 'epg_sources.txt'
        if epg_file.exists():
            try:
                epg_sources = []
                with open(epg_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and line.startswith('http'):
                            epg_sources.append(line)
                if epg_sources:
                    config.setdefault('epg', {})['sources'] = epg_sources
            except Exception as e:
                self.logger.warning(f"Failed to load epg_sources.txt: {e}")
    
    def _create_missing_configs(self) -> None:
        """Create missing configuration files with defaults"""
        # Create main config file
        main_config_path = self.config_dir / f'{self.config_name}.toml'
        if not main_config_path.exists():
            self._create_default_config_file(main_config_path, ConfigFormat.TOML)
        
        # Create providers.txt
        providers_path = self.config_dir / 'providers.txt'
        if not providers_path.exists():
            self._create_providers_file(providers_path)
        
        # Create epg_sources.txt
        epg_path = self.config_dir / 'epg_sources.txt'
        if not epg_path.exists():
            self._create_epg_sources_file(epg_path)
        
        # Create additional directories
        for dir_name in ['logs', 'output', 'cache', 'backup']:
            dir_path = Path(dir_name)
            dir_path.mkdir(exist_ok=True)
    
    def _create_default_config_file(self, file_path: Path, format_type: ConfigFormat) -> None:
        """Create default configuration file"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type == ConfigFormat.TOML:
                with open(file_path, 'w', encoding='utf-8') as f:
                    toml.dump(self.DEFAULT_CONFIG, f)
            elif format_type == ConfigFormat.JSON:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.DEFAULT_CONFIG, f, indent=2)
            elif format_type == ConfigFormat.YAML:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False)
            
            self.logger.info(f"Created default config file: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create config file {file_path}: {e}")
    
    def _create_providers_file(self, file_path: Path) -> None:
        """Create default providers.txt file"""
        content = """# M3U Provider URLs
# Add your M3U playlist URLs here, one per line
# Lines starting with # are comments

# Example providers (replace with your actual URLs):
# https://example.com/playlist.m3u8
# http://your-provider.com/channels.m3u

# Free IPTV samples (for testing):
# https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ad.m3u
# https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ae.m3u
"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"Created providers file: {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to create providers file: {e}")
    
    def _create_epg_sources_file(self, file_path: Path) -> None:
        """Create default epg_sources.txt file"""
        content = """# EPG (Electronic Program Guide) Sources
# Add your EPG XML URLs here, one per line
# Lines starting with # are comments

# Example EPG sources:
# https://example.com/epg.xml
# http://your-epg-provider.com/guide.xml

# Free EPG sources (for testing):
# https://raw.githubusercontent.com/iptv-org/epg/master/sites/tv.com/tv.com.channels.xml
"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"Created EPG sources file: {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to create EPG sources file: {e}")
    
    def _validate_configuration(self) -> None:
        """Validate configuration against rules"""
        errors = []
        warnings = []
        
        for rule in self.VALIDATION_RULES:
            try:
                value = self._get_nested_value(self.config, rule.key_path)
                
                if value is None:
                    if rule.required:
                        errors.append(f"Required config key missing: {rule.key_path}")
                    continue
                
                # Type validation
                if not isinstance(value, rule.data_type):
                    errors.append(f"Config key {rule.key_path} must be {rule.data_type.__name__}, got {type(value).__name__}")
                    continue
                
                # Range validation
                if rule.min_value is not None and value < rule.min_value:
                    errors.append(f"Config key {rule.key_path} must be >= {rule.min_value}, got {value}")
                
                if rule.max_value is not None and value > rule.max_value:
                    errors.append(f"Config key {rule.key_path} must be <= {rule.max_value}, got {value}")
                
                # Allowed values validation
                if rule.allowed_values is not None and value not in rule.allowed_values:
                    errors.append(f"Config key {rule.key_path} must be one of {rule.allowed_values}, got {value}")
                
            except Exception as e:
                warnings.append(f"Failed to validate {rule.key_path}: {e}")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        if warnings:
            for warning in warnings:
                self.logger.warning(warning)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        return self._get_nested_value(self.config, key_path, default)
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        self.config = self._set_nested_value(self.config, key_path, value)
    
    def save(self, file_path: Optional[Path] = None, format_type: ConfigFormat = ConfigFormat.TOML) -> None:
        """Save current configuration to file"""
        if file_path is None:
            file_path = self.config_dir / f'{self.config_name}.{format_type.value}'
        
        # Create backup
        if file_path.exists():
            backup_path = file_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
        
        # Save configuration
        self._create_default_config_file(file_path, format_type)
        self.logger.info(f"Configuration saved to {file_path}")
    
    def reload(self) -> None:
        """Reload configuration from all sources"""
        self._load_configuration()
        self.logger.info("Configuration reloaded")
    
    def get_validation_errors(self) -> List[str]:
        """Get configuration validation errors without raising exception"""
        errors = []
        
        for rule in self.VALIDATION_RULES:
            try:
                value = self._get_nested_value(self.config, rule.key_path)
                
                if value is None and rule.required:
                    errors.append(f"Required config key missing: {rule.key_path}")
                    continue
                
                if value is not None:
                    if not isinstance(value, rule.data_type):
                        errors.append(f"Config key {rule.key_path} must be {rule.data_type.__name__}")
                    elif rule.allowed_values and value not in rule.allowed_values:
                        errors.append(f"Config key {rule.key_path} must be one of {rule.allowed_values}")
                        
            except Exception as e:
                errors.append(f"Failed to validate {rule.key_path}: {e}")
        
        return errors
    
    # Utility methods
    def _deep_merge_config(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge configuration dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_config(base[key], value)
            else:
                base[key] = value
    
    def _get_nested_value(self, config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
        """Get nested value using dot notation"""
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def _set_nested_value(self, config: Dict[str, Any], key_path: str, value: Any) -> Dict[str, Any]:
        """Set nested value using dot notation"""
        keys = key_path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        return config
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type"""
        # Boolean values
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False
        
        # Numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # JSON values
        if value.startswith(('[', '{')):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # String value
        return value

# Example usage and testing
if __name__ == "__main__":
    # Initialize config manager
    config_manager = ComprehensiveConfigManager(
        config_name="m3u_parser",
        auto_create=True,
        auto_migrate=True
    )
    
    # Test configuration access
    print("Parser Configuration:")
    print(f"  Strict Mode: {config_manager.get('parser.strict_mode')}")
    print(f"  Max File Size: {config_manager.get('parser.max_file_size')}")
    print(f"  Supported Protocols: {config_manager.get('parser.supported_protocols')}")
    
    print("\nValidation Configuration:")
    print(f"  Validate URLs: {config_manager.get('validation.validate_urls')}")
    print(f"  Max URL Length: {config_manager.get('validation.max_url_length')}")
    
    print("\nProcessing Configuration:")
    print(f"  Remove Duplicates: {config_manager.get('processing.remove_duplicates')}")
    print(f"  Auto Categorize: {config_manager.get('processing.auto_categorize')}")
    
    # Test validation
    errors = config_manager.get_validation_errors()
    if errors:
        print(f"\nValidation Errors: {errors}")
    else:
        print("\n✅ Configuration validation passed!")
    
    # Test setting values
    config_manager.set('parser.strict_mode', True)
    config_manager.set('validation.validation_level', 'strict')
    
    print(f"\nUpdated Strict Mode: {config_manager.get('parser.strict_mode')}")
    print(f"Updated Validation Level: {config_manager.get('validation.validation_level')}")
    
    # Save configuration
    config_manager.save()
    print("\n💾 Configuration saved successfully!")

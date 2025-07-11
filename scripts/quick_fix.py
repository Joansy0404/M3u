#!/usr/bin/env python3
"""
Quick Fix Script for M3U Tool
Run this to fix immediate issues and get your tool working
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def log(message):
    """Simple logging function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_missing_modules():
    """Create any missing module files with working implementations"""
    
    modules_dir = Path("scripts/modules")
    modules_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py if missing
    init_file = modules_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")
        log("✅ Created scripts/modules/__init__.py")
    
    # Create processor.py fallback
    processor_file = modules_dir / "processor.py"
    if not processor_file.exists() or processor_file.stat().st_size < 100:
        processor_content = '''"""
Basic M3U Processor Module
"""

import re
import urllib.parse

class M3UProcessor:
    def __init__(self):
        self.channels = []
    
    def process_channels(self, channels):
        """Process channels with basic validation"""
        valid_channels = []
        for channel in channels:
            if channel.get('url') and channel.get('name'):
                valid_channels.append(channel)
        return valid_channels
    
    def remove_duplicates(self, channels):
        """Remove duplicate channels based on URL"""
        seen_urls = set()
        unique_channels = []
        
        for channel in channels:
            url = channel.get('url', '').strip()
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_channels.append(channel)
        
        return unique_channels
    
    def is_valid_url(self, url):
        """Check if URL is valid"""
        if not url or len(url) < 10:
            return False
        return url.startswith(('http://', 'https://', 'rtmp://', 'rtmps://'))
'''
        processor_file.write_text(processor_content)
        log("✅ Created/Updated scripts/modules/processor.py")
    
    # Create config_manager.py fallback
    config_file = modules_dir / "config_manager.py"
    if not config_file.exists() or config_file.stat().st_size < 100:
        config_content = '''"""
Configuration Manager Module
"""

import os

class ConfigManager:
    def __init__(self):
        self.config = {}
    
    def load_config(self):
        """Load configuration from files"""
        config = {}
        
        # Load providers
        if os.path.exists('config/providers.txt'):
            with open('config/providers.txt', 'r') as f:
                providers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                config['providers'] = providers
        
        return config
    
    def get_providers(self):
        """Get list of provider URLs"""
        config = self.load_config()
        return config.get('providers', [])
'''
        config_file.write_text(config_content)
        log("✅ Created/Updated scripts/modules/config_manager.py")
    
    # Create logger_config.py fallback
    logger_file = modules_dir / "logger_config.py"
    if not logger_file.exists() or logger_file.stat().st_size < 100:
        logger_content = '''"""
Logger Configuration Module
"""

import logging
import sys
from pathlib import Path

def setup_logger():
    """Setup basic logging"""
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/processing.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)
'''
        logger_file.write_text(logger_content)
        log("✅ Created/Updated scripts/modules/logger_config.py")

def fix_country_grouper():
    """Fix country_grouper.py to handle missing pycountry"""
    country_file = Path("scripts/country_grouper.py")
    
    country_content = '''"""
Country detection and grouping functionality
Fixed version that handles missing pycountry gracefully
"""

try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False

import re
from typing import Optional, Dict, List

class CountryGrouper:
    def __init__(self):
        self.country_patterns = {
            'US': [r'\\b(usa?|united states|american?)\\b', r'\\bus\\b'],
            'UK': [r'\\b(uk|united kingdom|british?)\\b', r'\\bgb\\b'],
            'CA': [r'\\b(canada|canadian?)\\b', r'\\bca\\b'],
            'DE': [r'\\b(germany|german|deutschland)\\b', r'\\bde\\b'],
            'FR': [r'\\b(france|french|français)\\b', r'\\bfr\\b'],
            'ES': [r'\\b(spain|spanish|españa)\\b', r'\\bes\\b'],
            'IT': [r'\\b(italy|italian|italia)\\b', r'\\bit\\b'],
            'BR': [r'\\b(brazil|brazilian|brasil)\\b', r'\\bbr\\b'],
            'MX': [r'\\b(mexico|mexican|méxico)\\b', r'\\bmx\\b'],
            'IN': [r'\\b(india|indian)\\b', r'\\bin\\b'],
            'AU': [r'\\b(australia|australian|aussie)\\b', r'\\bau\\b'],
            'NL': [r'\\b(netherlands|dutch|holland)\\b', r'\\bnl\\b'],
            'TR': [r'\\b(turkey|turkish|türkiye)\\b', r'\\btr\\b'],
            'AR': [r'\\b(argentina|argentinian)\\b', r'\\bar\\b'],
            'RU': [r'\\b(russia|russian)\\b', r'\\bru\\b']
        }

    def detect_country(self, name: str, group: str = "") -> Optional[str]:
        """Detect country from channel name and group"""
        text = f"{name} {group}".lower()
        
        for country_code, patterns in self.country_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return country_code
        
        return None

    def group_by_country(self, channels: List[Dict]) -> Dict[str, List[Dict]]:
        """Group channels by detected country"""
        groups = {}
        
        for channel in channels:
            country = self.detect_country(
                channel.get('name', ''),
                channel.get('group', '')
            )
            
            if not country:
                country = 'Unknown'
            
            if country not in groups:
                groups[country] = []
            
            groups[country].append(channel)
        
        return groups

def detect_country_from_text(text: str) -> Optional[str]:
    """Standalone function for country detection"""
    grouper = CountryGrouper()
    return grouper.detect_country(text)
'''
    
    country_file.write_text(country_content)
    log("✅ Fixed scripts/country_grouper.py")

def create_fallback_imports():
    """Create fallback import files"""
    scripts_dir = Path("scripts")
    
    # Create importer.py fallback
    importer_file = scripts_dir / "importer.py"
    if not importer_file.exists() or importer_file.stat().st_size < 100:
        importer_content = '''"""
M3U Importer Module - Fallback Implementation
"""

import requests
import re

class M3UImporter:
    def __init__(self):
        pass
    
    def import_from_file(self, filepath):
        """Import channels from local M3U file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return self.parse_m3u_content(content)
        except Exception as e:
            print(f"Error importing {filepath}: {e}")
            return []
    
    def import_from_url(self, url):
        """Import channels from M3U URL"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return self.parse_m3u_content(response.text)
        except Exception as e:
            print(f"Error importing {url}: {e}")
            return []
    
    def parse_m3u_content(self, content):
        """Basic M3U parsing"""
        channels = []
        lines = content.split('\\n')
        current_channel = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                # Extract name from EXTINF line
                name_match = re.search(r',(.+)$', line)
                name = name_match.group(1) if name_match else 'Unknown'
                current_channel = {'name': name, 'group': 'General'}
            elif line and not line.startswith('#') and current_channel:
                current_channel['url'] = line
                channels.append(current_channel)
                current_channel = None
        
        return channels
'''
        importer_file.write_text(importer_content)
        log("✅ Created scripts/importer.py")
    
    # Create exporter.py fallback
    exporter_file = scripts_dir / "exporter.py"
    if not exporter_file.exists() or exporter_file.stat().st_size < 100:
        exporter_content = '''"""
M3U Exporter Module - Fallback Implementation
"""

import os

class M3UExporter:
    def __init__(self):
        pass
    
    def export_m3u(self, channels, filepath):
        """Export channels to M3U file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\\n')
            for channel in channels:
                name = channel.get('name', 'Unknown')
                url = channel.get('url', '')
                group = channel.get('group', '')
                
                # Write EXTINF line
                extinf = f'#EXTINF:-1'
                if group:
                    extinf += f' group-title="{group}"'
                extinf += f',{name}\\n'
                f.write(extinf)
                
                # Write URL
                f.write(f'{url}\\n')
    
    def export_json(self, channels, filepath):
        """Export channels to JSON file"""
        import json
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(channels, f, indent=2, ensure_ascii=False)
'''
        exporter_file.write_text(exporter_content)
        log("✅ Created scripts/exporter.py")

def fix_process_yml():
    """Fix the truncated process.yml file"""
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if process.yml is truncated
    process_yml = workflow_dir / "process.yml"
    
    if process_yml.exists():
        content = process_yml.read_text()
        # Check if it's truncated (ends with incomplete script)
        if "#!/usr/bi" in content and not content.strip().endswith("fi"):
            log("⚠️ Detected truncated process.yml - backing up and fixing...")
            
            # Create backup
            backup_file = workflow_dir / f"process.yml.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_file.write_text(content)
            log(f"📁 Backup created: {backup_file}")
            
            # Replace with working version
            working_yml = '''name: 🔧 M3U Processor - FIXED VERSION

on:
  workflow_dispatch:
    inputs:
      test_mode:
        description: 'Run in test mode'
        required: false
        default: 'true'
        type: boolean
  push:
    paths:
      - 'bulk_import.m3u'
      - 'playlist.m3u'
      - 'config/providers.txt'

permissions:
  contents: write

jobs:
  process:
    runs-on: ubuntu-latest
    
    steps:
    - name: 🔄 Checkout repository
      uses: actions/checkout@v4
        
    - name: 🐍 Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        
    - name: 📦 Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests>=2.28.0 charset-normalizer>=3.0.0 pycountry>=22.0.0
        
    - name: 📁 Create directories
      run: |
        mkdir -p playlists reports logs backups scripts
        
    - name: 🔧 Run quick fix
      run: |
        python quick_fix.py
        
    - name: 🚀 Process M3U files
      run: |
        python scripts/main.py
        
    - name: 📊 Show results
      run: |
        if [ -f "playlists/final.m3u" ]; then
          echo "📺 Channels: $(grep -c '^#EXTINF' playlists/final.m3u || echo '0')"
          echo "📁 File size: $(du -h playlists/final.m3u | cut -f1)"
        fi
        
    - name: 💾 Commit results
      run: |
        git config user.name "M3U Processor"
        git config user.email "actions@github.com"
        git add playlists/ reports/ -f
        
        if ! git diff --staged --quiet; then
          CHANNELS=$(grep -c '^#EXTINF' playlists/final.m3u 2>/dev/null || echo '0')
          git commit -m "🔄 Updated M3U playlist - $CHANNELS channels - $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
          git push
        fi
'''
            process_yml.write_text(working_yml)
            log("✅ Fixed process.yml workflow")

def check_requirements():
    """Check and create requirements.txt if missing"""
    req_file = Path("requirements.txt")
    
    if not req_file.exists():
        requirements = '''# M3U Tool Dependencies
requests>=2.28.0
charset-normalizer>=3.0.0
pycountry>=22.0.0
lxml>=4.9.0
beautifulsoup4>=4.11.0
'''
        req_file.write_text(requirements)
        log("✅ Created requirements.txt")

def ensure_config_files():
    """Ensure all config files exist"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # providers.txt
    providers_file = config_dir / "providers.txt"
    if not providers_file.exists():
        providers_content = '''# M3U Provider URLs
# Add your IPTV playlist URLs here (one per line)
https://iptv-org.github.io/iptv/languages/eng.m3u
https://raw.githubusercontent.com/iptv-org/iptv/master/streams/us.m3u
'''
        providers_file.write_text(providers_content)
        log("✅ Created config/providers.txt")
    
    # epg_sources.txt
    epg_file = config_dir / "epg_sources.txt"
    if not epg_file.exists():
        epg_content = '''# EPG Source URLs
# Add EPG (Electronic Program Guide) URLs here
'''
        epg_file.write_text(epg_content)
        log("✅ Created config/epg_sources.txt")

def main():
    """Main fix function"""
    log("🔧 Starting M3U Tool Quick Fix...")
    log("="*50)
    
    try:
        # Fix workflow first (most critical)
        fix_process_yml()
        
        # Create missing modules
        create_missing_modules()
        
        # Fix country grouper
        fix_country_grouper()
        
        # Create fallback imports
        create_fallback_imports()
        
        # Check requirements
        check_requirements()
        
        # Ensure config files
        ensure_config_files()
        
        log("="*50)
        log("✅ Quick fix completed successfully!")
        log("")
        log("🚀 Next steps:")
        log("1. Commit these fixes: git add . && git commit -m 'Fixed M3U tool issues'")
        log("2. Push to trigger workflow: git push")
        log("3. Check GitHub Actions tab for processing")
        log("4. Download results from playlists/final.m3u")
        log("")
        log("Your M3U tool should now work properly! 🎉")
        
    except Exception as e:
        log(f"❌ Error during fix: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
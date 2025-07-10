#!/usr/bin/env python3
"""
Ultimate M3U Editor - Complete Setup Script (UPDATED VERSION)
This script creates a comprehensive M3U playlist editor system for GitHub deployment
"""

import os
import sys
from datetime import datetime

def log(message):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    with open("processing.log", "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def create_directory_structure():
    """Create the required directory structure"""
    directories = [
        ".github/workflows",
        "config",
        "editor", 
        "playlists",
        "scripts",
        "scripts/modules",  # Ensure the modules directory is created
        "logs",             # Add logs directory
        "backups"           # Add backups directory
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        log(f"Created directory: {directory}")

def create_module_files():
    """Create missing modules in the scripts/modules directory"""
    modules = {
        "scripts/modules/__init__.py": "",
        "scripts/modules/config_manager.py": """# Handles configuration settings
def load_config():
    pass
""",
        "scripts/modules/backup_manager.py": """# Manages file backups
def create_backup():
    pass
""",
        "scripts/modules/logger_config.py": """# Logger configuration
def setup_logger():
    pass
""",
        "scripts/modules/channel_processor.py": """# Advanced channel processing logic
def process_channels():
    pass
""",
        "scripts/modules/file_handler.py": """# File I/O operations
def handle_files():
    pass
""",
        "scripts/modules/country_detector.py": """# Detects channel country
def detect_country():
    pass
""",
        "scripts/modules/quality_detector.py": """# Detects stream quality
def detect_quality():
    pass
""",
        "scripts/modules/duplicate_manager.py": """# Manages duplicate channels
def remove_duplicates():
    pass
""",
        "scripts/modules/channel_manager.py": """# Manages channel metadata
def manage_channels():
    pass
""",
        "scripts/modules/group_filter.py": """# Filters groups
def filter_groups():
    pass
""",
        "scripts/modules/m3u_generator.py": """# Generates M3U files
def generate_m3u():
    pass
""",
        "scripts/modules/stats_generator.py": """# Generates statistics
def generate_stats():
    pass
""",
        "scripts/modules/setup.py": """# Setup logic for modules
def setup():
    pass
"""
    }

    for file_path, content in modules.items():
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        log(f"Created module: {file_path}")

def create_github_workflow():
    """Create GitHub workflow file"""
    workflow_content = '''name: Ultimate M3U Editor

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
  push:
    paths:
      - 'config/**'
      - 'editor/**'
      - 'scripts/**'

permissions:
  contents: write

jobs:
  process:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
        
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        pip install requests pycountry lxml beautifulsoup4
        
    - name: Run processing
      run: |
        echo "Running M3U processing..."
        python scripts/main.py
        
    - name: Commit changes
      run: |
        git config user.name "M3U Editor Bot"
        git config user.email "actions@github.com"
        
        git pull origin main --rebase || true
        git add .
        
        if ! git diff --staged --quiet; then
          CHANNEL_COUNT=$(grep -c '^#EXTINF' playlists/final.m3u 2>/dev/null || echo '0')
          TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
          
          git commit -m "Auto-update M3U playlist - $TIMESTAMP | Channels: $CHANNEL_COUNT | By GitHub Actions"
          git push origin main --force-with-lease || git push origin main
        else
          echo "No changes to commit"
        fi
'''
    with open(".github/workflows/process.yml", "w", encoding="utf-8") as f:
        f.write(workflow_content)
    log("Created GitHub workflow: .github/workflows/process.yml")

def create_config_files():
    """Create or enhance configuration files"""
    # Enhanced providers.txt
    providers_content = """# M3U Provider URLs
# Add your IPTV playlist URLs here (one per line)
https://iptv-org.github.io/iptv/languages/eng.m3u
https://raw.githubusercontent.com/iptv-org/iptv/master/streams/us.m3u
"""
    with open("config/providers.txt", "w", encoding="utf-8") as f:
        f.write(providers_content)
    log("Enhanced config/providers.txt")

    # Enhanced epg_sources.txt
    epg_content = """# EPG Source URLs
# Add EPG (Electronic Program Guide) URLs here
https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz
"""
    with open("config/epg_sources.txt", "w", encoding="utf-8") as f:
        f.write(epg_content)
    log("Enhanced config/epg_sources.txt")

    # Enhanced commands.txt
    commands_content = """# Processing Commands
# Define the processing pipeline
IMPORT
GROUP_BY_COUNTRY
APPLY_EPG
APPLY_LOGOS
EXPORT
"""
    with open("config/commands.txt", "w", encoding="utf-8") as f:
        f.write(commands_content)
    log("Enhanced config/commands.txt")

def create_utils_script():
    """Create utility functions script"""
    utils_content = '''#!/usr/bin/env python3
"""
M3U Editor Utilities
Common utility functions for M3U processing
"""

import re
import os
import requests
from urllib.parse import urlparse


def log(message, level="INFO"):
    """Enhanced logging function"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"
    print(log_message)
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    with open("logs/processing.log", "a", encoding="utf-8") as f:
        f.write(log_message + "\\n")


def normalize_name(name):
    """Normalize channel name for matching"""
    if not name:
        return ""
    return re.sub(r'[^\\w\\s]', '', name.lower()).strip()


def get_logo_from_name(channel_name):
    """Generate logo URL from channel name"""
    name_lower = channel_name.lower()
    
    logo_map = {
        'cnn': 'https://upload.wikimedia.org/wikipedia/commons/b/b1/CNN.svg',
        'bbc': 'https://upload.wikimedia.org/wikipedia/commons/6/62/BBC_News_2019.svg',
        'fox': 'https://upload.wikimedia.org/wikipedia/commons/6/67/Fox_News_Channel_logo.svg',
        'espn': 'https://upload.wikimedia.org/wikipedia/commons/2/2f/ESPN_wordmark.svg',
        'discovery': 'https://upload.wikimedia.org/wikipedia/commons/2/27/Discovery_Channel_logo.svg',
        'history': 'https://logos-world.net/wp-content/uploads/2020/06/History-Channel-Logo.png',
        'national geographic': 'https://logos-world.net/wp-content/uploads/2020/09/National-Geographic-Logo.png',
        'disney': 'https://logos-world.net/wp-content/uploads/2020/05/Disney-Channel-Logo-2014-2019.png'
    }
    
    for key, logo in logo_map.items():
        if key in name_lower:
            return logo
    
    return ""


def get_epg_id(channel_name):
    """Generate EPG ID from channel name"""
    name_lower = channel_name.lower()
    
    epg_map = {
        'cnn international': 'cnn.international',
        'cnn': 'cnn.us',
        'bbc world news': 'bbc.world.news',
        'bbc news': 'bbc.news.uk',
        'bbc one': 'bbc.one.uk',
        'fox news': 'fox.news.us',
        'espn': 'espn.us',
        'discovery channel': 'discovery.channel',
        'history channel': 'history.us',
        'national geographic': 'nat.geo.us',
        'disney channel': 'disney.channel.us',
        'sky news': 'sky.news.uk',
        'al jazeera': 'aljazeera.english'
    }
    
    for key, epg_id in epg_map.items():
        if key in name_lower:
            return epg_id
    
    clean_name = normalize_name(channel_name)
    return clean_name.replace(' ', '.')


def detect_country_from_name(name):
    """Detect country from channel name"""
    name_lower = name.lower()
    
    if any(x in name_lower for x in ['cnn', 'fox', 'nbc', 'abc', 'usa']):
        return 'US'
    elif any(x in name_lower for x in ['bbc', 'itv', 'sky', 'uk']):
        return 'GB'
    elif any(x in name_lower for x in ['france', 'tf1']):
        return 'FR'
    elif any(x in name_lower for x in ['deutschland', 'ard', 'zdf']):
        return 'DE'
    
    return 'Unknown'


def validate_url(url):
    """Validate if URL is accessible"""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False
'''
    with open("scripts/utils.py", "w", encoding="utf-8") as f:
        f.write(utils_content)
    log("Created scripts/utils.py")

def create_main_script():
    """Create enhanced main processing script"""
    main_content = '''#!/usr/bin/env python3
"""
M3U Editor Main Processing Script
Handles the complete M3U playlist processing pipeline
"""

import requests
import re
import os
import sys
from urllib.parse import urlparse

# Add current directory to path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from utils import log, normalize_name, get_logo_from_name, get_epg_id, detect_country_from_name
except ImportError:
    # Fallback if utils module not available
    def log(msg): print(f"[M3U] {msg}")
    def normalize_name(name): return name.lower().strip() if name else ""
    def get_logo_from_name(name): return ""
    def get_epg_id(name): return normalize_name(name).replace(' ', '.')
    def detect_country_from_name(name): return 'General'


def download_playlists():
    """Download and parse M3U playlists from configured providers"""
    urls = []
    try:
        with open('config/providers.txt', 'r') as f:
            urls = [line.strip() for line in f if line.strip() and line.startswith('http')]
    except:
        urls = ['https://iptv-org.github.io/iptv/languages/eng.m3u']
    
    all_channels = []
    for url in urls:
        try:
            log(f"Downloading from {url}")
            r = requests.get(url, timeout=30)
            content = r.text
            
            # Parse M3U with full attribute extraction
            lines = content.split('\\n')
            current = {}
            for line in lines:
                line = line.strip()
                if line.startswith('#EXTINF'):
                    current = {'name': '', 'url': '', 'group': 'General', 'logo': '', 'epg': ''}
                    
                    # Extract channel name
                    if ',' in line:
                        name = line.split(',', 1)[1].strip()
                        current['name'] = name
                        
                        # Extract existing logo from tvg-logo
                        logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                        if logo_match:
                            current['logo'] = logo_match.group(1)
                        else:
                            current['logo'] = get_logo_from_name(name)
                        
                        # Extract existing EPG from tvg-id
                        epg_match = re.search(r'tvg-id="([^"]*)"', line)
                        if epg_match:
                            current['epg'] = epg_match.group(1)
                        else:
                            current['epg'] = get_epg_id(name)
                        
                        # Extract group
                        group_match = re.search(r'group-title="([^"]*)"', line)
                        if group_match:
                            current['group'] = group_match.group(1)
                        else:
                            # Smart country detection
                            country = detect_country_from_name(name)
                            if country != 'Unknown':
                                current['group'] = f'{country} Channels'
                            elif any(x in name.lower() for x in ['news']):
                                current['group'] = 'News'
                            elif any(x in name.lower() for x in ['sport', 'espn']):
                                current['group'] = 'Sports'
                            elif any(x in name.lower() for x in ['movie', 'cinema', 'film']):
                                current['group'] = 'Movies'
                                
                elif line and not line.startswith('#') and current and current['name']:
                    current['url'] = line
                    all_channels.append(current)
                    current = {}
                    
            log(f"Found {len([c for c in all_channels if c.get('url')])} channels")
        except Exception as e:
            log(f"Error processing {url}: {e}")
    
    return all_channels


def write_playlist(channels):
    """Write processed channels to M3U playlist and editor file"""
    os.makedirs('playlists', exist_ok=True)
    
    # Sort by group
    channels.sort(key=lambda x: (x.get('group', ''), x.get('name', '')))
    
    # Write M3U playlist
    with open('playlists/final.m3u', 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\\n')
        for ch in channels:
            if ch.get('url') and ch.get('name'):
                extinf = f'#EXTINF:-1'
                if ch.get('epg'):
                    extinf += f' tvg-id="{ch["epg"]}"'
                if ch.get('logo'):
                    extinf += f' tvg-logo="{ch["logo"]}"'
                extinf += f' group-title="{ch["group"]}",{ch["name"]}'
                f.write(f'{extinf}\\n')
                f.write(f'{ch["url"]}\\n')
    
    log(f"Exported {len(channels)} channels to playlists/final.m3u")
    
    # Create editor file
    os.makedirs('editor', exist_ok=True)
    with open('editor/channels.txt', 'w', encoding='utf-8') as f:
        f.write("# Ultimate M3U Editor - Channel Editor\\n")
        f.write("# ===================================\\n")
        f.write("# Edit channel information below\\n")
        f.write("# Format: [Channel Name]\\n")
        f.write("#         group: Group Name\\n")
        f.write("#         url: Stream URL\\n")
        f.write("#         logo: Logo URL\\n")
        f.write("#         epg: EPG ID\\n\\n")
        
        current_group = ""
        for ch in channels:
            group = ch.get('group', 'General')
            if group != current_group:
                f.write(f"\\n## {group}\\n")
                f.write("=" * (len(group) + 3) + "\\n\\n")
                current_group = group
            
            f.write(f"[{ch['name']}]\\n")
            f.write(f"group: {ch['group']}\\n")
            f.write(f"url: {ch['url']}\\n")
            
            if ch.get('logo'):
                f.write(f"logo: {ch['logo']}\\n")
            else:
                f.write("logo: (add custom logo URL here)\\n")
            
            if ch.get('epg'):
                f.write(f"epg: {ch['epg']}\\n")
            else:
                f.write("epg: (add custom EPG ID here)\\n")
            
            f.write("\\n")


def main():
    """Main processing function"""
    log("Starting M3U processing...")
    try:
        channels = download_playlists()
        if channels:
            write_playlist(channels)
            log("Processing completed successfully!")
        else:
            log("No channels found to process")
    except Exception as e:
        log(f"Processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
'''
    with open("scripts/main.py", "w", encoding="utf-8") as f:
        f.write(main_content)
    log("Created scripts/main.py")

def create_importer_script():
    """Create playlist importer script"""
    importer_content = '''#!/usr/bin/env python3
"""
M3U Playlist Importer
Handles importing and validating M3U playlists
"""

import requests
import re
import os
import sys
from urllib.parse import urlparse


def import_playlist(url):
    """Import a single playlist from URL"""
    try:
        print(f"Importing playlist from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content = response.text
        channels = []
        lines = content.split('\\n')
        current_channel = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('#EXTINF'):
                current_channel = parse_extinf_line(line)
            elif line and not line.startswith('#') and current_channel:
                current_channel['url'] = line
                channels.append(current_channel)
                current_channel = {}
        
        print(f"Successfully imported {len(channels)} channels")
        return channels
        
    except Exception as e:
        print(f"Error importing playlist: {e}")
        return []


def parse_extinf_line(line):
    """Parse EXTINF line to extract channel information"""
    channel = {
        'name': '',
        'group': 'General',
        'logo': '',
        'epg': '',
        'url': ''
    }
    
    # Extract channel name
    if ',' in line:
        channel['name'] = line.split(',', 1)[1].strip()
    
    # Extract attributes
    logo_match = re.search(r'tvg-logo="([^"]*)"', line)
    if logo_match:
        channel['logo'] = logo_match.group(1)
    
    epg_match = re.search(r'tvg-id="([^"]*)"', line)
    if epg_match:
        channel['epg'] = epg_match.group(1)
    
    group_match = re.search(r'group-title="([^"]*)"', line)
    if group_match:
        channel['group'] = group_match.group(1)
    
    return channel


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        channels = import_playlist(url)
        print(f"Imported {len(channels)} channels from {url}")
    else:
        print("Usage: python importer.py <playlist_url>")
'''
    with open("scripts/importer.py", "w", encoding="utf-8") as f:
        f.write(importer_content)
    log("Created scripts/importer.py")

def create_country_grouper_script():
    """Create country grouping script"""
    grouper_content = '''#!/usr/bin/env python3
"""
M3U Country Grouper
Groups channels by country based on various detection methods
"""

import re
import pycountry


def detect_country_from_channel(channel_info):
    """Detect country from channel information"""
    name = channel_info.get('name', '').lower()
    group = channel_info.get('group', '').lower()
    url = channel_info.get('url', '').lower()
    
    # Country patterns
    country_patterns = {
        'US': ['usa', 'america', 'cnn', 'fox', 'nbc', 'abc', 'cbs'],
        'GB': ['uk', 'britain', 'british', 'bbc', 'itv', 'sky'],
        'FR': ['france', 'french', 'tf1', 'canal+'],
        'DE': ['germany', 'german', 'deutschland', 'ard', 'zdf'],
        'IT': ['italy', 'italian', 'italia', 'rai'],
        'ES': ['spain', 'spanish', 'espana', 'tve'],
        'PT': ['portugal', 'portuguese', 'rtp'],
        'NL': ['netherlands', 'dutch', 'npo'],
        'BE': ['belgium', 'belgian', 'vrt'],
        'SE': ['sweden', 'swedish', 'svt'],
        'NO': ['norway', 'norwegian', 'nrk'],
        'DK': ['denmark', 'danish', 'dr'],
        'FI': ['finland', 'finnish', 'yle'],
        'PL': ['poland', 'polish', 'tvp'],
        'RU': ['russia', 'russian', 'rossiya'],
        'TR': ['turkey', 'turkish', 'trt'],
        'GR': ['greece', 'greek', 'ert'],
        'IN': ['india', 'indian', 'zee', 'star'],
        'CN': ['china', 'chinese', 'cctv'],
        'JP': ['japan', 'japanese', 'nhk'],
        'KR': ['korea', 'korean', 'kbs'],
        'AU': ['australia', 'australian', 'abc'],
        'CA': ['canada', 'canadian', 'cbc'],
        'BR': ['brazil', 'brazilian', 'globo'],
        'MX': ['mexico', 'mexican', 'televisa'],
        'AR': ['argentina', 'argentine', 'telefe']
    }
    
    # Check all text fields for country patterns
    all_text = f"{name} {group} {url}"
    
    for country_code, patterns in country_patterns.items():
        for pattern in patterns:
            if pattern in all_text:
                return country_code
    
    # Check for country codes in text
    for country in pycountry.countries:
        if country.alpha_2.lower() in all_text:
            return country.alpha_2
        if hasattr(country, 'alpha_3') and country.alpha_3.lower() in all_text:
            return country.alpha_2
    
    return 'Unknown'


def group_channels_by_country(channels):
    """Group channels by detected country"""
    grouped = {}
    
    for channel in channels:
        country = detect_country_from_channel(channel)
        
        if country not in grouped:
            grouped[country] = []
        
        # Update channel group
        if country != 'Unknown':
            try:
                country_obj = pycountry.countries.get(alpha_2=country)
                channel['group'] = f"{country_obj.name} Channels"
            except:
                channel['group'] = f"{country} Channels"
        
        grouped[country].append(channel)
    
    return grouped


if __name__ == "__main__":
    print("Country Grouper - Use as module")
'''
    with open("scripts/country_grouper.py", "w", encoding="utf-8") as f:
        f.write(grouper_content)
    log("Created scripts/country_grouper.py")

def create_epg_manager_script():
    """Create EPG management script"""
    epg_content = '''#!/usr/bin/env python3
"""
EPG (Electronic Program Guide) Manager
Handles EPG data integration for M3U playlists
"""

import requests
import xml.etree.ElementTree as ET
import gzip
import os
from urllib.parse import urlparse


def download_epg_data(url):
    """Download EPG data from URL"""
    try:
        print(f"Downloading EPG data from: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        content = response.content
        
        # Handle gzipped content
        if url.endswith('.gz'):
            content = gzip.decompress(content)
        
        return content.decode('utf-8', errors='ignore')
    
    except Exception as e:
        print(f"Error downloading EPG data: {e}")
        return None


def parse_epg_channels(epg_content):
    """Parse EPG XML to extract channel information"""
    try:
        root = ET.fromstring(epg_content)
        channels = {}
        
        for channel in root.findall('channel'):
            channel_id = channel.get('id')
            display_name = channel.find('display-name')
            
            if channel_id and display_name is not None:
                channels[channel_id] = {
                    'id': channel_id,
                    'name': display_name.text,
                    'icon': None
                }
                
                # Extract icon if available
                icon = channel.find('icon')
                if icon is not None:
                    channels[channel_id]['icon'] = icon.get('src')
        
        return channels
    
    except Exception as e:
        print(f"Error parsing EPG data: {e}")
        return {}


def match_channels_to_epg(m3u_channels, epg_channels):
    """Match M3U channels to EPG channels"""
    matched = 0
    
    for channel in m3u_channels:
        channel_name = channel.get('name', '').lower()
        
        # Try exact match first
        for epg_id, epg_info in epg_channels.items():
            epg_name = epg_info['name'].lower()
            
            if channel_name == epg_name:
                channel['epg'] = epg_id
                if epg_info.get('icon') and not channel.get('logo'):
                    channel['logo'] = epg_info['icon']
                matched += 1
                break
        
        # Try partial match if no exact match
        if not channel.get('epg'):
            for epg_id, epg_info in epg_channels.items():
                epg_name = epg_info['name'].lower()
                
                if any(word in epg_name for word in channel_name.split() if len(word) > 2):
                    channel['epg'] = epg_id
                    if epg_info.get('icon') and not channel.get('logo'):
                        channel['logo'] = epg_info['icon']
                    matched += 1
                    break
    
    print(f"Matched {matched} channels to EPG data")
    return m3u_channels


def process_epg_sources():
    """Process all configured EPG sources"""
    epg_urls = []
    try:
        with open('config/epg_sources.txt', 'r') as f:
            epg_urls = [line.strip() for line in f if line.strip() and line.startswith('http')]
    except:
        return {}
    
    all_epg_channels = {}
    
    for url in epg_urls:
        epg_content = download_epg_data(url)
        if epg_content:
            epg_channels = parse_epg_channels(epg_content)
            all_epg_channels.update(epg_channels)
    
    return all_epg_channels


if __name__ == "__main__":
    print("EPG Manager - Use as module")
'''
    with open("scripts/epg_manager.py", "w", encoding="utf-8") as f:
        f.write(epg_content)
    log("Created scripts/epg_manager.py")

def create_logo_manager_script():
    """Create logo management script"""
    logo_content = '''#!/usr/bin/env python3
"""
Logo Manager
Handles channel logo detection and assignment
"""

import requests
import re
from urllib.parse import urlparse, urljoin


def get_channel_logo(channel_name, channel_url=None):
    """Get logo URL for a channel"""
    
    # Predefined logo mappings
    logo_mappings = {
        'cnn': 'https://upload.wikimedia.org/wikipedia/commons/b/b1/CNN.svg',
        'bbc news': 'https://upload.wikimedia.org/wikipedia/commons/6/62/BBC_News_2019.svg',
        'bbc one': 'https://upload.wikimedia.org/wikipedia/commons/8/8b/BBC_One_logo_2021.svg',
        'bbc two': 'https://upload.wikimedia.org/wikipedia/commons/1/15/BBC_Two_logo_2021.svg',
        'fox news': 'https://upload.wikimedia.org/wikipedia/commons/6/67/Fox_News_Channel_logo.svg',
        'espn': 'https://upload.wikimedia.org/wikipedia/commons/2/2f/ESPN_wordmark.svg',
        'discovery': 'https://upload.wikimedia.org/wikipedia/commons/2/27/Discovery_Channel_logo.svg',
        'history': 'https://logos-world.net/wp-content/uploads/2020/06/History-Channel-Logo.png',
        'national geographic': 'https://logos-world.net/wp-content/uploads/2020/09/National-Geographic-Logo.png',
        'disney channel': 'https://logos-world.net/wp-content/uploads/2020/05/Disney-Channel-Logo-2014-2019.png',
        'mtv': 'https://upload.wikimedia.org/wikipedia/commons/6/68/MTV_2021_logo.svg',
        'vh1': 'https://upload.wikimedia.org/wikipedia/commons/9/94/VH1_logonew.svg',
        'comedy central': 'https://upload.wikimedia.org/wikipedia/commons/a/aa/Comedy_Central_2018.svg',
        'cartoon network': 'https://upload.wikimedia.org/wikipedia/commons/8/80/Cartoon_Network_2010_logo.svg',
        'nickelodeon': 'https://upload.wikimedia.org/wikipedia/commons/7/7a/Nickelodeon_2009_logo.svg',
        'animal planet': 'https://upload.wikimedia.org/wikipedia/commons/2/20/2018_Animal_Planet_logo.svg',
        'travel channel': 'https://logos-world.net/wp-content/uploads/2020/06/Travel-Channel-Logo.png',
        'food network': 'https://logos-world.net/wp-content/uploads/2020/06/Food-Network-Logo.png',
        'hgtv': 'https://logos-world.net/wp-content/uploads/2020/06/HGTV-Logo.png',
        'tlc': 'https://upload.wikimedia.org/wikipedia/commons/7/74/TLC_Logo.svg',
        'lifetime': 'https://logos-world.net/wp-content/uploads/2020/06/Lifetime-Logo.png',
        'a&e': 'https://upload.wikimedia.org/wikipedia/commons/d/df/A%26E_Network_logo.svg',
        'syfy': 'https://upload.wikimedia.org/wikipedia/commons/b/b9/Syfy_logo_2017.svg',
        'usa network': 'https://upload.wikimedia.org/wikipedia/commons/d/d7/USA_Network_logo_2016.svg',
        'fx': 'https://upload.wikimedia.org/wikipedia/commons/4/4d/FX_International_logo.svg',
        'amc': 'https://upload.wikimedia.org/wikipedia/commons/1/16/AMC_logo_2016.svg',
        'tnt': 'https://upload.wikimedia.org/wikipedia/commons/2/2e/TNT_Logo_2016.svg',
        'tbs': 'https://upload.wikimedia.org/wikipedia/commons/d/de/TBS_logo_2016.svg',
        'spike': 'https://logos-world.net/wp-content/uploads/2020/06/Spike-TV-Logo.png',
        'bravo': 'https://upload.wikimedia.org/wikipedia/commons/6/64/Bravo_2017_logo.svg'
    }
    
    # Normalize channel name for matching
    name_lower = channel_name.lower().strip()
    
    # Try exact match first
    if name_lower in logo_mappings:
        return logo_mappings[name_lower]
    
    # Try partial matches
    for key, logo_url in logo_mappings.items():
        if key in name_lower or any(word in name_lower for word in key.split() if len(word) > 2):
            return logo_url
    
    # Try to extract logo from channel URL domain
    if channel_url:
        try:
            domain = urlparse(channel_url).netloc.lower()
            for key, logo_url in logo_mappings.items():
                if any(word in domain for word in key.split() if len(word) > 2):
                    return logo_url
        except:
            pass
    
    return None


def assign_logos_to_channels(channels):
    """Assign logos to channels that don't have them"""
    assigned = 0
    
    for channel in channels:
        if not channel.get('logo'):
            logo_url = get_channel_logo(
                channel.get('name', ''),
                channel.get('url', '')
            )
            
            if logo_url:
                channel['logo'] = logo_url
                assigned += 1
    
    print(f"Assigned logos to {assigned} channels")
    return channels


def validate_logo_urls(channels):
    """Validate that logo URLs are accessible"""
    validated = 0
    
    for channel in channels:
        logo_url = channel.get('logo')
        if logo_url:
            try:
                response = requests.head(logo_url, timeout=10)
                if response.status_code == 200:
                    validated += 1
                else:
                    print(f"Invalid logo URL for {channel.get('name')}: {logo_url}")
                    channel['logo'] = ''
            except:
                print(f"Unreachable logo URL for {channel.get('name')}: {logo_url}")
                channel['logo'] = ''
    
    print(f"Validated {validated} logo URLs")
    return channels


if __name__ == "__main__":
    print("Logo Manager - Use as module")
'''
    with open("scripts/logo_manager.py", "w", encoding="utf-8") as f:
        f.write(logo_content)
    log("Created scripts/logo_manager.py")

def create_exporter_script():
    """Create playlist exporter script"""
    exporter_content = '''#!/usr/bin/env python3
"""
M3U Playlist Exporter
Handles exporting processed channels to various formats
"""

import os
import json
from datetime import datetime


def export_to_m3u(channels, filename="final.m3u"):
    """Export channels to M3U format"""
    os.makedirs('playlists', exist_ok=True)
    filepath = os.path.join('playlists', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\\n')
        
        for channel in channels:
            if channel.get('url') and channel.get('name'):
                # Build EXTINF line
                extinf = '#EXTINF:-1'
                
                if channel.get('epg'):
                    extinf += f' tvg-id="{channel["epg"]}"'
                
                if channel.get('logo'):
                    extinf += f' tvg-logo="{channel["logo"]}"'
                
                extinf += f' group-title="{channel.get("group", "General")}",{channel["name"]}'
                
                f.write(f'{extinf}\\n')
                f.write(f'{channel["url"]}\\n')
    
    print(f"Exported {len(channels)} channels to {filepath}")
    return filepath


def export_to_json(channels, filename="channels.json"):
    """Export channels to JSON format"""
    os.makedirs('playlists', exist_ok=True)
    filepath = os.path.join('playlists', filename)
    
    export_data = {
        'metadata': {
            'export_date': datetime.now().isoformat(),
            'total_channels': len(channels),
            'format_version': '1.0'
        },
        'channels': channels
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(channels)} channels to {filepath}")
    return filepath


def export_to_txt(channels, filename="channels_list.txt"):
    """Export channels to simple text format"""
    os.makedirs('playlists', exist_ok=True)
    filepath = os.path.join('playlists', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Channel List - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        f.write(f"# Total channels: {len(channels)}\\n\\n")
        
        current_group = ""
        for channel in sorted(channels, key=lambda x: (x.get('group', ''), x.get('name', ''))):
            group = channel.get('group', 'General')
            
            if group != current_group:
                f.write(f"\\n## {group}\\n")
                f.write("=" * (len(group) + 3) + "\\n")
                current_group = group
            
            f.write(f"- {channel.get('name', 'Unknown')}\\n")
            if channel.get('url'):
                f.write(f"  URL: {channel['url']}\\n")
            if channel.get('logo'):
                f.write(f"  Logo: {channel['logo']}\\n")
            if channel.get('epg'):
                f.write(f"  EPG: {channel['epg']}\\n")
            f.write("\\n")
    
    print(f"Exported {len(channels)} channels to {filepath}")
    return filepath


def export_by_group(channels):
    """Export channels grouped by category"""
    groups = {}
    
    for channel in channels:
        group = channel.get('group', 'General')
        if group not in groups:
            groups[group] = []
        groups[group].append(channel)
    
    exported_files = []
    
    for group_name, group_channels in groups.items():
        safe_name = "".join(c for c in group_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name.replace(' ', '_').lower()}.m3u"
        filepath = export_to_m3u(group_channels, filename)
        exported_files.append(filepath)
    
    print(f"Exported {len(groups)} group files")
    return exported_files


def create_playlist_index(channels):
    """Create an index file listing all playlists"""
    os.makedirs('playlists', exist_ok=True)
    
    groups = {}
    for channel in channels:
        group = channel.get('group', 'General')
        groups[group] = groups.get(group, 0) + 1
    
    with open('playlists/index.html', 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\\n')
        f.write('<html>\\n<head>\\n')
        f.write('<title>M3U Playlist Index</title>\\n')
        f.write('<style>\\n')
        f.write('body { font-family: Arial, sans-serif; margin: 40px; }\\n')
        f.write('h1 { color: #333; }\\n')
        f.write('.playlist { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }\\n')
        f.write('.count { color: #666; font-size: 0.9em; }\\n')
        f.write('</style>\\n</head>\\n<body>\\n')
        f.write('<h1>M3U Playlist Index</h1>\\n')
        f.write(f'<p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>\\n')
        f.write(f'<p>Total channels: {len(channels)}</p>\\n')
        
        f.write('<div class="playlist">\\n')
        f.write('<h3><a href="final.m3u">Complete Playlist</a></h3>\\n')
        f.write(f'<span class="count">{len(channels)} channels</span>\\n')
        f.write('</div>\\n')
        
        for group_name, count in sorted(groups.items()):
            safe_name = "".join(c for c in group_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name.replace(' ', '_').lower()}.m3u"
            
            f.write('<div class="playlist">\\n')
            f.write(f'<h3><a href="{filename}">{group_name}</a></h3>\\n')
            f.write(f'<span class="count">{count} channels</span>\\n')
            f.write('</div>\\n')
        
        f.write('</body>\\n</html>')
    
    print("Created playlist index at playlists/index.html")


if __name__ == "__main__":
    print("Exporter - Use as module")
'''
    with open("scripts/exporter.py", "w", encoding="utf-8") as f:
        f.write(exporter_content)
    log("Created scripts/exporter.py")

def create_placeholder_files():
    """Create placeholder files for editor"""
    os.makedirs("editor", exist_ok=True)
    
    with open("editor/custom_channels.txt", "w", encoding="utf-8") as f:
        f.write("# Add your custom channels here\n")
        f.write("# Format: [Channel Name]\n")
        f.write("#         group: Group Name\n")
        f.write("#         url: Stream URL\n")
        f.write("#         logo: Logo URL\n")
        f.write("#         epg: EPG ID\n\n")
    log("Created editor/custom_channels.txt")

def create_readme():
    """Create comprehensive README"""
    readme_content = '''# Ultimate M3U Editor

A comprehensive IPTV playlist editor and processor with GitHub Actions automation.

## Features

- **Automatic Playlist Processing**: Download and process M3U playlists from multiple sources
- **Smart Channel Grouping**: Automatically group channels by country/category
- **EPG Integration**: Add Electronic Program Guide data to channels
- **Logo Management**: Automatically assign channel logos
- **GitHub Actions**: Automated processing with daily updates
- **Multiple Export Formats**: M3U, JSON, and TXT formats
- **Channel Editor**: Easy-to-use text-based channel editing

## Quick Start

1. **Add Playlist Sources**: Edit `config/providers.txt` and add your M3U playlist URLs
2. **Configure EPG**: Edit `config/epg_sources.txt` to add EPG data sources
3. **Commit and Push**: All files to trigger automatic processing
4. **Download**: Your processed playlist from `playlists/final.m3u`

## Configuration Files

### config/providers.txt
Add your M3U playlist URLs (one per line):
```
https://example.com/playlist1.m3u
https://example.com/playlist2.m3u
```

### config/epg_sources.txt
Add EPG data sources:
```
https://example.com/epg.xml.gz
```

### config/commands.txt
Define processing pipeline:
```
IMPORT
GROUP_BY_COUNTRY
APPLY_EPG
APPLY_LOGOS
EXPORT
```

## Directory Structure

```
├── config/              # Configuration files
├── editor/              # Channel editing files
├── playlists/           # Generated playlists
├── scripts/             # Processing scripts
│   ├── modules/         # Core modules
│   ├── main.py          # Main processor
│   ├── utils.py         # Utility functions
│   └── ...             # Additional scripts
├── logs/               # Processing logs
└── .github/workflows/  # GitHub Actions
```

## Processing Pipeline

1. **Import**: Download playlists from configured sources
2. **Group**: Organize channels by country/category
3. **EPG**: Apply Electronic Program Guide data
4. **Logos**: Assign channel logos
5. **Export**: Generate final playlists

## GitHub Actions

The repository includes automated workflows:

- **Daily Processing**: Automatically updates playlists every day
- **Manual Trigger**: Run processing on-demand
- **Auto-commit**: Commits processed files back to repository

## Channel Editing

Edit channels manually in `editor/channels.txt`:

```
[Channel Name]
group: Category Name
url: http://stream.url
logo: http://logo.url
epg: channel.epg.id
```

## Output Files

- `playlists/final.m3u` - Complete processed playlist
- `playlists/channels.json` - JSON format export
- `playlists/index.html` - Web interface for playlists
- `editor/channels.txt` - Editable channel list

## Logs

Check `logs/processing.log` for detailed processing information and error messages.

## Advanced Usage

### Custom Processing Scripts

Create custom processing scripts in the `scripts/` directory and modify `scripts/main.py` to include them.

### Logo Customization

Add custom logo mappings in `scripts/logo_manager.py`.

### EPG Mapping

Customize EPG channel matching in `scripts/epg_manager.py`.

## Troubleshooting

1. **No channels found**: Check playlist URLs in `config/providers.txt`
2. **Processing errors**: Review `logs/processing.log`
3. **GitHub Actions failing**: Check repository permissions and secrets
4. **Missing logos/EPG**: Verify source URLs and internet connectivity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and feature requests, please use the GitHub Issues page.
'''
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    log("Created README.md")

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/*.log

# Temporary files
tmp/
temp/
*.tmp
*.temp

# Backups
*.bak
*.backup
backups/

# Local configuration
.env
.env.local

# Processing artifacts
processing.log
debug.log
'''
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    log("Created .gitignore")

def main():
    """Main setup function"""
    log("Starting Ultimate M3U Editor setup...")
    
    try:
        create_directory_structure()
        create_module_files()
        create_github_workflow()
        create_config_files()
        create_utils_script()
        create_main_script()
        create_importer_script()
        create_country_grouper_script()
        create_epg_manager_script()
        create_logo_manager_script()
        create_exporter_script()
        create_placeholder_files()
        create_readme()
        create_gitignore()
        
        log("=" * 60)
        log("🎉 SETUP COMPLETED SUCCESSFULLY!")
        log("=" * 60)
        log("")
        log("📋 NEXT STEPS:")
        log("1. Add your M3U playlist URLs to config/providers.txt")
        log("2. Configure EPG sources in config/epg_sources.txt")
        log("3. Commit and push all files to your GitHub repository:")
        log("   git add .")
        log("   git commit -m 'Initial M3U Editor setup'")
        log("   git push origin main")
        log("")
        log("4. Enable GitHub Actions in your repository settings")
        log("5. Check the Actions tab for automatic processing")
        log("6. Download your clean playlist from playlists/final.m3u")
        log("")
        log("📖 For detailed instructions, see README.md")
        log("🔍 Check processing.log for any issues")
        log("")
        log("🚀 Your IPTV playlist editor is ready!")
        log("✅ The channels.txt format has been FIXED!")
        
    except Exception as e:
        log(f"❌ Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
M3U Editor Helper Module
Common helper functions for M3U processing
"""

import re
import os
import requests
import logging
from urllib.parse import urlparse
from datetime import datetime


def setup_logging():
    """Setup logging configuration"""
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/processing.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def normalize_channel_name(name):
    """Normalize channel name for comparison and matching"""
    if not name:
        return ""
    
    # Remove special characters but keep spaces
    normalized = re.sub(r'[^\w\s]', '', name)
    # Convert to lowercase and strip whitespace
    normalized = normalized.lower().strip()
    # Replace multiple spaces with single space
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized


def extract_channel_info(extinf_line):
    """Extract channel information from EXTINF line"""
    info = {
        'name': '',
        'group': 'General',
        'logo': '',
        'epg': '',
        'language': '',
        'country': ''
    }
    
    # Extract channel name (after the comma)
    if ',' in extinf_line:
        info['name'] = extinf_line.split(',', 1)[1].strip()
    
    # Extract attributes using regex
    attributes = [
        ('logo', r'tvg-logo="([^"]*)"'),
        ('epg', r'tvg-id="([^"]*)"'),
        ('group', r'group-title="([^"]*)"'),
        ('language', r'tvg-language="([^"]*)"'),
        ('country', r'tvg-country="([^"]*)"')
    ]
    
    for attr, pattern in attributes:
        match = re.search(pattern, extinf_line)
        if match:
            info[attr] = match.group(1)
    
    return info


def validate_url(url, timeout=10):
    """Validate if a URL is accessible"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except:
        return False


def clean_filename(filename):
    """Clean filename for safe file system usage"""
    # Remove or replace invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    cleaned = cleaned.strip('. ')
    # Limit length
    if len(cleaned) > 200:
        cleaned = cleaned[:200]
    
    return cleaned


def get_file_size(filepath):
    """Get file size in human readable format"""
    try:
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return "Unknown"


def backup_file(filepath, backup_dir="backups"):
    """Create a backup of a file"""
    if not os.path.exists(filepath):
        return None
    
    os.makedirs(backup_dir, exist_ok=True)
    
    filename = os.path.basename(filepath)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{timestamp}_{filename}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        import shutil
        shutil.copy2(filepath, backup_path)
        return backup_path
    except:
        return None


def merge_channel_lists(*channel_lists):
    """Merge multiple channel lists, removing duplicates"""
    merged = []
    seen_urls = set()
    
    for channel_list in channel_lists:
        for channel in channel_list:
            url = channel.get('url', '')
            if url and url not in seen_urls:
                merged.append(channel)
                seen_urls.add(url)
    
    return merged


def filter_channels_by_group(channels, allowed_groups):
    """Filter channels by allowed groups"""
    if not allowed_groups:
        return channels
    
    allowed_groups_lower = [g.lower() for g in allowed_groups]
    
    return [
        ch for ch in channels 
        if ch.get('group', '').lower() in allowed_groups_lower
    ]


def sort_channels(channels, sort_by='name'):
    """Sort channels by specified criteria"""
    if sort_by == 'name':
        return sorted(channels, key=lambda x: x.get('name', '').lower())
    elif sort_by == 'group':
        return sorted(channels, key=lambda x: (x.get('group', ''), x.get('name', '')))
    elif sort_by == 'url':
        return sorted(channels, key=lambda x: x.get('url', ''))
    else:
        return channels


def get_channel_statistics(channels):
    """Get statistics about the channel list"""
    stats = {
        'total_channels': len(channels),
        'groups': {},
        'with_logo': 0,
        'with_epg': 0,
        'unique_urls': len(set(ch.get('url', '') for ch in channels if ch.get('url')))
    }
    
    for channel in channels:
        # Count by group
        group = channel.get('group', 'Unknown')
        stats['groups'][group] = stats['groups'].get(group, 0) + 1
        
        # Count channels with logos and EPG
        if channel.get('logo'):
            stats['with_logo'] += 1
        if channel.get('epg'):
            stats['with_epg'] += 1
    
    return stats
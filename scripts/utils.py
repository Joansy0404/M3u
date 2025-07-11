#!/usr/bin/env python3
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
        f.write(log_message + "\n")


def normalize_name(name):
    """Normalize channel name for matching"""
    if not name:
        return ""
    return re.sub(r'[^\w\s]', '', name.lower()).strip()


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

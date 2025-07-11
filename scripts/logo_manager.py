#!/usr/bin/env python3
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

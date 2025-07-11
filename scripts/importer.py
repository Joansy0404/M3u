#!/usr/bin/env python3
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
        lines = content.split('\n')
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

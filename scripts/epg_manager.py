#!/usr/bin/env python3
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

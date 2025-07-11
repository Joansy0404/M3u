#!/usr/bin/env python3
"""
M3U Processor Module
Main processing logic for M3U playlist operations
"""

import requests
import re
import os
import logging
from urllib.parse import urlparse
from .helper import normalize_channel_name, extract_channel_info, validate_url


class M3UProcessor:
    """Main M3U processor class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.channels = []
        self.stats = {}
    
    def download_playlist(self, url, timeout=30):
        """Download M3U playlist from URL"""
        try:
            self.logger.info(f"Downloading playlist from: {url}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Error downloading playlist from {url}: {e}")
            return None
    
    def parse_m3u_content(self, content):
        """Parse M3U content and extract channel information"""
        channels = []
        lines = content.split('\n')
        current_channel = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF'):
                # Parse channel info from EXTINF line
                current_channel = extract_channel_info(line)
                
            elif line and not line.startswith('#') and current_channel:
                # This is the stream URL
                current_channel['url'] = line
                channels.append(current_channel)
                current_channel = None
        
        self.logger.info(f"Parsed {len(channels)} channels from M3U content")
        return channels
    
    def process_playlist_url(self, url):
        """Process a single playlist URL"""
        content = self.download_playlist(url)
        if content:
            return self.parse_m3u_content(content)
        return []
    
    def process_multiple_playlists(self, urls):
        """Process multiple playlist URLs"""
        all_channels = []
        
        for url in urls:
            channels = self.process_playlist_url(url)
            all_channels.extend(channels)
        
        # Remove duplicates based on URL
        unique_channels = []
        seen_urls = set()
        
        for channel in all_channels:
            url = channel.get('url', '')
            if url and url not in seen_urls:
                unique_channels.append(channel)
                seen_urls.add(url)
        
        self.channels = unique_channels
        self.logger.info(f"Processed {len(all_channels)} total channels, {len(unique_channels)} unique")
        return unique_channels
    
    def filter_working_streams(self, channels=None, timeout=10, max_checks=None):
        """Filter channels to only include working streams"""
        if channels is None:
            channels = self.channels
        
        working_channels = []
        checked = 0
        
        for channel in channels:
            if checked >= max_checks:
                self.logger.warning(f"Reached maximum check limit of {max_checks}")
                break
            
            url = channel.get('url', '')
            if url and validate_url(url, timeout):
                working_channels.append(channel)
                self.logger.debug(f"Working stream: {channel.get('name', 'Unknown')}")
            else:
                self.logger.debug(f"Non-working stream: {channel.get('name', 'Unknown')}")
            
            checked += 1
        
        self.logger.info(f"Found {len(working_channels)} working streams out of {checked} checked")
        return working_channels
    
    def group_channels_by_category(self, channels=None):
        """Group channels by category/group"""
        if channels is None:
            channels = self.channels
        
        grouped = {}
        
        for channel in channels:
            group = channel.get('group', 'General')
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(channel)
        
        return grouped
    
    def remove_duplicate_channels(self, channels=None):
        """Remove duplicate channels based on name and URL"""
        if channels is None:
            channels = self.channels
        
        unique_channels = []
        seen_combinations = set()
        
        for channel in channels:
            name = normalize_channel_name(channel.get('name', ''))
            url = channel.get('url', '')
            
            combination = (name, url)
            if combination not in seen_combinations:
                unique_channels.append(channel)
                seen_combinations.add(combination)
        
        self.logger.info(f"Removed {len(channels) - len(unique_channels)} duplicate channels")
        return unique_channels
    
    def enhance_channel_info(self, channels=None):
        """Enhance channel information with smart detection"""
        if channels is None:
            channels = self.channels
        
        enhanced = []
        
        for channel in channels:
            enhanced_channel = channel.copy()
            name = channel.get('name', '').lower()
            
            # Auto-detect country/group if not set
            if not enhanced_channel.get('group') or enhanced_channel['group'] == 'General':
                enhanced_channel['group'] = self._detect_channel_group(name)
            
            # Auto-detect language
            if not enhanced_channel.get('language'):
                enhanced_channel['language'] = self._detect_language(name)
            
            enhanced.append(enhanced_channel)
        
        return enhanced
    
    def _detect_channel_group(self, name):
        """Detect channel group from name"""
        name_lower = name.lower()
        
        # News channels
        if any(keyword in name_lower for keyword in ['news', 'cnn', 'bbc news', 'fox news']):
            return 'News'
        
        # Sports channels
        if any(keyword in name_lower for keyword in ['sport', 'espn', 'fox sports', 'sky sport']):
            return 'Sports'
        
        # Movies channels
        if any(keyword in name_lower for keyword in ['movie', 'cinema', 'film', 'hbo', 'starz']):
            return 'Movies'
        
        # Kids channels
        if any(keyword in name_lower for keyword in ['kids', 'cartoon', 'disney', 'nick']):
            return 'Kids'
        
        # Music channels
        if any(keyword in name_lower for keyword in ['music', 'mtv', 'vh1']):
            return 'Music'
        
        # Country-based detection
        if any(keyword in name_lower for keyword in ['usa', 'america', 'us ']):
            return 'US Channels'
        elif any(keyword in name_lower for keyword in ['uk', 'britain', 'british']):
            return 'UK Channels'
        elif any(keyword in name_lower for keyword in ['canada', 'canadian']):
            return 'Canadian Channels'
        
        return 'General'
    
    def _detect_language(self, name):
        """Detect language from channel name"""
        name_lower = name.lower()
        
        if any(keyword in name_lower for keyword in ['español', 'spanish', 'mexico', 'spain']):
            return 'Spanish'
        elif any(keyword in name_lower for keyword in ['français', 'french', 'france']):
            return 'French'
        elif any(keyword in name_lower for keyword in ['deutsch', 'german', 'germany']):
            return 'German'
        elif any(keyword in name_lower for keyword in ['italiano', 'italian', 'italy']):
            return 'Italian'
        elif any(keyword in name_lower for keyword in ['português', 'portuguese', 'brazil', 'portugal']):
            return 'Portuguese'
        
        return 'English'  # Default
    
    def export_to_m3u(self, channels, filepath):
        """Export channels to M3U format"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            
            for channel in channels:
                if channel.get('url') and channel.get('name'):
                    # Build EXTINF line
                    extinf = '#EXTINF:-1'
                    
                    if channel.get('epg'):
                        extinf += f' tvg-id="{channel["epg"]}"'
                    
                    if channel.get('logo'):
                        extinf += f' tvg-logo="{channel["logo"]}"'
                    
                    if channel.get('language'):
                        extinf += f' tvg-language="{channel["language"]}"'
                    
                    extinf += f' group-title="{channel.get("group", "General")}",{channel["name"]}'
                    
                    f.write(f'{extinf}\n')
                    f.write(f'{channel["url"]}\n')
        
        self.logger.info(f"Exported {len(channels)} channels to {filepath}")
    
    def get_processing_stats(self):
        """Get processing statistics"""
        return {
            'total_channels': len(self.channels),
            'groups': len(set(ch.get('group', 'General') for ch in self.channels)),
            'with_logos': len([ch for ch in self.channels if ch.get('logo')]),
            'with_epg': len([ch for ch in self.channels if ch.get('epg')]),
            'languages': len(set(ch.get('language', 'Unknown') for ch in self.channels))
        }

#!/usr/bin/env python3
"""
M3U Generator Module - Complete Working Implementation
Replace your scripts/modules/m3u_generator.py with this file
"""

import os
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class DefaultConfig:
    """Default configuration for M3U generation"""
    def __init__(self):
        self.output_format = "m3u"
        self.include_logos = True
        self.include_epg = True
        self.sort_channels = True
        self.group_channels = True
        self.validate_urls = True

class M3UGenerator:
    """M3U Generator that actually works and integrates with your system"""
    
    def __init__(self, config=None):
        self.config = config or DefaultConfig()
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'channels_processed': 0,
            'channels_skipped': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def generate(self, channels: List[Dict], output_path: str = "playlists/final.m3u", 
                epg_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Main method to generate M3U playlist
        
        Args:
            channels: List of channel dictionaries
            output_path: Output file path
            epg_url: Optional EPG URL for header
            
        Returns:
            Dictionary with generation results
        """
        self._reset_statistics()
        self.stats['start_time'] = datetime.now()
        
        try:
            self.logger.info(f"🎬 Starting M3U generation with {len(channels)} channels")
            
            # Validate and process channels
            valid_channels = self._validate_and_process_channels(channels)
            
            if not valid_channels:
                self.logger.error("❌ No valid channels to process")
                return self._create_error_result("No valid channels")
            
            # Sort channels if configured
            if self.config.sort_channels:
                valid_channels = self._sort_channels(valid_channels)
            
            # Build M3U content
            m3u_content = self._build_m3u_content(valid_channels, epg_url)
            
            # Write to file
            success = self._write_playlist_file(m3u_content, output_path)
            
            if success:
                # Verify the file
                verification_result = self._verify_m3u_file(output_path)
                
                self.stats['end_time'] = datetime.now()
                processing_time = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
                
                result = {
                    'success': True,
                    'output_path': output_path,
                    'channels_processed': self.stats['channels_processed'],
                    'channels_skipped': self.stats['channels_skipped'],
                    'errors': self.stats['errors'],
                    'processing_time': processing_time,
                    'verification': verification_result,
                    'file_size': os.path.getsize(output_path) if os.path.exists(output_path) else 0
                }
                
                self.logger.info(f"✅ M3U generation completed: {self.stats['channels_processed']} channels")
                return result
            else:
                return self._create_error_result("Failed to write M3U file")
                
        except Exception as e:
            self.logger.error(f"❌ Error generating M3U: {e}")
            return self._create_error_result(str(e))
    
    def _reset_statistics(self):
        """Reset processing statistics"""
        self.stats = {
            'channels_processed': 0,
            'channels_skipped': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _validate_and_process_channels(self, channels: List[Dict]) -> List[Dict]:
        """Validate and clean channel data"""
        valid_channels = []
        
        for i, channel in enumerate(channels):
            try:
                processed_channel = self._process_single_channel(channel, i)
                if processed_channel:
                    valid_channels.append(processed_channel)
                    self.stats['channels_processed'] += 1
                else:
                    self.stats['channels_skipped'] += 1
                    
            except Exception as e:
                self.logger.warning(f"Error processing channel {i}: {e}")
                self.stats['errors'] += 1
        
        return valid_channels
    
    def _process_single_channel(self, channel: Dict, index: int) -> Optional[Dict]:
        """Process and validate a single channel"""
        try:
            # Extract basic info with multiple possible field names
            name = (channel.get('name') or 
                   channel.get('Channel Name') or 
                   channel.get('Name') or 
                   f'Channel {index + 1}')
            
            url = (channel.get('url') or 
                  channel.get('Stream URL') or 
                  channel.get('URL') or '')
            
            group = (channel.get('group') or 
                    channel.get('Group') or 
                    channel.get('group_title') or 
                    'General')
            
            # Validate required fields
            if not url or not url.strip():
                self.logger.debug(f"Skipping channel {name}: No URL")
                return None
            
            if not self._is_valid_url(url):
                self.logger.debug(f"Skipping channel {name}: Invalid URL format")
                return None
            
            # Clean and format data
            cleaned_channel = {
                'name': self._clean_channel_name(name),
                'url': self._clean_url(url),
                'group': self._clean_group_name(group),
                'logo': self._clean_logo_url(channel.get('logo', '') or 
                                           channel.get('Logo', '') or 
                                           channel.get('tvg-logo', '')),
                'epg_id': self._clean_epg_id(channel.get('epg', '') or 
                                           channel.get('EPG', '') or 
                                           channel.get('tvg-id', ''))
            }
            
            return cleaned_channel
            
        except Exception as e:
            self.logger.warning(f"Error processing channel at index {index}: {e}")
            return None
    
    def _clean_channel_name(self, name: str) -> str:
        """Clean channel name"""
        if not name:
            return "Unknown Channel"
        # Remove problematic characters
        name = re.sub(r'["\r\n\t]', '', str(name))
        return name.strip()
    
    def _clean_url(self, url: str) -> str:
        """Clean stream URL"""
        return str(url).strip()
    
    def _clean_group_name(self, group: str) -> str:
        """Clean group name"""
        if not group:
            return "General"
        # Remove problematic characters
        group = re.sub(r'["\r\n\t]', '', str(group))
        return group.strip()
    
    def _clean_logo_url(self, logo: str) -> str:
        """Clean logo URL"""
        return str(logo).strip() if logo else ""
    
    def _clean_epg_id(self, epg_id: str) -> str:
        """Clean EPG ID"""
        return str(epg_id).strip() if epg_id else ""
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        if not url:
            return False
        
        url = url.strip().lower()
        valid_schemes = ['http://', 'https://', 'rtmp://', 'rtmps://', 'udp://', 'rtp://']
        
        return any(url.startswith(scheme) for scheme in valid_schemes)
    
    def _sort_channels(self, channels: List[Dict]) -> List[Dict]:
        """Sort channels by group and name"""
        try:
            return sorted(channels, key=lambda x: (x['group'].lower(), x['name'].lower()))
        except Exception as e:
            self.logger.warning(f"Error sorting channels: {e}")
            return channels
    
    def _build_m3u_content(self, channels: List[Dict], epg_url: Optional[str] = None) -> str:
        """Build complete M3U content string"""
        content_lines = []
        
        # Add M3U header
        if epg_url:
            content_lines.append(f'#EXTM3U url-tvg="{epg_url}"')
        else:
            content_lines.append('#EXTM3U')
        
        # Process each channel
        for channel in channels:
            try:
                # Build EXTINF line
                extinf_line = '#EXTINF:-1'
                
                # Add EPG ID if available
                if channel['epg_id']:
                    extinf_line += f' tvg-id="{channel["epg_id"]}"'
                
                # Add logo if available
                if channel['logo']:
                    extinf_line += f' tvg-logo="{channel["logo"]}"'
                
                # Add group
                extinf_line += f' group-title="{channel["group"]}"'
                
                # Add channel name
                extinf_line += f',{channel["name"]}'
                
                # Add EXTINF and URL
                content_lines.append(extinf_line)
                content_lines.append(channel['url'])
                
            except Exception as e:
                self.logger.warning(f"Error building content for channel {channel.get('name', 'Unknown')}: {e}")
                continue
        
        return '\n'.join(content_lines)
    
    def _write_playlist_file(self, content: str, output_path: str) -> bool:
        """Write M3U content to file"""
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Write file with UTF-8 encoding
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"📁 M3U file written to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing M3U file: {e}")
            return False
    
    def _verify_m3u_file(self, file_path: str) -> Dict[str, Any]:
        """Verify the generated M3U file"""
        try:
            if not os.path.exists(file_path):
                return {'valid': False, 'error': 'File does not exist'}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return {'valid': False, 'error': 'File is empty'}
            
            # Check for M3U header
            first_line = lines[0].strip()
            if not first_line.startswith('#EXTM3U'):
                return {'valid': False, 'error': 'Missing #EXTM3U header'}
            
            # Count EXTINF and URL lines
            extinf_count = sum(1 for line in lines if line.strip().startswith('#EXTINF'))
            url_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
            url_count = len(url_lines)
            
            if extinf_count != url_count:
                return {
                    'valid': False, 
                    'error': f'Structure mismatch: {extinf_count} EXTINF vs {url_count} URLs'
                }
            
            # Verify URLs
            invalid_urls = []
            for url in url_lines[:5]:  # Check first 5 URLs
                if not self._is_valid_url(url):
                    invalid_urls.append(url[:50])
            
            return {
                'valid': True,
                'extinf_count': extinf_count,
                'url_count': url_count,
                'total_lines': len(lines),
                'file_size': os.path.getsize(file_path),
                'invalid_urls': invalid_urls[:3]  # Show max 3 invalid URLs
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Verification error: {e}'}
    
    def _create_empty_playlist(self, output_path: str, reason: str = "No channels") -> Dict[str, Any]:
        """Create an empty but valid M3U playlist"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('#EXTM3U\n')
                f.write(f'# Empty playlist - {reason}\n')
            
            return {
                'success': True,
                'output_path': output_path,
                'channels_processed': 0,
                'empty': True,
                'reason': reason
            }
            
        except Exception as e:
            return self._create_error_result(f"Failed to create empty playlist: {e}")
    
    def _create_backup(self, file_path: str) -> bool:
        """Create backup of existing file"""
        try:
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(file_path, backup_path)
                self.logger.info(f"📋 Created backup: {backup_path}")
                return True
            return True
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {e}")
            return False
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result dictionary"""
        return {
            'success': False,
            'error': error_message,
            'channels_processed': self.stats['channels_processed'],
            'channels_skipped': self.stats['channels_skipped'],
            'errors': self.stats['errors']
        }
    
    def validate_m3u_structure(self, file_path: str) -> Dict[str, Any]:
        """Public method to validate M3U file structure"""
        return self._verify_m3u_file(file_path)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return self.stats.copy()
    
    def get_playlist_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a playlist file"""
        try:
            if not os.path.exists(file_path):
                return {'exists': False}
            
            verification = self._verify_m3u_file(file_path)
            
            return {
                'exists': True,
                'file_size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                'verification': verification
            }
            
        except Exception as e:
            return {'exists': False, 'error': str(e)}


# Legacy function for backward compatibility
def generate_m3u(channels=None, output_file="playlists/final.m3u", epg_url=None):
    """
    Legacy function - now uses the proper M3UGenerator class
    This ensures existing code continues to work
    """
    if channels is None:
        channels = []
    
    generator = M3UGenerator()
    result = generator.generate(channels, output_file, epg_url)
    
    return result['success'] if 'success' in result else False


# Main execution for testing
if __name__ == "__main__":
    # Test the generator
    test_channels = [
        {
            'name': 'Test Channel 1',
            'url': 'http://example.com/stream1.m3u8',
            'group': 'Test',
            'logo': 'http://example.com/logo1.png',
            'epg_id': 'test1'
        },
        {
            'name': 'Test Channel 2', 
            'url': 'http://example.com/stream2.m3u8',
            'group': 'Test',
            'logo': '',
            'epg_id': ''
        }
    ]
    
    generator = M3UGenerator()
    result = generator.generate(test_channels, "test_output.m3u")
    
    print("🧪 Test Results:")
    print(f"Success: {result.get('success', False)}")
    print(f"Channels: {result.get('channels_processed', 0)}")
    print(f"Output: {result.get('output_path', 'N/A')}")
    
    if result.get('verification'):
        print(f"Verification: {result['verification']['valid']}")

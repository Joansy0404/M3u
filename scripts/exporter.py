#!/usr/bin/env python3
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
        f.write('#EXTM3U\n')
        
        for channel in channels:
            if channel.get('url') and channel.get('name'):
                # Build EXTINF line
                extinf = '#EXTINF:-1'
                
                if channel.get('epg'):
                    extinf += f' tvg-id="{channel["epg"]}"'
                
                if channel.get('logo'):
                    extinf += f' tvg-logo="{channel["logo"]}"'
                
                extinf += f' group-title="{channel.get("group", "General")}",{channel["name"]}'
                
                f.write(f'{extinf}\n')
                f.write(f'{channel["url"]}\n')
    
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
        f.write(f"# Channel List - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total channels: {len(channels)}\n\n")
        
        current_group = ""
        for channel in sorted(channels, key=lambda x: (x.get('group', ''), x.get('name', ''))):
            group = channel.get('group', 'General')
            
            if group != current_group:
                f.write(f"\n## {group}\n")
                f.write("=" * (len(group) + 3) + "\n")
                current_group = group
            
            f.write(f"- {channel.get('name', 'Unknown')}\n")
            if channel.get('url'):
                f.write(f"  URL: {channel['url']}\n")
            if channel.get('logo'):
                f.write(f"  Logo: {channel['logo']}\n")
            if channel.get('epg'):
                f.write(f"  EPG: {channel['epg']}\n")
            f.write("\n")
    
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
        f.write('<!DOCTYPE html>\n')
        f.write('<html>\n<head>\n')
        f.write('<title>M3U Playlist Index</title>\n')
        f.write('<style>\n')
        f.write('body { font-family: Arial, sans-serif; margin: 40px; }\n')
        f.write('h1 { color: #333; }\n')
        f.write('.playlist { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }\n')
        f.write('.count { color: #666; font-size: 0.9em; }\n')
        f.write('</style>\n</head>\n<body>\n')
        f.write('<h1>M3U Playlist Index</h1>\n')
        f.write(f'<p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>\n')
        f.write(f'<p>Total channels: {len(channels)}</p>\n')
        
        f.write('<div class="playlist">\n')
        f.write('<h3><a href="final.m3u">Complete Playlist</a></h3>\n')
        f.write(f'<span class="count">{len(channels)} channels</span>\n')
        f.write('</div>\n')
        
        for group_name, count in sorted(groups.items()):
            safe_name = "".join(c for c in group_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name.replace(' ', '_').lower()}.m3u"
            
            f.write('<div class="playlist">\n')
            f.write(f'<h3><a href="{filename}">{group_name}</a></h3>\n')
            f.write(f'<span class="count">{count} channels</span>\n')
            f.write('</div>\n')
        
        f.write('</body>\n</html>')
    
    print("Created playlist index at playlists/index.html")


if __name__ == "__main__":
    print("Exporter - Use as module")

#!/usr/bin/env python3
"""
M3U Country Grouper - Fixed Version
Groups channels by country based on various detection methods
No external dependencies required
"""

import re


# Built-in country mapping to avoid pycountry dependency
COUNTRY_MAP = {
    'US': 'United States',
    'GB': 'United Kingdom', 
    'FR': 'France',
    'DE': 'Germany',
    'IT': 'Italy',
    'ES': 'Spain',
    'PT': 'Portugal',
    'NL': 'Netherlands',
    'BE': 'Belgium',
    'SE': 'Sweden',
    'NO': 'Norway',
    'DK': 'Denmark',
    'FI': 'Finland',
    'PL': 'Poland',
    'RU': 'Russia',
    'TR': 'Turkey',
    'GR': 'Greece',
    'IN': 'India',
    'CN': 'China',
    'JP': 'Japan',
    'KR': 'South Korea',
    'AU': 'Australia',
    'CA': 'Canada',
    'BR': 'Brazil',
    'MX': 'Mexico',
    'AR': 'Argentina',
    'AL': 'Albania'
}


def detect_country_from_channel(channel_info):
    """Detect country from channel information"""
    name = channel_info.get('name', '').lower()
    group = channel_info.get('group', '').lower()
    url = channel_info.get('url', '').lower()
    
    # Country patterns - enhanced for Albania
    country_patterns = {
        'AL': ['albania', 'albanian', 'tirana', 'rtk', 'tv klan', 'top channel'],
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
    for country_code in COUNTRY_MAP.keys():
        if country_code.lower() in all_text:
            return country_code
    
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
            country_name = COUNTRY_MAP.get(country, country)
            channel['group'] = f"{country_name} Channels"
        
        grouped[country].append(channel)
    
    return grouped


if __name__ == "__main__":
    print("Country Grouper - Use as module")

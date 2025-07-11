"""Country detection and grouping functionality"""

try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False

import re
from typing import Optional, Dict, List

class CountryGrouper:
    def __init__(self):
        self.country_patterns = {
            'US': [r'\b(usa?|united states|american?)\b', r'\bus\b'],
            'UK': [r'\b(uk|united kingdom|british?)\b', r'\bgb\b'],
            'CA': [r'\b(canada|canadian?)\b', r'\bca\b'],
            'DE': [r'\b(germany|german|deutschland)\b', r'\bde\b'],
            'FR': [r'\b(france|french|français)\b', r'\bfr\b'],
            'ES': [r'\b(spain|spanish|españa)\b', r'\bes\b'],
            'IT': [r'\b(italy|italian|italia)\b', r'\bit\b'],
            'BR': [r'\b(brazil|brazilian|brasil)\b', r'\bbr\b'],
            'MX': [r'\b(mexico|mexican|méxico)\b', r'\bmx\b'],
            'IN': [r'\b(india|indian)\b', r'\bin\b'],
            'AU': [r'\b(australia|australian|aussie)\b', r'\bau\b'],
            'NL': [r'\b(netherlands|dutch|holland)\b', r'\bnl\b'],
            'TR': [r'\b(turkey|turkish|türkiye)\b', r'\btr\b'],
            'AR': [r'\b(argentina|argentinian)\b', r'\bar\b'],
            'RU': [r'\b(russia|russian)\b', r'\bru\b'],
            'HR': [r'\b(croatia|croatian|hrvatska)\b', r'\bhr\b']
        }

    def detect_country(self, name: str, group: str = "") -> Optional[str]:
        """Detect country from channel name and group"""
        text = f"{name} {group}".lower()
        
        for country_code, patterns in self.country_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return country_code
        
        return None

    def group_by_country(self, channels: List[Dict]) -> Dict[str, List[Dict]]:
        """Group channels by detected country"""
        groups = {}
        
        for channel in channels:
            country = self.detect_country(
                channel.get('name', ''),
                channel.get('group', '')
            )
            
            if not country:
                country = 'Unknown'
            
            if country not in groups:
                groups[country] = []
            
            groups[country].append(channel)
        
        return groups

def detect_country_from_text(text: str) -> Optional[str]:
    """Standalone function for country detection"""
    grouper = CountryGrouper()
    return grouper.detect_country(text)

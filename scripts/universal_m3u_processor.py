#!/usr/bin/env python3
"""
Universal M3U Processor - Complete System
Handles all M3U formats, provides comprehensive processing capabilities
"""

import os
import re
import json
import logging
import asyncio
import aiohttp
import hashlib
import time
from typing import Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urlparse
import unicodedata
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET

# Import our universal components
from universal_m3u_parser import UniversalM3UParser, ParsedChannel, M3UFormat
from comprehensive_validator import ComprehensiveM3UValidator, ValidationLevel

class ProcessingMode(Enum):
    """Processing operation modes"""
    IMPORT = "import"
    CLEAN = "clean"
    VALIDATE = "validate"
    DEDUPLICATE = "deduplicate"
    CATEGORIZE = "categorize"
    EXPORT = "export"
    FULL_PIPELINE = "full_pipeline"

@dataclass
class ProcessingConfig:
    """Configuration for M3U processing"""
    # Input/Output
    input_file: str = ""
    output_file: str = "processed_playlist.m3u"
    backup_enabled: bool = True
    
    # Processing options
    strict_validation: bool = False
    remove_duplicates: bool = True
    auto_categorize: bool = True
    test_connectivity: bool = False
    fix_encoding: bool = True
    
    # Duplicate detection
    duplicate_detection_method: str = "url_similarity"  # url_exact, url_similarity, name_similarity, metadata
    similarity_threshold: float = 0.85
    
    # Categorization
    auto_detect_countries: bool = True
    auto_detect_quality: bool = True
    normalize_groups: bool = True
    
    # URL validation
    validate_url_format: bool = True
    test_stream_health: bool = False
    timeout_seconds: int = 10
    max_concurrent_tests: int = 20
    
    # Output format
    output_format: str = "m3u"  # m3u, json, csv, txt
    include_metadata: bool = True
    generate_stats: bool = True
    
    # Filtering
    min_name_length: int = 1
    max_name_length: int = 200
    blocked_domains: List[str] = None
    required_protocols: List[str] = None
    
    def __post_init__(self):
        if self.blocked_domains is None:
            self.blocked_domains = ['example.com', 'test.com', 'localhost']
        if self.required_protocols is None:
            self.required_protocols = ['http://', 'https://', 'rtmp://', 'rtmps://']

@dataclass
class ProcessingStats:
    """Statistics from processing operation"""
    input_channels: int = 0
    output_channels: int = 0
    channels_removed: int = 0
    duplicates_found: int = 0
    invalid_urls: int = 0
    encoding_fixes: int = 0
    categorization_updates: int = 0
    processing_time: float = 0.0
    format_detected: str = ""
    quality_score: float = 0.0
    
    def efficiency_ratio(self) -> float:
        return (self.output_channels / max(1, self.input_channels)) * 100

class UniversalM3UProcessor:
    """
    Complete M3U processing system with universal format support
    """
    
    def __init__(self, config: ProcessingConfig = None, logger: logging.Logger = None):
        self.config = config or ProcessingConfig()
        self.logger = logger or self._setup_logging()
        
        # Initialize components
        self.parser = UniversalM3UParser(self.logger)
        self.validator = ComprehensiveM3UValidator(self.logger)
        
        # Processing state
        self.stats = ProcessingStats()
        self.processed_channels: List[ParsedChannel] = []
        self.duplicate_groups: List[List[int]] = []
        
        # Categorization patterns
        self.country_patterns = self._load_country_patterns()
        self.quality_patterns = self._load_quality_patterns()
        self.genre_patterns = self._load_genre_patterns()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('M3UProcessor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def process_file(self, input_file: str, mode: ProcessingMode = ProcessingMode.FULL_PIPELINE) -> ProcessingStats:
        """
        Process M3U file with specified mode
        
        Args:
            input_file: Path to input M3U file
            mode: Processing mode to execute
            
        Returns:
            Processing statistics
        """
        start_time = time.time()
        self.config.input_file = input_file
        
        try:
            self.logger.info(f"Starting {mode.value} processing for {input_file}")
            
            # Create backup if enabled
            if self.config.backup_enabled:
                self._create_backup(input_file)
            
            # Parse input file
            channels = await self._parse_input_file(input_file)
            self.stats.input_channels = len(channels)
            self.stats.format_detected = self.parser.last_format_detected if hasattr(self.parser, 'last_format_detected') else "unknown"
            
            # Execute processing based on mode
            if mode == ProcessingMode.IMPORT:
                self.processed_channels = await self._import_channels(channels)
            elif mode == ProcessingMode.CLEAN:
                self.processed_channels = await self._clean_channels(channels)
            elif mode == ProcessingMode.VALIDATE:
                await self._validate_channels(channels)
                self.processed_channels = channels
            elif mode == ProcessingMode.DEDUPLICATE:
                self.processed_channels = await self._deduplicate_channels(channels)
            elif mode == ProcessingMode.CATEGORIZE:
                self.processed_channels = await self._categorize_channels(channels)
            elif mode == ProcessingMode.EXPORT:
                await self._export_channels(channels)
                self.processed_channels = channels
            elif mode == ProcessingMode.FULL_PIPELINE:
                self.processed_channels = await self._full_pipeline(channels)
            
            self.stats.output_channels = len(self.processed_channels)
            self.stats.channels_removed = self.stats.input_channels - self.stats.output_channels
            self.stats.processing_time = time.time() - start_time
            
            # Generate output
            if mode != ProcessingMode.VALIDATE:
                await self._generate_output()
            
            # Generate statistics if enabled
            if self.config.generate_stats:
                await self._generate_statistics_report()
            
            self.logger.info(f"Processing completed: {self.stats.output_channels}/{self.stats.input_channels} channels retained")
            return self.stats
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            raise
    
    async def _parse_input_file(self, input_file: str) -> List[ParsedChannel]:
        """Parse input file using universal parser"""
        try:
            with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Handle encoding issues
            if self.config.fix_encoding:
                content = self._fix_encoding_issues(content)
            
            parse_result = self.parser.parse_content(content, self.config.strict_validation)
            
            # Store format info
            if hasattr(self.parser, 'last_format_detected'):
                self.parser.last_format_detected = parse_result.format_detected.value
            
            # Log parsing results
            self.logger.info(f"Parsed {len(parse_result.channels)} channels from {parse_result.format_detected.value} format")
            if parse_result.errors:
                self.logger.warning(f"Parsing errors: {len(parse_result.errors)}")
            if parse_result.warnings:
                self.logger.info(f"Parsing warnings: {len(parse_result.warnings)}")
            
            return parse_result.channels
            
        except Exception as e:
            self.logger.error(f"Failed to parse input file: {e}")
            raise
    
    async def _import_channels(self, channels: List[ParsedChannel]) -> List[ParsedChannel]:
        """Import and basic processing of channels"""
        imported = []
        
        for channel in channels:
            # Basic validation
            if self._is_channel_valid_for_import(channel):
                imported.append(channel)
            else:
                self.logger.debug(f"Skipped invalid channel: {channel.name}")
        
        self.logger.info(f"Imported {len(imported)}/{len(channels)} channels")
        return imported
    
    async def _clean_channels(self, channels: List[ParsedChannel]) -> List[ParsedChannel]:
        """Clean and normalize channel data"""
        cleaned = []
        
        for channel in channels:
            # Create cleaned copy
            clean_channel = ParsedChannel(
                name=self._clean_channel_name(channel.name),
                url=self._clean_url(channel.url),
                group=self._clean_group_name(channel.group),
                logo=self._clean_logo_url(channel.logo),
                epg_id=self._clean_epg_id(channel.epg_id),
                country=channel.country,
                language=channel.language,
                quality=channel.quality,
                duration=channel.duration,
                attributes=channel.attributes.copy() if channel.attributes else {}
            )
            
            # Apply cleaning rules
            if self._is_channel_valid_after_cleaning(clean_channel):
                cleaned.append(clean_channel)
                if clean_channel.name != channel.name or clean_channel.group != channel.group:
                    self.stats.encoding_fixes += 1
            
        self.logger.info(f"Cleaned {len(cleaned)}/{len(channels)} channels")
        return cleaned
    
    async def _validate_channels(self, channels: List[ParsedChannel]) -> None:
        """Validate channels using comprehensive validator"""
        # Create temporary file for validation
        temp_file = "temp_validation.m3u"
        await self._write_m3u_file(channels, temp_file)
        
        try:
            validation_level = ValidationLevel.DEEP if self.config.test_connectivity else ValidationLevel.ADVANCED
            report = await self.validator.validate_file(temp_file, validation_level)
            
            self.stats.quality_score = report.quality_score
            
            # Log validation results
            self.logger.info(f"Validation completed - Quality Score: {report.quality_score}/100")
            self.logger.info(f"Issues found: {len(report.issues)}")
            
            for issue in report.issues:
                if issue.type.value == 'error':
                    self.logger.error(f"Validation error: {issue.message}")
                elif issue.type.value == 'warning':
                    self.logger.warning(f"Validation warning: {issue.message}")
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    async def _deduplicate_channels(self, channels: List[ParsedChannel]) -> List[ParsedChannel]:
        """Remove duplicate channels"""
        if not self.config.remove_duplicates:
            return channels
        
        duplicates_removed = 0
        seen_signatures = set()
        unique_channels = []
        
        for channel in channels:
            signature = self._generate_channel_signature(channel)
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_channels.append(channel)
            else:
                duplicates_removed += 1
                self.logger.debug(f"Removed duplicate: {channel.name}")
        
        self.stats.duplicates_found = duplicates_removed
        self.logger.info(f"Removed {duplicates_removed} duplicate channels")
        return unique_channels
    
    async def _categorize_channels(self, channels: List[ParsedChannel]) -> List[ParsedChannel]:
        """Auto-categorize channels by country, quality, genre"""
        categorized = []
        
        for channel in channels:
            updated_channel = ParsedChannel(
                name=channel.name,
                url=channel.url,
                group=channel.group,
                logo=channel.logo,
                epg_id=channel.epg_id,
                country=channel.country,
                language=channel.language,
                quality=channel.quality,
                duration=channel.duration,
                attributes=channel.attributes.copy() if channel.attributes else {}
            )
            
            # Auto-detect country
            if self.config.auto_detect_countries and not updated_channel.country:
                detected_country = self._detect_country_from_text(f"{channel.name} {channel.group}")
                if detected_country:
                    updated_channel.country = detected_country
                    self.stats.categorization_updates += 1
            
            # Auto-detect quality
            if self.config.auto_detect_quality and not updated_channel.quality:
                detected_quality = self._detect_quality_from_text(f"{channel.name} {channel.group}")
                if detected_quality:
                    updated_channel.quality = detected_quality
            
            # Update group based on country if enabled
            if self.config.normalize_groups and updated_channel.country:
                if updated_channel.group in ['General', 'Uncategorized', '']:
                    updated_channel.group = self._get_country_group_name(updated_channel.country)
                    self.stats.categorization_updates += 1
            
            categorized.append(updated_channel)
        
        self.logger.info(f"Applied {self.stats.categorization_updates} categorization updates")
        return categorized
    
    async def _full_pipeline(self, channels: List[ParsedChannel]) -> List[ParsedChannel]:
        """Execute full processing pipeline"""
        self.logger.info("Executing full processing pipeline")
        
        # Step 1: Import and basic validation
        channels = await self._import_channels(channels)
        
        # Step 2: Clean data
        channels = await self._clean_channels(channels)
        
        # Step 3: Remove duplicates
        channels = await self._deduplicate_channels(channels)
        
        # Step 4: Auto-categorize
        channels = await self._categorize_channels(channels)
        
        # Step 5: Validate final result
        await self._validate_channels(channels)
        
        # Step 6: Test connectivity if enabled
        if self.config.test_stream_health:
            channels = await self._test_stream_connectivity(channels)
        
        return channels
    
    async def _test_stream_connectivity(self, channels: List[ParsedChannel]) -> List[ParsedChannel]:
        """Test stream connectivity and filter accessible channels"""
        if not channels:
            return channels
        
        self.logger.info(f"Testing connectivity for {len(channels)} channels...")
        
        # Limit concurrent tests
        semaphore = asyncio.Semaphore(self.config.max_concurrent_tests)
        accessible_channels = []
        
        async def test_channel(channel):
            async with semaphore:
                try:
                    timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.head(channel.url, allow_redirects=True) as response:
                            if 200 <= response.status < 400:
                                return channel
                            else:
                                self.logger.debug(f"Channel inaccessible: {channel.name} (Status: {response.status})")
                                return None
                except Exception as e:
                    self.logger.debug(f"Channel test failed: {channel.name} ({e})")
                    return None
        
        # Test all channels concurrently
        tasks = [test_channel(channel) for channel in channels]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect accessible channels
        for result in results:
            if isinstance(result, ParsedChannel):
                accessible_channels.append(result)
        
        removed_count = len(channels) - len(accessible_channels)
        self.logger.info(f"Connectivity test: {len(accessible_channels)}/{len(channels)} channels accessible ({removed_count} removed)")
        
        return accessible_channels
    
    async def _generate_output(self):
        """Generate output file in specified format"""
        if not self.processed_channels:
            self.logger.warning("No channels to export")
            return
        
        output_path = self.config.output_file
        
        if self.config.output_format.lower() == 'json':
            await self._write_json_file(self.processed_channels, output_path)
        elif self.config.output_format.lower() == 'csv':
            await self._write_csv_file(self.processed_channels, output_path)
        elif self.config.output_format.lower() == 'txt':
            await self._write_txt_file(self.processed_channels, output_path)
        else:  # Default to M3U
            await self._write_m3u_file(self.processed_channels, output_path)
        
        self.logger.info(f"Output written to {output_path}")
    
    async def _write_m3u_file(self, channels: List[ParsedChannel], output_path: str):
        """Write channels to M3U format"""
        lines = ["#EXTM3U"]
        
        for channel in channels:
            # Build EXTINF line
            extinf_parts = ["#EXTINF:-1"]
            
            # Add attributes
            if channel.epg_id:
                extinf_parts.append(f'tvg-id="{channel.epg_id}"')
            if channel.logo:
                extinf_parts.append(f'tvg-logo="{channel.logo}"')
            if channel.group and channel.group != 'General':
                extinf_parts.append(f'group-title="{channel.group}"')
            if channel.country:
                extinf_parts.append(f'tvg-country="{channel.country}"')
            if channel.language:
                extinf_parts.append(f'tvg-language="{channel.language}"')
            
            # Add name
            extinf_line = " ".join(extinf_parts) + f",{channel.name}"
            
            lines.append(extinf_line)
            lines.append(channel.url)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    async def _write_json_file(self, channels: List[ParsedChannel], output_path: str):
        """Write channels to JSON format"""
        channel_dicts = [asdict(channel) for channel in channels]
        
        output_data = {
            "metadata": {
                "total_channels": len(channels),
                "generated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "format": "json",
                "processor": "UniversalM3UProcessor"
            },
            "channels": channel_dicts
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    async def _write_csv_file(self, channels: List[ParsedChannel], output_path: str):
        """Write channels to CSV format"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['name', 'url', 'group', 'logo', 'epg_id', 'country', 'language', 'quality']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for channel in channels:
                writer.writerow({
                    'name': channel.name,
                    'url': channel.url,
                    'group': channel.group,
                    'logo': channel.logo,
                    'epg_id': channel.epg_id,
                    'country': channel.country,
                    'language': channel.language,
                    'quality': channel.quality
                })
    
    async def _write_txt_file(self, channels: List[ParsedChannel], output_path: str):
        """Write channels to simple text format"""
        lines = []
        
        for channel in channels:
            lines.append(f"Name: {channel.name}")
            lines.append(f"URL: {channel.url}")
            lines.append(f"Group: {channel.group}")
            if channel.logo:
                lines.append(f"Logo: {channel.logo}")
            if channel.epg_id:
                lines.append(f"EPG ID: {channel.epg_id}")
            if channel.country:
                lines.append(f"Country: {channel.country}")
            lines.append("")  # Empty line between channels
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    async def _generate_statistics_report(self):
        """Generate detailed statistics report"""
        report_data = {
            "processing_summary": asdict(self.stats),
            "channel_analysis": {
                "by_group": self._analyze_by_group(),
                "by_country": self._analyze_by_country(),
                "by_quality": self._analyze_by_quality(),
                "url_protocols": self._analyze_url_protocols()
            },
            "quality_metrics": {
                "efficiency_ratio": self.stats.efficiency_ratio(),
                "duplicate_ratio": (self.stats.duplicates_found / max(1, self.stats.input_channels)) * 100,
                "invalid_url_ratio": (self.stats.invalid_urls / max(1, self.stats.input_channels)) * 100
            }
        }
        
        # Write report
        report_path = self.config.output_file.replace('.m3u', '_stats.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Statistics report written to {report_path}")
    
    def _create_backup(self, input_file: str):
        """Create backup of input file"""
        import shutil
        backup_path = f"{input_file}.backup.{int(time.time())}"
        shutil.copy2(input_file, backup_path)
        self.logger.info(f"Backup created: {backup_path}")
    
    def _fix_encoding_issues(self, content: str) -> str:
        """Fix common encoding issues"""
        # Handle BOM
        if content.startswith('\ufeff'):
            content = content[1:]
            self.stats.encoding_fixes += 1
        
        # Normalize Unicode
        content = unicodedata.normalize('NFC', content)
        
        # Fix line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        return content
    
    def _is_channel_valid_for_import(self, channel: ParsedChannel) -> bool:
        """Check if channel is valid for import"""
        # Check required fields
        if not channel.name or not channel.name.strip():
            return False
        if not channel.url or not channel.url.strip():
            return False
        
        # Check name length
        name_len = len(channel.name.strip())
        if name_len < self.config.min_name_length or name_len > self.config.max_name_length:
            return False
        
        # Check URL protocol
        url_lower = channel.url.lower()
        if not any(url_lower.startswith(protocol) for protocol in self.config.required_protocols):
            self.stats.invalid_urls += 1
            return False
        
        # Check blocked domains
        parsed_url = urlparse(channel.url)
        if any(blocked in parsed_url.netloc.lower() for blocked in self.config.blocked_domains):
            return False
        
        return True
    
    def _is_channel_valid_after_cleaning(self, channel: ParsedChannel) -> bool:
        """Check if channel is valid after cleaning"""
        return (channel.name and 
                channel.name.strip() and 
                channel.url and 
                channel.url.strip() and
                len(channel.name.strip()) >= self.config.min_name_length)
    
    def _clean_channel_name(self, name: str) -> str:
        """Clean and normalize channel name"""
        if not name:
            return "Unnamed Channel"
        
        # Remove EXTINF artifacts
        name = re.sub(r'tvg-[^=]*="[^"]*"', '', name)
        name = re.sub(r'group-title="[^"]*"', '', name)
        name = re.sub(r'radio="[^"]*"', '', name)
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove leading/trailing punctuation
        name = name.strip('.,;:-_|')
        
        # Remove HTML entities
        name = re.sub(r'&[a-zA-Z0-9#]+;', '', name)
        
        if not name:
            return "Unnamed Channel"
        
        return name
    
    def _clean_url(self, url: str) -> str:
        """Clean and normalize URL"""
        if not url:
            return ""
        
        # Basic cleaning
        url = url.strip()
        
        # Remove common URL artifacts
        url = re.sub(r'\s+', '', url)  # Remove any whitespace
        
        return url
    
    def _clean_group_name(self, group: str) -> str:
        """Clean and normalize group name"""
        if not group:
            return "General"
        
        group = group.strip()
        
        # Remove quotes if fully quoted
        if (group.startswith('"') and group.endswith('"')) or \
           (group.startswith("'") and group.endswith("'")):
            group = group[1:-1]
        
        # Normalize common group names
        group_lower = group.lower()
        if group_lower in ['entertainment', 'general', 'misc', 'other']:
            return "Entertainment"
        elif group_lower in ['news', 'news & politics']:
            return "News"
        elif group_lower in ['sports', 'sport']:
            return "Sports"
        elif group_lower in ['movies', 'films', 'cinema']:
            return "Movies"
        elif group_lower in ['kids', 'children', 'cartoon']:
            return "Kids"
        elif group_lower in ['music', 'audio']:
            return "Music"
        
        return group if group else "General"
    
    def _clean_logo_url(self, logo: str) -> str:
        """Clean and validate logo URL"""
        if not logo:
            return ""
        
        logo = logo.strip()
        
        # Basic URL validation
        if logo and (logo.startswith('http://') or logo.startswith('https://')):
            return logo
        
        return ""
    
    def _clean_epg_id(self, epg_id: str) -> str:
        """Clean and normalize EPG ID"""
        if not epg_id:
            return ""
        
        epg_id = epg_id.strip()
        
        # Remove spaces (EPG IDs shouldn't have spaces)
        epg_id = re.sub(r'\s+', '', epg_id)
        
        # Validate length (reasonable EPG ID length)
        if len(epg_id) > 100:
            return ""
        
        return epg_id
    
    def _generate_channel_signature(self, channel: ParsedChannel) -> str:
        """Generate signature for duplicate detection"""
        if self.config.duplicate_detection_method == "url_exact":
            return hashlib.md5(channel.url.lower().encode()).hexdigest()
        elif self.config.duplicate_detection_method == "url_similarity":
            # Normalize URL for similarity comparison
            parsed = urlparse(channel.url.lower())
            normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            return hashlib.md5(normalized_url.encode()).hexdigest()
        elif self.config.duplicate_detection_method == "name_similarity":
            # Normalize name for comparison
            normalized_name = re.sub(r'[^\w\s]', '', channel.name.lower())
            normalized_name = re.sub(r'\s+', ' ', normalized_name).strip()
            return hashlib.md5(normalized_name.encode()).hexdigest()
        else:  # metadata combination
            signature_text = f"{channel.name.lower()}|{channel.url.lower()}|{channel.group.lower()}"
            return hashlib.md5(signature_text.encode()).hexdigest()
    
    def _detect_country_from_text(self, text: str) -> Optional[str]:
        """Detect country code from text"""
        text_lower = text.lower()
        
        # Load country patterns if not loaded
        if not hasattr(self, 'country_patterns') or not self.country_patterns:
            self.country_patterns = self._load_country_patterns()
        
        for country_code, patterns in self.country_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return country_code
        
        return None
    
    def _detect_quality_from_text(self, text: str) -> Optional[str]:
        """Detect quality level from text"""
        text_lower = text.lower()
        
        # Load quality patterns if not loaded
        if not hasattr(self, 'quality_patterns') or not self.quality_patterns:
            self.quality_patterns = self._load_quality_patterns()
        
        for quality, patterns in self.quality_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return quality
        
        return None
    
    def _get_country_group_name(self, country_code: str) -> str:
        """Get group name for country"""
        country_names = {
            'US': 'USA', 'UK': 'United Kingdom', 'CA': 'Canada', 'AU': 'Australia',
            'DE': 'Germany', 'FR': 'France', 'IT': 'Italy', 'ES': 'Spain',
            'BR': 'Brazil', 'IN': 'India', 'CN': 'China', 'JP': 'Japan',
            'KR': 'South Korea', 'RU': 'Russia', 'TR': 'Turkey', 'AR': 'Argentina',
            'MX': 'Mexico', 'NL': 'Netherlands', 'SE': 'Sweden', 'NO': 'Norway',
            'DK': 'Denmark', 'FI': 'Finland', 'BE': 'Belgium', 'CH': 'Switzerland',
            'AT': 'Austria', 'PT': 'Portugal', 'GR': 'Greece', 'PL': 'Poland'
        }
        return country_names.get(country_code, country_code)
    
    def _analyze_by_group(self) -> Dict[str, int]:
        """Analyze channels by group"""
        groups = {}
        for channel in self.processed_channels:
            group = channel.group or 'Uncategorized'
            groups[group] = groups.get(group, 0) + 1
        return dict(sorted(groups.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_by_country(self) -> Dict[str, int]:
        """Analyze channels by country"""
        countries = {}
        for channel in self.processed_channels:
            country = channel.country or 'Unknown'
            countries[country] = countries.get(country, 0) + 1
        return dict(sorted(countries.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_by_quality(self) -> Dict[str, int]:
        """Analyze channels by quality"""
        qualities = {}
        for channel in self.processed_channels:
            quality = channel.quality or 'Unknown'
            qualities[quality] = qualities.get(quality, 0) + 1
        return dict(sorted(qualities.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_url_protocols(self) -> Dict[str, int]:
        """Analyze URL protocols used"""
        protocols = {}
        for channel in self.processed_channels:
            if channel.url:
                parsed = urlparse(channel.url)
                protocol = parsed.scheme.lower()
                protocols[protocol] = protocols.get(protocol, 0) + 1
        return dict(sorted(protocols.items(), key=lambda x: x[1], reverse=True))
    
    def _load_country_patterns(self) -> Dict[str, List[str]]:
        """Load country detection patterns"""
        return {
            'US': [r'\busa?\b', r'\bunited\s*states?\b', r'\bamerican?\b'],
            'UK': [r'\buk\b', r'\bbritish?\b', r'\bengland\b', r'\bscotland\b'],
            'CA': [r'\bcanada\b', r'\bcanadian?\b'],
            'AU': [r'\baustralia\b', r'\baussie\b', r'\boz\b'],
            'DE': [r'\bgerman[y]?\b', r'\bdeutsch\b'],
            'FR': [r'\bfrance\b', r'\bfrench\b', r'\bfr\b'],
            'IT': [r'\bitaly\b', r'\bitalian?\b'],
            'ES': [r'\bspain\b', r'\bspanish\b', r'\bespa[ñn]a\b'],
            'BR': [r'\bbrazil\b', r'\bbrasil\b', r'\bportuguese\b'],
            'IN': [r'\bindia\b', r'\bindian?\b', r'\bhindi\b'],
            'CN': [r'\bchina\b', r'\bchinese\b', r'\bmandarin\b'],
            'JP': [r'\bjapan\b', r'\bjapanese\b'],
            'KR': [r'\bkorea\b', r'\bkorean\b'],
            'RU': [r'\brussia\b', r'\brussian\b'],
            'TR': [r'\bturkey\b', r'\bturkish\b'],
            'AR': [r'\bargentina\b', r'\bargentinian?\b'],
            'MX': [r'\bmexico\b', r'\bmexican?\b'],
            'NL': [r'\bnetherlands?\b', r'\bdutch\b', r'\bholland\b'],
            'SE': [r'\bsweden\b', r'\bswedish\b'],
            'NO': [r'\bnorway\b', r'\bnorwegian\b'],
            'DK': [r'\bdenmark\b', r'\bdanish\b'],
            'FI': [r'\bfinland\b', r'\bfinnish\b'],
            'BE': [r'\bbelgium\b', r'\bbelgian?\b'],
            'CH': [r'\bswitzerland\b', r'\bswiss\b'],
            'AT': [r'\baustria\b', r'\baustrian?\b'],
            'PT': [r'\bportugal\b', r'\bportuguese\b'],
            'GR': [r'\bgreece\b', r'\bgreek\b'],
            'PL': [r'\bpoland\b', r'\bpolish\b']
        }
    
    def _load_quality_patterns(self) -> Dict[str, List[str]]:
        """Load quality detection patterns"""
        return {
            '4K': [r'\b4k\b', r'\buhd\b', r'\b2160p?\b', r'\bultra\s*hd\b'],
            'FHD': [r'\bfhd\b', r'\b1080p?\b', r'\bfull\s*hd\b'],
            'HD': [r'\bhd\b', r'\b720p?\b', r'\bhigh\s*def\b'],
            'SD': [r'\bsd\b', r'\b480p?\b', r'\bstandard\b']
        }
    
    def _load_genre_patterns(self) -> Dict[str, List[str]]:
        """Load genre detection patterns"""
        return {
            'News': [r'\bnews\b', r'\bcnn\b', r'\bbbc\b', r'\bfox\b', r'\bmsnbc\b'],
            'Sports': [r'\bsports?\b', r'\bespn\b', r'\bfootball\b', r'\bsoccer\b', r'\bbasketball\b'],
            'Movies': [r'\bmovies?\b', r'\bcinema\b', r'\bfilms?\b', r'\bhbo\b'],
            'Kids': [r'\bkids?\b', r'\bchildren\b', r'\bcartoon\b', r'\bdisney\b'],
            'Music': [r'\bmusic\b', r'\bmtv\b', r'\bvh1\b', r'\bradio\b'],
            'Entertainment': [r'\bentertainment\b', r'\bcomedy\b', r'\bdrama\b']
        }

# Command Line Interface
class M3UProcessorCLI:
    """Command line interface for the M3U processor"""
    
    def __init__(self):
        self.processor = None
    
    async def run(self, args):
        """Run CLI with provided arguments"""
        import argparse
        
        parser = argparse.ArgumentParser(description='Universal M3U Processor')
        parser.add_argument('input_file', help='Input M3U file path')
        parser.add_argument('--output', '-o', help='Output file path', default='processed_playlist.m3u')
        parser.add_argument('--mode', choices=['import', 'clean', 'validate', 'deduplicate', 'categorize', 'export', 'full'], 
                          default='full', help='Processing mode')
        parser.add_argument('--format', choices=['m3u', 'json', 'csv', 'txt'], default='m3u', help='Output format')
        parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
        parser.add_argument('--strict', action='store_true', help='Enable strict validation')
        parser.add_argument('--test-connectivity', action='store_true', help='Test stream connectivity')
        parser.add_argument('--no-duplicates', action='store_true', help='Skip duplicate removal')
        parser.add_argument('--no-categorize', action='store_true', help='Skip auto-categorization')
        parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
        
        args = parser.parse_args(args)
        
        # Setup logging
        if args.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        
        # Create configuration
        config = ProcessingConfig(
            input_file=args.input_file,
            output_file=args.output,
            output_format=args.format,
            backup_enabled=not args.no_backup,
            strict_validation=args.strict,
            test_stream_health=args.test_connectivity,
            remove_duplicates=not args.no_duplicates,
            auto_categorize=not args.no_categorize
        )
        
        # Create processor and run
        self.processor = UniversalM3UProcessor(config)
        
        # Map mode string to enum
        mode_map = {
            'import': ProcessingMode.IMPORT,
            'clean': ProcessingMode.CLEAN,
            'validate': ProcessingMode.VALIDATE,
            'deduplicate': ProcessingMode.DEDUPLICATE,
            'categorize': ProcessingMode.CATEGORIZE,
            'export': ProcessingMode.EXPORT,
            'full': ProcessingMode.FULL_PIPELINE
        }
        
        mode = mode_map[args.mode]
        
        try:
            stats = await self.processor.process_file(args.input_file, mode)
            
            # Print results
            print(f"\n{'='*60}")
            print(f"PROCESSING COMPLETE")
            print(f"{'='*60}")
            print(f"Input:           {stats.input_channels} channels")
            print(f"Output:          {stats.output_channels} channels")
            print(f"Removed:         {stats.channels_removed} channels")
            print(f"Duplicates:      {stats.duplicates_found}")
            print(f"Invalid URLs:    {stats.invalid_urls}")
            print(f"Efficiency:      {stats.efficiency_ratio():.1f}%")
            print(f"Quality Score:   {stats.quality_score:.1f}/100")
            print(f"Processing Time: {stats.processing_time:.1f}s")
            print(f"Format Detected: {stats.format_detected}")
            print(f"Output File:     {args.output}")
            
        except Exception as e:
            print(f"Error: {e}")
            return 1
        
        return 0

# Usage Examples and Main Entry Point
async def main():
    """Main entry point with usage examples"""
    import sys
    
    if len(sys.argv) < 2:
        print("Universal M3U Processor - Complete System")
        print("=" * 50)
        print()
        print("USAGE EXAMPLES:")
        print()
        print("# Full processing pipeline (recommended)")
        print("python processor.py playlist.m3u --mode full --output clean_playlist.m3u")
        print()
        print("# Validate only")
        print("python processor.py playlist.m3u --mode validate --verbose")
        print()
        print("# Clean and remove duplicates")
        print("python processor.py playlist.m3u --mode clean --no-categorize")
        print()
        print("# Test connectivity and export accessible channels")
        print("python processor.py playlist.m3u --test-connectivity --format json")
        print()
        print("# Convert format")
        print("python processor.py playlist.m3u --mode export --format csv")
        print()
        print("PROCESSING MODES:")
        print("  import      - Basic import and validation")
        print("  clean       - Clean and normalize data")
        print("  validate    - Comprehensive validation")
        print("  deduplicate - Remove duplicate channels")
        print("  categorize  - Auto-categorize channels")
        print("  export      - Export to different format")
        print("  full        - Complete processing pipeline")
        print()
        print("OUTPUT FORMATS:")
        print("  m3u         - Standard M3U playlist")
        print("  json        - JSON with metadata")
        print("  csv         - CSV spreadsheet")
        print("  txt         - Simple text format")
        return 1
    
    cli = M3UProcessorCLI()
    return await cli.run(sys.argv[1:])

if __name__ == "__main__":
    import sys
    from enum import Enum
    
    # Define ProcessingMode enum here since it's used in main
    class ProcessingMode(Enum):
        IMPORT = "import"
        CLEAN = "clean"
        VALIDATE = "validate"
        DEDUPLICATE = "deduplicate"
        CATEGORIZE = "categorize"
        EXPORT = "export"
        FULL_PIPELINE = "full_pipeline"
    
    sys.exit(asyncio.run(main()))
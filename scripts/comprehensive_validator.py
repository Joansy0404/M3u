#!/usr/bin/env python3
"""
Comprehensive M3U Validator - Complete Validation System
Handles ALL streaming protocols with flexible validation levels

This replaces over-restrictive validation with a smart, configurable system.
SUPPORTS: HTTP, HTTPS, RTMP, RTMPS, UDP, RTP, MMS, RTSP, SRT, and more
"""

import re
import asyncio
import aiohttp
import logging
import socket
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse, parse_qs
import ipaddress
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class ValidationLevel(Enum):
    """Validation strictness levels"""
    BASIC = "basic"          # Format validation only
    STANDARD = "standard"    # Format + URL structure validation  
    STRICT = "strict"        # Full validation including connectivity tests
    PERMISSIVE = "permissive" # Very lenient for malformed files

class IssueType(Enum):
    """Types of validation issues"""
    ERROR = "error"         # Critical issues that break functionality
    WARNING = "warning"     # Issues that may cause problems
    INFO = "info"          # Informational notes
    SUGGESTION = "suggestion" # Optimization suggestions

class ProtocolCategory(Enum):
    """Streaming protocol categories"""
    HTTP_STREAMING = "http_streaming"
    RTMP_STREAMING = "rtmp_streaming"
    UDP_STREAMING = "udp_streaming"
    RTP_STREAMING = "rtp_streaming"
    CUSTOM_STREAMING = "custom_streaming"
    FILE_BASED = "file_based"

@dataclass
class ValidationIssue:
    """Individual validation issue"""
    type: IssueType
    category: str
    message: str
    line_number: Optional[int] = None
    channel_name: Optional[str] = None
    url: Optional[str] = None
    suggestion: Optional[str] = None
    severity_score: int = 1  # 1-10 scale

@dataclass
class StreamHealthCheck:
    """Stream connectivity health check result"""
    url: str
    accessible: bool = False
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    error_message: Optional[str] = None
    protocol_supported: bool = True

@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    valid: bool
    validation_level: ValidationLevel
    total_channels: int
    valid_channels: int
    issues: List[ValidationIssue]
    stream_health: List[StreamHealthCheck]
    statistics: Dict[str, Any]
    quality_score: float  # 0-100 scale
    recommendations: List[str]
    processing_time: float

class ComprehensiveM3UValidator:
    """
    Comprehensive M3U validation system with flexible protocol support
    
    KEY FEATURES:
    - Supports ALL major streaming protocols (HTTP, RTMP, UDP, RTP, MMS, etc.)
    - Configurable validation levels (basic to strict)
    - Smart URL validation with protocol-specific rules
    - Connectivity testing with timeout controls
    - Detailed reporting with actionable suggestions
    - Country and quality detection
    - Duplicate detection with similarity scoring
    """
    
    # Comprehensive protocol support - EXPANDED for real-world usage
    SUPPORTED_PROTOCOLS = {
        'http://': ProtocolCategory.HTTP_STREAMING,
        'https://': ProtocolCategory.HTTP_STREAMING,
        'rtmp://': ProtocolCategory.RTMP_STREAMING,
        'rtmps://': ProtocolCategory.RTMP_STREAMING,
        'rtmpe://': ProtocolCategory.RTMP_STREAMING,
        'rtmpt://': ProtocolCategory.RTMP_STREAMING,
        'rtmpte://': ProtocolCategory.RTMP_STREAMING,
        'udp://': ProtocolCategory.UDP_STREAMING,
        'rtp://': ProtocolCategory.RTP_STREAMING,
        'rtsp://': ProtocolCategory.RTP_STREAMING,
        'mms://': ProtocolCategory.CUSTOM_STREAMING,
        'mmsh://': ProtocolCategory.CUSTOM_STREAMING,
        'mmst://': ProtocolCategory.CUSTOM_STREAMING,
        'mmsq://': ProtocolCategory.CUSTOM_STREAMING,
        'srt://': ProtocolCategory.CUSTOM_STREAMING,
        'hls://': ProtocolCategory.HTTP_STREAMING,
        'dash://': ProtocolCategory.HTTP_STREAMING,
        'icecast://': ProtocolCategory.HTTP_STREAMING,
        'shoutcast://': ProtocolCategory.HTTP_STREAMING,
        'ftp://': ProtocolCategory.FILE_BASED,
        'ftps://': ProtocolCategory.FILE_BASED,
        'sftp://': ProtocolCategory.FILE_BASED,
        'file://': ProtocolCategory.FILE_BASED,
        'smb://': ProtocolCategory.FILE_BASED,
        'nfs://': ProtocolCategory.FILE_BASED
    }
    
    # Valid streaming file extensions
    STREAMING_EXTENSIONS = {
        '.m3u8', '.ts', '.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm',
        '.mpg', '.mpeg', '.m4v', '.3gp', '.wmv', '.asf', '.rm', '.rmvb',
        '.mp3', '.aac', '.ogg', '.flac', '.wav', '.m4a', '.wma'
    }
    
    # Domain validation patterns
    DOMAIN_PATTERNS = {
        'valid_domain': re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'),
        'ip_address': re.compile(r'^(\d{1,3}\.){3}\d{1,3}$'),
        'ipv6_address': re.compile(r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$')
    }
    
    # Quality indicators for detection
    QUALITY_INDICATORS = {
        '4K': [r'\b4k\b', r'\buhd\b', r'\b2160p?\b', r'\bultra\s*hd\b'],
        'FHD': [r'\bfhd\b', r'\b1080p?\b', r'\bfull\s*hd\b'],
        'HD': [r'\bhd\b', r'\b720p?\b', r'\bhigh\s*def\b'],
        'SD': [r'\bsd\b', r'\b480p?\b', r'\bstandard\b']
    }
    
    def __init__(self, 
                 validation_level: ValidationLevel = ValidationLevel.STANDARD,
                 timeout: int = 10,
                 max_concurrent_tests: int = 20,
                 enable_connectivity_tests: bool = False):
        """
        Initialize validator with configuration
        
        Args:
            validation_level: Level of validation strictness
            timeout: Network timeout for connectivity tests
            max_concurrent_tests: Maximum concurrent stream tests
            enable_connectivity_tests: Whether to test actual connectivity
        """
        self.validation_level = validation_level
        self.timeout = timeout
        self.max_concurrent_tests = max_concurrent_tests
        self.enable_connectivity_tests = enable_connectivity_tests
        
        self.logger = logging.getLogger(__name__)
        
        # Quality scoring weights
        self.quality_weights = {
            'format_compliance': 0.25,
            'url_validity': 0.20,
            'metadata_completeness': 0.15,
            'stream_accessibility': 0.25,
            'duplicate_ratio': 0.10,
            'encoding_quality': 0.05
        }
        
        # Common streaming ports for validation
        self.streaming_ports = {80, 443, 8080, 8443, 1935, 554, 8554, 1234, 5004}
        
        # Country detection patterns
        self.country_patterns = {
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
            'NL': [r'\bnetherlands?\b', r'\bdutch\b', r'\bholland\b']
        }
    
    async def validate_playlist(self, content: Union[str, List[str]]) -> ValidationReport:
        """
        Main validation method for M3U playlists
        
        Args:
            content: M3U content as string or list of lines
            
        Returns:
            Comprehensive validation report
        """
        start_time = time.time()
        
        # Normalize input
        if isinstance(content, str):
            lines = self._normalize_content(content)
        else:
            lines = [line.strip() for line in content if line.strip()]
        
        # Initialize report
        issues = []
        stream_health = []
        statistics = self._initialize_statistics()
        
        # Parse channels
        channels = self._parse_channels(lines, issues, statistics)
        
        # Validate format structure
        self._validate_format_structure(lines, channels, issues, statistics)
        
        # Validate individual channels
        await self._validate_channels(channels, issues, statistics)
        
        # Test stream connectivity if enabled
        if self.enable_connectivity_tests:
            stream_health = await self._test_stream_connectivity(channels)
            self._update_statistics_with_health(stream_health, statistics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, statistics)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(issues, statistics, stream_health)
        
        # Determine overall validity
        error_count = len([i for i in issues if i.type == IssueType.ERROR])
        valid = error_count == 0 or self.validation_level == ValidationLevel.PERMISSIVE
        
        processing_time = time.time() - start_time
        
        return ValidationReport(
            valid=valid,
            validation_level=self.validation_level,
            total_channels=len(channels),
            valid_channels=statistics['valid_channels'],
            issues=issues,
            stream_health=stream_health,
            statistics=statistics,
            quality_score=quality_score,
            recommendations=recommendations,
            processing_time=processing_time
        )
    
    def validate_url(self, url: str, allow_custom_protocols: bool = True) -> Tuple[bool, List[str]]:
        """
        Flexible URL validation supporting all streaming protocols
        
        Args:
            url: URL to validate
            allow_custom_protocols: Whether to allow non-standard protocols
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        if not url or not url.strip():
            return False, ["Empty URL"]
        
        url = url.strip()
        issues = []
        
        try:
            # Basic format check
            if len(url) > 2048:
                issues.append("URL exceeds maximum length (2048 characters)")
                if self.validation_level == ValidationLevel.STRICT:
                    return False, issues
            
            # Parse URL
            parsed = urlparse(url)
            
            # Protocol validation
            protocol = f"{parsed.scheme.lower()}://" if parsed.scheme else ""
            
            if protocol in self.SUPPORTED_PROTOCOLS:
                # Known protocol - apply specific validation
                protocol_category = self.SUPPORTED_PROTOCOLS[protocol]
                protocol_valid, protocol_issues = self._validate_protocol_specific(url, protocol_category, parsed)
                issues.extend(protocol_issues)
                
                if not protocol_valid and self.validation_level == ValidationLevel.STRICT:
                    return False, issues
                    
            elif allow_custom_protocols and parsed.scheme:
                # Unknown protocol - warn but don't fail
                issues.append(f"Unknown protocol '{parsed.scheme}' - may not be supported by all players")
                
            elif not parsed.scheme:
                # No protocol - check if it's a relative URL or file path
                if '/' in url or '\\' in url:
                    issues.append("URL missing protocol (http://, rtmp://, etc.)")
                else:
                    return False, ["Invalid URL format"]
            
            # Host validation (if applicable)
            if parsed.netloc:
                host_valid, host_issues = self._validate_host(parsed.netloc)
                issues.extend(host_issues)
                
                if not host_valid and self.validation_level == ValidationLevel.STRICT:
                    return False, issues
            
            # Path validation
            if parsed.path:
                path_valid, path_issues = self._validate_path(parsed.path)
                issues.extend(path_issues)
            
            # Query parameters validation
            if parsed.query:
                query_valid, query_issues = self._validate_query_params(parsed.query)
                issues.extend(query_issues)
            
            # Determine validity based on validation level
            error_count = len([i for i in issues if "Invalid" in i or "missing" in i.lower()])
            
            if self.validation_level == ValidationLevel.PERMISSIVE:
                return True, issues  # Always valid in permissive mode
            elif self.validation_level == ValidationLevel.BASIC:
                return error_count == 0, issues
            elif self.validation_level == ValidationLevel.STANDARD:
                return error_count == 0, issues
            else:  # STRICT
                return len(issues) == 0, issues
                
        except Exception as e:
            return False, [f"URL parsing error: {str(e)}"]
    
    def _validate_protocol_specific(self, url: str, category: ProtocolCategory, parsed) -> Tuple[bool, List[str]]:
        """Validate URL based on protocol category"""
        issues = []
        
        if category == ProtocolCategory.HTTP_STREAMING:
            # HTTP/HTTPS validation
            if not parsed.netloc:
                issues.append("HTTP URL missing hostname")
                return False, issues
            
            # Check for common streaming patterns
            if parsed.path:
                if any(ext in parsed.path.lower() for ext in self.STREAMING_EXTENSIONS):
                    # Looks like a valid streaming URL
                    pass
                elif parsed.path == '/':
                    issues.append("HTTP URL path is just root - may not be a stream")
                
        elif category == ProtocolCategory.RTMP_STREAMING:
            # RTMP validation
            if not parsed.netloc:
                issues.append("RTMP URL missing hostname")
                return False, issues
            
            # RTMP typically uses port 1935
            if parsed.port and parsed.port not in {1935, 80, 443}:
                issues.append(f"Unusual RTMP port {parsed.port} - standard is 1935")
                
        elif category == ProtocolCategory.UDP_STREAMING:
            # UDP validation
            if not parsed.netloc:
                issues.append("UDP URL missing hostname/IP")
                return False, issues
            
            # UDP streams often use multicast addresses
            hostname = parsed.hostname
            if hostname:
                try:
                    ip = ipaddress.ip_address(hostname)
                    if ip.is_multicast:
                        # Multicast address - this is good for UDP
                        pass
                    elif ip.is_private:
                        issues.append("UDP stream uses private IP - may not be accessible externally")
                except ValueError:
                    issues.append("UDP URL should typically use IP address")
                    
        elif category == ProtocolCategory.RTP_STREAMING:
            # RTP/RTSP validation
            if not parsed.netloc:
                issues.append("RTP/RTSP URL missing hostname")
                return False, issues
            
            # RTSP typically uses port 554
            if parsed.port and parsed.port not in {554, 8554}:
                issues.append(f"Unusual RTSP port {parsed.port} - standard is 554")
                
        elif category == ProtocolCategory.FILE_BASED:
            # File-based protocols
            if parsed.scheme == 'file' and not parsed.path:
                issues.append("File URL missing path")
                return False, issues
        
        return True, issues
    
    def _validate_host(self, netloc: str) -> Tuple[bool, List[str]]:
        """Validate hostname/IP in URL"""
        issues = []
        
        # Extract hostname and port
        if ':' in netloc:
            hostname, port_str = netloc.rsplit(':', 1)
            try:
                port = int(port_str)
                if port < 1 or port > 65535:
                    issues.append(f"Invalid port number: {port}")
                    return False, issues
            except ValueError:
                issues.append(f"Invalid port format: {port_str}")
                return False, issues
        else:
            hostname = netloc
            port = None
        
        # Validate hostname
        if not hostname:
            issues.append("Empty hostname")
            return False, issues
        
        # Check if it's an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_loopback and self.validation_level == ValidationLevel.STRICT:
                issues.append("Loopback IP address may not be accessible externally")
            elif ip.is_private:
                issues.append("Private IP address may not be accessible externally")
            return True, issues
        except ValueError:
            pass
        
        # Validate as domain name
        if not self.DOMAIN_PATTERNS['valid_domain'].match(hostname):
            issues.append(f"Invalid hostname format: {hostname}")
            return False, issues
        
        # Check for suspicious patterns
        if any(suspicious in hostname.lower() for suspicious in ['localhost', 'example', 'test', 'invalid']):
            issues.append(f"Hostname '{hostname}' appears to be a placeholder")
        
        return True, issues
    
    def _validate_path(self, path: str) -> Tuple[bool, List[str]]:
        """Validate URL path"""
        issues = []
        
        # Check for suspicious characters
        if any(char in path for char in ['<', '>', '"', '|', '*', '?']):
            issues.append("URL path contains suspicious characters")
        
        # Check for encoding issues
        if '%' in path:
            # URL encoded - try to decode
            try:
                from urllib.parse import unquote
                decoded = unquote(path)
                if any(ord(c) < 32 or ord(c) > 126 for c in decoded if ord(c) < 128):
                    issues.append("URL path contains control characters")
            except Exception:
                issues.append("URL path has malformed encoding")
        
        return True, issues
    
    def _validate_query_params(self, query: str) -> Tuple[bool, List[str]]:
        """Validate URL query parameters"""
        issues = []
        
        try:
            params = parse_qs(query)
            
            # Check for common streaming parameters
            streaming_params = {'token', 'auth', 'key', 'session', 'user', 'pass', 'password'}
            found_auth = any(param.lower() in streaming_params for param in params.keys())
            
            if found_auth:
                issues.append("URL contains authentication parameters - ensure they are valid")
                
        except Exception:
            issues.append("Malformed query parameters")
        
        return True, issues
    
    async def _test_stream_connectivity(self, channels: List[Dict[str, Any]]) -> List[StreamHealthCheck]:
        """Test stream connectivity for channels"""
        if not self.enable_connectivity_tests:
            return []
        
        self.logger.info(f"Testing connectivity for {len(channels)} channels...")
        
        # Limit concurrent tests
        semaphore = asyncio.Semaphore(self.max_concurrent_tests)
        
        async def test_single_stream(channel: Dict[str, Any]) -> StreamHealthCheck:
            async with semaphore:
                return await self._test_single_stream(channel['url'])
        
        # Run tests concurrently
        tasks = [test_single_stream(channel) for channel in channels]
        health_checks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_checks = [check for check in health_checks if isinstance(check, StreamHealthCheck)]
        
        self.logger.info(f"Completed connectivity tests: {len(valid_checks)} results")
        return valid_checks
    
    async def _test_single_stream(self, url: str) -> StreamHealthCheck:
        """Test connectivity for a single stream"""
        health = StreamHealthCheck(url=url)
        
        try:
            parsed = urlparse(url)
            protocol = parsed.scheme.lower()
            
            if protocol in ['http', 'https']:
                # Test HTTP/HTTPS streams
                health = await self._test_http_stream(url)
            elif protocol in ['rtmp', 'rtmps']:
                # Test RTMP streams (limited testing)
                health = await self._test_rtmp_stream(url)
            elif protocol == 'udp':
                # Test UDP streams
                health = await self._test_udp_stream(url)
            else:
                # Other protocols - basic reachability test
                health = await self._test_generic_stream(url)
                
        except Exception as e:
            health.error_message = str(e)
            health.accessible = False
        
        return health
    
    async def _test_http_stream(self, url: str) -> StreamHealthCheck:
        """Test HTTP/HTTPS stream connectivity"""
        health = StreamHealthCheck(url=url)
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start_time = time.time()
                
                async with session.head(url, allow_redirects=True) as response:
                    health.response_time = time.time() - start_time
                    health.status_code = response.status
                    health.content_type = response.headers.get('Content-Type', '')
                    health.accessible = 200 <= response.status < 400
                    
                    if not health.accessible:
                        health.error_message = f"HTTP {response.status}"
                        
        except asyncio.TimeoutError:
            health.error_message = "Connection timeout"
        except Exception as e:
            health.error_message = str(e)
        
        return health
    
    async def _test_rtmp_stream(self, url: str) -> StreamHealthCheck:
        """Test RTMP stream connectivity (basic)"""
        health = StreamHealthCheck(url=url)
        
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            port = parsed.port or 1935
            
            # Test if RTMP port is reachable
            loop = asyncio.get_event_loop()
            start_time = time.time()
            
            try:
                await asyncio.wait_for(
                    loop.create_connection(lambda: asyncio.Protocol(), hostname, port),
                    timeout=self.timeout
                )
                health.response_time = time.time() - start_time
                health.accessible = True
            except (OSError, asyncio.TimeoutError):
                health.error_message = f"Cannot reach RTMP server {hostname}:{port}"
                
        except Exception as e:
            health.error_message = str(e)
        
        return health
    
    async def _test_udp_stream(self, url: str) -> StreamHealthCheck:
        """Test UDP stream connectivity (basic)"""
        health = StreamHealthCheck(url=url)
        
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            port = parsed.port or 1234
            
            # Basic UDP socket test
            loop = asyncio.get_event_loop()
            
            def test_udp():
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(self.timeout)
                    sock.connect((hostname, port))
                    sock.close()
                    return True
                except Exception:
                    return False
            
            start_time = time.time()
            accessible = await loop.run_in_executor(None, test_udp)
            health.response_time = time.time() - start_time
            health.accessible = accessible
            
            if not accessible:
                health.error_message = f"Cannot reach UDP endpoint {hostname}:{port}"
                
        except Exception as e:
            health.error_message = str(e)
        
        return health
    
    async def _test_generic_stream(self, url: str) -> StreamHealthCheck:
        """Generic connectivity test for unsupported protocols"""
        health = StreamHealthCheck(url=url)
        
        try:
            parsed = urlparse(url)
            if parsed.hostname:
                # Test basic hostname resolution
                loop = asyncio.get_event_loop()
                start_time = time.time()
                
                try:
                    await loop.getaddrinfo(parsed.hostname, None)
                    health.response_time = time.time() - start_time
                    health.accessible = True
                except Exception:
                    health.error_message = f"Cannot resolve hostname {parsed.hostname}"
            else:
                health.error_message = "No hostname to test"
                
        except Exception as e:
            health.error_message = str(e)
        
        return health
    
    def _parse_channels(self, lines: List[str], issues: List[ValidationIssue], statistics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse channels from M3U lines"""
        channels = []
        current_extinf = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if line.startswith('#EXTINF'):
                current_extinf = {'line_num': line_num, 'extinf': line}
                statistics['extinf_lines'] += 1
                
            elif self._looks_like_url(line):
                url_valid, url_issues = self.validate_url(line)
                
                channel = {
                    'url': line,
                    'line_num': line_num,
                    'extinf_data': current_extinf,
                    'valid': url_valid
                }
                
                # Add URL validation issues
                for issue_msg in url_issues:
                    issue_type = IssueType.ERROR if not url_valid else IssueType.WARNING
                    issues.append(ValidationIssue(
                        type=issue_type,
                        category='url_validation',
                        message=issue_msg,
                        line_number=line_num,
                        url=line
                    ))
                
                if url_valid:
                    statistics['valid_channels'] += 1
                else:
                    statistics['invalid_channels'] += 1
                
                channels.append(channel)
                current_extinf = None
                
        statistics['total_channels'] = len(channels)
        return channels
    
    def _looks_like_url(self, line: str) -> bool:
        """Check if line looks like a URL"""
        if not line:
            return False
        
        # Check for known protocols
        for protocol in self.SUPPORTED_PROTOCOLS.keys():
            if line.lower().startswith(protocol):
                return True
        
        # Check for common URL patterns
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', line):
            return True
        
        # Check for domain-like patterns
        if re.search(r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', line):
            return True
        
        return False
    
    def _validate_format_structure(self, lines: List[str], channels: List[Dict[str, Any]], 
                                 issues: List[ValidationIssue], statistics: Dict[str, Any]) -> None:
        """Validate M3U format structure"""
        
        # Check for M3U header
        if lines and not lines[0].upper().startswith('#EXTM3U'):
            if self.validation_level != ValidationLevel.PERMISSIVE:
                issues.append(ValidationIssue(
                    type=IssueType.WARNING,
                    category='format_structure',
                    message='Missing #EXTM3U header - file may not be recognized as M3U',
                    line_number=1,
                    suggestion='Add #EXTM3U as the first line'
                ))
        
        # Check EXTINF to URL ratio
        extinf_count = statistics.get('extinf_lines', 0)
        url_count = len(channels)
        
        if extinf_count > url_count:
            issues.append(ValidationIssue(
                type=IssueType.WARNING,
                category='format_structure',
                message=f'More EXTINF lines ({extinf_count}) than URLs ({url_count}) - orphaned metadata',
                suggestion='Ensure each EXTINF line is followed by a URL'
            ))
        elif extinf_count < url_count and extinf_count > 0:
            issues.append(ValidationIssue(
                type=IssueType.INFO,
                category='format_structure',
                message=f'Mixed format detected - some URLs lack EXTINF metadata',
                suggestion='Consider adding EXTINF lines for all channels for better compatibility'
            ))
    
    async def _validate_channels(self, channels: List[Dict[str, Any]], 
                               issues: List[ValidationIssue], statistics: Dict[str, Any]) -> None:
        """Validate individual channels"""
        
        duplicate_urls = set()
        seen_urls = set()
        
        for channel in channels:
            url = channel['url']
            line_num = channel['line_num']
            
            # Check for duplicates
            if url.lower() in seen_urls:
                duplicate_urls.add(url)
                issues.append(ValidationIssue(
                    type=IssueType.WARNING,
                    category='duplicates',
                    message='Duplicate URL detected',
                    line_number=line_num,
                    url=url,
                    suggestion='Remove duplicate entries to reduce playlist size'
                ))
            else:
                seen_urls.add(url.lower())
            
            # Validate EXTINF data if present
            if channel.get('extinf_data'):
                self._validate_extinf_data(channel['extinf_data'], issues)
            
            # Protocol-specific validation
            self._validate_channel_protocol(channel, issues)
            
            # Quality and country detection
            self._detect_channel_metadata(channel, statistics)
        
        statistics['duplicate_urls'] = len(duplicate_urls)
        statistics['unique_urls'] = len(seen_urls)
    
    def _validate_extinf_data(self, extinf_data: Dict[str, Any], issues: List[ValidationIssue]) -> None:
        """Validate EXTINF line data"""
        extinf_line = extinf_data['extinf']
        line_num = extinf_data['line_num']
        
        # Parse duration
        duration_match = re.search(r'#EXTINF:\s*(-?\d+(?:\.\d+)?)', extinf_line)
        if not duration_match:
            issues.append(ValidationIssue(
                type=IssueType.ERROR,
                category='extinf_format',
                message='EXTINF line missing duration',
                line_number=line_num,
                suggestion='Add duration after #EXTINF: (use -1 for live streams)'
            ))
        
        # Check for title
        if ',' in extinf_line:
            title_part = extinf_line.split(',', 1)[1].strip()
            if not title_part:
                issues.append(ValidationIssue(
                    type=IssueType.WARNING,
                    category='metadata_quality',
                    message='EXTINF line has empty title',
                    line_number=line_num,
                    suggestion='Add descriptive channel name after comma'
                ))
        else:
            issues.append(ValidationIssue(
                type=IssueType.WARNING,
                category='extinf_format',
                message='EXTINF line missing title separator (comma)',
                line_number=line_num,
                suggestion='Add comma and title after duration'
            ))
    
    def _validate_channel_protocol(self, channel: Dict[str, Any], issues: List[ValidationIssue]) -> None:
        """Validate channel based on its protocol"""
        url = channel['url']
        line_num = channel['line_num']
        
        try:
            parsed = urlparse(url)
            protocol = f"{parsed.scheme.lower()}://" if parsed.scheme else ""
            
            if protocol in self.SUPPORTED_PROTOCOLS:
                category = self.SUPPORTED_PROTOCOLS[protocol]
                
                # Protocol-specific warnings
                if category == ProtocolCategory.UDP_STREAMING:
                    if not parsed.port:
                        issues.append(ValidationIssue(
                            type=IssueType.INFO,
                            category='protocol_specific',
                            message='UDP stream missing port number',
                            line_number=line_num,
                            url=url,
                            suggestion='UDP streams typically require port specification'
                        ))
                
                elif category == ProtocolCategory.RTMP_STREAMING:
                    if not parsed.path or parsed.path == '/':
                        issues.append(ValidationIssue(
                            type=IssueType.WARNING,
                            category='protocol_specific',
                            message='RTMP stream missing application/stream path',
                            line_number=line_num,
                            url=url,
                            suggestion='RTMP URLs typically need /application/stream_name path'
                        ))
                
        except Exception as e:
            issues.append(ValidationIssue(
                type=IssueType.ERROR,
                category='url_parsing',
                message=f'Failed to parse URL: {str(e)}',
                line_number=line_num,
                url=url
            ))
    
    def _detect_channel_metadata(self, channel: Dict[str, Any], statistics: Dict[str, Any]) -> None:
        """Detect country, quality, and other metadata from channel"""
        
        # Combine all text for analysis
        text_to_analyze = channel['url']
        if channel.get('extinf_data'):
            text_to_analyze += " " + channel['extinf_data']['extinf']
        
        # Country detection
        detected_country = self._detect_country(text_to_analyze)
        if detected_country:
            statistics.setdefault('countries', {})
            statistics['countries'][detected_country] = statistics['countries'].get(detected_country, 0) + 1
        
        # Quality detection
        detected_quality = self._detect_quality(text_to_analyze)
        if detected_quality:
            statistics.setdefault('qualities', {})
            statistics['qualities'][detected_quality] = statistics['qualities'].get(detected_quality, 0) + 1
    
    def _detect_country(self, text: str) -> Optional[str]:
        """Detect country from channel text"""
        text_lower = text.lower()
        
        for country_code, patterns in self.country_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return country_code
        
        return None
    
    def _detect_quality(self, text: str) -> Optional[str]:
        """Detect quality level from channel text"""
        text_lower = text.lower()
        
        for quality, patterns in self.QUALITY_INDICATORS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return quality
        
        return None
    
    def _update_statistics_with_health(self, health_checks: List[StreamHealthCheck], 
                                     statistics: Dict[str, Any]) -> None:
        """Update statistics with stream health data"""
        accessible_count = sum(1 for check in health_checks if check.accessible)
        statistics['accessible_streams'] = accessible_count
        statistics['inaccessible_streams'] = len(health_checks) - accessible_count
        
        if health_checks:
            response_times = [check.response_time for check in health_checks 
                            if check.response_time is not None]
            if response_times:
                statistics['avg_response_time'] = sum(response_times) / len(response_times)
                statistics['max_response_time'] = max(response_times)
                statistics['min_response_time'] = min(response_times)
    
    def _generate_recommendations(self, issues: List[ValidationIssue], 
                                statistics: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Count issue types
        error_count = len([i for i in issues if i.type == IssueType.ERROR])
        warning_count = len([i for i in issues if i.type == IssueType.WARNING])
        
        if error_count > 0:
            recommendations.append(f"Fix {error_count} critical errors to ensure playlist compatibility")
        
        if warning_count > 5:
            recommendations.append(f"Address {warning_count} warnings to improve playlist quality")
        
        # Duplicate recommendations
        duplicate_count = statistics.get('duplicate_urls', 0)
        if duplicate_count > 0:
            recommendations.append(f"Remove {duplicate_count} duplicate URLs to reduce file size")
        
        # Protocol recommendations
        protocol_issues = [i for i in issues if i.category == 'protocol_specific']
        if len(protocol_issues) > 5:
            recommendations.append("Review protocol configurations for better stream compatibility")
        
        # Metadata recommendations
        metadata_issues = [i for i in issues if i.category == 'metadata_quality']
        if len(metadata_issues) > 0:
            recommendations.append("Add missing channel metadata (names, groups, logos) for better user experience")
        
        # Performance recommendations
        total_channels = statistics.get('total_channels', 0)
        if total_channels > 10000:
            recommendations.append("Consider splitting large playlist into smaller files for better performance")
        
        return recommendations
    
    def _calculate_quality_score(self, issues: List[ValidationIssue], 
                                statistics: Dict[str, Any], 
                                health_checks: List[StreamHealthCheck]) -> float:
        """Calculate overall quality score (0-100)"""
        scores = {}
        
        # Format compliance score
        format_errors = len([i for i in issues if i.category in ['format_structure', 'extinf_format'] and i.type == IssueType.ERROR])
        total_channels = statistics.get('total_channels', 1)
        scores['format_compliance'] = max(0, 100 - (format_errors / total_channels * 100))
        
        # URL validity score
        valid_channels = statistics.get('valid_channels', 0)
        scores['url_validity'] = (valid_channels / total_channels * 100) if total_channels > 0 else 0
        
        # Metadata completeness score
        metadata_issues = len([i for i in issues if i.category == 'metadata_quality'])
        scores['metadata_completeness'] = max(0, 100 - (metadata_issues / total_channels * 50))
        
        # Stream accessibility score (if tested)
        if health_checks:
            accessible_count = sum(1 for check in health_checks if check.accessible)
            scores['stream_accessibility'] = (accessible_count / len(health_checks) * 100)
        else:
            scores['stream_accessibility'] = 50  # Neutral score if not tested
        
        # Duplicate ratio score
        duplicate_count = statistics.get('duplicate_urls', 0)
        unique_count = statistics.get('unique_urls', total_channels)
        duplicate_ratio = duplicate_count / total_channels if total_channels > 0 else 0
        scores['duplicate_ratio'] = max(0, 100 - (duplicate_ratio * 100))
        
        # Encoding quality score (basic check)
        encoding_issues = len([i for i in issues if 'encoding' in i.message.lower()])
        scores['encoding_quality'] = max(0, 100 - (encoding_issues / total_channels * 100))
        
        # Calculate weighted average
        total_score = sum(scores[key] * self.quality_weights[key] for key in scores.keys())
        
        return round(total_score, 1)
    
    def _initialize_statistics(self) -> Dict[str, Any]:
        """Initialize statistics dictionary"""
        return {
            'total_channels': 0,
            'valid_channels': 0,
            'invalid_channels': 0,
            'extinf_lines': 0,
            'duplicate_urls': 0,
            'unique_urls': 0,
            'countries': {},
            'qualities': {},
            'protocols': {},
            'accessible_streams': 0,
            'inaccessible_streams': 0
        }
    
    def _normalize_content(self, content: str) -> List[str]:
        """Normalize M3U content for parsing"""
        # Remove BOM if present
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Split into lines and clean
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if line:  # Skip empty lines
                lines.append(line)
        
        return lines

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_validator():
        # Test the validator with various scenarios
        
        # Sample M3U content with various issues
        test_m3u = """#EXTM3U
#EXTINF:-1 tvg-id="cnn" tvg-name="CNN" group-title="News",CNN International
http://cnn-live.example.com/stream.m3u8
#EXTINF:180,BBC News HD
https://bbc-hd.example.com/live/news.m3u8
#EXTINF:-1,RTMP Stream Test
rtmp://streaming.example.com:1935/live/stream1
#EXTINF:-1,UDP Multicast
udp://239.1.1.1:1234
http://duplicate.example.com/stream.m3u8
http://duplicate.example.com/stream.m3u8
#EXTINF:-1,Invalid URL Test
not-a-valid-url
#EXTINF:-1,Missing URL Test"""
        
        # Test different validation levels
        levels = [ValidationLevel.BASIC, ValidationLevel.STANDARD, ValidationLevel.STRICT, ValidationLevel.PERMISSIVE]
        
        for level in levels:
            print(f"\n=== Testing {level.value.upper()} validation ===")
            
            validator = ComprehensiveM3UValidator(
                validation_level=level,
                enable_connectivity_tests=False,  # Disable for testing
                timeout=5
            )
            
            report = await validator.validate_playlist(test_m3u)
            
            print(f"Valid: {report.valid}")
            print(f"Total Channels: {report.total_channels}")
            print(f"Valid Channels: {report.valid_channels}")
            print(f"Quality Score: {report.quality_score}")
            print(f"Issues: {len(report.issues)} ({len([i for i in report.issues if i.type == IssueType.ERROR])} errors)")
            
            # Show first few issues
            for issue in report.issues[:3]:
                print(f"  - {issue.type.value}: {issue.message}")
            
            if report.recommendations:
                print(f"Recommendations: {len(report.recommendations)}")
                for rec in report.recommendations[:2]:
                    print(f"  • {rec}")
        
        # Test URL validation
        print(f"\n=== Testing URL Validation ===")
        test_urls = [
            "http://example.com/stream.m3u8",
            "https://secure.example.com:8443/live/channel1.ts",
            "rtmp://streaming.example.com:1935/live/stream1",
            "rtmps://secure-streaming.example.com/app/stream2",
            "udp://239.1.1.1:1234",
            "rtp://192.168.1.100:5004",
            "mms://media.example.com/stream",
            "invalid-url-format",
            "http://",
            "ftp://files.example.com/video.mp4"
        ]
        
        validator = ComprehensiveM3UValidator(validation_level=ValidationLevel.STANDARD)
        
        for url in test_urls:
            valid, issues = validator.validate_url(url)
            status = "✅" if valid else "❌"
            print(f"{status} {url}")
            for issue in issues[:2]:  # Show first 2 issues
                print(f"    • {issue}")
    
    # Run tests
    asyncio.run(test_validator())

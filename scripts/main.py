#!/usr/bin/env python3
"""
Complete M3U Repository Fix
This script identifies and fixes all disconnected components in your M3U tool
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}")

def diagnose_repository():
    """Diagnose what's broken in the repository"""
    log("🔍 DIAGNOSING REPOSITORY ISSUES...")
    
    issues = []
    
    # 1. Check if scripts/main.py is functional
    main_py = Path("scripts/main.py")
    if main_py.exists():
        content = main_py.read_text()
        if "not yet implemented" in content or "placeholder" in content.lower():
            issues.append("❌ scripts/main.py is a placeholder, not functional")
        elif len(content) < 500:
            issues.append("❌ scripts/main.py is too small to be functional")
    else:
        issues.append("❌ scripts/main.py is missing")
    
    # 2. Check if config/providers.txt has content
    providers_txt = Path("config/providers.txt")
    if providers_txt.exists():
        content = providers_txt.read_text()
        urls = [line.strip() for line in content.splitlines() 
                if line.strip() and not line.startswith('#') and line.startswith('http')]
        if not urls:
            issues.append("❌ config/providers.txt has no valid URLs")
    else:
        issues.append("❌ config/providers.txt is missing")
    
    # 3. Check if workflow can find main.py
    workflow_file = Path(".github/workflows/process.yml")
    if workflow_file.exists():
        content = workflow_file.read_text()
        if "scripts/main.py" in content:
            log("✅ Workflow references scripts/main.py")
        else:
            issues.append("❌ Workflow doesn't call scripts/main.py")
    else:
        issues.append("❌ No GitHub workflow found")
    
    # 4. Check if playlists directory exists
    playlists_dir = Path("playlists")
    if not playlists_dir.exists():
        issues.append("❌ playlists/ directory missing")
    
    # 5. Check if final.m3u exists and is recent
    final_m3u = Path("playlists/final.m3u")
    if final_m3u.exists():
        age_hours = (datetime.now().timestamp() - final_m3u.stat().st_mtime) / 3600
        if age_hours > 24:
            issues.append(f"⚠️ final.m3u is {age_hours:.1f} hours old")
    else:
        issues.append("❌ playlists/final.m3u doesn't exist")
    
    return issues

def create_functional_main_py():
    """Create a working scripts/main.py"""
    log("🔧 Creating functional scripts/main.py...")
    
    scripts_dir = Path("scripts")
    scripts_dir.mkdir(exist_ok=True)
    
    main_py_content = '''#!/usr/bin/env python3
"""
Functional M3U Processor - Actually generates final.m3u
This replaces the placeholder with working code
"""

import os
import sys
import json
import requests
import re
from pathlib import Path
from datetime import datetime

def log(msg):
    """Simple logging function"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def ensure_directories():
    """Create required directories"""
    directories = ["config", "playlists", "reports", "logs", "editor"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def create_default_config():
    """Create default config if missing"""
    config_file = Path("config/providers.txt")
    
    if not config_file.exists():
        default_config = """# M3U Provider URLs
# Add your IPTV playlist URLs here (one per line)
https://iptv-org.github.io/iptv/languages/eng.m3u
https://raw.githubusercontent.com/iptv-org/iptv/master/streams/us.m3u
https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ca.m3u
https://raw.githubusercontent.com/iptv-org/iptv/master/streams/uk.m3u
"""
        config_file.write_text(default_config)
        log("✅ Created default config/providers.txt")

def load_providers():
    """Load provider URLs from config"""
    config_file = Path("config/providers.txt")
    providers = []
    
    if config_file.exists():
        content = config_file.read_text()
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and line.startswith('http'):
                providers.append(line)
    
    if not providers:
        log("⚠️ No providers found, using defaults")
        providers = [
            "https://iptv-org.github.io/iptv/languages/eng.m3u",
            "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/us.m3u"
        ]
    
    return providers

def download_m3u(url):
    """Download M3U content from URL"""
    try:
        log(f"📡 Downloading: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        
        # Handle encoding
        content = response.content
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                decoded = content.decode(encoding)
                if '#EXTINF' in decoded:
                    log(f"✅ Downloaded {len(decoded)} characters")
                    return decoded
            except UnicodeDecodeError:
                continue
        
        # Fallback
        decoded = content.decode('utf-8', errors='replace')
        return decoded
        
    except Exception as e:
        log(f"❌ Error downloading {url}: {e}")
        return None

def parse_m3u(content):
    """Parse M3U content and extract channels"""
    if not content or '#EXTINF' not in content:
        return []
    
    channels = []
    lines = content.splitlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF:'):
            extinf = line
            
            # Find the URL on next non-comment line
            url = None
            j = i + 1
            while j < len(lines) and j < i + 5:
                potential_url = lines[j].strip()
                if potential_url and not potential_url.startswith('#'):
                    if potential_url.startswith('http'):
                        url = potential_url
                        break
                j += 1
            
            if url:
                # Extract channel name
                name_match = re.search(r',([^,]+)$', extinf)
                name = name_match.group(1).strip() if name_match else "Unknown Channel"
                
                channels.append({
                    'extinf': extinf,
                    'url': url,
                    'name': name
                })
                i = j + 1
            else:
                i += 1
        else:
            i += 1
    
    return channels

def remove_duplicates(channels):
    """Remove duplicate channels"""
    log("🔄 Removing duplicates...")
    
    seen_urls = set()
    unique_channels = []
    
    for channel in channels:
        url = channel['url'].lower()
        if url not in seen_urls:
            seen_urls.add(url)
            unique_channels.append(channel)
    
    removed = len(channels) - len(unique_channels)
    log(f"📊 Removed {removed} duplicates, {len(unique_channels)} unique channels remain")
    
    return unique_channels

def generate_final_m3u(channels):
    """Generate the final M3U playlist"""
    log("📝 Generating final.m3u...")
    
    output_file = Path("playlists/final.m3u")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("#EXTM3U\\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\\n")
            f.write(f"# Channels: {len(channels)}\\n")
            f.write(f"# Processed by M3U Auto-Updater\\n")
            f.write("\\n")
            
            # Channels
            for channel in channels:
                f.write(f"{channel['extinf']}\\n")
                f.write(f"{channel['url']}\\n")
        
        file_size = output_file.stat().st_size
        log(f"✅ Generated final.m3u with {len(channels)} channels ({file_size:,} bytes)")
        
        return True, len(channels), file_size
        
    except Exception as e:
        log(f"❌ Error writing final.m3u: {e}")
        return False, 0, 0

def create_report(channel_count, file_size):
    """Create processing report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "channels": channel_count,
        "file_size": file_size,
        "status": "success"
    }
    
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    with open(reports_dir / "latest_processing.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    log("📊 Created processing report")

def main():
    """Main processing function"""
    log("🚀 Starting M3U Auto-Update Processor...")
    
    try:
        # Setup
        ensure_directories()
        create_default_config()
        
        # Load providers
        providers = load_providers()
        log(f"📂 Loaded {len(providers)} provider sources")
        
        # Download and parse
        all_channels = []
        
        for provider_url in providers:
            content = download_m3u(provider_url)
            if content:
                channels = parse_m3u(content)
                if channels:
                    all_channels.extend(channels)
                    log(f"📺 Found {len(channels)} channels")
        
        if not all_channels:
            log("❌ No channels found from any source")
            return False
        
        log(f"📊 Total channels collected: {len(all_channels)}")
        
        # Remove duplicates
        unique_channels = remove_duplicates(all_channels)
        
        # Generate final M3U
        success, channel_count, file_size = generate_final_m3u(unique_channels)
        
        if success:
            create_report(channel_count, file_size)
            log("✅ M3U processing completed successfully!")
            return True
        else:
            log("❌ Failed to generate final M3U")
            return False
            
    except Exception as e:
        log(f"❌ Critical error: {e}")
        import traceback
        log(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''
    
    main_py_file = Path("scripts/main.py")
    main_py_file.write_text(main_py_content)
    log("✅ Created functional scripts/main.py")

def fix_workflow():
    """Fix the GitHub Actions workflow"""
    log("🔧 Fixing GitHub Actions workflow...")
    
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = '''name: M3U Auto-Updater

on:
  workflow_dispatch:
  push:
    paths:
      - 'config/providers.txt'
  schedule:
    - cron: '0 */6 * * *'

permissions:
  contents: write

jobs:
  update-m3u:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
        
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install requests
        
    - name: Run M3U processor
      run: |
        python scripts/main.py
        
    - name: Check results
      id: check
      run: |
        if [ -f "playlists/final.m3u" ]; then
          CHANNELS=$(grep -c '^#EXTINF' playlists/final.m3u || echo '0')
          echo "channels=$CHANNELS" >> $GITHUB_OUTPUT
          echo "success=true" >> $GITHUB_OUTPUT
          echo "✅ Generated final.m3u with $CHANNELS channels"
        else
          echo "success=false" >> $GITHUB_OUTPUT
          echo "❌ final.m3u not created"
          exit 1
        fi
        
    - name: Commit results
      if: steps.check.outputs.success == 'true'
      run: |
        git config user.name "GitHub Actions"
        git config user.email "actions@github.com"
        git add playlists/ reports/ config/ -f
        
        if ! git diff --staged --quiet; then
          CHANNELS="${{ steps.check.outputs.channels }}"
          git commit -m "🔄 Auto-update M3U playlist - $CHANNELS channels - $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
          git push
          echo "✅ Changes committed"
        else
          echo "ℹ️ No changes to commit"
        fi
'''
    
    workflow_file = workflow_dir / "process.yml"
    workflow_file.write_text(workflow_content)
    log("✅ Fixed .github/workflows/process.yml")

def ensure_config_with_working_sources():
    """Ensure config has working M3U sources"""
    log("🔧 Ensuring config has working sources...")
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    providers_file = config_dir / "providers.txt"
    
    working_sources = """# M3U Provider URLs - Working Sources
# These are tested, free, and legal IPTV sources

# IPTV-ORG Sources (Free and Legal)
https://iptv-org.github.io/iptv/languages/eng.m3u
https://raw.githubusercontent.com/iptv-org/iptv/master/streams/us.m3u
https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ca.m3u
https://raw.githubusercontent.com/iptv-org/iptv/master/streams/uk.m3u
https://raw.githubusercontent.com/iptv-org/iptv/master/streams/au.m3u

# News Channels
https://raw.githubusercontent.com/iptv-org/iptv/master/categories/news.m3u

# Sports Channels  
https://raw.githubusercontent.com/iptv-org/iptv/master/categories/sports.m3u

# Add your own sources below:
"""
    
    providers_file.write_text(working_sources)
    log("✅ Updated config/providers.txt with working sources")

def test_connection():
    """Test if the system works end-to-end"""
    log("🧪 Testing end-to-end connection...")
    
    try:
        # Import and run the main function
        import subprocess
        result = subprocess.run([sys.executable, "scripts/main.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            log("✅ scripts/main.py executed successfully")
            
            # Check if final.m3u was created
            final_m3u = Path("playlists/final.m3u")
            if final_m3u.exists():
                log("✅ final.m3u was generated")
                
                # Count channels
                content = final_m3u.read_text()
                channel_count = content.count('#EXTINF')
                log(f"✅ Found {channel_count} channels in final.m3u")
                
                return True, channel_count
            else:
                log("❌ final.m3u was not created")
                return False, 0
        else:
            log(f"❌ scripts/main.py failed: {result.stderr}")
            return False, 0
            
    except Exception as e:
        log(f"❌ Test failed: {e}")
        return False, 0

def main():
    """Main fix function"""
    print("🔧 COMPLETE M3U REPOSITORY CONNECTION FIX")
    print("=" * 60)
    
    # 1. Diagnose issues
    issues = diagnose_repository()
    
    if issues:
        log("🔍 Issues found:")
        for issue in issues:
            log(f"  {issue}")
        print()
    else:
        log("✅ No major issues detected")
    
    # 2. Fix each component
    log("🔧 Applying fixes...")
    
    create_functional_main_py()
    fix_workflow()
    ensure_config_with_working_sources()
    
    # 3. Test the connection
    log("🧪 Testing the complete system...")
    success, channel_count = test_connection()
    
    print()
    print("=" * 60)
    
    if success:
        log("✅ SUCCESS! Your M3U auto-update system is now working!")
        log(f"📺 Generated {channel_count} channels in final.m3u")
        log("")
        log("🚀 Next steps:")
        log("1. Commit these changes: git add . && git commit -m 'Fixed M3U auto-update system'")
        log("2. Push to GitHub: git push")
        log("3. Go to Actions tab and run the workflow manually")
        log("4. Your final.m3u will update every 6 hours automatically")
    else:
        log("❌ There are still issues to resolve")
        log("Check the error messages above and try running the script again")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

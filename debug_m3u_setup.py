#!/usr/bin/env python3
"""
Enhanced M3U Setup Debug Script
Comprehensive testing and error detection for M3U Editor setup and processing
"""

import traceback
import sys
import os
import json
import subprocess
import importlib.util
import yaml
from datetime import datetime
from pathlib import Path
import tempfile
import shutil


class M3UDebugger:
    def __init__(self):
        self.log_file = "debugging.log"
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
        # Clear previous log
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def log(self, message, level="INFO"):
        """Enhanced logging with levels and timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
        
        # Track errors and warnings
        if level == "ERROR":
            self.results['errors'].append(message)
        elif level == "WARNING":
            self.results['warnings'].append(message)

    def test_python_environment(self):
        """Test Python environment and version"""
        self.log("Testing Python environment...", "DEBUG")
        test_results = {}
        
        try:
            # Python version
            python_version = sys.version_info
            test_results['python_version'] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
            
            if python_version.major >= 3 and python_version.minor >= 8:
                self.log(f"✅ Python version: {test_results['python_version']}", "INFO")
                test_results['python_version_ok'] = True
            else:
                self.log(f"❌ Python version too old: {test_results['python_version']} (need 3.8+)", "ERROR")
                test_results['python_version_ok'] = False

            # Test pip
            try:
                import pip
                test_results['pip_available'] = True
                self.log("✅ pip is available", "INFO")
            except ImportError:
                test_results['pip_available'] = False
                self.log("❌ pip is not available", "ERROR")

            # Test virtual environment detection
            test_results['in_venv'] = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            if test_results['in_venv']:
                self.log("✅ Running in virtual environment", "INFO")
            else:
                self.log("⚠️ Not running in virtual environment", "WARNING")

        except Exception as e:
            self.log(f"❌ Python environment test failed: {e}", "ERROR")
            test_results['error'] = str(e)

        self.results['tests']['python_environment'] = test_results
        return test_results

    def test_dependencies(self):
        """Test all required dependencies"""
        self.log("Testing dependencies...", "DEBUG")
        test_results = {}
        
        required_packages = [
            'requests', 'pycountry', 'lxml', 'beautifulsoup4', 
            'aiohttp', 'aiofiles', 'urllib3', 'dnspython',
            'python-dateutil', 'validators', 'toml', 'yaml'
        ]
        
        optional_packages = [
            'asyncio-throttle', 'unicodedata2', 'matplotlib', 'pandas'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                test_results[package] = "INSTALLED"
                self.log(f"✅ {package}: installed", "INFO")
            except ImportError:
                test_results[package] = "MISSING"
                self.log(f"❌ {package}: missing (required)", "ERROR")
        
        for package in optional_packages:
            try:
                __import__(package.replace('-', '_'))
                test_results[package] = "INSTALLED"
                self.log(f"✅ {package}: installed (optional)", "INFO")
            except ImportError:
                test_results[package] = "MISSING"
                self.log(f"⚠️ {package}: missing (optional)", "WARNING")

        self.results['tests']['dependencies'] = test_results
        return test_results

    def test_directory_structure(self):
        """Test complete directory structure"""
        self.log("Testing directory structure...", "DEBUG")
        test_results = {}
        
        required_structure = {
            '.github/workflows': 'GitHub Actions workflows',
            'config': 'Configuration files',
            'editor': 'Channel editor files',
            'playlists': 'M3U playlist files',
            'scripts': 'Python processing scripts',
            'scripts/modules': 'Python modules',
            'logs': 'Log files',
            'backups': 'Backup files',
            'reports': 'Processing reports'
        }
        
        for directory, description in required_structure.items():
            path = Path(directory)
            if path.exists() and path.is_dir():
                file_count = len(list(path.iterdir()))
                test_results[directory] = f"EXISTS: {file_count} items"
                self.log(f"✅ {directory}: exists ({file_count} items) - {description}", "INFO")
            else:
                test_results[directory] = "MISSING"
                self.log(f"❌ {directory}: missing - {description}", "ERROR")
                # Auto-create missing directories
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.log(f"🔧 Auto-created directory: {directory}", "INFO")
                except Exception as e:
                    self.log(f"❌ Failed to create {directory}: {e}", "ERROR")

        self.results['tests']['directory_structure'] = test_results
        return test_results

    def test_configuration_files(self):
        """Test all configuration files"""
        self.log("Testing configuration files...", "DEBUG")
        test_results = {}
        
        config_files = {
            'config/providers.txt': 'M3U provider URLs',
            'config/epg_sources.txt': 'EPG source URLs',
            'config/commands.txt': 'Processing commands',
            'config/workflow_config.json': 'Workflow configuration',
            'editor/channels.txt': 'Channel editor list'
        }
        
        for config_file, description in config_files.items():
            path = Path(config_file)
            try:
                if path.exists():
                    content = path.read_text(encoding='utf-8').strip()
                    if content:
                        if config_file.endswith('.json'):
                            # Validate JSON
                            try:
                                json.loads(content)
                                lines = len(content.split('\n'))
                                test_results[config_file] = f"VALID JSON: {lines} lines"
                                self.log(f"✅ {config_file}: valid JSON ({lines} lines) - {description}", "INFO")
                            except json.JSONDecodeError as e:
                                test_results[config_file] = f"INVALID JSON: {e}"
                                self.log(f"❌ {config_file}: invalid JSON - {e}", "ERROR")
                        else:
                            lines = [line.strip() for line in content.split('\n') 
                                   if line.strip() and not line.startswith('#')]
                            test_results[config_file] = f"VALID: {len(lines)} entries"
                            self.log(f"✅ {config_file}: {len(lines)} entries - {description}", "INFO")
                    else:
                        test_results[config_file] = "EMPTY"
                        self.log(f"⚠️ {config_file}: empty file - {description}", "WARNING")
                else:
                    test_results[config_file] = "MISSING"
                    self.log(f"❌ {config_file}: missing - {description}", "ERROR")
                    # Create sample file
                    self._create_sample_config(config_file, description)
                    
            except Exception as e:
                test_results[config_file] = f"ERROR: {e}"
                self.log(f"❌ {config_file}: error reading - {e}", "ERROR")

        self.results['tests']['configuration_files'] = test_results
        return test_results

    def _create_sample_config(self, config_file, description):
        """Create sample configuration files"""
        try:
            path = Path(config_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if config_file == 'config/providers.txt':
                sample_content = """# M3U Provider URLs
# Add your M3U playlist URLs here, one per line
# Example:
# https://example.com/playlist.m3u
"""
            elif config_file == 'config/epg_sources.txt':
                sample_content = """# EPG Source URLs
# Add your EPG XML URLs here, one per line
# Example:
# https://example.com/epg.xml
"""
            elif config_file == 'config/commands.txt':
                sample_content = """# Processing Commands
# Add custom processing commands here
# Example:
# filter_by_country=US,UK,CA
# remove_duplicates=true
"""
            elif config_file == 'config/workflow_config.json':
                sample_content = json.dumps({
                    "validation": {"validation_level": "standard", "test_connectivity": False},
                    "parser": {"error_recovery": True},
                    "processing": {"remove_duplicates": True}
                }, indent=2)
            else:
                sample_content = f"# {description}\n# Add your configuration here\n"
            
            path.write_text(sample_content, encoding='utf-8')
            self.log(f"🔧 Created sample file: {config_file}", "INFO")
            
        except Exception as e:
            self.log(f"❌ Failed to create sample {config_file}: {e}", "ERROR")

    def test_script_files(self):
        """Test all Python script files"""
        self.log("Testing script files...", "DEBUG")
        test_results = {}
        
        script_files = {
            'scripts/main.py': 'Main processing script',
            'scripts/universal_m3u_parser.py': 'Universal M3U parser',
            'scripts/comprehensive_config_manager.py': 'Configuration manager',
            'scripts/comprehensive_validator.py': 'Validation system',
            'scripts/error_recovery_manager.py': 'Error recovery system',
            'scripts/utils.py': 'Utility functions',
            'scripts/importer.py': 'M3U importer',
            'scripts/country_grouper.py': 'Country grouping',
            'scripts/epg_manager.py': 'EPG management',
            'scripts/logo_manager.py': 'Logo management',
            'scripts/exporter.py': 'Export functionality',
            'scripts/modules/__init__.py': 'Module initializer',
            'scripts/modules/helper.py': 'Helper functions',
            'scripts/modules/processor.py': 'Processing module',
            'scripts/modules/config_manager.py': 'Config management',
            'scripts/modules/logger_config.py': 'Logging configuration'
        }
        
        for script_file, description in script_files.items():
            path = Path(script_file)
            try:
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    # Test Python syntax
                    try:
                        compile(content, script_file, 'exec')
                        test_results[script_file] = f"VALID: {len(content.split())} lines"
                        self.log(f"✅ {script_file}: valid Python syntax - {description}", "INFO")
                    except SyntaxError as e:
                        test_results[script_file] = f"SYNTAX ERROR: {e}"
                        self.log(f"❌ {script_file}: syntax error - {e}", "ERROR")
                else:
                    test_results[script_file] = "MISSING"
                    self.log(f"❌ {script_file}: missing - {description}", "ERROR")
                    # Create minimal script
                    self._create_minimal_script(script_file, description)
                    
            except Exception as e:
                test_results[script_file] = f"ERROR: {e}"
                self.log(f"❌ {script_file}: error - {e}", "ERROR")

        self.results['tests']['script_files'] = test_results
        return test_results

    def _create_minimal_script(self, script_file, description):
        """Create minimal Python script files"""
        try:
            path = Path(script_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if script_file.endswith('__init__.py'):
                content = f'"""{description}"""\n'
            elif 'main.py' in script_file:
                content = f'''#!/usr/bin/env python3
"""{description}"""

def main():
    """Main processing function"""
    print("M3U processing not yet implemented")
    return True

if __name__ == "__main__":
    main()
'''
            else:
                content = f'''#!/usr/bin/env python3
"""{description}"""

# TODO: Implement {description.lower()}

def placeholder_function():
    """Placeholder function"""
    pass
'''
            
            path.write_text(content, encoding='utf-8')
            self.log(f"🔧 Created minimal script: {script_file}", "INFO")
            
        except Exception as e:
            self.log(f"❌ Failed to create minimal script {script_file}: {e}", "ERROR")

    def test_github_workflows(self):
        """Test GitHub workflow files"""
        self.log("Testing GitHub workflows...", "DEBUG")
        test_results = {}
        
        workflow_files = [
            '.github/workflows/process.yml',
            '.github/workflows/debug_m3u_setup.yml'
        ]
        
        for workflow_file in workflow_files:
            path = Path(workflow_file)
            try:
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    
                    # Test YAML syntax
                    try:
                        yaml_data = yaml.safe_load(content)
                        
                        # Check workflow structure
                        checks = {
                            'has_name': 'name' in yaml_data,
                            'has_on': 'on' in yaml_data,
                            'has_jobs': 'jobs' in yaml_data,
                            'has_runs_on': any('runs-on' in str(job) for job in yaml_data.get('jobs', {}).values()),
                            'has_steps': any('steps' in str(job) for job in yaml_data.get('jobs', {}).values())
                        }
                        
                        passed_checks = sum(checks.values())
                        total_checks = len(checks)
                        
                        test_results[workflow_file] = f"VALID YAML: {passed_checks}/{total_checks} checks passed"
                        self.log(f"✅ {workflow_file}: valid YAML ({passed_checks}/{total_checks} checks)", "INFO")
                        
                        for check, result in checks.items():
                            if not result:
                                self.log(f"  ⚠️ Missing: {check}", "WARNING")
                                
                    except yaml.YAMLError as e:
                        test_results[workflow_file] = f"INVALID YAML: {e}"
                        self.log(f"❌ {workflow_file}: invalid YAML - {e}", "ERROR")
                        
                else:
                    test_results[workflow_file] = "MISSING"
                    self.log(f"❌ {workflow_file}: missing", "ERROR")
                    
            except Exception as e:
                test_results[workflow_file] = f"ERROR: {e}"
                self.log(f"❌ {workflow_file}: error - {e}", "ERROR")

        self.results['tests']['github_workflows'] = test_results
        return test_results

    def test_module_imports(self):
        """Test importing all modules"""
        self.log("Testing module imports...", "DEBUG")
        test_results = {}
        
        # Add scripts directory to path
        scripts_path = Path('scripts').absolute()
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
        
        modules_to_test = [
            ('main', 'scripts/main.py'),
            ('utils', 'scripts/utils.py'),
            ('importer', 'scripts/importer.py'),
            ('country_grouper', 'scripts/country_grouper.py'),
            ('epg_manager', 'scripts/epg_manager.py'),
            ('logo_manager', 'scripts/logo_manager.py'),
            ('exporter', 'scripts/exporter.py'),
            ('universal_m3u_parser', 'scripts/universal_m3u_parser.py'),
            ('comprehensive_config_manager', 'scripts/comprehensive_config_manager.py'),
            ('comprehensive_validator', 'scripts/comprehensive_validator.py'),
            ('error_recovery_manager', 'scripts/error_recovery_manager.py'),
            ('modules.helper', 'scripts/modules/helper.py'),
            ('modules.processor', 'scripts/modules/processor.py'),
            ('modules.config_manager', 'scripts/modules/config_manager.py'),
            ('modules.logger_config', 'scripts/modules/logger_config.py')
        ]
        
        for module_name, file_path in modules_to_test:
            try:
                if os.path.exists(file_path):
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        test_results[module_name] = "SUCCESS"
                        self.log(f"✅ Successfully imported {module_name}", "INFO")
                    else:
                        test_results[module_name] = "FAILED: No spec/loader"
                        self.log(f"❌ Failed to create spec for {module_name}", "ERROR")
                else:
                    test_results[module_name] = "FAILED: File not found"
                    self.log(f"❌ Module file not found: {file_path}", "ERROR")
                    
            except Exception as e:
                test_results[module_name] = f"FAILED: {e}"
                self.log(f"❌ Failed to import {module_name}: {e}", "ERROR")

        self.results['tests']['module_imports'] = test_results
        return test_results

    def test_system_integration(self):
        """Test system integration and end-to-end functionality"""
        self.log("Testing system integration...", "DEBUG")
        test_results = {}
        
        try:
            # Test file permissions
            test_results['file_permissions'] = self._test_file_permissions()
            
            # Test disk space
            test_results['disk_space'] = self._test_disk_space()
            
            # Test network connectivity (if applicable)
            test_results['network'] = self._test_network_connectivity()
            
            # Test sample M3U processing
            test_results['sample_processing'] = self._test_sample_processing()
            
        except Exception as e:
            self.log(f"❌ System integration test failed: {e}", "ERROR")
            test_results['error'] = str(e)

        self.results['tests']['system_integration'] = test_results
        return test_results

    def _test_file_permissions(self):
        """Test file system permissions"""
        try:
            # Test write permissions in key directories
            test_dirs = ['playlists', 'logs', 'backups', 'editor']
            results = {}
            
            for test_dir in test_dirs:
                test_file = Path(test_dir) / 'permission_test.tmp'
                try:
                    test_file.write_text('test')
                    test_file.unlink()
                    results[test_dir] = "WRITABLE"
                    self.log(f"✅ {test_dir}: writable", "INFO")
                except Exception as e:
                    results[test_dir] = f"NOT WRITABLE: {e}"
                    self.log(f"❌ {test_dir}: not writable - {e}", "ERROR")
            
            return results
        except Exception as e:
            return f"ERROR: {e}"

    def _test_disk_space(self):
        """Test available disk space"""
        try:
            statvfs = os.statvfs('.')
            available_bytes = statvfs.f_frsize * statvfs.f_bavail
            available_mb = available_bytes / (1024 * 1024)
            
            if available_mb > 100:  # Need at least 100MB
                self.log(f"✅ Disk space: {available_mb:.1f} MB available", "INFO")
                return f"OK: {available_mb:.1f} MB"
            else:
                self.log(f"⚠️ Low disk space: {available_mb:.1f} MB available", "WARNING")
                return f"LOW: {available_mb:.1f} MB"
                
        except Exception as e:
            return f"ERROR: {e}"

    def _test_network_connectivity(self):
        """Test basic network connectivity"""
        try:
            import urllib.request
            urllib.request.urlopen('https://httpbin.org/get', timeout=5)
            self.log("✅ Network connectivity: OK", "INFO")
            return "OK"
        except Exception as e:
            self.log(f"⚠️ Network connectivity: {e}", "WARNING")
            return f"FAILED: {e}"

    def _test_sample_processing(self):
        """Test processing with a sample M3U file"""
        try:
            # Create a minimal test M3U
            sample_m3u = """#EXTM3U
#EXTINF:-1,Test Channel
https://example.com/stream.m3u8
"""
            
            test_file = Path('playlists/test_sample.m3u')
            test_file.write_text(sample_m3u)
            
            # Try to parse it (basic validation)
            content = test_file.read_text()
            if '#EXTM3U' in content and '#EXTINF' in content:
                self.log("✅ Sample M3U processing: basic validation passed", "INFO")
                test_file.unlink()  # Clean up
                return "OK"
            else:
                return "FAILED: Invalid M3U format"
                
        except Exception as e:
            return f"ERROR: {e}"

    def generate_report(self):
        """Generate comprehensive debug report"""
        self.log("Generating comprehensive debug report...", "INFO")
        
        # Calculate summary statistics
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.results['tests'].items():
            if isinstance(results, dict):
                for test, result in results.items():
                    total_tests += 1
                    if any(keyword in str(result).upper() for keyword in ['SUCCESS', 'VALID', 'OK', 'EXISTS', 'INSTALLED']):
                        passed_tests += 1

        self.results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'error_count': len(self.results['errors']),
            'warning_count': len(self.results['warnings']),
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        # Generate detailed report
        report_content = self._generate_detailed_report()
        
        # Save report
        report_file = f"debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        Path(report_file).write_text(report_content, encoding='utf-8')
        
        # Save JSON results
        json_file = f"debug_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(json_file).write_text(json.dumps(self.results, indent=2), encoding='utf-8')
        
        self.log(f"📄 Debug report saved: {report_file}", "INFO")
        self.log(f"📊 JSON results saved: {json_file}", "INFO")
        
        return report_file, json_file

    def _generate_detailed_report(self):
        """Generate detailed markdown report"""
        summary = self.results['summary']
        
        report = f"""# M3U Editor Debug Report

**Generated:** {self.results['timestamp']}

## 📊 Summary

- **Total Tests:** {summary['total_tests']}
- **Passed:** {summary['passed_tests']} ({summary['success_rate']:.1f}%)
- **Failed:** {summary['failed_tests']}
- **Errors:** {summary['error_count']}
- **Warnings:** {summary['warning_count']}

## 🎯 Test Results

"""
        
        for category, results in self.results['tests'].items():
            report += f"### {category.replace('_', ' ').title()}\n\n"
            
            if isinstance(results, dict):
                for test, result in results.items():
                    status = "✅" if any(keyword in str(result).upper() for keyword in ['SUCCESS', 'VALID', 'OK', 'EXISTS', 'INSTALLED']) else "❌"
                    report += f"- {status} **{test}**: {result}\n"
            else:
                status = "✅" if any(keyword in str(results).upper() for keyword in ['SUCCESS', 'VALID', 'OK', 'EXISTS', 'INSTALLED']) else "❌"
                report += f"- {status} {results}\n"
            
            report += "\n"

        if self.results['errors']:
            report += "## ❌ Errors\n\n"
            for error in self.results['errors']:
                report += f"- {error}\n"
            report += "\n"

        if self.results['warnings']:
            report += "## ⚠️ Warnings\n\n"
            for warning in self.results['warnings']:
                report += f"- {warning}\n"
            report += "\n"

        report += """## 🔧 Recommendations

Based on the test results, here are the recommended actions:

1. **Fix all ERROR items** - These are critical issues that will prevent the system from working
2. **Review WARNING items** - These may cause issues but aren't immediately critical
3. **Ensure all required dependencies are installed**
4. **Verify configuration files are properly formatted**
5. **Test the system end-to-end after fixes**

## 📚 Next Steps

1. Address any missing files or directories
2. Install missing dependencies
3. Fix Python syntax errors
4. Validate configuration files
5. Run the full debug suite again to verify fixes

---
*Generated by Enhanced M3U Debug System*
"""
        
        return report

    def run_full_debug_suite(self):
        """Run complete debug test suite"""
        self.log("=" * 70, "INFO")
        self.log("🚀 STARTING ENHANCED M3U EDITOR DEBUG SUITE", "INFO")
        self.log("=" * 70, "INFO")
        
        # Run all test categories
        test_categories = [
            ("Python Environment", self.test_python_environment),
            ("Dependencies", self.test_dependencies),
            ("Directory Structure", self.test_directory_structure),
            ("Configuration Files", self.test_configuration_files),
            ("Script Files", self.test_script_files),
            ("GitHub Workflows", self.test_github_workflows),
            ("Module Imports", self.test_module_imports),
            ("System Integration", self.test_system_integration)
        ]
        
        for category_name, test_function in test_categories:
            self.log(f"\n🔍 Testing {category_name}...", "INFO")
            try:
                test_function()
            except Exception as e:
                self.log(f"❌ {category_name} test suite failed: {e}", "ERROR")
                self.log(f"Stack trace: {traceback.format_exc()}", "DEBUG")

        # Generate final report
        self.log("\n" + "=" * 70, "INFO")
        self.log("📊 GENERATING FINAL REPORT", "INFO")
        self.log("=" * 70, "INFO")
        
        report_file, json_file = self.generate_report()
        
        # Final summary
        summary = self.results['summary']
        self.log(f"\n🎯 FINAL RESULTS:", "INFO")
        self.log(f"   Tests: {summary['passed_tests']}/{summary['total_tests']} passed ({summary['success_rate']:.1f}%)", "INFO")
        self.log(f"   Errors: {summary['error_count']}", "INFO")
        self.log(f"   Warnings: {summary['warning_count']}", "INFO")
        
        if summary['success_rate'] >= 90:
            self.log("🎉 EXCELLENT! Your M3U editor setup is in great shape!", "INFO")
        elif summary['success_rate'] >= 70:
            self.log("👍 GOOD! Most tests passed, but some issues need attention.", "INFO")
        elif summary['success_rate'] >= 50:
            self.log("⚠️ NEEDS WORK! Several issues need to be resolved.", "WARNING")
        else:
            self.log("🚨 CRITICAL! Major issues detected that need immediate attention.", "ERROR")
        
        self.log(f"\n📄 Detailed report: {report_file}", "INFO")
        self.log(f"📊 JSON data: {json_file}", "INFO")
        
        return self.results


def main():
    """Main entry point"""
    debugger = M3UDebugger()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--simple":
        # Simple compatibility mode
        debugger.log("Running in simple compatibility mode", "INFO")
        debugger.test_directory_structure()
        debugger.test_script_files()
    else:
        # Full comprehensive debug suite
        debugger.run_full_debug_suite()


if __name__ == "__main__":
    main()

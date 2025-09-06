#!/usr/bin/env python3
"""
F1 Scraper Troubleshooting Script
=================================

This script helps diagnose common issues with the F1 scraper.
Run this before the main scraper to identify potential problems.
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*50}")
    print(f"{title}")
    print('='*50)


def check_python_version():
    """Check Python version compatibility."""
    print_header("PYTHON VERSION CHECK")
    
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ISSUE: Python 3.8 or higher is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True


def check_dependencies():
    """Check if required dependencies are installed."""
    print_header("DEPENDENCY CHECK")
    
    required_packages = {
        'requests': 'HTTP requests library',
        'bs4': 'BeautifulSoup HTML parsing',
        'lxml': 'XML/HTML parser for BeautifulSoup',
        'urllib3': 'HTTP client library',
        'certifi': 'SSL certificates'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✅ {package:<12} - {description}")
        except ImportError:
            print(f"❌ {package:<12} - MISSING: {description}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def check_network_connectivity():
    """Check network connectivity to F1 website."""
    print_header("NETWORK CONNECTIVITY CHECK")
    
    try:
        import requests
        
        # Test basic connectivity
        test_url = "https://www.formula1.com"
        print(f"Testing connection to: {test_url}")
        
        response = requests.get(test_url, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response Size: {len(response.content)} bytes")
        
        # Test specific scraping endpoint
        scrape_url = "https://www.formula1.com/en/results/2025/races"
        print(f"\nTesting scraping endpoint: {scrape_url}")
        
        response = requests.get(scrape_url, timeout=15)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Content Type: {response.headers.get('content-type', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Network connectivity failed: {e}")
        return False


def check_file_permissions():
    """Check file system permissions."""
    print_header("FILE PERMISSIONS CHECK")
    
    # Check current directory write permissions
    try:
        test_file = Path("test_permissions.tmp")
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Current directory is writable")
    except Exception as e:
        print(f"❌ Cannot write to current directory: {e}")
        return False
    
    # Check output directory
    output_dir = Path("output")
    try:
        output_dir.mkdir(exist_ok=True)
        test_file = output_dir / "test_permissions.tmp"
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Output directory is writable")
    except Exception as e:
        print(f"❌ Cannot write to output directory: {e}")
        return False
    
    return True


def check_scraper_import():
    """Check if the main scraper can be imported."""
    print_header("SCRAPER IMPORT CHECK")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path.cwd()))
        
        # Try to import the scraper
        from f1_scraper_pro import F1ResultsScraperPro, RaceResult
        print("✅ F1ResultsScraperPro imported successfully")
        
        # Try to create an instance
        scraper = F1ResultsScraperPro(year=2025, rate_limit=0.1)
        print("✅ Scraper instance created successfully")
        print(f"✅ Base URL: {scraper.base_url}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import scraper: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating scraper instance: {e}")
        return False


def check_environment():
    """Check environment variables and settings."""
    print_header("ENVIRONMENT CHECK")
    
    print(f"Operating System: {os.name}")
    print(f"Platform: {sys.platform}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Python Executable: {sys.executable}")
    
    # Check environment variables
    env_vars = [
        'F1_DEFAULT_YEAR',
        'F1_OUTPUT_DIR',
        'F1_LOG_LEVEL',
        'F1_RATE_LIMIT'
    ]
    
    print("\nEnvironment Variables:")
    for var in env_vars:
        value = os.getenv(var, 'Not set')
        print(f"  {var}: {value}")
    
    return True


def run_basic_test():
    """Run a basic scraper test."""
    print_header("BASIC SCRAPER TEST")
    
    try:
        sys.path.insert(0, str(Path.cwd()))
        from f1_scraper_pro import F1ResultsScraperPro
        
        # Create scraper with test settings
        scraper = F1ResultsScraperPro(
            year=2024,  # Use 2024 as it likely has data
            output_dir="test_output",
            log_level="DEBUG",
            rate_limit=2.0  # Slower rate for testing
        )
        
        print("✅ Scraper initialized")
        
        # Test URL fetching (without full scrape)
        test_url = scraper.base_url
        soup = scraper.fetch_page(test_url)
        
        if soup:
            print("✅ Successfully fetched test page")
            print(f"✅ Page title: {soup.title.string if soup.title else 'No title'}")
            return True
        else:
            print("❌ Failed to fetch test page")
            return False
            
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False


def main():
    """Run all diagnostic checks."""
    print_header("F1 SCRAPER TROUBLESHOOTING")
    print("This script will diagnose common issues with the F1 scraper")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Network Connectivity", check_network_connectivity),
        ("File Permissions", check_file_permissions),
        ("Scraper Import", check_scraper_import),
        ("Environment", check_environment),
        ("Basic Test", run_basic_test)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} check crashed: {e}")
            results[check_name] = False
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}")
    print()
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    if passed == total:
        print("\n🎉 All checks passed! The scraper should work correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
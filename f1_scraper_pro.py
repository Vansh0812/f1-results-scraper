"""
F1 Results Scraper - Enhanced Professional Version
================================================

A robust web scraper for Formula 1 race results with comprehensive error handling,
data validation, and multiple output formats.

Author: Vansh Jain
Version: 2.0.0
License: MIT
"""

import logging
import time
import sys
import json
import csv
import requests
import os
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Suppress SSL warnings for older sites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class RaceResult:
    """Data class for race results with proper typing."""
    date: str
    grand_prix: str
    winner: str
    car: str = ""
    time: str = ""
    scraped_at: str = ""
    
    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()


class F1ResultsScraperPro:
    """
    Professional Formula 1 Results Scraper
    
    Features:
    - Robust error handling and retry logic
    - Multiple output formats (CSV, JSON, Excel)
    - Comprehensive logging
    - Data validation and cleaning
    - Rate limiting for responsible scraping
    - Multiple year support
    - Configurable via environment variables or CLI
    """
    
    DEFAULT_BASE_URL = "https://www.formula1.com/en/results/{year}/races"
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    def __init__(self, 
                 year: int = 2025,
                 output_dir: str = "output",
                 log_level: str = "INFO",
                 rate_limit: float = 1.0):
        """
        Initialize the F1 Results Scraper.
        
        Args:
            year: Year to scrape results for
            output_dir: Directory to save output files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            rate_limit: Delay between requests in seconds
        """
        self.year = year
        self.output_dir = Path(output_dir)
        self.rate_limit = rate_limit
        self.base_url = self.DEFAULT_BASE_URL.format(year=year)
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize session with retry strategy
        self.session = self._setup_session()
        
        # Initialize results storage
        self.results: List[RaceResult] = []
        
        # Setup logging
        self.logger = self._setup_logging(log_level)
        
        self.logger.info(f"F1 Results Scraper initialized for year {year}")
    
    def _setup_session(self) -> requests.Session:
        """Setup requests session with retry strategy and proper headers."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update(self.DEFAULT_HEADERS)
        
        return session
    
    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup comprehensive logging configuration."""
        log_file = self.output_dir / f"f1_scraper_{self.year}.log"
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup logger
        logger = logging.getLogger(f"F1Scraper_{self.year}")
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def fetch_page(self, url: str, timeout: int = 15) -> Optional[BeautifulSoup]:
        """
        Fetch a webpage with proper error handling and rate limiting.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            self.logger.info(f"Fetching: {url}")
            
            # Rate limiting
            time.sleep(self.rate_limit)
            
            response = self.session.get(url, timeout=timeout, verify=False)
            response.raise_for_status()
            
            # Check if we got actual HTML content
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                self.logger.warning(f"Unexpected content type: {content_type}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            self.logger.info(f"Successfully fetched page (size: {len(response.content)} bytes)")
            
            return soup
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout while fetching {url}")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error while fetching {url}")
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error {e.response.status_code} while fetching {url}")
        except Exception as e:
            self.logger.error(f"Unexpected error while fetching {url}: {e}")
        
        return None
    
    def extract_race_results(self, soup: BeautifulSoup) -> List[RaceResult]:
        """
        Extract race results from the page with improved parsing logic.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of RaceResult objects
        """
        results = []
        
        try:
            # Multiple selectors to try
            table_selectors = [
                'table.resultsarchive-table',
                'table[class*="results"]',
                'table[class*="archive"]',
                '.results-table table',
                'table'
            ]
            
            results_table = None
            for selector in table_selectors:
                results_table = soup.select_one(selector)
                if results_table:
                    self.logger.info(f"Found results table using selector: {selector}")
                    break
            
            if not results_table:
                self.logger.error("No results table found")
                self._save_debug_html(soup)
                return results
            
            # Extract rows
            tbody = results_table.find('tbody')
            rows = tbody.find_all('tr') if tbody else results_table.find_all('tr')[1:]
            
            self.logger.info(f"Found {len(rows)} potential race rows")
            
            for i, row in enumerate(rows):
                try:
                    race_result = self._parse_race_row(row)
                    if race_result:
                        results.append(race_result)
                        self.logger.info(f"Extracted: {race_result.grand_prix} - Winner: {race_result.winner}")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse row {i+1}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error extracting race results: {e}")
            self._save_debug_html(soup)
        
        return results
    
    def _parse_race_row(self, row) -> Optional[RaceResult]:
        """
        Parse individual race row with enhanced logic.
        
        Args:
            row: BeautifulSoup row element
            
        Returns:
            RaceResult object or None
        """
        try:
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 3:
                return None
            
            cell_texts = [self._clean_text(cell.get_text()) for cell in cells]
            
            # Skip header rows
            if any(text.upper() in ['GRAND PRIX', 'DATE', 'WINNER'] for text in cell_texts[:3]):
                return None
            
            # Initialize variables
            grand_prix = ""
            race_date = ""
            winner = ""
            car = ""
            time = ""
            
            # Improved parsing logic based on common F1 table structures
            if len(cell_texts) >= 5:
                # Full table: Date, Grand Prix, Winner, Car, Time/Points
                race_date = cell_texts[0]
                grand_prix = cell_texts[1]
                winner = cell_texts[2]
                car = cell_texts[3] if len(cell_texts) > 3 else ""
                time = cell_texts[4] if len(cell_texts) > 4 else ""
            elif len(cell_texts) >= 3:
                # Basic table: Grand Prix, Date, Winner
                grand_prix = cell_texts[0]
                race_date = cell_texts[1]
                winner = cell_texts[2]
            
            # Validate essential fields
            if not all([grand_prix, winner]) or grand_prix.upper() in ['GRAND PRIX', 'GP']:
                return None
            
            # Clean and validate date
            race_date = self._clean_date(race_date)
            
            return RaceResult(
                date=race_date,
                grand_prix=self._clean_text(grand_prix),
                winner=self._clean_text(winner),
                car=self._clean_text(car),
                time=self._clean_text(time)
            )
            
        except Exception as e:
            self.logger.debug(f"Error parsing race row: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text data."""
        if not text:
            return ""
        return ' '.join(text.strip().split())
    
    def _clean_date(self, date_str: str) -> str:
        """Clean and validate date string."""
        cleaned = self._clean_text(date_str)
        
        # Basic date validation - contains month abbreviation or numbers
        date_indicators = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        if any(month in cleaned for month in date_indicators) or any(char.isdigit() for char in cleaned):
            return cleaned
        
        return "Date TBD"
    
    def _save_debug_html(self, soup: BeautifulSoup) -> None:
        """Save HTML for debugging purposes."""
        debug_file = self.output_dir / f"debug_page_{self.year}.html"
        try:
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            self.logger.info(f"Debug HTML saved to {debug_file}")
        except Exception as e:
            self.logger.error(f"Failed to save debug HTML: {e}")
    
    def validate_results(self) -> Tuple[bool, List[str]]:
        """
        Validate scraped results.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not self.results:
            issues.append("No results found")
            return False, issues
        
        # Check for required fields
        for i, result in enumerate(self.results):
            if not result.grand_prix.strip():
                issues.append(f"Result {i+1}: Missing Grand Prix name")
            
            if not result.winner.strip():
                issues.append(f"Result {i+1}: Missing winner")
            
            if not result.date.strip():
                issues.append(f"Result {i+1}: Missing date")
        
        # Check for duplicates
        seen_races = set()
        for result in self.results:
            race_key = result.grand_prix.lower().strip()
            if race_key in seen_races:
                issues.append(f"Duplicate race found: {result.grand_prix}")
            seen_races.add(race_key)
        
        is_valid = len(issues) == 0
        self.logger.info(f"Validation {'passed' if is_valid else 'failed'} for {len(self.results)} results")
        
        if issues:
            self.logger.warning(f"Validation issues: {issues}")
        
        return is_valid, issues
    
    def save_to_csv(self, filename: Optional[str] = None) -> bool:
        """Save results to CSV file."""
        if not filename:
            filename = f"f1_{self.year}_results.csv"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if not self.results:
                    self.logger.warning("No results to save to CSV")
                    return False
                
                fieldnames = ['date', 'grand_prix', 'winner', 'car', 'time', 'scraped_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in self.results:
                    writer.writerow(asdict(result))
                
            self.logger.info(f"Results saved to CSV: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save CSV: {e}")
            return False
    
    def save_to_json(self, filename: Optional[str] = None) -> bool:
        """Save results to JSON file with metadata."""
        if not filename:
            filename = f"f1_{self.year}_results.json"
        
        filepath = self.output_dir / filename
        
        try:
            data = {
                'metadata': {
                    'scraped_at': datetime.now().isoformat(),
                    'source_url': self.base_url,
                    'year': self.year,
                    'total_races': len(self.results),
                    'scraper_version': '2.0.0'
                },
                'results': [asdict(result) for result in self.results]
            }
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Results saved to JSON: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save JSON: {e}")
            return False
    
    def scrape(self) -> bool:
        """
        Main scraping method.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Starting F1 {self.year} results scraping...")
        
        try:
            # Fetch the main page
            soup = self.fetch_page(self.base_url)
            if not soup:
                self.logger.error("Failed to fetch the main results page")
                return False
            
            # Extract results
            self.results = self.extract_race_results(soup)
            
            if not self.results:
                self.logger.error("No race results were extracted")
                return False
            
            # Validate results
            is_valid, issues = self.validate_results()
            if not is_valid:
                self.logger.warning(f"Validation issues found: {issues}")
            
            # Save results
            csv_success = self.save_to_csv()
            json_success = self.save_to_json()
            
            if csv_success and json_success:
                self.logger.info(f"Successfully scraped {len(self.results)} race results for {self.year}")
                return True
            else:
                self.logger.error("Failed to save some results")
                return False
                
        except Exception as e:
            self.logger.error(f"Unexpected error during scraping: {e}")
            return False
    
    def get_results(self) -> List[Dict]:
        """Return the scraped results as dictionaries."""
        return [asdict(result) for result in self.results]
    
    def get_summary(self) -> Dict:
        """Get summary statistics of the scraped data."""
        if not self.results:
            return {'total_races': 0, 'winners': {}, 'cars': {}}
        
        winners = {}
        cars = {}
        
        for result in self.results:
            # Count winners
            winner = result.winner
            winners[winner] = winners.get(winner, 0) + 1
            
            # Count cars (if available)
            if result.car:
                car = result.car
                cars[car] = cars.get(car, 0) + 1
        
        return {
            'total_races': len(self.results),
            'unique_winners': len(winners),
            'winners': dict(sorted(winners.items(), key=lambda x: x[1], reverse=True)),
            'cars': dict(sorted(cars.items(), key=lambda x: x[1], reverse=True)) if cars else {}
        }


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Professional F1 Results Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--year', '-y',
        type=int,
        default=2025,
        help='Year to scrape results for (default: 2025)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='output',
        help='Output directory for results (default: output)'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--rate-limit', '-r',
        type=float,
        default=1.0,
        help='Rate limit between requests in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--summary', '-s',
        action='store_true',
        help='Show summary statistics after scraping'
    )
    
    return parser


def main():
    """Main function with CLI support."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    print("=" * 60)
    print("F1 Results Scraper Professional v2.0.0")
    print("=" * 60)
    print(f"Year: {args.year}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Log Level: {args.log_level}")
    print("-" * 60)
    
    # Initialize scraper
    scraper = F1ResultsScraperPro(
        year=args.year,
        output_dir=args.output_dir,
        log_level=args.log_level,
        rate_limit=args.rate_limit
    )
    
    # Run scraper
    success = scraper.scrape()
    
    if success:
        results = scraper.get_results()
        print(f"\n✅ Successfully scraped {len(results)} race results!")
        
        # Show sample results
        print(f"\n📊 Sample Results for {args.year}:")
        for i, result in enumerate(results[:5]):
            print(f"{i+1:2d}. {result['grand_prix']:<25} ({result['date']:<12}) - {result['winner']}")
        
        if len(results) > 5:
            print(f"     ... and {len(results) - 5} more races")
        
        # Show summary if requested
        if args.summary:
            summary = scraper.get_summary()
            print(f"\n📈 Summary Statistics:")
            print(f"   Total Races: {summary['total_races']}")
            print(f"   Unique Winners: {summary['unique_winners']}")
            
            if summary['winners']:
                print(f"\n🏆 Top Winners:")
                for winner, count in list(summary['winners'].items())[:5]:
                    print(f"   {winner}: {count} wins")
        
        print(f"\n💾 Output Files:")
        print(f"   📄 CSV: {args.output_dir}/f1_{args.year}_results.csv")
        print(f"   📄 JSON: {args.output_dir}/f1_{args.year}_results.json")
        print(f"   📄 Log: {args.output_dir}/f1_scraper_{args.year}.log")
        
    else:
        print(f"\n❌ Scraping failed for year {args.year}")
        print(f"Check the log file for details: {args.output_dir}/f1_scraper_{args.year}.log")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
import logging, time, sys, json, csv, requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class F1ResultsScraper:
 
    def __init__(self, base_url: str = "https://www.formula1.com/en/results/2025/races"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results: List[Dict[str, str]] = []
        self.setup_logging()
        self.setup_session()
    
    def setup_logging(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('f1_scraper.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_session(self) -> None:
        self.session.headers.update({
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
        })
    
    def fetch_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        for attempt in range(retries):
            try:
                self.logger.info(f"Fetching {url} (attempt {attempt + 1}/{retries})")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                # Add delay to be respectful to the server
                time.sleep(1)
                
                return BeautifulSoup(response.content, 'html.parser')
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    self.logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
                time.sleep(2)

        return None
    
    def extract_race_results(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        results = []
        
        try:
            results_table = None
            
            selectors = [
                'table.resultsarchive-table',
                'table',
                '.results-table',
                '[class*="result"]'
            ]
            
            for selector in selectors:
                results_table = soup.select_one(selector)
                if results_table:
                    self.logger.info(f"Found results table using selector: {selector}")
                    break
            
            if not results_table:
                all_tables = soup.find_all('table')
                if all_tables:
                    results_table = all_tables[0]
                    self.logger.info("Using first available table")
                else:
                    self.logger.error("No results table found on the page")
                    self.logger.info(f"Page title: {soup.title.string if soup.title else 'No title'}")
                    self.logger.info(f"Available text content preview: {soup.get_text()[:500]}")
                    return results
            
            tbody = results_table.find('tbody')
            if tbody:
                race_rows = tbody.find_all('tr')
            else:
                race_rows = results_table.find_all('tr')[1:]
            
            self.logger.info(f"Found {len(race_rows)} race rows to process")
            
            for i, row in enumerate(race_rows):
                try:
                    race_data = self.parse_race_row(row)
                    if race_data:
                        results.append(race_data)
                        self.logger.info(f"Extracted: {race_data['grand_prix']} - Winner: {race_data['winner']}")
                    else:
                        self.logger.warning(f"Row {i+1} returned no data")
                
                except Exception as e:
                    self.logger.warning(f"Failed to parse race row {i+1}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error extracting race results: {e}")
        
        return results
    
    def parse_race_row(self, row) -> Optional[Dict[str, str]]:
        try:
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 3:
                self.logger.debug(f"Row has only {len(cells)} cells, skipping")
                return None
            
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            self.logger.debug(f"Row cells: {cell_texts}")

            grand_prix = ""
            race_date = ""
            winner = ""
            
            date_patterns = []
            for i, cell_text in enumerate(cell_texts):
                if any(month in cell_text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                    date_patterns.append((i, cell_text))
            
            if len(cells) >= 6:
                grand_prix = self.clean_text(cells[0].get_text(strip=True))
                race_date = self.clean_text(cells[1].get_text(strip=True))
                winner = self.clean_text(cells[2].get_text(strip=True))
            elif len(cells) >= 3:
                if date_patterns:
                    date_idx = date_patterns[0][0]
                    if date_idx == 0:  
                        race_date = self.clean_text(cells[0].get_text(strip=True))
                        grand_prix = self.clean_text(cells[1].get_text(strip=True))
                        winner = self.clean_text(cells[2].get_text(strip=True))
                    elif date_idx == 1: 
                        grand_prix = self.clean_text(cells[0].get_text(strip=True))
                        race_date = self.clean_text(cells[1].get_text(strip=True))
                        winner = self.clean_text(cells[2].get_text(strip=True))
                else:
                    grand_prix = self.clean_text(cells[0].get_text(strip=True))
                    winner = self.clean_text(cells[1].get_text(strip=True))
                    race_date = self.clean_text(cells[2].get_text(strip=True)) if len(cells) > 2 else "Unknown"
            
            if not grand_prix or not winner or grand_prix in ['GRAND PRIX', 'Grand Prix', 'GP']:
                self.logger.debug(f"Skipping row - insufficient data: GP='{grand_prix}', Winner='{winner}'")
                return None
            
            race_data = {
                'date': self.clean_date(race_date),
                'grand_prix': self.clean_text(grand_prix),
                'winner': self.clean_text(winner),
                'scraped_at': datetime.now().isoformat()
            }
            
            return race_data
            
        except Exception as e:
            self.logger.warning(f"Error parsing race row: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        return ' '.join(text.split()).strip()
    
    def clean_date(self, date_str: str) -> str:
        cleaned = self.clean_text(date_str)
        return cleaned
    
    def validate_results(self) -> bool:
        if not self.results:
            self.logger.error("No results found to validate")
            return False
        
        for i, result in enumerate(self.results):
            required_fields = ['date', 'grand_prix', 'winner']
            
            for field in required_fields:
                if not result.get(field) or not result[field].strip():
                    self.logger.warning(f"Missing or empty {field} in result {i + 1}")
                    return False
        
        self.logger.info(f"Validation passed for {len(self.results)} results")
        return True
    
    def save_to_csv(self, filename: str = 'f1_2025_results.csv') -> bool:
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if not self.results:
                    self.logger.warning("No results to save")
                    return False
                
                fieldnames = ['date', 'grand_prix', 'winner', 'scraped_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(self.results)
                
            self.logger.info(f"Results saved to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save CSV: {e}")
            return False
    
    def save_to_json(self, filename: str = 'f1_2025_results.json') -> bool:
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump({
                    'scraping_metadata': {
                        'scraped_at': datetime.now().isoformat(),
                        'source_url': self.base_url,
                        'total_races': len(self.results)
                    },
                    'results': self.results
                }, jsonfile, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Results saved to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save JSON: {e}")
            return False
    
    def scrape(self) -> bool:
        self.logger.info("Starting F1 2025 results scraping...")
        
        try:
            soup = self.fetch_page(self.base_url)
            if not soup:
                self.logger.error("Failed to fetch the main results page")
                return False
            
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(str(soup))
            self.logger.info("Saved page HTML to debug_page.html for inspection")
            
            self.results = self.extract_race_results(soup)
            
            if not self.results:
                self.logger.error("No race results were extracted")
                self.logger.info("The page might be using JavaScript to load content.")
                self.logger.info("Try checking debug_page.html to see what was actually fetched.")
                return False
            
            if not self.validate_results():
                self.logger.warning("Results validation failed, but continuing with available data")
            
            csv_success = self.save_to_csv()
            json_success = self.save_to_json()
            
            if csv_success and json_success:
                self.logger.info(f"Successfully scraped {len(self.results)} race results")
                return True
            else:
                self.logger.error("Failed to save results")
                return False
                
        except Exception as e:
            self.logger.error(f"Unexpected error during scraping: {e}")
            return False
    
    def get_results(self) -> List[Dict[str, str]]:
        """Return the scraped results."""
        return self.results


def main():
    """Main function to run the scraper."""
    print("F1 2025 Season Results Scraper")
    print("=" * 40)
    
    scraper = F1ResultsScraper()
    success = scraper.scrape()
    
    if success:
        results = scraper.get_results()
        print(f"\nSuccessfully scraped {len(results)} race results!")
        print("\nSample results:")
        for i, result in enumerate(results[:3]):
            print(f"{i+1}. {result['grand_prix']} ({result['date']}) - Winner: {result['winner']}")
        
        if len(results) > 3:
            print(f"... and {len(results) - 3} more races")
        
        print("\nFiles created:")
        print("- f1_2025_results.csv")
        print("- f1_2025_results.json")
        print("- f1_scraper.log")
    else:
        print("\nScraping failed. Check f1_scraper.log for details.")
    
    return success


if __name__ == "__main__":
    main()
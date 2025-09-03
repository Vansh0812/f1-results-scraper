"""
Test suite for F1 Results Scraper Professional
==============================================

Run with: pytest tests/test_f1_scraper.py -v
"""

import pytest
import tempfile
import json
import csv
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
import requests

# Import the main scraper class
import sys
sys.path.append('..')
from f1_scraper_pro import F1ResultsScraperPro, RaceResult


class TestF1ResultsScraperPro:
    """Test cases for the main scraper class."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def scraper(self, temp_output_dir):
        """Create a scraper instance for testing."""
        return F1ResultsScraperPro(
            year=2024,
            output_dir=temp_output_dir,
            log_level="DEBUG",
            rate_limit=0.1  # Faster for tests
        )
    
    @pytest.fixture
    def sample_html(self):
        """Sample HTML content for testing."""
        return """
        <html>
        <head><title>F1 Results 2024</title></head>
        <body>
            <table class="resultsarchive-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Grand Prix</th>
                        <th>Winner</th>
                        <th>Car</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>02 Mar</td>
                        <td>Bahrain Grand Prix</td>
                        <td>Max Verstappen VER</td>
                        <td>Red Bull Racing Honda RBPT</td>
                        <td>1:31:44.742</td>
                    </tr>
                    <tr>
                        <td>09 Mar</td>
                        <td>Saudi Arabian Grand Prix</td>
                        <td>Sergio Perez PER</td>
                        <td>Red Bull Racing Honda RBPT</td>
                        <td>1:20:43.273</td>
                    </tr>
                    <tr>
                        <td>24 Mar</td>
                        <td>Australian Grand Prix</td>
                        <td>Carlos Sainz SAI</td>
                        <td>Ferrari</td>
                        <td>1:20:26.843</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
    
    def test_initialization(self, temp_output_dir):
        """Test scraper initialization."""
        scraper = F1ResultsScraperPro(
            year=2024,
            output_dir=temp_output_dir,
            log_level="INFO",
            rate_limit=1.0
        )
        
        assert scraper.year == 2024
        assert scraper.output_dir == Path(temp_output_dir)
        assert scraper.rate_limit == 1.0
        assert scraper.base_url == "https://www.formula1.com/en/results/2024/races"
        assert scraper.results == []
        assert scraper.logger is not None
    
    def test_session_setup(self, scraper):
        """Test HTTP session setup."""
        session = scraper.session
        
        assert session is not None
        assert isinstance(session, requests.Session)
        assert 'User-Agent' in session.headers
        assert 'Mozilla' in session.headers['User-Agent']
    
    @patch('f1_scraper_pro.time.sleep')
    @patch('requests.Session.get')
    def test_fetch_page_success(self, mock_get, mock_sleep, scraper, sample_html):
        """Test successful page fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.content = sample_html.encode('utf-8')
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test fetch
        soup = scraper.fetch_page("https://example.com")
        
        assert soup is not None
        assert isinstance(soup, BeautifulSoup)
        assert "F1 Results 2024" in str(soup)
        mock_sleep.assert_called_once_with(scraper.rate_limit)
    
    @patch('f1_scraper_pro.time.sleep')
    @patch('requests.Session.get')
    def test_fetch_page_failure(self, mock_get, mock_sleep, scraper):
        """Test page fetching failure."""
        # Mock request exception
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        # Test fetch
        soup = scraper.fetch_page("https://example.com")
        
        assert soup is None
    
    def test_parse_race_row_success(self, scraper):
        """Test successful race row parsing."""
        html = """
        <tr>
            <td>02 Mar</td>
            <td>Bahrain Grand Prix</td>
            <td>Max Verstappen VER</td>
            <td>Red Bull Racing Honda RBPT</td>
            <td>1:31:44.742</td>
        </tr>
        """
        soup = BeautifulSoup(html, 'html.parser')
        row = soup.find('tr')
        
        result = scraper._parse_race_row(row)
        
        assert result is not None
        assert isinstance(result, RaceResult)
        assert result.date == "02 Mar"
        assert result.grand_prix == "Bahrain Grand Prix"
        assert result.winner == "Max Verstappen VER"
        assert result.car == "Red Bull Racing Honda RBPT"
        assert result.time == "1:31:44.742"
    
    def test_parse_race_row_insufficient_data(self, scraper):
        """Test race row parsing with insufficient data."""
        html = "<tr><td>Test</td></tr>"
        soup = BeautifulSoup(html, 'html.parser')
        row = soup.find('tr')
        
        result = scraper._parse_race_row(row)
        
        assert result is None
    
    def test_extract_race_results(self, scraper, sample_html):
        """Test race results extraction."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        results = scraper.extract_race_results(soup)
        
        assert len(results) == 3
        assert all(isinstance(result, RaceResult) for result in results)
        
        # Check first result
        first_result = results[0]
        assert first_result.grand_prix == "Bahrain Grand Prix"
        assert first_result.winner == "Max Verstappen VER"
        assert first_result.date == "02 Mar"
    
    def test_clean_text(self, scraper):
        """Test text cleaning functionality."""
        # Test normal text
        assert scraper._clean_text("  Normal text  ") == "Normal text"
        
        # Test empty/None text
        assert scraper._clean_text("") == ""
        assert scraper._clean_text(None) == ""
        
        # Test text with multiple spaces
        assert scraper._clean_text("Multiple   spaces   here") == "Multiple spaces here"
    
    def test_clean_date(self, scraper):
        """Test date cleaning functionality."""
        # Valid dates
        assert scraper._clean_date("02 Mar") == "02 Mar"
        assert scraper._clean_date("  15 December  ") == "15 December"
        assert scraper._clean_date("2024-03-15") == "2024-03-15"
        
        # Invalid dates
        assert scraper._clean_date("Invalid") == "Date TBD"
        assert scraper._clean_date("") == "Date TBD"
    
    def test_validate_results_success(self, scraper):
        """Test successful results validation."""
        scraper.results = [
            RaceResult(
                date="02 Mar",
                grand_prix="Bahrain Grand Prix",
                winner="Max Verstappen"
            ),
            RaceResult(
                date="09 Mar",
                grand_prix="Saudi Arabian Grand Prix",
                winner="Sergio Perez"
            )
        ]
        
        is_valid, issues = scraper.validate_results()
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_validate_results_failure(self, scraper):
        """Test results validation with errors."""
        scraper.results = [
            RaceResult(date="", grand_prix="Test GP", winner=""),
            RaceResult(date="02 Mar", grand_prix="", winner="Driver")
        ]
        
        is_valid, issues = scraper.validate_results()
        
        assert is_valid is False
        assert len(issues) > 0
    
    def test_save_to_csv(self, scraper):
        """Test CSV saving functionality."""
        scraper.results = [
            RaceResult(
                date="02 Mar",
                grand_prix="Bahrain Grand Prix",
                winner="Max Verstappen",
                car="Red Bull Racing",
                time="1:31:44.742"
            )
        ]
        
        success = scraper.save_to_csv("test_results.csv")
        
        assert success is True
        
        # Verify file exists and content
        csv_file = scraper.output_dir / "test_results.csv"
        assert csv_file.exists()
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        assert len(rows) == 1
        assert rows[0]['grand_prix'] == "Bahrain Grand Prix"
        assert rows[0]['winner'] == "Max Verstappen"
    
    def test_save_to_json(self, scraper):
        """Test JSON saving functionality."""
        scraper.results = [
            RaceResult(
                date="02 Mar",
                grand_prix="Bahrain Grand Prix",
                winner="Max Verstappen"
            )
        ]
        
        success = scraper.save_to_json("test_results.json")
        
        assert success is True
        
        # Verify file exists and content
        json_file = scraper.output_dir / "test_results.json"
        assert json_file.exists()
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'metadata' in data
        assert 'results' in data
        assert data['metadata']['year'] == scraper.year
        assert len(data['results']) == 1
        assert data['results'][0]['grand_prix'] == "Bahrain Grand Prix"
    
    def test_get_summary(self, scraper):
        """Test summary statistics generation."""
        scraper.results = [
            RaceResult(date="02 Mar", grand_prix="Bahrain GP", winner="Max Verstappen", car="Red Bull"),
            RaceResult(date="09 Mar", grand_prix="Saudi GP", winner="Max Verstappen", car="Red Bull"),
            RaceResult(date="24 Mar", grand_prix="Australian GP", winner="Carlos Sainz", car="Ferrari")
        ]
        
        summary = scraper.get_summary()
        
        assert summary['total_races'] == 3
        assert summary['unique_winners'] == 2
        assert summary['winners']['Max Verstappen'] == 2
        assert summary['winners']['Carlos Sainz'] == 1
        assert summary['cars']['Red Bull'] == 2
        assert summary['cars']['Ferrari'] == 1
    
    def test_get_summary_empty(self, scraper):
        """Test summary with no results."""
        summary = scraper.get_summary()
        
        assert summary['total_races'] == 0
        assert summary['winners'] == {}
        assert summary['cars'] == {}
    
    @patch('f1_scraper_pro.F1ResultsScraperPro.fetch_page')
    def test_scrape_integration(self, mock_fetch, scraper, sample_html):
        """Test complete scraping workflow."""
        # Mock successful page fetch
        soup = BeautifulSoup(sample_html, 'html.parser')
        mock_fetch.return_value = soup
        
        # Run scraper
        success = scraper.scrape()
        
        assert success is True
        assert len(scraper.results) == 3
        
        # Verify output files were created
        csv_file = scraper.output_dir / f"f1_{scraper.year}_results.csv"
        json_file = scraper.output_dir / f"f1_{scraper.year}_results.json"
        
        assert csv_file.exists()
        assert json_file.exists()


class TestRaceResult:
    """Test cases for the RaceResult data class."""
    
    def test_race_result_creation(self):
        """Test RaceResult creation with required fields."""
        result = RaceResult(
            date="02 Mar",
            grand_prix="Bahrain Grand Prix",
            winner="Max Verstappen"
        )
        
        assert result.date == "02 Mar"
        assert result.grand_prix == "Bahrain Grand Prix"
        assert result.winner == "Max Verstappen"
        assert result.car == ""
        assert result.time == ""
        assert result.scraped_at != ""  # Should be auto-populated
    
    def test_race_result_with_optional_fields(self):
        """Test RaceResult creation with all fields."""
        result = RaceResult(
            date="02 Mar",
            grand_prix="Bahrain Grand Prix",
            winner="Max Verstappen",
            car="Red Bull Racing",
            time="1:31:44.742",
            scraped_at="2024-01-15T10:30:00"
        )
        
        assert result.car == "Red Bull Racing"
        assert result.time == "1:31:44.742"
        assert result.scraped_at == "2024-01-15T10:30:00"


class TestCLIIntegration:
    """Test cases for command-line interface."""
    
    @patch('sys.argv', ['f1_scraper_pro.py', '--year', '2024', '--summary'])
    @patch('f1_scraper_pro.F1ResultsScraperPro.scrape')
    def test_cli_basic_usage(self, mock_scrape):
        """Test basic CLI usage."""
        mock_scrape.return_value = True
        
        from f1_scraper_pro import create_argument_parser
        
        parser = create_argument_parser()
        args = parser.parse_args(['--year', '2024', '--summary'])
        
        assert args.year == 2024
        assert args.summary is True
        assert args.output_dir == 'output'
        assert args.log_level == 'INFO'
    
    def test_cli_argument_parser(self):
        """Test CLI argument parsing."""
        from f1_scraper_pro import create_argument_parser
        
        parser = create_argument_parser()
        
        # Test with custom arguments
        args = parser.parse_args([
            '--year', '2023',
            '--output-dir', '/custom/path',
            '--log-level', 'DEBUG',
            '--rate-limit', '2.0',
            '--summary'
        ])
        
        assert args.year == 2023
        assert args.output_dir == '/custom/path'
        assert args.log_level == 'DEBUG'
        assert args.rate_limit == 2.0
        assert args.summary is True


if __name__ == '__main__':
    pytest.main(['-v', __file__])
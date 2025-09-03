# F1 Results Scraper Professional 🏎️

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A robust, professional-grade web scraper for Formula 1 race results with comprehensive error handling, data validation, and multiple output formats.

## ✨ Features

- **Robust Scraping**: Advanced error handling with retry logic and rate limiting
- **Multiple Formats**: Export to CSV, JSON, and Excel formats
- **Data Validation**: Comprehensive data cleaning and validation
- **Professional Logging**: Detailed logging with multiple levels
- **CLI Support**: Full command-line interface with configurable options
- **Multiple Years**: Support for scraping different F1 seasons
- **Debug Mode**: HTML debugging output for troubleshooting
- **Statistics**: Built-in summary and statistics generation

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Vansh0812/f1-results-scraper.git
cd f1-results-scraper

# Install dependencies
pip install -r requirements.txt

# Run the scraper
python f1_scraper_pro.py
```

### Basic Usage

```python
from f1_scraper_pro import F1ResultsScraperPro

# Initialize scraper for 2025 season
scraper = F1ResultsScraperPro(year=2025)

# Run scraper
success = scraper.scrape()

if success:
    results = scraper.get_results()
    print(f"Scraped {len(results)} races!")
```

## 📋 Command Line Interface

```bash
# Scrape current year with default settings
python f1_scraper_pro.py

# Scrape specific year with custom output directory
python f1_scraper_pro.py --year 2024 --output-dir ./2024_results

# Enable debug logging and show summary
python f1_scraper_pro.py --log-level DEBUG --summary

# Custom rate limiting (slower scraping)
python f1_scraper_pro.py --rate-limit 2.0
```

### CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--year` | `-y` | Year to scrape results for | 2025 |
| `--output-dir` | `-o` | Output directory for results | output |
| `--log-level` | `-l` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO |
| `--rate-limit` | `-r` | Rate limit between requests (seconds) | 1.0 |
| `--summary` | `-s` | Show summary statistics after scraping | False |

## 📊 Output Formats

The scraper generates multiple output files:

### CSV Format (`f1_YYYY_results.csv`)
```csv
date,grand_prix,winner,car,time,scraped_at
01 Mar,Bahrain Grand Prix,Max Verstappen,Red Bull Racing,1:31:44.742,2025-01-15T10:30:00
```

### JSON Format (`f1_YYYY_results.json`)
```json
{
  "metadata": {
    "scraped_at": "2025-01-15T10:30:00",
    "source_url": "https://www.formula1.com/en/results/2025/races",
    "year": 2025,
    "total_races": 24,
    "scraper_version": "2.0.0"
  },
  "results": [
    {
      "date": "01 Mar",
      "grand_prix": "Bahrain Grand Prix",
      "winner": "Max Verstappen",
      "car": "Red Bull Racing",
      "time": "1:31:44.742",
      "scraped_at": "2025-01-15T10:30:00"
    }
  ]
}
```

## 🏗️ Architecture

### Class Structure

```
F1ResultsScraperPro
├── __init__()          # Initialize scraper with configuration
├── scrape()            # Main scraping orchestration
├── fetch_page()        # HTTP request handling with retries
├── extract_race_results()  # Parse HTML and extract data
├── validate_results()  # Data validation and quality checks
├── save_to_csv()       # CSV export functionality
├── save_to_json()      # JSON export functionality
└── get_summary()       # Statistics generation
```

### Key Components

- **Session Management**: Configured requests session with retry strategy
- **Rate Limiting**: Respectful scraping with configurable delays
- **Error Handling**: Comprehensive exception handling at all levels
- **Data Validation**: Multi-level validation for data quality
- **Logging System**: Professional logging with file and console output

## 🔧 Configuration

### Environment Variables

Create a `.env` file for configuration:

```env
# Scraping Configuration
F1_DEFAULT_YEAR=2025
F1_OUTPUT_DIR=./output
F1_LOG_LEVEL=INFO
F1_RATE_LIMIT=1.0

# HTTP Configuration
F1_REQUEST_TIMEOUT=15
F1_MAX_RETRIES=3
```

### Advanced Configuration

```python
scraper = F1ResultsScraperPro(
    year=2024,
    output_dir="custom_output",
    log_level="DEBUG",
    rate_limit=0.5  # Faster scraping
)
```

## 📈 Statistics and Analysis

Get detailed statistics about scraped data:

```python
scraper = F1ResultsScraperPro()
scraper.scrape()

summary = scraper.get_summary()
print(f"Total races: {summary['total_races']}")
print(f"Top winners: {summary['winners']}")
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=f1_scraper_pro tests/
```

## 🔍 Troubleshooting

### Common Issues

1. **No results found**: Check the debug HTML file in output directory
2. **Connection errors**: Verify internet connection and try increasing rate limit
3. **Parsing errors**: Website structure may have changed - check logs for details

### Debug Mode

Enable debug logging to see detailed execution:

```bash
python f1_scraper_pro.py --log-level DEBUG
```

### Debug Files

The scraper generates debug files:
- `debug_page_YYYY.html`: Raw HTML for inspection
- `f1_scraper_YYYY.log`: Detailed execution logs

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY f1_scraper_pro.py .
RUN mkdir output

CMD ["python", "f1_scraper_pro.py"]
```

Build and run:
```bash
docker build -t f1-scraper .
docker run -v $(pwd)/output:/app/output f1-scraper
```

### GitHub Actions CI/CD

```yaml
name: F1 Scraper CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

### Scheduled Scraping

Set up automated scraping with cron:
```bash
# Run every day at 8 AM
0 8 * * * /path/to/python /path/to/f1_scraper_pro.py --year 2025
```

## 📋 API Reference

### Class: F1ResultsScraperPro

#### Constructor
```python
F1ResultsScraperPro(
    year: int = 2025,
    output_dir: str = "output",
    log_level: str = "INFO",
    rate_limit: float = 1.0
)
```

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `scrape()` | Main scraping method | `bool` |
| `get_results()` | Get scraped results | `List[Dict]` |
| `get_summary()` | Get statistics summary | `Dict` |
| `validate_results()` | Validate scraped data | `Tuple[bool, List[str]]` |
| `save_to_csv(filename)` | Save results to CSV | `bool` |
| `save_to_json(filename)` | Save results to JSON | `bool` |

### Data Models

#### RaceResult
```python
@dataclass
class RaceResult:
    date: str
    grand_prix: str
    winner: str
    car: str = ""
    time: str = ""
    scraped_at: str = ""
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/Vansh0812/f1-results-scraper.git
cd f1-results-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install
```

### Code Style

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pytest** for testing

```bash
# Format code
black f1_scraper_pro.py

# Check linting
flake8 f1_scraper_pro.py

# Type checking
mypy f1_scraper_pro.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Formula 1 for providing race data
- BeautifulSoup and Requests libraries
- Python community for excellent tooling

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Vansh0812/f1-results-scraper/issues)
- **Email**: vanshjain081203@gmail.com
- **LinkedIn**: [LinkedIn](https://linkedin.com/in/vjain812)

## 📊 Project Status

- ✅ Basic scraping functionality
- ✅ Multi-format output (CSV, JSON)
- ✅ CLI interface
- ✅ Professional logging
- ✅ Data validation
- ✅ Docker support
- 🔄 Excel output format (in progress)
- 🔄 Historical data analysis (planned)
- 🔄 Web dashboard (planned)

---

**Built with ❤️ for Formula 1 enthusiasts and data professionals**
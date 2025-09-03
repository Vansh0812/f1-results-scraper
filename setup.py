"""
F1 Results Scraper - Package Setup
==================================
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

requirements = (this_directory / "requirements.txt").read_text().splitlines()
requirements = [req for req in requirements if not req.startswith('#') and req.strip()]

setup(
    name="f1-results-scraper",
    version="2.0.0",
    author="Vansh Jain",
    author_email="vanshjain081203@gmail.com",
    description="Professional Formula 1 race results scraper with comprehensive data handling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Vansh0812/f1-results-scraper",
    project_urls={
        "Bug Reports": "https://github.com/Vansh0812/f1-results-scraper/issues",
        "Source": "https://github.com/Vansh0812/f1-results-scraper",
        "Documentation": "https://f1-scraper.readthedocs.io/",
    },
    packages=find_packages(),
    py_modules=["f1_scraper_pro"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Data Scientists",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
        ],
        "excel": [
            "openpyxl>=3.1.0",
            "xlsxwriter>=3.1.0",
        ],
        "dashboard": [
            "streamlit>=1.25.0",
            "plotly>=5.15.0",
            "dash>=2.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "f1-scraper=f1_scraper_pro:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="formula1 f1 scraping motorsport data-extraction racing",
    zip_safe=False,
)
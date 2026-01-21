"""
Shared configuration and utility functions for the job board application.
"""

import json
import os
import re
from typing import Dict, List

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get('DATA_DIR', os.path.join(SCRIPT_DIR, 'data'))
COMPANIES_FILE = os.path.join(SCRIPT_DIR, 'companies.json')
DISCOVERED_FILE = os.path.join(DATA_DIR, 'discovered_companies.json')
KEYWORDS_FILE = os.path.join(DATA_DIR, 'keywords.json')
LOCATIONS_FILE = os.path.join(DATA_DIR, 'locations.json')
DB_PATH = os.path.join(DATA_DIR, 'applications.db')
JOBS_FILE = os.path.join(DATA_DIR, 'devops_jobs.json')

# Default keywords for job matching
DEFAULT_KEYWORDS = [
    'devops', 'sre', 'site reliability', 'platform engineer',
    'infrastructure', 'cloud engineer', 'devsecops', 'kubernetes', 'terraform'
]

# Default locations (word boundary matching)
DEFAULT_LOCATIONS = {
    'allowed': [
        'united states', 'usa', 'u.s.', 'america',
        'canada', 'north america', 'americas', 'us/canada',
        'remote', 'worldwide', 'global', 'anywhere'
    ]
}


def ensure_data_dir():
    """Ensure the data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json_file(filepath: str, default=None):
    """Load a JSON file with error handling"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return default if default is not None else {}


def save_json_file(filepath: str, data, indent: int = 2):
    """Save data to a JSON file"""
    ensure_data_dir()
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)


def load_companies() -> Dict:
    """Load company lists from JSON file"""
    return load_json_file(COMPANIES_FILE, {})


def load_discovered_companies() -> Dict:
    """Load discovered companies from file"""
    return load_json_file(DISCOVERED_FILE, {})


def load_keywords() -> List[str]:
    """Load search keywords from file"""
    keywords = load_json_file(KEYWORDS_FILE)
    if keywords and isinstance(keywords, list):
        return keywords
    return DEFAULT_KEYWORDS.copy()


def save_keywords(keywords: List[str]):
    """Save search keywords to file"""
    save_json_file(KEYWORDS_FILE, keywords, indent=None)


def load_locations() -> Dict:
    """Load location filters from file or companies.json"""
    # First check for custom locations file
    data = load_json_file(LOCATIONS_FILE)
    if data and isinstance(data, dict) and 'allowed' in data:
        return {'allowed': data['allowed']}

    # Fall back to companies.json locations
    companies = load_companies()
    if 'locations' in companies:
        return {'allowed': companies['locations'].get('allowed', [])}

    return DEFAULT_LOCATIONS.copy()


def save_locations(locations: Dict):
    """Save location filters to file"""
    save_json_file(LOCATIONS_FILE, locations)


def matches_location_word_boundary(text: str, allowed_locations: List[str] = None) -> bool:
    """
    Check if text matches any allowed location using word boundary matching.
    Prevents 'usa' from matching 'australia'.
    """
    if allowed_locations is None:
        allowed_locations = DEFAULT_LOCATIONS['allowed']

    text_lower = text.lower()

    for term in allowed_locations:
        pattern = r'\b' + re.escape(term.lower()) + r'\b'
        if re.search(pattern, text_lower):
            return True

    return False

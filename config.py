"""
Configuration for Bejaa Digital Website Optimization Scanner
"""

import os
from datetime import datetime

# Scanner Configuration
SCANNER_CONFIG = {
    "version": "1.0.0",
    "company": "Bejaa Digital",
    "website": "https://bejaadigital.com",
    "contact_email": "hello@bejaadigital.com",
    
    # Performance thresholds
    "performance_thresholds": {
        "good": 90,      # Score >= 90
        "needs_improvement": 50,  # 50 <= Score < 90
        "poor": 0        # Score < 50
    },
    
    # Timeouts (in seconds)
    "timeouts": {
        "request_timeout": 20,
        "speedtest_timeout": 45,
        "ssl_timeout": 10
    },
    
    # File paths
    "paths": {
        "reports": "reports",
        "templates": "templates",
        "static": "static"
    },
    
    # Scoring weights
    "weights": {
        "seo": 0.25,
        "performance": 0.30,
        "security": 0.25,
        "mobile": 0.20
    }
}

# Security headers to check
SECURITY_HEADERS = [
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Strict-Transport-Security",
    "X-XSS-Protection",
    "Referrer-Policy",
    "Permissions-Policy"
]

# SEO meta tags to check
SEO_TAGS = [
    "title",
    "description",
    "keywords",
    "viewport",
    "robots",
    "canonical",
    "og:title",
    "og:description",
    "og:image",
    "twitter:card",
    "twitter:title",
    "twitter:description"
]

# Performance metrics
PERFORMANCE_METRICS = {
    "page_load_time": 3.0,  # seconds (good threshold)
    "time_to_first_byte": 0.8,  # seconds
    "page_size": 2000,  # KB (good threshold)
    "requests_count": 50  # max requests (good threshold)
}

def get_report_filename(url):
    """Generate unique report filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
    return f"{timestamp}_{domain}_report.html"

def ensure_directories():
    """Create necessary directories"""
    directories = [
        "reports",
        "templates",
        "static/css",
        "static/js",
        "static/images",
        "modules"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    return True
#!/usr/bin/env python3
"""
Run script for Trivy Vulnerability Scanner Dashboard
"""

import sys
import os

# Add the package to Python path
sys.path.insert(0, os.path.dirname(__file__))

from trivy_scanner.app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
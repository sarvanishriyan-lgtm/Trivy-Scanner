# Trivy Vulnerability Scanner Dashboard

A comprehensive web dashboard for visualizing and analyzing Trivy container vulnerability scan results from AWS ECR repositories.

## 📁 Project Structure

```
trivy_scanner/
├── app/                          # Flask web application
│   ├── __init__.py              # Application factory
│   ├── app.py                   # Main application entry point
│   ├── routes.py                # API routes and handlers
│   ├── static/                  # Static assets
│   │   ├── css/
│   │   └── js/
│   └── templates/               # HTML templates
├── scripts/                     # Utility scripts
│   ├── fetch_ecr_images.py      # ECR image discovery
│   └── scan_images.py           # Trivy scanning
├── config/                      # Configuration files
├── data/                        # Data files
│   └── images.json              # ECR image metadata
├── docs/                        # Documentation
│   ├── PHASE_1_PLAN.md         # Phase 1 planning
│   ├── PHASE_2_PLAN.md         # Phase 2 planning
│   └── PHASE_3_PLAN.md         # Phase 3 planning
├── output/                      # Trivy scan results
├── tests/                       # Unit tests
├── __init__.py                  # Package initialization
├── setup.py                     # Package setup
├── run.py                       # Application runner
├── MANIFEST.in                  # Package manifest
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Features

- **ECR Image Discovery**: Automatically fetch all repositories and tagged images from AWS ECR
- **Parallel Vulnerability Scanning**: Multi-threaded Trivy scanning with Docker integration
- **Interactive Web Dashboard**: Modern Flask-based dashboard with real-time filtering
- **Advanced Analytics**: Severity distribution charts, top vulnerable images, and detailed CVE information
- **Pagination & Search**: Handle large datasets with 100-item pagination and multi-field search
- **Export Capabilities**: Download vulnerability reports as Excel spreadsheets
- **Dark Security Theme**: Professional UI designed for security operations

## 📋 Prerequisites

- Python 3.8+
- AWS CLI configured with ECR access
- Docker Desktop (for Trivy scanning)
- Trivy CLI

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sarvanishriyan-lgtm/Trivy-Scanner.git
   cd Trivy-Scanner
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Trivy CLI:**
   ```bash
   # macOS with Homebrew
   brew install trivy

   # Or download from: https://github.com/aquasecurity/trivy
   ```

5. **Configure AWS CLI:**
   ```bash
   aws configure sso
   # Or use your preferred AWS authentication method
   ```

## 📖 Usage

### Phase 1: Discover ECR Images

```bash
python scripts/fetch_ecr_images.py --profile your-aws-profile --region us-east-1 --output data/images.json
```

### Phase 2: Scan Images with Trivy

```bash
python scripts/scan_images.py --max-workers 3
```

### Phase 3: Launch Dashboard

```bash
# Option 1: Direct execution
python run.py

# Option 2: Using Flask
export FLASK_APP=trivy_scanner.app.app
flask run --host=0.0.0.0 --port=5000

# Option 3: After installation
pip install -e .
trivy-dashboard
```

Then open your browser to: **http://localhost:5000**

## 🔧 Configuration

### Environment Variables

- `FLASK_ENV`: Set to `development` for debug mode
- `AWS_PROFILE`: AWS CLI profile for ECR access
- `AWS_REGION`: AWS region for ECR repositories

### Dashboard Configuration

The dashboard automatically detects Trivy scan results in the `output/` directory. Scan results are organized by environment and repository for easy navigation.

## 📊 Dashboard Features

- **Summary Cards**: Total images scanned, vulnerability counts by severity
- **Interactive Charts**: Severity distribution donut chart, top vulnerable images bar chart
- **Advanced Filtering**: Search by image name, package, or CVE ID; filter by severity
- **Pagination**: 100 items per page with navigation controls
- **CVE Details**: Click any CVE for detailed information and affected images
- **Export**: Download complete vulnerability reports as Excel files

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=trivy_scanner tests/
```

## 📝 Development

### Code Style

```bash
# Format code
black trivy_scanner/

# Lint code
flake8 trivy_scanner/

# Type checking
mypy trivy_scanner/
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes following the existing code structure
3. Add tests for new functionality
4. Update documentation as needed
5. Submit pull request

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Trivy](https://github.com/aquasecurity/trivy) - Comprehensive vulnerability scanner
- [Flask](https://flask.palletsprojects.com/) - Lightweight WSGI web application framework
- [Chart.js](https://www.chartjs.org/) - Simple yet flexible JavaScript charting library

## 📞 Support

For questions or issues, please open a GitHub issue or contact the maintainers.

```bash
python3 app.py
```

Then navigate to:
```
http://localhost:5000
```

## Dashboard Features

- **Summary Cards**: Images scanned, total vulnerabilities, severity breakdown
- **Charts**: Severity distribution (donut), top images by vulnerabilities (bar)
- **Search & Filter**: By image name, package, CVE ID, and severity level
- **Vulnerability Table**: Sortable table with all CVE details
- **CVE Details Panel**: Click any CVE to see full details, affected images, and references
- **Export**: Download all vulnerabilities as Excel (.xlsx) file
- **Dark Theme**: Security-focused design inspired by modern vulnerability management tools

## Project Structure

```
.
├── src/
│   ├── fetch_ecr_images.py     # Phase 1: ECR discovery
│   └── scan_images.py          # Phase 2: Trivy scanning
├── app.py                       # Phase 3: Flask dashboard
├── templates/
│   └── dashboard.html          # Dashboard UI
├── static/
│   ├── styles.css              # Dark theme styling
│   └── dashboard.js            # Interactive dashboard
├── data/
│   └── images.json             # ECR image list (Phase 1 output)
├── output/                      # Trivy scan reports (Phase 2 output)
├── docs/
│   ├── PHASE_1_PLAN.md
│   ├── PHASE_2_PLAN.md
│   └── PHASE_3_PLAN.md
├── requirements.txt            # Python dependencies
└── README.md
```

## Notes

- Phase 1 requires AWS CLI configured.
- Phase 2 requires Trivy CLI installed and Docker running.
- Phase 3 requires Flask and pandas installed (see requirements.txt).
- All phases are independent and can be run separately.

# Trivy-Scanner
# Trivy-Scanner

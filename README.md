# Trivy Phases 1-3: ECR Discovery, Scanning, and Dashboard

This repository contains Phases 1, 2, and 3 of the Trivy-based vulnerability scanning workflow:

- `src/fetch_ecr_images.py`: fetches AWS ECR repositories and tagged images via AWS CLI
- `src/scan_images.py`: scans images from `data/images.json` using Trivy with parallel threading
- `app.py`: Flask web dashboard to visualize and analyze Trivy vulnerability reports
- `data/images.json`: generated output file containing ECR image metadata
- `output/`: directory with segregated Trivy scan results by repository
- `docs/PHASE_1_PLAN.md`: Phase 1 implementation plan
- `docs/PHASE_2_PLAN.md`: Phase 2 implementation plan
- `docs/PHASE_3_PLAN.md`: Phase 3 implementation plan

## Installation

1. **Install Python dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Install Trivy CLI:**
   For macOS with Homebrew:
   ```bash
   brew install trivy
   ```

3. **Configure AWS CLI:**
   ```bash
   aws configure sso
   ```

## Usage

### Phase 1: Fetch ECR Images

```bash
python3 src/fetch_ecr_images.py --profile <AWS_PROFILE> --region <AWS_REGION> --output data/images.json
```

### Phase 2: Scan Images with Trivy

```bash
python3 src/scan_images.py --max-workers 3
```

Note: The script automatically checks if Docker is running and starts Docker Desktop on macOS if needed. Trivy runs with unique cache directories to avoid conflicts during concurrent scans.

### Phase 3: Start the Vulnerability Dashboard

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

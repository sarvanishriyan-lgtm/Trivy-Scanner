# Phase 3 Plan: Vulnerability Dashboard

## Objective

Build a Flask-based web dashboard to visualize and analyze Trivy vulnerability scan results from Phase 2.

## Scope

- Read all Trivy JSON files from `output/` directory (organized by repository).
- Parse and extract vulnerability metadata.
- Display aggregated statistics and actionable insights.
- Provide search, filter, and export capabilities.

## Inputs

- Trivy JSON scan reports from `output/<repository>/*.json` (Phase 2 output).
- Flask framework for web application.
- Pandas and openpyxl for Excel export.

## Output

- Flask web application accessible at `http://localhost:5000`.
- Interactive dashboard with charts, tables, and filters.
- Excel export of vulnerability data.

## Dashboard Components

### 1. Summary Cards (Top)
- **Images Scanned**: Total count of unique images.
- **Total Vulnerabilities**: Aggregate CVE count across all images.
- **Critical**: Count of CRITICAL severity CVEs.
- **High**: Count of HIGH severity CVEs.
- **Medium**: Count of MEDIUM severity CVEs.
- **Low**: Count of LOW severity CVEs.

### 2. Charts
- **Severity Distribution (Donut)**: Pie/donut chart showing % split by severity.
- **Top 10 Images (Bar)**: Horizontal bar chart of images with most vulnerabilities.
- **Vulnerability Trend (Optional)**: Line chart if timeline data available.

### 3. Search & Filters
- **Text Search**: By image name, package name, or CVE ID.
- **Severity Filter**: Dropdown to show only CRITICAL, HIGH, MEDIUM, LOW, or all.

### 4. Vulnerability Table
Columns:
- Image
- Package
- CVE ID
- Severity (with color coding)
- Installed Version
- Fixed Version
- Description (truncated, expandable)
- Status (e.g., "Fixable", "No Fix Available")

### 5. CVE Details Panel (Right Sidebar / Modal)
When a vulnerability is selected:
- CVE ID
- Title / Description
- Severity + CVSS Score (if available)
- Affected Package
- Installed Version
- Fixed Version
- Affected Images List
- Reference Links
- Remediation Steps

### 6. Export
- **Export Report Button**: Download all vulnerabilities as Excel (.xlsx) with formatting.

## Implementation Steps

1. Create `app.py` with Flask routes and JSON parsing logic.
2. Create `templates/dashboard.html` with responsive layout.
3. Create `static/styles.css` for dark security theme.
4. Create `static/dashboard.js` for interactivity (search, filter, chart rendering).
5. Use Chart.js or similar for data visualization.
6. Implement Excel export with pandas.
7. Test dashboard locally.

### Run Command

```bash
python3 app.py
```

Then navigate to `http://localhost:5000`.

## Technology Stack

- **Backend**: Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Processing**: Pandas, JSON
- **Export**: openpyxl
- **Charting**: Chart.js (or similar)
- **Styling**: Custom CSS with dark theme

## Validation

- Dashboard loads without errors.
- All vulnerability data is parsed and displayed.
- Filters and search work correctly.
- Charts render properly.
- Excel export is complete and readable.
- Responsive design works on desktop and tablet.

## Notes

- Phase 2 outputs are stored in `output/<repository>/`, not `reports/`.
- Scan may have errors; parser should skip files with `scan_error`.
- Dark theme provides visual appeal for security tools.
- Export functionality aids in reporting and compliance.
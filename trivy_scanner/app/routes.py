import json
import os
import glob
from collections import defaultdict
from flask import Blueprint, render_template, jsonify, request
import pandas as pd
from io import BytesIO

main_bp = Blueprint('main', __name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')


def load_vulnerabilities():
    """Load and parse all Trivy JSON reports from output/ directory."""
    vulnerabilities = []
    images_metadata = {}

    # Find all JSON files in output directory
    json_files = glob.glob(os.path.join(OUTPUT_DIR, '**/*.json'), recursive=True)

    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            # Skip files with scan errors
            if 'scan_error' in data:
                continue

            image_name = data.get('ArtifactName', 'unknown')

            # Store metadata about the image
            if image_name not in images_metadata:
                images_metadata[image_name] = {
                    'repository': data.get('Metadata', {}).get('Repo', 'unknown'),
                    'scanned_at': data.get('CreatedAt', ''),
                    'artifact_id': data.get('ArtifactID', ''),
                }

            # Parse vulnerabilities
            if 'Results' in data:
                for result in data['Results']:
                    if 'Vulnerabilities' in result:
                        for vuln in result['Vulnerabilities']:
                            v = {
                                'image': image_name,
                                'package': vuln.get('PkgName', ''),
                                'vulnerability_id': vuln.get('VulnerabilityID', ''),
                                'severity': vuln.get('Severity', 'UNKNOWN'),
                                'installed_version': vuln.get('InstalledVersion', ''),
                                'fixed_version': vuln.get('FixedVersion', ''),
                                'description': vuln.get('Description', ''),
                                'title': vuln.get('Title', ''),
                                'cvss_score': vuln.get('CVSS', {}).get('nvd', {}).get('V3Score', 'N/A'),
                                'references': vuln.get('References', []),
                                'fix_available': bool(vuln.get('FixedVersion')),
                            }
                            vulnerabilities.append(v)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing {json_file}: {e}")

    return vulnerabilities, images_metadata


@main_bp.route('/')
def dashboard():
    """Render the main dashboard page."""
    return render_template('dashboard.html')


@main_bp.route('/api/vulnerabilities')
def api_vulnerabilities():
    """API endpoint to fetch vulnerabilities with optional filtering and pagination."""
    vulns, _ = load_vulnerabilities()

    # Get filter parameters
    severity_filter = request.args.get('severity', '').upper()
    search_term = request.args.get('search', '').lower()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 100, type=int)

    # Apply filters
    filtered = vulns
    if severity_filter and severity_filter != 'ALL':
        filtered = [v for v in filtered if v['severity'] == severity_filter]

    if search_term:
        filtered = [
            v for v in filtered
            if search_term in v['image'].lower() or
               search_term in v['package'].lower() or
               search_term in v['vulnerability_id'].lower()
        ]

    # Sort by severity (CRITICAL > HIGH > MEDIUM > LOW)
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'UNKNOWN': 4}
    filtered = sorted(filtered, key=lambda x: (severity_order.get(x['severity'], 5), x['image']))

    # Calculate pagination
    total_items = len(filtered)
    total_pages = (total_items + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated = filtered[start_idx:end_idx]

    return jsonify({
        'items': paginated,
        'page': page,
        'page_size': page_size,
        'total_items': total_items,
        'total_pages': total_pages
    })


@main_bp.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics."""
    vulns, images_metadata = load_vulnerabilities()

    severity_counts = defaultdict(int)
    for v in vulns:
        severity_counts[v['severity']] += 1

    unique_images = set(v['image'] for v in vulns)

    # Top images by vulnerability count
    image_vuln_count = defaultdict(int)
    for v in vulns:
        image_vuln_count[v['image']] += 1

    top_images = sorted(image_vuln_count.items(), key=lambda x: x[1], reverse=True)[:10]

    stats = {
        'images_scanned': len(unique_images),
        'total_vulnerabilities': len(vulns),
        'severity_counts': dict(severity_counts),
        'top_images': [{'image': img, 'count': cnt} for img, cnt in top_images],
    }

    return jsonify(stats)


@main_bp.route('/api/cve/<cve_id>')
def api_cve_details(cve_id):
    """API endpoint for CVE details."""
    vulns, images_metadata = load_vulnerabilities()

    cve_vulns = [v for v in vulns if v['vulnerability_id'] == cve_id]

    if not cve_vulns:
        return jsonify({'error': 'CVE not found'}), 404

    # Aggregate info from all instances of this CVE
    first = cve_vulns[0]
    affected_images = list(set(v['image'] for v in cve_vulns))

    details = {
        'cve_id': cve_id,
        'title': first['title'],
        'description': first['description'],
        'severity': first['severity'],
        'cvss_score': first['cvss_score'],
        'affected_images': affected_images,
        'references': first['references'],
        'instances': cve_vulns,
    }

    return jsonify(details)


@main_bp.route('/api/export')
def api_export():
    """Export vulnerabilities to Excel."""
    vulns, _ = load_vulnerabilities()

    df = pd.DataFrame(vulns)

    # Select and reorder columns
    columns_order = [
        'image', 'package', 'vulnerability_id', 'severity',
        'installed_version', 'fixed_version', 'description', 'fix_available'
    ]
    df = df[columns_order]

    # Create Excel workbook
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Vulnerabilities', index=False)

    output.seek(0)

    return output.getvalue(), 200, {
        'Content-Disposition': 'attachment; filename=vulnerability_report.xlsx',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
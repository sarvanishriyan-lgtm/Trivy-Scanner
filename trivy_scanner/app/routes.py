import json
import os
import glob
from collections import defaultdict
from flask import Blueprint, render_template, jsonify, request
import pandas as pd
from io import BytesIO

main_bp = Blueprint('main', __name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')


def load_vulnerabilities(profile='dev'):
    """Load and parse all Trivy JSON reports from output/<profile>/ directory."""
    vulnerabilities = []
    images_metadata = {}

    # Use profile-specific output directory
    profile_output_dir = os.path.join(OUTPUT_DIR, profile)

    # Find all JSON files in profile-specific output directory
    json_files = glob.glob(os.path.join(profile_output_dir, '**/*.json'), recursive=True)

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
    profile = request.args.get('profile', 'dev')  # Default to dev
    vulns, _ = load_vulnerabilities(profile)

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
    profile = request.args.get('profile', 'dev')
    vulns, images_metadata = load_vulnerabilities(profile)

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
    profile = request.args.get('profile', 'dev')
    vulns, images_metadata = load_vulnerabilities(profile)

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


@main_bp.route('/api/profiles')
def api_profiles():
    """API endpoint to get available profiles/environments."""
    try:
        # Get all subdirectories in output directory
        profiles = []
        if os.path.exists(OUTPUT_DIR):
            profiles = [d for d in os.listdir(OUTPUT_DIR)
                       if os.path.isdir(os.path.join(OUTPUT_DIR, d))]

        # Sort profiles with dev first, then alphabetically
        profiles.sort(key=lambda x: (0 if x == 'dev' else 1, x))

        return jsonify({
            'profiles': profiles,
            'default': 'dev'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
// Dashboard JavaScript

let allVulnerabilities = [];
let severityChart = null;
let topImagesChart = null;
let currentPage = 1;
let totalPages = 1;
let totalItems = 0;

// Load data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadVulnerabilities();
});

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('stat-images').textContent = stats.images_scanned;
        document.getElementById('stat-total').textContent = stats.total_vulnerabilities;
        document.getElementById('stat-critical').textContent = stats.severity_counts['CRITICAL'] || 0;
        document.getElementById('stat-high').textContent = stats.severity_counts['HIGH'] || 0;
        document.getElementById('stat-medium').textContent = stats.severity_counts['MEDIUM'] || 0;
        document.getElementById('stat-low').textContent = stats.severity_counts['LOW'] || 0;
        
        renderCharts(stats);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load vulnerabilities
async function loadVulnerabilities(page = 1) {
    try {
        const searchTerm = document.getElementById('searchInput')?.value || '';
        const severity = document.getElementById('severityFilter')?.value || '';
        
        const params = new URLSearchParams();
        params.append('page', page);
        params.append('page_size', 100);
        if (searchTerm) params.append('search', searchTerm);
        if (severity) params.append('severity', severity);
        
        const response = await fetch(`/api/vulnerabilities?${params}`);
        const data = await response.json();
        
        allVulnerabilities = data.items;
        currentPage = data.page;
        totalPages = data.total_pages;
        totalItems = data.total_items;
        
        renderVulnerabilityTable(allVulnerabilities);
        renderPaginationControls();
    } catch (error) {
        console.error('Error loading vulnerabilities:', error);
    }
}

// Render charts
function renderCharts(stats) {
    const severityCtx = document.getElementById('severityChart').getContext('2d');
    
    const severityLabels = Object.keys(stats.severity_counts);
    const severityData = Object.values(stats.severity_counts);
    const severityColors = {
        'CRITICAL': '#ff0000',
        'HIGH': '#ff6b35',
        'MEDIUM': '#ffd700',
        'LOW': '#32cd32'
    };
    
    if (severityChart) {
        severityChart.destroy();
    }
    
    severityChart = new Chart(severityCtx, {
        type: 'doughnut',
        data: {
            labels: severityLabels.map(label => `${label} (${stats.severity_counts[label]})`),
            datasets: [{
                data: severityData,
                backgroundColor: severityLabels.map(label => severityColors[label] || '#666'),
                borderColor: '#1a202c',
                borderWidth: 3,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            layout: {
                padding: 10
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e2e8f0',
                        font: { size: 13, weight: '600' },
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 20, 25, 0.9)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#cbd5e0',
                    borderColor: '#00d9ff',
                    borderWidth: 1,
                    padding: 12,
                    titleFont: { size: 13, weight: 'bold' },
                    bodyFont: { size: 12 },
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label.split(' (')[0]}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    // Top images chart
    const topImagesCtx = document.getElementById('topImagesChart').getContext('2d');
    const topImages = stats.top_images;
    const imageLabels = topImages.map(img => img.image.split('/').pop() || img.image);
    const imageCounts = topImages.map(img => img.count);
    
    if (topImagesChart) {
        topImagesChart.destroy();
    }
    
    topImagesChart = new Chart(topImagesCtx, {
        type: 'bar',
        data: {
            labels: imageLabels,
            datasets: [{
                label: 'Vulnerabilities',
                data: imageCounts,
                backgroundColor: '#00d9ff',
                borderColor: '#00d9ff',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { labels: { color: '#e2e8f0' } }
            },
            scales: {
                x: {
                    ticks: { color: '#cbd5e0' },
                    grid: { color: '#4a5568' }
                },
                y: {
                    ticks: { color: '#cbd5e0' },
                    grid: { color: '#4a5568' }
                }
            }
        }
    });
}

// Render vulnerability table
function renderVulnerabilityTable(vulns) {
    const tbody = document.getElementById('vulnTableBody');
    tbody.innerHTML = '';
    
    vulns.forEach(v => {
        const row = document.createElement('tr');
        
        const severityClass = `severity-${v.severity.toLowerCase()}`;
        const statusText = v.fix_available ? '✓ Fixable' : '✗ No Fix';
        const statusClass = v.fix_available ? 'status-fixable' : 'status-unfixable';
        
        row.innerHTML = `
            <td>${escapeHtml(v.image.split('/').pop() || v.image)}</td>
            <td>${escapeHtml(v.package)}</td>
            <td onclick="showCVEDetails('${v.vulnerability_id}')" style="cursor: pointer; color: #00d9ff; text-decoration: underline;">
                ${escapeHtml(v.vulnerability_id)}
            </td>
            <td><span class="${severityClass}">${v.severity}</span></td>
            <td>${escapeHtml(v.installed_version)}</td>
            <td>${escapeHtml(v.fixed_version || 'N/A')}</td>
            <td title="${escapeHtml(v.description)}" style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;">
                ${escapeHtml(v.description.substring(0, 50))}...
            </td>
            <td><span class="${statusClass}">${statusText}</span></td>
        `;
        
        row.onclick = () => showCVEDetails(v.vulnerability_id);
        tbody.appendChild(row);
    });
}

// Apply filters
function applyFilters() {
    currentPage = 1;
    loadVulnerabilities(1);
}

// Show CVE details modal
async function showCVEDetails(cveId) {
    try {
        const response = await fetch(`/api/cve/${cveId}`);
        const details = await response.json();
        
        if (response.ok) {
            const modalBody = document.getElementById('cveModalBody');
            modalBody.innerHTML = `
                <div class="cve-detail-group">
                    <div class="cve-detail-label">CVE ID</div>
                    <div class="cve-detail-value">${escapeHtml(details.cve_id)}</div>
                </div>
                <div class="cve-detail-group">
                    <div class="cve-detail-label">Title</div>
                    <div class="cve-detail-value">${escapeHtml(details.title)}</div>
                </div>
                <div class="cve-detail-group">
                    <div class="cve-detail-label">Severity</div>
                    <div class="cve-detail-value severity-${details.severity.toLowerCase()}">
                        ${details.severity} ${details.cvss_score !== 'N/A' ? `(CVSS: ${details.cvss_score})` : ''}
                    </div>
                </div>
                <div class="cve-detail-group">
                    <div class="cve-detail-label">Description</div>
                    <div class="cve-detail-value">${escapeHtml(details.description)}</div>
                </div>
                <div class="cve-detail-group">
                    <div class="cve-detail-label">Affected Images (${details.affected_images.length})</div>
                    <div class="cve-detail-value">
                        ${details.affected_images.map(img => `<div>• ${escapeHtml(img)}</div>`).join('')}
                    </div>
                </div>
                ${details.references.length > 0 ? `
                <div class="cve-detail-group">
                    <div class="cve-detail-label">References</div>
                    <div class="cve-detail-value">
                        ${details.references.map(ref => `<div><a href="${escapeHtml(ref)}" target="_blank" style="color: #00d9ff;">🔗 ${escapeHtml(ref)}</a></div>`).join('')}
                    </div>
                </div>
                ` : ''}
            `;
            
            document.getElementById('cveModal').classList.add('show');
        }
    } catch (error) {
        console.error('Error loading CVE details:', error);
    }
}

// Close CVE modal
function closeCVEModal() {
    document.getElementById('cveModal').classList.remove('show');
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('cveModal');
    if (event.target === modal) {
        modal.classList.remove('show');
    }
};

// Sort table
function sortTable(columnIndex) {
    const tbody = document.getElementById('vulnTableBody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent;
        const bValue = b.children[columnIndex].textContent;
        
        if (!isNaN(aValue) && !isNaN(bValue)) {
            return parseFloat(aValue) - parseFloat(bValue);
        }
        
        return aValue.localeCompare(bValue);
    });
    
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

// Export report
async function exportReport() {
    try {
        const response = await fetch('/api/export');
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'vulnerability_report.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error exporting report:', error);
        alert('Failed to export report');
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Pagination functions
function goToPage(page) {
    if (page >= 1 && page <= totalPages) {
        loadVulnerabilities(page);
    }
}

function nextPage() {
    if (currentPage < totalPages) {
        goToPage(currentPage + 1);
    }
}

function previousPage() {
    if (currentPage > 1) {
        goToPage(currentPage - 1);
    }
}

// Render pagination controls
function renderPaginationControls() {
    const paginationContainer = document.getElementById('paginationControls');
    if (!paginationContainer) return;
    
    let html = '<div class="pagination">';
    
    // Previous button
    html += `<button class="btn btn-sm ${currentPage === 1 ? 'disabled' : ''}" onclick="previousPage()" ${currentPage === 1 ? 'disabled' : ''}>← Previous</button>`;
    
    // Page info
    html += `<span class="pagination-info">Page <strong>${currentPage}</strong> of <strong>${totalPages}</strong> (Showing ${allVulnerabilities.length} of ${totalItems})</span>`;
    
    // Next button
    html += `<button class="btn btn-sm ${currentPage === totalPages ? 'disabled' : ''}" onclick="nextPage()" ${currentPage === totalPages ? 'disabled' : ''}>Next →</button>`;
    
    html += '</div>';
    paginationContainer.innerHTML = html;
}

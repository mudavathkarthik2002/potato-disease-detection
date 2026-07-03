// ============================================
// INIT CHARTS
// ============================================
function initCharts() {
    // Trend Chart
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        const ctx = trendCtx.getContext('2d');
        const trendData = window.chartData || (function() {
            const el = document.getElementById('trendChart');
            try {
                const labels = el && el.dataset.labels ? JSON.parse(el.dataset.labels) : [];
                const data = el && el.dataset.data ? JSON.parse(el.dataset.data) : [];
                return { labels, data };
            } catch (e) {
                return { labels: [], data: [] };
            }
        })();
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: trendData.labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Detections',
                    data: trendData.data || [12, 19, 15, 22, 18, 25, 30],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 4,
                    pointBackgroundColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(26, 32, 44, 0.9)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        cornerRadius: 8,
                        padding: 12
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }
    
    // Pie Chart
    const pieCtx = document.getElementById('pieChart');
    if (pieCtx) {
        const ctx = pieCtx.getContext('2d');
        const pieData = window.pieData || (function() {
            const el = document.getElementById('pieChart');
            try {
                return el && el.dataset.pie ? JSON.parse(el.dataset.pie) : [35, 30, 35];
            } catch (e) {
                return [35, 30, 35];
            }
        })();
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Healthy', 'Early Blight', 'Late Blight'],
                datasets: [{
                    data: pieData,
                    backgroundColor: ['#48bb78', '#ed8936', '#fc8181'],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            pointStyleWidth: 10,
                            font: { size: 12, family: "'Inter', sans-serif" }
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }
}

// ============================================
// VIEW DETAILS
// ============================================
function viewDetails(id) {
    showToast('Loading activity details...', 'info');
}

// ============================================
// DELETE ACTIVITY
// ============================================
async function deleteActivity(id) {
    if (!confirm('Are you sure you want to delete this activity?')) return;
    
    try {
        const result = await apiCall(`/api/activity/${id}`, 'DELETE');
        if (result.success) {
            showToast('Activity deleted successfully', 'success');
            window.location.reload();
        }
    } catch (error) {
        // Error handled by apiCall
    }
}

// ============================================
// EXPORT REPORT
// ============================================
async function exportReport() {
    try {
        showToast('Generating report...', 'info');
        const result = await apiCall('/api/report/export', 'GET');
        if (result.success && result.url) {
            window.open(result.url, '_blank');
            showToast('Report downloaded successfully', 'success');
        }
    } catch (error) {
        // Error handled by apiCall
    }
}

// ============================================
// INIT
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart !== 'undefined') {
        initCharts();
    }
    // Apply progress bar widths from data attributes (set in templates)
    document.querySelectorAll('.progress-bar[data-width]').forEach(el => {
        try { el.style.width = el.dataset.width; } catch (e) {}
    });
    
    document.querySelectorAll('[data-period]').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('[data-period]').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            showToast(`Loading ${this.dataset.period} data...`, 'info');
        });
    });
});
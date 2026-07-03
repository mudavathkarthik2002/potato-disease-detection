let selectedFile = null;
let predictionHistory = JSON.parse(localStorage.getItem('predictionHistory') || '[]');

// ============================================
// HANDLE PREDICTION
// ============================================
async function handlePrediction() {
    if (!selectedFile) {
        showToast('Please select an image first', 'warning');
        return;
    }
    
    const predictBtn = document.getElementById('predictBtn');
    const resultContainer = document.getElementById('resultContainer');
    const loadingDiv = document.getElementById('loadingDiv');
    
    if (predictBtn) setLoading('predictBtn', true, 'Analyzing...');
    if (loadingDiv) loadingDiv.style.display = 'block';
    if (resultContainer) resultContainer.style.display = 'none';
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'Prediction failed');
        }
        
        if (result.success) {
            displayPredictionResult(result);
            saveToHistory(result);
        }
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        if (predictBtn) setLoading('predictBtn', false);
        if (loadingDiv) loadingDiv.style.display = 'none';
    }
}

// ============================================
// DISPLAY RESULT
// ============================================
function displayPredictionResult(result) {
    const container = document.getElementById('resultContainer');
    if (!container) return;
    
    const prediction = result.prediction;
    const confidence = result.confidence;
    const info = result.disease_info || {};
    
    document.getElementById('predictionText').textContent = prediction.replace('_', ' ').toUpperCase();
    document.getElementById('confidenceText').textContent = (confidence * 100).toFixed(2) + '%';
    
    setTimeout(() => {
        document.getElementById('confidenceFill').style.width = (confidence * 100) + '%';
    }, 100);
    
    if (info.severity) {
        const badge = document.getElementById('severityBadge');
        badge.textContent = info.severity.toUpperCase();
        badge.className = `disease-badge badge-${info.severity}`;
    }
    
    document.getElementById('diseaseInfo').innerHTML = `
        <div class="row mt-3">
            <div class="col-12">
                <p><i class="fas fa-info-circle me-2" style="color: #667eea;"></i>
                <strong>Description:</strong> ${info.description || 'No description available'}</p>
            </div>
            <div class="col-12">
                <p><i class="fas fa-stethoscope me-2" style="color: #667eea;"></i>
                <strong>Treatment:</strong> ${info.treatment || 'Consult a specialist'}</p>
            </div>
        </div>
    `;
    
    const icons = {
        'healthy': 'fas fa-check-circle text-success',
        'early_blight': 'fas fa-exclamation-triangle text-warning',
        'late_blight': 'fas fa-biohazard text-danger'
    };
    document.getElementById('statusIcon').className = icons[prediction] || 'fas fa-question-circle';
    document.getElementById('statusIcon').style.fontSize = '30px';
    
    container.style.display = 'block';
    container.className = `result-container result-${prediction}`;
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================
// SAVE TO HISTORY
// ============================================
function saveToHistory(result) {
    const historyItem = {
        id: Date.now(),
        date: new Date().toISOString(),
        prediction: result.prediction,
        confidence: result.confidence,
        disease_info: result.disease_info
    };
    
    predictionHistory.unshift(historyItem);
    if (predictionHistory.length > 50) predictionHistory = predictionHistory.slice(0, 50);
    localStorage.setItem('predictionHistory', JSON.stringify(predictionHistory));
    showHistory();
}

// ============================================
// SHOW HISTORY
// ============================================
function showHistory() {
    const container = document.getElementById('historyContainer');
    if (!container) return;
    
    if (predictionHistory.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-history fa-2x text-muted mb-2"></i>
                <p class="text-muted">No prediction history yet</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="list-group">';
    predictionHistory.forEach(item => {
        const date = new Date(item.date).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });
        const status = item.prediction;
        
        html += `
            <div class="list-group-item list-group-item-action">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="fw-bold">${status.replace('_', ' ').toUpperCase()}</span>
                        <span class="badge bg-${status === 'healthy' ? 'success' : status === 'early_blight' ? 'warning' : 'danger'} ms-2">
                            ${(item.confidence * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div>
                        <small class="text-muted me-2">${date}</small>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteHistory(${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

// ============================================
// DELETE HISTORY
// ============================================
function deleteHistory(id) {
    if (!confirm('Delete this history item?')) return;
    predictionHistory = predictionHistory.filter(item => item.id !== id);
    localStorage.setItem('predictionHistory', JSON.stringify(predictionHistory));
    showHistory();
    showToast('History item deleted', 'success');
}

// ============================================
// CLEAR HISTORY
// ============================================
function clearHistory() {
    if (!confirm('Clear all prediction history?')) return;
    predictionHistory = [];
    localStorage.setItem('predictionHistory', JSON.stringify(predictionHistory));
    showHistory();
    showToast('History cleared', 'success');
}

// ============================================
// INIT
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        setupDragDrop('uploadArea', 'fileInput', 'imagePreview');
        
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                selectedFile = this.files[0];
                const preview = document.getElementById('imagePreview');
                if (preview) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    };
                    reader.readAsDataURL(selectedFile);
                }
                document.getElementById('uploadArea').style.display = 'none';
                document.getElementById('previewContainer').style.display = 'block';
                document.getElementById('resultContainer').style.display = 'none';
            }
        });
    }
    
    document.getElementById('predictBtn')?.addEventListener('click', handlePrediction);
    
    document.getElementById('newImageBtn')?.addEventListener('click', function() {
        document.getElementById('uploadArea').style.display = 'block';
        document.getElementById('previewContainer').style.display = 'none';
        document.getElementById('resultContainer').style.display = 'none';
        document.getElementById('fileInput').value = '';
        selectedFile = null;
    });
    
    document.getElementById('clearHistoryBtn')?.addEventListener('click', clearHistory);
    showHistory();
});
// Get HTML elements
const newsText = document.getElementById('newsText');
const newsUrl = document.getElementById('newsUrl');
const loading = document.getElementById('loading');
const loadingStage = document.getElementById('loadingStage');
const results = document.getElementById('results');
const resultContent = document.getElementById('resultContent');

// API endpoint - works for both local and production
const API_URL = window.location.origin + '/predict';


// Main check function
async function checkNews() {
    console.log('Analyzing news...');
    
    // Get user input
    const text = newsText.value.trim();
    const url = newsUrl.value.trim();
    
    // Validate input
    if (!text && !url) {
        alert('Please enter news text or URL');
        return;
    }
    
    if (!validateInput(text, url)) {
        return;
    }
    
    // Show loading
    showLoading();
    hideResults();
    updateLoadingStage('Analyzing with ML model...');
    
    // Update stage
    setTimeout(() => {
        updateLoadingStage('Verifying with trusted sources...');
    }, 1000);
    
    try {
        // Call backend API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ text, url })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (response.ok) {
            showResult(data);
        } else {
            showError(data.error || 'Analysis failed');
        }
        
    } catch (error) {
        hideLoading();
        showError('Cannot connect to server. Please ensure the backend is running.');
        console.error('Error:', error);
    }
}


// Display result
function showResult(data) {
    const prediction = data.prediction;
    const confidence = Math.round(data.confidence * 100);
    const verifiedSources = data.verified_sources || [];
    
    // Determine result type
    let resultClass, resultLabel;
    
    if (prediction === 'REAL') {
        resultClass = 'success';
        resultLabel = 'REAL NEWS';
    } else if (prediction === 'FAKE') {
        resultClass = 'error';
        resultLabel = 'FAKE NEWS';
    } else if (prediction.includes('UNVERIFIED')) {
        resultClass = 'warning';
        resultLabel = 'UNVERIFIED';
    } else {
        resultClass = 'warning';
        resultLabel = prediction;
    }
    
    // Build HTML
    let html = `
        <div class="${resultClass}">
            <h3>${resultLabel}</h3>
            <div class="confidence-bar">
                <div class="confidence-label">Confidence: ${confidence}%</div>
                <div class="bar">
                    <div class="bar-fill ${resultClass}" style="width: ${confidence}%"></div>
                </div>
            </div>
    `;
    
    // Show verified sources if any
    if (verifiedSources.length > 0) {
        html += `
            <div class="sources-section">
                <h4>Verified Sources Found (${verifiedSources.length})</h4>
                <ul class="source-list">
        `;
        
        verifiedSources.forEach(source => {
            const sourceName = source.source.replace('www.', '').replace('.com', '');
            html += `
                <li>
                    <span class="source-name">${sourceName}</span>
                    <a href="${source.link}" target="_blank" class="view-link">View Article</a>
                </li>
            `;
        });
        
        html += '</ul></div>';
    } else {
        html += `
            <div class="sources-section">
                <p class="no-sources">No verified sources found for this claim.</p>
            </div>
        `;
    }
    
    html += '</div>';
    
    resultContent.innerHTML = html;
    showResults();
}


// Show error
function showError(msg) {
    resultContent.innerHTML = `
        <div class="error">
            <h3>Error</h3>
            <p>${msg}</p>
        </div>
    `;
    showResults();
}


// UI controls
function showLoading() {
    loading.classList.remove('hidden');
    loading.classList.add('show');
}

function hideLoading() {
    loading.classList.add('hidden');
    loading.classList.remove('show');
    if (loadingStage) {
        loadingStage.textContent = '';
    }
}

function showResults() {
    results.classList.remove('hidden');
    results.classList.add('show');
}

function hideResults() {
    results.classList.add('hidden');
    results.classList.remove('show');
}

function updateLoadingStage(msg) {
    if (loadingStage) {
        loadingStage.textContent = msg;
    }
}

function clearInputs() {
    newsText.value = '';
    newsUrl.value = '';
    hideResults();
    hideLoading();
    newsText.focus();
}


// Validation
function validateInput(text, url) {
    if (url && !url.startsWith('http')) {
        alert('URL must start with http:// or https://');
        return false;
    }
    
    if (text && text.length < 10) {
        alert('Please enter at least 10 characters');
        return false;
    }
    
    return true;
}


// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.target === newsUrl && e.key === 'Enter') {
        checkNews();
    }
    
    if (e.target === newsText && e.ctrlKey && e.key === 'Enter') {
        checkNews();
    }
    
    if (e.key === 'Escape') {
        clearInputs();
    }
});


// Startup
console.log('Fake News Detector - Ready');
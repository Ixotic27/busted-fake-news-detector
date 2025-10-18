// Get HTML elements
const newsText = document.getElementById('newsText');
const newsUrl = document.getElementById('newsUrl');
const loading = document.getElementById('loading');
const loadingStage = document.getElementById('loadingStage');
const results = document.getElementById('results');
const resultContent = document.getElementById('resultContent');

// API endpoint
const API_URL = 'http://localhost:5000/predict';

// Main function to check news
async function checkNews() {
    console.log('Checking news...');
    
    // Get user input
    const text = newsText.value.trim();
    const url = newsUrl.value.trim();
    
    // Check if user entered something
    if (!text && !url) {
        alert('Please enter news text or URL');
        return;
    }
    
    // Validate input
    if (!validateInput(text, url)) {
        return;
    }
    
    // Show loading with stage updates
    showLoading();
    hideResults();
    updateLoadingStage('Stage 1: Running ML analysis...');
    
    // Simulate stage progression
    setTimeout(() => {
        updateLoadingStage('Stage 2: Verifying on trusted sources...');
    }, 1000);
    
    try {
        // Call Flask API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text, url })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (response.ok) {
            showResult(data);
        } else {
            showError(data.error || 'Something went wrong');
        }
        
    } catch (error) {
        hideLoading();
        showError('Cannot connect to backend. Make sure Flask is running!');
        console.error('Error:', error);
    }
}

// Update loading stage message
function updateLoadingStage(msg) {
    if (loadingStage) {
        loadingStage.textContent = msg;
    }
}

// Clear all inputs
function clearInputs() {
    newsText.value = '';
    newsUrl.value = '';
    hideResults();
    hideLoading();
    newsText.focus();
}

// Show loading message
function showLoading() {
    loading.classList.remove('hidden');
    loading.classList.add('show');
}

// Hide loading message
function hideLoading() {
    loading.classList.add('hidden');
    loading.classList.remove('show');
    if (loadingStage) {
        loadingStage.textContent = '';
    }
}

// Show results section
function showResults() {
    results.classList.remove('hidden');
    results.classList.add('show');
}

// Hide results section
function hideResults() {
    results.classList.add('hidden');
    results.classList.remove('show');
}

// Show real result from Flask
function showResult(data) {
    const pred = data.prediction;
    const conf = Math.round(data.confidence * 100);
    const stage = data.stage || '';
    const reason = data.reason || '';
    const ml = data.ml_says || '';
    const sources = data.sources || [];
    const links = data.links || [];
    
    let cssClass, emoji;
    if (pred.includes('REAL')) {
        cssClass = 'success';
        emoji = '✅';
    } else if (pred.includes('LIKELY') || pred.includes('UNVERIFIED')) {
        cssClass = 'warning';
        emoji = '⚠️';
    } else {
        cssClass = 'error';
        emoji = '❌';
    }
    
    let html = `
        <div class="${cssClass}">
            <h4>${emoji} ${pred}</h4>
            <p><strong>Confidence:</strong> ${conf}%</p>
            <p><strong>Stage:</strong> ${stage}</p>
            <p><strong>Analysis:</strong> ${reason}</p>
            <p><strong>ML Model Says:</strong> ${ml.toUpperCase()}</p>
    `;
    
    // Show sources if found
    if (sources.length > 0) {
        html += '<hr><p><strong>✅ Verified on:</strong></p><ul>';
        sources.forEach(src => {
            html += `<li>${src}</li>`;
        });
        html += '</ul>';
    }
    
    // Show links if found
    if (links.length > 0) {
        html += '<p><strong>🔗 Source Links:</strong></p><ul>';
        links.forEach(link => {
            html += `<li><a href="${link}" target="_blank">${link.substring(0, 60)}...</a></li>`;
        });
        html += '</ul>';
    }
    
    if (sources.length === 0) {
        html += '<hr><p><em>❌ No verification found on trusted sources</em></p>';
    }
    
    html += '</div>';
    
    resultContent.innerHTML = html;
    showResults();
}

// Show error message
function showError(msg) {
    resultContent.innerHTML = `
        <div class="error">
            <h4>❌ Error</h4>
            <p>${msg}</p>
        </div>
    `;
    showResults();
}

// Simple input validation
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

// Welcome message
console.log('🚀 Busted! Fake News Detector - CONNECTED');
console.log('👥 Team: Web Scrappers');
console.log('✅ Flask backend ready!');
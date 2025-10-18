// ========== GET HTML ELEMENTS ==========
const newsText = document.getElementById('newsText');
const newsUrl = document.getElementById('newsUrl');
const loading = document.getElementById('loading');
const loadingStage = document.getElementById('loadingStage');
const results = document.getElementById('results');
const resultContent = document.getElementById('resultContent');

// API endpoint
const API_URL = 'http://localhost:5000/predict';


// ========== MAIN CHECK FUNCTION ==========

async function checkNews() {
    console.log('Checking news...');
    
    // Get user input
    const text = newsText.value.trim();
    const url = newsUrl.value.trim();
    
    // Validate input exists
    if (!text && !url) {
        alert('Please enter news text or URL');
        return;
    }
    
    // Validate format
    if (!validateInput(text, url)) {
        return;
    }
    
    // Show loading animation
    showLoading();
    hideResults();
    updateLoadingStage('Stage 1: ML Analysis...');
    
    // Update stage after 1 second
    setTimeout(() => {
        updateLoadingStage('Stage 2: Web Verification...');
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
        
        // Show result or error
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


// ========== DISPLAY FUNCTIONS ==========

function showResult(data) {
    /**
     * Display prediction results
     * Shows: prediction, confidence, verified sources with similarity scores
     */
    const pred = data.prediction;
    const conf = Math.round(data.confidence * 100);
    const stage = data.stage || '';
    const reason = data.reason || '';
    const ml = data.ml_says || '';
    const verified = data.verified_sources || [];
    
    // Choose color and emoji based on prediction
    let cssClass, emoji;
    if (pred.includes('REAL')) {
        cssClass = 'success';
        emoji = '✅';
    } else if (pred.includes('UNVERIFIED') || pred.includes('LIKELY')) {
        cssClass = 'warning';
        emoji = '⚠️';
    } else {
        cssClass = 'error';
        emoji = '❌';
    }
    
    // Build result HTML
    let html = `
        <div class="${cssClass}">
            <h4>${emoji} ${pred}</h4>
            <p><strong>Confidence:</strong> ${conf}%</p>
            <p><strong>Stage:</strong> ${stage}</p>
            <p><strong>Analysis:</strong> ${reason}</p>
            <p><strong>ML Model Says:</strong> ${ml.toUpperCase()}</p>
    `;
    
    // Show verified sources with article links and similarity
    if (verified.length > 0) {
        html += '<hr><p><strong>✅ Verified Sources:</strong></p>';
        html += '<ul class="verified-list">';
        
        verified.forEach(v => {
            const sourceName = v.source.replace('www.', '');
            const similarity = v.similarity ? Math.round(v.similarity * 100) + '% match' : '';
            
            html += `
                <li>
                    <div class="source-info">
                        <strong>${sourceName}</strong>
                        ${similarity ? `<span class="similarity">${similarity}</span>` : ''}
                    </div>
                    <a href="${v.link}" target="_blank" class="source-link">
                        📰 View Article
                    </a>
                </li>
            `;
        });
        
        html += '</ul>';
    } else {
        html += '<hr><p><em>❌ No verified sources found</em></p>';
    }
    
    html += '</div>';
    
    resultContent.innerHTML = html;
    showResults();
}

function showError(msg) {
    /**
     * Display error message
     */
    resultContent.innerHTML = `
        <div class="error">
            <h4>❌ Error</h4>
            <p>${msg}</p>
        </div>
    `;
    showResults();
}


// ========== UI CONTROLS ==========

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


// ========== VALIDATION ==========

function validateInput(text, url) {
    /**
     * Check if user input is valid
     * URL must start with http/https
     * Text must be at least 10 characters
     */
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


// ========== KEYBOARD SHORTCUTS ==========

document.addEventListener('keydown', function(e) {
    // Enter on URL field = check news
    if (e.target === newsUrl && e.key === 'Enter') {
        checkNews();
    }
    
    // Ctrl+Enter on text area = check news
    if (e.target === newsText && e.ctrlKey && e.key === 'Enter') {
        checkNews();
    }
    
    // Escape = clear all
    if (e.key === 'Escape') {
        clearInputs();
    }
});


// ========== STARTUP MESSAGE ==========

console.log('🚀 Busted! Fake News Detector');
console.log('👥 Team: Web Scrappers');
console.log('✅ Ready to detect fake news!');
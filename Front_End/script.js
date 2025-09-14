// Get HTML elements
const newsText = document.getElementById('newsText');
const newsUrl = document.getElementById('newsUrl');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const resultContent = document.getElementById('resultContent');

// Main function to check news
function checkNews() {
    console.log('Checking news...');
    
    // Get user input
    const textInput = newsText.value.trim();
    const urlInput = newsUrl.value.trim();
    
    // Check if user entered something
    if (!textInput && !urlInput) {
        alert('Please enter news text or URL');
        return;
    }
    
    // Show loading
    showLoading();
    hideResults();
    
    // For now, show dummy result after 2 seconds
    // TODO: Replace with Flask API call
    setTimeout(() => {
        hideLoading();
        showDummyResult();
    }, 2000);
    
    /* 
    ===========================================
    FLASK INTEGRATION - UNCOMMENT WHEN READY:
    ===========================================
    
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: textInput,
            url: urlInput
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        showResult(data);
    })
    .catch(error => {
        hideLoading();
        showError('Error: Could not analyze news');
        console.error('Error:', error);
    });
    */
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

// Show dummy result (remove when Flask is ready)
function showDummyResult() {
    resultContent.innerHTML = `
        <div class="error">
            <h4>⚠️ Backend Not Connected</h4>
            <p>Flask integration coming soon!</p>
            <p>Team Web Scrappers is working on it.</p>
        </div>
        <br>
        <div class="success">
            <h4>📊 Sample Result:</h4>
            <p><strong>Classification:</strong> REAL NEWS</p>
            <p><strong>Confidence:</strong> 85%</p>
        </div>
    `;
    showResults();
}

// Show real result from Flask
// TODO: Use this function when Flask backend is ready
function showResult(data) {
    const prediction = data.prediction; // "FAKE" or "REAL"
    const confidence = Math.round(data.confidence * 100); // Convert to percentage
    
    const isReal = prediction === 'REAL';
    const cssClass = isReal ? 'success' : 'error';
    const emoji = isReal ? '✅' : '❌';
    
    resultContent.innerHTML = `
        <div class="${cssClass}">
            <h4>${emoji} ${prediction} NEWS</h4>
            <p><strong>Confidence:</strong> ${confidence}%</p>
        </div>
    `;
    
    showResults();
}

// Show error message
function showError(message) {
    resultContent.innerHTML = `
        <div class="error">
            <h4>❌ Error</h4>
            <p>${message}</p>
        </div>
    `;
    showResults();
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Press Enter in URL field to check news
    if (e.target === newsUrl && e.key === 'Enter') {
        checkNews();
    }
    
    // Press Ctrl+Enter in text area to check news
    if (e.target === newsText && e.ctrlKey && e.key === 'Enter') {
        checkNews();
    }
    
    // Press Escape to clear
    if (e.key === 'Escape') {
        clearInputs();
    }
});

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

// Welcome message for developers
console.log('🚀 Busted! Fake News Detector');
console.log('👥 Team: Web Scrappers');
console.log('🔧 Ready for Flask integration!');
console.log('📝 To connect Flask:');
console.log('   1. Uncomment the fetch code in checkNews()');
console.log('   2. Set up /predict endpoint in Flask');
console.log('   3. Return {prediction: "FAKE/REAL", confidence: 0.85}');
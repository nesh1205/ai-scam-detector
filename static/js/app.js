const API_BASE_URL = 'http://localhost:5000/api';

let currentTab = 'text';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeScanButton();
});

// Tab switching
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const textTab = document.getElementById('text-tab');
    const urlTab = document.getElementById('url-tab');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabType = button.dataset.tab;
            currentTab = tabType;
            
            // Update active state
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Show/hide appropriate input
            if (tabType === 'text') {
                textTab.style.display = 'block';
                urlTab.style.display = 'none';
            } else {
                textTab.style.display = 'none';
                urlTab.style.display = 'block';
            }
            
            // Clear results
            hideResults();
        });
    });
}

// Scan button handler
function initializeScanButton() {
    const scanButton = document.getElementById('scan-button');
    scanButton.addEventListener('click', handleScan);
}

async function handleScan() {
    const scanButton = document.getElementById('scan-button');
    const loading = document.getElementById('loading');
    const resultsSection = document.getElementById('results-section');
    
    // Get content based on current tab
    let content = '';
    if (currentTab === 'text') {
        content = document.getElementById('text-input').value.trim();
    } else {
        content = document.getElementById('url-input').value.trim();
    }
    
    if (!content) {
        alert('Please enter some text or a URL to scan');
        return;
    }
    
    // Show loading, hide results
    loading.classList.add('show');
    resultsSection.classList.remove('show');
    scanButton.disabled = true;
    scanButton.textContent = 'Scanning...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: currentTab,
                content: content
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data.analysis);
        } else {
            throw new Error(data.error || 'Scan failed');
        }
    } catch (error) {
        console.error('Scan error:', error);
        alert('Error scanning content: ' + error.message);
    } finally {
        loading.classList.remove('show');
        scanButton.disabled = false;
        scanButton.textContent = 'Scan for Scam';
    }
}

function displayResults(analysis) {
    const resultsSection = document.getElementById('results-section');
    const percentageValue = document.getElementById('percentage-value');
    const percentageLabel = document.getElementById('percentage-label');
    const statusBadge = document.getElementById('status-badge');
    const indicatorsList = document.getElementById('indicators-list');
    const explanationText = document.getElementById('explanation-text');
    const recommendationsText = document.getElementById('recommendations-text');
    
    // Update percentage
    const scamPercentage = analysis.scam_percentage || 0;
    percentageValue.textContent = `${scamPercentage}%`;
    
    // Update status badge
    statusBadge.className = 'status-badge';
    if (scamPercentage >= 70) {
        statusBadge.textContent = '⚠️ HIGH RISK - Likely Scam';
        statusBadge.classList.add('danger');
    } else if (scamPercentage >= 40) {
        statusBadge.textContent = '⚠️ MEDIUM RISK - Be Cautious';
        statusBadge.classList.add('warning');
    } else {
        statusBadge.textContent = '✓ LOW RISK - Appears Safe';
        statusBadge.classList.add('safe');
    }
    
    // Update indicators
    indicatorsList.innerHTML = '';
    if (analysis.indicators && analysis.indicators.length > 0) {
        analysis.indicators.forEach(indicator => {
            const li = document.createElement('li');
            li.textContent = indicator;
            indicatorsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No specific indicators found';
        indicatorsList.appendChild(li);
    }
    
    // Update explanation
    explanationText.textContent = analysis.explanation || 'No explanation available';
    
    // Update recommendations
    recommendationsText.textContent = analysis.recommendations || 'No recommendations available';
    
    // Show results with animation
    resultsSection.classList.add('show');
    
    // Animate percentage circle
    animatePercentage(scamPercentage);
}

function animatePercentage(percentage) {
    const circle = document.querySelector('.percentage-circle');
    const color = percentage >= 70 ? '#ef4444' : percentage >= 40 ? '#f59e0b' : '#10b981';
    
    // Create SVG circle animation
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '200');
    svg.setAttribute('height', '200');
    svg.style.position = 'absolute';
    svg.style.top = '0';
    svg.style.left = '0';
    svg.style.transform = 'rotate(-90deg)';
    
    const circleBg = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circleBg.setAttribute('cx', '100');
    circleBg.setAttribute('cy', '100');
    circleBg.setAttribute('r', '90');
    circleBg.setAttribute('fill', 'none');
    circleBg.setAttribute('stroke', '#334155');
    circleBg.setAttribute('stroke-width', '10');
    
    const circleProgress = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circleProgress.setAttribute('cx', '100');
    circleProgress.setAttribute('cy', '100');
    circleProgress.setAttribute('r', '90');
    circleProgress.setAttribute('fill', 'none');
    circleProgress.setAttribute('stroke', color);
    circleProgress.setAttribute('stroke-width', '10');
    circleProgress.setAttribute('stroke-linecap', 'round');
    circleProgress.setAttribute('stroke-dasharray', `${2 * Math.PI * 90}`);
    circleProgress.setAttribute('stroke-dashoffset', `${2 * Math.PI * 90 * (1 - percentage / 100)}`);
    circleProgress.style.transition = 'stroke-dashoffset 1s ease';
    
    svg.appendChild(circleBg);
    svg.appendChild(circleProgress);
    
    // Remove existing SVG if any
    const existingSvg = circle.querySelector('svg');
    if (existingSvg) {
        existingSvg.remove();
    }
    
    circle.appendChild(svg);
}

function hideResults() {
    const resultsSection = document.getElementById('results-section');
    resultsSection.classList.remove('show');
}


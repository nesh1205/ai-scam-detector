const API_BASE_URL = 'http://localhost:5000/api';

let firebaseUnsubscribes = [];
let allScansData = [];

// Initialize dashboard
let dashboardInitialized = false;

document.addEventListener('DOMContentLoaded', () => {
    // Prevent multiple initializations
    if (dashboardInitialized) {
        console.log('Dashboard already initialized, skipping...');
        return;
    }
    
    console.log('=== Admin Dashboard Initializing ===');
    dashboardInitialized = true;
    
    // Wait a bit for DOM to be fully ready
    setTimeout(() => {
        // Check authentication (non-blocking, with delay to prevent redirect loops)
        setTimeout(() => {
            checkAuth();
        }, 500);
        
        // Verify DOM elements exist
        const requiredElements = [
            'total-scans', 'scam-count', 'safe-count', 'avg-percentage',
            'scans-table-body', 'all-scans-table-body'
        ];
        
        const missingElements = requiredElements.filter(id => !document.getElementById(id));
        if (missingElements.length > 0) {
            console.error('Missing DOM elements:', missingElements);
        } else {
            console.log('✓ All required DOM elements found');
        }
        
        // Start loading immediately
        console.log('Loading initial data...');
        loadStats();
        loadAllScans();
        
        // Set up polling interval (every 5 seconds - less aggressive)
        console.log('Setting up polling interval (every 5 seconds)...');
        let pollCount = 0;
        window.dashboardPollInterval = setInterval(() => {
            pollCount++;
            if (pollCount % 3 === 0) { // Log every 3rd poll to reduce console spam
                const now = new Date().toLocaleTimeString();
                console.log(`[${now}] Polling for updates...`);
            }
            loadStats();
            loadAllScans();
        }, 5000); // Changed to 5 seconds
        
        console.log('✓ Polling interval set up successfully');
        
        // Also try Firebase Realtime Database if available (as enhancement)
        setTimeout(() => {
            if (window.firebaseDatabase) {
                console.log('Firebase Realtime Database available, initializing real-time listeners...');
                initializeFirebaseRealtime();
                // If Firebase works, reduce polling frequency
                if (window.dashboardPollInterval) {
                    clearInterval(window.dashboardPollInterval);
                    window.dashboardPollInterval = setInterval(() => {
                        loadStats();
                        loadAllScans();
                    }, 20000); // Poll every 20 seconds as backup
                }
            } else {
                console.log('Firebase Realtime Database not available, using API polling only');
            }
        }, 2000);
        
        console.log('=== Dashboard Initialization Complete ===');
    }, 100);
});

function checkAuth() {
    const token = localStorage.getItem('admin_token');
    if (!token) {
        console.log('No admin token found, redirecting to login...');
        setTimeout(() => {
            window.location.href = '/login';
        }, 100);
        return;
    }
    
    // Check auth asynchronously, don't block dashboard loading
    fetch('/api/admin/check', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        // If 401, definitely not authenticated
        if (res.status === 401) {
            return res.json().then(data => {
                throw new Error('Unauthorized');
            });
        }
        // If not 200, something went wrong
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        if (data.authenticated === true) {
            console.log('✓ Authentication successful');
        } else {
            console.log('Not authenticated, redirecting to login...');
            localStorage.removeItem('admin_token');
            setTimeout(() => {
                window.location.href = '/login';
            }, 100);
        }
    })
    .catch((error) => {
        console.error('Auth check error:', error);
        // Only redirect on actual auth failures (401), not network errors
        if (error.message === 'Unauthorized' || error.message.includes('401')) {
            console.log('Authentication failed, redirecting to login...');
            localStorage.removeItem('admin_token');
            setTimeout(() => {
                window.location.href = '/login';
            }, 100);
        } else {
            // Network error or other issue - allow dashboard to continue loading
            console.log('Auth check failed (network issue), continuing anyway...');
        }
    });
}

function initializeFirebaseRealtime() {
    if (!window.firebaseDatabase || !window.firebaseRef || !window.firebaseOnValue) {
        console.log('Firebase Realtime Database not available');
        return;
    }
    
    const database = window.firebaseDatabase;
    const ref = window.firebaseRef;
    const onValue = window.firebaseOnValue;
    
    try {
        console.log('Initializing Firebase Realtime Database listener...');
        
        // Reference to scans in Realtime Database
        const scansRef = ref(database, 'scans');
        
        // Set up real-time listener
        const unsubscribe = onValue(scansRef, (snapshot) => {
            console.log('Firebase Realtime Database update received');
            updateConnectionStatus(true);
            
            const data = snapshot.val();
            allScansData = [];
            const recentScans = [];
            
            if (data) {
                // Convert object to array
                Object.keys(data).forEach((key) => {
                    const scanData = data[key];
                    scanData.id = key;
                    allScansData.push(scanData);
                });
                
                // Sort by timestamp descending
                allScansData.sort((a, b) => {
                    const timeA = new Date(a.timestamp || 0).getTime();
                    const timeB = new Date(b.timestamp || 0).getTime();
                    return timeB - timeA;
                });
                
                // Limit to 100 most recent
                allScansData = allScansData.slice(0, 100);
                
                // Calculate stats
                let totalScans = 0;
                let scamCount = 0;
                let safeCount = 0;
                let totalPercentage = 0;
                
                allScansData.forEach((scanData) => {
                    totalScans++;
                    totalPercentage += scanData.scam_percentage || 0;
                    
                    if (scanData.is_scam) {
                        scamCount++;
                    } else {
                        safeCount++;
                    }
                    
                    // Get recent 10 scans
                    if (recentScans.length < 10) {
                        recentScans.push({
                            id: scanData.id,
                            type: scanData.type || 'text',
                            scam_percentage: scanData.scam_percentage || 0,
                            is_scam: scanData.is_scam || false,
                            timestamp: scanData.timestamp || '',
                            content_preview: (scanData.content || '').substring(0, 100)
                        });
                    }
                });
                
                // Update stats
                const avgPercentage = totalScans > 0 ? (totalPercentage / totalScans) : 0;
                
                const totalScansEl = document.getElementById('total-scans');
                const scamCountEl = document.getElementById('scam-count');
                const safeCountEl = document.getElementById('safe-count');
                const avgPercentageEl = document.getElementById('avg-percentage');
                
                if (totalScansEl) totalScansEl.textContent = totalScans;
                if (scamCountEl) scamCountEl.textContent = scamCount;
                if (safeCountEl) safeCountEl.textContent = safeCount;
                if (avgPercentageEl) avgPercentageEl.textContent = `${avgPercentage.toFixed(1)}%`;
                
                // Update tables
                updateRecentScansTable(recentScans);
                updateAllScansTable(allScansData);
                
                // Add animation to updated stats
                animateStatUpdate();
                
                console.log(`✓ Updated: ${totalScans} scans, ${scamCount} scams, ${safeCount} safe`);
            } else {
                // No data yet
                console.log('No scans data in Firebase yet');
                updateConnectionStatus(true);
            }
        }, (error) => {
            console.error('Firebase Realtime Database error:', error);
            updateConnectionStatus(false, error.message);
            
            // Fallback to API polling
            console.log('Falling back to API polling...');
        });
        
        firebaseUnsubscribes.push(() => {
            if (window.firebaseOff) {
                window.firebaseOff(scansRef);
            }
        });
        
        console.log('✓ Firebase Realtime Database listener initialized');
        
    } catch (error) {
        console.error('Error initializing Firebase Realtime Database:', error);
        updateConnectionStatus(false, error.message);
    }
}

function animateStatUpdate() {
    const statCards = document.querySelectorAll('.stat-value');
    statCards.forEach(card => {
        card.style.transition = 'transform 0.3s ease';
        card.style.transform = 'scale(1.1)';
        setTimeout(() => {
            card.style.transform = 'scale(1)';
        }, 300);
    });
}

function updateConnectionStatus(connected, errorMessage = '') {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (!indicator || !statusText) {
        console.warn('Connection status elements not found');
        return;
    }
    
    if (connected) {
        indicator.style.background = '#10b981'; // Green
        statusText.textContent = 'Real-time Connected';
        statusText.style.color = '#10b981';
    } else {
        indicator.style.background = '#6366f1'; // Blue for API polling
        if (errorMessage) {
            statusText.textContent = `Error: ${errorMessage.substring(0, 30)}`;
            statusText.style.color = '#f59e0b';
        } else {
            statusText.textContent = 'Live Updates (API)';
            statusText.style.color = '#6366f1';
        }
    }
}

// Logout functionality
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            const token = localStorage.getItem('admin_token');
            try {
                await fetch('/api/admin/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ token })
                });
            } catch (e) {
                console.error('Logout error:', e);
            }
            localStorage.removeItem('admin_token');
            window.location.href = '/login';
        });
    }
});

let isUpdating = false;

async function loadStats() {
    // Prevent multiple simultaneous requests
    if (isUpdating) {
        return;
    }
    
    try {
        isUpdating = true;
        
        const response = await fetch(`${API_BASE_URL}/stats`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            cache: 'no-cache'
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('admin_token');
                window.location.href = '/login';
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update stats
        const totalScansEl = document.getElementById('total-scans');
        const scamCountEl = document.getElementById('scam-count');
        const safeCountEl = document.getElementById('safe-count');
        const avgPercentageEl = document.getElementById('avg-percentage');
        
        if (totalScansEl) {
            totalScansEl.textContent = data.total_scans || 0;
        }
        
        if (scamCountEl) {
            scamCountEl.textContent = data.scam_count || 0;
        }
        
        if (safeCountEl) {
            safeCountEl.textContent = data.safe_count || 0;
        }
        
        if (avgPercentageEl) {
            avgPercentageEl.textContent = `${data.average_scam_percentage || 0}%`;
        }
        
        // Update recent scans table
        updateRecentScansTable(data.recent_scans || []);
        
        // Update connection status
        updateConnectionStatus(false);
        
    } catch (error) {
        console.error('Error loading stats:', error);
        if (error.message.includes('Unauthorized') || error.message.includes('401')) {
            localStorage.removeItem('admin_token');
            window.location.href = '/login';
        } else {
            updateConnectionStatus(false, error.message);
        }
    } finally {
        isUpdating = false;
    }
}

function updateRecentScansTable(scans) {
    const tbody = document.getElementById('scans-table-body');
    
    if (scans.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    No scans yet
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = scans.map(scan => {
        const statusBadge = scan.is_scam 
            ? '<span class="status-badge danger">Scam</span>'
            : '<span class="status-badge safe">Safe</span>';
        
        const timestamp = new Date(scan.timestamp).toLocaleString();
        const contentPreview = scan.content_preview || (scan.type === 'url' ? 'URL scan' : 'Text scan');
        
        return `
            <tr>
                <td>${scan.type === 'url' ? '🔗 URL' : '📝 Text'}</td>
                <td>${truncateText(contentPreview, 50)}</td>
                <td><strong>${scan.scam_percentage}%</strong></td>
                <td>${statusBadge}</td>
                <td>${timestamp}</td>
            </tr>
        `;
    }).join('');
}

let isUpdatingScans = false;

async function loadAllScans() {
    // Prevent multiple simultaneous requests
    if (isUpdatingScans) {
        return;
    }
    
    try {
        isUpdatingScans = true;
        
        const response = await fetch(`${API_BASE_URL}/scans`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            cache: 'no-cache'
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('admin_token');
                window.location.href = '/login';
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        updateAllScansTable(data.scans || []);
        
    } catch (error) {
        console.error('Error loading all scans:', error);
        const tbody = document.getElementById('all-scans-table-body');
        if (tbody) {
            if (error.message.includes('Unauthorized') || error.message.includes('401')) {
                localStorage.removeItem('admin_token');
                window.location.href = '/login';
            } else {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; padding: 2rem; color: var(--danger-color);">
                            Error loading scans: ${error.message}
                        </td>
                    </tr>
                `;
            }
        }
    } finally {
        isUpdatingScans = false;
    }
}

function updateAllScansTable(scans) {
    const tbody = document.getElementById('all-scans-table-body');
    
    if (scans.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    No scans found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = scans.map(scan => {
        const statusBadge = scan.is_scam 
            ? '<span class="status-badge danger">Scam</span>'
            : '<span class="status-badge safe">Safe</span>';
        
        const timestamp = new Date(scan.timestamp).toLocaleString();
        const contentPreview = scan.content || (scan.type === 'url' ? scan.url || 'URL scan' : 'Text scan');
        const confidence = scan.confidence || 0;
        
        return `
            <tr>
                <td>${scan.type === 'url' ? '🔗 URL' : '📝 Text'}</td>
                <td>${truncateText(contentPreview, 60)}</td>
                <td><strong>${scan.scam_percentage || 0}%</strong></td>
                <td>${statusBadge}</td>
                <td>${confidence}%</td>
                <td>${timestamp}</td>
            </tr>
        `;
    }).join('');
}

function truncateText(text, maxLength) {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}


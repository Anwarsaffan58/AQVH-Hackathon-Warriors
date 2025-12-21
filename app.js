// Application data from provided JSON
const applicationData = {
    qkd_protocols: [
        {"name": "BB84", "description": "Bennett-Brassard 1984 protocol using polarized photons", "security_level": "High", "implementation_status": "Active"},
        {"name": "E91", "description": "Ekert 1991 protocol using quantum entanglement", "security_level": "Ultra-High", "implementation_status": "Active"}
    ],
    communication_platforms: [
        {"name": "Satellite", "status": "Secure", "encryption_strength": 256, "last_key_exchange": "2025-08-20 21:30:15"},
        {"name": "Naval", "status": "Secure", "encryption_strength": 256, "last_key_exchange": "2025-08-20 21:25:42"},
        {"name": "Airborne", "status": "Monitoring", "encryption_strength": 128, "last_key_exchange": "2025-08-20 21:20:33"},
        {"name": "Ground", "status": "Secure", "encryption_strength": 256, "last_key_exchange": "2025-08-20 21:35:01"}
    ],
    threat_detection: [
        {"timestamp": "2025-08-20 21:32:15", "threat_type": "Eavesdropping Attempt", "platform": "Airborne", "severity": "Medium", "status": "Mitigated"},
        {"timestamp": "2025-08-20 21:28:42", "threat_type": "Key Compromise", "platform": "Ground", "severity": "Low", "status": "Resolved"},
        {"timestamp": "2025-08-20 21:15:33", "threat_type": "Quantum Decoherence", "platform": "Satellite", "severity": "High", "status": "Monitoring"}
    ],
    qrng_metrics: {"generation_rate": "5.7 Gbps", "entropy_level": 0.9987, "randomness_tests_passed": 15, "current_buffer": 1024},
    system_performance: {"cpu_usage": 67, "quantum_coherence": 0.94, "network_latency": 12, "security_score": 98},
    ai_anomaly_data: [
        {"time": "21:00", "normal_score": 0.95, "anomaly_score": 0.05},
        {"time": "21:05", "normal_score": 0.92, "anomaly_score": 0.08},
        {"time": "21:10", "normal_score": 0.89, "anomaly_score": 0.11},
        {"time": "21:15", "normal_score": 0.78, "anomaly_score": 0.22},
        {"time": "21:20", "normal_score": 0.85, "anomaly_score": 0.15},
        {"time": "21:25", "normal_score": 0.93, "anomaly_score": 0.07},
        {"time": "21:30", "normal_score": 0.96, "anomaly_score": 0.04},
        {"time": "21:35", "normal_score": 0.94, "anomaly_score": 0.06}
    ],
    quantum_states: {"bell_state_fidelity": 0.987, "entanglement_strength": 0.943, "superposition_coherence": 0.891, "measurement_accuracy": 0.994}
};

// Global variables
let charts = {};
let updateIntervals = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    initializeApp();
});

function initializeApp() {
    setupTabSwitching();
    updateTimestamp();
    populateInitialData();
    
    // Delay chart initialization to ensure elements are ready
    setTimeout(() => {
        initializeCharts();
    }, 100);
    
    startRealTimeUpdates();
    setupEventListeners();
    console.log('App initialized successfully');
}

// Tab switching functionality - Fixed version
function setupTabSwitching() {
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabContents = document.querySelectorAll('.tab-content');

    console.log('Found nav tabs:', navTabs.length);
    console.log('Found tab contents:', tabContents.length);

    navTabs.forEach((tab, index) => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Tab clicked:', this.dataset.tab);
            
            const targetTab = this.dataset.tab;
            
            // Remove active class from all tabs and contents
            navTabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            const targetContent = document.getElementById(targetTab);
            if (targetContent) {
                targetContent.classList.add('active');
                console.log('Switched to tab:', targetTab);
                
                // Initialize charts for specific tabs when they become active
                if (targetTab === 'qrng' && !charts.entropy) {
                    setTimeout(initializeEntropyChart, 100);
                } else if (targetTab === 'ai-detection' && !charts.aiDetection) {
                    setTimeout(initializeAIDetectionChart, 100);
                } else if (targetTab === 'analytics' && !charts.performance) {
                    setTimeout(() => {
                        initializePerformanceChart();
                        initializeSuccessRateChart();
                    }, 100);
                }
            } else {
                console.error('Target content not found:', targetTab);
            }
        });
    });
}

// Update timestamp every second
function updateTimestamp() {
    const timestampElement = document.getElementById('current-timestamp');
    
    function update() {
        const now = new Date();
        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        };
        if (timestampElement) {
            timestampElement.textContent = now.toLocaleString('en-US', options);
        }
    }
    
    update();
    setInterval(update, 1000);
}

// Populate initial data
function populateInitialData() {
    populatePlatformsTable();
    populateThreatLog();
    populateDetailedThreatList();
    updateSystemMetrics();
    updateQRNGMetrics();
}

// Populate communication platforms table
function populatePlatformsTable() {
    const tbody = document.getElementById('platforms-table-body');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    applicationData.communication_platforms.forEach(platform => {
        const row = document.createElement('tr');
        const statusClass = platform.status.toLowerCase();
        
        row.innerHTML = `
            <td>${platform.name}</td>
            <td><span class="status-indicator ${statusClass}">${platform.status}</span></td>
            <td>${platform.encryption_strength}-bit</td>
            <td>${platform.last_key_exchange}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// Populate threat log
function populateThreatLog() {
    const threatLog = document.getElementById('threat-log');
    if (!threatLog) return;
    
    threatLog.innerHTML = '';
    
    applicationData.threat_detection.forEach(threat => {
        const threatItem = document.createElement('div');
        threatItem.className = 'threat-item';
        
        threatItem.innerHTML = `
            <div class="threat-info">
                <div class="threat-timestamp">${threat.timestamp}</div>
                <div class="threat-type">${threat.threat_type}</div>
                <div class="threat-platform">Platform: ${threat.platform}</div>
            </div>
            <div class="threat-badges">
                <span class="severity-badge ${threat.severity.toLowerCase()}">${threat.severity}</span>
            </div>
        `;
        
        threatLog.appendChild(threatItem);
    });
}

// Populate detailed threat list
function populateDetailedThreatList() {
    const threatList = document.getElementById('detailed-threat-list');
    if (!threatList) return;
    
    threatList.innerHTML = '';
    
    applicationData.threat_detection.forEach(threat => {
        const threatItem = document.createElement('div');
        threatItem.className = 'threat-item';
        
        threatItem.innerHTML = `
            <div class="threat-info">
                <div class="threat-timestamp">${threat.timestamp}</div>
                <div class="threat-type">${threat.threat_type}</div>
                <div class="threat-platform">Platform: ${threat.platform} | Status: ${threat.status}</div>
            </div>
            <div class="threat-badges">
                <span class="severity-badge ${threat.severity.toLowerCase()}">${threat.severity}</span>
            </div>
        `;
        
        threatList.appendChild(threatItem);
    });
}

// Update system metrics
function updateSystemMetrics() {
    const metrics = applicationData.system_performance;
    
    const elements = {
        'cpu-usage': `${metrics.cpu_usage}%`,
        'quantum-coherence': metrics.quantum_coherence.toFixed(2),
        'network-latency': `${metrics.network_latency}ms`,
        'security-score': `${metrics.security_score}%`
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
    
    // Update progress bars safely
    const progressUpdates = [
        { selector: '#cpu-usage', width: `${metrics.cpu_usage}%` },
        { selector: '#quantum-coherence', width: `${metrics.quantum_coherence * 100}%` },
        { selector: '#network-latency', width: `${100 - metrics.network_latency}%` },
        { selector: '#security-score', width: `${metrics.security_score}%` }
    ];
    
    progressUpdates.forEach(update => {
        const element = document.querySelector(update.selector);
        if (element && element.nextElementSibling) {
            const progressFill = element.nextElementSibling.querySelector('.progress-fill');
            if (progressFill) {
                progressFill.style.width = update.width;
            }
        }
    });
}

// Update QRNG metrics
function updateQRNGMetrics() {
    const qrng = applicationData.qrng_metrics;
    
    const elements = {
        'generation-rate': qrng.generation_rate,
        'entropy-value': `${(qrng.entropy_level * 100).toFixed(2)}%`,
        'tests-passed': `${qrng.randomness_tests_passed}/15`
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
    
    // Update entropy gauge
    updateEntropyGauge(qrng.entropy_level);
}

function updateEntropyGauge(entropyLevel) {
    const gaugeCircle = document.querySelector('.gauge-circle');
    if (gaugeCircle) {
        const percentage = entropyLevel * 100;
        const degrees = (percentage / 100) * 360;
        gaugeCircle.style.background = `conic-gradient(#32b8c5 0deg, #32b8c5 ${degrees}deg, #2a3441 ${degrees}deg)`;
    }
}

// Initialize charts
function initializeCharts() {
    console.log('Initializing charts...');
    
    // Only initialize anomaly chart initially (it's on the overview tab)
    initializeAnomalyChart();
}

// Anomaly detection chart
function initializeAnomalyChart() {
    const canvas = document.getElementById('anomaly-chart');
    if (!canvas) {
        console.warn('Anomaly chart canvas not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    charts.anomaly = new Chart(ctx, {
        type: 'line',
        data: {
            labels: applicationData.ai_anomaly_data.map(d => d.time),
            datasets: [
                {
                    label: 'Normal Score',
                    data: applicationData.ai_anomaly_data.map(d => d.normal_score),
                    borderColor: '#4ade80',
                    backgroundColor: 'rgba(74, 222, 128, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Anomaly Score',
                    data: applicationData.ai_anomaly_data.map(d => d.anomaly_score),
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#f5f5f5'
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#a7a9a9' },
                    grid: { color: '#2a3441' }
                },
                y: {
                    ticks: { color: '#a7a9a9' },
                    grid: { color: '#2a3441' },
                    min: 0,
                    max: 1
                }
            }
        }
    });
    
    console.log('Anomaly chart initialized');
}

// Entropy analysis chart
function initializeEntropyChart() {
    const canvas = document.getElementById('entropy-chart');
    if (!canvas) {
        console.warn('Entropy chart canvas not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    const entropyData = Array.from({length: 20}, (_, i) => ({
        time: `${20 + i}:00`,
        quantum: 0.995 + Math.random() * 0.004,
        classical: 0.85 + Math.random() * 0.1
    }));
    
    charts.entropy = new Chart(ctx, {
        type: 'line',
        data: {
            labels: entropyData.map(d => d.time),
            datasets: [
                {
                    label: 'Quantum Entropy',
                    data: entropyData.map(d => d.quantum),
                    borderColor: '#32b8c5',
                    backgroundColor: 'rgba(50, 184, 197, 0.1)',
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Classical Entropy',
                    data: entropyData.map(d => d.classical),
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251, 191, 36, 0.1)',
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#f5f5f5'
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#a7a9a9' },
                    grid: { color: '#2a3441' }
                },
                y: {
                    ticks: { color: '#a7a9a9' },
                    grid: { color: '#2a3441' },
                    min: 0.8,
                    max: 1
                }
            }
        }
    });
    
    console.log('Entropy chart initialized');
}

// AI Detection detailed chart
function initializeAIDetectionChart() {
    const canvas = document.getElementById('ai-detection-chart');
    if (!canvas) {
        console.warn('AI detection chart canvas not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    const detectionData = Array.from({length: 24}, (_, i) => ({
        time: `${i}:00`,
        confidence: 0.7 + Math.random() * 0.3,
        threshold: 0.8
    }));
    
    charts.aiDetection = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: detectionData.map(d => d.time),
            datasets: [
                {
                    label: 'Detection Confidence',
                    data: detectionData.map(d => d.confidence),
                    backgroundColor: detectionData.map(d => d.confidence > 0.8 ? '#4ade80' : '#fbbf24'),
                    borderColor: detectionData.map(d => d.confidence > 0.8 ? '#4ade80' : '#fbbf24'),
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#f5f5f5'
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#a7a9a9' },
                    grid: { color: '#2a3441' }
                },
                y: {
                    ticks: { color: '#a7a9a9' },
                    grid: { color: '#2a3441' },
                    min: 0,
                    max: 1
                }
            }
        }
    });
    
    console.log('AI detection chart initialized');
}

// Performance analytics chart
function initializePerformanceChart() {
    const canvas = document.getElementById('performance-chart');
    if (!canvas) {
        console.warn('Performance chart canvas not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    const performanceData = Array.from({length: 12}, (_, i) => ({
        hour: `${12 + i}:00`,
        fidelity: 0.98 + Math.random() * 0.015,
        efficiency: 0.92 + Math.random() * 0.06
    }));
    
    charts.performance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: performanceData.map(d => d.hour),
            datasets: [
                {
                    label: 'Quantum State Fidelity',
                    data: performanceData.map(d => d.fidelity),
                    borderColor: '#32b8c5',
                    backgroundColor: 'rgba(50, 184, 197, 0.1)',
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Channel Efficiency',
                    data: performanceData.map(d => d.efficiency),
                    borderColor: '#4ade80',
                    backgroundColor: 'rgba(74, 222, 128, 0.1)',
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#f5f5f5'
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#a7a9a9' },
                    grid: { color: '#2a3441' }
                },
                y: {
                    ticks: { color: '#a7a9a9' },
                    grid: { color: '#2a3441' },
                    min: 0.9,
                    max: 1
                }
            }
        }
    });
    
    console.log('Performance chart initialized');
}

// Success rate chart
function initializeSuccessRateChart() {
    const canvas = document.getElementById('success-rate-chart');
    if (!canvas) {
        console.warn('Success rate chart canvas not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    charts.successRate = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Successful', 'Failed', 'Retried'],
            datasets: [{
                data: [94.7, 2.1, 3.2],
                backgroundColor: ['#4ade80', '#ef4444', '#fbbf24'],
                borderColor: '#1a1f2e',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#f5f5f5'
                    }
                }
            }
        }
    });
    
    console.log('Success rate chart initialized');
}

// Real-time updates
function startRealTimeUpdates() {
    // Update system metrics every 5 seconds
    const metricsInterval = setInterval(() => {
        updateSystemMetricsRealTime();
    }, 5000);
    
    // Update charts every 10 seconds
    const chartsInterval = setInterval(() => {
        updateChartsRealTime();
    }, 10000);
    
    // Update threat log every 15 seconds
    const threatsInterval = setInterval(() => {
        addRandomThreat();
    }, 15000);
    
    updateIntervals.push(metricsInterval, chartsInterval, threatsInterval);
}

// Update system metrics with small variations
function updateSystemMetricsRealTime() {
    const metrics = applicationData.system_performance;
    
    // Small random variations
    const cpuVariation = Math.floor(Math.random() * 10) - 5;
    const coherenceVariation = (Math.random() - 0.5) * 0.02;
    const latencyVariation = Math.floor(Math.random() * 6) - 3;
    const securityVariation = Math.floor(Math.random() * 4) - 2;
    
    const newCpu = Math.max(0, Math.min(100, metrics.cpu_usage + cpuVariation));
    const newCoherence = Math.max(0.8, Math.min(1, metrics.quantum_coherence + coherenceVariation));
    const newLatency = Math.max(5, Math.min(30, metrics.network_latency + latencyVariation));
    const newSecurity = Math.max(90, Math.min(100, metrics.security_score + securityVariation));
    
    // Update stored values
    applicationData.system_performance = {
        cpu_usage: newCpu,
        quantum_coherence: newCoherence,
        network_latency: newLatency,
        security_score: newSecurity
    };
    
    // Update display
    updateSystemMetrics();
}

// Update charts with new data points
function updateChartsRealTime() {
    if (charts.anomaly && charts.anomaly.data) {
        const newTime = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
        const normalScore = 0.85 + Math.random() * 0.1;
        const anomalyScore = Math.max(0, Math.min(1, 1 - normalScore + (Math.random() - 0.5) * 0.05));
        
        charts.anomaly.data.labels.push(newTime);
        charts.anomaly.data.datasets[0].data.push(normalScore);
        charts.anomaly.data.datasets[1].data.push(anomalyScore);
        
        // Keep only last 10 data points
        if (charts.anomaly.data.labels.length > 10) {
            charts.anomaly.data.labels.shift();
            charts.anomaly.data.datasets[0].data.shift();
            charts.anomaly.data.datasets[1].data.shift();
        }
        
        charts.anomaly.update('none'); // No animation for better performance
    }
}

// Add random threat to log
function addRandomThreat() {
    const threatTypes = ['Eavesdropping Attempt', 'Key Compromise', 'Quantum Decoherence', 'Signal Interference', 'Authentication Failure'];
    const platforms = ['Satellite', 'Naval', 'Airborne', 'Ground'];
    const severities = ['Low', 'Medium', 'High'];
    const statuses = ['Detected', 'Monitoring', 'Mitigating'];
    
    const newThreat = {
        timestamp: new Date().toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        }),
        threat_type: threatTypes[Math.floor(Math.random() * threatTypes.length)],
        platform: platforms[Math.floor(Math.random() * platforms.length)],
        severity: severities[Math.floor(Math.random() * severities.length)],
        status: statuses[Math.floor(Math.random() * statuses.length)]
    };
    
    // Add to beginning of array
    applicationData.threat_detection.unshift(newThreat);
    
    // Keep only last 10 threats
    if (applicationData.threat_detection.length > 10) {
        applicationData.threat_detection.pop();
    }
    
    // Update displays
    populateThreatLog();
    populateDetailedThreatList();
}

// Setup event listeners
function setupEventListeners() {
    // Protocol buttons
    document.addEventListener('click', function(e) {
        if (e.target.matches('.protocol-card .btn')) {
            const protocolName = e.target.closest('.protocol-card').querySelector('h3').textContent;
            showNotification(`Starting ${protocolName} protocol simulation...`);
            animateKeyGeneration();
        }
        
        // QRNG generate button
        if (e.target.matches('.qrng-controls .btn--primary')) {
            generateRandomNumbers();
        }
        
        // Response action buttons
        if (e.target.matches('.response-actions .btn')) {
            const action = e.target.textContent;
            showNotification(`Executing: ${action}`);
            // Add visual feedback
            e.target.style.transform = 'scale(0.95)';
            setTimeout(() => {
                e.target.style.transform = 'scale(1)';
            }, 150);
        }
    });
    
    // Sensitivity slider
    document.addEventListener('input', function(e) {
        if (e.target.matches('.sensitivity-slider')) {
            const value = e.target.value;
            const nextSibling = e.target.nextElementSibling;
            if (nextSibling) {
                nextSibling.textContent = `${value}%`;
            }
        }
    });
}

// Show notification (simple alert replacement)
function showNotification(message) {
    // Create a simple notification element
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #32b8c5;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 1000;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Animate key generation progress
function animateKeyGeneration() {
    const progressBar = document.getElementById('key-progress');
    const progressText = document.querySelector('.progress-text');
    if (!progressBar || !progressText) return;
    
    let progress = 0;
    
    const interval = setInterval(() => {
        progress += Math.random() * 3;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            
            // Update keys generated counter
            const keysGenerated = document.getElementById('keys-generated');
            if (keysGenerated) {
                const currentKeys = parseInt(keysGenerated.textContent.replace(/,/g, '')) || 0;
                keysGenerated.textContent = (currentKeys + 1).toLocaleString();
            }
        }
        
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${Math.floor(progress)}% Complete`;
    }, 200);
}

// Generate random numbers
function generateRandomNumbers() {
    const numberTypeSelect = document.querySelector('.qrng-controls select');
    const lengthInput = document.querySelector('.qrng-controls input[type="number"]');
    const textarea = document.querySelector('.generated-numbers textarea');
    
    if (!numberTypeSelect || !lengthInput || !textarea) return;
    
    const numberType = numberTypeSelect.value;
    const length = parseInt(lengthInput.value) || 256;
    let result = '';
    
    switch (numberType.toLowerCase()) {
        case 'binary':
            for (let i = 0; i < length; i++) {
                result += Math.floor(Math.random() * 2);
                if (i > 0 && i % 8 === 7) result += ' ';
            }
            break;
        case 'hexadecimal':
            for (let i = 0; i < length; i++) {
                result += Math.floor(Math.random() * 16).toString(16).toUpperCase();
                if (i > 0 && i % 4 === 3) result += ' ';
            }
            break;
        case 'decimal':
            for (let i = 0; i < length; i++) {
                result += Math.floor(Math.random() * 10);
                if (i > 0 && i % 5 === 4) result += ' ';
            }
            break;
    }
    
    textarea.value = result;
    
    // Update generation rate display
    const newRate = (5.5 + Math.random() * 0.4).toFixed(1);
    const generationRateElement = document.getElementById('generation-rate');
    if (generationRateElement) {
        generationRateElement.textContent = `${newRate} Gbps`;
    }
    
    showNotification(`Generated ${length} random numbers`);
}

// Cleanup function
function cleanup() {
    updateIntervals.forEach(interval => clearInterval(interval));
    Object.values(charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
}

// Handle page unload
window.addEventListener('beforeunload', cleanup);
A
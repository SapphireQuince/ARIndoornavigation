// Main JavaScript file for Indoor Navigation System
class IndoorNavigation {
    constructor() {
        this.init();
    }

    init() {
        this.setupServiceWorker();
        this.setupEventListeners();
        this.checkSystemStatus();
    }

    setupServiceWorker() {
        // Register service worker for PWA functionality
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);
                })
                .catch(error => {
                    console.log('Service Worker registration failed:', error);
                });
        }
    }

    setupEventListeners() {
        // Handle destination card clicks with loading state
        const destinationCards = document.querySelectorAll('.destination-card, .destination-item');
        destinationCards.forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault();
                const destination = card.querySelector('.destination-name') || 
                                 card.querySelector('.destination-details h3');
                
                if (destination) {
                    this.showLoading(destination.textContent);
                    setTimeout(() => {
                        window.location.href = card.href;
                    }, 500);
                }
            });
        });

        // Handle back button
        const backButtons = document.querySelectorAll('.back-button');
        backButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                history.back();
            });
        });

        // Handle camera permission requests
        this.checkCameraPermission();
    }

    showLoading(destination) {
        const loadingHTML = `
            <div class="loading-overlay">
                <div class="loading-content">
                    <div class="loading-spinner"></div>
                    <p>Starting navigation to ${destination}...</p>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', loadingHTML);
    }

    async checkCameraPermission() {
        try {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                // Check if camera permission is already granted
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'environment' } 
                });
                stream.getTracks().forEach(track => track.stop());
                console.log('Camera permission granted');
            }
        } catch (error) {
            console.log('Camera permission not granted or not available:', error);
        }
    }

    async checkSystemStatus() {
        try {
            const response = await fetch('/api/health');
            const status = await response.json();
            
            if (!status.model_loaded) {
                this.showSystemAlert('Model not loaded. Please check model files.');
            }
            
            console.log('System status:', status);
        } catch (error) {
            console.error('Failed to check system status:', error);
        }
    }

    showSystemAlert(message) {
        const alertHTML = `
            <div class="system-alert">
                <div class="alert-content">
                    <h3>⚠️ System Notice</h3>
                    <p>${message}</p>
                    <button onclick="this.parentElement.parentElement.remove()">OK</button>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', alertHTML);
    }

    // Utility functions
    static formatTime(date = new Date()) {
        return date.toLocaleTimeString();
    }

    static vibrate(pattern = [100]) {
        if ('vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    }

    static showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'error' ? '#f44336' : '#2196F3'};
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            z-index: 1000;
            animation: slideUp 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize the navigation system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const navigation = new IndoorNavigation();
});

// Add CSS for loading overlay and alerts
const styles = `
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .loading-content {
        text-align: center;
        color: white;
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 3px solid rgba(255,255,255,0.3);
        border-top: 3px solid #2196F3;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 20px;
    }
    
    .system-alert {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .alert-content {
        background: white;
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        max-width: 300px;
        margin: 20px;
    }
    
    .alert-content h3 {
        margin-bottom: 15px;
        color: #f44336;
    }
    
    .alert-content button {
        background: #2196F3;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 20px;
        margin-top: 15px;
        cursor: pointer;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes slideUp {
        from { transform: translate(-50%, 100px); opacity: 0; }
        to { transform: translate(-50%, 0); opacity: 1; }
    }
    
    @keyframes slideDown {
        from { transform: translate(-50%, 0); opacity: 1; }
        to { transform: translate(-50%, 100px); opacity: 0; }
    }
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = styles;
document.head.appendChild(styleSheet);
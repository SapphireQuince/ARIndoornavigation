// AR Navigation main controller class

class ARNavigation {
    constructor(options = {}) {
        this.destination = options.destination || 'Unknown';
        this.entranceId = options.entranceId || 1;
        this.serverUrl = options.serverUrl || window.location.origin;

        this.camera = new CameraManager();
        this.socket = null;
        this.isProcessing = false;
        this.frameInterval = null;
        this.confidenceThreshold = 0.0; // Set to 0.0 for home testing. Change back to 0.5 for real use.

        this.elements = {};
        this.setupElements();
    }

    setupElements() {
        const ids = [
            'camera', 'overlay-canvas', 'loading-screen', 'error-screen', 'retry-btn',
            'back-error-btn', 'instruction-text', 'direction-arrow', 'connection-status',
            'confidence-fill', 'confidence-value'
        ];
        ids.forEach(id => {
            const el = document.getElementById(id);
            if (!el) {
                console.warn(`⚠️ Element with id '${id}' not found in DOM.`);
            }
            this.elements[id.replace(/-/g, '')] = el;
        });
        
        if (this.elements.retrybtn) {
            this.elements.retrybtn.addEventListener('click', () => {
                this.elements.errorscreen?.classList.add('hidden');
                this.restartNavigation();
            });
        }

        if (this.elements.backerrorbtn) {
            this.elements.backerrorbtn.addEventListener('click', () => {
                window.history.back();
            });
        }
    }

    async initialize() {
        try {
            // Prevent double initialization
            if (this.camera.isWorking()) {
                console.log('✅ Camera already initialized, skipping re-init.');
            } else {
                await this.setupCamera();
            }

            if (!this.socket || !this.socket.connected) {
                await this.connectToServer();
            }

            this.startNavigation();
            this.hideLoadingScreen();
        } catch (err) {
            this.showError(err.message);
        }
    }

    async setupCamera() {
        this.updateLoadingStep('step-camera', true);
        try {
            await this.camera.initialize(
                this.elements.camera,
                this.elements.overlaycanvas,
                'environment'
            );
            console.log('✅ Camera initialized successfully');
        } catch (err) {
            throw new Error('Failed to access camera. Please allow permissions and try again.');
        }
    }

    async connectToServer() {
        this.updateLoadingStep('step-connection', true);
        return new Promise((resolve, reject) => {
            // FORCE websocket only to prevent Ngrok/Eventlet handshake errors
            this.socket = io(this.serverUrl, { 
                transports: ['websocket'], 
                upgrade: false, // Don't try to upgrade from polling, start with WS
                reconnection: true,
                reconnectionAttempts: 5,
                timeout: 20000 // Give Ngrok plenty of time to route the connection
            });

            this.socket.on('connect', () => {
                // FIXED: Now uses the helper method to preserve the glowing dot CSS
                this.updateConnectionStatus('connected');
                console.log('✅ Connected to server via pure WebSocket');
                resolve();
            });

            this.socket.on('disconnect', () => {
                // FIXED: Preserves UI structure
                this.updateConnectionStatus('disconnected');
            });

            this.socket.on('navigation_result', data => {
                this.handleNavigationResult(data);
            });

            this.socket.on('connect_error', (err) => {
                console.error("❌ Socket connection error:", err);
                // FIXED: Preserves UI structure
                this.updateConnectionStatus('error');
            });

            // If we don't connect within 15 seconds, timeout and fail gracefully
            setTimeout(() => {
                if (!this.socket.connected) {
                    reject(new Error('Connection to server timed out. Check Ngrok tunnel.'));
                }
            }, 15000);
        });
    }

    startNavigation() {
        this.updateLoadingStep('step-ready', true);

        if (this.frameInterval) clearInterval(this.frameInterval);
        
        // Interval set to 150ms for smoother AR performance
        this.frameInterval = setInterval(() => this.processFrame(), 150);

        this.updateInstructions('Point your camera at the hallway ahead');
    }

    processFrame() {
        if (this.isProcessing || !this.camera.isWorking()) return;
        const frame = this.camera.captureFrame();
        if (!frame) return;

        this.isProcessing = true;
        this.socket.emit('process_frame', {
            frame,
            destination: this.destination,
            entrance_id: this.entranceId,
            timestamp: Date.now()
        });
    }

    handleNavigationResult(data) {
        this.isProcessing = false;
        if (data.error) {
            console.error("Navigation error from server:", data.error);
            return;
        }
        this.updateConfidence(data.confidence);
        this.updateNavigationUI(data.navigation, data.confidence);
    }

    updateNavigationUI(navigation, confidence) {
        if (confidence < this.confidenceThreshold) {
            this.updateInstructions('Keep camera steady...', 'warning');
            return;
        }
        this.updateInstructions(navigation.message);
        this.updateDirectionArrow(navigation.action);
        
        if (['turn_left', 'turn_right', 'destination_reached'].includes(navigation.action)) {
            if (navigator.vibrate) navigator.vibrate(50); // Short tap vibration
        }
        if (navigation.action === 'destination_reached') {
            this.handleDestinationReached();
        }
    }

    updateInstructions(text, type = 'normal') {
        if (this.elements.instructiontext) {
            this.elements.instructiontext.textContent = text;
            this.elements.instructiontext.className = `instruction-text instruction-${type}`;
        }
    }

    updateDirectionArrow(action) {
        if (!this.elements.directionarrow) return;
        const map = {
            continue_straight: '↑',
            turn_left: '←',
            turn_right: '→',
            go_upstairs: '⬆️',
            go_downstairs: '⬇️',
            destination_reached: '🎯',
            choose_direction: '❓'
        };
        // Safely map the action or default to straight
        this.elements.directionarrow.textContent = map[action] || '↑';
    }

    updateConnectionStatus(status) {
        if (!this.elements.connectionstatus) return;
        const dot = this.elements.connectionstatus.querySelector('.status-dot');
        const text = this.elements.connectionstatus.querySelector('span:last-child');
        
        if (dot) dot.className = `status-dot ${status}`;
        if (text) {
            const messages = {
                connected: 'Connected',
                connecting: 'Connecting...',
                disconnected: 'Disconnected',
                error: 'Connection Error'
            };
            text.textContent = messages[status] || status;
        }
    }

    updateConfidence(confidence) {
        if (!this.elements.confidencevalue || !this.elements.confidencefill) return;
        const pct = Math.round(confidence * 100);
        this.elements.confidencevalue.textContent = `${pct}%`;
        this.elements.confidencefill.style.width = `${pct}%`;
    }

    updateLoadingStep(id, active) {
        const el = document.getElementById(id);
        if (el) el.classList.toggle('active', active);
    }

    hideLoadingScreen() {
        if (this.elements.loadingscreen) this.elements.loadingscreen.style.display = 'none';
    }

    showError(msg) {
        this.hideLoadingScreen();
        const msgEl = document.getElementById('error-message');
        if (msgEl) msgEl.textContent = msg;
        if (this.elements.errorscreen) this.elements.errorscreen.classList.remove('hidden');
    }

    restartNavigation() {
        if (this.frameInterval) clearInterval(this.frameInterval);
        if (this.socket) this.socket.disconnect();
        this.camera.stop();
        if (this.elements.loadingscreen) this.elements.loadingscreen.style.display = 'flex';
        this.initialize();
    }

    handleDestinationReached() {
        if (this.frameInterval) clearInterval(this.frameInterval);
        this.updateInstructions("🎉 You've arrived!");
        if (this.elements.directionarrow) this.elements.directionarrow.textContent = '🎯';
        if (navigator.vibrate) navigator.vibrate([200, 100, 200]);
        setTimeout(() => window.history.back(), 5000);
    }
}
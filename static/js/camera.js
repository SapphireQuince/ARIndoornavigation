class CameraManager {
    constructor() {
        this.stream = null;
        this.video = null;
        this.isStreaming = false;

        // Hidden canvas strictly for resizing images for the ML model
        this.captureCanvas = document.createElement('canvas');
        this.captureCanvas.width = 224;  
        this.captureCanvas.height = 224;
        this.captureContext = this.captureCanvas.getContext('2d');
    }

    isWorking() {
        return this.isStreaming;
    }

    async initialize(videoElement, canvasElement, facingMode = 'environment') {
        this.video = videoElement;
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode, width: { ideal: 640 }, height: { ideal: 480 } },
                audio: false
            });
            this.video.srcObject = this.stream;
            await new Promise(resolve => this.video.onloadedmetadata = resolve);
            this.video.play();
            this.isStreaming = true;
            return true;
        } catch (err) {
            console.error("Camera init failed:", err);
            this.isStreaming = false;
            return false;
        }
    }

    captureFrame() {
        if (!this.isStreaming) return null;
        // Draw to tiny canvas and compress to JPEG to save bandwidth
        this.captureContext.drawImage(this.video, 0, 0, 224, 224);
        return this.captureCanvas.toDataURL('image/jpeg', 0.5);
    }

    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(t => t.stop());
            this.isStreaming = false;
        }
    }
}
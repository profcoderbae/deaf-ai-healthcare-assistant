/**
 * Sign Language Detection Client (SocketIO)
 * ==========================================
 * Adapted from COS301-SE-2025/Hands-Up frontend architecture.
 *
 * Uses MediaPipe Hands (browser) for landmark overlay + sends frames
 * to Flask-SocketIO backend for ASL classification.
 *
 * Modes: 'alpha' (letters), 'num' (numbers), 'glosses' (words/gestures)
 *
 * Features from Hands-Up:
 *  - Real-time frame capture from webcam (every 150ms)
 *  - Three detection modes switchable with UI buttons
 *  - Confidence display
 *  - Sentence builder from detected signs
 *  - Visual landmark overlay on hand
 */

class SignDetectionClient {
    constructor(opts = {}) {
        this.socket = null;
        this.videoElement = opts.video || null;
        this.canvasElement = opts.canvas || null;
        this.canvasCtx = null;
        this.mode = opts.mode || 'glosses';
        this.isActive = false;
        this.captureInterval = null;
        this.captureRate = opts.captureRate || 150; // ms between frames
        this.onDetection = opts.onDetection || null;
        this.onStatusChange = opts.onStatusChange || null;
        this.mpHands = null;
        this.handResults = null;
        this.lastFrameTime = 0;

        // Sentence builder state
        this.sentence = [];
        this.lastWord = '';
        this.lastWordTime = 0;
    }

    /* ═══════════════════════════════════════════════════════════
       INIT — Connect SocketIO + start MediaPipe Hands overlay
       ═══════════════════════════════════════════════════════════ */
    async init() {
        // Connect to Flask-SocketIO
        this.socket = io({
            transports: ['polling', 'websocket'],
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
        });

        this.socket.on('connect', () => {
            console.log('[SignDetect] Connected to server, sid:', this.socket.id);
            this.socket.emit('set_mode', { mode: this.mode });
            if (this.onStatusChange) this.onStatusChange('connected');
        });

        this.socket.on('connect_error', (err) => {
            console.error('[SignDetect] Connection error:', err.message);
            if (this.onStatusChange) this.onStatusChange('error');
        });

        this.socket.on('disconnect', (reason) => {
            console.log('[SignDetect] Disconnected:', reason);
            if (this.onStatusChange) this.onStatusChange('disconnected');
        });

        this.socket.on('detection', (data) => {
            this._handleDetection(data);
        });

        this.socket.on('mode_changed', (data) => {
            this.mode = data.mode;
            if (this.onStatusChange) this.onStatusChange('mode:' + data.mode);
        });

        // Init MediaPipe Hands for landmark overlay (visual only)
        if (this.canvasElement) {
            this.canvasCtx = this.canvasElement.getContext('2d');
            await this._initMediaPipeOverlay();
        }
    }

    /* ═══════════════════════════════════════════════════════════
       START/STOP detection
       ═══════════════════════════════════════════════════════════ */
    async start(videoElement, canvasElement) {
        if (videoElement) this.videoElement = videoElement;
        if (canvasElement) {
            this.canvasElement = canvasElement;
            this.canvasCtx = canvasElement.getContext('2d');
        }

        // If socket not initialized yet, init it
        if (!this.socket) {
            await this.init();
        }

        // Wait for connection (up to 5 seconds)
        if (!this.socket.connected) {
            await new Promise((resolve) => {
                const onConnect = () => { resolve(); };
                this.socket.once('connect', onConnect);
                setTimeout(() => {
                    this.socket.off('connect', onConnect);
                    resolve();
                }, 5000);
            });
        }

        this.isActive = true;

        // Start capturing frames
        this.captureInterval = setInterval(() => {
            if (this.isActive && this.videoElement && this.socket && this.socket.connected) {
                this._captureAndSend();
            }
        }, this.captureRate);

        // Start landmark overlay loop
        if (this.mpHands && this.canvasElement) {
            this._detectLoop();
        }

        if (this.onStatusChange) this.onStatusChange('active');
    }

    stop() {
        this.isActive = false;
        if (this.captureInterval) {
            clearInterval(this.captureInterval);
            this.captureInterval = null;
        }
        if (this.onStatusChange) this.onStatusChange('stopped');
    }

    setMode(mode) {
        this.mode = mode;
        this.sentence = [];
        this.lastWord = '';
        if (this.socket && this.socket.connected) {
            this.socket.emit('set_mode', { mode });
        }
    }

    getSentence() {
        return this.sentence.join(' ');
    }

    clearSentence() {
        this.sentence = [];
        this.lastWord = '';
    }

    addWordToSentence(word) {
        const now = Date.now();
        if (word === this.lastWord && (now - this.lastWordTime) < 2000) return;
        this.sentence.push(word);
        this.lastWord = word;
        this.lastWordTime = now;
    }

    destroy() {
        this.stop();
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       PRIVATE — Frame capture & send
       ═══════════════════════════════════════════════════════════ */
    _captureAndSend() {
        const video = this.videoElement;
        if (!video || video.readyState < 2) return;

        // Capture at 640x480 for server processing (balance quality vs speed)
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = 640;
        tempCanvas.height = 480;
        const ctx = tempCanvas.getContext('2d');
        ctx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);

        const dataUrl = tempCanvas.toDataURL('image/jpeg', 0.85);
        this.socket.emit('frame', { image: dataUrl });
    }

    /* ═══════════════════════════════════════════════════════════
       PRIVATE — Handle detection results from server
       ═══════════════════════════════════════════════════════════ */
    _handleDetection(data) {
        if (data.error) {
            if (this.onDetection) this.onDetection({ type: 'error', error: data.error });
            return;
        }

        if (data.type === 'letter') {
            if (this.onDetection) this.onDetection({
                type: 'letter',
                value: data.letter,
                confidence: data.confidence,
                sentence: this.getSentence(),
            });
        } else if (data.type === 'number') {
            if (this.onDetection) this.onDetection({
                type: 'number',
                value: data.number,
                confidence: data.confidence,
                sentence: this.getSentence(),
            });
        } else if (data.type === 'word') {
            if (this.onDetection) this.onDetection({
                type: 'word',
                value: data.word,
                gesture: data.gesture || null,
                confidence: data.confidence,
                source: data.source || null,
                sentence: this.getSentence(),
            });
        } else if (data.status === 'collecting') {
            if (this.onDetection) this.onDetection({
                type: 'status',
                status: 'collecting',
                hint: data.hint || null,
                frames: data.frames || 0,
            });
        } else if (data.status === 'scanning') {
            if (this.onDetection) this.onDetection({ type: 'status', status: 'scanning' });
        } else if (data.status === 'no_hand') {
            if (this.onDetection) this.onDetection({ type: 'status', status: 'no_hand' });
        }
    }

    /* ═══════════════════════════════════════════════════════════
       PRIVATE — MediaPipe Hands overlay (draw landmarks on canvas)
       ═══════════════════════════════════════════════════════════ */
    async _initMediaPipeOverlay() {
        // Check if MediaPipe Hands is available (loaded from CDN)
        if (typeof Hands === 'undefined') {
            console.warn('[SignDetect] MediaPipe Hands not loaded, skipping overlay');
            return;
        }

        this.mpHands = new Hands({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
        });

        this.mpHands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5,
        });

        this.mpHands.onResults((results) => {
            this.handResults = results;
        });
    }

    async _detectLoop() {
        if (!this.isActive || !this.mpHands || !this.videoElement) return;

        const video = this.videoElement;
        if (video.readyState >= 2) {
            try {
                await this.mpHands.send({ image: video });
            } catch (e) { /* mediapipe can throw on rapid frames */ }

            // Draw overlay with detected landmarks
            if (this.handResults && this.canvasCtx && this.canvasElement) {
                const ctx = this.canvasCtx;
                const canvas = this.canvasElement;
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                if (this.handResults.multiHandLandmarks) {
                    for (const landmarks of this.handResults.multiHandLandmarks) {
                        // Draw connections
                        if (window.drawConnectors) {
                            drawConnectors(ctx, landmarks, HAND_CONNECTIONS, {
                                color: '#00FF88',
                                lineWidth: 3,
                            });
                        }
                        // Draw landmarks
                        if (window.drawLandmarks) {
                            drawLandmarks(ctx, landmarks, {
                                color: '#FF3366',
                                lineWidth: 1,
                                radius: 4,
                            });
                        }
                        // Draw bounding box
                        this._drawBoundingBox(ctx, landmarks, canvas.width, canvas.height);
                    }
                }
            }
        }

        if (this.isActive) {
            requestAnimationFrame(() => this._detectLoop());
        }
    }

    _drawBoundingBox(ctx, landmarks, w, h) {
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        for (const lm of landmarks) {
            minX = Math.min(minX, lm.x * w);
            minY = Math.min(minY, lm.y * h);
            maxX = Math.max(maxX, lm.x * w);
            maxY = Math.max(maxY, lm.y * h);
        }
        const pad = 20;
        ctx.strokeStyle = '#00FF88';
        ctx.lineWidth = 2;
        ctx.strokeRect(minX - pad, minY - pad, (maxX - minX) + 2 * pad, (maxY - minY) + 2 * pad);
    }
}

/**
 * Gesture Detection Module
 * Uses MediaPipe Hands to detect hand gestures via webcam
 * - Frame throttling: processes every 4th frame to reduce jitter
 * - Confidence accumulation: requires 3 consecutive same-gesture detections
 * - Auto-focus bounding box: draws green square around closest hand
 * - Cooldown: 3.5 seconds between gesture callbacks
 */

class GestureDetector {
    constructor() {
        this.hands = null;
        this.camera = null;
        this.videoElement = null;
        this.canvasElement = null;
        this.canvasCtx = null;
        this.onGesture = null;
        this.isRunning = false;
        this.lastGesture = null;
        this.gestureTimeout = null;
        this.waveHistory = [];
        this.lastWristX = null;
        this.waveCount = 0;

        // Frame throttling
        this.frameCount = 0;
        this.frameSkip = 3; // Process every 4th frame

        // Confidence accumulation
        this.gestureBuffer = [];
        this.requiredConfirmations = 3; // Need 3 same detections in a row

        // Cooldown
        this.gestureCooldown = 3500; // 3.5 seconds
        this.isCoolingDown = false;
    }

    async init(videoElement, canvasElement, onGestureCallback) {
        this.videoElement = videoElement;
        this.canvasElement = canvasElement;
        this.canvasCtx = canvasElement.getContext('2d');
        this.onGesture = onGestureCallback;

        this.hands = new Hands({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
        });

        this.hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.7,
            minTrackingConfidence: 0.6,
        });

        this.hands.onResults((results) => this.processResults(results));
    }

    async start() {
        if (this.isRunning) return;
        this.isRunning = true;

        this.camera = new Camera(this.videoElement, {
            onFrame: async () => {
                if (!this.isRunning) return;
                this.frameCount++;
                // Only process every Nth frame to reduce jitter
                if (this.frameCount % (this.frameSkip + 1) !== 0) return;
                await this.hands.send({ image: this.videoElement });
            },
            width: 1280,
            height: 720,
        });

        await this.camera.start();
    }

    stop() {
        this.isRunning = false;
        if (this.camera) {
            this.camera.stop();
        }
    }

    processResults(results) {
        const ctx = this.canvasCtx;
        const w = this.canvasElement.width;
        const h = this.canvasElement.height;

        ctx.save();
        ctx.clearRect(0, 0, w, h);

        if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
            // Pick the closest (largest) hand
            let bestIdx = 0;
            let bestSize = 0;
            results.multiHandLandmarks.forEach((lm, idx) => {
                const xs = lm.map(p => p.x);
                const ys = lm.map(p => p.y);
                const size = (Math.max(...xs) - Math.min(...xs)) * (Math.max(...ys) - Math.min(...ys));
                if (size > bestSize) { bestSize = size; bestIdx = idx; }
            });

            const landmarks = results.multiHandLandmarks[bestIdx];

            // Draw hand landmarks
            drawConnectors(ctx, landmarks, HAND_CONNECTIONS,
                { color: '#0D9488', lineWidth: 3 });
            drawLandmarks(ctx, landmarks,
                { color: '#F59E0B', lineWidth: 1, radius: 4 });

            // Draw auto-focus bounding box around detected hand
            this.drawFocusBox(ctx, landmarks, w, h);

            // Detect gesture with confidence accumulation
            const gesture = this.detectGesture(landmarks);
            if (gesture) {
                this.gestureBuffer.push(gesture);
                if (this.gestureBuffer.length > this.requiredConfirmations) {
                    this.gestureBuffer.shift();
                }

                // Check if all recent detections agree
                const allSame = this.gestureBuffer.length >= this.requiredConfirmations &&
                    this.gestureBuffer.every(g => g === gesture);

                if (allSame && !this.isCoolingDown && gesture !== this.lastGesture) {
                    this.lastGesture = gesture;
                    this.isCoolingDown = true;
                    this.gestureBuffer = [];

                    if (this.onGesture) {
                        this.onGesture(gesture);
                    }

                    // Cooldown period before next gesture
                    clearTimeout(this.gestureTimeout);
                    this.gestureTimeout = setTimeout(() => {
                        this.lastGesture = null;
                        this.isCoolingDown = false;
                    }, this.gestureCooldown);
                }
            } else {
                // No gesture detected - slowly clear buffer
                if (this.gestureBuffer.length > 0) {
                    this.gestureBuffer.pop();
                }
            }
        }

        ctx.restore();
    }

    drawFocusBox(ctx, landmarks, canvasW, canvasH) {
        const xs = landmarks.map(p => p.x * canvasW);
        const ys = landmarks.map(p => p.y * canvasH);
        const pad = 30;
        const x1 = Math.max(0, Math.min(...xs) - pad);
        const y1 = Math.max(0, Math.min(...ys) - pad);
        const x2 = Math.min(canvasW, Math.max(...xs) + pad);
        const y2 = Math.min(canvasH, Math.max(...ys) + pad);

        ctx.strokeStyle = '#22C55E';
        ctx.lineWidth = 2.5;
        ctx.setLineDash([8, 4]);
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        ctx.setLineDash([]);

        // Label
        ctx.fillStyle = 'rgba(34, 197, 94, 0.85)';
        ctx.fillRect(x1, y1 - 22, 80, 20);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px sans-serif';
        ctx.fillText('🖐 Focus', x1 + 4, y1 - 6);
    }

    detectGesture(landmarks) {
        const fingers = this.getFingerStates(landmarks);
        const wrist = landmarks[0];

        // Detect WAVE: open hand moving side to side
        if (fingers.thumb && fingers.index && fingers.middle && fingers.ring && fingers.pinky) {
            if (this.lastWristX !== null) {
                const dx = wrist.x - this.lastWristX;
                if (Math.abs(dx) > 0.02) {
                    this.waveHistory.push(dx > 0 ? 'R' : 'L');
                    if (this.waveHistory.length > 12) this.waveHistory.shift();

                    let changes = 0;
                    for (let i = 1; i < this.waveHistory.length; i++) {
                        if (this.waveHistory[i] !== this.waveHistory[i - 1]) changes++;
                    }
                    if (changes >= 4) {
                        this.waveHistory = [];
                        return 'wave';
                    }
                }
            }
            this.lastWristX = wrist.x;
            return 'open_palm';
        }

        // THUMBS UP: only thumb extended, pointing upward
        if (fingers.thumb && !fingers.index && !fingers.middle && !fingers.ring && !fingers.pinky) {
            if (landmarks[4].y < landmarks[3].y && landmarks[4].y < landmarks[2].y) {
                return 'thumbs_up';
            }
        }

        // POINTING: only index extended
        if (!fingers.thumb && fingers.index && !fingers.middle && !fingers.ring && !fingers.pinky) {
            return 'pointing';
        }

        // PEACE / V sign: index and middle extended
        if (!fingers.thumb && fingers.index && fingers.middle && !fingers.ring && !fingers.pinky) {
            return 'peace';
        }

        // FIST: no fingers extended
        if (!fingers.thumb && !fingers.index && !fingers.middle && !fingers.ring && !fingers.pinky) {
            return 'fist';
        }

        // OK sign: thumb and index tips close together
        const thumbTip = landmarks[4];
        const indexTip = landmarks[8];
        const distance = Math.hypot(thumbTip.x - indexTip.x, thumbTip.y - indexTip.y);
        if (distance < 0.05 && fingers.middle && fingers.ring && fingers.pinky) {
            return 'ok_sign';
        }

        return null;
    }

    getFingerStates(landmarks) {
        return {
            thumb: Math.abs(landmarks[4].x - landmarks[2].x) > 0.06 ||
                   landmarks[4].y < landmarks[3].y,
            index: landmarks[8].y < landmarks[6].y - 0.02,
            middle: landmarks[12].y < landmarks[10].y - 0.02,
            ring: landmarks[16].y < landmarks[14].y - 0.02,
            pinky: landmarks[20].y < landmarks[18].y - 0.02,
        };
    }
}

// Gesture labels for display
const GESTURE_LABELS = {
    'wave': '👋 Wave - Hello!',
    'open_palm': '✋ Open Palm',
    'thumbs_up': '👍 Thumbs Up - Yes',
    'pointing': '👆 Pointing',
    'peace': '✌️ Peace / Two',
    'fist': '✊ Fist',
    'ok_sign': '👌 OK',
};

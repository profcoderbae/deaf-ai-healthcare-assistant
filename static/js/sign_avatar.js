/**
 * Realistic Sign Language Avatar Engine v2
 * - Anatomically proportioned human figure with skin shading, detailed face
 * - 2-bone inverse-kinematics arm system: hands move to exact body coordinates
 * - Articulated 5-finger hand shapes with per-segment bending
 * - Sign poses based on real sign language positions (chin, forehead, chest, etc.)
 * - Smooth ease-in-out interpolation between poses
 * - Secondary motions (wave, nod, tap, circle, twist) for realism
 */

class SignLanguageAvatar {
    constructor(containerId, opts = {}) {
        this.container = document.getElementById(containerId);
        this.W = opts.width || 340;
        this.H = opts.height || 480;
        this.isSigning = false;
        this.uid = containerId;

        // Body reference points (viewBox 0,0,340,480)
        this.B = {
            headCx: 170, headCy: 100, headRx: 42, headRy: 52,
            shoulderY: 182,
            lShoulder: { x: 108, y: 182 },
            rShoulder: { x: 232, y: 182 },
            chin: { x: 170, y: 152 },
            forehead: { x: 170, y: 72 },
            chest: { x: 170, y: 230 },
            stomach: { x: 170, y: 300 },
            rWristRest: { x: 252, y: 340 },
            lWristRest: { x: 88, y: 340 },
        };

        // Hand interpolation state
        this._lhTarget = { ...this.B.lWristRest };
        this._rhTarget = { ...this.B.rWristRest };
        this._lhCurrent = { ...this.B.lWristRest };
        this._rhCurrent = { ...this.B.rWristRest };
        this._lHandRot = 0;
        this._rHandRot = 0;
        this._interpT = 1;
        this._animId = null;

        this.render();
        this._startAnimLoop();
    }

    // ═══════════════ RENDERING ═══════════════
    render() {
        const u = this.uid;
        this.container.innerHTML = `
        <div class="sign-avatar-wrap" id="${u}_wrap">
          <svg id="${u}_svg" viewBox="0 0 ${this.W} ${this.H}" xmlns="http://www.w3.org/2000/svg"
               style="width:100%;height:auto;display:block;user-select:none;">
            <defs>
              <radialGradient id="${u}_skinG" cx="50%" cy="40%" r="55%">
                <stop offset="0%" stop-color="#E8C4A0"/>
                <stop offset="70%" stop-color="#D4A574"/>
                <stop offset="100%" stop-color="#C49564"/>
              </radialGradient>
              <linearGradient id="${u}_scrubG" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#16A394"/>
                <stop offset="50%" stop-color="#0F8C7F"/>
                <stop offset="100%" stop-color="#0B7068"/>
              </linearGradient>
              <filter id="${u}_shadow" x="-10%" y="-10%" width="130%" height="130%">
                <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#00000020"/>
              </filter>
              <radialGradient id="${u}_hairG" cx="50%" cy="30%" r="60%">
                <stop offset="0%" stop-color="#3D2317"/>
                <stop offset="100%" stop-color="#1A0E08"/>
              </radialGradient>
              <linearGradient id="${u}_lipG" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#D4706A"/>
                <stop offset="100%" stop-color="#B85A55"/>
              </linearGradient>
            </defs>

            <!-- ── BODY ── -->
            <g id="${u}_bodyGroup">
              <path d="M108,182 Q100,184 92,200 L80,260 L78,360 Q78,380 100,380 L240,380 Q262,380 262,360 L260,260 L248,200 Q240,184 232,182 L198,174 Q170,168 142,174 Z"
                    fill="url(#${u}_scrubG)" filter="url(#${u}_shadow)"/>
              <path d="M142,176 L170,210 L198,176" fill="none" stroke="#0A6B60" stroke-width="2.5" stroke-linejoin="round"/>
              <path d="M142,176 Q148,185 155,192" fill="none" stroke="#0E8073" stroke-width="1.2"/>
              <path d="M198,176 Q192,185 185,192" fill="none" stroke="#0E8073" stroke-width="1.2"/>
              <line x1="170" y1="210" x2="170" y2="375" stroke="#0A6B60" stroke-width="0.6" opacity="0.3"/>
              <path d="M148,180 Q144,210 148,235 Q152,250 158,248 Q166,258 174,248 Q180,250 184,235 Q188,210 184,180"
                    fill="none" stroke="#5A5A6A" stroke-width="3" stroke-linecap="round"/>
              <circle cx="166" cy="254" r="7" fill="#7A7A8A" stroke="#5A5A6A" stroke-width="2"/>
              <circle cx="166" cy="254" r="3" fill="#9A9AAA"/>
              <rect x="185" y="220" width="48" height="20" rx="4" fill="white" stroke="#D0D5DD" stroke-width="1"/>
              <text x="209" y="234" text-anchor="middle" font-size="8.5" font-weight="700" fill="#0D9488" font-family="Arial,sans-serif">THANDI</text>
              <path d="M148,152 L148,178 Q148,182 154,182 L186,182 Q192,182 192,178 L192,152"
                    fill="url(#${u}_skinG)"/>
              <path d="M155,160 Q170,165 185,160" fill="none" stroke="#C49060" stroke-width="0.8" opacity="0.3"/>
              <g id="${u}_headGroup">
                <ellipse cx="170" cy="100" rx="44" ry="54" fill="url(#${u}_skinG)"/>
                <path d="M130,115 Q140,155 170,158 Q200,155 210,115" fill="none" stroke="#C49060" stroke-width="0.6" opacity="0.25"/>
                <ellipse cx="125" cy="105" rx="7" ry="12" fill="#D4A574" stroke="#C49060" stroke-width="0.8"/>
                <ellipse cx="125" cy="105" rx="4" ry="8" fill="none" stroke="#C49060" stroke-width="0.6"/>
                <ellipse cx="215" cy="105" rx="7" ry="12" fill="#D4A574" stroke="#C49060" stroke-width="0.8"/>
                <ellipse cx="215" cy="105" rx="4" ry="8" fill="none" stroke="#C49060" stroke-width="0.6"/>
                <path d="M126,95 Q126,42 170,38 Q214,42 214,95 Q214,70 200,58 Q185,48 170,47 Q155,48 140,58 Q126,70 126,95 Z"
                      fill="url(#${u}_hairG)"/>
                <path d="M132,80 Q145,52 170,48 Q195,52 208,80" fill="none" stroke="#2A1508" stroke-width="1.5" opacity="0.3"/>
                <path d="M135,90 Q150,65 170,60 Q190,65 205,90" fill="none" stroke="#2A1508" stroke-width="0.8" opacity="0.2"/>
                <circle cx="206" cy="72" r="5.5" fill="#F7B731" stroke="#E09F20" stroke-width="1"/>
                <circle cx="206" cy="72" r="2.5" fill="#FFD866"/>
                <g id="${u}_eyes">
                  <ellipse cx="152" cy="102" rx="10" ry="7.5" fill="white" stroke="#C9B090" stroke-width="0.6"/>
                  <ellipse cx="188" cy="102" rx="10" ry="7.5" fill="white" stroke="#C9B090" stroke-width="0.6"/>
                  <circle cx="152" cy="103" r="5" fill="#3D2B1F"/>
                  <circle cx="188" cy="103" r="5" fill="#3D2B1F"/>
                  <circle cx="152" cy="103" r="2.5" fill="#1A0E08"/>
                  <circle cx="188" cy="103" r="2.5" fill="#1A0E08"/>
                  <circle cx="149" cy="100" r="2" fill="white" opacity="0.85"/>
                  <circle cx="185" cy="100" r="2" fill="white" opacity="0.85"/>
                  <circle cx="154" cy="105" r="1" fill="white" opacity="0.5"/>
                  <circle cx="190" cy="105" r="1" fill="white" opacity="0.5"/>
                  <path id="${u}_lLid" d="M141,99 Q152,93 163,99" fill="none" stroke="#3D2317" stroke-width="1.8" stroke-linecap="round"/>
                  <path id="${u}_rLid" d="M177,99 Q188,93 199,99" fill="none" stroke="#3D2317" stroke-width="1.8" stroke-linecap="round"/>
                  <path d="M143,107 Q152,111 161,107" fill="none" stroke="#6B4A3A" stroke-width="0.6" opacity="0.4"/>
                  <path d="M179,107 Q188,111 197,107" fill="none" stroke="#6B4A3A" stroke-width="0.6" opacity="0.4"/>
                </g>
                <path id="${u}_lBrow" d="M139,88 Q148,82 161,87" fill="none" stroke="#2A1508" stroke-width="2.5" stroke-linecap="round"/>
                <path id="${u}_rBrow" d="M179,87 Q192,82 201,88" fill="none" stroke="#2A1508" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M168,108 Q165,120 162,127 Q166,131 170,132 Q174,131 178,127 Q175,120 172,108"
                      fill="none" stroke="#C49060" stroke-width="1.2" stroke-linecap="round"/>
                <circle cx="165" cy="128" r="1.8" fill="#C49060" opacity="0.3"/>
                <circle cx="175" cy="128" r="1.8" fill="#C49060" opacity="0.3"/>
                <g id="${u}_mouthG">
                  <path id="${u}_mouth" d="M155,143 Q162,149 170,150 Q178,149 185,143"
                        fill="url(#${u}_lipG)" stroke="#B85A55" stroke-width="0.8"/>
                  <path d="M155,143 Q162,140 170,142 Q178,140 185,143" fill="none" stroke="#C46A64" stroke-width="0.6"/>
                </g>
                <path d="M140,120 Q138,130 142,138" fill="none" stroke="#C49060" stroke-width="0.5" opacity="0.2"/>
                <path d="M200,120 Q202,130 198,138" fill="none" stroke="#C49060" stroke-width="0.5" opacity="0.2"/>
              </g>
            </g>

            <!-- ── LEFT ARM (IK) ── -->
            <g id="${u}_lArmG">
              <path id="${u}_lArm" d="" fill="none" stroke="url(#${u}_scrubG)" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
              <path id="${u}_lForearm" d="" fill="none" stroke="url(#${u}_skinG)" stroke-width="14" stroke-linecap="round"/>
              <g id="${u}_lHand" transform="translate(88,340)"></g>
            </g>

            <!-- ── RIGHT ARM (IK) ── -->
            <g id="${u}_rArmG">
              <path id="${u}_rArm" d="" fill="none" stroke="url(#${u}_scrubG)" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
              <path id="${u}_rForearm" d="" fill="none" stroke="url(#${u}_skinG)" stroke-width="14" stroke-linecap="round"/>
              <g id="${u}_rHand" transform="translate(252,340)"></g>
            </g>

            <!-- ── LABEL ── -->
            <rect id="${u}_lbBg" x="70" y="${this.H - 36}" width="200" height="28" rx="8"
                  fill="rgba(13,148,136,0.92)" style="display:none"/>
            <text id="${u}_lbTxt" x="170" y="${this.H - 16}" text-anchor="middle"
                  font-size="13" font-weight="700" fill="white" font-family="Arial,sans-serif" style="display:none"></text>
          </svg>
        </div>`;
        this._drawArms();
        this._drawHand('l', 'relax', 0);
        this._drawHand('r', 'relax', 0);
    }

    // ═══════════════ 2-BONE IK ═══════════════
    _ik(shoulder, hand, upperLen, lowerLen, flipElbow) {
        const dx = hand.x - shoulder.x;
        const dy = hand.y - shoulder.y;
        const dist = Math.hypot(dx, dy);
        const maxReach = upperLen + lowerLen - 2;
        const clampDist = Math.min(dist, maxReach);
        const a = upperLen, b = lowerLen, c = clampDist;
        let cosAngle = (a * a + c * c - b * b) / (2 * a * c);
        cosAngle = Math.max(-1, Math.min(1, cosAngle));
        const angle = Math.acos(cosAngle);
        const baseAngle = Math.atan2(dy, dx);
        const elbowAngle = flipElbow ? baseAngle - angle : baseAngle + angle;
        return {
            x: shoulder.x + Math.cos(elbowAngle) * upperLen,
            y: shoulder.y + Math.sin(elbowAngle) * upperLen
        };
    }

    _drawArms() {
        const B = this.B;
        const upperLen = 70, lowerLen = 75;
        const lElbow = this._ik(B.lShoulder, this._lhCurrent, upperLen, lowerLen, false);
        this._setPath(`${this.uid}_lArm`, `M${B.lShoulder.x},${B.lShoulder.y} Q${lElbow.x},${lElbow.y} ${lElbow.x},${lElbow.y}`);
        this._setPath(`${this.uid}_lForearm`, `M${lElbow.x},${lElbow.y} L${this._lhCurrent.x},${this._lhCurrent.y}`);
        const lh = document.getElementById(`${this.uid}_lHand`);
        if (lh) lh.setAttribute('transform', `translate(${this._lhCurrent.x},${this._lhCurrent.y}) rotate(${this._lHandRot})`);
        const rElbow = this._ik(B.rShoulder, this._rhCurrent, upperLen, lowerLen, true);
        this._setPath(`${this.uid}_rArm`, `M${B.rShoulder.x},${B.rShoulder.y} Q${rElbow.x},${rElbow.y} ${rElbow.x},${rElbow.y}`);
        this._setPath(`${this.uid}_rForearm`, `M${rElbow.x},${rElbow.y} L${this._rhCurrent.x},${this._rhCurrent.y}`);
        const rh = document.getElementById(`${this.uid}_rHand`);
        if (rh) rh.setAttribute('transform', `translate(${this._rhCurrent.x},${this._rhCurrent.y}) rotate(${this._rHandRot})`);
    }

    _setPath(id, d) { const el = document.getElementById(id); if (el) el.setAttribute('d', d); }

    // ═══════════════ ANIMATION LOOP ═══════════════
    _startAnimLoop() {
        const step = () => {
            if (this._interpT < 1) {
                this._interpT = Math.min(1, this._interpT + 0.08);
                const t = this._ease(this._interpT);
                this._lhCurrent.x = this._lhStart.x + (this._lhTarget.x - this._lhStart.x) * t;
                this._lhCurrent.y = this._lhStart.y + (this._lhTarget.y - this._lhStart.y) * t;
                this._rhCurrent.x = this._rhStart.x + (this._rhTarget.x - this._rhStart.x) * t;
                this._rhCurrent.y = this._rhStart.y + (this._rhTarget.y - this._rhStart.y) * t;
                this._drawArms();
            }
            this._animId = requestAnimationFrame(step);
        };
        this._animId = requestAnimationFrame(step);
    }

    _ease(t) { return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t; }

    _moveHandsTo(lTarget, rTarget, lRot, rRot) {
        this._lhStart = { ...this._lhCurrent };
        this._rhStart = { ...this._rhCurrent };
        this._lhTarget = lTarget ? { ...lTarget } : { ...this._lhCurrent };
        this._rhTarget = rTarget ? { ...rTarget } : { ...this._rhCurrent };
        if (lRot !== undefined && lRot !== null) this._lHandRot = lRot;
        if (rRot !== undefined && rRot !== null) this._rHandRot = rRot;
        this._interpT = 0;
    }

    // ═══════════════ HAND SHAPES ═══════════════
    _drawHand(side, shape) {
        const el = document.getElementById(`${this.uid}_${side}Hand`);
        if (!el) return;
        const sc = '#D4A574', hl = '#E8C4A0', sh = '#B8956A';
        let svg = `<ellipse cx="0" cy="0" rx="10" ry="12" fill="${sc}" stroke="${sh}" stroke-width="0.6"/>`;
        svg += `<ellipse cx="0" cy="1" rx="7" ry="9" fill="${hl}" opacity="0.25"/>`;
        svg += this._getFingerPaths(shape);
        el.innerHTML = svg;
    }

    _getFingerPaths(shape) {
        let config;
        switch(shape) {
            case 'open':
                config = [{a:-140,l:16,curl:0},{a:-100,l:18,curl:0},{a:-88,l:19,curl:0},{a:-76,l:17,curl:0},{a:-60,l:14,curl:0}]; break;
            case 'fist':
                config = [{a:-130,l:10,curl:0.9},{a:-100,l:12,curl:0.95},{a:-88,l:13,curl:0.95},{a:-76,l:12,curl:0.95},{a:-60,l:10,curl:0.95}]; break;
            case 'point':
                config = [{a:-135,l:10,curl:0.8},{a:-92,l:19,curl:0},{a:-80,l:13,curl:0.9},{a:-70,l:12,curl:0.9},{a:-58,l:10,curl:0.9}]; break;
            case 'flat':
                config = [{a:-120,l:14,curl:0.3},{a:-94,l:18,curl:0},{a:-88,l:19,curl:0},{a:-82,l:17,curl:0},{a:-76,l:14,curl:0}]; break;
            case 'thumb_up':
                config = [{a:-160,l:16,curl:0},{a:-95,l:12,curl:0.95},{a:-85,l:13,curl:0.95},{a:-75,l:12,curl:0.95},{a:-65,l:10,curl:0.95}]; break;
            case 'peace':
                config = [{a:-130,l:10,curl:0.85},{a:-100,l:18,curl:0},{a:-78,l:19,curl:0},{a:-68,l:12,curl:0.9},{a:-55,l:10,curl:0.9}]; break;
            case 'claw':
                config = [{a:-140,l:14,curl:0.45},{a:-105,l:16,curl:0.45},{a:-88,l:17,curl:0.45},{a:-72,l:15,curl:0.45},{a:-55,l:13,curl:0.45}]; break;
            case 'ok':
                config = [{a:-115,l:12,curl:0.7},{a:-105,l:12,curl:0.7},{a:-82,l:18,curl:0},{a:-72,l:16,curl:0},{a:-60,l:13,curl:0}]; break;
            case 'pinch':
                config = [{a:-110,l:13,curl:0.5},{a:-100,l:14,curl:0.5},{a:-85,l:14,curl:0.6},{a:-74,l:13,curl:0.65},{a:-62,l:11,curl:0.7}]; break;
            case 'three':
                config = [{a:-140,l:15,curl:0},{a:-100,l:18,curl:0},{a:-82,l:19,curl:0},{a:-70,l:12,curl:0.9},{a:-58,l:10,curl:0.9}]; break;
            case 'four':
                config = [{a:-135,l:10,curl:0.9},{a:-102,l:18,curl:0},{a:-90,l:19,curl:0},{a:-78,l:17,curl:0},{a:-64,l:14,curl:0}]; break;
            case 'y_hand':
                config = [{a:-145,l:16,curl:0},{a:-100,l:12,curl:0.9},{a:-88,l:13,curl:0.9},{a:-76,l:12,curl:0.9},{a:-58,l:14,curl:0}]; break;
            case 'wave':
                config = [{a:-145,l:15,curl:0},{a:-108,l:18,curl:0.05},{a:-90,l:19,curl:0.05},{a:-72,l:17,curl:0.05},{a:-55,l:14,curl:0.05}]; break;
            default: // relax
                config = [{a:-130,l:12,curl:0.5},{a:-98,l:14,curl:0.45},{a:-86,l:15,curl:0.45},{a:-74,l:14,curl:0.45},{a:-60,l:12,curl:0.5}];
        }
        return config.map((f, i) => this._drawFinger(f, i === 0)).join('');
    }

    _drawFinger(cfg, isThumb) {
        const sc = '#D4A574', jc = '#C49060';
        const rad = cfg.a * Math.PI / 180;
        const w = isThumb ? 5 : 3.5;
        const segs = isThumb ? 2 : 3;
        const segLen = cfg.l / segs;
        let pts = [{ x: 0, y: 0 }];
        let curAngle = rad;
        const curlPerSeg = cfg.curl * 0.6;
        for (let s = 0; s < segs; s++) {
            const prev = pts[pts.length - 1];
            curAngle += curlPerSeg;
            pts.push({ x: prev.x + Math.cos(curAngle) * segLen, y: prev.y + Math.sin(curAngle) * segLen });
        }
        let svg = '';
        for (let s = 0; s < pts.length - 1; s++) {
            const p1 = pts[s], p2 = pts[s + 1];
            const sw = w - s * (isThumb ? 0.8 : 0.5);
            svg += `<line x1="${p1.x.toFixed(1)}" y1="${p1.y.toFixed(1)}" x2="${p2.x.toFixed(1)}" y2="${p2.y.toFixed(1)}" stroke="${sc}" stroke-width="${sw}" stroke-linecap="round"/>`;
            if (s > 0) svg += `<circle cx="${p1.x.toFixed(1)}" cy="${p1.y.toFixed(1)}" r="${sw*0.35}" fill="${jc}" opacity="0.4"/>`;
        }
        const tip = pts[pts.length - 1];
        svg += `<circle cx="${tip.x.toFixed(1)}" cy="${tip.y.toFixed(1)}" r="${(w - segs * 0.5) * 0.45}" fill="${sc}"/>`;
        const prev = pts[pts.length - 2];
        const na = Math.atan2(tip.y - prev.y, tip.x - prev.x);
        svg += `<circle cx="${(tip.x + Math.cos(na)).toFixed(1)}" cy="${(tip.y + Math.sin(na)).toFixed(1)}" r="1.6" fill="#F0D5C0" stroke="#DBBFA8" stroke-width="0.3"/>`;
        return svg;
    }

    // ═══════════════ EXPRESSIONS ═══════════════
    _setExpression(expr) {
        const u = this.uid;
        const mouth = document.getElementById(`${u}_mouth`);
        const lB = document.getElementById(`${u}_lBrow`);
        const rB = document.getElementById(`${u}_rBrow`);
        if (!mouth) return;
        switch (expr) {
            case 'happy':
                mouth.setAttribute('d', 'M155,141 Q162,151 170,153 Q178,151 185,141');
                if (lB) lB.setAttribute('d', 'M139,86 Q148,81 161,86');
                if (rB) rB.setAttribute('d', 'M179,86 Q192,81 201,86');
                break;
            case 'concerned':
                mouth.setAttribute('d', 'M158,147 Q164,143 170,142 Q176,143 182,147');
                if (lB) lB.setAttribute('d', 'M139,84 Q148,86 161,90');
                if (rB) rB.setAttribute('d', 'M179,90 Q192,86 201,84');
                break;
            case 'thinking':
                mouth.setAttribute('d', 'M160,145 Q165,143 170,144 Q175,143 180,145');
                if (lB) lB.setAttribute('d', 'M139,85 Q148,82 161,88');
                if (rB) rB.setAttribute('d', 'M179,87 Q192,82 201,86');
                break;
            default:
                mouth.setAttribute('d', 'M155,143 Q162,149 170,150 Q178,149 185,143');
                if (lB) lB.setAttribute('d', 'M139,88 Q148,82 161,87');
                if (rB) rB.setAttribute('d', 'M179,87 Q192,82 201,88');
        }
    }

    // ═══════════════ LABEL ═══════════════
    _showLabel(text) {
        const bg = document.getElementById(`${this.uid}_lbBg`);
        const txt = document.getElementById(`${this.uid}_lbTxt`);
        if (bg) bg.style.display = 'block';
        if (txt) { txt.style.display = 'block'; txt.textContent = text; }
    }
    _hideLabel() {
        const bg = document.getElementById(`${this.uid}_lbBg`);
        const txt = document.getElementById(`${this.uid}_lbTxt`);
        if (bg) bg.style.display = 'none';
        if (txt) txt.style.display = 'none';
    }

    // ═══════════════ SIGN POSES ═══════════════
    // Each sign = hand positions relative to body, hand shapes, rotation, expression, optional secondary motion
    static SIGNS = {
        // Greetings
        'hello':   { rPos:{x:215,y:85},  lPos:null, rShape:'open',  lShape:'relax', rRot:-10, expression:'happy',    label:'Hello',    motion:'wave_away' },
        'hi':      { rPos:{x:215,y:85},  lPos:null, rShape:'open',  lShape:'relax', rRot:-10, expression:'happy',    label:'Hi',       motion:'wave_away' },
        'goodbye': { rPos:{x:230,y:100}, lPos:null, rShape:'wave',  lShape:'relax', rRot:0,   expression:'happy',    label:'Goodbye',  motion:'wave_side' },
        'welcome': { rPos:{x:230,y:200}, lPos:{x:110,y:200}, rShape:'open', lShape:'open', rRot:20, lRot:-20, expression:'happy', label:'Welcome' },
        // Yes / No
        'yes':  { rPos:{x:230,y:180}, lPos:null, rShape:'fist',  lShape:'relax', rRot:0,  expression:'happy',    label:'Yes',   motion:'nod_fist' },
        'no':   { rPos:{x:220,y:160}, lPos:null, rShape:'pinch', lShape:'relax', rRot:0,  expression:'concerned',label:'No',    motion:'pinch_close' },
        // Common
        'please': { rPos:{x:190,y:230}, lPos:null, rShape:'flat',  lShape:'relax', rRot:0,   expression:'happy',    label:'Please', motion:'circle_chest' },
        'thank':  { rPos:{x:185,y:140}, lPos:null, rShape:'flat',  lShape:'relax', rRot:-15, expression:'happy',    label:'Thank you', motion:'chin_forward' },
        'thanks': { rPos:{x:185,y:140}, lPos:null, rShape:'flat',  lShape:'relax', rRot:-15, expression:'happy',    label:'Thank you', motion:'chin_forward' },
        'sorry':  { rPos:{x:190,y:240}, lPos:null, rShape:'fist',  lShape:'relax', rRot:0,   expression:'concerned',label:'Sorry',  motion:'circle_chest' },
        'ok':     { rPos:{x:230,y:180}, lPos:null, rShape:'ok',    lShape:'relax', rRot:0,   expression:'happy',    label:'OK' },
        'good':   { rPos:{x:185,y:140}, lPos:{x:155,y:250}, rShape:'flat', lShape:'flat', rRot:-20, lRot:20, expression:'happy', label:'Good', motion:'chin_to_palm' },
        // Questions
        'what':  { rPos:{x:220,y:200}, lPos:{x:120,y:200}, rShape:'open', lShape:'open', rRot:15, lRot:-15, expression:'thinking', label:'What?' },
        'where': { rPos:{x:230,y:160}, lPos:null, rShape:'point', lShape:'relax', rRot:0,  expression:'thinking', label:'Where?', motion:'wag' },
        'when':  { rPos:{x:220,y:170}, lPos:{x:140,y:170}, rShape:'point', lShape:'point', rRot:-10, lRot:10, expression:'thinking', label:'When?' },
        'how':   { rPos:{x:230,y:200}, lPos:{x:110,y:200}, rShape:'fist', lShape:'fist', rRot:30, lRot:-30, expression:'thinking', label:'How?' },
        'why':   { rPos:{x:200,y:80},  lPos:null, rShape:'y_hand', lShape:'relax', rRot:0, expression:'thinking', label:'Why?' },
        // Pronouns
        'i':    { rPos:{x:195,y:230}, lPos:null, rShape:'point', lShape:'relax', rRot:160, expression:'neutral', label:'I / Me' },
        'me':   { rPos:{x:195,y:230}, lPos:null, rShape:'point', lShape:'relax', rRot:160, expression:'neutral', label:'Me' },
        'you':  { rPos:{x:240,y:190}, lPos:null, rShape:'point', lShape:'relax', rRot:0,   expression:'neutral', label:'You' },
        'your': { rPos:{x:240,y:190}, lPos:null, rShape:'flat',  lShape:'relax', rRot:0,   expression:'neutral', label:'Your' },
        'we':   { rPos:{x:195,y:210}, lPos:null, rShape:'point', lShape:'relax', rRot:120, expression:'happy',   label:'We', motion:'sweep_lr' },
        'this': { rPos:{x:200,y:260}, lPos:null, rShape:'point', lShape:'relax', rRot:90,  expression:'neutral', label:'This' },
        // Body parts
        'head':     { rPos:{x:195,y:80},  lPos:null, rShape:'flat',  lShape:'relax', rRot:0, expression:'neutral',  label:'Head' },
        'headache': { rPos:{x:200,y:80},  lPos:{x:140,y:80}, rShape:'claw', lShape:'claw', rRot:0, lRot:0, expression:'concerned', label:'Headache' },
        'eye':      { rPos:{x:195,y:100}, lPos:null, rShape:'point', lShape:'relax', rRot:-30, expression:'neutral', label:'Eye' },
        'ear':      { rPos:{x:215,y:100}, lPos:null, rShape:'point', lShape:'relax', rRot:0,   expression:'neutral', label:'Ear' },
        'mouth':    { rPos:{x:195,y:140}, lPos:null, rShape:'point', lShape:'relax', rRot:-20, expression:'neutral', label:'Mouth' },
        'throat':   { rPos:{x:190,y:158}, lPos:null, rShape:'claw',  lShape:'relax', rRot:0,   expression:'concerned',label:'Throat' },
        'chest':    { rPos:{x:195,y:225}, lPos:null, rShape:'flat',  lShape:'relax', rRot:0,   expression:'neutral', label:'Chest' },
        'heart':    { rPos:{x:155,y:225}, lPos:null, rShape:'fist',  lShape:'relax', rRot:0,   expression:'concerned',label:'Heart', motion:'tap' },
        'stomach':  { rPos:{x:185,y:295}, lPos:null, rShape:'flat',  lShape:'relax', rRot:0,   expression:'concerned',label:'Stomach', motion:'circle_body' },
        'back':     { rPos:{x:130,y:260}, lPos:null, rShape:'flat',  lShape:'relax', rRot:30,  expression:'concerned',label:'Back' },
        'arm':      { rPos:{x:130,y:220}, lPos:null, rShape:'flat',  lShape:'relax', rRot:0,   expression:'neutral', label:'Arm', motion:'slide' },
        'leg':      { rPos:{x:200,y:370}, lPos:null, rShape:'flat',  lShape:'relax', rRot:90,  expression:'neutral', label:'Leg' },
        'hand':     { rPos:{x:155,y:280}, lPos:{x:155,y:280}, rShape:'flat', lShape:'open', rRot:0, lRot:0, expression:'neutral', label:'Hand' },
        // Symptoms
        'pain':    { rPos:{x:210,y:220}, lPos:{x:130,y:220}, rShape:'point', lShape:'point', rRot:160, lRot:20, expression:'concerned', label:'Pain', motion:'twist' },
        'hurt':    { rPos:{x:210,y:220}, lPos:{x:130,y:220}, rShape:'point', lShape:'point', rRot:160, lRot:20, expression:'concerned', label:'Hurt', motion:'twist' },
        'sick':    { rPos:{x:195,y:85},  lPos:{x:155,y:290}, rShape:'claw', lShape:'claw', rRot:0, lRot:0, expression:'concerned', label:'Sick' },
        'fever':   { rPos:{x:195,y:75},  lPos:null, rShape:'flat',  lShape:'relax', rRot:-10, expression:'concerned',label:'Fever' },
        'dizzy':   { rPos:{x:200,y:80},  lPos:null, rShape:'claw',  lShape:'relax', rRot:0,   expression:'concerned',label:'Dizzy', motion:'circle_head' },
        'blood':   { rPos:{x:210,y:230}, lPos:{x:140,y:200}, rShape:'claw', lShape:'fist', rRot:45, lRot:0, expression:'concerned', label:'Blood' },
        'breathe': { rPos:{x:195,y:240}, lPos:{x:145,y:240}, rShape:'open', lShape:'open', rRot:0, lRot:0, expression:'concerned', label:'Breathe', motion:'breathe' },
        'cough':   { rPos:{x:185,y:155}, lPos:null, rShape:'fist',  lShape:'relax', rRot:0,   expression:'concerned',label:'Cough' },
        'vomit':   { rPos:{x:195,y:140}, lPos:null, rShape:'claw',  lShape:'relax', rRot:0,   expression:'concerned',label:'Vomit' },
        'tired':   { rPos:{x:195,y:230}, lPos:{x:145,y:230}, rShape:'open', lShape:'open', rRot:30, lRot:-30, expression:'concerned', label:'Tired' },
        'swollen': { rPos:{x:220,y:210}, lPos:{x:120,y:210}, rShape:'claw', lShape:'claw', rRot:20, lRot:-20, expression:'concerned', label:'Swollen' },
        // Treatment
        'medicine':    { rPos:{x:200,y:250}, lPos:{x:145,y:260}, rShape:'point', lShape:'flat', rRot:0, lRot:30, expression:'neutral', label:'Medicine', motion:'tap' },
        'medication':  { rPos:{x:200,y:250}, lPos:{x:145,y:260}, rShape:'point', lShape:'flat', rRot:0, lRot:30, expression:'neutral', label:'Medication', motion:'tap' },
        'doctor':      { rPos:{x:200,y:250}, lPos:{x:146,y:200}, rShape:'flat', lShape:'flat', rRot:-20, lRot:20, expression:'neutral', label:'Doctor', motion:'tap' },
        'nurse':       { rPos:{x:200,y:200}, lPos:null, rShape:'peace', lShape:'relax', rRot:-10, expression:'neutral', label:'Nurse' },
        'hospital':    { rPos:{x:215,y:185}, lPos:null, rShape:'point', lShape:'relax', rRot:-30, expression:'neutral', label:'Hospital', motion:'h_cross' },
        'help':        { rPos:{x:200,y:200}, lPos:{x:145,y:260}, rShape:'thumb_up', lShape:'flat', rRot:0, lRot:30, expression:'concerned', label:'Help' },
        'water':       { rPos:{x:195,y:140}, lPos:null, rShape:'three', lShape:'relax', rRot:0, expression:'neutral', label:'Water', motion:'tap' },
        'food':        { rPos:{x:195,y:140}, lPos:null, rShape:'pinch', lShape:'relax', rRot:0, expression:'neutral', label:'Food', motion:'tap' },
        'eat':         { rPos:{x:195,y:140}, lPos:null, rShape:'pinch', lShape:'relax', rRot:0, expression:'neutral', label:'Eat', motion:'tap' },
        'sleep':       { rPos:{x:195,y:115}, lPos:null, rShape:'open',  lShape:'relax', rRot:-20, expression:'neutral', label:'Sleep' },
        'injection':   { rPos:{x:200,y:210}, lPos:{x:130,y:215}, rShape:'fist', lShape:'flat', rRot:-30, lRot:0, expression:'concerned', label:'Injection' },
        'test':        { rPos:{x:200,y:240}, lPos:{x:145,y:250}, rShape:'point', lShape:'flat', rRot:0, lRot:30, expression:'neutral', label:'Test' },
        'xray':        { rPos:{x:220,y:230}, lPos:{x:120,y:230}, rShape:'open', lShape:'open', rRot:10, lRot:-10, expression:'neutral', label:'X-Ray' },
        'prescription':{ rPos:{x:210,y:250}, lPos:{x:140,y:260}, rShape:'point', lShape:'flat', rRot:0, lRot:25, expression:'neutral', label:'Prescription', motion:'write' },
        'appointment': { rPos:{x:210,y:240}, lPos:{x:140,y:250}, rShape:'fist', lShape:'flat', rRot:0, lRot:20, expression:'neutral', label:'Appointment', motion:'circle_palm' },
        // Verbs
        'take':  { rPos:{x:240,y:210}, lPos:null, rShape:'claw',  lShape:'relax', rRot:0,   expression:'neutral', label:'Take',  motion:'grab_in' },
        'give':  { rPos:{x:250,y:220}, lPos:null, rShape:'open',  lShape:'relax', rRot:10,  expression:'happy',   label:'Give' },
        'wait':  { rPos:{x:225,y:210}, lPos:{x:115,y:210}, rShape:'open', lShape:'open', rRot:15, lRot:-15, expression:'neutral', label:'Wait' },
        'come':  { rPos:{x:240,y:190}, lPos:null, rShape:'point', lShape:'relax', rRot:-30, expression:'happy',   label:'Come',  motion:'beckon' },
        'go':    { rPos:{x:250,y:190}, lPos:null, rShape:'point', lShape:'relax', rRot:10,  expression:'neutral', label:'Go' },
        'stop':  { rPos:{x:240,y:170}, lPos:null, rShape:'flat',  lShape:'relax', rRot:0,   expression:'concerned',label:'Stop' },
        'feel':  { rPos:{x:185,y:235}, lPos:null, rShape:'point', lShape:'relax', rRot:180, expression:'neutral', label:'Feel',  motion:'tap' },
        'need':  { rPos:{x:225,y:210}, lPos:null, rShape:'claw',  lShape:'relax', rRot:30,  expression:'concerned',label:'Need',  motion:'pull_down' },
        'want':  { rPos:{x:220,y:210}, lPos:{x:120,y:210}, rShape:'claw', lShape:'claw', rRot:20, lRot:-20, expression:'neutral', label:'Want' },
        'understand': { rPos:{x:210,y:85}, lPos:null, rShape:'point', lShape:'relax', rRot:-30, expression:'happy', label:'Understand', motion:'flick_up' },
        'know':  { rPos:{x:200,y:80},  lPos:null, rShape:'flat',  lShape:'relax', rRot:-10, expression:'neutral', label:'Know' },
        'see':   { rPos:{x:200,y:100}, lPos:null, rShape:'peace', lShape:'relax', rRot:0,   expression:'neutral', label:'See' },
        'hear':  { rPos:{x:210,y:100}, lPos:null, rShape:'claw',  lShape:'relax', rRot:0,   expression:'neutral', label:'Hear' },
        'think': { rPos:{x:200,y:85},  lPos:null, rShape:'point', lShape:'relax', rRot:-20, expression:'thinking',label:'Think' },
        'have':  { rPos:{x:195,y:230}, lPos:null, rShape:'flat',  lShape:'relax', rRot:0,   expression:'neutral', label:'Have' },
        'can':   { rPos:{x:225,y:210}, lPos:{x:115,y:210}, rShape:'fist', lShape:'fist', rRot:0, lRot:0, expression:'neutral', label:'Can' },
        'not':   { rPos:{x:200,y:150}, lPos:null, rShape:'flat',  lShape:'relax', rRot:0,   expression:'concerned',label:'Not',   motion:'chin_forward' },
        "don't": { rPos:{x:200,y:150}, lPos:null, rShape:'flat',  lShape:'relax', rRot:0,   expression:'concerned',label:"Don't", motion:'chin_forward' },
        // Time
        'today':    { rPos:{x:220,y:210}, lPos:{x:120,y:210}, rShape:'flat', lShape:'flat', rRot:15, lRot:-15, expression:'neutral', label:'Today' },
        'tomorrow': { rPos:{x:205,y:95},  lPos:null, rShape:'thumb_up', lShape:'relax', rRot:0, expression:'neutral', label:'Tomorrow' },
        'morning':  { rPos:{x:230,y:175}, lPos:{x:130,y:240}, rShape:'flat', lShape:'flat', rRot:-20, lRot:10, expression:'happy', label:'Morning' },
        'night':    { rPos:{x:220,y:200}, lPos:{x:130,y:230}, rShape:'flat', lShape:'flat', rRot:30, lRot:15, expression:'neutral', label:'Night' },
        'time':     { rPos:{x:200,y:200}, lPos:{x:146,y:200}, rShape:'point', lShape:'flat', rRot:-20, lRot:20, expression:'neutral', label:'Time', motion:'tap' },
        'day':      { rPos:{x:230,y:170}, lPos:{x:130,y:240}, rShape:'flat', lShape:'flat', rRot:-30, lRot:10, expression:'neutral', label:'Day' },
        'week':     { rPos:{x:210,y:240}, lPos:{x:140,y:250}, rShape:'point', lShape:'flat', rRot:0, lRot:25, expression:'neutral', label:'Week', motion:'slide' },
        'minute':   { rPos:{x:210,y:240}, lPos:{x:146,y:200}, rShape:'point', lShape:'flat', rRot:0, lRot:20, expression:'neutral', label:'Minute' },
        // Numbers
        'one':   { rPos:{x:230,y:175}, lPos:null, rShape:'point', lShape:'relax', rRot:0, expression:'neutral', label:'1' },
        'two':   { rPos:{x:230,y:175}, lPos:null, rShape:'peace', lShape:'relax', rRot:0, expression:'neutral', label:'2' },
        'three': { rPos:{x:230,y:175}, lPos:null, rShape:'three', lShape:'relax', rRot:0, expression:'neutral', label:'3' },
        'four':  { rPos:{x:230,y:175}, lPos:null, rShape:'four',  lShape:'relax', rRot:0, expression:'neutral', label:'4' },
        'five':  { rPos:{x:230,y:175}, lPos:null, rShape:'open',  lShape:'relax', rRot:0, expression:'neutral', label:'5' },
        // Adjectives
        'big':    { rPos:{x:245,y:195}, lPos:{x:95,y:195},  rShape:'open', lShape:'open', rRot:15, lRot:-15, expression:'neutral', label:'Big' },
        'small':  { rPos:{x:200,y:210}, lPos:{x:140,y:210}, rShape:'flat', lShape:'flat', rRot:0, lRot:0, expression:'neutral', label:'Small' },
        'hot':    { rPos:{x:200,y:140}, lPos:null, rShape:'claw', lShape:'relax', rRot:0, expression:'concerned', label:'Hot' },
        'cold':   { rPos:{x:210,y:215}, lPos:{x:130,y:215}, rShape:'fist', lShape:'fist', rRot:0, lRot:0, expression:'concerned', label:'Cold', motion:'shiver' },
        'better': { rPos:{x:195,y:140}, lPos:null, rShape:'flat', lShape:'relax', rRot:-15, expression:'happy', label:'Better' },
        'worse':  { rPos:{x:200,y:250}, lPos:null, rShape:'claw', lShape:'relax', rRot:30, expression:'concerned', label:'Worse' },
        // Special
        'allergy':     { rPos:{x:195,y:125}, lPos:null, rShape:'point', lShape:'relax', rRot:-15, expression:'concerned', label:'Allergy' },
        'allergic':    { rPos:{x:195,y:125}, lPos:null, rShape:'point', lShape:'relax', rRot:-15, expression:'concerned', label:'Allergic' },
        'temperature': { rPos:{x:195,y:75},  lPos:null, rShape:'flat',  lShape:'relax', rRot:-10, expression:'concerned', label:'Temperature' },
    };

    // Words to skip
    static SKIP = new Set(['the','a','an','is','are','am','was','were','be','to','of','in','it','for','on','with','at','that','will','and','but','or','has','had','do','does','did','been','being','by','from','up','about','into','through','during','before','after','between','out','so','very','just','also','than','then','as','its','my','our','his','her','their']);

    static PHRASES = {
        'thank you':['thank'], 'how are you':['how','you'], 'i need':['i','need'], 'i have':['i','have'],
        'take medicine':['take','medicine'], 'come back':['come','back'], 'follow up':['appointment'],
        'x-ray':['xray'], 'dont':['not'], 'cannot':['can','not'], "can't":['can','not'], "won't":['not'], "i'm":['i'], "you're":['you'],
    };

    // ═══════════════ IDLE ═══════════════
    idle() {
        this._moveHandsTo(this.B.lWristRest, this.B.rWristRest, 0, 0);
        this._drawHand('l', 'relax'); this._drawHand('r', 'relax');
        this._setExpression('neutral'); this._hideLabel();
        this.isSigning = false;
    }

    _poseSign(sign) {
        const B = this.B;
        this._moveHandsTo(sign.lPos || B.lWristRest, sign.rPos || B.rWristRest, sign.lRot || 0, sign.rRot || 0);
        this._drawHand('l', sign.lShape || 'relax');
        this._drawHand('r', sign.rShape || 'relax');
        this._setExpression(sign.expression || 'neutral');
        this._showLabel(`\u{1F91F} ${sign.label}`);
    }

    // ═══════════════ SIGN SENTENCE ═══════════════
    async signSentence(text, opts = {}) {
        if (this.isSigning) { this.isSigning = false; await this._delay(100); }
        this.isSigning = true;
        const msPerSign = opts.msPerSign || 1200;
        const onWord = opts.onWord || null;
        const onDone = opts.onDone || null;
        const tokens = this._tokenize(text);

        for (let i = 0; i < tokens.length; i++) {
            if (!this.isSigning) break;
            const token = tokens[i];
            if (onWord) onWord(token, i, tokens.length);
            const key = token.toLowerCase().replace(/[^a-z0-9'-]/g, '');
            if (SignLanguageAvatar.SKIP.has(key)) continue;
            const sign = SignLanguageAvatar.SIGNS[key];
            if (!sign) { await this._fingerspell(token); continue; }
            this._poseSign(sign);
            if (sign.motion) { await this._delay(300); await this._doMotion(sign.motion, sign); }
            await this._delay(msPerSign);
            if (i < tokens.length - 1 && this.isSigning) {
                this._moveHandsTo({x:this.B.lWristRest.x,y:this.B.lWristRest.y-20},{x:this.B.rWristRest.x,y:this.B.rWristRest.y-20},0,0);
                await this._delay(250);
            }
        }
        if (this.isSigning) this.idle();
        this.isSigning = false;
        if (onDone) onDone();
    }

    cancel() { this.isSigning = false; this.idle(); }

    // ═══════════════ SECONDARY MOTIONS ═══════════════
    async _doMotion(type, sign) {
        if (!this.isSigning) return;
        const rP = sign.rPos || this.B.rWristRest;
        const lP = sign.lPos || this.B.lWristRest;
        switch (type) {
            case 'wave_away':
                this._moveHandsTo(null,{x:rP.x+25,y:rP.y},null,-15); await this._delay(250);
                this._moveHandsTo(null,{x:rP.x,y:rP.y},null,10); await this._delay(250); break;
            case 'wave_side':
                for(let i=0;i<2&&this.isSigning;i++){
                    this._moveHandsTo(null,{x:rP.x+15,y:rP.y},null,10); await this._delay(200);
                    this._moveHandsTo(null,{x:rP.x-15,y:rP.y},null,-10); await this._delay(200);
                } break;
            case 'nod_fist':
                for(let i=0;i<2&&this.isSigning;i++){
                    this._moveHandsTo(null,{x:rP.x,y:rP.y-12}); await this._delay(180);
                    this._moveHandsTo(null,{x:rP.x,y:rP.y+8}); await this._delay(180);
                } break;
            case 'pinch_close':
                this._drawHand('r','pinch'); await this._delay(200);
                this._drawHand('r','fist'); await this._delay(200);
                this._drawHand('r','pinch'); await this._delay(200); break;
            case 'chin_forward':
                this._moveHandsTo(null,{x:rP.x+20,y:rP.y+15}); await this._delay(350); break;
            case 'circle_chest':
                for(let a=0;a<360&&this.isSigning;a+=45){
                    const r=a*Math.PI/180;
                    this._moveHandsTo(null,{x:rP.x+Math.cos(r)*15,y:rP.y+Math.sin(r)*15}); await this._delay(80);
                } break;
            case 'tap':
                this._moveHandsTo(lP,{x:rP.x,y:rP.y-8}); await this._delay(180);
                this._moveHandsTo(lP,rP); await this._delay(180);
                this._moveHandsTo(lP,{x:rP.x,y:rP.y-8}); await this._delay(180); break;
            case 'twist':
                this._moveHandsTo({x:lP.x-5,y:lP.y-10},{x:rP.x+5,y:rP.y+10}); await this._delay(250);
                this._moveHandsTo({x:lP.x+5,y:lP.y+10},{x:rP.x-5,y:rP.y-10}); await this._delay(250); break;
            case 'circle_head':
                for(let a=0;a<360&&this.isSigning;a+=60){
                    const r=a*Math.PI/180;
                    this._moveHandsTo(null,{x:rP.x+Math.cos(r)*18,y:rP.y+Math.sin(r)*12}); await this._delay(100);
                } break;
            case 'circle_body':
                for(let a=0;a<360&&this.isSigning;a+=60){
                    const r=a*Math.PI/180;
                    this._moveHandsTo(null,{x:rP.x+Math.cos(r)*12,y:rP.y+Math.sin(r)*12}); await this._delay(80);
                } break;
            case 'breathe':
                this._moveHandsTo({x:lP.x+10,y:lP.y+15},{x:rP.x-10,y:rP.y+15}); await this._delay(400);
                this._moveHandsTo(lP,rP); await this._delay(400); break;
            case 'slide':
                this._moveHandsTo(null,{x:rP.x-25,y:rP.y}); await this._delay(300); break;
            case 'write':
                for(let i=0;i<3&&this.isSigning;i++){
                    this._moveHandsTo(null,{x:rP.x+12,y:rP.y+8}); await this._delay(150);
                    this._moveHandsTo(null,{x:rP.x-8,y:rP.y+16}); await this._delay(150);
                } break;
            case 'wag':
                for(let i=0;i<2&&this.isSigning;i++){
                    this._moveHandsTo(null,{x:rP.x+12,y:rP.y}); await this._delay(180);
                    this._moveHandsTo(null,{x:rP.x-12,y:rP.y}); await this._delay(180);
                } break;
            case 'beckon':
                this._drawHand('r','point'); await this._delay(200);
                this._drawHand('r','fist'); await this._delay(200);
                this._drawHand('r','point'); await this._delay(200); break;
            case 'flick_up':
                this._moveHandsTo(null,{x:rP.x,y:rP.y-25});
                this._drawHand('r','open'); await this._delay(300); break;
            case 'grab_in':
                this._drawHand('r','open'); await this._delay(200);
                this._moveHandsTo(null,{x:rP.x-20,y:rP.y});
                this._drawHand('r','fist'); await this._delay(300); break;
            case 'pull_down':
                this._moveHandsTo(null,{x:rP.x,y:rP.y+30}); await this._delay(350); break;
            case 'shiver':
                for(let i=0;i<3&&this.isSigning;i++){
                    this._moveHandsTo({x:lP.x+4,y:lP.y},{x:rP.x-4,y:rP.y}); await this._delay(120);
                    this._moveHandsTo({x:lP.x-4,y:lP.y},{x:rP.x+4,y:rP.y}); await this._delay(120);
                } break;
            case 'sweep_lr':
                this._moveHandsTo(null,{x:this.B.chest.x-30,y:rP.y}); await this._delay(200);
                this._moveHandsTo(null,{x:this.B.chest.x+60,y:rP.y}); await this._delay(300); break;
            case 'chin_to_palm':
                this._moveHandsTo(null,{x:rP.x,y:rP.y+80}); await this._delay(400); break;
            case 'h_cross':
                this._moveHandsTo(null,{x:rP.x,y:rP.y-15}); await this._delay(200);
                this._moveHandsTo(null,{x:rP.x+15,y:rP.y}); await this._delay(200); break;
            case 'circle_palm':
                for(let a=0;a<360&&this.isSigning;a+=60){
                    const r=a*Math.PI/180;
                    this._moveHandsTo(null,{x:rP.x+Math.cos(r)*10,y:rP.y+Math.sin(r)*10}); await this._delay(80);
                } break;
        }
    }

    // ═══════════════ FINGERSPELLING ═══════════════
    async _fingerspell(word) {
        const shapes = ['point','flat','fist','open','peace','claw','thumb_up','ok','three','y_hand'];
        for (let i = 0; i < word.length && this.isSigning; i++) {
            const ch = word[i].toUpperCase();
            const si = ch.charCodeAt(0) % shapes.length;
            this._moveHandsTo(null, {x:230, y:165 + ((i%3)-1)*12});
            this._drawHand('r', shapes[si]);
            this._showLabel(`\u270B ${ch}  (${word})`);
            await this._delay(420);
        }
    }

    // ═══════════════ TOKENIZER ═══════════════
    _tokenize(text) {
        let lower = text.toLowerCase().replace(/[^\w\s'-]/g, '').trim();
        const words = lower.split(/\s+/);
        const tokens = [];
        let i = 0;
        while (i < words.length) {
            let matched = false;
            for (let len = 3; len >= 2; len--) {
                if (i + len <= words.length) {
                    const phrase = words.slice(i, i + len).join(' ');
                    const mapped = SignLanguageAvatar.PHRASES[phrase];
                    if (mapped) { tokens.push(...(Array.isArray(mapped) ? mapped : [mapped])); i += len; matched = true; break; }
                }
            }
            if (!matched) { tokens.push(words[i]); i++; }
        }
        return tokens;
    }

    _delay(ms) { return new Promise(r => setTimeout(r, ms)); }
}

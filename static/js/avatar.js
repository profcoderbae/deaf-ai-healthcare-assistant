/**
 * Healthcare Avatar - "Thandi"
 * SVG-based animated avatar for healthcare communication
 */

class HealthcareAvatar {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.state = 'idle';  // idle, wave, signing, talking
        this.render();
    }

    render() {
        this.container.innerHTML = `
        <div class="avatar-wrapper avatar-idle" id="avatarAnimState">
            <svg viewBox="0 0 240 320" xmlns="http://www.w3.org/2000/svg" id="avatarSvg">
                <!-- Background glow -->
                <defs>
                    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" style="stop-color:#0D9488;stop-opacity:0.15"/>
                        <stop offset="100%" style="stop-color:#0D9488;stop-opacity:0"/>
                    </radialGradient>
                    <linearGradient id="scrubsGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style="stop-color:#14B8A6"/>
                        <stop offset="100%" style="stop-color:#0F766E"/>
                    </linearGradient>
                </defs>

                <!-- Glow circle -->
                <circle cx="120" cy="160" r="110" fill="url(#glow)"/>

                <!-- Body / Scrubs -->
                <path class="avatar-scrubs" d="M75,180 Q75,160 95,155 L120,150 L145,155 Q165,160 165,180 L170,280 Q170,295 155,295 L85,295 Q70,295 70,280 Z" fill="url(#scrubsGrad)"/>

                <!-- Scrubs V-neck -->
                <path d="M105,155 L120,175 L135,155" fill="none" stroke="#0B8074" stroke-width="2"/>

                <!-- Stethoscope -->
                <path class="avatar-stethoscope" d="M108,160 Q105,185 110,195 Q115,205 120,200 Q125,205 130,195 Q135,185 132,160"/>
                <circle cx="120" cy="202" r="6" fill="#6B7280" stroke="#4B5563" stroke-width="1.5"/>

                <!-- Name badge -->
                <rect x="100" y="210" width="40" height="18" rx="3" fill="white" stroke="#E2E8F0" stroke-width="1"/>
                <text x="120" y="223" text-anchor="middle" font-size="8" font-weight="600" fill="#0D9488">THANDI</text>

                <!-- Left Arm -->
                <g class="avatar-arm avatar-arm-left">
                    <path d="M75,160 Q55,175 50,210 Q48,225 55,230" fill="none" stroke="url(#scrubsGrad)" stroke-width="18" stroke-linecap="round"/>
                    <circle cx="55" cy="232" r="10" fill="#D4A574"/>
                </g>

                <!-- Right Arm -->
                <g class="avatar-arm avatar-arm-right">
                    <path d="M165,160 Q185,175 190,210 Q192,225 185,230" fill="none" stroke="url(#scrubsGrad)" stroke-width="18" stroke-linecap="round"/>
                    <circle cx="185" cy="232" r="10" fill="#D4A574"/>
                </g>

                <!-- Neck -->
                <rect x="110" y="130" width="20" height="25" rx="5" fill="#D4A574"/>

                <!-- Head -->
                <ellipse cx="120" cy="100" rx="42" ry="48" fill="#D4A574"/>

                <!-- Hair -->
                <path class="avatar-hair" d="M78,90 Q78,45 120,42 Q162,45 162,90 Q162,70 150,62 Q140,55 120,54 Q100,55 90,62 Q78,70 78,90 Z"/>
                <!-- Hair decoration -->
                <circle cx="152" cy="72" r="5" fill="#F59E0B"/>

                <!-- Eyes -->
                <g class="avatar-eyes">
                    <ellipse cx="105" cy="98" rx="5" ry="6"/>
                    <ellipse cx="135" cy="98" rx="5" ry="6"/>
                    <!-- Eye shine -->
                    <circle cx="103" cy="96" r="2" fill="white"/>
                    <circle cx="133" cy="96" r="2" fill="white"/>
                </g>

                <!-- Eyebrows -->
                <path d="M95,87 Q105,83 112,87" fill="none" stroke="#2C1810" stroke-width="2" stroke-linecap="round"/>
                <path d="M128,87 Q135,83 145,87" fill="none" stroke="#2C1810" stroke-width="2" stroke-linecap="round"/>

                <!-- Nose -->
                <path d="M118,105 Q120,112 122,105" fill="none" stroke="#B8956A" stroke-width="1.5"/>

                <!-- Mouth -->
                <ellipse class="avatar-mouth" cx="120" cy="120" rx="10" ry="4" fill="#E07070"/>

                <!-- Smile lines -->
                <path d="M108,118 Q120,128 132,118" fill="none" stroke="#C0846A" stroke-width="1" opacity="0.5"/>
            </svg>
        </div>`;
    }

    setState(newState) {
        const wrapper = document.getElementById('avatarAnimState');
        if (!wrapper) return;

        wrapper.className = 'avatar-wrapper';
        this.state = newState;

        switch(newState) {
            case 'idle':
                wrapper.classList.add('avatar-idle');
                break;
            case 'wave':
                wrapper.classList.add('avatar-wave');
                break;
            case 'signing':
                wrapper.classList.add('avatar-signing');
                break;
            case 'talking':
                wrapper.classList.add('avatar-signing', 'avatar-talking');
                break;
        }
    }

    // Set expression
    setExpression(expression) {
        const mouth = document.querySelector('.avatar-mouth');
        if (!mouth) return;

        switch(expression) {
            case 'happy':
                mouth.setAttribute('ry', '5');
                mouth.setAttribute('fill', '#E07070');
                break;
            case 'concerned':
                mouth.setAttribute('ry', '2');
                mouth.setAttribute('fill', '#C08080');
                break;
            case 'neutral':
                mouth.setAttribute('ry', '3');
                mouth.setAttribute('fill', '#D09090');
                break;
        }
    }

    // Animate signing with a callback when done
    async animateSigning(durationMs = 3000) {
        this.setState('signing');
        this.setExpression('happy');
        return new Promise(resolve => {
            setTimeout(() => {
                this.setState('idle');
                this.setExpression('neutral');
                resolve();
            }, durationMs);
        });
    }

    // Wave animation
    async animateWave(durationMs = 2000) {
        this.setState('wave');
        this.setExpression('happy');
        return new Promise(resolve => {
            setTimeout(() => {
                this.setState('idle');
                resolve();
            }, durationMs);
        });
    }
}

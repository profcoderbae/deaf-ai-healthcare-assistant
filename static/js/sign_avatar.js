/**
 * Emoji Sign Language Translator v6
 * ──────────────────────────────────
 * Enhanced with features from Hearing & Speech Hackathon project.
 *
 * Improvements over v5:
 *  - Proper ASL fingerspelling alphabet with correct hand-shape emojis
 *  - Per-sign duration (fast: 500ms, normal: 800ms, slow: 1200ms)
 *  - Pause between fingerspelled words for visual clarity
 *  - Sign type badge (WORD SIGN vs FINGERSPELLING vs PAUSE)
 *  - Replay & Stop controls
 *  - 180+ word→emoji mappings (medical + general)
 *  - Animated hand character above emoji
 *  - Progress counter "Sign 3 of 8"
 */

class SignLanguageAvatar {
    constructor(containerId, opts = {}) {
        this.container = document.getElementById(containerId);
        this.isSigning = false;
        this.uid = containerId;
        this._lastText = '';
        this._lastOpts = {};
        this._timeoutId = null;
        this.render();
    }

    /* ═══════════════════════════════════════════════════════════════
       RENDER — Emoji display panel with controls
       ═══════════════════════════════════════════════════════════════ */
    render() {
        const u = this.uid;
        this.container.innerHTML = `
        <div id="${u}_panel" style="
            background: linear-gradient(135deg, #F0FDFA 0%, #E0F7FA 50%, #E8F5E9 100%);
            border-radius: 20px;
            border: 3px solid #B2DFDB;
            padding: 24px 16px;
            text-align: center;
            min-height: 380px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        ">
            <!-- Idle state -->
            <div id="${u}_idle" style="display:flex;flex-direction:column;align-items:center;gap:12px;">
                <div style="font-size:80px;line-height:1;filter:drop-shadow(0 4px 12px rgba(0,0,0,0.15));">🤟</div>
                <div style="font-size:18px;font-weight:700;color:#0D9488;">Thandi — Sign Language Translator</div>
                <div style="font-size:14px;color:#64748B;">Doctor's words will appear here as emoji signs</div>
            </div>

            <!-- Active signing display -->
            <div id="${u}_active" style="display:none;flex-direction:column;align-items:center;gap:4px;width:100%;">
                <!-- Sign type badge -->
                <div id="${u}_badge" style="
                    display: inline-block;
                    padding: 3px 12px;
                    border-radius: 20px;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                    margin-bottom: 4px;
                    background: #DBEAFE;
                    color: #1E40AF;
                ">WORD SIGN</div>

                <!-- Big emoji -->
                <div id="${u}_emoji" style="
                    font-size: 120px;
                    line-height: 1;
                    filter: drop-shadow(0 6px 20px rgba(0,0,0,0.2));
                    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s ease;
                    transform: scale(1);
                    min-height: 140px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">🤟</div>

                <!-- Current word label -->
                <div id="${u}_word" style="
                    font-size: 36px;
                    font-weight: 800;
                    color: #0F766E;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    margin-top: 4px;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.08);
                "></div>

                <!-- Description of the sign -->
                <div id="${u}_desc" style="
                    font-size: 14px;
                    color: #64748B;
                    font-style: italic;
                    margin-top: 2px;
                    min-height: 20px;
                    max-width: 300px;
                "></div>

                <!-- Progress counter -->
                <div id="${u}_counter" style="
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    width: 100%;
                    margin-top: 8px;
                    padding: 0 4px;
                ">
                    <span id="${u}_countText" style="font-size:12px;color:#94A3B8;font-weight:600;"></span>
                    <span id="${u}_typeText" style="font-size:12px;color:#94A3B8;"></span>
                </div>

                <!-- Progress bar -->
                <div style="width:100%;height:6px;background:#E2E8F0;border-radius:3px;overflow:hidden;">
                    <div id="${u}_progbar" style="height:100%;width:0%;background:linear-gradient(90deg,#3B82F6,#0D9488);border-radius:3px;transition:width 0.3s ease;"></div>
                </div>

                <!-- Word strip (sentence progress) -->
                <div id="${u}_strip" style="
                    display: flex;
                    flex-wrap: wrap;
                    gap: 6px;
                    justify-content: center;
                    margin-top: 10px;
                    padding: 10px;
                    background: rgba(255,255,255,0.75);
                    border-radius: 12px;
                    width: 100%;
                    max-height: 80px;
                    overflow-y: auto;
                    border: 1px solid #E2E8F0;
                "></div>

                <!-- Replay/Stop controls -->
                <div id="${u}_controls" style="display:flex;gap:8px;margin-top:10px;">
                    <button id="${u}_stopBtn" onclick="window._signAvatar_${u}.cancel()" style="
                        padding: 6px 16px;
                        background: #FEE2E2;
                        color: #DC2626;
                        border: none;
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 600;
                        cursor: pointer;
                    ">⏹ Stop</button>
                </div>
            </div>

            <!-- Done state -->
            <div id="${u}_done" style="display:none;flex-direction:column;align-items:center;gap:10px;">
                <div style="font-size:72px;line-height:1;">✅</div>
                <div style="font-size:20px;font-weight:700;color:#059669;">Message Signed!</div>
                <div id="${u}_fullmsg" style="font-size:15px;color:#475569;max-width:300px;word-wrap:break-word;line-height:1.5;"></div>
                <!-- Replay button -->
                <button id="${u}_replayBtn" onclick="window._signAvatar_${u}.replay()" style="
                    padding: 8px 20px;
                    background: #DBEAFE;
                    color: #1E40AF;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    margin-top: 4px;
                    transition: background 0.2s;
                ">🔄 Replay</button>
            </div>
        </div>`;

        // Register on window for button onclick access
        window[`_signAvatar_${u}`] = this;
    }

    /* ═══════════════════════════════════════════════════════════════
       ASL FINGERSPELLING ALPHABET (from Hackathon reference)
       Correct hand-shape emojis + descriptions per letter
       ═══════════════════════════════════════════════════════════════ */
    static ASL_ALPHA = {
        'A': { emoji: '✊',  desc: 'Fist with thumb to the side' },
        'B': { emoji: '🖐', desc: 'Flat hand, fingers together, thumb tucked' },
        'C': { emoji: '🤏', desc: 'Curved hand like holding a cup' },
        'D': { emoji: '☝️',  desc: 'Index finger up, others touch thumb' },
        'E': { emoji: '✊',  desc: 'Fingers curled, thumb tucked under' },
        'F': { emoji: '👌', desc: 'Thumb and index touch, others up' },
        'G': { emoji: '👈', desc: 'Index and thumb pointing sideways' },
        'H': { emoji: '🤞', desc: 'Index and middle finger sideways' },
        'I': { emoji: '🤙', desc: 'Pinky up, others closed' },
        'J': { emoji: '🤙', desc: 'Pinky up with J motion downward' },
        'K': { emoji: '✌️',  desc: 'Index and middle up, thumb between' },
        'L': { emoji: '🤟', desc: 'L shape — index up, thumb out' },
        'M': { emoji: '✊',  desc: 'Thumb under three fingers' },
        'N': { emoji: '✊',  desc: 'Thumb under two fingers' },
        'O': { emoji: '👌', desc: 'All fingers touch thumb in O shape' },
        'P': { emoji: '👇', desc: 'Like K but pointing down' },
        'Q': { emoji: '👇', desc: 'Like G but pointing down' },
        'R': { emoji: '🤞', desc: 'Crossed index and middle fingers' },
        'S': { emoji: '✊',  desc: 'Fist with thumb over fingers' },
        'T': { emoji: '✊',  desc: 'Thumb between index and middle' },
        'U': { emoji: '✌️',  desc: 'Index and middle together, up' },
        'V': { emoji: '✌️',  desc: 'Index and middle spread apart' },
        'W': { emoji: '🤟', desc: 'Three middle fingers up' },
        'X': { emoji: '☝️',  desc: 'Index finger hooked' },
        'Y': { emoji: '🤙', desc: 'Thumb and pinky out — Y shape' },
        'Z': { emoji: '☝️',  desc: 'Index finger draws Z in air' },
    };

    /* ═══════════════════════════════════════════════════════════════
       EMOJI SIGN DICTIONARY — 180+ words with per-sign durations
       duration: ms to show each sign (default 800)
       ═══════════════════════════════════════════════════════════════ */
    static SIGNS = {
        // Greetings
        'hello':    { emoji: '👋', label: 'Hello', desc: 'Wave hand near forehead', duration: 1200 },
        'hi':       { emoji: '👋', label: 'Hi', desc: 'Wave hand', duration: 800 },
        'goodbye':  { emoji: '👋', label: 'Goodbye', desc: 'Open-close hand wave', duration: 1200 },
        'bye':      { emoji: '👋', label: 'Bye', desc: 'Wave goodbye', duration: 800 },
        'welcome':  { emoji: '🤗', label: 'Welcome', desc: 'Open arms welcome', duration: 1000 },
        'yes':      { emoji: '👍', label: 'Yes', desc: 'Fist nods up and down', duration: 800 },
        'no':       { emoji: '✊', label: 'No', desc: 'Index and middle finger snap to thumb', duration: 800 },
        'please':   { emoji: '🙏', label: 'Please', desc: 'Flat hand circles on chest', duration: 1000 },
        'thank':    { emoji: '🙏', label: 'Thank You', desc: 'Flat hand from chin forward', duration: 1000 },
        'thanks':   { emoji: '🙏', label: 'Thank You', desc: 'Flat hand from chin forward', duration: 800 },
        'sorry':    { emoji: '😔', label: 'Sorry', desc: 'Fist circles on chest', duration: 1000 },
        'ok':       { emoji: '👌', label: 'OK', desc: 'OK hand sign', duration: 600 },
        'good':     { emoji: '👍', label: 'Good', desc: 'Flat hand from chin outward', duration: 800 },

        // Questions
        'what':     { emoji: '🤷', label: 'What?', desc: 'Palms up, shake side to side', duration: 800 },
        'where':    { emoji: '👉❓', label: 'Where?', desc: 'Index finger waves side to side', duration: 800 },
        'when':     { emoji: '⏰❓', label: 'When?', desc: 'Index circles then touches other index', duration: 1000 },
        'how':      { emoji: '🤔', label: 'How?', desc: 'Knuckles together, roll forward, palms up', duration: 1000 },
        'why':      { emoji: '🤨❓', label: 'Why?', desc: 'Touch forehead, pull away into Y shape', duration: 1000 },
        'which':    { emoji: '👆↔️', label: 'Which?', desc: 'Alternating hands — choose', duration: 800 },
        'who':      { emoji: '🫵❓', label: 'Who?', desc: 'Point and circle — person', duration: 800 },

        // Pronouns
        'i':     { emoji: '👈', label: 'I / Me', desc: 'Point to self (chest)', duration: 500 },
        'me':    { emoji: '👈', label: 'Me', desc: 'Point to self', duration: 600 },
        'you':   { emoji: '👉', label: 'You', desc: 'Point index finger forward', duration: 600 },
        'your':  { emoji: '👉', label: 'Your', desc: 'Flat hand pushes forward', duration: 600 },
        'we':    { emoji: '👥', label: 'We', desc: 'Point between self and others', duration: 800 },
        'they':  { emoji: '👥', label: 'They', desc: 'Point side to side', duration: 800 },
        'he':    { emoji: '👉', label: 'He', desc: 'Point to side', duration: 500 },
        'she':   { emoji: '👉', label: 'She', desc: 'Point to side', duration: 500 },
        'this':  { emoji: '👇', label: 'This', desc: 'Point down — here', duration: 600 },

        // Body parts
        'head':     { emoji: '🧠', label: 'Head', desc: 'Touch side of head', duration: 800 },
        'headache': { emoji: '🤕', label: 'Headache', desc: 'Claw hands squeeze at temples', duration: 1000 },
        'eye':      { emoji: '👁️', label: 'Eye', desc: 'Point to eye', duration: 600 },
        'eyes':     { emoji: '👁️', label: 'Eyes', desc: 'Point to both eyes', duration: 600 },
        'ear':      { emoji: '👂', label: 'Ear', desc: 'Point to ear', duration: 600 },
        'mouth':    { emoji: '👄', label: 'Mouth', desc: 'Point to mouth', duration: 600 },
        'throat':   { emoji: '🫁', label: 'Throat', desc: 'Claw hand at throat', duration: 800 },
        'neck':     { emoji: '🤚', label: 'Neck', desc: 'Hand circles neck area', duration: 800 },
        'chest':    { emoji: '🫁', label: 'Chest', desc: 'Flat hand on chest', duration: 800 },
        'heart':    { emoji: '❤️', label: 'Heart', desc: 'Middle finger taps over heart', duration: 1000 },
        'lung':     { emoji: '🫁', label: 'Lung', desc: 'Hands on ribcage', duration: 800 },
        'lungs':    { emoji: '🫁', label: 'Lungs', desc: 'Hands expand on ribcage', duration: 800 },
        'stomach':  { emoji: '🤢', label: 'Stomach', desc: 'Flat hand circles belly', duration: 800 },
        'belly':    { emoji: '🤢', label: 'Belly', desc: 'Hand on belly', duration: 800 },
        'back':     { emoji: '🔙', label: 'Back', desc: 'Hand reaches behind to back', duration: 800 },
        'spine':    { emoji: '🔙', label: 'Spine', desc: 'Trace down back', duration: 800 },
        'arm':      { emoji: '💪', label: 'Arm', desc: 'Slide hand along arm', duration: 800 },
        'leg':      { emoji: '🦵', label: 'Leg', desc: 'Flat hand on thigh', duration: 800 },
        'knee':     { emoji: '🦵', label: 'Knee', desc: 'Point to knee', duration: 600 },
        'hand':     { emoji: '✋', label: 'Hand', desc: 'Show open hand', duration: 600 },
        'finger':   { emoji: '☝️', label: 'Finger', desc: 'Point to finger', duration: 600 },
        'foot':     { emoji: '🦶', label: 'Foot', desc: 'Point to foot', duration: 600 },
        'skin':     { emoji: '🤚', label: 'Skin', desc: 'Pinch and pull forearm skin', duration: 800 },
        'bone':     { emoji: '🦴', label: 'Bone', desc: 'Cross-arm tap on bone', duration: 800 },
        'teeth':    { emoji: '🦷', label: 'Teeth', desc: 'Point to teeth', duration: 600 },
        'tooth':    { emoji: '🦷', label: 'Tooth', desc: 'Point to tooth', duration: 600 },
        'nose':     { emoji: '👃', label: 'Nose', desc: 'Point to nose', duration: 600 },
        'tongue':   { emoji: '👅', label: 'Tongue', desc: 'Point to tongue', duration: 600 },
        'brain':    { emoji: '🧠', label: 'Brain', desc: 'Tap side of head', duration: 800 },
        'shoulder': { emoji: '💪', label: 'Shoulder', desc: 'Touch shoulder', duration: 600 },
        'hip':      { emoji: '🦵', label: 'Hip', desc: 'Touch hip area', duration: 600 },
        'wrist':    { emoji: '⌚', label: 'Wrist', desc: 'Touch wrist', duration: 600 },
        'elbow':    { emoji: '💪', label: 'Elbow', desc: 'Touch elbow', duration: 600 },
        'muscle':   { emoji: '💪', label: 'Muscle', desc: 'Flex arm — muscle', duration: 800 },

        // Symptoms & conditions
        'pain':     { emoji: '😣', label: 'Pain', desc: 'Index fingers twist toward each other', duration: 1000 },
        'hurt':     { emoji: '😣', label: 'Hurt', desc: 'Index fingers twist — hurting', duration: 1000 },
        'hurts':    { emoji: '😣', label: 'Hurts', desc: 'Index fingers twist — hurting', duration: 1000 },
        'ache':     { emoji: '😣', label: 'Ache', desc: 'Pressing motion — deep ache', duration: 1000 },
        'sick':     { emoji: '🤒', label: 'Sick', desc: 'Middle fingers on head & stomach', duration: 1000 },
        'ill':      { emoji: '🤒', label: 'Ill', desc: 'Middle fingers on head & stomach', duration: 1000 },
        'fever':    { emoji: '🌡️', label: 'Fever', desc: 'Hand on forehead — temperature', duration: 1000 },
        'dizzy':    { emoji: '😵‍💫', label: 'Dizzy', desc: 'Claw circles near head', duration: 1000 },
        'blood':    { emoji: '🩸', label: 'Blood', desc: 'Claw drips from fist — blood flow', duration: 1000 },
        'breathe':  { emoji: '😮‍💨', label: 'Breathe', desc: 'Hands rise and fall from chest', duration: 1200 },
        'breathing':{ emoji: '😮‍💨', label: 'Breathing', desc: 'Hands rise and fall from chest', duration: 1200 },
        'cough':    { emoji: '🤧', label: 'Cough', desc: 'Fist pounds at chest', duration: 800 },
        'vomit':    { emoji: '🤮', label: 'Vomit', desc: 'Claw from mouth outward', duration: 1000 },
        'nausea':   { emoji: '🤢', label: 'Nausea', desc: 'Hand circles stomach — queasy', duration: 1000 },
        'tired':    { emoji: '😩', label: 'Tired', desc: 'Hands drop on chest — exhausted', duration: 1000 },
        'exhausted':{ emoji: '😩', label: 'Exhausted', desc: 'Both hands drop — very tired', duration: 1000 },
        'swollen':  { emoji: '🎈', label: 'Swollen', desc: 'Claws expand outward — swelling', duration: 1000 },
        'swelling': { emoji: '🎈', label: 'Swelling', desc: 'Hands expand — swelling up', duration: 1000 },
        'rash':     { emoji: '🔴', label: 'Rash', desc: 'Tap dots on skin — red spots', duration: 800 },
        'itch':     { emoji: '🤏', label: 'Itch', desc: 'Scratch motion on arm', duration: 800 },
        'itchy':    { emoji: '🤏', label: 'Itchy', desc: 'Scratch motion on skin', duration: 800 },
        'burn':     { emoji: '🔥', label: 'Burn', desc: 'Wiggle fingers upward — flame', duration: 800 },
        'bleeding': { emoji: '🩸', label: 'Bleeding', desc: 'Blood dripping motion from hand', duration: 1000 },
        'infection':{ emoji: '🦠', label: 'Infection', desc: 'Spread fingers outward — germs spread', duration: 1000 },
        'infected': { emoji: '🦠', label: 'Infected', desc: 'Spread from point — infection', duration: 1000 },
        'broken':   { emoji: '💔', label: 'Broken', desc: 'Snap hands apart — break', duration: 1000 },
        'fracture': { emoji: '💔', label: 'Fracture', desc: 'Break motion — snap', duration: 1000 },
        'pregnant': { emoji: '🤰', label: 'Pregnant', desc: 'Hand arcs outward from belly', duration: 1200 },
        'diabetes': { emoji: '💉', label: 'Diabetes', desc: 'Inject into finger — blood sugar', duration: 1000 },
        'pressure': { emoji: '🫀', label: 'Pressure', desc: 'Squeeze arm — blood pressure', duration: 1000 },
        'allergy':  { emoji: '🤧', label: 'Allergy', desc: 'Point nose + flick away', duration: 1000 },
        'allergic': { emoji: '🤧', label: 'Allergic', desc: 'Point nose + flick away', duration: 1000 },
        'temperature':{ emoji: '🌡️', label: 'Temperature', desc: 'Hand slides on forehead', duration: 1000 },
        'stress':   { emoji: '😰', label: 'Stress', desc: 'Claws grip at temples', duration: 1000 },
        'anxiety':  { emoji: '😰', label: 'Anxiety', desc: 'Hands shake at chest', duration: 1000 },
        'depression':{ emoji: '😞', label: 'Depression', desc: 'Middle fingers slide down chest', duration: 1200 },
        'sleep':    { emoji: '😴', label: 'Sleep', desc: 'Hand closes sliding down cheek', duration: 1000 },
        'insomnia': { emoji: '😳', label: 'Insomnia', desc: 'Eyes wide open — cannot sleep', duration: 1000 },
        'numb':     { emoji: '🤚', label: 'Numb', desc: 'Hand goes limp — no feeling', duration: 800 },
        'stiff':    { emoji: '🤜', label: 'Stiff', desc: 'Fists rigid — cannot bend', duration: 800 },
        'cramp':    { emoji: '✊', label: 'Cramp', desc: 'Fist clenches tight — cramp', duration: 800 },
        'sore':     { emoji: '😣', label: 'Sore', desc: 'Touch tender area — soreness', duration: 800 },
        'weak':     { emoji: '😫', label: 'Weak', desc: 'Fingers collapse on palm', duration: 800 },
        'faint':    { emoji: '😵', label: 'Faint', desc: 'Hand drops — passing out', duration: 1000 },
        'unconscious':{ emoji: '😵', label: 'Unconscious', desc: 'Person down — not awake', duration: 1200 },
        'conscious': { emoji: '😃', label: 'Conscious', desc: 'Eyes open — awake', duration: 800 },
        'awake':    { emoji: '😃', label: 'Awake', desc: 'Eyes spring open', duration: 800 },
        'constipation':{ emoji: '😣', label: 'Constipation', desc: 'Fist blocked — stuck', duration: 1000 },
        'diarrhea': { emoji: '🚽', label: 'Diarrhea', desc: 'Liquid motion downward', duration: 1000 },
        'asthma':   { emoji: '😮‍💨', label: 'Asthma', desc: 'Difficulty breathing sign', duration: 1200 },
        'seizure':  { emoji: '⚡', label: 'Seizure', desc: 'Body shakes — seizure', duration: 1000 },
        'stroke':   { emoji: '🧠⚡', label: 'Stroke', desc: 'Brain + lightning — stroke', duration: 1200 },
        'cancer':   { emoji: '🎗️', label: 'Cancer', desc: 'Spread sign — cancer', duration: 1200 },
        'hiv':      { emoji: '🔬', label: 'HIV', desc: 'Blood test sign', duration: 1000 },
        'tb':       { emoji: '🫁', label: 'TB', desc: 'Cough + lungs', duration: 1000 },
        'covid':    { emoji: '😷', label: 'COVID', desc: 'Mask + cough sign', duration: 1000 },
        'malaria':  { emoji: '🦟', label: 'Malaria', desc: 'Mosquito + fever', duration: 1000 },
        'wound':    { emoji: '🩹', label: 'Wound', desc: 'Cut on skin — injury', duration: 800 },
        'cut':      { emoji: '🩹', label: 'Cut', desc: 'Slice on skin', duration: 800 },

        // Medical procedures & items
        'medicine':    { emoji: '💊', label: 'Medicine', desc: 'Middle finger taps palm — pills', duration: 1000 },
        'medication':  { emoji: '💊', label: 'Medication', desc: 'Middle finger taps palm — pills', duration: 1000 },
        'pill':        { emoji: '💊', label: 'Pill', desc: 'Pinch and flick to mouth — swallow pill', duration: 800 },
        'pills':       { emoji: '💊', label: 'Pills', desc: 'Pinch and flick to mouth — pills', duration: 800 },
        'tablet':      { emoji: '💊', label: 'Tablet', desc: 'Finger taps palm', duration: 800 },
        'capsule':     { emoji: '💊', label: 'Capsule', desc: 'Small pill sign', duration: 800 },
        'syrup':       { emoji: '🥤', label: 'Syrup', desc: 'Pour and drink motion', duration: 1000 },
        'cream':       { emoji: '🧴', label: 'Cream', desc: 'Rub on skin motion', duration: 800 },
        'ointment':    { emoji: '🧴', label: 'Ointment', desc: 'Rub on skin', duration: 800 },
        'drops':       { emoji: '💧', label: 'Drops', desc: 'Pinch drops into eye or ear', duration: 800 },
        'antibiotic':  { emoji: '💊🦠', label: 'Antibiotic', desc: 'Medicine that fights germs', duration: 1200 },
        'painkiller':  { emoji: '💊😌', label: 'Painkiller', desc: 'Medicine that stops pain', duration: 1200 },
        'doctor':      { emoji: '🩺', label: 'Doctor', desc: 'D-hand taps wrist pulse point', duration: 1000 },
        'nurse':       { emoji: '👩‍⚕️', label: 'Nurse', desc: 'N-fingertips tap inside wrist', duration: 1000 },
        'hospital':    { emoji: '🏥', label: 'Hospital', desc: 'Draw H-cross on upper arm', duration: 1000 },
        'clinic':      { emoji: '🏥', label: 'Clinic', desc: 'Draw cross — medical place', duration: 1000 },
        'pharmacy':    { emoji: '💊🏪', label: 'Pharmacy', desc: 'Medicine shop sign', duration: 1000 },
        'help':        { emoji: '🆘', label: 'Help', desc: 'Thumbs-up on flat palm, lift together', duration: 1000 },
        'emergency':   { emoji: '🚨', label: 'Emergency', desc: 'E-hand shakes rapidly', duration: 1000 },
        'ambulance':   { emoji: '🚑', label: 'Ambulance', desc: 'Cross + driving motion', duration: 1000 },
        'injection':   { emoji: '💉', label: 'Injection', desc: 'Push needle into upper arm', duration: 1000 },
        'inject':      { emoji: '💉', label: 'Inject', desc: 'Needle motion into arm', duration: 1000 },
        'vaccine':     { emoji: '💉', label: 'Vaccine', desc: 'Inject into upper arm', duration: 1000 },
        'test':        { emoji: '🧪', label: 'Test', desc: 'Index finger taps palm — examine', duration: 800 },
        'xray':        { emoji: '☢️', label: 'X-Ray', desc: 'Hands frame body — see through', duration: 1000 },
        'scan':        { emoji: '🔬', label: 'Scan', desc: 'Hand sweeps over body', duration: 1000 },
        'ultrasound':  { emoji: '🔊', label: 'Ultrasound', desc: 'Wand presses on belly', duration: 1000 },
        'surgery':     { emoji: '🔪', label: 'Surgery', desc: 'Draw cut line on body', duration: 1000 },
        'operation':   { emoji: '🔪', label: 'Operation', desc: 'Draw cut sign on body', duration: 1000 },
        'prescription':{ emoji: '📝', label: 'Prescription', desc: 'Write on palm — Rx order', duration: 1000 },
        'appointment': { emoji: '📅', label: 'Appointment', desc: 'Fist circles on palm — date set', duration: 1000 },
        'bandage':     { emoji: '🩹', label: 'Bandage', desc: 'Wrap around arm', duration: 800 },
        'oxygen':      { emoji: '😷', label: 'Oxygen', desc: 'Mask over face — breathing aid', duration: 1000 },
        'wheelchair':  { emoji: '♿', label: 'Wheelchair', desc: 'Wheel motion at sides', duration: 1000 },
        'stethoscope': { emoji: '🩺', label: 'Stethoscope', desc: 'Place on chest — listen', duration: 1000 },
        'drip':        { emoji: '💧', label: 'Drip', desc: 'IV drip motion — fluid', duration: 800 },
        'iv':          { emoji: '💉💧', label: 'IV', desc: 'Needle with drip — intravenous', duration: 1000 },
        'plaster':     { emoji: '🩹', label: 'Plaster', desc: 'Stick on wound', duration: 800 },
        'stitches':    { emoji: '🪡', label: 'Stitches', desc: 'Sew motion on skin', duration: 1000 },
        'cast':        { emoji: '🦴🩹', label: 'Cast', desc: 'Wrap rigid around limb', duration: 1000 },
        'crutches':    { emoji: '🩼', label: 'Crutches', desc: 'Walking support motion', duration: 1000 },
        'thermometer': { emoji: '🌡️', label: 'Thermometer', desc: 'Check temperature — under tongue', duration: 1000 },
        'mask':        { emoji: '😷', label: 'Mask', desc: 'Cover face with mask', duration: 800 },
        'gloves':      { emoji: '🧤', label: 'Gloves', desc: 'Pull gloves onto hands', duration: 800 },

        // Actions
        'take':  { emoji: '🤲', label: 'Take', desc: 'Claw hand grabs inward', duration: 800 },
        'give':  { emoji: '🫴', label: 'Give', desc: 'Open hand pushes outward', duration: 800 },
        'wait':  { emoji: '✋', label: 'Wait', desc: 'Open palms hold — pause', duration: 800 },
        'come':  { emoji: '🫳', label: 'Come', desc: 'Index fingers beckon toward self', duration: 800 },
        'go':    { emoji: '👉', label: 'Go', desc: 'Both index fingers point and arc forward', duration: 800 },
        'stop':  { emoji: '🛑', label: 'Stop', desc: 'Flat hand strikes other palm — halt', duration: 800 },
        'sit':   { emoji: '🪑', label: 'Sit', desc: 'Two fingers hook on other two — sit down', duration: 800 },
        'stand': { emoji: '🧍', label: 'Stand', desc: 'Two fingers stand on palm — stand up', duration: 800 },
        'walk':  { emoji: '🚶', label: 'Walk', desc: 'Two fingers walk on palm', duration: 800 },
        'lie':   { emoji: '🛏️', label: 'Lie Down', desc: 'Hand lies flat on palm', duration: 800 },
        'open':  { emoji: '📖', label: 'Open', desc: 'Palms apart — open', duration: 800 },
        'close': { emoji: '📕', label: 'Close', desc: 'Palms together — close', duration: 800 },
        'eat':   { emoji: '🍽️', label: 'Eat', desc: 'Bunched fingers tap mouth repeatedly', duration: 800 },
        'drink': { emoji: '🥤', label: 'Drink', desc: 'C-hand tips to mouth', duration: 800 },
        'swallow':{ emoji: '🤲👇', label: 'Swallow', desc: 'Hand traces down throat', duration: 800 },
        'feel':  { emoji: '🤚', label: 'Feel', desc: 'Middle finger taps chest — emotion', duration: 800 },
        'need':  { emoji: '🫵', label: 'Need', desc: 'X-handshape bends downward — require', duration: 800 },
        'want':  { emoji: '🤲', label: 'Want', desc: 'Clawed hands pull toward body', duration: 800 },
        'understand': { emoji: '💡', label: 'Understand', desc: 'Index finger flicks up near forehead', duration: 1000 },
        'know':  { emoji: '🧠', label: 'Know', desc: 'Flat hand taps forehead — knowledge', duration: 800 },
        'see':   { emoji: '👀', label: 'See', desc: 'V-hand from eyes forward', duration: 600 },
        'look':  { emoji: '👀', label: 'Look', desc: 'V-hand from eyes forward', duration: 600 },
        'hear':  { emoji: '👂', label: 'Hear', desc: 'Cup hand at ear', duration: 600 },
        'listen':{ emoji: '👂', label: 'Listen', desc: 'Cup hand at ear — pay attention', duration: 800 },
        'think': { emoji: '🤔', label: 'Think', desc: 'Point at forehead — thinking', duration: 800 },
        'remember':{ emoji: '💭', label: 'Remember', desc: 'Thumb from forehead pushes forward', duration: 1000 },
        'forget':  { emoji: '🤦', label: 'Forget', desc: 'Hand wipes across forehead', duration: 1000 },
        'tell':  { emoji: '🗣️', label: 'Tell', desc: 'Index from chin arcs forward', duration: 800 },
        'say':   { emoji: '🗣️', label: 'Say', desc: 'Index circles near mouth', duration: 800 },
        'speak': { emoji: '🗣️', label: 'Speak', desc: 'Four fingers tap from chin outward', duration: 800 },
        'read':  { emoji: '📖', label: 'Read', desc: 'V-hand scans across flat palm', duration: 800 },
        'write': { emoji: '✍️', label: 'Write', desc: 'Pinched hand writes on flat palm', duration: 800 },
        'show':  { emoji: '👐', label: 'Show', desc: 'Flat hand presents forward', duration: 800 },
        'have':  { emoji: '🤲', label: 'Have', desc: 'Hands pull to chest — possess', duration: 800 },
        'can':   { emoji: '💪', label: 'Can', desc: 'Both fists move down together — able', duration: 800 },
        'not':   { emoji: '🚫', label: 'Not', desc: 'Thumb from under chin forward — negative', duration: 800 },
        "don't": { emoji: '🚫', label: "Don't", desc: 'Hands cross outward — negative', duration: 800 },
        'try':   { emoji: '🤞', label: 'Try', desc: 'Fists push forward — attempt', duration: 800 },
        'check': { emoji: '🔍', label: 'Check', desc: 'V-hand inspects palm', duration: 800 },
        'examine':{ emoji: '🔍', label: 'Examine', desc: 'Look carefully at body', duration: 1000 },
        'measure':{ emoji: '📏', label: 'Measure', desc: 'Hands measure distance apart', duration: 800 },
        'clean': { emoji: '🧼', label: 'Clean', desc: 'Palm wipes other palm — clean', duration: 800 },
        'wash':  { emoji: '🧼', label: 'Wash', desc: 'Rub hands together — washing', duration: 800 },
        'rest':  { emoji: '😌', label: 'Rest', desc: 'Crossed arms on chest — rest', duration: 1000 },
        'relax': { emoji: '😌', label: 'Relax', desc: 'Hands float down gently', duration: 1000 },
        'exercise':{ emoji: '🏃', label: 'Exercise', desc: 'Arms pump up and down', duration: 1000 },
        'move':  { emoji: '🔄', label: 'Move', desc: 'Hands shift position', duration: 800 },
        'touch': { emoji: '👆', label: 'Touch', desc: 'Middle finger presses down', duration: 600 },
        'press': { emoji: '👇', label: 'Press', desc: 'Push down firmly', duration: 600 },
        'remove':{ emoji: '🗑️', label: 'Remove', desc: 'Pull away — remove', duration: 800 },
        'apply': { emoji: '🤚', label: 'Apply', desc: 'Rub onto surface — apply', duration: 800 },
        'put':   { emoji: '🫳', label: 'Put', desc: 'Place down gently', duration: 600 },

        // Emotions
        'happy': { emoji: '😊', label: 'Happy', desc: 'Flat hand brushes up on chest repeatedly', duration: 1000 },
        'sad':   { emoji: '😢', label: 'Sad', desc: 'Open hands slide down face', duration: 1000 },
        'angry': { emoji: '😠', label: 'Angry', desc: 'Claw hands pull from face — anger', duration: 1000 },
        'scared':{ emoji: '😨', label: 'Scared', desc: 'Fists open toward body — fear', duration: 1000 },
        'worried':{ emoji: '😟', label: 'Worried', desc: 'Hands alternate circles at forehead', duration: 1000 },
        'confused':{ emoji: '😕', label: 'Confused', desc: 'Curved hands circle — confusion', duration: 1000 },
        'calm':  { emoji: '😌', label: 'Calm', desc: 'Hands slowly lower — calm down', duration: 1000 },
        'comfortable':{ emoji: '😊', label: 'Comfortable', desc: 'Palms stroke down — at ease', duration: 1000 },
        'uncomfortable':{ emoji: '😣', label: 'Uncomfortable', desc: 'Hands twist — not at ease', duration: 1000 },

        // Food & drink
        'water':  { emoji: '💧', label: 'Water', desc: 'W-handshape taps chin — water', duration: 800 },
        'food':   { emoji: '🍽️', label: 'Food', desc: 'Bunched fingers tap mouth — eat', duration: 800 },
        'milk':   { emoji: '🥛', label: 'Milk', desc: 'Squeeze fist — milking motion', duration: 800 },
        'juice':  { emoji: '🧃', label: 'Juice', desc: 'J-hand near chin', duration: 800 },
        'tea':    { emoji: '☕', label: 'Tea', desc: 'Stir cup motion', duration: 800 },
        'coffee': { emoji: '☕', label: 'Coffee', desc: 'Grind fists — coffee', duration: 800 },
        'fruit':  { emoji: '🍎', label: 'Fruit', desc: 'F-hand on cheek twists', duration: 800 },
        'bread':  { emoji: '🍞', label: 'Bread', desc: 'Slice across back of hand', duration: 800 },
        'soup':   { emoji: '🥣', label: 'Soup', desc: 'Spoon scoops to mouth', duration: 800 },
        'sugar':  { emoji: '🍬', label: 'Sugar', desc: 'Fingers stroke down chin — sweet', duration: 800 },
        'salt':   { emoji: '🧂', label: 'Salt', desc: 'Sprinkle fingers — salt', duration: 800 },

        // Time
        'today':    { emoji: '📅', label: 'Today', desc: 'Both Y-hands drop — now/today', duration: 800 },
        'tomorrow': { emoji: '📅➡️', label: 'Tomorrow', desc: 'Thumb forward from cheek', duration: 1000 },
        'yesterday':{ emoji: '📅⬅️', label: 'Yesterday', desc: 'Thumb back at cheek', duration: 1000 },
        'morning':  { emoji: '🌅', label: 'Morning', desc: 'Arm rises from forearm — sunrise', duration: 1000 },
        'afternoon':{ emoji: '☀️', label: 'Afternoon', desc: 'Arm descends at angle — midday', duration: 1000 },
        'evening':  { emoji: '🌇', label: 'Evening', desc: 'Hand descends on forearm — sunset', duration: 1000 },
        'night':    { emoji: '🌙', label: 'Night', desc: 'Wrist bends down on forearm — dark', duration: 800 },
        'time':     { emoji: '⏰', label: 'Time', desc: 'Index taps back of wrist — clock', duration: 800 },
        'day':      { emoji: '☀️', label: 'Day', desc: 'Elbow on hand, arm arcs overhead', duration: 800 },
        'week':     { emoji: '📆', label: 'Week', desc: 'Index slides across flat palm', duration: 800 },
        'month':    { emoji: '🗓️', label: 'Month', desc: 'Index slides down other index', duration: 800 },
        'year':     { emoji: '🔄', label: 'Year', desc: 'Fists orbit each other — year', duration: 1000 },
        'minute':   { emoji: '⏱️', label: 'Minute', desc: 'Index ticks forward on palm', duration: 800 },
        'hour':     { emoji: '🕐', label: 'Hour', desc: 'Index circles on palm — hour', duration: 800 },
        'now':      { emoji: '👇', label: 'Now', desc: 'Both Y-hands drop — right now', duration: 600 },
        'later':    { emoji: '👉⏰', label: 'Later', desc: 'L-hand tilts forward — future', duration: 800 },
        'soon':     { emoji: '⏳', label: 'Soon', desc: 'Short time ahead', duration: 800 },
        'always':   { emoji: '♾️', label: 'Always', desc: 'Index circles continuously', duration: 1000 },
        'never':    { emoji: '🚫⏰', label: 'Never', desc: 'Hand swoops down — not ever', duration: 1000 },
        'sometimes':{ emoji: '🔄❓', label: 'Sometimes', desc: 'Occasional — on and off', duration: 1000 },
        'often':    { emoji: '🔄', label: 'Often', desc: 'Repeated bent-hand motion', duration: 800 },
        'daily':    { emoji: '☀️📅', label: 'Daily', desc: 'Every day — thumb slides on cheek', duration: 1000 },
        'twice':    { emoji: '✌️', label: 'Twice', desc: 'Two bounces on palm — two times', duration: 800 },

        // Numbers
        'one':   { emoji: '☝️', label: '1', desc: 'One finger up', duration: 600 },
        'two':   { emoji: '✌️', label: '2', desc: 'Two fingers up', duration: 600 },
        'three': { emoji: '🤟', label: '3', desc: 'Three fingers up', duration: 600 },
        'four':  { emoji: '🖖', label: '4', desc: 'Four fingers up', duration: 600 },
        'five':  { emoji: '🖐️', label: '5', desc: 'Open hand — five', duration: 600 },
        'six':   { emoji: '🤙', label: '6', desc: 'Thumb + pinky extended', duration: 600 },
        'seven': { emoji: '7️⃣', label: '7', desc: 'Seven', duration: 600 },
        'eight': { emoji: '8️⃣', label: '8', desc: 'Eight', duration: 600 },
        'nine':  { emoji: '9️⃣', label: '9', desc: 'Nine', duration: 600 },
        'ten':   { emoji: '🔟', label: '10', desc: 'Ten', duration: 600 },
        'once':  { emoji: '☝️', label: 'Once', desc: 'One time', duration: 600 },

        // Descriptors
        'big':    { emoji: '👐', label: 'Big', desc: 'Hands spread wide apart — large', duration: 800 },
        'small':  { emoji: '🤏', label: 'Small', desc: 'Palms close together — little', duration: 800 },
        'hot':    { emoji: '🥵', label: 'Hot', desc: 'Claw turns outward from mouth', duration: 800 },
        'cold':   { emoji: '🥶', label: 'Cold', desc: 'Fists shiver close to body', duration: 800 },
        'warm':   { emoji: '🌡️☀️', label: 'Warm', desc: 'Gentle heat — hand opens from chin', duration: 800 },
        'better': { emoji: '👍✨', label: 'Better', desc: 'Open hand rises from chin — improved', duration: 800 },
        'worse':  { emoji: '👎', label: 'Worse', desc: 'Claw drops downward — decline', duration: 800 },
        'more':   { emoji: '➕', label: 'More', desc: 'Bunched fingertips tap together', duration: 800 },
        'less':   { emoji: '➖', label: 'Less', desc: 'Hands close together — less', duration: 800 },
        'many':   { emoji: '🖐️🖐️', label: 'Many', desc: 'Fingers flick open — lots', duration: 800 },
        'few':    { emoji: '🤏', label: 'Few', desc: 'Thumb counts across fingers — some', duration: 800 },
        'new':    { emoji: '✨', label: 'New', desc: 'Back of hand scoops on palm', duration: 800 },
        'old':    { emoji: '👴', label: 'Old', desc: 'Fist drops from chin — beard', duration: 800 },
        'same':   { emoji: '🤝', label: 'Same', desc: 'Index fingers tap together', duration: 800 },
        'different':{ emoji: '↔️', label: 'Different', desc: 'Index fingers cross and pull apart', duration: 800 },
        'important':{ emoji: '❗', label: 'Important', desc: 'Both F-hands rise to center', duration: 1000 },
        'normal': { emoji: '👌', label: 'Normal', desc: 'Flat hands level — normal', duration: 800 },
        'strong': { emoji: '💪', label: 'Strong', desc: 'Flex bicep — strong', duration: 800 },
        'safe':   { emoji: '🛡️', label: 'Safe', desc: 'Crossed fists break apart — safe', duration: 800 },
        'dangerous':{ emoji: '⚠️', label: 'Dangerous', desc: 'Fist rises on other fist — danger', duration: 1000 },
        'left':   { emoji: '⬅️', label: 'Left', desc: 'L-hand moves left', duration: 600 },
        'right':  { emoji: '➡️', label: 'Right', desc: 'R-hand moves right', duration: 600 },
        'slow':   { emoji: '🐢', label: 'Slow', desc: 'Hand glides slowly up other hand', duration: 800 },
        'fast':   { emoji: '⚡', label: 'Fast', desc: 'L-hands flick — quick', duration: 800 },
        'deep':   { emoji: '👇⬇️', label: 'Deep', desc: 'Hand pushes deep down', duration: 800 },
        'sharp':  { emoji: '📌', label: 'Sharp', desc: 'Sharp point motion — stabbing', duration: 800 },
        'dull':   { emoji: '😑', label: 'Dull', desc: 'Flat aching feeling', duration: 800 },
        'chronic':{ emoji: '🔄😣', label: 'Chronic', desc: 'Ongoing — long-lasting pain', duration: 1200 },
        'severe': { emoji: '😣❗', label: 'Severe', desc: 'Intense — very bad', duration: 1000 },
        'mild':   { emoji: '🤏', label: 'Mild', desc: 'Small amount — gentle', duration: 800 },
        'moderate':{ emoji: '➖', label: 'Moderate', desc: 'Medium level — in between', duration: 800 },

        // People & places
        'family':  { emoji: '👨‍👩‍👧‍👦', label: 'Family', desc: 'F-hands circle out from body', duration: 1000 },
        'mother':  { emoji: '👩', label: 'Mother', desc: 'Thumb taps chin — mother', duration: 800 },
        'father':  { emoji: '👨', label: 'Father', desc: 'Thumb taps forehead — father', duration: 800 },
        'child':   { emoji: '👶', label: 'Child', desc: 'Lower hand pats — small person', duration: 800 },
        'baby':    { emoji: '👶', label: 'Baby', desc: 'Rock arms — baby in arms', duration: 1000 },
        'home':    { emoji: '🏠', label: 'Home', desc: 'Bunched fingers touch cheek then jaw', duration: 1000 },
        'bathroom':{ emoji: '🚻', label: 'Bathroom', desc: 'T-hand shakes side to side', duration: 800 },
        'person':  { emoji: '🧑', label: 'Person', desc: 'Draw body outline with P-hands', duration: 800 },
        'man':     { emoji: '👨', label: 'Man', desc: 'Open hand from forehead — male', duration: 800 },
        'woman':   { emoji: '👩', label: 'Woman', desc: 'Open hand from chin — female', duration: 800 },

        // Misc
        'phone':   { emoji: '📱', label: 'Phone', desc: 'Y-hand held at ear', duration: 800 },
        'money':   { emoji: '💰', label: 'Money', desc: 'Back of hand taps palm — money', duration: 800 },
        'question':{ emoji: '❓', label: 'Question', desc: 'Draw question mark in air', duration: 800 },
        'answer':  { emoji: '💬', label: 'Answer', desc: 'Index fingers from mouth outward', duration: 800 },
        'name':    { emoji: '🏷️', label: 'Name', desc: 'H-fingers tap — name', duration: 1000 },
        'sign':    { emoji: '🤟', label: 'Sign', desc: 'Index fingers alternate circles — sign language', duration: 1000 },
        'language':{ emoji: '🤟', label: 'Language', desc: 'L-hands pull apart — language', duration: 1000 },
        'again':   { emoji: '🔄', label: 'Again', desc: 'Curved hand arcs into flat palm — repeat', duration: 800 },
        'maybe':   { emoji: '🤷', label: 'Maybe', desc: 'Flat palms alternate up and down', duration: 800 },
        'ready':   { emoji: '👊', label: 'Ready', desc: 'R-hands move outward — prepared', duration: 800 },
        'finish':  { emoji: '👏', label: 'Finish', desc: 'Hands flip outward — all done', duration: 800 },
        'start':   { emoji: '▶️', label: 'Start', desc: 'Index finger twists in V-hand — begin', duration: 800 },
        'done':    { emoji: '✅', label: 'Done', desc: 'Hands flip outward — complete', duration: 800 },
        'here':    { emoji: '📍', label: 'Here', desc: 'Flat palms circle — this place', duration: 600 },
        'there':   { emoji: '👉📍', label: 'There', desc: 'Point away — that place', duration: 800 },
        'positive':{ emoji: '➕', label: 'Positive', desc: 'Plus sign — positive result', duration: 800 },
        'negative':{ emoji: '➖', label: 'Negative', desc: 'Minus sign — negative result', duration: 800 },
        'true':    { emoji: '✅', label: 'True', desc: 'Index from mouth forward — honest', duration: 800 },
        'correct': { emoji: '✅', label: 'Correct', desc: 'Index taps index — right', duration: 800 },
        'wrong':   { emoji: '❌', label: 'Wrong', desc: 'Y-hand on chin — mistake', duration: 800 },
        'careful': { emoji: '⚠️', label: 'Careful', desc: 'K-hands tap — be cautious', duration: 800 },
        'follow':  { emoji: '👉', label: 'Follow', desc: 'A-hands follow — come after', duration: 800 },
        'return':  { emoji: '🔙', label: 'Return', desc: 'Hand arcs back — come back', duration: 800 },
        'continue':{ emoji: '➡️', label: 'Continue', desc: 'Palms push forward — keep going', duration: 800 },
        'every':   { emoji: '🔄', label: 'Every', desc: 'Thumb slides down knuckles', duration: 800 },
        'each':    { emoji: '🔄', label: 'Each', desc: 'Thumb counts across fingers', duration: 800 },
        'bad':     { emoji: '👎', label: 'Bad', desc: 'Flat hand from chin turns down', duration: 800 },
        'friend':  { emoji: '🤝', label: 'Friend', desc: 'Hook index fingers and flip', duration: 1000 },
        'love':    { emoji: '🤗', label: 'Love', desc: 'Cross arms over chest — love', duration: 1000 },
        'work':    { emoji: '👊', label: 'Work', desc: 'Fist taps other wrist — work', duration: 1000 },
    };

    static SKIP = new Set(['the','a','an','is','are','am','was','were','be','to','of','in','it','for','on','with','at','that','will','and','but','or','has','had','do','does','did','been','being','by','from','up','about','into','through','during','before','after','between','out','so','very','just','also','than','then','as','its','my','our','his','her','their']);

    static PHRASES = {
        'thank you':['thank'], 'how are you':['how','you'], 'i need':['i','need'], 'i have':['i','have'],
        'take medicine':['take','medicine'], 'come back':['come','back'], 'follow up':['appointment'],
        'x-ray':['xray'], 'dont':['not'], 'cannot':['can','not'], "can't":['can','not'], "won't":['not'],
        "i'm":['i'], "you're":['you'], 'blood pressure':['pressure'], 'sit down':['sit'],
        'lie down':['lie'], 'stand up':['stand'], 'blood test':['blood','test'],
        'side effect':['medicine','dangerous'], "don't understand":['not','understand'],
        'i love you':['love'], 'thank you very much':['thank'],
    };

    /* ═══════════════════════════════════════════════════════════════
       SIGNING — Word by word with per-sign durations
       ═══════════════════════════════════════════════════════════════ */
    idle() {
        const u = this.uid;
        if (this._timeoutId) { clearTimeout(this._timeoutId); this._timeoutId = null; }
        document.getElementById(`${u}_idle`).style.display = 'flex';
        document.getElementById(`${u}_active`).style.display = 'none';
        document.getElementById(`${u}_done`).style.display = 'none';
        this.isSigning = false;
    }

    replay() {
        if (this._lastText) {
            this.signSentence(this._lastText, this._lastOpts);
        }
    }

    async signSentence(text, opts = {}) {
        if (this.isSigning) { this.isSigning = false; await this._delay(150); }
        this.isSigning = true;
        this._lastText = text;
        this._lastOpts = opts;
        const u = this.uid;
        const onWord = opts.onWord || null;
        const onDone = opts.onDone || null;

        const tokens = this._tokenize(text);

        // Show active state
        document.getElementById(`${u}_idle`).style.display = 'none';
        document.getElementById(`${u}_done`).style.display = 'none';
        document.getElementById(`${u}_active`).style.display = 'flex';

        // Build the word strip
        const strip = document.getElementById(`${u}_strip`);
        strip.innerHTML = tokens.map((t, i) => {
            const key = t.toLowerCase().replace(/[^a-z0-9'-]/g, '');
            const isSkip = SignLanguageAvatar.SKIP.has(key);
            return `<span id="${u}_sw_${i}" style="
                padding: 4px 10px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                background: ${isSkip ? '#F1F5F9' : '#E2E8F0'};
                color: ${isSkip ? '#94A3B8' : '#475569'};
                transition: all 0.3s ease;
                ${isSkip ? 'text-decoration: line-through;' : ''}
            ">${this._escHtml(t)}</span>`;
        }).join('');

        const emojiEl = document.getElementById(`${u}_emoji`);
        const wordEl  = document.getElementById(`${u}_word`);
        const descEl  = document.getElementById(`${u}_desc`);
        const badgeEl = document.getElementById(`${u}_badge`);
        const countText = document.getElementById(`${u}_countText`);
        const typeText  = document.getElementById(`${u}_typeText`);
        const progBar   = document.getElementById(`${u}_progbar`);

        // Count signable tokens
        let signCount = 0;
        let signTotal = tokens.filter(t => !SignLanguageAvatar.SKIP.has(t.toLowerCase().replace(/[^a-z0-9'-]/g, ''))).length;

        // Sign each token word by word
        for (let i = 0; i < tokens.length; i++) {
            if (!this.isSigning) break;
            const token = tokens[i];
            if (onWord) onWord(token, i, tokens.length);
            const key = token.toLowerCase().replace(/[^a-z0-9'-]/g, '');

            // Highlight current word in strip
            const sw = document.getElementById(`${u}_sw_${i}`);
            if (sw) {
                sw.style.background = '#0D9488';
                sw.style.color = 'white';
                sw.style.transform = 'scale(1.15)';
                sw.style.boxShadow = '0 2px 8px rgba(13,148,136,0.4)';
            }

            if (SignLanguageAvatar.SKIP.has(key)) {
                await this._delay(200);
                if (sw) { sw.style.background = '#CBD5E1'; sw.style.color = '#64748B'; sw.style.transform = 'scale(1)'; sw.style.boxShadow = 'none'; }
                continue;
            }

            signCount++;
            // Update progress
            const pct = ((signCount) / signTotal * 100).toFixed(0);
            progBar.style.width = pct + '%';
            countText.textContent = `Sign ${signCount} of ${signTotal}`;

            const sign = SignLanguageAvatar.SIGNS[key];
            if (sign) {
                // WORD SIGN
                badgeEl.textContent = 'WORD SIGN';
                badgeEl.style.background = '#DBEAFE';
                badgeEl.style.color = '#1E40AF';
                typeText.textContent = 'Word Sign';

                // Bounce animation
                emojiEl.style.transform = 'scale(0.3)';
                emojiEl.style.opacity = '0.3';
                await this._delay(150);
                emojiEl.textContent = sign.emoji;
                wordEl.textContent = sign.label;
                descEl.textContent = sign.desc;
                emojiEl.style.transform = 'scale(1.15)';
                emojiEl.style.opacity = '1';
                await this._delay(200);
                emojiEl.style.transform = 'scale(1)';
                await this._delay((sign.duration || 800) - 350);
            } else {
                // FINGERSPELLING
                badgeEl.textContent = 'FINGERSPELLING';
                badgeEl.style.background = '#FEF3C7';
                badgeEl.style.color = '#92400E';
                typeText.textContent = 'Fingerspelling';

                await this._fingerspell(token, emojiEl, wordEl, descEl);

                // Pause between fingerspelled words for visual clarity
                emojiEl.style.transform = 'scale(0.8)';
                emojiEl.style.opacity = '0.5';
                await this._delay(400);
                emojiEl.style.opacity = '1';
                emojiEl.style.transform = 'scale(1)';
            }

            // Mark word as completed in strip
            if (sw) {
                sw.style.background = '#CCFBF1';
                sw.style.color = '#0D9488';
                sw.style.transform = 'scale(1)';
                sw.style.boxShadow = 'none';
            }
        }

        // Show done state
        if (this.isSigning) {
            document.getElementById(`${u}_active`).style.display = 'none';
            document.getElementById(`${u}_done`).style.display = 'flex';
            document.getElementById(`${u}_fullmsg`).textContent = `"${text}"`;
            this._timeoutId = setTimeout(() => { if (!this.isSigning) this.idle(); }, 5000);
        }
        this.isSigning = false;
        if (onDone) onDone();
    }

    cancel() {
        this.isSigning = false;
        if (this._timeoutId) { clearTimeout(this._timeoutId); this._timeoutId = null; }
        this.idle();
    }

    /* ═══════════════════════════════════════════════════════════════
       FINGERSPELLING — ASL alphabet, letter by letter
       ═══════════════════════════════════════════════════════════════ */
    async _fingerspell(word, emojiEl, wordEl, descEl) {
        const letters = word.toUpperCase().split('');
        for (let i = 0; i < letters.length && this.isSigning; i++) {
            const ch = letters[i];
            const asl = SignLanguageAvatar.ASL_ALPHA[ch];
            if (!asl) continue;
            emojiEl.style.transform = 'scale(0.5)';
            await this._delay(80);
            emojiEl.textContent = asl.emoji;
            wordEl.textContent = ch;
            descEl.textContent = `${asl.desc}  ·  Spelling: ${word.toUpperCase()} (${i + 1}/${letters.length})`;
            emojiEl.style.transform = 'scale(1)';
            await this._delay(550);
        }
    }

    /* ═══════════════════════════════════════════════════════════════
       TOKENIZER
       ═══════════════════════════════════════════════════════════════ */
    _tokenize(text) {
        let lower = text.toLowerCase().replace(/[^\w\s'-]/g, '').trim();
        const words = lower.split(/\s+/);
        const tokens = [];
        let i = 0;
        while (i < words.length) {
            let matched = false;
            for (let len = 4; len >= 2; len--) {
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

    _escHtml(text) {
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }

    _delay(ms) { return new Promise(r => setTimeout(r, ms)); }
}

import json
import config

# System prompt for the healthcare avatar "Thandi"
SYSTEM_PROMPT = """You are Thandi, a warm and compassionate AI healthcare assistant at {hospital_name}. 
You communicate with deaf patients to help them get the medical care they need.

Your personality:
- Warm, patient, and empathetic
- Use simple, clear language (the patient may be reading text)
- Professional but friendly
- Culturally sensitive to South African context
- Never diagnose - only triage and direct to appropriate care

Your job:
1. Greet the patient warmly
2. Ask about their reason for visiting
3. Ask follow-up questions about symptoms
4. Assess urgency
5. Direct them to the right department

Keep responses SHORT (1-2 sentences). Always end with a clear question or instruction.
Do NOT use medical jargon. Be direct and compassionate.""".format(hospital_name=config.HOSPITAL_NAME)

# Pre-scripted triage flow for demo mode (no API key needed)
TRIAGE_FLOW = [
    {
        "id": "greeting",
        "message": "Hello! 👋 I'm Thandi, your healthcare assistant. I'm here to help you get the care you need today. What brings you to the hospital?",
        "options": [
            {"label": "🏥 General Checkup", "value": "general_checkup", "next": "symptoms"},
            {"label": "🤕 Pain or Injury", "value": "pain_injury", "next": "pain_location"},
            {"label": "📋 Follow-up Visit", "value": "followup", "next": "followup_dept"},
            {"label": "🚨 Urgent / Emergency", "value": "emergency", "next": "emergency_confirm"},
            {"label": "💊 Prescription / Pharmacy", "value": "pharmacy", "next": "pharmacy_info"},
            {"label": "🧠 Mental Health Support", "value": "mental_health", "next": "mental_health_q"},
            {"label": "✏️ Other (describe below)", "value": "other", "next": "other_describe"},
        ]
    },
    {
        "id": "symptoms",
        "message": "I'd like to understand what you're experiencing. Which of these best describes your main concern?",
        "options": [
            {"label": "🤒 Fever / Cold / Flu", "value": "fever_cold", "next": "duration"},
            {"label": "😵 Headache / Dizziness", "value": "headache", "next": "duration"},
            {"label": "🫁 Breathing Difficulty", "value": "breathing", "next": "duration"},
            {"label": "🤢 Stomach / Nausea", "value": "stomach", "next": "duration"},
            {"label": "👁️ Eye / Vision Issues", "value": "eye_issues", "next": "duration"},
            {"label": "👂 Ear / Hearing Changes", "value": "ear_issues", "next": "duration"},
            {"label": "🦴 Joint / Muscle Pain", "value": "joint_pain", "next": "duration"},
            {"label": "🔴 Skin Rash / Irritation", "value": "skin_issue", "next": "duration"},
            {"label": "✏️ Other (describe below)", "value": "other_symptom", "next": "other_describe"},
        ]
    },
    {
        "id": "pain_location",
        "message": "I'm sorry you're in pain. Can you tell me where the pain is?",
        "options": [
            {"label": "🧠 Head", "value": "head_pain", "next": "pain_level"},
            {"label": "💗 Chest", "value": "chest_pain", "next": "pain_level"},
            {"label": "🤰 Stomach / Abdomen", "value": "stomach_pain", "next": "pain_level"},
            {"label": "🦴 Back", "value": "back_pain", "next": "pain_level"},
            {"label": "🦵 Legs / Knees", "value": "leg_pain", "next": "pain_level"},
            {"label": "💪 Arms / Shoulders", "value": "arm_pain", "next": "pain_level"},
            {"label": "🦶 Hands / Feet", "value": "extremity_pain", "next": "pain_level"},
            {"label": "📍 Other Location", "value": "other_pain", "next": "pain_level"},
        ]
    },
    {
        "id": "pain_level",
        "message": "On a scale of 1-10, how would you rate your pain right now?",
        "options": [
            {"label": "1-3 😐 Mild (uncomfortable but manageable)", "value": "mild", "next": "duration"},
            {"label": "4-6 😣 Moderate (affects daily activities)", "value": "moderate", "next": "duration"},
            {"label": "7-9 😫 Severe (very difficult to bear)", "value": "severe", "next": "duration"},
            {"label": "10 🚨 Worst possible pain", "value": "extreme", "next": "emergency_confirm"},
        ]
    },
    {
        "id": "duration",
        "message": "How long have you been experiencing this?",
        "options": [
            {"label": "📅 Just today", "value": "today", "next": "allergies"},
            {"label": "📅 A few days", "value": "few_days", "next": "allergies"},
            {"label": "📅 About a week", "value": "one_week", "next": "allergies"},
            {"label": "📅 More than a week", "value": "over_week", "next": "allergies"},
            {"label": "📅 More than a month", "value": "over_month", "next": "allergies"},
        ]
    },
    {
        "id": "allergies",
        "message": "Do you have any allergies we should know about?",
        "options": [
            {"label": "✅ No known allergies", "value": "none", "next": "medication"},
            {"label": "💊 Medication allergies", "value": "med_allergy", "next": "medication"},
            {"label": "🍎 Food allergies", "value": "food_allergy", "next": "medication"},
            {"label": "⚠️ Multiple allergies", "value": "multiple_allergy", "next": "medication"},
        ]
    },
    {
        "id": "medication",
        "message": "Are you currently taking any medication?",
        "options": [
            {"label": "❌ No medication", "value": "no_meds", "next": "hospital_familiar"},
            {"label": "💊 Yes - prescribed medication", "value": "prescribed", "next": "hospital_familiar"},
            {"label": "🏪 Yes - over the counter", "value": "otc", "next": "hospital_familiar"},
        ]
    },
    {
        "id": "followup_dept",
        "message": "Which department is your follow-up appointment with?",
        "options": [
            {"label": "🏥 General Practice", "value": "general", "next": "hospital_familiar"},
            {"label": "💗 Cardiology (Heart)", "value": "cardiology", "next": "hospital_familiar"},
            {"label": "🦴 Orthopedics (Bones/Joints)", "value": "orthopedics", "next": "hospital_familiar"},
            {"label": "🧠 Neurology (Brain/Nerves)", "value": "neurology", "next": "hospital_familiar"},
            {"label": "🔴 Dermatology (Skin)", "value": "dermatology", "next": "hospital_familiar"},
            {"label": "📋 I'm not sure", "value": "unsure", "next": "hospital_familiar"},
        ]
    },
    {
        "id": "emergency_confirm",
        "message": "⚠️ This sounds urgent. I'm directing you to our Emergency Department immediately. A nurse will attend to you right away. Please proceed to Block A, Ground Floor.",
        "options": [
            {"label": "🗺️ I need directions", "value": "need_directions", "next": "complete_emergency"},
            {"label": "✅ I know where to go", "value": "know_way", "next": "complete_emergency"},
        ]
    },
    {
        "id": "pharmacy_info",
        "message": "Do you have a prescription to fill, or do you need to speak with a pharmacist?",
        "options": [
            {"label": "📋 Fill a prescription", "value": "fill_rx", "next": "hospital_familiar"},
            {"label": "💬 Speak with pharmacist", "value": "consult_pharmacist", "next": "hospital_familiar"},
        ]
    },
    {
        "id": "mental_health_q",
        "message": "Thank you for reaching out. Mental health is important. How would you describe what you're feeling?",
        "options": [
            {"label": "😟 Anxiety / Worry", "value": "anxiety", "next": "duration"},
            {"label": "😢 Sadness / Depression", "value": "depression", "next": "duration"},
            {"label": "😴 Sleep Problems", "value": "sleep", "next": "duration"},
            {"label": "😤 Stress / Overwhelmed", "value": "stress", "next": "duration"},
            {"label": "💬 I just need someone to talk to", "value": "counseling", "next": "duration"},
        ]
    },
    {
        "id": "other_describe",
        "message": "Please describe what you are feeling or experiencing in your own words:",
        "options": [],
        "text_input": True,
        "next": "duration"
    },
    {
        "id": "hospital_familiar",
        "message": "One last question - are you familiar with this hospital's layout?",
        "options": [
            {"label": "✅ Yes, I know my way around", "value": "familiar", "next": "complete"},
            {"label": "❌ No, I need directions", "value": "not_familiar", "next": "complete"},
        ]
    },
    {
        "id": "complete",
        "message": "Thank you for your patience! I've prepared everything for you. A medical professional will see you soon.",
        "options": [],
        "is_final": True
    },
    {
        "id": "complete_emergency",
        "message": "Please head to the Emergency Department now. Your information has been sent ahead.",
        "options": [],
        "is_final": True
    },
]

# Map symptom values to department keywords for matching
SYMPTOM_DEPARTMENT_MAP = {
    "general_checkup": "general",
    "fever_cold": "general fever cold flu",
    "headache": "headache migraine dizzy",
    "breathing": "breathing lung respiratory",
    "stomach": "stomach nausea digestion",
    "eye_issues": "eye vision",
    "ear_issues": "ear hearing",
    "joint_pain": "bone joint muscle",
    "skin_issue": "skin rash",
    "head_pain": "headache migraine",
    "chest_pain": "heart chest cardiac",
    "stomach_pain": "stomach abdomen digestion",
    "back_pain": "bone joint back pain",
    "leg_pain": "bone joint muscle knee",
    "arm_pain": "bone joint muscle shoulder",
    "extremity_pain": "bone joint",
    "other_pain": "general",
    "other": "general",
    "other_symptom": "general",
    "emergency": "emergency urgent",
    "followup": "general",
    "general": "general",
    "cardiology": "heart cardiac cardiovascular",
    "orthopedics": "bone joint muscle",
    "neurology": "headache nerve brain",
    "dermatology": "skin rash",
    "unsure": "general",
    "pharmacy": "medication prescription pharmacy",
    "fill_rx": "medication prescription pharmacy",
    "consult_pharmacist": "medication prescription pharmacy",
    "anxiety": "mental anxiety stress",
    "depression": "mental depression mood",
    "sleep": "mental sleep",
    "stress": "mental stress",
    "counseling": "mental counseling",
    "pain_injury": "general",
    "mental_health": "mental",
}


class HealthcareChatbot:
    def __init__(self):
        self.provider = config.AI_PROVIDER
        self.client = None
        self._init_client()

    def _init_client(self):
        if self.provider == 'groq' and config.GROQ_API_KEY:
            try:
                from groq import Groq
                self.client = Groq(api_key=config.GROQ_API_KEY)
            except ImportError:
                self.provider = 'demo'
        elif self.provider == 'openai' and config.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            except ImportError:
                self.provider = 'demo'
        else:
            self.provider = 'demo'

    def get_triage_flow(self):
        return TRIAGE_FLOW

    def get_step(self, step_id):
        for step in TRIAGE_FLOW:
            if step['id'] == step_id:
                return step
        return None

    def analyze_symptoms(self, answers):
        """Analyze collected answers to determine department."""
        all_keywords = []
        for answer in answers:
            value = answer.get('value', '')
            if value in SYMPTOM_DEPARTMENT_MAP:
                all_keywords.append(SYMPTOM_DEPARTMENT_MAP[value])
        combined = ' '.join(all_keywords)
        return combined if combined else 'general checkup'

    def get_ai_response(self, message, conversation_history=None):
        """Get AI response for free-form conversation (translator mode)."""
        if self.provider == 'demo':
            return self._demo_translator_response(message)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        try:
            if self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=config.GROQ_MODEL,
                    messages=messages,
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content
            elif self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages,
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"I understand. Let me help you with that. (AI service temporarily unavailable)"

    def _demo_translator_response(self, message):
        """Simple response for demo mode translator."""
        msg_lower = message.lower()
        if any(w in msg_lower for w in ['hello', 'hi', 'hey']):
            return "Hello! I'm here to help translate. Please go ahead and speak or sign."
        elif any(w in msg_lower for w in ['pain', 'hurt', 'ache']):
            return "I understand you're experiencing pain. Can you point to where it hurts?"
        elif any(w in msg_lower for w in ['medicine', 'medication', 'prescription']):
            return "I'll note that regarding your medication. The doctor will review this."
        elif any(w in msg_lower for w in ['thank', 'thanks']):
            return "You're welcome! Is there anything else you'd like to communicate?"
        elif any(w in msg_lower for w in ['yes', 'ok', 'agree']):
            return "Understood. The doctor has noted your response."
        elif any(w in msg_lower for w in ['no', 'not', 'don\'t']):
            return "Noted. The doctor will take this into account."
        else:
            return "The patient is communicating. Let me help translate that for you."

    def cleanup_sign_sentence(self, raw_words):
        """Clean up raw sign language words into a proper sentence.

        Takes fragmented gesture words like 'Hello Pain There Help Medicine'
        and converts them into natural language like 'Hello, I have pain there. I need help with medicine.'
        """
        if not raw_words or not raw_words.strip():
            return raw_words

        # If it's already a short clear message, return as-is
        word_list = raw_words.strip().split()
        if len(word_list) <= 2:
            return raw_words.strip()

        if self.provider == 'demo' or not self.client:
            return self._demo_cleanup(raw_words)

        cleanup_prompt = (
            "You are a sign language interpreter at a hospital. "
            "A deaf patient communicated using South African Sign Language gestures. "
            "Each gesture maps to a word. The raw words detected are shown below. "
            "Your job: rewrite these words into a SHORT, natural English sentence that preserves the patient's meaning. "
            "Rules:\n"
            "- Keep it SHORT (1 sentence, max 15 words)\n"
            "- Do NOT add symptoms or info the patient didn't say\n"
            "- Do NOT ask questions — just restate what the patient said\n"
            "- Remove duplicate/repeated words\n"
            "- If words are: Hello Pain There Medicine → output: Hello, I have pain there. I need medicine.\n"
            "- If words are: Yes Thank you → output: Yes, thank you.\n"
            "- If words are: No Feeling bad Help → output: No, I feel bad. I need help.\n"
            "- Output ONLY the cleaned sentence, nothing else."
        )

        try:
            messages = [
                {"role": "system", "content": cleanup_prompt},
                {"role": "user", "content": raw_words}
            ]
            if self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=config.GROQ_MODEL,
                    messages=messages,
                    max_tokens=60,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            elif self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages,
                    max_tokens=60,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
        except Exception:
            return self._demo_cleanup(raw_words)

        return self._demo_cleanup(raw_words)

    def _demo_cleanup(self, raw_words):
        """Simple rule-based cleanup when AI is unavailable."""
        words = raw_words.strip().split()
        # Remove consecutive duplicates
        cleaned = [words[0]]
        for w in words[1:]:
            if w.lower() != cleaned[-1].lower():
                cleaned.append(w)

        # Simple sentence patterns
        result = ' '.join(cleaned)

        # Add punctuation helpers
        replacements = {
            'Hello ': 'Hello, ',
            'Yes ': 'Yes, ',
            'No ': 'No, ',
            'Thank you': 'Thank you.',
            'Pain': 'I have pain',
            'Help': 'I need help',
            'Medicine': 'I need medicine',
            'Need': 'I need',
            'Feeling bad': 'I feel bad',
            'There': 'there',
            'OK': 'OK.',
            'Please wait': 'please wait',
            'Wait': 'wait',
            'Call': 'please call',
        }
        for old, new in replacements.items():
            if result.startswith(old + ' ') or result == old:
                result = result.replace(old, new, 1)

        if not result.endswith('.') and not result.endswith('!') and not result.endswith('?'):
            result += '.'
        return result

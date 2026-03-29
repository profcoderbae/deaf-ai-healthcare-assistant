import os

# Flask
SECRET_KEY = os.environ.get('SECRET_KEY', 'deaf-ai-hackathon-2026')
DEBUG = os.environ.get('DEBUG', 'false').lower() in ('true', '1', 'yes')
PORT = int(os.environ.get('PORT', 5000))

# AI Provider: 'groq', 'openai', or 'demo' (no API key needed)
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'groq')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.1-8b-instant')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

# Database
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hospital.db')

# Hospital Configuration
HOSPITAL_NAME = os.environ.get('HOSPITAL_NAME', 'Tygerberg Hospital')
HOSPITAL_LAT = float(os.environ.get('HOSPITAL_LAT', '-33.9137'))
HOSPITAL_LNG = float(os.environ.get('HOSPITAL_LNG', '18.8603'))

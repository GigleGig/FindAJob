import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    LINKEDIN_USERNAME = os.getenv('LINKEDIN_USERNAME')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
    
    # Job search settings
    MAX_POSITIONS = 3
    DATABASE_PATH = 'job_applications.db'
    
    # Chrome settings for bot detection bypass
    CHROME_OPTIONS = [
        '--no-sandbox',
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
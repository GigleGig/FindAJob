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
    
    # Chrome settings for bot detection bypass (compatible options only)
    CHROME_OPTIONS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images'
    ]
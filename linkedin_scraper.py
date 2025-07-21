import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent
import time
import random
from typing import List, Dict
from config import Config
from database import JobDatabase

class LinkedInScraper:
    def __init__(self):
        self.driver = None
        self.db = JobDatabase()
        self.user_info = {}
        
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        ua = UserAgent()
        
        options = uc.ChromeOptions()
        for option in Config.CHROME_OPTIONS:
            options.add_argument(option)
        
        # Additional anti-detection measures
        options.add_argument(f'--user-agent={ua.random}')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = uc.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login(self):
        """Login to LinkedIn using credentials"""
        try:
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(random.uniform(2, 4))
            
            # Enter username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(Config.LINKEDIN_USERNAME)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(Config.LINKEDIN_PASSWORD)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "global-nav"))
            )
            
            print("Successfully logged into LinkedIn")
            return True
            
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def search_jobs(self, position: str, location: str) -> List[Dict]:
        """Search for jobs on LinkedIn"""
        jobs = []
        
        try:
            # Navigate to jobs page
            jobs_url = f"https://www.linkedin.com/jobs/search/?keywords={position}&location={location}&f_AL=true"
            self.driver.get(jobs_url)
            time.sleep(random.uniform(3, 5))
            
            # Scroll to load more jobs
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
            
            # Find job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
            
            for card in job_cards[:10]:  # Limit to first 10 jobs
                try:
                    job_data = self.extract_job_data(card)
                    if job_data and self.is_easy_apply(card):
                        jobs.append(job_data)
                        
                except Exception as e:
                    print(f"Error extracting job data: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error searching jobs: {e}")
            
        return jobs
    
    def extract_job_data(self, job_card) -> Dict:
        """Extract job information from a job card"""
        try:
            # Job title
            title_element = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__title a")
            title = title_element.text.strip()
            url = title_element.get_attribute('href')
            
            # Company name
            company = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__subtitle a").text.strip()
            
            # Location
            location = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__location").text.strip()
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'url': url,
                'source': 'linkedin'
            }
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return None
    
    def is_easy_apply(self, job_card) -> bool:
        """Check if job has Easy Apply option"""
        try:
            easy_apply = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__easy-apply-button")
            return easy_apply is not None
        except NoSuchElementException:
            return False
    
    def apply_to_job(self, job_url: str, user_info: Dict) -> Dict:
        """Apply to a job if it's easy apply"""
        try:
            self.driver.get(job_url)
            time.sleep(random.uniform(3, 5))
            
            # Check for Easy Apply button
            try:
                easy_apply_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".jobs-apply-button--top-card"))
                )
                easy_apply_btn.click()
                time.sleep(random.uniform(2, 4))
                
                # Handle application form
                return self.handle_application_form(user_info)
                
            except TimeoutException:
                return {'success': False, 'reason': 'No Easy Apply button found'}
                
        except Exception as e:
            return {'success': False, 'reason': f'Application error: {e}'}
    
    def handle_application_form(self, user_info: Dict) -> Dict:
        """Handle the Easy Apply form"""
        missing_info = []
        
        try:
            # Handle multiple pages of the application
            while True:
                # Fill any form fields
                self.fill_form_fields(user_info, missing_info)
                
                # Look for Next or Submit button
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Continue to next step']")
                    next_btn.click()
                    time.sleep(random.uniform(1, 3))
                    
                except NoSuchElementException:
                    # Try to find submit button
                    try:
                        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Submit application']")
                        
                        if not missing_info:  # Only submit if no missing info
                            submit_btn.click()
                            time.sleep(random.uniform(2, 4))
                            return {'success': True, 'missing_info': []}
                        else:
                            # Don't submit, record missing info
                            return {'success': False, 'missing_info': missing_info}
                            
                    except NoSuchElementException:
                        break
            
        except Exception as e:
            return {'success': False, 'reason': f'Form handling error: {e}', 'missing_info': missing_info}
    
    def fill_form_fields(self, user_info: Dict, missing_info: List):
        """Fill form fields with user information"""
        # Common field selectors and their corresponding user info keys
        field_mappings = {
            'input[name*="phoneNumber"]': 'phone',
            'input[name*="phone"]': 'phone',
            'textarea[name*="coverLetter"]': 'cover_letter',
            'input[name*="experience"]': 'years_experience',
            'input[name*="salary"]': 'expected_salary'
        }
        
        for selector, info_key in field_mappings.items():
            try:
                field = self.driver.find_element(By.CSS_SELECTOR, selector)
                if field.is_displayed() and field.is_enabled():
                    if info_key in user_info:
                        field.clear()
                        field.send_keys(user_info[info_key])
                    else:
                        missing_info.append(info_key)
                        
            except NoSuchElementException:
                continue
    
    def set_user_info(self, user_info: Dict):
        """Set user information for applications"""
        self.user_info = user_info
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
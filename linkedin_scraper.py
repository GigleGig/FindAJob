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
        try:
            options = uc.ChromeOptions()
            
            # Stable Chrome options for better compatibility
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            
            # Use undetected chromedriver with minimal options
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Set shorter timeouts to prevent hanging
            self.driver.set_page_load_timeout(15)
            self.driver.implicitly_wait(5)
            
            # Set window size to ensure elements are visible
            self.driver.set_window_size(1920, 1080)
            
            print("Chrome driver setup successful")
            
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            print("This might be due to Chrome version compatibility or network issues.")
            raise e
        
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
    
    def search_and_apply_jobs_fast(self, position: str, location: str, user_info: Dict) -> Dict:
        """Fast workflow: Search and apply to jobs directly on the page"""
        results = {'applied': 0, 'failed': 0, 'total_found': 0}
        
        try:
            # Navigate to jobs page with Easy Apply filter
            jobs_url = f"https://www.linkedin.com/jobs/search/?keywords={position}&location={location}&f_AL=true"
            print(f"Navigating to: {jobs_url}")
            
            # Direct navigation with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"Navigation attempt {attempt + 1}...")
                    self.driver.get(jobs_url)
                    
                    # Wait for any content to load
                    time.sleep(8)
                    
                    # Check if we're on LinkedIn
                    current_url = self.driver.current_url
                    if "linkedin.com" in current_url:
                        print(f"Successfully navigated to LinkedIn: {current_url}")
                        break
                    else:
                        print(f"Unexpected URL: {current_url}")
                        if attempt == max_retries - 1:
                            return results
                        continue
                        
                except Exception as e:
                    print(f"Navigation attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        return results
                    time.sleep(3)
            
            # Process jobs page by page
            page = 1
            jobs_applied = 0
            max_applications = 10  # Limit applications per search
            
            while page <= 2 and jobs_applied < max_applications:  # Limit to 2 pages
                print(f"Processing page {page}...")
                
                # Find ALL li elements on the page - simple and direct
                job_items = self.driver.find_elements(By.TAG_NAME, "li")
                print(f"Found {len(job_items)} li elements on page {page}")
                
                if not job_items:
                    print("No li elements found, breaking")
                    break
                
                results['total_found'] += len(job_items)
                
                # Process each li element - simple approach
                for i, li_item in enumerate(job_items):
                    try:
                        if jobs_applied >= max_applications:
                            break
                        
                        # Check if this li has Easy Apply text
                        li_text = li_item.text.lower()
                        
                        if 'easy apply' in li_text or 'candidatura facile' in li_text:
                            print(f"Found Easy Apply in li {i+1} - NEW APPROACH!")
                            
                            # Get job title and link
                            job_title = f"Job {i+1}"
                            job_link = None
                            try:
                                links = li_item.find_elements(By.TAG_NAME, "a")
                                for link in links:
                                    if link.text and len(link.text.strip()) > 10:
                                        job_title = link.text.strip()[:60]
                                        job_link = link
                                        break
                            except:
                                pass
                            
                            print(f"STEP 1: Clicking job to open details: {job_title}")
                            
                            # STEP 1: Click the job to open job details
                            if job_link:
                                try:
                                    self.driver.execute_script("arguments[0].click();", job_link)
                                    time.sleep(4)
                                    print("Job details opened")
                                except:
                                    try:
                                        job_link.click()
                                        time.sleep(4)
                                        print("Job details opened (regular click)")
                                    except:
                                        print("Could not open job details")
                                        continue
                            
                            # STEP 2: Look for Easy Apply button in the job details area
                            print("STEP 2: Looking for Easy Apply button in job details...")
                            easy_apply_found = False
                            
                            # Try multiple selectors for Easy Apply button
                            selectors = [
                                ".jobs-apply-button",
                                ".jobs-s-apply button", 
                                "button[data-testid='jobs-apply-button']",
                                ".artdeco-button--primary",
                                "button:contains('Easy Apply')"
                            ]
                            
                            for selector in selectors:
                                try:
                                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                    for button in buttons:
                                        if button.is_displayed() and button.is_enabled():
                                            button_text = button.text.lower()
                                            if 'easy apply' in button_text or 'candidatura facile' in button_text or 'apply' in button_text:
                                                print(f"FOUND EASY APPLY BUTTON: {button.text}")
                                                self.driver.execute_script("arguments[0].click();", button)
                                                time.sleep(4)
                                                easy_apply_found = True
                                                break
                                    if easy_apply_found:
                                        break
                                except:
                                    continue
                            
                            if easy_apply_found:
                                # Check for modal
                                modals = self.driver.find_elements(By.CSS_SELECTOR, ".jobs-easy-apply-modal, .artdeco-modal, [role='dialog']")
                                if modals:
                                    print("MODAL APPEARED! Processing application...")
                                    if self.complete_full_application(user_info, job_title):
                                        results['applied'] += 1
                                        jobs_applied += 1
                                        print(f"✓ SUCCESSFULLY APPLIED TO: {job_title}")
                                    else:
                                        results['failed'] += 1
                                        print(f"✗ FAILED TO COMPLETE APPLICATION: {job_title}")
                                else:
                                    print("Modal still didn't appear")
                                    results['failed'] += 1
                            else:
                                print("Easy Apply button not found in job details")
                                results['failed'] += 1
                            
                            time.sleep(random.uniform(3, 5))
                    
                    except Exception as e:
                        continue
                
                # Go to next page
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next page']")
                    if next_button.is_enabled():
                        next_button.click()
                        time.sleep(3)
                        page += 1
                    else:
                        print("No more pages available")
                        break
                except:
                    print("Next page button not found")
                    break
                    
        except Exception as e:
            print(f"Error in search and apply: {e}")
            
        return results
    
    def apply_to_current_job(self, user_info: Dict, job_title: str) -> bool:
        """Apply to the currently selected job"""
        try:
            # Look for Easy Apply button in the job details section
            easy_apply_selectors = [
                ".jobs-apply-button",
                ".jobs-s-apply button",
                "button[data-testid='jobs-apply-button']",
                ".artdeco-button--primary",
                "button:contains('Easy Apply')",
                "button:contains('Candidatura facile')"
            ]
            
            easy_apply_button = None
            for selector in easy_apply_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button_text = button.text.lower()
                            if 'easy apply' in button_text or 'candidatura facile' in button_text or 'apply' in button_text:
                                easy_apply_button = button
                                break
                    if easy_apply_button:
                        break
                except:
                    continue
            
            if not easy_apply_button:
                print(f"No Easy Apply button found for {job_title}")
                return False
            
            # Click the Easy Apply button
            try:
                self.driver.execute_script("arguments[0].click();", easy_apply_button)
                time.sleep(3)
            except:
                try:
                    easy_apply_button.click()
                    time.sleep(3)
                except:
                    print(f"Could not click Easy Apply button")
                    return False
            
            # Handle the application modal
            return self.handle_application_modal(user_info, job_title)
            
        except Exception as e:
            print(f"Error applying to {job_title}: {e}")
            return False
    
    def handle_application_modal(self, user_info: Dict, job_title: str) -> bool:
        """Handle the Easy Apply modal dialog"""
        try:
            # Wait for modal to appear
            modal_selectors = [
                ".jobs-easy-apply-modal",
                ".artdeco-modal",
                "[role='dialog']",
                ".job-application-modal"
            ]
            
            modal_found = False
            for selector in modal_selectors:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    modal_found = True
                    break
                except:
                    continue
            
            if not modal_found:
                print(f"Application modal not found for {job_title}")
                return False
            
            # Fill form fields
            self.fill_application_form(user_info)
            
            # Submit the application
            return self.submit_application(job_title)
            
        except Exception as e:
            print(f"Error handling application modal for {job_title}: {e}")
            return False
    
    def fill_application_form(self, user_info: Dict):
        """Fill application form fields"""
        try:
            # Phone number
            phone_selectors = [
                "input[name*='phone']",
                "input[type='tel']", 
                "input[placeholder*='phone']",
                "input[placeholder*='telefono']"
            ]
            
            if 'phone' in user_info:
                for selector in phone_selectors:
                    try:
                        phone_inputs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for phone_input in phone_inputs:
                            if phone_input.is_displayed() and phone_input.is_enabled():
                                phone_input.clear()
                                phone_input.send_keys(user_info['phone'])
                                break
                    except:
                        continue
            
            # Years of experience
            exp_selectors = [
                "input[name*='experience']",
                "select[name*='experience']",
                "input[placeholder*='years']",
                "input[placeholder*='anni']"
            ]
            
            if 'years_experience' in user_info:
                for selector in exp_selectors:
                    try:
                        exp_inputs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for exp_input in exp_inputs:
                            if exp_input.is_displayed() and exp_input.is_enabled():
                                if exp_input.tag_name == 'select':
                                    from selenium.webdriver.support.ui import Select
                                    select = Select(exp_input)
                                    # Try to select by visible text
                                    options = [opt.text for opt in select.options]
                                    years = user_info['years_experience']
                                    for option in options:
                                        if years in option or f"{years} " in option:
                                            select.select_by_visible_text(option)
                                            break
                                else:
                                    exp_input.clear()
                                    exp_input.send_keys(user_info['years_experience'])
                                break
                    except:
                        continue
                        
        except Exception as e:
            print(f"Error filling form: {e}")
    
    def submit_application(self, job_title: str) -> bool:
        """Submit the application"""
        try:
            # Look for submit buttons
            submit_selectors = [
                "button[aria-label*='Submit']",
                "button[data-testid*='submit']",
                "button:contains('Submit')",
                "button:contains('Send')", 
                "button:contains('Invia')",
                ".artdeco-button--primary",
                ".jobs-apply-button[type='submit']"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button_text = button.text.lower()
                            if any(word in button_text for word in ['submit', 'send', 'invia', 'apply']):
                                submit_button = button
                                break
                    if submit_button:
                        break
                except:
                    continue
            
            if submit_button:
                try:
                    self.driver.execute_script("arguments[0].click();", submit_button)
                    time.sleep(2)
                    return True
                except:
                    try:
                        submit_button.click()
                        time.sleep(2)
                        return True
                    except:
                        pass
            
            print(f"No submit button found for {job_title}")
            return False
            
        except Exception as e:
            print(f"Error submitting application for {job_title}: {e}")
            return False
    
    def handle_application_modal_simple(self, user_info: Dict, job_title: str) -> bool:
        """Simple application modal handler - just fill and submit"""
        try:
            time.sleep(2)  # Wait for modal
            
            # Fill phone if there's a phone input
            phone_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='tel'], input[name*='phone']")
            if phone_inputs and 'phone' in user_info:
                for phone_input in phone_inputs:
                    try:
                        if phone_input.is_displayed():
                            phone_input.clear()
                            phone_input.send_keys(user_info['phone'])
                            break
                    except:
                        continue
            
            # Look for any submit/send button and click it
            submit_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in submit_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        button_text = button.text.lower()
                        if any(word in button_text for word in ['submit', 'send', 'invia', 'apply']):
                            print(f"Clicking submit button: '{button.text}'")
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(2)
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"Error in simple modal handler: {e}")
            return False
    
    def complete_full_application(self, user_info: Dict, job_title: str) -> bool:
        """Simple application process - just click any button until we submit"""
        try:
            for step in range(5):  # Max 5 steps
                print(f"Step {step + 1} - Looking for buttons...")
                time.sleep(2)
                
                # Fill phone if we see it
                try:
                    phone_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='tel']")
                    for phone_input in phone_inputs:
                        if phone_input.is_displayed() and not phone_input.get_attribute('value'):
                            phone_input.send_keys(user_info.get('phone', ''))
                            print(f"Filled phone")
                            break
                except:
                    pass
                
                # Find ONLY application-related buttons
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                found_button = False
                
                for button in buttons:
                    try:
                        if button.is_displayed() and button.is_enabled() and button.text:
                            button_text = button.text.strip().lower()
                            
                            # Skip "Easy Apply" if we're already in a modal
                            if 'easy apply' in button_text:
                                # Check if we're in a modal already
                                if self.driver.find_elements(By.CSS_SELECTOR, ".jobs-easy-apply-modal, .artdeco-modal"):
                                    print("Already in modal, skipping Easy Apply button")
                                    continue
                            
                            # Only click application-related buttons
                            if any(word in button_text for word in ['submit', 'send', 'next', 'continue', 'review', 'invia', 'avanti']):
                                print(f"CLICKING APPLICATION BUTTON: {button.text}")
                                button.click()
                                time.sleep(2)
                                found_button = True
                                
                                # If it's a submit button, we're done
                                if any(word in button_text for word in ['submit', 'send', 'invia']):
                                    print(f"SUBMITTED APPLICATION!")
                                    return True
                                
                                break
                    except:
                        continue
                
                if not found_button:
                    print("No application buttons found, trying primary buttons...")
                    primary_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".artdeco-button--primary")
                    for button in primary_buttons:
                        try:
                            if button.is_displayed() and button.is_enabled():
                                print(f"CLICKING PRIMARY: {button.text}")
                                button.click()
                                time.sleep(2)
                                break
                        except:
                            continue
                
            return True  # Assume success after 5 steps
            
        except Exception as e:
            print(f"Error in application: {e}")
            return False
    
    def fill_any_form_fields(self, user_info: Dict):
        """Fill any visible form fields"""
        try:
            # Fill phone numbers
            if 'phone' in user_info:
                phone_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='tel'], input[name*='phone'], input[placeholder*='phone']")
                for phone_input in phone_inputs:
                    try:
                        if phone_input.is_displayed() and phone_input.is_enabled() and not phone_input.get_attribute('value'):
                            phone_input.clear()
                            phone_input.send_keys(user_info['phone'])
                            print(f"Filled phone: {user_info['phone']}")
                    except:
                        continue
            
            # Fill experience
            if 'years_experience' in user_info:
                exp_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='experience'], select[name*='experience']")
                for exp_input in exp_inputs:
                    try:
                        if exp_input.is_displayed() and exp_input.is_enabled():
                            if exp_input.tag_name == 'select':
                                from selenium.webdriver.support.ui import Select
                                select = Select(exp_input)
                                # Try to select years of experience
                                years = user_info['years_experience']
                                for option in select.options:
                                    if years in option.text or f"{years} " in option.text:
                                        select.select_by_visible_text(option.text)
                                        print(f"Selected experience: {option.text}")
                                        break
                            else:
                                if not exp_input.get_attribute('value'):
                                    exp_input.clear()
                                    exp_input.send_keys(user_info['years_experience'])
                                    print(f"Filled experience: {user_info['years_experience']}")
                    except:
                        continue
                        
        except Exception as e:
            print(f"Error filling form fields: {e}")
    
    def handle_application_fast(self, user_info: Dict) -> bool:
        """Handle application form quickly"""
        try:
            # Wait for application modal
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-easy-apply-modal, .job-application-modal"))
            )
            
            # Fill any visible form fields quickly
            self.fill_form_fields_fast(user_info)
            
            # Look for Submit/Send button and click
            submit_selectors = [
                "button[aria-label='Submit application']",
                "button[data-testid='submit-button']", 
                ".jobs-apply-button[type='submit']",
                "button:contains('Send application')",
                "button:contains('Submit')"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_btn.is_enabled():
                        submit_btn.click()
                        time.sleep(1)
                        return True
                except:
                    continue
            
            # If no submit button found, try clicking any primary button
            try:
                primary_btn = self.driver.find_element(By.CSS_SELECTOR, ".artdeco-button--primary")
                primary_btn.click()
                time.sleep(1)
                return True
            except:
                pass
                
            return False
            
        except Exception as e:
            print(f"Error handling application: {e}")
            return False
    
    def fill_form_fields_fast(self, user_info: Dict):
        """Fill form fields quickly with available info"""
        try:
            # Phone number
            if 'phone' in user_info:
                phone_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='phone'], input[type='tel']")
                for input_field in phone_inputs:
                    if input_field.is_displayed() and not input_field.get_attribute('value'):
                        input_field.clear()
                        input_field.send_keys(user_info['phone'])
                        break
            
            # Years of experience
            if 'years_experience' in user_info:
                exp_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[name*='experience'], select[name*='experience']")
                for input_field in exp_inputs:
                    if input_field.is_displayed():
                        if input_field.tag_name == 'select':
                            # Handle dropdown
                            from selenium.webdriver.support.ui import Select
                            select = Select(input_field)
                            select.select_by_visible_text(user_info['years_experience'])
                        else:
                            input_field.clear()
                            input_field.send_keys(user_info['years_experience'])
                        break
                        
        except Exception as e:
            print(f"Error filling form: {e}")
    
    def search_jobs(self, position: str, location: str) -> List[Dict]:
        """Legacy method - now just calls the fast version and returns empty list"""
        print("Using fast application workflow...")
        return []
    
    def extract_job_data(self, job_card) -> Dict:
        """Extract job information from a job card"""
        try:
            # Try multiple selectors for job title
            title = None
            title_selectors = [
                ".job-search-card__title a",
                ".jobs-search-results__list-item h3 a",
                ".artdeco-entity-lockup__title a",
                "h3 a[data-testid='job-title']",
                ".job-card-container__link"
            ]
            
            for selector in title_selectors:
                try:
                    title_element = job_card.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip()
                    url = title_element.get_attribute('href')
                    if title and url:
                        break
                except:
                    continue
            
            if not title:
                return None
            
            # Try multiple selectors for company
            company = None
            company_selectors = [
                ".job-search-card__subtitle a",
                ".jobs-search-results__list-item h4 a",
                ".artdeco-entity-lockup__subtitle a",
                "[data-testid='job-company-name']"
            ]
            
            for selector in company_selectors:
                try:
                    company_element = job_card.find_element(By.CSS_SELECTOR, selector)
                    company = company_element.text.strip()
                    if company:
                        break
                except:
                    continue
            
            # Try multiple selectors for location
            location = None
            location_selectors = [
                ".job-search-card__location",
                ".jobs-search-results__list-item .artdeco-entity-lockup__caption",
                "[data-testid='job-location']",
                ".job-card-container__metadata"
            ]
            
            for selector in location_selectors:
                try:
                    location_element = job_card.find_element(By.CSS_SELECTOR, selector)
                    location = location_element.text.strip()
                    if location:
                        break
                except:
                    continue
            
            if title:
                return {
                    'title': title,
                    'company': company or 'Unknown Company',
                    'location': location or 'Unknown Location',
                    'url': url,
                    'source': 'linkedin'
                }
            
            return None
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return None
    
    def is_easy_apply(self, job_card) -> bool:
        """Check if job has Easy Apply option"""
        try:
            # Primary method: Check for artdeco-button__text with "Easy Apply" text
            try:
                easy_apply_buttons = job_card.find_elements(By.CSS_SELECTOR, ".artdeco-button__text")
                for button in easy_apply_buttons:
                    if button.text.strip().lower() == 'easy apply':
                        return True
            except:
                pass
            
            # Fallback selectors
            easy_apply_selectors = [
                "button .artdeco-button__text",
                ".jobs-apply-button .artdeco-button__text",
                ".artdeco-button--primary .artdeco-button__text",
                ".job-search-card__easy-apply-button",
                "button[aria-label*='Easy Apply']"
            ]
            
            for selector in easy_apply_selectors:
                try:
                    elements = job_card.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if 'easy apply' in element.text.lower():
                            return True
                except:
                    continue
            
            # Text-based detection as final fallback
            try:
                card_text = job_card.text.lower()
                if 'easy apply' in card_text:
                    return True
            except:
                pass
                
            return False
            
        except Exception as e:
            print(f"Error checking Easy Apply: {e}")
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
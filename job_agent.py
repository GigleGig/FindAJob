import time
import random
from typing import Dict, List
from cv_analyzer import CVAnalyzer
from linkedin_scraper import LinkedInScraper
from database import JobDatabase
from job_search_helper import JobSearchHelper
import json

class JobAgent:
    def __init__(self):
        self.cv_analyzer = CVAnalyzer()
        self.linkedin_scraper = LinkedInScraper()
        self.db = JobDatabase()
        self.cv_data = {}
        self.matched_positions = []
        self.user_info = {}
    
    def analyze_cv(self, cv_path: str) -> Dict:
        """Step 1: Analyze CV using Gemini API"""
        print("Analyzing CV...")
        self.cv_data = self.cv_analyzer.analyze_cv(cv_path)
        print(f"CV Analysis completed. Found {len(self.cv_data.get('skills', []))} skills")
        return self.cv_data
    
    def find_matched_positions(self, locations: List[str], preferences: Dict = None) -> List[Dict]:
        """Step 2: Find most matched positions"""
        print("Finding matched positions...")
        self.matched_positions = self.cv_analyzer.match_positions(self.cv_data, locations, preferences)
        print(f"Found {len(self.matched_positions)} matched positions:")
        for i, pos in enumerate(self.matched_positions, 1):
            print(f"{i}. {pos.get('title', 'Unknown')} (Match: {pos.get('match_score', 0)}%)")
        return self.matched_positions
    
    def set_user_info(self, user_info: Dict):
        """Set user information for job applications"""
        self.user_info = user_info
        self.linkedin_scraper.set_user_info(user_info)
        print("User information set for applications")
    
    def search_and_apply_jobs(self, locations: List[str]) -> Dict:
        """Step 3 & 4: Search for jobs and apply to easy apply positions"""
        results = {
            'total_found': 0,
            'applications_attempted': 0,
            'applications_successful': 0,
            'jobs_with_missing_info': 0
        }
        
        # Setup LinkedIn scraper
        print("Setting up LinkedIn scraper...")
        try:
            self.linkedin_scraper.setup_driver()
            
            if not self.linkedin_scraper.login():
                print("Failed to login to LinkedIn")
                return results
                
        except Exception as e:
            print(f"LinkedIn scraper setup failed: {e}")
            print("\nChrome automation encountered issues, switching to manual job search helper...")
            
            # Use the job search helper instead
            helper = JobSearchHelper()
            helper.interactive_job_search(self.cv_data, self.matched_positions, locations, self.user_info)
            
            return results
        
        try:
            # Use fast workflow for each matched position in each location
            for position in self.matched_positions:
                for location in locations:
                    print(f"\nFast applying for '{position['title']}' in {location}...")
                    
                    # Use the new fast search and apply method
                    fast_results = self.linkedin_scraper.search_and_apply_jobs_fast(
                        position['title'], 
                        location, 
                        self.user_info
                    )
                    
                    # Update results
                    results['total_found'] += fast_results.get('total_found', 0)
                    results['applications_successful'] += fast_results.get('applied', 0)
                    results['applications_attempted'] += fast_results.get('applied', 0) + fast_results.get('failed', 0)
                    
                    print(f"Applied to {fast_results.get('applied', 0)} jobs, failed on {fast_results.get('failed', 0)}")
                    
                    # Short delay between different position searches
                    time.sleep(random.uniform(3, 5))
        
        finally:
            self.linkedin_scraper.close()
        
        return results
    
    def generate_reports(self):
        """Generate reports for jobs with missing information"""
        print("\nGenerating reports...")
        
        # Export to text file
        self.db.export_to_txt('job_applications_report.txt')
        
        # Get unapplied jobs for summary
        unapplied_jobs = self.db.get_unapplied_jobs()
        
        print(f"\nSummary:")
        print(f"Total unapplied jobs: {len(unapplied_jobs)}")
        
        # Show jobs with missing information
        jobs_with_missing = [job for job in unapplied_jobs if job.get('missing_info')]
        if jobs_with_missing:
            print(f"\nJobs requiring additional information:")
            for job in jobs_with_missing:
                print(f"- {job['title']} at {job['company']}")
                print(f"  URL: {job['url']}")
                print(f"  Missing: {', '.join(job['missing_info'])}")
                print()
    
    def run_full_process(self, cv_path: str, locations: List[str], user_info: Dict, preferences: Dict = None):
        """Run the complete job finding and application process"""
        print("Starting Auto Job Finding Agent...")
        print("=" * 50)
        
        # Step 1: Analyze CV
        cv_analysis = self.analyze_cv(cv_path)
        
        if not cv_analysis:
            print("Failed to analyze CV. Exiting.")
            return
        
        # Step 2: Find matched positions
        positions = self.find_matched_positions(locations, preferences)
        
        if not positions:
            print("No matched positions found. Exiting.")
            return
        
        # Step 3: Set user info
        self.set_user_info(user_info)
        
        # Step 4: Search and apply to jobs
        results = self.search_and_apply_jobs(locations)
        
        # Step 5: Generate reports
        self.generate_reports()
        
        # Final summary
        print("\n" + "=" * 50)
        print("FINAL RESULTS")
        print("=" * 50)
        print(f"Total jobs found: {results['total_found']}")
        print(f"Applications attempted: {results['applications_attempted']}")
        print(f"Applications successful: {results['applications_successful']}")
        print(f"Jobs requiring additional info: {results['jobs_with_missing_info']}")
        print("\nCheck 'job_applications_report.txt' for detailed results.")
        
        return results
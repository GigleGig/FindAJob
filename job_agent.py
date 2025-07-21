import time
import random
from typing import Dict, List
from cv_analyzer import CVAnalyzer
from linkedin_scraper import LinkedInScraper
from database import JobDatabase
import json

class JobAgent:
    def __init__(self):
        self.cv_analyzer = CVAnalyzer()
        self.linkedin_scraper = LinkedInScraper()
        self.db = JobDatabase()
        self.cv_data = {}
        self.matched_positions = []
        self.user_info = {}
    
    def analyze_cv(self, cv_text: str) -> Dict:
        """Step 1: Analyze CV using Gemini API"""
        print("Analyzing CV...")
        self.cv_data = self.cv_analyzer.analyze_cv(cv_text)
        print(f"CV Analysis completed. Found {len(self.cv_data.get('skills', []))} skills")
        return self.cv_data
    
    def find_matched_positions(self, locations: List[str]) -> List[Dict]:
        """Step 2: Find 3 most matched positions"""
        print("Finding matched positions...")
        self.matched_positions = self.cv_analyzer.match_positions(self.cv_data, locations)
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
        self.linkedin_scraper.setup_driver()
        
        if not self.linkedin_scraper.login():
            print("Failed to login to LinkedIn")
            return results
        
        try:
            # Search for each matched position in each location
            for position in self.matched_positions:
                for location in locations:
                    print(f"\nSearching for '{position['title']}' in {location}...")
                    
                    # Search jobs
                    jobs = self.linkedin_scraper.search_jobs(position['title'], location)
                    results['total_found'] += len(jobs)
                    
                    print(f"Found {len(jobs)} easy apply jobs")
                    
                    # Process each job
                    for job in jobs:
                        # Add to database
                        application_id = self.db.add_job_application({
                            'title': job['title'],
                            'company': job['company'],
                            'url': job['url'],
                            'location': job['location'],
                            'status': 'found'
                        })
                        
                        if application_id:
                            # Try to apply
                            print(f"Attempting to apply to {job['title']} at {job['company']}")
                            results['applications_attempted'] += 1
                            
                            # Add random delay between applications
                            time.sleep(random.uniform(10, 20))
                            
                            application_result = self.linkedin_scraper.apply_to_job(job['url'], self.user_info)
                            
                            if application_result.get('success'):
                                self.db.mark_as_applied(application_id)
                                results['applications_successful'] += 1
                                print(f"✓ Successfully applied to {job['title']}")
                            else:
                                # Update database with missing info
                                missing_info = application_result.get('missing_info', [])
                                if missing_info:
                                    results['jobs_with_missing_info'] += 1
                                    print(f"⚠ Missing info for {job['title']}: {', '.join(missing_info)}")
                                else:
                                    print(f"✗ Failed to apply to {job['title']}: {application_result.get('reason', 'Unknown error')}")
                    
                    # Add delay between searches
                    time.sleep(random.uniform(5, 10))
        
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
    
    def run_full_process(self, cv_text: str, locations: List[str], user_info: Dict):
        """Run the complete job finding and application process"""
        print("Starting Auto Job Finding Agent...")
        print("=" * 50)
        
        # Step 1: Analyze CV
        cv_analysis = self.analyze_cv(cv_text)
        
        if not cv_analysis:
            print("Failed to analyze CV. Exiting.")
            return
        
        # Step 2: Find matched positions
        positions = self.find_matched_positions(locations)
        
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
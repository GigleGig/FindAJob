#!/usr/bin/env python3
"""
Manual Job Search Helper
Generates optimized LinkedIn search URLs and provides guidance for manual job applications
"""

import webbrowser
from typing import List, Dict

class JobSearchHelper:
    def __init__(self):
        pass
    
    def generate_search_urls(self, positions: List[Dict], locations: List[str]) -> List[Dict]:
        """Generate optimized LinkedIn search URLs"""
        search_urls = []
        
        for position in positions:
            for location in locations:
                # Create optimized search URL
                title = position.get('title', '')
                keywords = position.get('keywords', [])
                
                # Combine title with relevant keywords for better results
                search_terms = [title] + keywords[:3]  # Use top 3 keywords
                search_query = ' '.join(search_terms).replace(' ', '%20')
                location_query = location.replace(' ', '%20').replace(',', '%2C')
                
                # LinkedIn Easy Apply URL
                linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location={location_query}&f_AL=true&sortBy=DD"
                
                search_urls.append({
                    'position': title,
                    'location': location,
                    'match_score': position.get('match_score', 0),
                    'reason': position.get('reason', ''),
                    'linkedin_url': linkedin_url,
                    'keywords': keywords,
                    'search_terms': search_terms
                })
        
        return search_urls
    
    def create_job_search_report(self, cv_data: Dict, positions: List[Dict], locations: List[str], personal_info: Dict):
        """Create a comprehensive job search report"""
        
        report = f"""
=================================================================
                    JOB SEARCH REPORT
=================================================================
Generated for: {cv_data.get('personal_info', {}).get('name', 'Job Seeker')}
Date: {self.get_current_date()}

PERSONAL PROFILE SUMMARY:
-------------------------
Experience: {cv_data.get('experience_years', 'N/A')} years
Key Skills: {', '.join(cv_data.get('skills', [])[:10])}
Education: {', '.join(cv_data.get('education', []))}
Target Salary: €{personal_info.get('expected_salary', 'Not specified')}
Target Locations: {', '.join(locations)}

TOP MATCHED POSITIONS:
=====================
"""
        
        search_urls = self.generate_search_urls(positions, locations)
        
        for i, search_info in enumerate(search_urls, 1):
            report += f"""
{i}. {search_info['position']} in {search_info['location']}
   Match Score: {search_info['match_score']}%
   Why it matches: {search_info['reason'][:100]}...
   
   🔗 DIRECT LINKEDIN SEARCH:
   {search_info['linkedin_url']}
   
   💡 SEARCH TIP: Look for jobs with "Easy Apply" button
   📝 APPLICATION READY: Phone: {personal_info.get('phone', 'N/A')}, Experience: {personal_info.get('years_experience', 'N/A')} years
   
   ───────────────────────────────────────────────────
"""
        
        report += f"""

MANUAL APPLICATION WORKFLOW:
============================
1. Click the LinkedIn URLs above
2. Look for jobs with "Easy Apply" button
3. Click "Easy Apply" 
4. Fill any required fields with your info:
   - Phone: {personal_info.get('phone', 'N/A')}
   - Years of Experience: {personal_info.get('years_experience', 'N/A')}
   - Expected Salary: €{personal_info.get('expected_salary', 'N/A')}
5. Click "Send application" or "Submit"
6. Repeat for multiple jobs!

OPTIMIZATION TIPS:
=================
• Apply to 10-20 jobs per day for best results
• Focus on jobs posted in the last 24-48 hours
• Use keywords: {', '.join(set([kw for pos in positions for kw in pos.get('keywords', [])]))}
• Customize your profile headline to match target roles
• Connect with recruiters in your target companies

TRACKED KEYWORDS FOR YOUR PROFILE:
=================================
{', '.join(cv_data.get('skills', []))}

"""
        
        return report
    
    def save_report_to_file(self, report: str, filename: str = "job_search_report.txt"):
        """Save the report to a text file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Job search report saved to: {filename}")
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False
    
    def open_linkedin_searches(self, search_urls: List[Dict], max_tabs: int = 5):
        """Open LinkedIn search URLs in browser tabs"""
        try:
            for i, search_info in enumerate(search_urls[:max_tabs]):
                print(f"Opening search for {search_info['position']} in {search_info['location']}...")
                webbrowser.open(search_info['linkedin_url'])
                if i < len(search_urls) - 1:
                    input("Press Enter to open next search (or Ctrl+C to stop)...")
        except KeyboardInterrupt:
            print("Search opening stopped by user")
        except Exception as e:
            print(f"Error opening searches: {e}")
    
    def get_current_date(self):
        """Get current date string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def interactive_job_search(self, cv_data: Dict, positions: List[Dict], locations: List[str], personal_info: Dict):
        """Interactive job search helper"""
        print("\n" + "="*60)
        print("             MANUAL JOB SEARCH HELPER")
        print("="*60)
        
        # Generate search URLs
        search_urls = self.generate_search_urls(positions, locations)
        
        print(f"\nFound {len(search_urls)} optimized job searches for you:")
        for i, search_info in enumerate(search_urls, 1):
            print(f"{i}. {search_info['position']} in {search_info['location']} ({search_info['match_score']}% match)")
        
        print("\nWhat would you like to do?")
        print("1. Create detailed report and save to file")
        print("2. Open LinkedIn searches in browser")
        print("3. Show search URLs only")
        print("4. Do all of the above")
        
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice in ['1', '4']:
                report = self.create_job_search_report(cv_data, positions, locations, personal_info)
                self.save_report_to_file(report)
                print("\nReport created successfully!")
            
            if choice in ['2', '4']:
                print("\nOpening LinkedIn searches in your browser...")
                self.open_linkedin_searches(search_urls)
            
            if choice in ['3', '4']:
                print("\nOptimized LinkedIn Search URLs:")
                print("-" * 40)
                for search_info in search_urls:
                    print(f"\n{search_info['position']} in {search_info['location']}:")
                    print(search_info['linkedin_url'])
            
        except KeyboardInterrupt:
            print("\nJob search helper stopped by user")
        except Exception as e:
            print(f"Error in interactive search: {e}")

if __name__ == "__main__":
    helper = JobSearchHelper()
    # Test mode
    test_positions = [
        {"title": "AI Engineer", "match_score": 90, "keywords": ["Python", "ML", "AI"], "reason": "Perfect match for your AI and Python skills"}
    ]
    test_locations = ["Bologna", "Milan"]
    test_cv = {"skills": ["Python", "AI", "ML"], "experience_years": "3"}
    test_personal = {"phone": "+39 123456789", "expected_salary": "50000", "years_experience": "3"}
    
    helper.interactive_job_search(test_cv, test_positions, test_locations, test_personal)
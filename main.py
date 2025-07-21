#!/usr/bin/env python3
"""
Auto Job Finding Agent
This script helps automatically find and apply to jobs based on CV analysis using Gemini API
"""

import sys
import os
from job_agent import JobAgent

def main():
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Error: .env file not found!")
        print("Please create a .env file with your credentials:")
        print("GEMINI_API_KEY=your_api_key")
        print("LINKEDIN_USERNAME=your_username")
        print("LINKEDIN_PASSWORD=your_password")
        return
    
    # Example usage - you can modify this based on your needs
    agent = JobAgent()
    
    # Sample CV text (replace with actual CV content)
    sample_cv = """
    John Doe
    Software Engineer
    
    Experience:
    - 5 years as Full Stack Developer at TechCorp
    - 3 years as Frontend Developer at StartupXYZ
    
    Skills:
    - Python, JavaScript, React, Node.js
    - AWS, Docker, Kubernetes
    - Machine Learning, Data Analysis
    
    Education:
    - BS Computer Science, University of Technology
    
    Achievements:
    - Led team of 5 developers
    - Increased application performance by 40%
    - Built scalable microservices architecture
    """
    
    # Preferred locations
    locations = ["New York, NY", "San Francisco, CA", "Remote"]
    
    # User information for applications
    user_info = {
        'phone': '+1-555-123-4567',
        'years_experience': '5',
        'expected_salary': '120000',
        'cover_letter': 'I am excited to apply for this position...'
    }
    
    print("=== AUTO JOB FINDING AGENT ===")
    print()
    print("This agent will:")
    print("1. Analyze your CV using Gemini AI")
    print("2. Find the 3 most matched positions")
    print("3. Search for jobs in your preferred locations")
    print("4. Apply to Easy Apply positions automatically")
    print("5. Generate reports for positions requiring manual info")
    print()
    
    # Confirm before starting
    response = input("Do you want to proceed? (y/n): ").lower().strip()
    if response != 'y':
        print("Exiting...")
        return
    
    # Run the agent
    try:
        results = agent.run_full_process(sample_cv, locations, user_info)
        print("\nAgent completed successfully!")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()
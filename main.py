#!/usr/bin/env python3
"""
Auto Job Finding Agent
This script helps automatically find and apply to jobs based on CV analysis using Gemini API
"""

import sys
import os
from job_agent import JobAgent
from config_loader import ConfigLoader

def main():
    print("=== AUTO JOB FINDING AGENT ===")
    print()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Error: .env file not found!")
        print("Please create a .env file with your credentials:")
        print("GEMINI_API_KEY=your_api_key")
        print("LINKEDIN_USERNAME=your_username")
        print("LINKEDIN_PASSWORD=your_password")
        return
    
    # Load user configuration
    try:
        config_loader = ConfigLoader()
        if not config_loader.validate_config():
            print("Configuration validation failed!")
            print("Please check your user_config.json file")
            return
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return
    
    # Get CV file path from user
    print("CV File Input")
    print("-" * 20)
    cv_path = input("Enter the path to your CV file (PDF, TXT, DOC): ").strip()
    
    # Remove quotes if user included them
    cv_path = cv_path.strip('"\'')
    
    if not cv_path:
        print("No CV file specified!")
        return
    
    # Try relative path first, then absolute path
    if not os.path.exists(cv_path):
        # If not absolute, try relative to current directory
        if not os.path.isabs(cv_path):
            relative_path = os.path.join(os.getcwd(), cv_path)
            if os.path.exists(relative_path):
                cv_path = relative_path
            else:
                print(f"CV file not found: {cv_path}")
                print(f"   Tried: {os.path.abspath(cv_path)}")
                return
        else:
            print(f"CV file not found: {cv_path}")
            return
    
    # Load configuration
    personal_info = config_loader.get_personal_info()
    locations = config_loader.get_preferred_locations()
    job_preferences = config_loader.get_job_preferences()
    app_settings = config_loader.get_application_settings()
    
    # Display current settings
    print("\nCurrent Settings")
    print("-" * 20)
    print(f"CV File: {cv_path}")
    print(f"Preferred Locations: {', '.join(locations)}")
    print(f"Phone: {personal_info.get('phone', 'Not set')}")
    print(f"Email: {personal_info.get('email', 'Not set')}")
    print(f"Expected Salary: ${personal_info.get('expected_salary', 'Not set')}")
    print(f"Max Jobs per Search: {job_preferences.get('max_jobs_per_search', 3)}")
    print(f"Auto Submit: {app_settings.get('auto_submit', True)}")
    
    print("\nProcess Overview")
    print("-" * 20)
    print("This agent will:")
    print("1. Read and analyze your CV using Gemini AI")
    print("2. Find the most matched job positions")
    print("3. Search for jobs in your preferred locations")
    print("4. Apply to Easy Apply positions automatically")
    print("5. Generate reports for positions requiring manual info")
    print()
    
    # Confirm before starting
    response = input("Do you want to proceed? (y/n): ").lower().strip()
    if response != 'y':
        print("Exiting...")
        return
    
    # Initialize and run the agent
    try:
        agent = JobAgent()
        
        results = agent.run_full_process(
            cv_path=cv_path,
            locations=locations,
            user_info=personal_info,
            preferences={
                **job_preferences,
                **app_settings
            }
        )
        
        print("\nAgent completed successfully!")
        print("\nFinal Summary:")
        print(f"   - Jobs found: {results.get('total_found', 0)}")
        print(f"   - Applications attempted: {results.get('applications_attempted', 0)}")
        print(f"   - Applications successful: {results.get('applications_successful', 0)}")
        print(f"   - Jobs requiring manual info: {results.get('jobs_with_missing_info', 0)}")
        print("\nCheck 'job_applications_report.txt' for detailed results.")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("Please check your configuration and try again.")

def setup_wizard():
    """Interactive setup wizard for first-time users"""
    print("=== FIRST TIME SETUP WIZARD ===")
    print()
    
    config = {
        "personal_info": {},
        "preferred_locations": [],
        "job_preferences": {
            "max_jobs_per_search": 3,
            "min_match_score": 70,
            "excluded_companies": [],
            "preferred_companies": []
        },
        "application_settings": {
            "auto_submit": True,
            "delay_between_applications": 15,
            "max_applications_per_day": 50
        }
    }
    
    # Personal Information
    print("Personal Information")
    print("-" * 20)
    config["personal_info"]["phone"] = input("Phone number: ")
    config["personal_info"]["email"] = input("Email address: ")
    config["personal_info"]["years_experience"] = input("Years of experience: ")
    config["personal_info"]["expected_salary"] = input("Expected salary: ")
    config["personal_info"]["cover_letter"] = input("Cover letter (optional): ")
    
    # Locations
    print("\nPreferred Locations")
    print("-" * 20)
    print("Enter locations one by one (press Enter with empty input to finish):")
    while True:
        location = input("Location: ").strip()
        if not location:
            break
        config["preferred_locations"].append(location)
    
    # Job Preferences
    print("\nJob Preferences")
    print("-" * 20)
    max_jobs = input("Max jobs per search (default 3): ").strip()
    if max_jobs:
        config["job_preferences"]["max_jobs_per_search"] = int(max_jobs)
    
    min_score = input("Minimum match score % (default 70): ").strip()
    if min_score:
        config["job_preferences"]["min_match_score"] = int(min_score)
    
    # Save configuration
    try:
        with open('user_config.json', 'w', encoding='utf-8') as file:
            import json
            json.dump(config, file, indent=2, ensure_ascii=False)
        
        print("\nConfiguration saved to user_config.json")
        print("You can now run the main agent!")
        
    except Exception as e:
        print(f"Error saving configuration: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        setup_wizard()
    else:
        main()
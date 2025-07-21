# Auto Job Finding Agent

An intelligent job search and application automation tool powered by Google's Gemini AI. This agent analyzes your CV, finds the most suitable positions, and automatically applies to Easy Apply jobs on LinkedIn.

## Features

1. **CV Analysis**: Uses Gemini AI to analyze your CV and extract key skills, experience, and qualifications
2. **Position Matching**: Finds the 3 most suitable job positions based on your profile
3. **Location-Based Search**: Searches for jobs in your preferred locations
4. **Easy Apply Automation**: Automatically applies to jobs that support Easy Apply
5. **Bot Detection Bypass**: Uses undetected Chrome driver to avoid LinkedIn's bot detection
6. **Smart Form Filling**: Automatically fills application forms with your information
7. **Missing Info Tracking**: Records jobs that require additional information you haven't provided
8. **Database Tracking**: SQLite database to track all applications and their status
9. **Report Generation**: Generates detailed reports of all job applications

## Requirements

- Python 3.8+
- Chrome browser
- LinkedIn account
- Gemini API key
- All dependencies in requirements.txt

## Setup

1. **Clone and navigate to the project:**
   ```bash
   cd Agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

4. **Configure your credentials in .env:**
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   LINKEDIN_USERNAME=your_linkedin_username
   LINKEDIN_PASSWORD=your_linkedin_password
   ```

## Usage

1. **Modify the CV and user information in main.py:**
   - Replace the sample CV with your actual CV content
   - Update your preferred locations
   - Set your user information (phone, experience, salary expectations, etc.)

2. **Run the agent:**
   ```bash
   python main.py
   ```

3. **The agent will:**
   - Analyze your CV using Gemini AI
   - Find 3 most matched positions
   - Search LinkedIn for Easy Apply jobs
   - Automatically apply to suitable positions
   - Generate reports for jobs requiring manual information

## Configuration

### User Information Fields

Update the `user_info` dictionary in main.py with your details:

```python
user_info = {
    'phone': '+1-555-123-4567',
    'years_experience': '5',
    'expected_salary': '120000',
    'cover_letter': 'Your cover letter text...'
}
```

### Supported Locations

Add your preferred job locations:

```python
locations = ["New York, NY", "San Francisco, CA", "Remote", "London, UK"]
```

## Output Files

- **job_applications.db**: SQLite database with all job applications
- **job_applications_report.txt**: Human-readable report of all applications

## Safety Features

1. **Easy Apply Only**: Only applies to jobs with Easy Apply feature
2. **Missing Info Detection**: Records jobs that need additional information instead of submitting incomplete applications  
3. **Rate Limiting**: Built-in delays between applications to avoid detection
4. **Bot Detection Bypass**: Uses undetected Chrome driver and random user agents

## Troubleshooting

1. **Login Issues**: 
   - Verify LinkedIn credentials in .env file
   - Check if LinkedIn requires 2FA (temporarily disable it)

2. **Bot Detection**:
   - The tool uses several anti-detection measures
   - If detected, wait a few hours before retrying

3. **API Limits**:
   - Gemini API has rate limits
   - Add delays if you hit rate limits

## Limitations

- Only works with LinkedIn Easy Apply jobs
- Requires manual review of jobs with missing information
- Subject to LinkedIn's rate limiting and bot detection
- Gemini API usage costs apply

## Ethical Usage

This tool is designed for legitimate job searching. Please:
- Only apply to positions you're genuinely interested in
- Review and customize applications before submission
- Respect platforms' terms of service
- Use reasonable delays between applications

## Support

For issues and questions, please check:
- LinkedIn credentials are correct
- Gemini API key is valid and has credits
- Chrome browser is installed and updated
- All Python dependencies are installed
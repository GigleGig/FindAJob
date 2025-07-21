import google.generativeai as genai
from config import Config
from pdf_reader import PDFReader
from typing import Dict, List
import json
import os

class CVAnalyzer:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.pdf_reader = PDFReader()
    
    def read_cv_file(self, cv_path: str) -> str:
        """
        Read CV from file (supports PDF and text files)
        """
        if not os.path.exists(cv_path):
            raise FileNotFoundError(f"CV file not found: {cv_path}")
        
        file_extension = os.path.splitext(cv_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                print("Reading PDF CV...")
                return self.pdf_reader.extract_text(cv_path)
            elif file_extension in ['.txt']:
                print("Reading text CV...")
                with open(cv_path, 'r', encoding='utf-8') as file:
                    return file.read()
            elif file_extension in ['.doc', '.docx']:
                raise ValueError("DOC/DOCX files are not yet supported. Please convert to PDF or TXT format.")
            else:
                raise ValueError(f"Unsupported file format: {file_extension}. Supported formats: PDF, TXT")
        except Exception as e:
            print(f"Error reading CV file: {e}")
            raise
    
    def analyze_cv(self, cv_input) -> Dict:
        """
        Analyze CV and extract key information for job matching
        cv_input can be either a file path (str) or CV text content (str)
        """
        # Determine if input is a file path or text content
        if os.path.exists(str(cv_input)):
            cv_text = self.read_cv_file(cv_input)
        else:
            cv_text = str(cv_input)
        
        if not cv_text or len(cv_text.strip()) < 50:
            raise ValueError("CV content is too short or empty")
        
        prompt = f"""
        Analyze the following CV and extract structured information in JSON format:
        
        CV Content:
        {cv_text}
        
        Please extract and return the following information in JSON format:
        {{
            "personal_info": {{
                "name": "Full name from CV",
                "email": "Email address if found",
                "phone": "Phone number if found"
            }},
            "skills": ["list of technical and soft skills"],
            "experience_years": "total years of experience as number",
            "job_titles": ["list of previous job titles"],
            "industries": ["list of industries worked in"],
            "education": ["degrees and certifications"],
            "key_achievements": ["notable achievements"],
            "preferred_roles": ["suggested job roles based on experience"],
            "salary_range": {{
                "min": "estimated minimum salary",
                "max": "estimated maximum salary"
            }},
            "summary": "Brief professional summary"
        }}
        
        Focus on technical skills, years of experience, and suggest 3-5 most suitable job positions.
        For salary ranges, consider the experience level and industry standards.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean and parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            cv_data = json.loads(response_text)
            print(f"Successfully analyzed CV for {cv_data.get('personal_info', {}).get('name', 'Unknown')}")
            return cv_data
            
        except Exception as e:
            print(f"Error analyzing CV: {e}")
            return {}
    
    def match_positions(self, cv_data: Dict, locations: List[str], preferences: Dict = None) -> List[Dict]:
        """
        Generate top 3 most matched positions based on CV analysis and preferred locations
        """
        max_positions = preferences.get('max_jobs_per_search', 3) if preferences else 3
        min_score = preferences.get('min_match_score', 70) if preferences else 70
        
        prompt = f"""
        Based on the CV analysis data below and preferred locations, suggest exactly {max_positions} most suitable job positions:
        
        CV Data:
        {json.dumps(cv_data, indent=2)}
        
        Preferred Locations:
        {', '.join(locations)}
        
        Job Preferences:
        - Minimum match score: {min_score}%
        - Focus on roles matching experience level
        
        Return exactly {max_positions} job positions in JSON format:
        {{
            "positions": [
                {{
                    "title": "Job Title",
                    "keywords": ["keyword1", "keyword2", "keyword3"],
                    "seniority_level": "entry/mid/senior",
                    "match_score": 95,
                    "reason": "Why this position matches",
                    "expected_salary_range": {{
                        "min": "minimum expected salary",
                        "max": "maximum expected salary"
                    }}
                }}
            ]
        }}
        
        Focus on positions that:
        1. Match the candidate's skills and experience level
        2. Are available in the specified locations
        3. Have high demand in current job market
        4. Align with career progression
        5. Meet the minimum match score of {min_score}%
        
        Consider the candidate's experience years: {cv_data.get('experience_years', 'unknown')}
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            data = json.loads(response_text)
            positions = data.get('positions', [])
            
            # Filter positions by minimum score if specified
            if min_score:
                positions = [pos for pos in positions if pos.get('match_score', 0) >= min_score]
            
            return positions[:max_positions]  # Ensure we don't exceed max positions
            
        except Exception as e:
            print(f"Error matching positions: {e}")
            return []
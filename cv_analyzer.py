import google.generativeai as genai
from config import Config
from typing import Dict, List
import json

class CVAnalyzer:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_cv(self, cv_text: str) -> Dict:
        """
        Analyze CV and extract key information for job matching
        """
        prompt = f"""
        Analyze the following CV and extract structured information in JSON format:
        
        CV Content:
        {cv_text}
        
        Please extract and return the following information in JSON format:
        {{
            "skills": ["list of technical and soft skills"],
            "experience_years": "total years of experience",
            "job_titles": ["list of previous job titles"],
            "industries": ["list of industries worked in"],
            "education": ["degrees and certifications"],
            "key_achievements": ["notable achievements"],
            "preferred_roles": ["suggested job roles based on experience"],
            "salary_range": "estimated salary range based on experience"
        }}
        
        Focus on technical skills, years of experience, and suggest 3-5 most suitable job positions.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean and parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
        except Exception as e:
            print(f"Error analyzing CV: {e}")
            return {}
    
    def match_positions(self, cv_data: Dict, locations: List[str]) -> List[Dict]:
        """
        Generate top 3 most matched positions based on CV analysis and preferred locations
        """
        prompt = f"""
        Based on the CV analysis data below and preferred locations, suggest exactly 3 most suitable job positions:
        
        CV Data:
        {json.dumps(cv_data, indent=2)}
        
        Preferred Locations:
        {', '.join(locations)}
        
        Return exactly 3 job positions in JSON format:
        {{
            "positions": [
                {{
                    "title": "Job Title",
                    "keywords": ["keyword1", "keyword2", "keyword3"],
                    "seniority_level": "entry/mid/senior",
                    "match_score": 95,
                    "reason": "Why this position matches"
                }}
            ]
        }}
        
        Focus on positions that:
        1. Match the candidate's skills and experience
        2. Are available in the specified locations
        3. Have high demand in current job market
        4. Align with career progression
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            data = json.loads(response_text)
            return data.get('positions', [])[:3]  # Ensure max 3 positions
        except Exception as e:
            print(f"Error matching positions: {e}")
            return []
import sqlite3
from typing import Dict, List
from config import Config
import json
from datetime import datetime

class JobDatabase:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Applications table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            location TEXT,
            applied BOOLEAN DEFAULT FALSE,
            application_date TIMESTAMP,
            status TEXT DEFAULT 'pending',
            requirements TEXT,
            missing_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Missing requirements table for positions that couldn't be auto-applied
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS missing_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            requirement TEXT NOT NULL,
            user_response TEXT,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_job_application(self, job_data: Dict) -> int:
        """Add a new job application to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO applications 
            (job_title, company, url, location, requirements, missing_info, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('title', ''),
                job_data.get('company', ''),
                job_data.get('url', ''),
                job_data.get('location', ''),
                json.dumps(job_data.get('requirements', [])),
                json.dumps(job_data.get('missing_info', [])),
                job_data.get('status', 'pending')
            ))
            
            application_id = cursor.lastrowid
            conn.commit()
            return application_id
            
        except sqlite3.IntegrityError:
            # Job already exists
            return None
        finally:
            conn.close()
    
    def mark_as_applied(self, application_id: int):
        """Mark application as successfully applied"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE applications 
        SET applied = TRUE, application_date = ?, status = 'applied'
        WHERE id = ?
        ''', (datetime.now(), application_id))
        
        conn.commit()
        conn.close()
    
    def get_unapplied_jobs(self) -> List[Dict]:
        """Get all jobs that haven't been applied to yet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM applications 
        WHERE applied = FALSE 
        ORDER BY created_at DESC
        ''')
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'id': row[0],
                'title': row[1],
                'company': row[2],
                'url': row[3],
                'location': row[4],
                'requirements': json.loads(row[7]) if row[7] else [],
                'missing_info': json.loads(row[8]) if row[8] else [],
                'status': row[9]
            })
        
        conn.close()
        return jobs
    
    def export_to_txt(self, filename: str = 'job_applications.txt'):
        """Export all job applications to a text file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM applications ORDER BY created_at DESC')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("JOB APPLICATIONS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            for row in cursor.fetchall():
                f.write(f"Job Title: {row[1]}\n")
                f.write(f"Company: {row[2]}\n")
                f.write(f"URL: {row[3]}\n")
                f.write(f"Location: {row[4]}\n")
                f.write(f"Applied: {'Yes' if row[5] else 'No'}\n")
                f.write(f"Status: {row[9]}\n")
                
                if row[8]:  # missing_info
                    missing = json.loads(row[8])
                    if missing:
                        f.write(f"Missing Information: {', '.join(missing)}\n")
                
                f.write("-" * 30 + "\n\n")
        
        conn.close()
        print(f"Report exported to {filename}")
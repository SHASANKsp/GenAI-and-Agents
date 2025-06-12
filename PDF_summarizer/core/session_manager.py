import os
import json
from datetime import datetime
from typing import Dict, List

class SessionManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_dir = f"sessions/{user_id}"
        os.makedirs(self.session_dir, exist_ok=True)
    
    def create_session(self, project_name: str) -> str:
        """Initialize new research project"""
        session_id = f"{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_path = f"{self.session_dir}/{session_id}.json"
        
        with open(session_path, 'w') as f:
            json.dump({
                "project": project_name,
                "created": datetime.now().isoformat(),
                "papers": [],
                "summaries": {}
            }, f)
        
        return session_id
    
    def add_paper(self, session_id: str, paper_data: Dict):
        """Add processed paper to session"""
        session_path = f"{self.session_dir}/{session_id}.json"
        
        with open(session_path, 'r+') as f:
            session = json.load(f)
            session["papers"].append({
                "title": paper_data.get("title", ""),
                "pmid": paper_data.get("pmid", ""),
                "year": paper_data.get("year", ""),
                "path": paper_data["storage_path"]
            })
            f.seek(0)
            json.dump(session, f)
    
    def get_session(self, session_id: str) -> Dict:
        """Retrieve complete session data"""
        with open(f"{self.session_dir}/{session_id}.json", 'r') as f:
            return json.load(f)
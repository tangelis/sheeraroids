import os
import json
import datetime

class HighScoreManager:
    def __init__(self, max_scores=10):
        self.max_scores = max_scores
        self.scores_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")
        self.high_scores = self.load_scores()
        
    def load_scores(self):
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_scores(self):
        with open(self.scores_file, 'w') as f:
            json.dump(self.high_scores, f)
    
    def add_score(self, initials, score, level):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        new_entry = {
            "initials": initials.upper()[:3],
            "score": score,
            "level": level,
            "date": date
        }
        
        self.high_scores.append(new_entry)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        
        if len(self.high_scores) > self.max_scores:
            self.high_scores = self.high_scores[:self.max_scores]
            
        self.save_scores()
        
    def is_high_score(self, score):
        if len(self.high_scores) < self.max_scores:
            return True
        return score > min(entry["score"] for entry in self.high_scores)
    
    def get_rank(self, score):
        for i, entry in enumerate(self.high_scores):
            if score > entry["score"]:
                return i + 1
        return len(self.high_scores) + 1 if len(self.high_scores) < self.max_scores else 0
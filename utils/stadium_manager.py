"""
Stadium GIF Manager
Loads and manages stadium GIFs and commentary
"""
import json
import os
import random
from pathlib import Path


class StadiumManager:
    """Manages stadium GIFs and match commentary"""
    
    def __init__(self):
        self.data = {}
        self.load_data()
    
    def load_data(self):
        """Load stadium GIFs and commentary from JSON file"""
        gif_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'stadium_gifs.json')
        
        try:
            with open(gif_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print(f"Warning: stadium_gifs.json not found at {gif_file}")
            self.data = self._get_default_data()
        except json.JSONDecodeError:
            print("Warning: Invalid JSON in stadium_gifs.json")
            self.data = self._get_default_data()
    
    def _get_default_data(self):
        """Return default data structure if file not found"""
        return {
            "stadiums": {
                "default": ["https://media.giphy.com/media/cricket-stadium.gif"]
            },
            "commentary": {
                "dot_ball": ["No run."],
                "single": ["One run."],
                "four": ["FOUR!"],
                "six": ["SIX!"],
                "wicket": ["OUT!"]
            }
        }
    
    def get_stadium_gif(self, stadium_name: str = None) -> str:
        """Get random GIF for a stadium"""
        stadiums = self.data.get("stadiums", {})
        
        if stadium_name and stadium_name in stadiums:
            gif_data = stadiums[stadium_name]
        else:
            gif_data = stadiums.get("default", [""])
        
        if isinstance(gif_data, list):
            return random.choice(gif_data) if gif_data else ""
        return gif_data if gif_data else ""
    
    def get_commentary(self, event_type: str) -> str:
        """Get random commentary for an event"""
        commentary = self.data.get("commentary", {})
        event_comments = commentary.get(event_type, [f"{event_type}!"])
        
        if isinstance(event_comments, list):
            return random.choice(event_comments) if event_comments else f"{event_type}!"
        return event_comments
    
    def reload(self):
        """Reload data from file"""
        self.load_data()


# Global instance
stadium_manager = StadiumManager()

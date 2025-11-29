"""
Celebration GIF Manager
Loads and manages player celebration GIFs for match events
Supports multiple GIFs per player - randomly selects one
"""
import json
import os
import random


class CelebrationManager:
    """Manages celebration GIFs for cricket events"""
    
    def __init__(self):
        self.gifs = {}
        self.load_gifs()
    
    def load_gifs(self):
        """Load GIF URLs from JSON file"""
        gif_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'celebration_gifs.json')
        
        try:
            with open(gif_file, 'r', encoding='utf-8') as f:
                self.gifs = json.load(f)
        except FileNotFoundError:
            print(f"Warning: celebration_gifs.json not found at {gif_file}")
            self.gifs = self._get_default_gifs()
        except json.JSONDecodeError:
            print("Warning: Invalid JSON in celebration_gifs.json")
            self.gifs = self._get_default_gifs()
    
    def _get_default_gifs(self):
        """Return default GIF structure if file not found"""
        return {
            "wicket_celebrations": {"default": ["https://media.giphy.com/media/3o7TKSx0g7RqRniGFG/giphy.gif"]},
            "century_celebrations": {"default": ["https://media.giphy.com/media/26u4cqiYI30juCOGY/giphy.gif"]},
            "fifty_celebrations": {"default": ["https://media.giphy.com/media/3o6Zt6ML6BklcajjsA/giphy.gif"]},
            "six_celebrations": {"default": ["https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"]},
            "four_celebrations": {"default": ["https://media.giphy.com/media/3oEjHV0z8S7WM4MwnK/giphy.gif"]},
            "match_win": {"default": ["https://media.giphy.com/media/26u4lOMA8JKSnL9Uk/giphy.gif"]},
            "match_start": {"default": ["https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif"]},
            "hat_trick": {"default": ["https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"]},
            "duck_out": {"default": ["https://media.giphy.com/media/3oEjHKvjqt5pssL99C/giphy.gif"]}
        }
    
    def _get_random_gif(self, gif_data):
        """Helper to get random GIF from string or list"""
        if isinstance(gif_data, list):
            return random.choice(gif_data) if gif_data else ""
        return gif_data if gif_data else ""
    
    def get_wicket_gif(self, bowler_name: str = None):
        """Get wicket celebration GIF for a specific bowler (randomly chosen if multiple)"""
        category = self.gifs.get('wicket_celebrations', {})
        
        if bowler_name and bowler_name in category:
            return self._get_random_gif(category[bowler_name])
        
        return self._get_random_gif(category.get('default', ""))
    
    def get_century_gif(self, batsman_name: str = None):
        """Get century celebration GIF for a specific batsman (randomly chosen if multiple)"""
        category = self.gifs.get('century_celebrations', {})
        
        if batsman_name and batsman_name in category:
            return self._get_random_gif(category[batsman_name])
        
        return self._get_random_gif(category.get('default', ""))
    
    def get_fifty_gif(self, batsman_name: str = None):
        """Get fifty celebration GIF for a specific batsman (randomly chosen if multiple)"""
        category = self.gifs.get('fifty_celebrations', {})
        
        if batsman_name and batsman_name in category:
            return self._get_random_gif(category[batsman_name])
        
        return self._get_random_gif(category.get('default', ""))
    
    def get_six_gif(self, batsman_name: str = None):
        """Get six celebration GIF for a specific batsman (randomly chosen if multiple)"""
        category = self.gifs.get('six_celebrations', {})
        
        if batsman_name and batsman_name in category:
            return self._get_random_gif(category[batsman_name])
        
        return self._get_random_gif(category.get('default', ""))
    
    def get_four_gif(self, batsman_name: str = None):
        """Get four celebration GIF (randomly chosen if multiple)"""
        category = self.gifs.get('four_celebrations', {})
        
        if batsman_name and batsman_name in category:
            return self._get_random_gif(category[batsman_name])
        
        return self._get_random_gif(category.get('default', ""))
    
    def get_match_win_gif(self, team_name: str = None):
        """Get match win celebration GIF (randomly chosen if multiple)"""
        category = self.gifs.get('match_win', {})
        
        if team_name and team_name in category:
            return self._get_random_gif(category[team_name])
        
        return self._get_random_gif(category.get('default', ""))
    
    def get_match_start_gif(self):
        """Get match start GIF (randomly chosen if multiple)"""
        category = self.gifs.get('match_start', {})
        return self._get_random_gif(category.get('default', ""))
    
    def get_hat_trick_gif(self):
        """Get hat-trick celebration GIF (randomly chosen if multiple)"""
        category = self.gifs.get('hat_trick', {})
        return self._get_random_gif(category.get('default', ""))
    
    def get_duck_gif(self):
        """Get duck out GIF (randomly chosen if multiple)"""
        category = self.gifs.get('duck_out', {})
        return self._get_random_gif(category.get('default', ""))
    
    def get_super_over_gif(self):
        """Get super over GIF (randomly chosen if multiple)"""
        category = self.gifs.get('super_over', {})
        return self._get_random_gif(category.get('default', ""))
    
    def add_player_gif(self, category: str, player_name: str, gif_url: str):
        """Add a GIF to a player's collection (creates array if player has multiple)"""
        if category not in self.gifs:
            self.gifs[category] = {}
        
        # If player already exists, convert to array or append
        if player_name in self.gifs[category]:
            existing = self.gifs[category][player_name]
            if isinstance(existing, list):
                # Already a list, append
                existing.append(gif_url)
            else:
                # Convert single GIF to list
                self.gifs[category][player_name] = [existing, gif_url]
        else:
            # New player - add as single GIF
            self.gifs[category][player_name] = gif_url
        
        # Save to file
        gif_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'celebration_gifs.json')
        try:
            with open(gif_file, 'w', encoding='utf-8') as f:
                json.dump(self.gifs, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving GIF: {e}")
            return False
    
    def reload_gifs(self):
        """Reload GIFs from file (useful after manual edits)"""
        self.load_gifs()


# Global instance
celebration_gifs = CelebrationManager()

"""
Image generation utilities using Pillow
Creates scoreboards, player cards, and match graphics
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import os


class ImageGenerator:
    """Generate cricket match images"""
    
    def __init__(self):
        self.width = 1200
        self.height = 800
        self.colors = {
            'bg_primary': (91, 44, 145),  # Purple
            'bg_secondary': (75, 35, 120),
            'gold': (255, 215, 0),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'green': (59, 165, 93),
            'red': (237, 66, 69),
            'orange': (255, 165, 0),
            'grey': (128, 128, 128),
            'light_grey': (200, 200, 200)
        }
        
        # Try to load fonts, fallback to default if not available
        try:
            self.font_large = ImageFont.truetype("arial.ttf", 72)
            self.font_title = ImageFont.truetype("arialbd.ttf", 48)
            self.font_medium = ImageFont.truetype("arial.ttf", 36)
            self.font_small = ImageFont.truetype("arial.ttf", 24)
            self.font_tiny = ImageFont.truetype("arial.ttf", 18)
        except:
            # Fallback to default font
            self.font_large = ImageFont.load_default()
            self.font_title = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_tiny = ImageFont.load_default()
    
    def create_match_start_image(self, venue, weather, umpire):
        """Create match start information image"""
        img = Image.new('RGB', (self.width, self.height), self.colors['bg_primary'])
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect
        for i in range(self.height):
            alpha = i / self.height
            color = tuple(int(self.colors['bg_primary'][j] * (1-alpha) + 
                             self.colors['bg_secondary'][j] * alpha) for j in range(3))
            draw.rectangle([(0, i), (self.width, i+1)], fill=color)
        
        # Title
        draw.text((self.width//2, 100), "🏏 MATCH DETAILS", 
                 fill=self.colors['gold'], font=self.font_title, anchor='mm')
        
        # Venue
        draw.text((self.width//2, 250), f"📍 {venue['name']}", 
                 fill=self.colors['white'], font=self.font_medium, anchor='mm')
        draw.text((self.width//2, 300), f"{venue['location']}, {venue['country']}", 
                 fill=self.colors['light_grey'], font=self.font_small, anchor='mm')
        
        # Weather
        draw.text((self.width//2, 400), f"{weather['emoji']} {weather['condition']}", 
                 fill=self.colors['white'], font=self.font_medium, anchor='mm')
        
        # Umpire
        draw.text((self.width//2, 520), f"🎓 Umpire: {umpire}", 
                 fill=self.colors['white'], font=self.font_small, anchor='mm')
        
        # Border
        draw.rectangle([(10, 10), (self.width-10, self.height-10)], 
                      outline=self.colors['gold'], width=5)
        
        return self._image_to_bytes(img)
    
    def create_playing_xi_image(self, team_name, players):
        """Create Playing XI image"""
        img = Image.new('RGB', (self.width, 1400), self.colors['bg_primary'])
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.rectangle([(0, 0), (self.width, 120)], fill=self.colors['gold'])
        draw.text((self.width//2, 60), f"⭐ {team_name} - PLAYING XI", 
                 fill=self.colors['bg_primary'], font=self.font_title, anchor='mm')
        
        y_offset = 180
        
        for idx, player in enumerate(players, 1):
            role_emoji = {
                'batsman': '🏏',
                'bowler': '⚡',
                'all_rounder': '💎',
                'wicket_keeper': '🧤'
            }.get(player['role'], '👤')
            
            # Player card
            card_y = y_offset + (idx - 1) * 110
            
            # Card background
            if idx <= 4:  # Top order
                card_color = self.colors['bg_secondary']
            elif player['role'] == 'wicket_keeper':
                card_color = self.colors['green']
            elif player['role'] == 'all_rounder':
                card_color = (100, 60, 150)
            else:
                card_color = self.colors['bg_secondary']
            
            draw.rectangle([(50, card_y), (self.width-50, card_y+90)], 
                          fill=card_color, outline=self.colors['gold'], width=2)
            
            # Player info
            draw.text((100, card_y+25), f"{role_emoji} {idx}. {player['name']}", 
                     fill=self.colors['white'], font=self.font_medium, anchor='lm')
            
            # Stats
            draw.text((self.width-250, card_y+25), f"BAT: {player['batting']}", 
                     fill=self.colors['gold'], font=self.font_small, anchor='lm')
            draw.text((self.width-250, card_y+60), f"BOWL: {player['bowling']}", 
                     fill=self.colors['gold'], font=self.font_small, anchor='lm')
            
            # Country flag
            draw.text((self.width-100, card_y+45), player['country'], 
                     fill=self.colors['white'], font=self.font_large, anchor='mm')
        
        return self._image_to_bytes(img)
    
    def create_scoreboard_image(self, match_state, team_name, bowling_team_name):
        """Create live scoreboard image"""
        img = Image.new('RGB', (1400, 900), self.colors['bg_primary'])
        draw = ImageDraw.Draw(img)
        
        # Main scoreboard section
        draw.rectangle([(0, 0), (1400, 200)], fill=self.colors['gold'])
        
        # Score
        score_text = f"{match_state.score}/{match_state.wickets}"
        draw.text((700, 80), score_text, 
                 fill=self.colors['bg_primary'], font=self.font_large, anchor='mm')
        
        # Overs
        overs_text = f"({match_state.current_over}.{match_state.current_ball} / {match_state.total_overs})"
        draw.text((700, 150), overs_text, 
                 fill=self.colors['bg_primary'], font=self.font_small, anchor='mm')
        
        # Team name
        draw.text((100, 30), team_name, 
                 fill=self.colors['bg_primary'], font=self.font_medium, anchor='lm')
        
        # Run rate
        crr = match_state.get_current_run_rate()
        draw.text((1300, 100), f"RR: {crr:.2f}", 
                 fill=self.colors['bg_primary'], font=self.font_small, anchor='rm')
        
        # Batsmen section
        y_offset = 250
        striker = match_state.get_current_striker()
        non_striker = match_state.get_current_non_striker()
        
        for i, batsman_id in enumerate([striker['id'], non_striker['id']]):
            if batsman_id in match_state.batsmen_stats:
                stats = match_state.batsmen_stats[batsman_id]
                is_striker = (i == 0)
                
                # Batsman card
                card_y = y_offset + i * 120
                card_color = self.colors['green'] if is_striker else self.colors['bg_secondary']
                
                draw.rectangle([(50, card_y), (1350, card_y+100)], 
                              fill=card_color, outline=self.colors['gold'], width=3)
                
                # Name with striker indicator
                name_text = f"{'⚫' if is_striker else ''} {stats['name']}"
                draw.text((80, card_y+50), name_text, 
                         fill=self.colors['white'], font=self.font_medium, anchor='lm')
                
                # Runs and balls
                draw.text((700, card_y+50), f"{stats['runs']} ({stats['balls']})", 
                         fill=self.colors['gold'], font=self.font_medium, anchor='mm')
                
                # Boundaries
                draw.text((1000, card_y+30), f"4s: {stats['fours']}", 
                         fill=self.colors['white'], font=self.font_small, anchor='lm')
                draw.text((1000, card_y+70), f"6s: {stats['sixes']}", 
                         fill=self.colors['white'], font=self.font_small, anchor='lm')
                
                # Strike rate
                draw.text((1250, card_y+50), f"SR: {stats['strike_rate']:.1f}", 
                         fill=self.colors['orange'], font=self.font_small, anchor='mm')
        
        # Current bowler section
        bowler = match_state.get_current_bowler()
        draw.rectangle([(50, 520), (1350, 620)], 
                      fill=self.colors['red'], outline=self.colors['gold'], width=3)
        
        draw.text((80, 570), f"⚡ {bowler['name']}", 
                 fill=self.colors['white'], font=self.font_medium, anchor='lm')
        
        if bowler['id'] in match_state.bowlers_stats:
            bowl_stats = match_state.bowlers_stats[bowler['id']]
            stats_text = f"{bowl_stats['overs']}-{bowl_stats['maidens']}-{bowl_stats['runs']}-{bowl_stats['wickets']}"
            draw.text((700, 570), stats_text, 
                     fill=self.colors['gold'], font=self.font_medium, anchor='mm')
            
            econ = bowl_stats['economy']
            draw.text((1250, 570), f"ECON: {econ:.2f}", 
                     fill=self.colors['white'], font=self.font_small, anchor='mm')
        
        # Timeline (last 10 balls)
        timeline_y = 680
        draw.text((700, timeline_y), "Timeline:", 
                 fill=self.colors['white'], font=self.font_small, anchor='mm')
        
        timeline_balls = match_state.current_over_balls[-10:] if hasattr(match_state, 'current_over_balls') else []
        ball_x = 200
        for ball in timeline_balls:
            ball_color = self.colors['green']
            if ball == 'W':
                ball_color = self.colors['red']
            elif ball in [4, 6]:
                ball_color = self.colors['gold']
            
            draw.ellipse([(ball_x, timeline_y+40), (ball_x+50, timeline_y+90)], 
                        fill=ball_color, outline=self.colors['white'], width=2)
            draw.text((ball_x+25, timeline_y+65), str(ball), 
                     fill=self.colors['white'], font=self.font_small, anchor='mm')
            ball_x += 70
        
        return self._image_to_bytes(img)
    
    def create_wicket_image(self, batsman_name, batsman_stats, bowler_name, dismissal_type):
        """Create wicket celebration image"""
        img = Image.new('RGB', (1200, 800), self.colors['red'])
        draw = ImageDraw.Draw(img)
        
        # Add dramatic effect
        for i in range(self.height):
            alpha = i / self.height
            color = tuple(int(self.colors['red'][j] * (1-alpha*0.3)) for j in range(3))
            draw.rectangle([(0, i), (self.width, i+1)], fill=color)
        
        # OUT! text
        draw.text((self.width//2, 120), "🔴 OUT!", 
                 fill=self.colors['white'], font=self.font_large, anchor='mm')
        
        # Dismissal type
        draw.text((self.width//2, 220), dismissal_type.upper(), 
                 fill=self.colors['gold'], font=self.font_title, anchor='mm')
        
        # Batsman name and stats
        draw.rectangle([(100, 300), (self.width-100, 480)], 
                      fill=self.colors['bg_primary'], outline=self.colors['gold'], width=4)
        
        draw.text((self.width//2, 340), batsman_name, 
                 fill=self.colors['white'], font=self.font_title, anchor='mm')
        
        stats_text = f"{batsman_stats['runs']} ({batsman_stats['balls']}) - {batsman_stats['fours']}x4  {batsman_stats['sixes']}x6"
        draw.text((self.width//2, 420), stats_text, 
                 fill=self.colors['gold'], font=self.font_medium, anchor='mm')
        
        # Bowler celebration
        draw.text((self.width//2, 580), f"⚡ {bowler_name} STRIKES!", 
                 fill=self.colors['white'], font=self.font_medium, anchor='mm')
        
        # Starburst effect
        center_x, center_y = self.width//2, self.height//2
        for angle in range(0, 360, 30):
            import math
            x1 = center_x + 400 * math.cos(math.radians(angle))
            y1 = center_y + 300 * math.sin(math.radians(angle))
            draw.line([(center_x, center_y), (x1, y1)], 
                     fill=(*self.colors['gold'], 50), width=3)
        
        return self._image_to_bytes(img)
    
    def create_innings_summary(self, team_name, total_score, wickets, overs, 
                              batsmen_stats, bowlers_stats):
        """Create innings summary scoreboard"""
        height = max(1200, 400 + len(batsmen_stats) * 80 + len(bowlers_stats) * 60)
        img = Image.new('RGB', (1400, height), self.colors['bg_primary'])
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.rectangle([(0, 0), (1400, 150)], fill=self.colors['gold'])
        draw.text((700, 50), f"{team_name}", 
                 fill=self.colors['bg_primary'], font=self.font_title, anchor='mm')
        draw.text((700, 110), f"{total_score}/{wickets} ({overs})", 
                 fill=self.colors['bg_primary'], font=self.font_large, anchor='mm')
        
        # Batting scorecard
        y = 200
        draw.text((100, y), "BATTING", 
                 fill=self.colors['gold'], font=self.font_medium, anchor='lm')
        
        y += 60
        # Headers
        draw.text((100, y), "BATSMAN", fill=self.colors['white'], font=self.font_small, anchor='lm')
        draw.text((600, y), "R", fill=self.colors['white'], font=self.font_small, anchor='mm')
        draw.text((700, y), "B", fill=self.colors['white'], font=self.font_small, anchor='mm')
        draw.text((800, y), "4s", fill=self.colors['white'], font=self.font_small, anchor='mm')
        draw.text((900, y), "6s", fill=self.colors['white'], font=self.font_small, anchor='mm')
        draw.text((1050, y), "SR", fill=self.colors['white'], font=self.font_small, anchor='mm')
        
        y += 50
        for batsman_id, stats in batsmen_stats.items():
            draw.rectangle([(50, y-5), (1350, y+45)], 
                          fill=self.colors['bg_secondary'], outline=self.colors['gold'], width=1)
            
            draw.text((100, y+20), stats['name'], 
                     fill=self.colors['white'], font=self.font_small, anchor='lm')
            draw.text((600, y+20), str(stats['runs']), 
                     fill=self.colors['gold'], font=self.font_small, anchor='mm')
            draw.text((700, y+20), str(stats['balls']), 
                     fill=self.colors['white'], font=self.font_small, anchor='mm')
            draw.text((800, y+20), str(stats['fours']), 
                     fill=self.colors['white'], font=self.font_small, anchor='mm')
            draw.text((900, y+20), str(stats['sixes']), 
                     fill=self.colors['white'], font=self.font_small, anchor='mm')
            draw.text((1050, y+20), f"{stats['strike_rate']:.1f}", 
                     fill=self.colors['orange'], font=self.font_small, anchor='mm')
            
            y += 70
        
        # Bowling scorecard
        y += 50
        draw.text((100, y), "BOWLING", 
                 fill=self.colors['gold'], font=self.font_medium, anchor='lm')
        
        y += 60
        # Headers
        draw.text((100, y), "BOWLER", fill=self.colors['white'], font=self.font_small, anchor='lm')
        draw.text((600, y), "O", fill=self.colors['white'], font=self.font_small, anchor='mm')
        draw.text((700, y), "M", fill=self.colors['white'], font=self.font_small, anchor='mm')
        draw.text((800, y), "R", fill=self.colors['white'], font=self.font_small, anchor='mm')
        draw.text((900, y), "W", fill=self.colors['white'], font=self.font_small, anchor='mm')
        draw.text((1050, y), "ECON", fill=self.colors['white'], font=self.font_small, anchor='mm')
        
        y += 50
        for bowler_id, stats in bowlers_stats.items():
            draw.rectangle([(50, y-5), (1350, y+45)], 
                          fill=self.colors['bg_secondary'], outline=self.colors['gold'], width=1)
            
            draw.text((100, y+20), stats['name'], 
                     fill=self.colors['white'], font=self.font_small, anchor='lm')
            draw.text((600, y+20), str(stats['overs']), 
                     fill=self.colors['gold'], font=self.font_small, anchor='mm')
            draw.text((700, y+20), str(stats['maidens']), 
                     fill=self.colors['white'], font=self.font_small, anchor='mm')
            draw.text((800, y+20), str(stats['runs']), 
                     fill=self.colors['white'], font=self.font_small, anchor='mm')
            draw.text((900, y+20), str(stats['wickets']), 
                     fill=self.colors['red'], font=self.font_small, anchor='mm')
            draw.text((1050, y+20), f"{stats['economy']:.2f}", 
                     fill=self.colors['orange'], font=self.font_small, anchor='mm')
            
            y += 60
        
        return self._image_to_bytes(img)
    
    def create_match_result_image(self, winner_name, margin, team1_score, team2_score):
        """Create final match result image"""
        img = Image.new('RGB', (1400, 900), self.colors['bg_primary'])
        draw = ImageDraw.Draw(img)
        
        # Celebration background
        for i in range(900):
            alpha = abs(450 - i) / 450
            color = tuple(int(self.colors['bg_primary'][j] * (1-alpha*0.3) + 
                             self.colors['gold'][j] * alpha * 0.2) for j in range(3))
            draw.rectangle([(0, i), (1400, i+1)], fill=color)
        
        # Trophy
        draw.text((700, 120), "🏆", 
                 fill=self.colors['gold'], font=self.font_large, anchor='mm')
        
        # Winner
        draw.text((700, 250), f"{winner_name} WON!", 
                 fill=self.colors['gold'], font=self.font_large, anchor='mm')
        
        # Margin
        draw.text((700, 350), margin, 
                 fill=self.colors['white'], font=self.font_title, anchor='mm')
        
        # Scores
        draw.rectangle([(150, 450), (1250, 750)], 
                      fill=self.colors['bg_secondary'], outline=self.colors['gold'], width=5)
        
        draw.text((700, 520), f"{team1_score}", 
                 fill=self.colors['white'], font=self.font_medium, anchor='mm')
        
        draw.text((700, 600), "VS", 
                 fill=self.colors['grey'], font=self.font_small, anchor='mm')
        
        draw.text((700, 680), f"{team2_score}", 
                 fill=self.colors['white'], font=self.font_medium, anchor='mm')
        
        return self._image_to_bytes(img)
    
    def _image_to_bytes(self, img):
        """Convert PIL Image to bytes"""
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr


# Global instance
image_gen = ImageGenerator()

"""
Match Graphics Generator - Creates professional cricket graphics
Wagon Wheels, Manhattan Graphs, Scorecards, Milestone Cards
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import math
import random

class MatchGraphics:
    """Generate professional cricket match graphics"""
    
    def __init__(self):
        self.bg_color = (26, 26, 26)  # Dark background
        self.text_color = (255, 255, 255)
        self.accent_color = (255, 165, 0)  # Orange
        self.green = (46, 204, 113)
        self.red = (231, 76, 60)
        self.blue = (52, 152, 219)
        
    def create_wagon_wheel(self, shot_zones):
        """
        Create wagon wheel showing where batsman scored runs
        shot_zones: list of (angle, runs) tuples
        """
        size = 600
        img = Image.new('RGBA', (size, size), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        center = (size // 2, size // 2)
        radius = 250
        
        # Draw cricket field circle
        draw.ellipse([center[0] - radius, center[1] - radius, 
                     center[0] + radius, center[1] + radius], 
                     outline=self.text_color, width=3)
        
        # Draw pitch in center
        pitch_length = 80
        pitch_width = 10
        draw.rectangle([center[0] - pitch_width, center[1] - pitch_length,
                       center[0] + pitch_width, center[1] + pitch_length],
                       fill=(139, 69, 19), outline=self.text_color)
        
        # Draw boundary circle
        boundary_radius = radius - 20
        draw.ellipse([center[0] - boundary_radius, center[1] - boundary_radius,
                     center[0] + boundary_radius, center[1] + boundary_radius],
                     outline=self.green, width=2, fill=None)
        
        # Plot shots
        for angle, runs in shot_zones:
            # Convert angle to radians
            rad = math.radians(angle - 90)  # -90 to make 0 degrees point up
            
            # Calculate distance based on runs (1s go shorter, 4s/6s go further)
            if runs == 1:
                distance = radius * 0.4
                color = self.blue
                thickness = 2
            elif runs == 2:
                distance = radius * 0.6
                color = self.blue
                thickness = 3
            elif runs == 4:
                distance = radius * 0.9
                color = self.accent_color
                thickness = 4
            elif runs == 6:
                distance = boundary_radius
                color = self.red
                thickness = 5
            else:
                continue
            
            # Calculate end point
            end_x = center[0] + distance * math.cos(rad)
            end_y = center[1] + distance * math.sin(rad)
            
            # Draw line from center to end point
            draw.line([center[0], center[1], end_x, end_y], 
                     fill=color, width=thickness)
            
            # Draw circle at end
            circle_size = 4 + runs
            draw.ellipse([end_x - circle_size, end_y - circle_size,
                         end_x + circle_size, end_y + circle_size],
                         fill=color)
        
        # Add title
        try:
            title_font = ImageFont.truetype("arial.ttf", 32)
        except:
            title_font = ImageFont.load_default()
        
        draw.text((size // 2, 30), "WAGON WHEEL", fill=self.text_color, 
                 font=title_font, anchor="mm")
        
        # Add legend
        legend_y = size - 60
        legend_font = ImageFont.load_default()
        draw.text((50, legend_y), "● Ones/Twos", fill=self.blue, font=legend_font)
        draw.text((200, legend_y), "● Fours", fill=self.accent_color, font=legend_font)
        draw.text((350, legend_y), "● Sixes", fill=self.red, font=legend_font)
        
        # Convert to bytes
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    
    def create_manhattan_graph(self, runs_per_over):
        """
        Create Manhattan graph showing runs scored per over
        runs_per_over: list of runs scored in each over
        """
        width = 800
        height = 500
        img = Image.new('RGBA', (width, height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Title
        try:
            title_font = ImageFont.truetype("arial.ttf", 32)
            label_font = ImageFont.truetype("arial.ttf", 18)
        except:
            title_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
        
        draw.text((width // 2, 30), "MANHATTAN - RUNS PER OVER", 
                 fill=self.text_color, font=title_font, anchor="mm")
        
        # Graph area
        graph_left = 80
        graph_right = width - 50
        graph_top = 100
        graph_bottom = height - 80
        graph_width = graph_right - graph_left
        graph_height = graph_bottom - graph_top
        
        # Draw axes
        draw.line([graph_left, graph_bottom, graph_right, graph_bottom], 
                 fill=self.text_color, width=2)
        draw.line([graph_left, graph_bottom, graph_left, graph_top], 
                 fill=self.text_color, width=2)
        
        if not runs_per_over:
            return buf
        
        max_runs = max(runs_per_over) if runs_per_over else 20
        if max_runs < 15:
            max_runs = 15
        
        bar_width = graph_width // len(runs_per_over) - 10
        
        # Draw bars
        for i, runs in enumerate(runs_per_over):
            bar_height = (runs / max_runs) * graph_height
            x = graph_left + (i * (graph_width // len(runs_per_over)))
            
            # Color based on runs
            if runs >= 15:
                color = self.red
            elif runs >= 10:
                color = self.accent_color
            elif runs >= 6:
                color = self.green
            else:
                color = self.blue
            
            # Draw bar
            draw.rectangle([x + 5, graph_bottom - bar_height, 
                          x + bar_width, graph_bottom],
                          fill=color, outline=self.text_color)
            
            # Draw over number
            draw.text((x + bar_width // 2, graph_bottom + 10), 
                     str(i + 1), fill=self.text_color, font=label_font, anchor="mm")
            
            # Draw runs on top of bar
            if runs > 0:
                draw.text((x + bar_width // 2, graph_bottom - bar_height - 10),
                         str(runs), fill=self.text_color, font=label_font, anchor="mm")
        
        # Y-axis labels
        for i in range(0, int(max_runs) + 5, 5):
            y = graph_bottom - (i / max_runs) * graph_height
            draw.line([graph_left - 5, y, graph_left, y], fill=self.text_color)
            draw.text((graph_left - 15, y), str(i), fill=self.text_color, 
                     font=label_font, anchor="rm")
        
        # Convert to bytes
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    
    def create_milestone_card(self, player_name, runs, balls, fours, sixes, strike_rate, milestone_type):
        """
        Create milestone celebration card (50 or 100)
        """
        width = 800
        height = 600
        
        # Create gradient background
        img = Image.new('RGBA', (width, height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw gradient
        for i in range(height):
            alpha = int(255 * (1 - i / height))
            color = (self.accent_color[0], self.accent_color[1], self.accent_color[2], alpha)
            draw.line([(0, i), (width, i)], fill=color)
        
        # Try to load fonts
        try:
            huge_font = ImageFont.truetype("arialbd.ttf", 120)
            title_font = ImageFont.truetype("arialbd.ttf", 60)
            stat_font = ImageFont.truetype("arial.ttf", 40)
            label_font = ImageFont.truetype("arial.ttf", 28)
        except:
            huge_font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            stat_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
        
        # Draw milestone text
        milestone_text = "FIFTY!" if milestone_type == 50 else "CENTURY!"
        emoji = "🔥" if milestone_type == 50 else "💯"
        
        draw.text((width // 2, 100), f"{emoji} {milestone_text} {emoji}", 
                 fill=self.red, font=title_font, anchor="mm", 
                 stroke_width=3, stroke_fill=(0, 0, 0))
        
        # Player name
        draw.text((width // 2, 200), player_name.upper(), 
                 fill=self.text_color, font=title_font, anchor="mm",
                 stroke_width=2, stroke_fill=(0, 0, 0))
        
        # Main score
        draw.text((width // 2, 320), str(runs), 
                 fill=self.accent_color, font=huge_font, anchor="mm",
                 stroke_width=4, stroke_fill=(0, 0, 0))
        
        # Stats row
        stats_y = 450
        spacing = width // 4
        
        # Balls
        draw.text((spacing, stats_y), str(balls), fill=self.text_color, 
                 font=stat_font, anchor="mm")
        draw.text((spacing, stats_y + 50), "BALLS", fill=self.text_color, 
                 font=label_font, anchor="mm")
        
        # Fours
        draw.text((spacing * 2, stats_y), str(fours), fill=self.green, 
                 font=stat_font, anchor="mm")
        draw.text((spacing * 2, stats_y + 50), "FOURS", fill=self.text_color, 
                 font=label_font, anchor="mm")
        
        # Sixes
        draw.text((spacing * 3, stats_y), str(sixes), fill=self.red, 
                 font=stat_font, anchor="mm")
        draw.text((spacing * 3, stats_y + 50), "SIXES", fill=self.text_color, 
                 font=label_font, anchor="mm")
        
        # Strike rate at bottom
        draw.text((width // 2, height - 50), f"Strike Rate: {strike_rate:.1f}", 
                 fill=self.accent_color, font=stat_font, anchor="mm")
        
        # Convert to bytes
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    
    def create_wicket_card(self, batsman_name, runs, balls, fours, sixes, strike_rate, 
                          dismissal_type, bowler_name):
        """
        Create wicket card showing batsman's innings
        """
        width = 750
        height = 500
        img = Image.new('RGBA', (width, height), (20, 20, 20))
        draw = ImageDraw.Draw(img)
        
        # Red border for OUT
        border_width = 8
        draw.rectangle([0, 0, width, height], outline=self.red, width=border_width)
        
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 48)
            name_font = ImageFont.truetype("arialbd.ttf", 40)
            stat_font = ImageFont.truetype("arial.ttf", 36)
            label_font = ImageFont.truetype("arial.ttf", 24)
            dismiss_font = ImageFont.truetype("arial.ttf", 20)
        except:
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            stat_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            dismiss_font = ImageFont.load_default()
        
        # OUT text
        draw.text((width // 2, 60), "🔴 OUT!", fill=self.red, 
                 font=title_font, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
        
        # Batsman name
        draw.text((width // 2, 130), batsman_name.upper(), 
                 fill=self.text_color, font=name_font, anchor="mm")
        
        # Main score
        score_text = f"{runs} ({balls})"
        draw.text((width // 2, 210), score_text, 
                 fill=self.accent_color, font=title_font, anchor="mm")
        
        # Stats
        stats_y = 310
        col1_x = width // 4
        col2_x = width // 2
        col3_x = width * 3 // 4
        
        # Fours
        draw.text((col1_x, stats_y), str(fours), fill=self.green, 
                 font=stat_font, anchor="mm")
        draw.text((col1_x, stats_y + 45), "FOURS", fill=self.text_color, 
                 font=label_font, anchor="mm")
        
        # Sixes
        draw.text((col2_x, stats_y), str(sixes), fill=self.red, 
                 font=stat_font, anchor="mm")
        draw.text((col2_x, stats_y + 45), "SIXES", fill=self.text_color, 
                 font=label_font, anchor="mm")
        
        # Strike Rate
        draw.text((col3_x, stats_y), f"{strike_rate:.1f}", fill=self.blue, 
                 font=stat_font, anchor="mm")
        draw.text((col3_x, stats_y + 45), "STRIKE RATE", fill=self.text_color, 
                 font=label_font, anchor="mm")
        
        # Dismissal info
        dismissal_text = f"{dismissal_type} by {bowler_name}"
        draw.text((width // 2, height - 40), dismissal_text, 
                 fill=self.text_color, font=dismiss_font, anchor="mm")
        
        # Convert to bytes
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    
    def get_form_indicator(self, recent_scores):
        """
        Get form indicator based on recent scores
        recent_scores: list of recent innings scores
        """
        if not recent_scores:
            return "⚪ New Player"
        
        avg = sum(recent_scores) / len(recent_scores)
        
        if avg >= 50:
            return "🔥🔥🔥 On Fire!"
        elif avg >= 35:
            return "🔥🔥 Hot Form"
        elif avg >= 20:
            return "🔥 Good Form"
        elif avg >= 10:
            return "⚪ Average"
        else:
            return "❄️ Cold"

# Global instance
match_graphics = MatchGraphics()

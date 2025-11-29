"""
Match Statistics Tracker
Tracks all ball-by-ball data for analytics and graphics
"""

class MatchTracker:
    """Track detailed match statistics"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all tracking data"""
        self.innings_data = {
            'batsmen': {},  # {batsman_id: {runs, balls, fours, sixes, shots}}
            'bowlers': {},  # {bowler_id: {overs, runs, wickets, balls}}
            'partnerships': [],  # List of partnerships
            'runs_per_over': [],  # Runs scored in each over
            'timeline': [],  # Ball-by-ball outcomes
            'shot_zones': [],  # (angle, runs) for wagon wheel
            'current_over_balls': 0,
            'current_over_runs': 0,
            'total_runs': 0,
            'total_wickets': 0,
            'total_balls': 0
        }
    
    def add_ball(self, batsman_id, bowler_id, runs, outcome, shot_type=None):
        """
        Record a ball
        outcome: 'dot', 'wicket', or run value (1, 2, 4, 6)
        """
        data = self.innings_data
        
        # Initialize batsman if new
        if batsman_id not in data['batsmen']:
            data['batsmen'][batsman_id] = {
                'runs': 0,
                'balls': 0,
                'fours': 0,
                'sixes': 0,
                'dots': 0,
                'shots': [],
                'milestones': []
            }
        
        # Initialize bowler if new
        if bowler_id not in data['bowlers']:
            data['bowlers'][bowler_id] = {
                'balls': 0,
                'runs': 0,
                'wickets': 0,
                'overs': 0.0,
                'maidens': 0
            }
        
        batsman = data['batsmen'][batsman_id]
        bowler = data['bowlers'][bowler_id]
        
        # Update batsman stats
        if outcome != 'wicket':
            batsman['balls'] += 1
            data['total_balls'] += 1
            bowler['balls'] += 1
            
            if outcome == 'dot':
                batsman['dots'] += 1
                data['timeline'].append('•')
            else:
                batsman['runs'] += runs
                data['total_runs'] += runs
                bowler['runs'] += runs
                data['current_over_runs'] += runs
                
                if runs == 4:
                    batsman['fours'] += 1
                    data['timeline'].append('4')
                elif runs == 6:
                    batsman['sixes'] += 1
                    data['timeline'].append('6')
                else:
                    data['timeline'].append(str(runs))
                
                # Record shot zone for wagon wheel
                if shot_type:
                    angle = self._shot_to_angle(shot_type)
                    data['shot_zones'].append((angle, runs))
        else:
            # Wicket
            batsman['balls'] += 1
            data['total_balls'] += 1
            data['total_wickets'] += 1
            bowler['balls'] += 1
            bowler['wickets'] += 1
            data['timeline'].append('W')
        
        # Check milestones
        if outcome != 'wicket':
            if batsman['runs'] == 50 and 50 not in batsman['milestones']:
                batsman['milestones'].append(50)
            elif batsman['runs'] >= 100 and 100 not in batsman['milestones']:
                batsman['milestones'].append(100)
        
        # Update over tracking
        data['current_over_balls'] += 1
        if data['current_over_balls'] == 6:
            data['runs_per_over'].append(data['current_over_runs'])
            data['current_over_balls'] = 0
            data['current_over_runs'] = 0
            
            # Update bowler overs
            bowler['overs'] = bowler['balls'] // 6 + (bowler['balls'] % 6) / 10
    
    def _shot_to_angle(self, shot_type):
        """Convert shot type to angle for wagon wheel"""
        shot_angles = {
            'drive': 0,  # Straight
            'loft': 30,  # Over mid-off
            'sweep': 60,  # Square leg
            'pull': 90,  # Mid-wicket
            'flick': 45,  # Fine leg
            'cut': 120,  # Point
            'defend': 0,  # Straight (if any runs)
            'leave': 0
        }
        
        # Add randomness ±15 degrees
        base_angle = shot_angles.get(shot_type, 0)
        import random
        return base_angle + random.randint(-15, 15)
    
    def get_batsman_stats(self, batsman_id):
        """Get detailed batsman statistics"""
        if batsman_id not in self.innings_data['batsmen']:
            return None
        
        stats = self.innings_data['batsmen'][batsman_id]
        runs = stats['runs']
        balls = stats['balls']
        
        return {
            'runs': runs,
            'balls': balls,
            'fours': stats['fours'],
            'sixes': stats['sixes'],
            'dots': stats['dots'],
            'strike_rate': (runs / balls * 100) if balls > 0 else 0,
            'milestones': stats['milestones']
        }
    
    def get_bowler_stats(self, bowler_id):
        """Get detailed bowler statistics"""
        if bowler_id not in self.innings_data['bowlers']:
            return None
        
        stats = self.innings_data['bowlers'][bowler_id]
        
        return {
            'overs': stats['overs'],
            'runs': stats['runs'],
            'wickets': stats['wickets'],
            'economy': (stats['runs'] / stats['overs']) if stats['overs'] > 0 else 0
        }
    
    def get_partnership(self):
        """Get current partnership details"""
        # This would track partnership between current batsmen
        # For simplicity, returning basic info
        return {
            'runs': self.innings_data['total_runs'],
            'balls': self.innings_data['total_balls']
        }
    
    def get_innings_summary(self):
        """Get complete innings summary"""
        return {
            'total_runs': self.innings_data['total_runs'],
            'total_wickets': self.innings_data['total_wickets'],
            'total_balls': self.innings_data['total_balls'],
            'overs': self.innings_data['total_balls'] // 6 + (self.innings_data['total_balls'] % 6) / 10,
            'run_rate': (self.innings_data['total_runs'] / (self.innings_data['total_balls'] / 6)) if self.innings_data['total_balls'] > 0 else 0,
            'batsmen': self.innings_data['batsmen'],
            'bowlers': self.innings_data['bowlers'],
            'runs_per_over': self.innings_data['runs_per_over'],
            'timeline': self.innings_data['timeline'],
            'shot_zones': self.innings_data['shot_zones']
        }

# Global tracker instance
match_tracker = MatchTracker()

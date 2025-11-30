"""
Dynamic match commentary and event generator for Cric Masters
"""
import random

def generate_match_commentary(team1, team2, result, highlights=None):
    """
    Generate realistic match commentary and highlights.
    Args:
        team1 (str): Team 1 name
        team2 (str): Team 2 name
        result (dict): Match result summary
        highlights (list): Optional list of highlight events
    Returns:
        str: Commentary string
    """
    comments = [
        f"Welcome to the clash between {team1} and {team2}!",
        f"{team1} won the toss and elected to bat first.",
        f"The crowd is buzzing with excitement!",
        f"A brilliant start by {team1}'s openers.",
        f"{team2}'s bowlers are fighting back with tight lines.",
        f"A stunning catch at the boundary!",
        f"{team1} sets a challenging total of {result.get('team1_score', 'N/A')}.",
        f"{team2} begins their chase with confidence.",
        f"A crucial wicket falls—momentum shifts!",
        f"{team2} needs {result.get('target', 'N/A')} runs in the last over!",
        f"It's down to the wire!",
        f"{result.get('winner', 'The match')} takes the victory!",
        f"Player of the Match: {result.get('player_of_match', 'N/A')}"
    ]
    if highlights:
        comments.extend(highlights)
    return "\n".join(random.sample(comments, min(len(comments), 8)))

def generate_dynamic_event():
    """
    Generate a random dynamic event (form boost, minor injury, highlight).
    Returns:
        str: Event description
    """
    events = [
        "A player is in top form and receives a temporary stat boost!",
        "Minor injury reported—player will play at reduced capacity for one match.",
        "Spectacular six! The crowd goes wild.",
        "Bowler bowls a maiden over—pressure mounts.",
        "Batsman scores a quick fifty!",
        "All-rounder delivers with both bat and ball.",
        "Wicket-keeper pulls off a lightning stumping!"
    ]
    return random.choice(events)

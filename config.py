"""
Configuration settings for Cric Mater Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')
ADMIN_IDS = [int(id_) for id_ in os.getenv('ADMIN_IDS', '').split(',') if id_]

# Match Configuration
MATCH_TYPES = {
    'test20': {'overs': 20, 'name': 'Test T20'},
    't20': {'overs': 20, 'name': 'T20'},
    'odi': {'overs': 50, 'name': 'ODI'},
    't10': {'overs': 10, 'name': 'T10'},
    'hundred': {'overs': 16.4, 'name': 'The Hundred'}
}

# Cricket venues
VENUES = [
    {"name": "Lord's", "location": "London", "country": "England"},
    {"name": "Eden Gardens", "location": "Kolkata", "country": "India"},
    {"name": "MCG", "location": "Melbourne", "country": "Australia"},
    {"name": "Wanderers", "location": "Johannesburg", "country": "South Africa"},
    {"name": "Seddon Park", "location": "Hamilton", "country": "New Zealand"},
    {"name": "Gaddafi Stadium", "location": "Lahore", "country": "Pakistan"},
    {"name": "Pallekele", "location": "Kandy", "country": "Sri Lanka"},
    {"name": "Kensington Oval", "location": "Barbados", "country": "West Indies"},
    {"name": "Dubai International", "location": "Dubai", "country": "UAE"},
    {"name": "Wankhede Stadium", "location": "Mumbai", "country": "India"},
]

# Umpires
UMPIRES = [
    "Chris Gaffaney", "Kumar Dharmasena", "Aleem Dar", "Richard Illingworth",
    "Marais Erasmus", "Paul Reiffel", "Joel Wilson", "Rod Tucker",
    "Richard Kettleborough", "Nitin Menon", "Adrian Holdstock"
]

# Weather conditions
WEATHER_CONDITIONS = [
    {"condition": "Sunny", "emoji": "☀️", "pitch_impact": 0.1},
    {"condition": "Partly Cloudy", "emoji": "⛅", "pitch_impact": 0},
    {"condition": "Overcast", "emoji": "☁️", "pitch_impact": -0.1},
    {"condition": "Humid", "emoji": "💧", "pitch_impact": -0.05},
    {"condition": "Windy", "emoji": "💨", "pitch_impact": 0.05},
]

# Pitch conditions
PITCH_CONDITIONS = [
    {"type": "Grassy", "desc": "Helps fast bowlers", "emoji": "🟢"},
    {"type": "Dry", "desc": "Aids spinners", "emoji": "🟤"},
    {"type": "Flat", "desc": "Batsman paradise", "emoji": "🟡"},
    {"type": "Two-paced", "desc": "Unpredictable bounce", "emoji": "🟠"},
]

# Colors for embeds
COLORS = {
    'primary': 0x5B2C91,  # Purple
    'success': 0x3BA55D,  # Green
    'danger': 0xED4245,   # Red
    'warning': 0xFEE75C,  # Yellow
    'info': 0x5865F2,     # Blue
    'gold': 0xFFD700,     # Gold
}

# Auction settings
AUCTION_SETTINGS = {
    'initial_budget': 10000000000,  # 100 crore (100 cr)
    'min_bid_increment': 500000,   # 5 lakh
    'team_size': 11,
    'min_batsmen': 3,
    'min_bowlers': 3,
    'min_all_rounders': 1,
    'min_wicket_keepers': 1,
    'max_overseas': 4,
    'impact_players': 1,
    'matches_before_auction': 3
}

# Economy settings
ECONOMY_SETTINGS = {
    'win_reward': 1000,           # Coins per win
    'loss_reward': 250,           # Coins for participation
    'wicket_bonus': 50,           # Per wicket taken
    'fifty_bonus': 100,           # For scoring 50
    'century_bonus': 500,         # For scoring 100
    'daily_bonus': 100,           # Daily login reward
    'starting_balance': 500,      # New user starting coins
    'legendary_auction_cost': 5000,  # Coins to enter legendary auction
}

# Shop items
SHOP_ITEMS = {
    'stat_boosts': {
        'batting_boost': {'name': 'Batting Boost +5', 'price': 500, 'boost': 5, 'duration': 3},
        'bowling_boost': {'name': 'Bowling Boost +5', 'price': 500, 'boost': 5, 'duration': 3},
        'super_boost': {'name': 'Super Boost +10', 'price': 1500, 'boost': 10, 'duration': 5},
    },
    'consumables': {
        'lucky_coin': {'name': 'Lucky Coin', 'price': 300, 'effect': 'Double coins for next match'},
        'revival': {'name': 'Revival Token', 'price': 800, 'effect': 'One extra review in match'},
        'power_play': {'name': 'Power Play Boost', 'price': 600, 'effect': 'Extra boundaries in powerplay'},
    },
    'packs': {
        'bronze_pack': {'name': 'Bronze Pack', 'price': 200, 'players': 3, 'rarity': 'common'},
        'silver_pack': {'name': 'Silver Pack', 'price': 500, 'players': 5, 'rarity': 'rare'},
        'gold_pack': {'name': 'Gold Pack', 'price': 1000, 'players': 5, 'rarity': 'epic'},
        'diamond_pack': {'name': 'Diamond Pack', 'price': 2500, 'players': 7, 'rarity': 'legendary'},
    }
}

# Player rarities
PLAYER_RARITIES = {
    'common': {'color': 0x808080, 'emoji': '⚪', 'boost': 0},
    'rare': {'color': 0x0099FF, 'emoji': '🔵', 'boost': 0.03},
    'epic': {'color': 0x9B59B6, 'emoji': '🟣', 'boost': 0.05},
    'legendary': {'color': 0xFFD700, 'emoji': '🟡', 'boost': 0.08},
}

# Leaderboard settings
LEADERBOARD_SETTINGS = {
    'weekly_prizes': {
        1: {'coins': 5000, 'pack': 'diamond_pack', 'title': '🥇 Weekly Champion'},
        2: {'coins': 3000, 'pack': 'gold_pack', 'title': '🥈 Runner Up'},
        3: {'coins': 2000, 'pack': 'silver_pack', 'title': '🥉 Third Place'},
    },
    'monthly_prizes': {
        1: {'coins': 20000, 'pack': 'diamond_pack', 'title': '👑 Monthly King'},
        2: {'coins': 15000, 'pack': 'gold_pack', 'title': '⭐ Monthly Star'},
        3: {'coins': 10000, 'pack': 'gold_pack', 'title': '💎 Monthly Legend'},
    },
    'reset_day': 'Monday',  # Weekly reset
}

# Image paths
IMAGE_PATHS = {
    'backgrounds': 'assets/backgrounds/',
    'celebrations': 'assets/celebrations/',
    'generated': 'images/generated/',
    'player_images': 'assets/players/',
}

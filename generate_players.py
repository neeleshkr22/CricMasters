import random

# Player name components
first_names = [
    # Common cricket names from various countries
    "Rahul", "Virat", "Rohit", "Shubman", "Prithvi", "Ruturaj", "Devdutt", "Yashasvi", "Tilak", "Rinku",
    "Steve", "David", "Glenn", "Mitchell", "Pat", "Josh", "Travis", "Cameron", "Marcus", "Aaron",
    "Joe", "Ben", "James", "Sam", "Chris", "Jonny", "Jos", "Moeen", "Mark", "Ollie",
    "Kane", "Tom", "Tim", "Devon", "Daryl", "Jimmy", "Trent", "Kyle", "Neil", "Martin",
    "Babar", "Shaheen", "Mohammad", "Hasan", "Fakhar", "Shadab", "Iftikhar", "Haris", "Naseem", "Abdullah",
    "Quinton", "Kagiso", "Anrich", "Lungi", "Aiden", "Temba", "Rassie", "Heinrich", "Keshav", "Marco",
    "Kusal", "Wanindu", "Dhananjaya", "Pathum", "Charith", "Dasun", "Chamika", "Maheesh", "Lahiru", "Dimuth",
    "Andre", "Jason", "Kieron", "Nicholas", "Shimron", "Alzarri", "Akeal", "Romario", "Kyle", "Shamar",
    "Shakib", "Mushfiqur", "Tamim", "Liton", "Mehidy", "Taskin", "Mustafizur", "Mahmudullah", "Afif", "Shoriful",
    "Rashid", "Mohammad", "Rahmat", "Hashmatullah", "Mujeeb", "Najibullah", "Gulbadin", "Azmatullah", "Naveen", "Fazalhaq",
    "Paul", "Harry", "Andrew", "George", "Curtis", "Mark", "Joshua", "Lorcan", "Barry", "Andy"
]

last_names = [
    "Sharma", "Patel", "Kumar", "Singh", "Kohli", "Yadav", "Reddy", "Gupta", "Varma", "Iyer",
    "Smith", "Warner", "Maxwell", "Starc", "Cummins", "Hazlewood", "Head", "Green", "Marsh", "Lyon",
    "Root", "Stokes", "Anderson", "Broad", "Wood", "Bairstow", "Buttler", "Ali", "Archer", "Pope",
    "Williamson", "Boult", "Southee", "Santner", "Mitchell", "Neesham", "Sodhi", "Phillips", "Young", "Henry",
    "Azam", "Afridi", "Rizwan", "Ali", "Zaman", "Khan", "Ahmed", "Rauf", "Shah", "Shafique",
    "de Kock", "Rabada", "Nortje", "Ngidi", "Markram", "Bavuma", "van der Dussen", "Klaasen", "Miller", "Maharaj",
    "Mendis", "Hasaranga", "de Silva", "Nissanka", "Asalanka", "Shanaka", "Karunaratne", "Theekshana", "Kumara", "Rajapaksa",
    "Russell", "Holder", "Pollard", "Pooran", "Hetmyer", "Joseph", "Hosein", "Shepherd", "Mayers", "Thomas",
    "Al Hasan", "Rahim", "Iqbal", "Das", "Hasan", "Ahmed", "Rahman", "Riyad", "Hossain", "Islam",
    "Khan", "Nabi", "Shah", "Shahidi", "Ur Rahman", "Zadran", "Naib", "Omarzai", "ul-Haq", "Farooqi",
    "Stirling", "Tector", "Balbirnie", "Adair", "Campher", "Little", "Tucker", "McBrine", "McCarthy", "Dockrell",
    "Williams", "Raza", "Ervine", "Chakabva", "Madhevere", "Jongwe", "Ngarava", "Muzarabani", "Masakadza", "Burl"
]

countries = [
    ("🇮🇳", False),  # India - not overseas
    ("🇦🇺", True),   # Australia
    ("🏴", True),    # England
    ("🇳🇿", True),   # New Zealand
    ("🇵🇰", True),   # Pakistan
    ("🇿🇦", True),   # South Africa
    ("🇱🇰", True),   # Sri Lanka
    ("🇧🇧", True),   # West Indies
    ("🇧🇩", True),   # Bangladesh
    ("🇦🇫", True),   # Afghanistan
    ("🇮🇪", True),   # Ireland
    ("🇿🇼", True),   # Zimbabwe
]

roles = {
    "batsman": {"bat_range": (65, 95), "bowl_range": (10, 50)},
    "bowler": {"bat_range": (10, 50), "bowl_range": (65, 95)},
    "all_rounder": {"bat_range": (60, 90), "bowl_range": (60, 90)},
    "wicket_keeper": {"bat_range": (65, 90), "bowl_range": (10, 40)}
}

def generate_players(count=1000):
    players_by_role = {
        "batsmen": [],
        "bowlers": [],
        "all_rounders": [],
        "wicket_keepers": []
    }
    
    # Distribution: 35% batsmen, 35% bowlers, 20% all-rounders, 10% keepers
    role_counts = {
        "batsman": int(count * 0.35),
        "bowler": int(count * 0.35),
        "all_rounder": int(count * 0.20),
        "wicket_keeper": int(count * 0.10)
    }
    
    player_id = 1
    used_names = set()
    
    for role, target_count in role_counts.items():
        if role == "batsman":
            role_key = "batsmen"
        elif role == "bowler":
            role_key = "bowlers"
        elif role == "all_rounder":
            role_key = "all_rounders"
        else:  # wicket_keeper
            role_key = "wicket_keepers"
        
        for i in range(target_count):
            # Generate unique name
            while True:
                first = random.choice(first_names)
                last = random.choice(last_names)
                name = f"{first} {last}"
                if name not in used_names:
                    used_names.add(name)
                    break
            
            country, overseas = random.choice(countries)
            
            # Generate stats based on role
            bat_min, bat_max = roles[role]["bat_range"]
            bowl_min, bowl_max = roles[role]["bowl_range"]
            
            batting = random.randint(bat_min, bat_max)
            bowling = random.randint(bowl_min, bowl_max)
            
            # Add some variance for realism
            if random.random() < 0.1:  # 10% chance of exceptional player
                if role == "batsman":
                    batting = min(99, batting + random.randint(5, 10))
                elif role == "bowler":
                    bowling = min(99, bowling + random.randint(5, 10))
                elif role == "all_rounder":
                    batting = min(95, batting + random.randint(3, 7))
                    bowling = min(95, bowling + random.randint(3, 7))
            
            prefix = role[:3] if role != "wicket_keeper" else "wk"
            player = {
                "id": f"{prefix}_{player_id:04d}",
                "name": name,
                "country": country,
                "role": role,
                "batting": batting,
                "bowling": bowling,
                "overseas": overseas
            }
            
            players_by_role[role_key].append(player)
            player_id += 1
    
    return players_by_role

# Generate players
print("Generating 1000 cricket players...")
players = generate_players(1000)

# Create the file content
content = '''"""
Player database with 1000 diverse cricket players from around the world
"""

PLAYERS_DATABASE = {
'''

for role, player_list in players.items():
    content += f'    # {role.upper().replace("_", " ")}\n'
    content += f'    "{role}": [\n'
    
    for player in player_list:
        content += f'        {player},\n'
    
    content += '    ],\n\n'

content += '''
}

def get_all_players():
    """Get all players as a flat list"""
    all_players = []
    for role_players in PLAYERS_DATABASE.values():
        all_players.extend(role_players)
    return all_players

def get_player_by_id(player_id):
    """Find a player by ID"""
    for role_players in PLAYERS_DATABASE.values():
        for player in role_players:
            if player["id"] == player_id:
                return player
    return None

def get_players_by_role(role):
    """Get all players of a specific role"""
    role_key = role + "s" if role != "wicket_keeper" else "wicket_keepers"
    return PLAYERS_DATABASE.get(role_key, [])
'''

# Write to file
with open('data/players.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Generated {len(players['batsmen'])} batsmen")
print(f"✅ Generated {len(players['bowlers'])} bowlers")  
print(f"✅ Generated {len(players['all_rounders'])} all-rounders")
print(f"✅ Generated {len(players['wicket_keepers'])} wicket keepers")
print(f"✅ Total: {sum(len(p) for p in players.values())} players")
print("✅ File saved to data/players.py")

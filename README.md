# 🏏 Cric Mater - Discord Cricket Bot

**The Ultimate Discord Cricket Bot with Full Economy System**

An immersive Discord bot that brings the excitement of cricket to your server! Play realistic cricket matches, build your dream team through auctions, earn coins, collect legendary players, and compete for weekly prizes!

## ✨ Features

### 🎮 Match System
- **Realistic Gameplay**: Ball-by-ball simulation with dynamic outcomes
- **Multiple Formats**: T20, ODI, T10, Test20, and The Hundred
- **Interactive UI**: Choose bowling types (Yorker, Googly, Bouncer, etc.) and batting shots (Drive, Cut, Pull, Sweep, etc.)
- **Live Scoreboard**: Beautiful generated scoreboards with player stats
- **DRS System**: Review umpire decisions with realistic outcomes
- **Match Conditions**: Dynamic weather, pitch conditions, and venues
- **Wicket Celebrations**: Animated wicket scenes with player stats
- **Coin Rewards**: Earn coins based on match performance!

### 💰 Economy System (NEW!)
- **Win Rewards**: 1000 coins for winning, 250 for losing
- **Performance Bonuses**: Extra coins for wickets (50), fifties (100), centuries (500)
- **Daily Rewards**: Claim 100 coins every 24 hours
- **Free Daily Packs**: Get random player packs daily
- **Coin Gifting**: Transfer coins to friends
- **Starting Balance**: New players start with 500 coins

### 🛒 Shop System (NEW!)
**Stat Boosts:**
- Batting Boost (+5 batting, 1 hour) - 500 coins
- Bowling Boost (+5 bowling, 1 hour) - 500 coins  
- Super Boost (+10 all stats, 2 hours) - 1500 coins

**Consumables:**
- Lucky Coin (2x coin rewards) - 750 coins
- Revival Token (continue after losing) - 1000 coins
- Power Play (guaranteed good over) - 800 coins

**Player Packs:**
- Bronze Pack (3 common players) - 1000 coins
- Silver Pack (5 rare players) - 2500 coins
- Gold Pack (5 epic players) - 5000 coins
- Diamond Pack (5 legendary players) - 10000 coins

### 👑 Legendary Auction System (NEW!)
- **Premium Entry**: 5000 coins to join
- **Top Players Only**: Legendary tier players with +10 stat boost
- **Higher Stakes**: 50M bidding budget
- **Exclusive Access**: Only for serious players

### 🏆 Enhanced Leaderboard (NEW!)
**Three Competition Types:**
1. **All-Time**: Overall best players
2. **Weekly**: Resets every Monday with prizes
3. **Monthly**: Resets monthly with bigger prizes

**Weekly Prizes:**
- 🥇 1st: 5000 coins + Gold Pack
- 🥈 2nd: 3000 coins + Silver Pack
- 🥉 3rd: 1500 coins + Bronze Pack

**Monthly Prizes:**
- 🥇 1st: 10000 coins + Diamond Pack
- 🥈 2nd: 6000 coins + Gold Pack
- 🥉 3rd: 3000 coins + Silver Pack

### 👥 Team Management
- **Player Database**: 100+ real cricket players from around the world
- **Hidden Selection**: Keep your Playing XI secret until the match
- **Team Requirements**: 4 Batsmen, 3 Bowlers, 2 All-Rounders, 2 Wicket-Keepers
- **Player Stats**: Batting and bowling ratings affect match outcomes
- **Rarity System**: Common, Rare, Epic, and Legendary players

### 🎪 Regular Auction System
- **IPL-Style Auctions**: Bid on players to build your team
- **Starting Budget**: $100 million per team
- **Impact Player Rule**: Modern cricket format support
- **Budget Management**: Strategic bidding to build balanced teams

### 📊 Statistics & Records
- **Personal Stats**: Track wins, losses, highest scores, and more
- **Match History**: Review recent matches with detailed stats
- **Global Leaderboard**: Compete with other players
- **Win Rates**: Detailed performance analytics
- **Economy Stats**: Total coins earned and spent tracking

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- MongoDB database
- Discord Bot Token

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```powershell
pip install -r requirements.txt
```

3. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Fill in your credentials:
```env
DISCORD_TOKEN=your_bot_token_here
MONGODB_URI=your_mongodb_connection_string
ADMIN_IDS=your_discord_id,another_admin_id
```

4. **Create Discord Bot**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to "Bot" section and create a bot
   - Copy the token to your `.env` file
   - Enable "Message Content Intent" and "Server Members Intent"

5. **Setup MongoDB**:
   - Create a free MongoDB Atlas account at [mongodb.com](https://www.mongodb.com/)
   - Create a cluster and get connection string
   - Add connection string to `.env` file

6. **Run the bot**:
```powershell
python bot.py
```

## 📝 Commands

### 🎮 Match Commands
- `cmplay [overs] [type]` - Start a new cricket match
  - Example: `cmplay 20 t20`
  - Types: t20, odi, t10, test20, hundred
  - **Earn 1000 coins for winning!**

- `cmselectteam` - Select your Playing XI (via DM)
- `cmteam [@user]` - View your or someone else's team

### 📊 Stats Commands
- `cmstats [@user]` - View match statistics and records
- `cmleaderboard [period]` - View leaderboard
  - Periods: `all`, `weekly`, `monthly`
  - Example: `cmleaderboard weekly`
- `cmrecords` - View your detailed match history

### 💰 Economy Commands
- `cmbal [@user]` - Check coin balance and stats
- `cmdaily` - Claim daily reward (100 coins, 24h cooldown)
- `cmshop [category]` - Browse the shop
  - Categories: `boosts`, `consumables`, `packs`
  - Example: `cmshop packs`
- `cmbuy [item_id]` - Purchase items from shop
- `cminventory` - View your items, boosts, and player cards
- `cmpack` - Open free daily pack (once per 24h)
- `cmgift @user [amount]` - Gift coins to another player
  - Example: `cmgift @friend 500`

### 🏛️ Auction Commands
- `cmjoinauction` - Join regular auction
- `cmjoinlegendary` - Join legendary auction (5000 coins)
- `cmbid [amount]` - Place a bid on current player
  - Example: `cmbid 5000000`
- `cmauctionstats` - View auction status
- `cmmyauction` - View your auction team

### ⚙️ Admin Commands
- `cmauction [players]` - Start a regular player auction
- `cmlegendaryauction [num]` - Start legendary auction with top players
- `cmnextbid` - Move to next player in auction
- `cmendauction` - End current auction

### ℹ️ Help
- `cmhelp` - Show all commands and economy tips
- `cmban @user [reason]` - Ban a user from the bot
- `cmunban [user_id]` - Unban a user
- `cmdbstats` - View database statistics

### General
- `cmhelp` - Show all commands

## 🎮 How to Play

### 1. Create Your Team
```
cmselectteam
```
Follow the DM prompts to select your Playing XI from the global player pool.

### 2. Start a Match
```
cmplay 20 t20
```
This starts a 20-over T20 match. Wait for another player to join.

### 3. Toss
The match creator calls heads or tails. Winner chooses to bat or bowl first.

### 4. Select Bowler
Bowling team selects their opening bowler from the team.

### 5. Play Ball-by-Ball
- **Bowler**: Choose delivery type (Yorker, Bouncer, Googly, etc.)
- **Batsman**: Choose shot (Drive, Pull, Sweep, etc.)
- Results are calculated based on player skills and choices

### 6. DRS
When a batsman is dismissed, they can review the decision.

### 7. Innings Complete
After both innings, the winner is declared with a full match summary.

## 🎪 Auction System

### Joining Auctions
1. Wait for admin to start an auction: `cmauction 20`
2. Join the auction: `cmjoinauction`
3. You receive $100 million budget

### Bidding
- Admin shows each player one by one
- Use `cmbid [amount]` to place bids
- Minimum increment: $500,000
- Highest bidder wins the player

### Building Your Team
- Must have balanced team composition
- Max 4 overseas players
- 1 impact player slot
- After auction ends, your team is automatically saved

## 🏗️ Project Structure

```
matchbot/
├── bot.py                      # Main bot file
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── cogs/
│   ├── cricket_commands.py     # Match and team commands
│   ├── admin_commands.py       # Admin-only commands
│   └── auction_commands.py     # Auction system commands
├── data/
│   └── players.py              # Player database
├── database/
│   └── db.py                   # MongoDB operations
├── game/
│   └── engine.py               # Cricket simulation engine
└── utils/
    └── image_generator.py      # Scoreboard image generation
```

## 🎨 Features Showcase

### Live Scoreboard
- Current score and overs
- Batsman stats (runs, balls, 4s, 6s, SR)
- Bowler stats (overs, maidens, runs, wickets, economy)
- Timeline of last 10 balls
- Run rate calculations

### Wicket Scenes
- Dismissal type (Bowled, Caught, LBW, etc.)
- Batsman scorecard
- Bowler celebration
- Dramatic visual effects

### Match Summary
- Complete batting scorecard
- Complete bowling figures
- Match result with margin
- Man of the Match (future feature)

## 🔮 Future Features

- [ ] **cmdrop** - Random player drops for trading
- [ ] Power-ups and boosts
- [ ] Tournament system
- [ ] Fantasy leagues
- [ ] Player form system
- [ ] Weather-affected gameplay
- [ ] Injury system
- [ ] Coaching upgrades
- [ ] Daily rewards
- [ ] Achievement badges

## ⚠️ Rules

1. **No Alt Accounts**: Statpadding with alternate accounts results in permanent ban
2. **No Match Abandonment**: Leaving matches counts as a loss
3. **Fair Play**: Respect opponents and enjoy the game
4. **Admin Decisions**: Final in case of disputes

## 🐛 Troubleshooting

### Bot doesn't respond
- Check if bot is online
- Verify you're using correct prefix: `cm`
- Check bot permissions in channel

### Can't receive DMs
- Enable "Allow direct messages from server members" in Privacy Settings

### Database errors
- Verify MongoDB connection string
- Check if MongoDB cluster is active

### Image generation issues
- Ensure Pillow is installed: `pip install Pillow`
- On Windows, may need to install fonts manually

## 🤝 Contributing

This is currently a personal project, but suggestions are welcome! Contact the bot owner for feature requests or bug reports.

## 📄 License

This project is for educational and entertainment purposes. Cricket player names and data are used under fair use.

## 👨‍💻 Developer

Created with ❤️ by a cricket enthusiast

---

## 🎮 Quick Start Commands

```powershell
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Run the bot
python bot.py
```

**Enjoy playing cricket on Discord! 🏏🎉**

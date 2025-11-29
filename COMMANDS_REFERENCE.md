# 🏏 Cric Mater Bot - Quick Command Reference

## 🎮 Player Commands

### Getting Started
```
cmhelp                          Show all commands
cmselectteam                    Create your Playing XI (via DM)
cmteam                          View your team
cmteam @username                View someone else's team
```

### Playing Matches
```
cmplay 20 t20                   Start a T20 (20 overs)
cmplay 50 odi                   Start an ODI (50 overs)
cmplay 10 t10                   Start a T10 (10 overs)
cmplay 20 test20                Start a Test T20
```

### Statistics
```
cmstats                         View your statistics
cmstats @username               View someone's statistics
cmleaderboard                   View top 10 players
```

### Auction System
```
cmjoinauction                   Join active auction
cmbid 5000000                   Bid $5 million on player
cmauctionstats                  View auction status
cmmyauction                     View your auction team
```

## 🛡️ Admin Commands

### Auction Management
```
cmauction 20                    Start auction with 20 players
cmnextbid                       Move to next player
cmendauction                    End auction and save teams
```

### Server Management
```
cmban @user Reason text         Ban a user from the bot
cmunban 123456789              Unban user by ID
cmclearmatches                  Clear all active matches
cmdbstats                       View database statistics
```

### Player Management
```
cmaddplayer "Name" role 85 75   Add custom player
                                (role: batsman/bowler/all_rounder/wicket_keeper)
```

## 🎯 Match Flow

1. **Start Match**: `cmplay 20 t20`
2. **Players Join**: React with ✅
3. **Toss**: Click Heads or Tails
4. **Choose**: Bat first or Bowl first
5. **Select Bowler**: Choose opening bowler
6. **Play Ball**: Choose bowling type and batting shot
7. **Continue**: Play all balls until innings complete
8. **Second Innings**: Repeat for chasing team
9. **Result**: Winner announced with full scorecard!

## 💡 Tips & Tricks

### Team Selection
- Select balanced team with variety
- Mix experienced and young players
- Have good fast bowlers AND spinners
- Choose reliable wicket-keeper

### Auction Strategy
- Don't spend all budget on first few players
- Target all-rounders for value
- Save money for impact players
- Build balanced team composition

### Match Strategy
- Use Yorkers at death overs
- Employ spin on turning pitches
- Aggressive shots when ahead
- Defensive play under pressure

## 📊 Understanding Stats

### Batting Stats
- **Runs**: Total runs scored
- **Balls**: Balls faced
- **4s/6s**: Boundaries hit
- **SR**: Strike Rate (runs per 100 balls)

### Bowling Stats
- **O**: Overs bowled
- **M**: Maiden overs (no runs)
- **R**: Runs conceded
- **W**: Wickets taken
- **Econ**: Economy rate (runs per over)

## 🎪 Auction Details

- **Starting Budget**: $100,000,000
- **Team Size**: 11 players
- **Min Bid Increment**: $500,000
- **Max Overseas**: 4 players
- **Impact Players**: 1 slot
- **Requirement**: Play 3 matches first

## ⚠️ Rules

1. **No Stat Padding**: Alt accounts = permanent ban
2. **No Leaving**: Abandoning match = automatic loss
3. **Respect Opponents**: Be a good sport
4. **Follow Admin Decisions**: Final in disputes
5. **Have Fun**: It's a game, enjoy it!

## 🆘 Need Help?

**Bot not responding?**
- Check bot is online (green status)
- Verify you used correct prefix: `cm`
- Make sure bot has channel permissions

**Can't select team?**
- Enable DMs from server members
- Check bot can send you messages

**Images not loading?**
- Wait a few seconds for generation
- Check your internet connection
- Bot might be processing

**Match stuck?**
- Contact an admin
- They can use `cmclearmatches`

## 🎮 Example Session

```
User1: cmplay 20 t20
Bot: [Shows match details with venue, weather, etc.]

User2: [Reacts with ✅]

Bot: [Toss interface]
User1: [Clicks Heads]
Bot: User1 won the toss!

User1: [Clicks Bat First]
Bot: [Shows User1's Playing XI]

User2: [Selects opening bowler]
Bot: [Shows bowling and batting options]

[Ball-by-ball gameplay continues...]

Bot: [Match complete! Shows final result]
```

## 🏆 Pro Tips

1. **Practice First**: Play a few matches to understand mechanics
2. **Build Team Carefully**: Team composition matters!
3. **Join Auctions**: Get better players over time
4. **Track Stats**: Learn from your performance
5. **Participate in Tournaments**: More fun with competitions!

---

**Quick Access:**
- Full Guide: README.md
- Setup Help: SETUP_GUIDE.md
- Project Info: PROJECT_SUMMARY.md

**Enjoy Cric Mater Bot! 🏏✨**

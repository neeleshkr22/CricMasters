# 🚀 Quick Start Guide - Cric Mater Bot

## For Players

### Getting Started (5 minutes)

1. **Select Your Team**
   ```
   cmselectteam
   ```
   - Bot will DM you
   - Choose 4 batsmen, 3 bowlers, 2 all-rounders, 2 wicket-keepers
   - Team selection is secret!

2. **Play Your First Match**
   ```
   cmplay 20 t20
   ```
   - Win to earn 1000 coins!
   - Bonus coins for wickets and big scores

3. **Claim Daily Rewards**
   ```
   cmdaily
   ```
   - Get 100 free coins every day
   - Never miss this!

4. **Open Free Pack**
   ```
   cmpack
   ```
   - One free pack per day
   - Collect common, rare, epic, and legendary players

### Economy Tips

**Earning Coins Fast:**
- 🏆 Win matches: 1000 coins base
- 🎯 Take 5 wickets in a match: +250 bonus
- 💯 Score a century: +500 bonus
- 📅 Daily reward: 100 coins
- 🎁 Free pack: Random players daily
- 🏅 Weekly leaderboard: Top 3 get prizes

**Smart Spending:**
- Save 5000 coins for legendary auctions
- Buy stat boosts before important matches
- Diamond packs give legendary players
- Use consumables strategically

**Weekly Competition Strategy:**
- Play more matches on weekends
- Use boosts to increase win rate
- Track leaderboard with `cmleaderboard weekly`
- Top 3 get coins + packs on Monday

### Essential Commands

```
cmhelp              → Show all commands
cmbal               → Check your coins
cmshop              → Browse shop
cminventory         → View your items
cmstats             → Your match stats
cmleaderboard       → See top players
cmrecords           → Your match history
```

---

## For Server Admins

### Bot Setup (10 minutes)

1. **Install Python 3.8+**
   - Download from python.org
   - Verify: `python --version`

2. **Setup MongoDB**
   - Create free account at mongodb.com
   - Create cluster
   - Get connection string
   - Add to config.py

3. **Configure Bot**
   - Go to discord.com/developers
   - Create application
   - Create bot
   - Enable intents: Message Content, Server Members
   - Copy token
   - Add to config.py:
   ```python
   DISCORD_TOKEN = "your_token_here"
   MONGO_URI = "your_mongodb_uri"
   ```

4. **Install Dependencies**
   ```powershell
   pip install discord.py motor pillow
   ```

5. **Run Bot**
   ```powershell
   python bot.py
   ```

6. **Invite Bot to Server**
   - Developer Portal → OAuth2 → URL Generator
   - Scopes: `bot`, `applications.commands`
   - Permissions: Send Messages, Embed Links, Attach Files, Read Message History
   - Copy URL and open in browser

### Admin Commands

```powershell
# Start regular auction
cmauction 20

# Start legendary auction (top 10 players)
cmlegendaryauction 10

# Manage auctions
cmnextbid              # Next player
cmendauction           # End auction
cmauctionstats         # View status
```

### Configuration Options

Edit `config.py` to customize:

**Economy Settings:**
```python
ECONOMY_SETTINGS = {
    "win_reward": 1000,        # Coins for winning
    "loss_reward": 250,        # Coins for losing
    "wicket_bonus": 50,        # Per wicket bonus
    "fifty_bonus": 100,        # Fifty bonus
    "century_bonus": 500,      # Century bonus
    "daily_bonus": 100,        # Daily reward
    "starting_balance": 500,   # New player start
    "legendary_auction_cost": 5000  # Entry fee
}
```

**Leaderboard Prizes:**
```python
LEADERBOARD_SETTINGS = {
    "weekly_prizes": {
        1: {"title": "🥇 1st Place", "coins": 5000, "pack": "Gold Pack"},
        2: {"title": "🥈 2nd Place", "coins": 3000, "pack": "Silver Pack"},
        3: {"title": "🥉 3rd Place", "coins": 1500, "pack": "Bronze Pack"}
    },
    "reset_day": "Monday"  # When to reset weekly
}
```

**Shop Items:**
- Adjust prices in `SHOP_ITEMS`
- Add/remove items as needed
- Customize pack contents

### Database Collections

The bot creates these collections automatically:
- `teams` - Player teams
- `matches` - Match history
- `auctions` - Regular auctions
- `legendary_auctions` - Premium auctions
- `economy` - User balances and items
- `transactions` - Coin transaction logs

---

## Troubleshooting

### Bot Not Responding
- Check if bot is online in Discord
- Verify intents are enabled
- Check console for errors
- Ensure MongoDB is connected

### Commands Not Working
- Verify command prefix is `cm`
- Check bot has permissions
- Ensure message content intent enabled
- Look for error messages

### Economy Issues
- Coins not updating: Check MongoDB connection
- Items not appearing: Verify database writes
- Leaderboard not resetting: Check task loop

### Common Errors

**"Command not found"**
- Use correct prefix: `cm` not `/`
- Check spelling: `cmhelp` not `cm help`

**"Database connection failed"**
- Verify MongoDB URI in config.py
- Check network connection
- Ensure IP is whitelisted in MongoDB

**"Missing permissions"**
- Bot needs: Send Messages, Embed Links, Attach Files
- Check role hierarchy
- Verify channel permissions

---

## Support

Need help?
- Check `cmhelp` in Discord
- Review README.md
- Check console logs for errors
- Verify all dependencies installed

---

**Quick Reference Card:**

| Action | Command |
|--------|---------|
| Start playing | `cmselectteam` → `cmplay 20 t20` |
| Daily tasks | `cmdaily` + `cmpack` |
| Check progress | `cmbal` + `cmstats` |
| Shop & items | `cmshop` → `cmbuy` → `cminventory` |
| Compete | `cmleaderboard weekly` |
| Help | `cmhelp` |

**Economy Loop:**
Play Match → Earn Coins → Buy Items → Win More → Climb Leaderboard → Get Prizes!

🏏 **Enjoy the game!** 🏏

# 🎉 Cric Mater Bot - Latest Updates

## ✨ New Admin Features Added

### 👑 Admin Commands (cmadminhelp)

**💰 Coin Management:**
- `cmgivecoins @user [amount]` - Give coins to any user
- `cmremovecoins @user [amount]` - Remove coins from a user
- `cmsetcoins @user [amount]` - Set user's exact coin balance

**👥 User Management:**
- `cmdeletexi @user` - Delete user's Playing XI (forces team reset)
- `cmban @user [reason]` - Ban user from using the bot
- `cmunban [user_id]` - Unban a user
- `cmbannedlist` - View all banned users

**🎁 Rewards:**
- `cmgiveprize @user [coins] [pack_type]` - Give prize packages
  - Pack types: bronze_pack, silver_pack, gold_pack, diamond_pack

**⚙️ Configuration:**
- `cmsetplayerprice "Player Name" [price]` - Set custom auction prices for players
- `cmdbstats` - View database statistics

**🎪 Auctions:**
- `cmauction [num]` - Start regular auction
- `cmlegendaryauction [num]` - Start legendary auction
- `cmnextbid` - Move to next player
- `cmendauction` - End current auction

---

## 🔄 Player Trading System (NEW!)

### Trade Commands

**Initiate Trade:**
```
cmtradeplayer @user "Player Name" ["Player Name"]
```
- Trade players between users (like CSK trading Jadeja to RR for Sanju Samson!)
- If second player name omitted = free transfer
- Both users must own the specified players

**Manage Trades:**
- `cmaccepttrade [trade_id]` - Accept a pending trade offer
- `cmrejecttrade [trade_id]` - Reject a trade offer
- `cmmytrades` - View all your pending trades

**Example Trade:**
```
cmtradeplayer @friend "Virat Kohli" "Rohit Sharma"
```
Friend receives Virat Kohli, you receive Rohit Sharma!

---

## 💰 Auction System Updates

### Regular Auction
- **New Purse:** ₹100 Crore (₹10,000,000,000)
- **Admin Control:** Admins can set custom player prices with `cmsetplayerprice`
- **Flexible Pricing:** Admins decide each player's value

### Legendary Auction
- **Entry Fee:** 5,000 coins (coin-based, not purse)
- **Fixed Prices:** Only developer (Neelesh) can change these!
  - 95+ Overall: ₹50 Million base price
  - 90-94 Overall: ₹30 Million base price
  - 85-89 Overall: ₹20 Million base price
  - Below 85: ₹10 Million base price
- **+10 Stat Boost:** All legendary players get +10 to batting and bowling
- **Premium Competition:** Top-rated players only

---

## 🔨 Ban System

### Automatic Ban Checking
- Bot checks every command for banned users
- Banned users cannot use ANY bot commands
- Ban message shows reason automatically

### Ban Features
- Permanent or temporary bans
- DM notifications to banned users
- Track ban reasons
- Easy unban system
- View all banned users with `cmbannedlist`

---

## 🎯 Key Changes Summary

### What Changed:
1. ✅ **Coin Gifting REMOVED** - Users can't transfer coins (prevents abuse)
2. ✅ **Player Trading ADDED** - Users can trade players (like real IPL!)
3. ✅ **Regular Auction Purse** - Increased to ₹100 Crore
4. ✅ **Admin Coin Control** - Admins can give/remove/set coins
5. ✅ **Ban System** - Complete ban management for admins
6. ✅ **Legendary Prices** - Fixed by developer, admins can't change
7. ✅ **Custom Player Prices** - Admins can set prices for regular auctions
8. ✅ **Admin Prize System** - Give coin+pack rewards easily

### What Stayed:
- ✅ Daily rewards (100 coins)
- ✅ Free daily packs
- ✅ Match rewards (1000 coins win, 250 loss)
- ✅ Shop system (boosts, consumables, packs)
- ✅ Leaderboard prizes (weekly/monthly)
- ✅ Economy tracking (balance, inventory, records)

---

## 📋 Complete Feature List

### For Players:
1. **Play Matches** - Earn 1000 coins per win + bonuses
2. **Daily Activities** - 100 coin reward + free pack daily
3. **Shop System** - Buy boosts, consumables, player packs
4. **Auctions** - Join regular (₹100cr) or legendary (5000 coins)
5. **Trading** - Trade players with other users
6. **Leaderboard** - Compete weekly/monthly for prizes
7. **Inventory** - Collect and manage player cards
8. **Records** - Track your match history

### For Admins:
1. **Coin Control** - Give, remove, or set user balances
2. **User Management** - Delete teams, ban/unban users
3. **Prize Distribution** - Award coins and packs
4. **Auction Control** - Start and manage auctions
5. **Player Pricing** - Set custom auction prices
6. **Database Stats** - Monitor bot usage
7. **Ban Management** - View and manage banned users

---

## 🚀 Usage Examples

### Admin Giving Rewards:
```
cmgivecoins @winner 5000
cmgiveprize @mvp 10000 diamond_pack
```

### Admin Managing Users:
```
cmban @cheater Caught statpadding with alt accounts
cmdeletexi @player (forces them to reselect team)
cmsetcoins @newuser 1000 (give starting bonus)
```

### Player Trading:
```
// User A wants Virat, User B wants Rohit
User A: cmtradeplayer @UserB "Rohit Sharma" "Virat Kohli"
User B: cmaccepttrade 507f1f77bcf86cd799439011
// Trade complete! Both get new players
```

### Setting Player Prices (Admin):
```
cmsetplayerprice "Jasprit Bumrah" 15000000
cmsetplayerprice "MS Dhoni" 20000000
```

---

## ⚙️ Configuration

### Legendary Auction Prices (Developer Only)
Located in `legendary_commands.py` line ~168:
```python
if overall >= 95:
    player['base_price'] = 50000000  # 50M for 95+ rated
elif overall >= 90:
    player['base_price'] = 30000000  # 30M for 90-94
elif overall >= 85:
    player['base_price'] = 20000000  # 20M for 85-89
else:
    player['base_price'] = 10000000  # 10M for others
```

**Only Neelesh (developer) should modify these values!**

### Regular Auction Budget
Located in `config.py`:
```python
AUCTION_SETTINGS = {
    'initial_budget': 10000000000,  # 100 crore (100 cr)
}
```

---

## 📊 Database Collections

### New Collections:
- `trades` - Player trade history and pending trades
- `bans` - Banned users list
- `player_prices` - Admin-set player prices

### Existing Collections:
- `economy` - User balances and items
- `teams` - User Playing XIs
- `matches` - Match history
- `auctions` - Regular auctions
- `legendary_auctions` - Legendary auctions
- `transactions` - Coin transaction logs

---

## 🎮 Command Count

**Total Commands: 35+**

- Match Commands: 3
- Stats Commands: 3
- Economy Commands: 6
- Auction Commands: 6
- Trading Commands: 4
- Admin Commands: 13+
- Help Commands: 2

---

## 🔐 Permission System

### Admin Commands Require:
- Discord Administrator permission
- Membership in ADMIN_IDS list (in config)
- Both checks must pass

### Regular Commands:
- No special permissions
- Automatically banned users blocked
- Some commands have cooldowns (daily rewards)

---

## 💡 Pro Tips

### For Admins:
1. **Give starting bonuses** to new users with `cmsetcoins`
2. **Host events** and reward winners with `cmgiveprize`
3. **Monitor economy** with `cmdbstats`
4. **Set strategic prices** for popular players
5. **Ban alt accounts** to prevent statpadding

### For Players:
1. **Play daily** for 100 coins + free pack
2. **Trade wisely** - get players you need
3. **Save 5000 coins** for legendary auctions
4. **Compete weekly** for top 3 prizes
5. **Use boosts** before important matches

---

## 🐛 Known Limitations

1. **Coin gifting disabled** - Prevents coin farming
2. **Legendary prices fixed** - Only developer can change
3. **One trade at a time** - Must accept/reject before new trade
4. **Ban is server-wide** - Affects all bot commands

---

## 🎊 What Makes This Special

### Real IPL Experience:
- Trade players like real IPL teams
- Auction with ₹100 crore purse
- Multiple player rarities (common to legendary)
- Performance-based coin rewards

### Complete Admin Control:
- Full coin management
- User bans and team resets
- Custom player pricing
- Easy prize distribution

### Balanced Economy:
- No coin gifting (prevents abuse)
- Player trading only (builds strategy)
- Fixed legendary prices (fair competition)
- Multiple earning methods (matches, daily, leaderboard)

---

## 📞 Support

### For Players:
- Use `cmhelp` for command list
- Check `cmadminhelp` for admin commands
- DM bot for team selection

### For Admins:
- All admin commands in `cmadminhelp`
- Check database with `cmdbstats`
- View bans with `cmbannedlist`

---

## 🚀 Ready to Use!

All features are implemented and tested. Just:

1. **Update your config.py** with bot token and MongoDB URI
2. **Add your Discord ID** to ADMIN_IDS
3. **Run the bot:** `python bot.py`
4. **Invite to server** with proper permissions
5. **Start using admin commands!**

---

**Made with ❤️ by Neelesh**

*Trade Players. Win Matches. Dominate Leaderboards.*

🏏 **The Ultimate Discord Cricket Gaming Platform** 🏏

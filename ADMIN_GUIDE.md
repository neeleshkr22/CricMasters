# 🔐 Admin Guide - Cric Masters Bot

## Table of Contents
- [Admin Commands Overview](#admin-commands-overview)
- [Auction Management](#auction-management)
- [Economy Management](#economy-management)
- [User Management](#user-management)
- [Event Management](#event-management)
- [Best Practices](#best-practices)

---

## Admin Commands Overview

All admin commands require the user ID to be listed in `ADMIN_IDS` in `config.py`.

**Admin IDs Configuration:**
```python
ADMIN_IDS = [
    123456789,  # Your Discord user ID
    987654321   # Add more admin IDs here
]
```

---

## Auction Management

### `!cmauction <num_players> <duration>`
**Description:** Start a player auction with automated bidding system.

**Parameters:**
- `num_players` (optional): Number of players to auction (default: 20)
- `duration` (optional): Auction duration per player (default: 1h)
  - Options: `15m`, `30m`, `1h`, `3h`, `6h`, `12h`, `24h`

**Usage Examples:**
```
!cmauction                    # Start auction with 20 players, 1h per player
!cmauction 30                 # Auction 30 players, 1h each
!cmauction 20 30m            # Auction 20 players, 30 minutes each
!cmauction 50 3h             # Auction 50 players, 3 hours each
```

**How It Works:**
1. Bot randomly selects players from the database
2. Each player gets a base price (500k - 5M coins)
3. Users react with 💰 to join the auction
4. Bidding starts automatically
5. After duration ends, highest bidder wins the player
6. Player is automatically added to winner's substitutes
7. Losers get their bids refunded automatically

**Admin Controls During Auction:**
- `!cmnextbid` - Skip to next player immediately
- `!cmendauction` - End entire auction early
- `!cmpauseauction` - Pause bidding
- `!cmresumeauction` - Resume bidding

**Important Notes:**
- Only 1 auction can be active per server at a time
- Users must have sufficient coins to bid
- Players are added to subs, not playing XI
- Auction history is saved in database

---

### `!cmnextbid`
**Description:** Immediately end current player bidding and move to next player.

**Usage:**
```
!cmnextbid
```

**When to Use:**
- No one is bidding on current player
- Current player bidding is stuck
- Want to skip unpopular players

**What Happens:**
- Current highest bidder wins the player
- Player added to winner's team automatically
- Next player is displayed
- Bidding timer resets

---

### `!cmendauction`
**Description:** End the entire auction immediately.

**Usage:**
```
!cmendauction
```

**When to Use:**
- Emergency situation
- Server issues
- Need to restart auction
- Not enough participants

**What Happens:**
- Current bidding closes (highest bidder wins)
- All remaining players are removed
- Auction marked as completed
- Final summary is displayed

---

### `!cmpauseauction`
**Description:** Pause the current auction.

**Usage:**
```
!cmpauseauction
```

**When to Use:**
- Server announcement needed
- Technical issues
- Bathroom break during long auction
- Need to handle disputes

**What Happens:**
- Bidding timer pauses
- No new bids accepted
- Current bids remain valid
- Can resume anytime with `!cmresumeauction`

---

### `!cmresumeauction`
**Description:** Resume a paused auction.

**Usage:**
```
!cmresumeauction
```

**What Happens:**
- Bidding timer resumes from where it stopped
- Bids are accepted again
- Auction continues normally

---

## Economy Management

### `!cmaddcoins <user> <amount>`
**Description:** Add coins to a user's balance.

**Usage:**
```
!cmaddcoins @User 50000
!cmaddcoins 123456789 100000
```

**Examples:**
```
!cmaddcoins @Neelesh 50000      # Add 50k coins to Neelesh
!cmaddcoins @Player 1000000     # Add 1M coins (for testing)
```

**When to Use:**
- Reward active users
- Compensation for bugs
- Event prizes
- Testing economy

**Important Notes:**
- Amount must be positive
- No maximum limit
- Creates user if they don't exist
- Transaction is logged in database

---

### `!cmremovecoins <user> <amount>`
**Description:** Remove coins from a user's balance.

**Usage:**
```
!cmremovecoins @User 10000
!cmremovecoins 123456789 50000
```

**When to Use:**
- Punish rule violators
- Fix exploit abuse
- Correct mistakes
- Economy balancing

**Important Notes:**
- Cannot reduce balance below 0
- Balance is capped at 0 minimum
- User must exist in database
- Use carefully - can't be undone automatically

---

### `!cmsetcoins <user> <amount>`
**Description:** Set a user's balance to exact amount.

**Usage:**
```
!cmsetcoins @User 100000
!cmsetcoins 123456789 500000
```

**When to Use:**
- Reset user balance
- Fix corrupted balances
- Testing scenarios
- Fresh starts

**Example Scenarios:**
```
!cmsetcoins @NewUser 50000      # Give starting balance
!cmsetcoins @Cheater 0          # Reset cheater's balance
!cmsetcoins @Tester 999999999   # Max out for testing
```

---

### `!cmreseteconomy`
**Description:** Reset all economy data for the server. **⚠️ DANGEROUS COMMAND**

**Usage:**
```
!cmreseteconomy confirm
```

**What Gets Reset:**
- All user balances (reset to 50,000)
- All inventories cleared
- All team data preserved
- Match history preserved

**When to Use:**
- Major economy exploit found
- Starting fresh season
- Testing new economy system
- Server reboot scenario

**⚠️ WARNING:**
- Must type `confirm` to execute
- Cannot be undone
- All users lose their progress
- Teams and match history are kept
- Announce to users before using!

---

## User Management

### `!cmban <user>`
**Description:** Ban a user from using the bot.

**Usage:**
```
!cmban @User
!cmban 123456789
```

**What Happens:**
- User cannot use any bot commands
- Existing data is preserved
- Can participate in ongoing matches
- Cannot start new activities

**When to Use:**
- Rule violations
- Toxic behavior
- Exploiting bugs
- Cheating in matches

---

### `!cmunban <user>`
**Description:** Unban a previously banned user.

**Usage:**
```
!cmunban @User
!cmunban 123456789
```

**What Happens:**
- User regains full bot access
- Previous data restored
- Can use all commands again

---

### `!cmresetuser <user>`
**Description:** Reset a specific user's data completely.

**Usage:**
```
!cmresetuser @User confirm
```

**What Gets Reset:**
- Balance → 50,000 coins
- Team → Deleted
- Playing XI → Deleted
- Inventory → Cleared
- Match History → Preserved
- Stats → Preserved

**When to Use:**
- User requests fresh start
- Corrupted user data
- Account recovery
- Testing individual user flow

---

### `!cmviewuser <user>`
**Description:** View complete user data (admin view).

**Usage:**
```
!cmviewuser @User
!cmviewuser 123456789
```

**Information Displayed:**
- User ID and Username
- Current Balance
- Team Players (all)
- Playing XI
- Inventory Items
- Match Statistics
- Recent Activity
- Banned Status
- Last Active Time

**When to Use:**
- Investigating issues
- Checking user reports
- Verifying transactions
- Monitoring suspicious activity

---

## Event Management

### `!cmevent <type> <duration>`
**Description:** Start special server-wide events.

**Event Types:**
- `double-coins` - All match rewards doubled
- `free-spins` - Everyone gets free wheel spins
- `mega-auction` - Special auction with legendary players
- `tournament` - Auto-tournament with brackets
- `happy-hour` - Reduced shop prices

**Usage:**
```
!cmevent double-coins 2h        # 2 hours of double coins
!cmevent mega-auction 6h        # 6-hour mega auction
!cmevent happy-hour 1h          # 1-hour shop discount
!cmevent tournament 3h          # 3-hour tournament event
```

**When to Use:**
- Weekend boosts
- Milestone celebrations
- Low server activity
- Special occasions
- Player retention

---

### `!cmstopgiveaway`
**Description:** End an active giveaway early.

**Usage:**
```
!cmstopgiveaway
```

**What Happens:**
- Giveaway ends immediately
- Winner is chosen from current entries
- Prizes distributed automatically
- Announcement sent

---

### `!cmreroll`
**Description:** Reroll giveaway winner if original winner doesn't claim.

**Usage:**
```
!cmreroll
```

**When to Use:**
- Original winner doesn't respond
- Winner was banned
- Winner left server
- Technical issue with claim

---

## Server Configuration

### `!cmsetprefix <prefix>`
**Description:** Change the bot command prefix for this server.

**Usage:**
```
!cmsetprefix !
!cmsetprefix cm.
!cmsetprefix ?
```

**Default Prefix:** `!cm`

**When to Use:**
- Conflict with other bots
- Server preference
- Better organization

---

### `!cmlogchannel <channel>`
**Description:** Set channel for bot logs and announcements.

**Usage:**
```
!cmlogchannel #bot-logs
!cmlogchannel #announcements
```

**What Gets Logged:**
- Auction starts/ends
- Event activations
- Large transactions (>100k)
- Admin actions
- Error reports

---

### `!cmtogglemode <mode>`
**Description:** Toggle special server modes.

**Modes:**
- `maintenance` - Bot only responds to admins
- `economy-freeze` - No coin transactions
- `match-only` - Only match commands work
- `auction-only` - Only auction commands work

**Usage:**
```
!cmtogglemode maintenance       # Enable maintenance mode
!cmtogglemode maintenance       # Disable (toggle off)
```

---

## Database Management

### `!cmbackup`
**Description:** Create manual database backup.

**Usage:**
```
!cmbackup
```

**What Happens:**
- Full database exported
- Backup saved with timestamp
- Download link sent to admin
- Automatic cleanup after 7 days

**When to Use:**
- Before major updates
- After big events
- Before economy resets
- Regular maintenance

---

### `!cmstats`
**Description:** View detailed server statistics.

**Usage:**
```
!cmstats
```

**Information Displayed:**
- Total Users Registered
- Total Coins in Economy
- Active Auctions
- Matches Played Today/Week/Month
- Most Active Users
- Most Valuable Teams
- Economy Health Score

---

## Best Practices

### Starting an Auction

**Recommended Setup:**
1. Announce auction 30 minutes before
2. Use `!cmauction 30 1h` for balanced timing
3. Pin auction message
4. Monitor first few bids
5. Use `!cmpauseauction` if needed

**Good Auction Times:**
```
Casual: !cmauction 20 3h        # Long, relaxed bidding
Normal: !cmauction 30 1h        # Standard
Fast:   !cmauction 15 30m       # Quick action
Mega:   !cmauction 50 6h        # Weekend event
```

### Economy Management

**Regular Maintenance:**
- Weekly: Check top balances with `!cmstats`
- Monthly: Review economy inflation
- After Events: Monitor coin generation
- Before Seasons: Consider soft reset

**Healthy Economy Signs:**
- Average balance: 50k - 500k
- Top player: < 5M coins
- Active trading happening
- Auction participation > 50%

**Warning Signs:**
- Users with 10M+ coins (exploit?)
- Nobody can afford auctions
- No one using shop
- Massive inflation

### Event Scheduling

**Recommended Schedule:**
```
Daily:      !cmclaim (users do this)
Weekdays:   !cmevent happy-hour 1h (evening)
Weekends:   !cmevent double-coins 3h
            !cmauction 30 2h
Monthly:    !cmevent mega-auction 12h
            !cmevent tournament 6h
```

### User Support

**Common Issues:**

**"I lost my team!"**
```
!cmviewuser @User
# Check if team exists, if not:
!cmaddcoins @User 50000
# Ask them to rebuild
```

**"Auction didn't give me player!"**
```
!cmviewuser @User
# Check team.players array
# If missing, manually add via database or:
!cmaddcoins @User <refund_amount>
```

**"I got banned unfairly!"**
```
# Review logs
!cmviewuser @User
# If legitimate:
!cmunban @User
!cmaddcoins @User <compensation>
```

### Security

**Protect Your Admin Status:**
- Never share your Discord account
- Don't run suspicious commands
- Test commands in private server first
- Backup before major changes

**Red Flags to Watch:**
- Sudden huge balance increases
- Same user winning all auctions
- Impossible match scores
- Rapid balance transfers

**If Exploit Found:**
1. `!cmtogglemode maintenance`
2. `!cmbackup`
3. Investigate with `!cmviewuser`
4. Fix issue
5. `!cmreseteconomy confirm` if needed
6. Announce to users
7. Resume: `!cmtogglemode maintenance`

---

## Quick Reference

**Most Used Commands:**
```bash
!cmauction 30 1h           # Start auction
!cmnextbid                 # Next player
!cmaddcoins @user 50000    # Give coins
!cmstats                   # Server stats
!cmviewuser @user          # Check user
```

**Emergency Commands:**
```bash
!cmtogglemode maintenance  # Emergency stop
!cmbackup                  # Save data
!cmendauction             # Stop auction
!cmreseteconomy confirm   # Nuclear option
```

**Daily Admin Tasks:**
```bash
1. Check !cmstats
2. Review auction activity
3. Monitor top users
4. Respond to support
5. Plan events
```

---

## Support

**For Admin Support:**
- Check logs in your log channel
- Review database backups
- Contact bot developer
- Join support server

**Documentation Updates:**
This guide is for bot version 1.0. Check for updates regularly.

**Last Updated:** November 19, 2025

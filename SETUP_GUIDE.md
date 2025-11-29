# 🚀 Quick Start Guide - Cric Mater Bot

## 📋 Prerequisites Checklist

Before running the bot, make sure you have:

- [ ] Python 3.8+ installed
- [ ] Discord account
- [ ] MongoDB Atlas account (free tier is fine)
- [ ] Text editor (VS Code recommended)

## 🔧 Step-by-Step Setup

### Step 1: Install Python Packages

Open PowerShell in this directory and run:

```powershell
pip install -r requirements.txt
```

Wait for all packages to install successfully.

### Step 2: Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Give it a name (e.g., "Cric Mater")
4. Go to "Bot" tab on the left
5. Click "Add Bot"
6. Click "Reset Token" and copy the token
7. **Important**: Enable these intents:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
8. Save Changes

### Step 3: Setup MongoDB

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create a free M0 cluster
4. Click "Connect" → "Connect your application"
5. Copy the connection string
6. Replace `<password>` with your database password
7. Replace `<dbname>` with `cricketbot`

### Step 4: Configure Bot

1. Open the `.env` file in this folder
2. Replace the values:

```env
DISCORD_TOKEN=paste_your_bot_token_here
MONGODB_URI=paste_your_mongodb_connection_string_here
ADMIN_IDS=your_discord_user_id_here
```

**To get your Discord User ID:**
- Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
- Right-click your name → Copy ID

### Step 5: Invite Bot to Server

1. Go back to Discord Developer Portal
2. Go to "OAuth2" → "URL Generator"
3. Select scopes:
   - ✅ bot
   - ✅ applications.commands
4. Select bot permissions:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Add Reactions
   - ✅ Use External Emojis
5. Copy the generated URL
6. Paste in browser and invite to your server

### Step 6: Run the Bot

In PowerShell, run:

```powershell
python bot.py
```

You should see:
```
✅ Logged in as Cric Mater (ID)
📊 Connected to X servers
✅ Connected to MongoDB
✅ Loaded cogs.cricket_commands
✅ Loaded cogs.admin_commands
✅ Loaded cogs.auction_commands
🎮 Bot is ready!
```

## 🎮 First Commands to Try

In your Discord server:

1. **Check if bot is working**:
   ```
   cmhelp
   ```

2. **Create your team**:
   ```
   cmselectteam
   ```
   Follow the DM instructions to select 11 players

3. **View your team**:
   ```
   cmteam
   ```

4. **Start a match**:
   ```
   cmplay 20 t20
   ```

5. **(Admin) Start an auction**:
   ```
   cmauction 20
   ```

## ❗ Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'discord'"
**Solution**: Run `pip install -r requirements.txt`

### Issue: "discord.errors.LoginFailure: Improper token"
**Solution**: Check your DISCORD_TOKEN in .env file

### Issue: "ServerSelectionTimeoutError" (MongoDB)
**Solution**: 
- Check your MongoDB connection string
- Make sure your IP is whitelisted in MongoDB Atlas (Network Access)
- Try adding `0.0.0.0/0` to allow all IPs

### Issue: Bot doesn't respond to commands
**Solution**:
- Make sure bot has "Send Messages" permission
- Check if "Message Content Intent" is enabled
- Verify bot is online (green status)

### Issue: Can't receive DMs for team selection
**Solution**: Enable DMs in your Discord privacy settings for that server

### Issue: Images not generating properly
**Solution**: 
- Make sure Pillow is installed: `pip install Pillow`
- On some systems, you may need to install: `pip install Pillow --upgrade`

## 🎯 Testing Checklist

After setup, test these features:

- [ ] Bot comes online
- [ ] `cmhelp` shows commands
- [ ] `cmselectteam` sends DM
- [ ] Team selection works
- [ ] `cmteam` shows your team with image
- [ ] `cmplay` starts a match
- [ ] Scoreboard images generate
- [ ] Match simulation works
- [ ] Stats are saved to database

## 📞 Need Help?

If you're stuck:
1. Check the README.md file
2. Verify all environment variables are correct
3. Make sure all prerequisites are installed
4. Check bot permissions in Discord
5. Review error messages in the console

## 🎉 You're All Set!

Your Cric Mater bot is now ready to host amazing cricket matches!

**Pro Tips:**
- Create a dedicated channel for matches
- Set up roles for regular players
- Host tournaments with prizes
- Use auctions to build dream teams

**Enjoy and may the best team win! 🏏🏆**

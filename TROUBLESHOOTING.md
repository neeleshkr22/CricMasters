# 🔧 Cric Mater Bot - Troubleshooting Guide

## 🚨 Common Errors & Solutions

### 1. Bot Won't Start

#### Error: "ModuleNotFoundError: No module named 'discord'"
**Cause**: Discord.py not installed
**Solution**:
```powershell
pip install -r requirements.txt
```

#### Error: "ModuleNotFoundError: No module named 'motor'"
**Cause**: MongoDB driver not installed
**Solution**:
```powershell
pip install motor pymongo dnspython
```

#### Error: "discord.errors.LoginFailure: Improper token"
**Cause**: Invalid or missing Discord bot token
**Solution**:
1. Check `.env` file exists
2. Verify DISCORD_TOKEN is correct
3. Make sure no extra spaces or quotes
4. Get new token from Discord Developer Portal if needed

---

### 2. Database Issues

#### Error: "ServerSelectionTimeoutError"
**Cause**: Can't connect to MongoDB
**Solutions**:
1. Check MONGODB_URI in `.env`
2. Verify MongoDB cluster is running
3. Add your IP to MongoDB Network Access:
   - Go to MongoDB Atlas
   - Network Access → Add IP Address
   - Add `0.0.0.0/0` to allow all (for testing)
4. Check if connection string includes password

#### Error: "Authentication failed"
**Cause**: Wrong MongoDB credentials
**Solution**:
1. Reset MongoDB user password
2. Update connection string in `.env`
3. Make sure to replace `<password>` with actual password

---

### 3. Bot Permission Issues

#### Bot doesn't respond to commands
**Causes & Solutions**:

1. **Missing Message Content Intent**:
   - Go to Discord Developer Portal
   - Your Application → Bot
   - Enable "Message Content Intent"
   - Restart bot

2. **Missing Channel Permissions**:
   - Right-click channel → Edit Channel
   - Permissions → Bot role
   - Enable: Read Messages, Send Messages, Embed Links, Attach Files

3. **Wrong Prefix**:
   - Make sure you use `cm` prefix
   - Example: `cmhelp` not `!help`

---

### 4. Team Selection Issues

#### Can't receive DMs for team selection
**Cause**: DMs disabled
**Solution**:
1. Right-click server name
2. Privacy Settings
3. Enable "Allow direct messages from server members"

#### Team selection times out
**Cause**: Took too long to respond
**Solution**:
- Redo `cmselectteam`
- Have player numbers ready
- Respond within 120 seconds

---

### 5. Image Generation Issues

#### Images not displaying
**Causes & Solutions**:

1. **Pillow not installed**:
   ```powershell
   pip install Pillow --upgrade
   ```

2. **Font issues on Windows**:
   - Bot uses Arial font
   - Should work on all Windows systems
   - If issues, bot falls back to default font

3. **Memory issues**:
   - Restart bot
   - Check system resources

#### Images look wrong
**Cause**: Font or image library issue
**Solution**:
```powershell
pip uninstall Pillow
pip install Pillow
```

---

### 6. Match Issues

#### Match gets stuck
**Causes**:
- Network timeout
- Database connection lost
- Bot crashed

**Solutions**:
1. **As Admin**:
   ```
   cmclearmatches
   ```
2. Restart the bot
3. Start new match

#### Can't join match
**Cause**: Match already has 2 players
**Solution**: Start a new match

---

### 7. Auction Issues

#### Can't place bid
**Causes & Solutions**:

1. **Not registered**:
   ```
   cmjoinauction
   ```

2. **Insufficient budget**:
   - Check your remaining budget
   - Can't bid more than you have

3. **Bid too low**:
   - Must be higher than current bid
   - Minimum increment: $500,000

#### Auction stuck
**Cause**: Admin needs to move to next player
**Solution** (Admin):
```
cmnextbid
```

---

### 8. Command Errors

#### "Missing required argument"
**Cause**: Command needs more information
**Solution**: Check command usage
```
cmplay [overs] [type]
cmplay 20 t20
```

#### "You don't have permission"
**Cause**: Admin-only command
**Solution**: 
- Add your Discord ID to ADMIN_IDS in `.env`
- Or ask an admin to run the command

---

### 9. Performance Issues

#### Bot is slow
**Causes & Solutions**:

1. **Database lag**:
   - Use closer MongoDB region
   - Upgrade to paid tier (if needed)

2. **Too many matches**:
   ```
   cmclearmatches
   ```

3. **Image generation slow**:
   - Normal, images take 1-2 seconds
   - Be patient

#### Bot crashes
**Solutions**:
1. Check console for errors
2. Restart bot
3. Check system resources
4. Update dependencies:
   ```powershell
   pip install --upgrade -r requirements.txt
   ```

---

### 10. Setup Issues

#### Can't find .env file
**Solution**:
1. Create new file named `.env` (with the dot)
2. Copy content from `.env.example`
3. Fill in your values

#### Python version too old
**Requirement**: Python 3.8+
**Check version**:
```powershell
python --version
```
**Solution**: Download latest Python from python.org

#### Bot token not working
**Solution**:
1. Go to Discord Developer Portal
2. Your Application → Bot
3. Reset Token
4. Copy new token to `.env`
5. Never share token publicly!

---

## 🔍 Debugging Tips

### 1. Check Bot Console
- Read error messages carefully
- Most errors tell you what's wrong
- Google the error message

### 2. Enable Debug Logging
Add to bot.py (temporarily):
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. Test Components
Test each part individually:
```python
# Test database connection
from database.db import db
import asyncio
asyncio.run(db.connect())
```

### 4. Verify Environment
```powershell
# Check Python
python --version

# Check packages
pip list

# Check MongoDB
# Try connecting with MongoDB Compass
```

---

## 📞 Still Having Issues?

### Before Asking for Help:

1. ✅ Read error message completely
2. ✅ Check this troubleshooting guide
3. ✅ Verify all setup steps completed
4. ✅ Try restarting bot
5. ✅ Check .env file has correct values

### When Asking for Help, Include:

- **Error message** (full text)
- **What you were doing** (command used)
- **Bot console output**
- **Python version**
- **Operating system**

### Check These First:

- [ ] .env file exists and has values
- [ ] Discord token is valid
- [ ] MongoDB connection string is correct
- [ ] All packages installed
- [ ] Bot has correct permissions
- [ ] Message Content Intent enabled

---

## 🎯 Quick Fixes

### Reset Everything:
```powershell
# Reinstall packages
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Clear Python cache
Remove-Item -Recurse -Force __pycache__
```

### Fresh Start:
1. Delete `.env`
2. Copy from `.env.example`
3. Fill in values carefully
4. Restart bot

### Database Reset:
1. Go to MongoDB Atlas
2. Browse Collections
3. Delete all documents (if needed)
4. Bot will recreate on next use

---

## ✅ Health Check

Run these commands to verify bot is working:

1. `cmhelp` - Bot responds
2. `cmselectteam` - Gets DM
3. `cmteam` - Shows image
4. `cmstats` - Shows stats
5. `cmleaderboard` - Shows leaderboard

If all work, bot is healthy! 🎉

---

## 🚀 Performance Tips

1. **Use good internet connection**
2. **Keep bot running on stable server**
3. **Don't run multiple instances**
4. **Clear old matches regularly**
5. **Monitor database size**
6. **Update packages monthly**

---

## 📚 Additional Resources

- **Discord.py Docs**: https://discordpy.readthedocs.io/
- **MongoDB Docs**: https://docs.mongodb.com/
- **Python Docs**: https://docs.python.org/

---

**Remember**: Most issues are simple configuration problems. Take your time and check each step carefully! 🔧✨

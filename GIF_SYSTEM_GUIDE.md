# 🎬 Cricket Bot GIF Celebration System

## Multi-GIF Support for Players

Players can now have **multiple celebration GIFs** - the bot will randomly select one each time!

## How It Works

### 📁 File Structure
- **Location**: `data/celebration_gifs.json`
- **Manager**: `utils/celebration_manager.py`

### ✨ Features
- 🎲 **Random Selection**: Multiple GIFs per player = variety!
- 🌟 **Player-Specific**: Each player has their own celebrations
- 🔄 **Fallback System**: Default GIFs used if player not found
- 🌍 **World Players**: Pre-loaded with top international cricketers

---

## 📋 GIF Categories

### 1. Wicket Celebrations (`wicket_celebrations`)
For bowlers taking wickets:
- **Players Included**: Bumrah (3 GIFs), Starc (2), Rashid Khan, Boult, Cummins, Rabada, Shaheen, Shami, Chahal, Kuldeep, Archer
- **Usage**: Shown when a bowler takes a wicket

### 2. Century Celebrations (`century_celebrations`)
For batsmen scoring 100+ runs:
- **Players Included**: 
  - Virat Kohli (5 GIFs!) - Kiss celebration, roar, 100 gesture
  - Rohit Sharma (3 GIFs)
  - Babar Azam, Joe Root, Kane Williamson, Steve Smith, David Warner
  - AB de Villiers (3 GIFs including superman!)
  - MS Dhoni, Ben Stokes, KL Rahul, Quinton de Kock, Rishabh Pant
- **Usage**: Shown when a batsman reaches 100 runs

### 3. Fifty Celebrations (`fifty_celebrations`)
For batsmen scoring 50-99 runs:
- **Players Included**: Kohli (2), Rohit (2), Warner (2), KL Rahul, Buttler (2), Babar, Dhawan
- **Usage**: Shown when a batsman reaches 50 runs

### 4. Six Celebrations (`six_celebrations`)
For hitting sixes (most variety!):
- **Players Included**:
  - MS Dhoni (4 GIFs!) - Helicopter shot variations
  - Chris Gayle (4 GIFs!) - Universe Boss power
  - AB de Villiers (3 GIFs) - 360° shots, superman
  - Andre Russell (2), Hardik Pandya (2), Rohit (2), Kohli (2)
  - Glenn Maxwell (2) - Switch hit!
  - Suryakumar Yadav (2), Kieron Pollard, Rishabh Pant
- **Usage**: Shown when a six is hit

### 5. Four Celebrations (`four_celebrations`)
For hitting fours:
- **Players Included**: Kohli (2) cover drives, Kane, Root, Babar (2), Sachin
- **Usage**: Shown when a four is hit

### 6. Match Events
- **Match Win** (`match_win`): Team celebrations (India, Australia, England, Pakistan)
- **Match Start** (`match_start`): Toss, match beginning (3 variations)
- **Hat-Trick** (`hat_trick`): 3 wickets in 3 balls (2 variations)
- **Duck Out** (`duck_out`): Out on 0 runs (2 variations)
- **Super Over** (`super_over`): Tie-breaker scenarios (2 variations)

---

## 🎯 How to Add More GIFs

### Method 1: Edit JSON Directly

```json
"Virat Kohli": [
  "https://media.tenor.com/first-gif.gif",
  "https://media.tenor.com/second-gif.gif",
  "https://media.tenor.com/third-gif.gif"
]
```

### Method 2: Add Single GIF for New Player

```json
"Shubman Gill": "https://media.tenor.com/gill-celebration.gif"
```

### Method 3: Use the Manager (in code)

```python
from utils.celebration_manager import celebration_manager

# Add a GIF to existing player (converts to array automatically)
celebration_manager.add_player_gif(
    "century_celebrations",
    "Virat Kohli",
    "https://media.tenor.com/new-kohli-century.gif"
)
```

---

## 🔍 Finding GIF URLs

### Best Sources
1. **Tenor**: https://tenor.com
   - Search: "virat kohli century celebration cricket"
   - Right-click GIF → Copy link address
   - Use the `.gif` URL (not the page URL)

2. **Giphy**: https://giphy.com
   - Search for player celebrations
   - Click "Copy Link" → Get GIF URL
   - Example: `https://media.giphy.com/media/ID/giphy.gif`

### Search Tips
- Use specific terms: `"player name" + "century" + "celebration" + "cricket"`
- Try variations: wicket, six, hundred, 100, fifty, 50
- Filter by: Sports, Cricket, IPL, World Cup

---

## 💡 Pro Tips

### Variety is Key
- **Virat Kohli**: 5 century GIFs for maximum variety
- **MS Dhoni**: 4 six GIFs (different helicopter shots)
- **Chris Gayle**: 4 six GIFs (Universe Boss power moments)

### Fallback System
```json
"default": ["https://media.giphy.com/media/generic-celebration.gif"]
```
- Always include a `default` array
- Used when player not found
- Can have multiple default GIFs too!

### Performance
- GIFs load from cache after first use
- Random selection happens instantly
- No performance impact from multiple GIFs

---

## 🎮 Usage in Match Simulation

The celebration manager is automatically used during matches:

```python
from utils.celebration_manager import celebration_manager

# When wicket is taken
gif_url = celebration_manager.get_wicket_gif("Jasprit Bumrah")
# Returns random GIF from Bumrah's 3 wicket celebrations

# When century is scored
gif_url = celebration_manager.get_century_gif("Virat Kohli")
# Returns random GIF from Kohli's 5 century celebrations

# When six is hit
gif_url = celebration_manager.get_six_gif("MS Dhoni")
# Returns random GIF from Dhoni's 4 six celebrations (including helicopter!)
```

---

## 🌟 Current Statistics

### Total Players with GIFs: **40+**

**Category Breakdown:**
- 🎯 Wicket Celebrations: 11 bowlers
- 💯 Century Celebrations: 13 batsmen (Kohli has 5!)
- 5️⃣0️⃣ Fifty Celebrations: 7 batsmen
- 6️⃣ Six Celebrations: 11 batsmen (Dhoni & Gayle have 4 each!)
- 4️⃣ Four Celebrations: 5 batsmen

**Total GIFs in Database: 85+**

---

## 🎨 Customization Examples

### Add an Emerging Player
```json
"Shubman Gill": [
  "https://media.tenor.com/gill-century-1.gif",
  "https://media.tenor.com/gill-century-2.gif"
]
```

### Add More to Existing Player
Just add to their array:
```json
"Virat Kohli": [
  "https://media.tenor.com/existing-1.gif",
  "https://media.tenor.com/existing-2.gif",
  "https://media.tenor.com/NEW-GIF-HERE.gif"  // <- Add more!
]
```

### Add Team-Specific Win Celebrations
```json
"match_win": {
  "Mumbai Indians": [
    "https://media.tenor.com/mi-celebration-1.gif",
    "https://media.tenor.com/mi-celebration-2.gif"
  ],
  "Chennai Super Kings": [
    "https://media.tenor.com/csk-celebration.gif"
  ]
}
```

---

## 🚀 Future Enhancements

Ideas for expansion:
- [ ] Add more players (Rashid Khan, Shaheen Afridi, etc.)
- [ ] Team-specific celebrations (MI, CSK, RCB)
- [ ] Special event GIFs (IPL wins, World Cup moments)
- [ ] Animated scorecard overlays
- [ ] Player-specific emojis

---

## 🎬 Example: Virat Kohli's 5 Century Celebrations

When Kohli scores a century, one of these is randomly shown:
1. 🎥 Kissing the wedding ring
2. 🎥 Aggressive roar at crowd
3. 🎥 Bat raised, helmet off celebration
4. 🎥 Arms spread celebration
5. 🎥 Pointing to sky tribute

**This creates dynamic, non-repetitive match experiences!**

---

## 📞 Support

To add your own GIFs:
1. Find GIF on Tenor/Giphy
2. Copy the direct `.gif` URL
3. Add to `celebration_gifs.json`
4. Restart bot to reload

**That's it! Enjoy the celebrations! 🎉**

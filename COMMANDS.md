# CricMasters Bot Admin Commands Reference

This document lists all admin commands available in the CricMasters Discord bot, with usage examples and their purpose.

---

## Coin Management

- **cmgivecoins @user [amount]**
  - *Purpose*: Give coins to a user.
  - *Usage*: `cmgivecoins @username 10000`

- **cmremovecoins @user [amount]**
  - *Purpose*: Remove coins from a user.
  - *Usage*: `cmremovecoins @username 5000`

- **cmsetcoins @user [amount]**
  - *Purpose*: Set a user's coin balance.
  - *Usage*: `cmsetcoins @username 20000`

---

## User Management

- **cmsetteam [@user]**
  - *Purpose*: Create a default team for any user.
  - *Usage*: `cmsetteam @username` or `cmsetteam` (for yourself)

- **cmdeletexi @user**
  - *Purpose*: Delete a user's Playing XI.
  - *Usage*: `cmdeletexi @username`

- **cmban @user [reason]**
  - *Purpose*: Ban a user from the bot.
  - *Usage*: `cmban @username Spamming`

- **cmunban [user_id]**
  - *Purpose*: Unban a user.
  - *Usage*: `cmunban 123456789012345678`

- **cmbannedlist**
  - *Purpose*: View all banned users.
  - *Usage*: `cmbannedlist`

---

## Rewards & Giveaways

- **cmgiveprize @user [coins] [pack]**
  - *Purpose*: Give a prize package to a user.
  - *Usage*: `cmgiveprize @username 5000 gold_pack`

- **cmgiveaway [winners] [players]**
  - *Purpose*: Start a player giveaway (30s).
  - *Usage*: `cmgiveaway 3 5` (3 winners, 5 players each)

---

## Configuration

- **cmsetplayerprice "Name" [price]**
  - *Purpose*: Set a player's auction price.
  - *Usage*: `cmsetplayerprice "Virat Kohli" 1000000`

- **cmdbstats**
  - *Purpose*: View database statistics.
  - *Usage*: `cmdbstats`

---

## Auctions

- **cmauction [num] [duration]**
  - *Purpose*: Start regular auction.
  - *Usage*: `cmauction 20 1h`

- **cmlegendaryauction [num]**
  - *Purpose*: Start legendary auction.
  - *Usage*: `cmlegendaryauction 10`

- **cmnextbid**
  - *Purpose*: Move to next player in auction.
  - *Usage*: `cmnextbid`

- **cmendauction**
  - *Purpose*: End current auction.
  - *Usage*: `cmendauction`

- **cmaddplayerauction "Player 1" "Player 2" ...**
  - *Purpose*: Add specific players to the current auction.
  - *Usage*: `cmaddplayerauction "Virat Kohli" "MS Dhoni"`

---

## Other Useful Admin Commands

- **setplayerovr <player_id_or_name> <ovr>**
  - *Purpose*: Set a player's OVR by adjusting stats.
  - *Usage*: `cmsetplayerovr bat_0001 92.5`

- **setovr <bat|bowl|ovr> <value> <player name or id>**
  - *Purpose*: Flexible OVR/stats setter.
  - *Usage*: `cmsetovr bowl 98 bumrah`

- **revertplayerovr <player_id_or_name>**
  - *Purpose*: Revert any persistent OVR override for a player.
  - *Usage*: `cmrevertplayerovr bat_0001`

---

## Help

- **adminhelp**
  - *Purpose*: Show all admin commands.
  - *Usage*: `adminhelp`

---

*All commands require Administrator permission. Use responsibly!*

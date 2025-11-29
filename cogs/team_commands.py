"""
Team Commands - Manage teams and playing XI
"""
import discord
from discord.ext import commands
import asyncio

from config import COLORS
from database.db import db
from data.players import PLAYERS_DATABASE, get_player_by_id
from utils.image_generator import image_gen


class TeamCommands(commands.Cog):
    """Team management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='debut', aliases=['start', 'register', 'begin'])
    async def debut_command(self, ctx):
        """
        Start your cricket journey
        Usage: !cmdebut
        """
        user_id = str(ctx.author.id)
        
        existing_user = await db.get_economy_user(user_id)
        
        if existing_user:
            embed = discord.Embed(
                title="⚠️ Already Registered!",
                description=f"Welcome back, **{ctx.author.name}**!\n\nYou're already part of Cric Masters.",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="💰 Your Balance",
                value=f"{existing_user.get('coins', 0):,} coins",
                inline=True
            )
            embed.add_field(
                name="🏆 Matches",
                value=f"{existing_user.get('matches_played', 0)} played",
                inline=True
            )
            embed.set_footer(text="Use !cmhelp to see all commands")
            await ctx.send(embed=embed)
            return
        
        starter_coins = 50000
        
        await db.create_economy_user(user_id, starter_coins)
        
        embed = discord.Embed(
            title="🎉 Welcome to Cric Masters!",
            description=f"**{ctx.author.name}** has made their debut!\n\nYour cricket management journey begins now!",
            color=discord.Color.green()
        )
        
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        embed.add_field(
            name="💰 Starter Bonus",
            value=f"**{starter_coins:,} coins** added to your account!",
            inline=False
        )
        
        embed.add_field(
            name="🎯 What's Next?",
            value="1️⃣ Use **`!cmauction`** to start building your team\n"
                  "2️⃣ Use **`!cmplay`** to play your first match\n"
                  "3️⃣ Use **`!cmbal`** to check your balance\n"
                  "4️⃣ Use **`!cmhelp`** to explore all features",
            inline=False
        )
        
        embed.add_field(
            name="💡 Pro Tips",
            value="• Win matches to earn more coins\n"
                  "• Participate in auctions to get star players\n"
                  "• Check daily rewards with `!cmdaily`\n"
                  "• Climb the leaderboard for weekly prizes!",
            inline=False
        )
        
        embed.set_footer(text="Good luck building your dream team! 🏏")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='selectteam')
    async def select_team(self, ctx):
        """
        Select your playing XI
        Usage: !cmselectteam
        """
        user_id = ctx.author.id
        
        user_team = await db.get_user_team(user_id)
        
        embed = discord.Embed(
            title="🏏 Team Selection",
            description="Select your Playing XI!\n\n**Required:**\n• 4 Batsmen\n• 3 Bowlers\n• 2 All-Rounders\n• 2 Wicket-Keepers\n\n*Note: Your selection is hidden from opponents!*",
            color=COLORS['primary']
        )
        
        await ctx.send(embed=embed)
        
        try:
            dm_channel = await ctx.author.create_dm()
            
            # Batsmen
            batsmen_list = ""
            for idx, player in enumerate(PLAYERS_DATABASE['batsmen'][:30], 1):
                batsmen_list += f"`{idx}.` {player['name']} {player['country']} - BAT: {player['batting']}\n"
            
            embed1 = discord.Embed(title="🏏 Select 4 Batsmen", description=batsmen_list, color=COLORS['primary'])
            embed1.set_footer(text="Reply with numbers: 1 5 12 18")
            await dm_channel.send(embed=embed1)
            
            def check(m):
                return m.author.id == user_id and m.channel == dm_channel
            
            try:
                batsmen_msg = await self.bot.wait_for('message', check=check, timeout=120)
                selected_batsmen_ids = [int(x) - 1 for x in batsmen_msg.content.split()]
                
                if len(selected_batsmen_ids) != 4:
                    await dm_channel.send("❌ Please select exactly 4 batsmen!")
                    return
                
                selected_players = {
                    'batsmen': [PLAYERS_DATABASE['batsmen'][i] for i in selected_batsmen_ids]
                }
                
                # Bowlers
                bowlers_list = ""
                for idx, player in enumerate(PLAYERS_DATABASE['bowlers'][:30], 1):
                    bowlers_list += f"`{idx}.` {player['name']} {player['country']} - BOWL: {player['bowling']}\n"
                
                embed2 = discord.Embed(title="⚡ Select 3 Bowlers", description=bowlers_list, color=COLORS['danger'])
                embed2.set_footer(text="Reply with numbers: 2 7 15")
                await dm_channel.send(embed=embed2)
                
                bowlers_msg = await self.bot.wait_for('message', check=check, timeout=120)
                selected_bowlers_ids = [int(x) - 1 for x in bowlers_msg.content.split()]
                
                if len(selected_bowlers_ids) != 3:
                    await dm_channel.send("❌ Please select exactly 3 bowlers!")
                    return
                
                selected_players['bowlers'] = [PLAYERS_DATABASE['bowlers'][i] for i in selected_bowlers_ids]
                
                # All-rounders
                ar_list = ""
                for idx, player in enumerate(PLAYERS_DATABASE['all_rounders'][:25], 1):
                    ar_list += f"`{idx}.` {player['name']} {player['country']} - BAT: {player['batting']} BOWL: {player['bowling']}\n"
                
                embed3 = discord.Embed(title="💎 Select 2 All-Rounders", description=ar_list, color=COLORS['success'])
                embed3.set_footer(text="Reply with numbers: 3 8")
                await dm_channel.send(embed=embed3)
                
                ar_msg = await self.bot.wait_for('message', check=check, timeout=120)
                selected_ar_ids = [int(x) - 1 for x in ar_msg.content.split()]
                
                if len(selected_ar_ids) != 2:
                    await dm_channel.send("❌ Please select exactly 2 all-rounders!")
                    return
                
                selected_players['all_rounders'] = [PLAYERS_DATABASE['all_rounders'][i] for i in selected_ar_ids]
                
                # Wicket-keepers
                wk_list = ""
                for idx, player in enumerate(PLAYERS_DATABASE['wicket_keepers'][:20], 1):
                    wk_list += f"`{idx}.` {player['name']} {player['country']} - BAT: {player['batting']}\n"
                
                embed4 = discord.Embed(title="🧤 Select 2 Wicket-Keepers", description=wk_list, color=COLORS['warning'])
                embed4.set_footer(text="Reply with numbers: 1 4")
                await dm_channel.send(embed=embed4)
                
                wk_msg = await self.bot.wait_for('message', check=check, timeout=120)
                selected_wk_ids = [int(x) - 1 for x in wk_msg.content.split()]
                
                if len(selected_wk_ids) != 2:
                    await dm_channel.send("❌ Please select exactly 2 wicket-keepers!")
                    return
                
                selected_players['wicket_keepers'] = [PLAYERS_DATABASE['wicket_keepers'][i] for i in selected_wk_ids]
                
                all_players = (selected_players['batsmen'] + 
                             selected_players['bowlers'] + 
                             selected_players['all_rounders'] + 
                             selected_players['wicket_keepers'])
                
                team_name = f"{ctx.author.name}'s XI"
                await db.create_user_team(user_id, team_name, all_players)
                
                await dm_channel.send("✅ **Team saved successfully!**\n\nYour Playing XI is ready for matches!")
                await ctx.send(f"✅ {ctx.author.mention} Your team has been saved!")
                
            except asyncio.TimeoutError:
                await dm_channel.send("❌ Team selection timed out!")
                
        except discord.Forbidden:
            await ctx.send("❌ I cannot send you DMs! Please enable DMs from server members.")
    
    @commands.command(name='team')
    async def view_team(self, ctx, member: discord.Member = None):
        """
        View team details
        Usage: !cmteam [@user]
        """
        target = member or ctx.author
        user_team = await db.get_user_team(target.id)
        
        if not user_team:
            await ctx.send(f"❌ {target.mention} hasn't created a team yet!")
            return
        
        player_ids = user_team.get('players', [])
        team_name = user_team.get('team_name', f"{target.display_name}'s Team")
        
        # Convert player IDs to player objects
        players = []
        for pid in player_ids:
            player = get_player_by_id(pid)
            if player:
                players.append(player)
        
        if not players:
            await ctx.send(f"❌ {target.mention}'s team has no players!")
            return
        
        img_bytes = image_gen.create_playing_xi_image(team_name, players)
        file = discord.File(img_bytes, filename="team.png")
        
        embed = discord.Embed(
            title=f"⭐ {team_name}",
            description=f"**Matches Played:** {user_team.get('matches_played', 0)}\n**Wins:** {user_team.get('wins', 0)} | **Losses:** {user_team.get('losses', 0)}",
            color=COLORS['primary']
        )
        embed.set_image(url="attachment://team.png")
        embed.set_footer(text=f"Budget Remaining: ${user_team.get('budget_remaining', 0):,}")
        
        await ctx.send(file=file, embed=embed)
    
    @commands.command(name='xi')
    async def view_playing_xi(self, ctx, member: discord.Member = None):
        """
        View playing XI with detailed stats
        Usage: !cmxi [@user]
        """
        target = member or ctx.author
        
        # Get playing XI directly from database (primary method)
        playing_xi = await db.get_playing_xi(target.id)
        
        # Also get team data for team name
        team_data = await db.get_user_team(target.id)
        
        if not playing_xi or len(playing_xi) == 0:
            await ctx.send(f"❌ {target.mention} hasn't set their playing XI yet! Use `!cmsetxi` to set it or ask an admin to use `!cmsetteam`")
            return
        team_name = team_data.get('team_name', f"{target.display_name}'s Team")
        
        # Calculate team OVR
        total_ovr = 0
        player_count = 0
        
        batsmen = []
        bowlers = []
        all_rounders = []
        wicket_keepers = []
        
        from utils.ovr_calculator import calculate_ovr
        
        for player_id in playing_xi:
            player = get_player_by_id(player_id)
            if player:
                ovr = calculate_ovr(player)
                total_ovr += ovr
                player_count += 1
                
                # Get rarity emoji
                if ovr >= 90:
                    card = "⚜️"
                elif ovr >= 85:
                    card = "💎"
                elif ovr >= 80:
                    card = "🏆"
                else:
                    card = "🎖️"
                
                player_line = f"{card}| {player['name']} | {int(ovr)} | {player['batting']} | {player['bowling']} | {player['country']}"
                
                if player['role'] == 'batsman':
                    batsmen.append(player_line)
                elif player['role'] == 'bowler':
                    bowlers.append(player_line)
                elif player['role'] == 'all_rounder':
                    all_rounders.append(player_line)
                elif player['role'] == 'wicket_keeper':
                    wicket_keepers.append(player_line)
        
        team_ovr = int(total_ovr / player_count) if player_count > 0 else 0
        
        embed = discord.Embed(
            title=f"🏏 {team_name}",
            description=f"**( {team_name} ) • OVR: {team_ovr}**\n\nCard | Player | OVR | BAT | BOWL | Country",
            color=0x2ecc71
        )
        
        # Add players by role
        if batsmen:
            embed.add_field(name="Batters 🏏", value="\n".join(batsmen), inline=False)
        
        if wicket_keepers:
            embed.add_field(name="WK 🧤", value="\n".join(wicket_keepers), inline=False)
        
        if all_rounders:
            embed.add_field(name="All-Rounders 🔥", value="\n".join(all_rounders), inline=False)
        
        if bowlers:
            embed.add_field(name="Bowlers 🎯", value="\n".join(bowlers), inline=False)
        
        embed.set_footer(text=f"{target.display_name} • Playing XI", icon_url=target.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='setteamname', aliases=['teamname', 'changename'])
    async def change_team_name(self, ctx, *, new_name: str = None):
        """
        Change your team name
        Usage: !cmsetteamname <new name>
        """
        if not new_name:
            await ctx.send("❌ Please provide a team name!\nUsage: `!cmsetteamname Your Team Name`")
            return
        
        # Validate name length
        if len(new_name) > 30:
            await ctx.send("❌ Team name must be 30 characters or less!")
            return
        
        if len(new_name) < 3:
            await ctx.send("❌ Team name must be at least 3 characters!")
            return
        
        # Check if user has a team
        team_data = await db.get_user_team(ctx.author.id)
        if not team_data:
            await ctx.send("❌ You don't have a team yet! Use `!cmcreate` to create one.")
            return
        
        # Update team name
        from datetime import datetime
        await db.db.teams.update_one(
            {"user_id": str(ctx.author.id)},
            {"$set": {"team_name": new_name, "updated_at": datetime.utcnow()}}
        )
        
        embed = discord.Embed(
            title="✅ Team Name Updated!",
            description=f"Your team is now called:\n**{new_name}**",
            color=COLORS['success']
        )
        embed.set_footer(text=f"Use !cmxi to see your updated team")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='setxi')
    async def set_playing_xi(self, ctx):
        """
        Auto-select balanced playing XI
        Usage: !cmsetxi
        """
        user_team = await db.get_user_team(ctx.author.id)
        
        if not user_team or not user_team.get('players'):
            await ctx.send("❌ You don't have any players yet! Join an auction first with `!cmauction`")
            return
        
        players = user_team['players']
        
        if len(players) < 11:
            await ctx.send(f"❌ You need at least 11 players to set a playing XI! You have {len(players)} players.")
            return
        
        batsmen = [p for p in players if get_player_by_id(p) and get_player_by_id(p)['role'] == 'batsman']
        bowlers = [p for p in players if get_player_by_id(p) and get_player_by_id(p)['role'] == 'bowler']
        all_rounders = [p for p in players if get_player_by_id(p) and get_player_by_id(p)['role'] == 'all_rounder']
        wicket_keepers = [p for p in players if get_player_by_id(p) and get_player_by_id(p)['role'] == 'wicket_keeper']
        
        playing_xi = []
        
        if wicket_keepers:
            playing_xi.append(wicket_keepers[0])
        
        playing_xi.extend(batsmen[:4])
        playing_xi.extend(all_rounders[:2])
        playing_xi.extend(bowlers[:4])
        
        while len(playing_xi) < 11 and len(playing_xi) < len(players):
            for p in players:
                if p not in playing_xi:
                    playing_xi.append(p)
                    if len(playing_xi) == 11:
                        break
        
        await db.set_playing_xi(ctx.author.id, playing_xi)
        
        embed = discord.Embed(
            title="✅ Playing XI Set!",
            description="Your playing XI has been automatically selected from your squad.",
            color=COLORS['success']
        )
        
        xi_text = []
        for i, player_id in enumerate(playing_xi, 1):
            player = get_player_by_id(player_id)
            if player:
                role_emoji = {"batsman": "🏏", "bowler": "⚾", "all_rounder": "⚡", "wicket_keeper": "🧤"}
                emoji = role_emoji.get(player['role'], "👤")
                xi_text.append(f"{i}. {emoji} {player['name']} {player['country']}")
        
        embed.add_field(name="Your Playing XI", value="\n".join(xi_text), inline=False)
        embed.set_footer(text="Use !cmxi to view your playing XI anytime")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='subs', aliases=['substitutes', 'bench'])
    async def view_substitutes(self, ctx, member: discord.Member = None):
        """
        View substitute players (bench)
        Usage: !cmsubs [@user]
        """
        target = member or ctx.author
        user_team = await db.get_user_team(target.id)
        
        if not user_team:
            await ctx.send(f"❌ {target.mention} hasn't created a team yet!")
            return
        
        # Get playing XI
        playing_xi = await db.get_playing_xi(target.id)
        if not playing_xi:
            playing_xi = []
        
        # Get all players
        all_players = user_team.get('players', [])
        
        # Substitute players = all players - playing XI
        substitutes = [p for p in all_players if p not in playing_xi]
        
        if not substitutes:
            await ctx.send(f"📋 {target.display_name} has no substitute players!\n\n✅ All players are in the playing XI.")
            return
        
        embed = discord.Embed(
            title=f"📋 {target.display_name}'s Substitutes",
            description=f"**Total Substitutes:** {len(substitutes)}/9\n**Playing XI:** {len(playing_xi)}/11\n**Squad Size:** {len(all_players)}/20",
            color=COLORS['info']
        )
        
        # Group substitutes by role
        batsmen = []
        bowlers = []
        all_rounders = []
        wicket_keepers = []
        
        for player_id in substitutes:
            player = get_player_by_id(player_id)
            if player:
                if player['role'] == 'batsman':
                    batsmen.append(f"🏏 {player['name']} ({player['country']}) - BAT: {player['batting']}")
                elif player['role'] == 'bowler':
                    bowlers.append(f"⚾ {player['name']} ({player['country']}) - BOWL: {player['bowling']}")
                elif player['role'] == 'all_rounder':
                    all_rounders.append(f"⚡ {player['name']} ({player['country']}) - BAT: {player['batting']} BOWL: {player['bowling']}")
                elif player['role'] == 'wicket_keeper':
                    wicket_keepers.append(f"🧤 {player['name']} ({player['country']}) - BAT: {player['batting']}")
        
        if wicket_keepers:
            embed.add_field(name="🧤 Wicket Keepers", value="\n".join(wicket_keepers), inline=False)
        if batsmen:
            embed.add_field(name="🏏 Batsmen", value="\n".join(batsmen), inline=False)
        if all_rounders:
            embed.add_field(name="⚡ All-Rounders", value="\n".join(all_rounders), inline=False)
        if bowlers:
            embed.add_field(name="⚾ Bowlers", value="\n".join(bowlers), inline=False)
        
        embed.set_footer(text=f"Use !cmsetxi to change your playing XI • Squad capacity: 20 players")
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='swap', aliases=['swapplayer', 'exchange'])
    async def swap_players(self, ctx, player1: str = None, player2: str = None):
        """
        Swap a player between playing XI and substitutes
        Usage: !cmswap <xi_number> <sub_number>
        Example: !cmswap 4 2
        
        Or use player IDs: !cmswap bat_001 bat_005
        Or use interactive mode: !cmswap
        """
        user_team = await db.get_user_team(ctx.author.id)
        
        if not user_team:
            await ctx.send("❌ You don't have a team yet! Use `!cmdebut` to start.")
            return
        
        playing_xi = await db.get_playing_xi(ctx.author.id)
        all_players = user_team.get('players', [])
        substitutes = [p for p in all_players if p not in playing_xi]
        
        if not playing_xi:
            await ctx.send("❌ You haven't set your playing XI yet! Use `!cmsetxi` first.")
            return
        
        # If no arguments, show interactive swap menu
        if not player1 or not player2:
            embed = discord.Embed(
                title="🔄 Swap Players",
                description="**Usage:** `!cmswap <xi_number> <sub_number>`\n**Example:** `!cmswap 4 2`\n\n⬇️ First number = Playing XI player\n⬇️ Second number = Substitute player",
                color=COLORS['primary']
            )
            
            # Show playing XI
            xi_list = []
            for idx, pid in enumerate(playing_xi, 1):
                player = get_player_by_id(pid)
                if player:
                    role_emoji = {"batsman": "🏏", "bowler": "⚾", "all_rounder": "⚡", "wicket_keeper": "🧤"}
                    emoji = role_emoji.get(player['role'], "👤")
                    xi_list.append(f"**{idx}.** {emoji} {player['name']}")
            
            embed.add_field(
                name="🏏 Playing XI",
                value="\n".join(xi_list) if xi_list else "None",
                inline=False
            )
            
            # Show substitutes
            sub_list = []
            for idx, pid in enumerate(substitutes, 1):
                player = get_player_by_id(pid)
                if player:
                    role_emoji = {"batsman": "🏏", "bowler": "⚾", "all_rounder": "⚡", "wicket_keeper": "🧤"}
                    emoji = role_emoji.get(player['role'], "👤")
                    sub_list.append(f"**{idx}.** {emoji} {player['name']}")
            
            embed.add_field(
                name="📋 Substitutes",
                value="\n".join(sub_list) if sub_list else "None",
                inline=False
            )
            
            embed.set_footer(text="Example: !cmswap 4 2 (swaps XI #4 with Sub #2)")
            
            await ctx.send(embed=embed)
            return
        
        # Check if both arguments are numbers
        xi_player_id = None
        sub_player_id = None
        
        try:
            num1 = int(player1)
            num2 = int(player2)
            
            # Both are numbers - first from XI, second from Subs
            if 1 <= num1 <= len(playing_xi):
                xi_player_id = playing_xi[num1 - 1]
            else:
                await ctx.send(f"❌ XI number must be between 1 and {len(playing_xi)}!")
                return
            
            if 1 <= num2 <= len(substitutes):
                sub_player_id = substitutes[num2 - 1]
            else:
                await ctx.send(f"❌ Substitute number must be between 1 and {len(substitutes)}!")
                return
            
            player1 = xi_player_id
            player2 = sub_player_id
            
        except ValueError:
            # At least one is not a number, treat as player IDs
            pass
        
        # Validate players
        if player1 not in all_players:
            await ctx.send(f"❌ `{player1}` not found in your squad!")
            return
        
        if player2 not in all_players:
            await ctx.send(f"❌ `{player2}` not found in your squad!")
            return
        
        # Check if one is in XI and other is in subs
        player1_in_xi = player1 in playing_xi
        player2_in_xi = player2 in playing_xi
        
        if player1_in_xi == player2_in_xi:
            await ctx.send("❌ One player must be in playing XI and the other in substitutes!")
            return
        
        # Get player details
        p1 = get_player_by_id(player1)
        p2 = get_player_by_id(player2)
        
        if not p1 or not p2:
            await ctx.send("❌ Player data not found!")
            return
        
        # Check role compatibility (must be same role)
        if p1['role'] != p2['role']:
            await ctx.send(f"❌ Cannot swap players of different roles!\n**{p1['name']}** is {p1['role']} but **{p2['name']}** is {p2['role']}")
            return
        
        # Perform swap
        new_xi = playing_xi.copy()
        
        if player1_in_xi:
            # Replace player1 with player2 in XI
            idx = new_xi.index(player1)
            new_xi[idx] = player2
        else:
            # Replace player2 with player1 in XI
            idx = new_xi.index(player2)
            new_xi[idx] = player1
        
        # Update database
        await db.set_playing_xi(ctx.author.id, new_xi)
        
        embed = discord.Embed(
            title="✅ Players Swapped!",
            description="Your playing XI has been updated.",
            color=COLORS['success']
        )
        
        if player1_in_xi:
            embed.add_field(
                name="🔽 Moved to Bench",
                value=f"**{p1['name']}** ({p1['role'].replace('_', ' ').title()})",
                inline=True
            )
            embed.add_field(
                name="🔼 Added to XI",
                value=f"**{p2['name']}** ({p2['role'].replace('_', ' ').title()})",
                inline=True
            )
        else:
            embed.add_field(
                name="🔼 Added to XI",
                value=f"**{p1['name']}** ({p1['role'].replace('_', ' ').title()})",
                inline=True
            )
            embed.add_field(
                name="🔽 Moved to Bench",
                value=f"**{p2['name']}** ({p2['role'].replace('_', ' ').title()})",
                inline=True
            )
        
        embed.set_footer(text="Use !cmxi to view your updated playing XI")
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TeamCommands(bot))

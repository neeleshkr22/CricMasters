"""
Legendary Auction and Leaderboard Commands
Premium features with coin-based entry
"""
import discord
from discord.ext import commands, tasks
import random
from datetime import datetime, timedelta

from config import COLORS, ECONOMY_SETTINGS, LEADERBOARD_SETTINGS, PLAYER_RARITIES
from database.db import db
from data.players import get_all_players
from utils.ovr_calculator import calculate_ovr, get_legendary_price


class LegendaryCommands(commands.Cog):
    """Legendary auction and enhanced leaderboard"""
    
    def __init__(self, bot):
        self.bot = bot
        self.weekly_reset.start()
    
    def cog_unload(self):
        self.weekly_reset.cancel()
    
    @tasks.loop(hours=24)
    async def weekly_reset(self):
        """Check for weekly leaderboard reset and award prizes"""
        now = datetime.utcnow()
        
        # Check if already awarded this week
        last_reset = await db.db.system.find_one({"_id": "last_weekly_reset"})
        if last_reset:
            last_reset_date = last_reset.get('date')
            # If already awarded this week, skip
            if last_reset_date and (now - last_reset_date).days < 7:
                return
        
        # Check if it's Monday (reset day)
        if now.strftime('%A') == LEADERBOARD_SETTINGS['reset_day']:
            # Get top 3 winners
            leaderboard = await db.get_leaderboard_by_period('weekly', limit=3)
            
            if leaderboard:
                # Award prizes to top 3
                for idx, user_data in enumerate(leaderboard, 1):
                    user_id = int(user_data['user_id'])
                    
                    # Give 10000 coins automatically
                    await db.add_coins(user_id, 10000, f"Weekly Leaderboard Rank #{idx}")
                    
                    # Give mystery box (random players)
                    num_players = 5 if idx == 1 else 3  # 1st gets 5 players, others get 3
                    mystery_players = []
                    
                    all_players = get_all_players()
                    # Higher rank = better rarity chances
                    if idx == 1:
                        rarity_weights = [30, 30, 25, 15]  # common, rare, epic, legendary
                    elif idx == 2:
                        rarity_weights = [40, 35, 20, 5]
                    else:
                        rarity_weights = [50, 30, 15, 5]
                    
                    rarities = ['common', 'rare', 'epic', 'legendary']
                    
                    for _ in range(num_players):
                        rarity = random.choices(rarities, weights=rarity_weights)[0]
                        player = random.choice(all_players).copy()
                        player['rarity'] = rarity
                        
                        # Apply rarity boosts
                        rarity_boost = PLAYER_RARITIES[rarity]['boost']
                        player['batting'] = min(100, int(player['batting'] * (1 + rarity_boost)))
                        player['bowling'] = min(100, int(player['bowling'] * (1 + rarity_boost)))
                        
                        mystery_players.append(player)
                    
                    # Add mystery box to inventory
                    await db.add_item_to_inventory(user_id, 'players', {'players': mystery_players})
                
                # Mark this week as awarded
                await db.db.system.update_one(
                    {"_id": "last_weekly_reset"},
                    {"$set": {"date": now, "updated_at": now}},
                    upsert=True
                )
            
            # Announce in all guilds
            for guild in self.bot.guilds:
                channel = discord.utils.find(
                    lambda c: 'cricket' in c.name.lower() or 'general' in c.name.lower(),
                    guild.text_channels
                )
                
                if channel and leaderboard:
                    embed = discord.Embed(
                        title="🎁 Weekly Leaderboard Prizes Awarded!",
                        description="**Top 3 players received exciting prizes!**\n\n"
                                   "🎊 **Automatic Rewards:**\n"
                                   "💰 10,000 Coins\n"
                                   "🎁 Mystery Box (Random Players)\n\n"
                                   "**This Week's Winners:**",
                        color=COLORS['gold']
                    )
                    
                    medals = ["🥇", "🥈", "🥉"]
                    for idx, user_data in enumerate(leaderboard, 1):
                        try:
                            user = await self.bot.fetch_user(int(user_data['user_id']))
                            wins = user_data.get('wins', 0)
                            embed.add_field(
                                name=f"{medals[idx-1]} {user.display_name}",
                                value=f"**{wins} Wins**\n"
                                     f"💰 10,000 coins\n"
                                     f"🎁 {5 if idx == 1 else 3} mystery players!",
                                inline=True
                            )
                        except:
                            pass
                    
                    embed.set_footer(text="Keep playing to win next week!")
                    
                    try:
                        await channel.send(embed=embed)
                    except:
                        pass
    
    @weekly_reset.before_loop
    async def before_weekly_reset(self):
        await self.bot.wait_until_ready()
    
    @commands.command(name='prizes', aliases=['leaderboardprizes'])
    async def enhanced_leaderboard(self, ctx, period: str = 'all'):
        """
        View enhanced leaderboard with prizes
        Usage: cmleaderboard [period]
        Periods: all, weekly, monthly
        """
        if period not in ['all', 'weekly', 'monthly']:
            await ctx.send("❌ Invalid period! Use: all, weekly, or monthly")
            return
        
        if period == 'all':
            leaderboard = await db.get_leaderboard(limit=10)
            title = "🏆 All-Time Leaderboard"
            prizes = None
        else:
            leaderboard = await db.get_leaderboard_by_period(period, limit=10)
            title = f"🏆 {period.title()} Leaderboard"
            prizes = LEADERBOARD_SETTINGS.get(f'{period}_prizes', {})
        
        if not leaderboard:
            await ctx.send("❌ No leaderboard data available!")
            return
        
        embed = discord.Embed(
            title=title,
            description="Top players based on wins!",
            color=COLORS['gold']
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for idx, user_data in enumerate(leaderboard, 1):
            medal = medals[idx-1] if idx <= 3 else f"`{idx}.`"
            
            user_id = user_data['user_id']
            try:
                user = await self.bot.fetch_user(int(user_id))
                username = user.display_name
            except:
                username = "Unknown User"
            
            wins = user_data.get('wins', 0)
            matches = user_data.get('matches_played', 0)
            win_rate = (wins / matches * 100) if matches > 0 else 0
            
            value = f"**Wins:** {wins} | **Matches:** {matches} | **Win Rate:** {win_rate:.1f}%"
            
            # Add prize info if applicable
            if prizes and idx in prizes:
                prize = prizes[idx]
                value += f"\n🎁 **Prize:** {prize['coins']:,} coins + {prize['pack']}"
            
            embed.add_field(
                name=f"{medal} {username}",
                value=value,
                inline=False
            )
        
        # Time until reset
        if period in ['weekly', 'monthly']:
            now = datetime.utcnow()
            if period == 'weekly':
                days_until = (7 - now.weekday()) % 7
                reset_text = f"Resets in {days_until} days"
            else:
                days_until = 30 - now.day
                reset_text = f"Resets in {days_until} days"
            
            embed.set_footer(text=reset_text)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='legendaryauction')
    @commands.has_permissions(administrator=True)
    async def start_legendary_auction(self, ctx, num_players: int = 10):
        """
        Start a legendary auction with historic cricket legends
        Usage: cmlegendaryauction [num_players]
        Can run parallel to regular auctions!
        """
        # Check for active LEGENDARY auction only
        active_legendary = await db.db.legendary_auctions.find_one({
            "guild_id": str(ctx.guild.id),
            "status": "active"
        })
        
        if active_legendary:
            await ctx.send("⚠️ A legendary auction is already in progress!")
            return
        
        # Historic Cricket Legends Database
        legendary_players = [
            # The Greatest (99+ Overall)
            {'id': 'leg_001', 'name': 'Don Bradman', 'country': '🇦🇺', 'role': 'batsman', 'batting': 99, 'bowling': 20},
            {'id': 'leg_002', 'name': 'Sachin Tendulkar', 'country': '🇮🇳', 'role': 'batsman', 'batting': 98, 'bowling': 45},
            {'id': 'leg_003', 'name': 'Viv Richards', 'country': '🇧🇧', 'role': 'batsman', 'batting': 97, 'bowling': 35},
            {'id': 'leg_004', 'name': 'Brian Lara', 'country': '🇹🇹', 'role': 'batsman', 'batting': 97, 'bowling': 25},
            
            # Legendary All-Rounders (95+ Overall)
            {'id': 'leg_005', 'name': 'Jacques Kallis', 'country': '🇿🇦', 'role': 'all_rounder', 'batting': 95, 'bowling': 85},
            {'id': 'leg_006', 'name': 'Garfield Sobers', 'country': '🇧🇧', 'role': 'all_rounder', 'batting': 93, 'bowling': 88},
            {'id': 'leg_007', 'name': 'Imran Khan', 'country': '🇵🇰', 'role': 'all_rounder', 'batting': 80, 'bowling': 95},
            {'id': 'leg_008', 'name': 'Richard Hadlee', 'country': '🇳🇿', 'role': 'all_rounder', 'batting': 75, 'bowling': 96},
            {'id': 'leg_009', 'name': 'Kapil Dev', 'country': '🇮🇳', 'role': 'all_rounder', 'batting': 82, 'bowling': 90},
            
            # Legendary Bowlers (95+ Overall)
            {'id': 'leg_010', 'name': 'Shane Warne', 'country': '🇦🇺', 'role': 'bowler', 'batting': 40, 'bowling': 99},
            {'id': 'leg_011', 'name': 'Muttiah Muralitharan', 'country': '🇱🇰', 'role': 'bowler', 'batting': 25, 'bowling': 99},
            {'id': 'leg_012', 'name': 'Glenn McGrath', 'country': '🇦🇺', 'role': 'bowler', 'batting': 20, 'bowling': 98},
            {'id': 'leg_013', 'name': 'Malcolm Marshall', 'country': '🇧🇧', 'role': 'bowler', 'batting': 35, 'bowling': 97},
            {'id': 'leg_014', 'name': 'Wasim Akram', 'country': '🇵🇰', 'role': 'bowler', 'batting': 45, 'bowling': 97},
            
            # Modern Legends (92-95 Overall)
            {'id': 'leg_015', 'name': 'AB de Villiers', 'country': '🇿🇦', 'role': 'wicket_keeper', 'batting': 96, 'bowling': 40},
            {'id': 'leg_016', 'name': 'Kumar Sangakkara', 'country': '🇱🇰', 'role': 'wicket_keeper', 'batting': 94, 'bowling': 30},
            {'id': 'leg_017', 'name': 'Adam Gilchrist', 'country': '🇦🇺', 'role': 'wicket_keeper', 'batting': 92, 'bowling': 35},
            {'id': 'leg_018', 'name': 'MS Dhoni', 'country': '🇮🇳', 'role': 'wicket_keeper', 'batting': 88, 'bowling': 40},
            
            # Batting Legends (90-95)
            {'id': 'leg_019', 'name': 'Ricky Ponting', 'country': '🇦🇺', 'role': 'batsman', 'batting': 95, 'bowling': 30},
            {'id': 'leg_020', 'name': 'Virat Kohli', 'country': '🇮🇳', 'role': 'batsman', 'batting': 96, 'bowling': 35},
            {'id': 'leg_021', 'name': 'Steve Smith', 'country': '🇦🇺', 'role': 'batsman', 'batting': 94, 'bowling': 45},
            {'id': 'leg_022', 'name': 'Kane Williamson', 'country': '🇳🇿', 'role': 'batsman', 'batting': 93, 'bowling': 40},
            {'id': 'leg_023', 'name': 'Joe Root', 'country': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'role': 'batsman', 'batting': 92, 'bowling': 42},
            {'id': 'leg_024', 'name': 'Babar Azam', 'country': '🇵🇰', 'role': 'batsman', 'batting': 91, 'bowling': 35},
        ]
        
        # Select random legendary players
        import random
        selected_legends = random.sample(legendary_players, min(num_players, len(legendary_players)))
        
        # Add auction data and calculate prices
        for player in selected_legends:
            player['rarity'] = 'legendary'
            player['overall'] = calculate_ovr(player)
            player['current_bid'] = 0
            player['highest_bidder'] = None
            player['base_price'] = get_legendary_price(player)
        
        # Create legendary auction
        auction_id = await db.create_legendary_auction(ctx.guild.id, selected_legends, ctx.author.id)
        
        embed = discord.Embed(
            title="👑 HISTORIC LEGENDS AUCTION!",
            description=f"**{num_players} Cricket Legends** from history!\n\n"
                       f"🏆 **Entry Fee:** {ECONOMY_SETTINGS['legendary_auction_cost']:,} coins\n"
                       f"⭐ **Historic players with authentic stats!**\n"
                       f"💰 **Can run alongside regular auctions!**\n\n"
                       f"React with 💎 to join!",
            color=COLORS['gold']
        )
        
        # Show top 3 players as preview
        for i, player in enumerate(selected_legends[:3], 1):
            overall = calculate_ovr(player)
            embed.add_field(
                name=f"#{i} {player['name']} {player['country']}",
                value=f"**{player['role'].replace('_', ' ').title()}**\n"
                     f"BAT: {player['batting']} | BOWL: {player['bowling']}\n"
                     f"Overall: {overall:.1f}",
                inline=True
            )
        
        embed.set_footer(text="Historic cricket legends! Runs parallel to regular auctions.")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("💎")
        
        await ctx.send("✅ Legendary Auction created! Use `!cmjoinlegendary` to join!")
    
    @commands.command(name='joinlegendary')
    async def join_legendary_auction(self, ctx):
        """
        Join the legendary auction
        Usage: cmjoinlegendary
        """
        # Get active legendary auction
        auction = await db.db.legendary_auctions.find_one({
            "guild_id": str(ctx.guild.id),
            "status": "active"
        })
        
        if not auction:
            await ctx.send("❌ No active legendary auction in this server!")
            return
        
        # Check if already joined
        participant = next(
            (p for p in auction.get('participants', []) if p['user_id'] == str(ctx.author.id)),
            None
        )
        
        if participant:
            await ctx.send("⚠️ You have already joined this legendary auction!")
            return
        
        # Check balance
        entry_fee = auction.get('entry_fee', ECONOMY_SETTINGS['legendary_auction_cost'])
        balance = await db.get_user_balance(ctx.author.id)
        
        if balance < entry_fee:
            await ctx.send(
                f"❌ Insufficient coins! Legendary auction entry costs **{entry_fee:,} coins**.\n"
                f"You have **{balance:,} coins**. Play more matches to earn coins!"
            )
            return
        
        # Charge entry fee
        success = await db.remove_coins(ctx.author.id, entry_fee, "Legendary Auction Entry")
        
        if not success:
            await ctx.send("❌ Failed to join auction! Please try again.")
            return
        
        # Add participant with coin-based budget
        participant = {
            "user_id": str(ctx.author.id),
            "username": ctx.author.display_name,
            "budget": 50000000,  # 50M coin budget for legendary auction
            "players": []
        }
        
        await db.db.legendary_auctions.update_one(
            {"_id": auction['_id']},
            {"$addToSet": {"participants": participant}}
        )
        
        embed = discord.Embed(
            title="💎 Joined Legendary Auction!",
            description=f"**{ctx.author.display_name}** joined the legendary auction!",
            color=COLORS['success']
        )
        
        embed.add_field(name="💰 Entry Fee Paid", value=f"{entry_fee:,} coins", inline=True)
        embed.add_field(name="💵 Bidding Budget", value=f"${participant['budget']:,}", inline=True)
        embed.set_footer(text="Get ready to bid on legendary players!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='legendarystats')
    async def legendary_stats(self, ctx):
        """
        View legendary auction statistics
        Usage: cmlegendarystats
        """
        # Get active legendary auction
        active = await db.db.legendary_auctions.find_one({
            "guild_id": str(ctx.guild.id),
            "status": "active"
        })
        
        if not active:
            await ctx.send("❌ No active legendary auction in this server!")
            return
        
        participants = active.get('participants', [])
        players = active.get('players', [])
        current_index = active.get('current_player_index', 0)
        
        embed = discord.Embed(
            title="👑 Legendary Auction Stats",
            description="Current auction statistics",
            color=COLORS['gold']
        )
        
        embed.add_field(name="👥 Participants", value=len(participants), inline=True)
        embed.add_field(name="🏏 Total Players", value=len(players), inline=True)
        embed.add_field(name="📊 Progress", value=f"{current_index}/{len(players)}", inline=True)
        
        # Show current player if any
        if current_index < len(players):
            current_player = players[current_index]
            overall = calculate_ovr(current_player)
            
            embed.add_field(
                name="⚡ Current Player",
                value=f"**{current_player['name']}** {current_player['country']}\n"
                     f"BAT: {current_player['batting']} | BOWL: {current_player['bowling']}\n"
                     f"Overall: {overall:.1f}\n"
                     f"Base Price: ${current_player.get('base_price', 0):,}",
                inline=False
            )
            
            if current_player.get('highest_bidder'):
                try:
                    bidder = await self.bot.fetch_user(int(current_player['highest_bidder']))
                    embed.add_field(
                        name="🏆 Highest Bidder",
                        value=f"{bidder.mention}\n${current_player.get('current_bid', 0):,}",
                        inline=False
                    )
                except:
                    pass
        
        # Show top bidders
        if participants:
            top_spenders = sorted(participants, key=lambda x: len(x.get('players', [])), reverse=True)[:3]
            
            top_text = []
            for i, p in enumerate(top_spenders, 1):
                try:
                    user = await self.bot.fetch_user(int(p['user_id']))
                    player_count = len(p.get('players', []))
                    top_text.append(f"{i}. {user.mention} - {player_count} players")
                except:
                    pass
            
            if top_text:
                embed.add_field(
                    name="💰 Top Collectors",
                    value="\n".join(top_text),
                    inline=False
                )
        
        embed.set_footer(text="Historic cricket legends auction!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='pack')
    async def random_pack(self, ctx):
        """
        Get a random free pack (once per day)
        Usage: cmpack
        """
        # Check if already claimed today
        user_data = await db.db.economy.find_one({"user_id": str(ctx.author.id)})
        
        if user_data and user_data.get('last_pack_claim'):
            last_claim = user_data['last_pack_claim']
            now = datetime.utcnow()
            
            if (now - last_claim).total_seconds() < 86400:
                time_left = 86400 - (now - last_claim).total_seconds()
                hours = int(time_left // 3600)
                minutes = int((time_left % 3600) // 60)
                
                await ctx.send(f"⏰ You can claim your next free pack in **{hours}h {minutes}m**!")
                return
        
        # Generate random pack
        pack_types = ['bronze_pack', 'silver_pack', 'gold_pack']
        weights = [60, 30, 10]  # 60% bronze, 30% silver, 10% gold
        
        pack_id = random.choices(pack_types, weights=weights)[0]
        pack_data = {
            'bronze_pack': {'name': 'Bronze Pack', 'players': 3, 'rarity': 'common'},
            'silver_pack': {'name': 'Silver Pack', 'players': 5, 'rarity': 'rare'},
            'gold_pack': {'name': 'Gold Pack', 'players': 5, 'rarity': 'epic'},
        }[pack_id]
        
        # Generate players
        from cogs.economy_commands import EconomyCommands
        eco_cog = EconomyCommands(self.bot)
        players = await eco_cog.generate_pack_contents(pack_data)
        
        # Save to inventory
        await db.add_item_to_inventory(ctx.author.id, 'players', {'players': players})
        
        # Add players to team and auto-fill Playing XI
        user_team = await db.get_user_team(ctx.author.id)
        playing_xi = await db.get_playing_xi(ctx.author.id) or []
        
        for player in players:
            if user_team:
                current_players = user_team.get('players', [])
                current_players.append(player['id'])
                await db.update_user_team(ctx.author.id, current_players, user_team.get('budget_remaining', 0))
            else:
                # Create team if doesn't exist
                await db.create_user_team(ctx.author.id, f"{ctx.author.name}'s Team", [player['id']])
                user_team = await db.get_user_team(ctx.author.id)
            
            # Auto-add to Playing XI if less than 11 players
            if len(playing_xi) < 11:
                playing_xi.append(player['id'])
        
        # Update Playing XI
        if len(playing_xi) > 0:
            await db.set_playing_xi(ctx.author.id, playing_xi[:11])  # Max 11 players
        
        # Update last claim time
        await db.db.economy.update_one(
            {"user_id": str(ctx.author.id)},
            {"$set": {"last_pack_claim": datetime.utcnow()}},
            upsert=True
        )
        
        embed = discord.Embed(
            title=f"🎁 Free {pack_data['name']} Opened!",
            description="Here are your players!",
            color=COLORS['gold']
        )
        
        for player in players:
            rarity_data = PLAYER_RARITIES[player['rarity']]
            embed.add_field(
                name=f"{rarity_data['emoji']} {player['name']} {player['country']}",
                value=f"{player['role'].title()}\nBAT: {player['batting']} | BOWL: {player['bowling']}",
                inline=True
            )
        
        embed.set_footer(text="Come back tomorrow for another free pack!")
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LegendaryCommands(bot))

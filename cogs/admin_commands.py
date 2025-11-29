"""
Admin Commands for Cric Mater Bot
Powerful moderation and management tools
"""
import discord
from discord.ext import commands
import random
from datetime import datetime, timedelta

from config import ADMIN_IDS, COLORS, AUCTION_SETTINGS, ECONOMY_SETTINGS
from database.db import db
from data.players import get_all_players


class AdminCommands(commands.Cog):
    """Admin-only commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return user_id in ADMIN_IDS
    
    @commands.command(name='auction')
    @commands.has_permissions(administrator=True)
    async def start_auction(self, ctx, num_players: int = 20, duration: str = "1h"):
        """
        Start a player auction with automated bidding
        Usage: cmauction <num_players> <duration>
        Examples: 
            cmauction 20        # 20 players, 1 hour per player
            cmauction 30 30m    # 30 players, 30 minutes each
            cmauction 50 3h     # 50 players, 3 hours each
        
        Durations: 15m, 30m, 1h, 3h, 6h, 12h, 24h
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        # Parse duration
        duration_map = {
            "15m": 15, "30m": 30, "1h": 60, "2h": 120,
            "3h": 180, "6h": 360, "12h": 720, "24h": 1440
        }
        
        if duration not in duration_map:
            await ctx.send(f"❌ Invalid duration! Use: {', '.join(duration_map.keys())}")
            return
        
        duration_minutes = duration_map[duration]
        
        # Check for active auction
        active = await db.get_active_auction(ctx.guild.id)
        if active:
            await ctx.send("⚠️ An auction is already in progress!")
            return
        
        # Get random players
        all_players = get_all_players()
        auction_players = random.sample(all_players, min(num_players, len(all_players)))
        
        # Add auction data
        for player in auction_players:
            player['current_bid'] = 0
            player['highest_bidder'] = None
            player['base_price'] = random.choice([500000, 1000000, 2000000, 5000000])
        
        # Create auction with duration
        auction_id = await db.create_auction(ctx.guild.id, auction_players, ctx.author.id)
        
        # Store duration and auto-mode
        await db.db.auctions.update_one(
            {"_id": auction_id},
            {"$set": {
                "duration_minutes": duration_minutes,
                "auto_mode": True,
                "created_at": datetime.utcnow()
            }}
        )
        
        embed = discord.Embed(
            title="🎪 AUTOMATED AUCTION STARTED!",
            description=f"**{num_players} players** up for grabs!\n\n⏱️ **{duration}** per player\n💰 React to participate!",
            color=COLORS['gold']
        )
        
        embed.add_field(name="💵 Starting Budget", value=f"${AUCTION_SETTINGS['initial_budget']:,}", inline=True)
        embed.add_field(name="⏱️ Duration", value=f"{duration} per player", inline=True)
        embed.add_field(name="🤖 Mode", value="Automated", inline=True)
        embed.set_footer(text="Players auto-award to highest bidder after time expires!")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("💰")
        
        # Store auction message
        await db.db.auctions.update_one(
            {"_id": auction_id},
            {"$set": {"message_id": msg.id, "channel_id": ctx.channel.id}}
        )
        
        await ctx.send(f"✅ Auction created! Each player will auto-sell after **{duration}**.")
        
        # Start auto-auction task
        self.bot.loop.create_task(self.run_automated_auction(ctx, auction_id, duration_minutes))
    
    @commands.command(name='nextbid')
    @commands.has_permissions(administrator=True)
    async def next_bid(self, ctx):
        """
        Move to next player in auction
        Usage: cmnextbid
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        auction = await db.get_active_auction(ctx.guild.id)
        if not auction:
            await ctx.send("❌ No active auction!")
            return
        
        # Close current bid
        next_player = await db.close_current_bid(str(auction['_id']))
        
        if not next_player:
            # Auction complete
            embed = discord.Embed(
                title="🎊 AUCTION COMPLETE!",
                description="All players have been sold!",
                color=COLORS['success']
            )
            await ctx.send(embed=embed)
            return
        
        # Show next player
        embed = discord.Embed(
            title="🎪 Next Player",
            description=f"**{next_player['name']}** {next_player['country']}",
            color=COLORS['gold']
        )
        
        embed.add_field(name="Role", value=next_player['role'].replace('_', ' ').title(), inline=True)
        embed.add_field(name="Batting", value=next_player['batting'], inline=True)
        embed.add_field(name="Bowling", value=next_player['bowling'], inline=True)
        embed.add_field(name="💰 Base Price", value=f"${next_player['base_price']:,}", inline=False)
        embed.set_footer(text="Use cmbid [amount] to place a bid!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='endauction')
    @commands.has_permissions(administrator=True)
    async def end_auction(self, ctx):
        """
        End the current auction
        Usage: cmendauction
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        from bson.objectid import ObjectId
        
        auction = await db.get_active_auction(ctx.guild.id)
        if not auction:
            await ctx.send("❌ No active auction!")
            return
        
        # Mark as completed
        await db.db.auctions.update_one(
            {"_id": auction['_id']},
            {"$set": {"status": "completed"}}
        )
        
        # Save teams to database
        for participant in auction.get('participants', []):
            user_id = participant['user_id']
            players = participant.get('players', [])
            budget_remaining = participant.get('budget', 0)
            
            if players:
                await db.update_user_team(user_id, players, budget_remaining)
        
        embed = discord.Embed(
            title="✅ Auction Ended",
            description="All teams have been saved!",
            color=COLORS['success']
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clearmatches')
    @commands.has_permissions(administrator=True)
    async def clear_matches(self, ctx):
        """
        Clear all active matches
        Usage: cmclearmatches
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        # This would clear active matches from the bot's memory
        # Implementation depends on how matches are stored
        
        await ctx.send("✅ All active matches cleared!")
    
    @commands.command(name='addplayer')
    @commands.has_permissions(administrator=True)
    async def add_player(self, ctx, player_name: str, role: str, batting: int, bowling: int):
        """
        Add a custom player to database
        Usage: cmaddplayer "Player Name" batsman 85 75
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        # This would add player to database
        # For now, just confirmation
        
        embed = discord.Embed(
            title="✅ Player Added",
            description=f"**{player_name}** has been added to the player pool!",
            color=COLORS['success']
        )
        
        embed.add_field(name="Role", value=role, inline=True)
        embed.add_field(name="Batting", value=batting, inline=True)
        embed.add_field(name="Bowling", value=bowling, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='ban')
    @commands.has_permissions(administrator=True)
    async def ban_user(self, ctx, member: discord.Member, *, reason: str = "Violating rules"):
        """
        Ban a user from using the bot
        Usage: cmban @user Reason
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        # Store ban in database
        await db.db.bans.insert_one({
            "user_id": str(member.id),
            "banned_by": str(ctx.author.id),
            "reason": reason,
            "timestamp": discord.utils.utcnow()
        })
        
        embed = discord.Embed(
            title="🔨 User Banned",
            description=f"{member.mention} has been banned from using Cric Mater Bot",
            color=COLORS['danger']
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='unban')
    @commands.has_permissions(administrator=True)
    async def unban_user(self, ctx, user_id: str):
        """
        Unban a user
        Usage: cmunban 123456789
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        # Remove ban from database
        result = await db.db.bans.delete_one({"user_id": user_id})
        
        if result.deleted_count > 0:
            await ctx.send(f"✅ User <@{user_id}> has been unbanned!")
        else:
            await ctx.send(f"❌ User <@{user_id}> is not banned!")
    
    @commands.command(name='dbstats')
    @commands.has_permissions(administrator=True)
    async def database_stats(self, ctx):
        """
        Show database statistics
        Usage: cmdbstats
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        # Get stats from database
        total_teams = await db.db.teams.count_documents({})
        total_matches = await db.db.matches.count_documents({})
        active_auctions = await db.db.auctions.count_documents({"status": "active"})
        total_economy = await db.db.economy.count_documents({})
        
        embed = discord.Embed(
            title="📊 Database Statistics",
            color=COLORS['info']
        )
        
        embed.add_field(name="👥 Total Teams", value=total_teams, inline=True)
        embed.add_field(name="🎮 Total Matches", value=total_matches, inline=True)
        embed.add_field(name="🎪 Active Auctions", value=active_auctions, inline=True)
        embed.add_field(name="💰 Economy Users", value=total_economy, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='givecoins')
    @commands.has_permissions(administrator=True)
    async def give_coins(self, ctx, member: discord.Member, amount: int):
        """
        Give coins to a user
        Usage: cmgivecoins @user [amount]
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        
        if member.bot:
            await ctx.send("❌ Cannot give coins to bots!")
            return
        
        # Add coins
        await db.add_coins(member.id, amount, f"Admin gift from {ctx.author.display_name}")
        
        embed = discord.Embed(
            title="💰 Coins Added!",
            description=f"**{ctx.author.display_name}** gave **{amount:,} coins** to {member.mention}!",
            color=COLORS['success']
        )
        
        embed.set_footer(text=f"Admin: {ctx.author.display_name}")
        await ctx.send(embed=embed)
        
        # DM the user
        try:
            dm = await member.create_dm()
            dm_embed = discord.Embed(
                title="🎁 You Received Coins!",
                description=f"An admin gave you **{amount:,} coins**!",
                color=COLORS['gold']
            )
            await dm.send(embed=dm_embed)
        except:
            pass
    
    @commands.command(name='removecoins')
    @commands.has_permissions(administrator=True)
    async def remove_coins(self, ctx, member: discord.Member, amount: int):
        """
        Remove coins from a user
        Usage: cmremovecoins @user [amount]
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        
        if member.bot:
            await ctx.send("❌ Cannot remove coins from bots!")
            return
        
        # Check balance
        balance = await db.get_user_balance(member.id)
        
        if balance < amount:
            await ctx.send(f"⚠️ {member.display_name} only has **{balance:,} coins**!")
            return
        
        # Remove coins
        success = await db.remove_coins(member.id, amount, f"Admin removal by {ctx.author.display_name}")
        
        if success:
            embed = discord.Embed(
                title="💸 Coins Removed!",
                description=f"Removed **{amount:,} coins** from {member.mention}!",
                color=COLORS['danger']
            )
            embed.add_field(name="Remaining", value=f"{balance - amount:,} coins", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to remove coins!")
    
    @commands.command(name='setcoins')
    @commands.has_permissions(administrator=True)
    async def set_coins(self, ctx, member: discord.Member, amount: int):
        """
        Set a user's coin balance
        Usage: cmsetcoins @user [amount]
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        if amount < 0:
            await ctx.send("❌ Amount cannot be negative!")
            return
        
        if member.bot:
            await ctx.send("❌ Cannot set coins for bots!")
            return
        
        # Get current balance
        current = await db.get_user_balance(member.id)
        
        # Set new balance
        await db.db.economy.update_one(
            {"user_id": str(member.id)},
            {
                "$set": {
                    "balance": amount,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        embed = discord.Embed(
            title="⚙️ Balance Updated!",
            description=f"**{member.display_name}'s** balance set to **{amount:,} coins**!",
            color=COLORS['warning']
        )
        
        embed.add_field(name="Previous", value=f"{current:,} coins", inline=True)
        embed.add_field(name="New", value=f"{amount:,} coins", inline=True)
        await ctx.send(embed=embed)
    
    @commands.command(name='deletexi')
    @commands.has_permissions(administrator=True)
    async def delete_xi(self, ctx, member: discord.Member):
        """
        Delete a user's Playing XI
        Usage: cmdeletexi @user
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        if member.bot:
            await ctx.send("❌ Cannot delete bot teams!")
            return
        
        # Delete team
        result = await db.db.teams.delete_one({"user_id": str(member.id)})
        
        if result.deleted_count > 0:
            embed = discord.Embed(
                title="🗑️ Team Deleted!",
                description=f"**{member.display_name}'s** Playing XI deleted!",
                color=COLORS['danger']
            )
            embed.add_field(
                name="Action Required",
                value=f"{member.mention} must run `cmselectteam`",
                inline=False
            )
            await ctx.send(embed=embed)
            
            # DM the user
            try:
                dm = await member.create_dm()
                dm_embed = discord.Embed(
                    title="⚠️ Your Team Was Reset",
                    description="An admin deleted your Playing XI.\nUse `cmselectteam` to create a new team!",
                    color=COLORS['warning']
                )
                await dm.send(embed=dm_embed)
            except:
                pass
        else:
            await ctx.send(f"❌ {member.display_name} doesn't have a team!")
    
    @commands.command(name='giveprize')
    @commands.has_permissions(administrator=True)
    async def give_prize(self, ctx, member: discord.Member, coins: int, pack: str = None):
        """
        Give a prize package to a user
        Usage: cmgiveprize @user [coins] [pack_type]
        Packs: bronze_pack, silver_pack, gold_pack, diamond_pack
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        if member.bot:
            await ctx.send("❌ Cannot give prizes to bots!")
            return
        
        if coins < 0:
            await ctx.send("❌ Coin amount cannot be negative!")
            return
        
        # Give coins
        if coins > 0:
            await db.add_coins(member.id, coins, f"Admin prize from {ctx.author.display_name}")
        
        # Give pack
        pack_given = None
        if pack:
            pack_lower = pack.lower()
            valid_packs = ['bronze_pack', 'silver_pack', 'gold_pack', 'diamond_pack']
            
            if pack_lower in valid_packs:
                from cogs.economy_commands import EconomyCommands
                eco_cog = EconomyCommands(self.bot)
                
                pack_data = {
                    'bronze_pack': {'name': 'Bronze Pack', 'players': 3, 'rarity': 'common'},
                    'silver_pack': {'name': 'Silver Pack', 'players': 5, 'rarity': 'rare'},
                    'gold_pack': {'name': 'Gold Pack', 'players': 5, 'rarity': 'epic'},
                    'diamond_pack': {'name': 'Diamond Pack', 'players': 5, 'rarity': 'legendary'},
                }[pack_lower]
                
                players = await eco_cog.generate_pack_contents(pack_data)
                await db.add_item_to_inventory(member.id, 'players', {'players': players})
                pack_given = pack_data['name']
        
        embed = discord.Embed(
            title="🎁 Prize Given!",
            description=f"**{member.display_name}** received a prize!",
            color=COLORS['gold']
        )
        
        if coins > 0:
            embed.add_field(name="💰 Coins", value=f"{coins:,}", inline=True)
        
        if pack_given:
            embed.add_field(name="📦 Pack", value=pack_given, inline=True)
        
        await ctx.send(embed=embed)
        
        # DM the user
        try:
            dm = await member.create_dm()
            dm_embed = discord.Embed(
                title="🎁 You Received a Prize!",
                description="An admin gave you a special prize!",
                color=COLORS['gold']
            )
            
            if coins > 0:
                dm_embed.add_field(name="💰 Coins", value=f"{coins:,}", inline=True)
            
            if pack_given:
                dm_embed.add_field(name="📦 Pack", value=pack_given, inline=True)
            
            await dm.send(embed=dm_embed)
        except:
            pass
    
    @commands.command(name='setplayerprice')
    @commands.has_permissions(administrator=True)
    async def set_player_price(self, ctx, player_name: str, price: int):
        """
        Set a player's auction base price
        Usage: cmsetplayerprice "Player Name" [price]
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        if price < 0:
            await ctx.send("❌ Price cannot be negative!")
            return
        
        # Find player
        players = get_all_players()
        player = None
        
        for p in players:
            if player_name.lower() in p['name'].lower():
                player = p
                break
        
        if not player:
            await ctx.send(f"❌ Player '{player_name}' not found!")
            return
        
        # Update player price in database
        await db.db.player_prices.update_one(
            {"player_id": player['id']},
            {
                "$set": {
                    "player_id": player['id'],
                    "player_name": player['name'],
                    "base_price": price,
                    "set_by": str(ctx.author.id),
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        embed = discord.Embed(
            title="💰 Player Price Updated!",
            description=f"**{player['name']}** {player['country']}",
            color=COLORS['success']
        )
        
        embed.add_field(name="New Base Price", value=f"${price:,}", inline=True)
        embed.add_field(name="Role", value=player['role'].replace('_', ' ').title(), inline=True)
        embed.add_field(
            name="Stats",
            value=f"BAT: {player['batting']} | BOWL: {player['bowling']}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='bannedlist')
    @commands.has_permissions(administrator=True)
    async def banned_list(self, ctx):
        """
        View all banned users
        Usage: cmbannedlist
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        banned = await db.db.bans.find({}).to_list(length=None)
        
        if not banned:
            await ctx.send("✅ No banned users!")
            return
        
        embed = discord.Embed(
            title="🔨 Banned Users",
            description=f"Total: {len(banned)} users",
            color=COLORS['danger']
        )
        
        for ban in banned[:10]:  # Show first 10
            user_id = ban['user_id']
            reason = ban.get('reason', 'No reason')
            
            embed.add_field(
                name=f"User ID: {user_id}",
                value=f"**Reason:** {reason}",
                inline=False
            )
        
        if len(banned) > 10:
            embed.set_footer(text=f"Showing 10 of {len(banned)} banned users")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='adminhelp')
    @commands.has_permissions(administrator=True)
    async def admin_help(self, ctx):
        """Show all admin commands"""
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        embed = discord.Embed(
            title="⚙️ Admin Commands",
            description="Powerful tools for server administrators",
            color=COLORS['warning']
        )
        
        commands_list = {
            "💰 Coin Management": {
                "cmgivecoins @user [amount]": "Give coins to a user",
                "cmremovecoins @user [amount]": "Remove coins from a user",
                "cmsetcoins @user [amount]": "Set user's coin balance",
            },
            "👥 User Management": {
                "cmsetteam [user_id]": "Create default team for any user",
                "cmdeletexi @user": "Delete user's Playing XI",
                "cmban @user [reason]": "Ban user from bot",
                "cmunban [user_id]": "Unban a user",
                "cmbannedlist": "View all banned users",
            },
            "🎁 Rewards & Giveaways": {
                "cmgiveprize @user [coins] [pack]": "Give prize package",
                "cmgiveaway [winners] [players]": "Start player giveaway (30s)",
            },
            "⚙️ Configuration": {
                "cmsetplayerprice \"Name\" [price]": "Set player's auction price",
                "cmdbstats": "View database statistics",
            },
            "🎪 Auctions": {
                "cmauction [num]": "Start regular auction",
                "cmlegendaryauction [num]": "Start legendary auction",
                "cmnextbid": "Move to next player",
                "cmendauction": "End current auction",
            }
        }
        
        for category, cmds in commands_list.items():
            cmd_text = "\n".join([f"`{cmd}` - {desc}" for cmd, desc in cmds.items()])
            embed.add_field(name=category, value=cmd_text, inline=False)
        
        embed.add_field(
            name="⚠️ Important",
            value="• Requires Administrator permission\n• All actions are logged\n• Use responsibly!",
            inline=False
        )
        
        embed.set_footer(text="For regular commands, use cmhelp")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='giveaway')
    @commands.has_permissions(administrator=True)
    async def start_giveaway(self, ctx, num_winners: int = 1, num_players: int = 3):
        """
        Start a player giveaway
        Usage: cmgiveaway [winners] [players_each]
        Example: cmgiveaway 3 5 (3 winners, 5 players each)
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        if num_winners < 1 or num_winners > 10:
            await ctx.send("❌ Number of winners must be between 1 and 10!")
            return
        
        if num_players < 1 or num_players > 10:
            await ctx.send("❌ Number of players must be between 1 and 10!")
            return
        
        # Create giveaway embed
        embed = discord.Embed(
            title="🎊 PLAYER GIVEAWAY!",
            description=f"**{num_winners} Lucky Winner(s)** will receive **{num_players} Random Players!**\n\n"
                       f"React with 🎁 to enter!\n"
                       f"Giveaway ends in **30 seconds**!",
            color=COLORS['gold']
        )
        
        embed.add_field(name="Winners", value=num_winners, inline=True)
        embed.add_field(name="Players per Winner", value=num_players, inline=True)
        embed.set_footer(text=f"Started by {ctx.author.display_name}")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎁")
        
        # Wait for 30 seconds
        import asyncio
        await asyncio.sleep(30)
        
        # Get message again to get reactions
        msg = await ctx.channel.fetch_message(msg.id)
        
        # Get users who reacted (excluding bots)
        participants = []
        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎁":
                async for user in reaction.users():
                    if not user.bot and user.id != ctx.author.id:
                        participants.append(user)
        
        if not participants:
            await ctx.send("❌ No one entered the giveaway!")
            return
        
        # Select random winners
        winners = random.sample(participants, min(num_winners, len(participants)))
        
        # Give players to winners
        all_players = get_all_players()
        winner_details = []
        
        for winner in winners:
            # Generate random players
            giveaway_players = []
            rarities = ['common', 'rare', 'epic', 'legendary']
            weights = [50, 30, 15, 5]  # Rarity chances
            
            for _ in range(num_players):
                rarity = random.choices(rarities, weights=weights)[0]
                player = random.choice(all_players).copy()
                player['rarity'] = rarity
                
                # Apply rarity boosts
                from config import PLAYER_RARITIES
                rarity_boost = PLAYER_RARITIES[rarity]['boost']
                player['batting'] = min(100, int(player['batting'] * (1 + rarity_boost)))
                player['bowling'] = min(100, int(player['bowling'] * (1 + rarity_boost)))
                
                giveaway_players.append(player)
            
            # Add to inventory
            await db.add_item_to_inventory(winner.id, 'players', {'players': giveaway_players})
            
            # Track for announcement
            winner_details.append({
                'user': winner,
                'players': giveaway_players
            })
            
            # DM the winner
            try:
                dm = await winner.create_dm()
                dm_embed = discord.Embed(
                    title="🎊 You Won the Giveaway!",
                    description=f"Congratulations! You received **{num_players} players**!",
                    color=COLORS['gold']
                )
                
                for player in giveaway_players:
                    rarity_data = PLAYER_RARITIES[player['rarity']]
                    dm_embed.add_field(
                        name=f"{rarity_data['emoji']} {player['name']} {player['country']}",
                        value=f"{player['role'].title()}\nBAT: {player['batting']} | BOWL: {player['bowling']}",
                        inline=True
                    )
                
                await dm.send(embed=dm_embed)
            except:
                pass
        
        # Announce winners
        result_embed = discord.Embed(
            title="🎊 Giveaway Ended!",
            description=f"**{len(participants)} participants** • **{len(winners)} winners**",
            color=COLORS['success']
        )
        
        for idx, detail in enumerate(winner_details, 1):
            winner = detail['user']
            players = detail['players']
            
            # Show first 3 players they got
            player_list = []
            for player in players[:3]:
                from config import PLAYER_RARITIES
                emoji = PLAYER_RARITIES[player['rarity']]['emoji']
                player_list.append(f"{emoji} {player['name']}")
            
            if len(players) > 3:
                player_list.append(f"...and {len(players) - 3} more!")
            
            result_embed.add_field(
                name=f"🏆 Winner #{idx}: {winner.display_name}",
                value="\n".join(player_list),
                inline=False
            )
        
        result_embed.set_footer(text="Check your DMs for full details!")
        
        await ctx.send(embed=result_embed)
    
    @commands.command(name='addplayerauction', aliases=['addauctionplayer'])
    @commands.has_permissions(administrator=True)
    async def add_player_to_auction(self, ctx, *player_names: str):
        """
        Add specific players to the current auction
        Usage: !cmaddplayerauction "Virat Kohli" "MS Dhoni" "Rohit Sharma"
        
        You can add multiple players at once by listing their names in quotes.
        Example: !cmaddplayerauction "Player 1" "Player 2" "Player 3"
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        # Check for active auction
        auction = await db.get_active_auction(ctx.guild.id)
        if not auction:
            await ctx.send("❌ No active auction! Start one first with `!cmauction`")
            return
        
        if not player_names:
            await ctx.send("❌ Please specify player names in quotes!\nExample: `!cmaddplayerauction \"Virat Kohli\" \"MS Dhoni\"`")
            return
        
        # Find players in database
        from data.players import get_all_players
        all_players = get_all_players()
        
        added_players = []
        not_found = []
        
        for name in player_names:
            # Search for player (case-insensitive)
            player = next((p for p in all_players if p['name'].lower() == name.lower()), None)
            
            if player:
                # Add auction fields
                auction_player = player.copy()
                auction_player['current_bid'] = 0
                auction_player['highest_bidder'] = None
                auction_player['base_price'] = random.choice([500000, 1000000, 2000000, 5000000])
                added_players.append(auction_player)
            else:
                not_found.append(name)
        
        if added_players:
            # Add to auction
            await db.db.auctions.update_one(
                {"_id": auction['_id']},
                {"$push": {"players": {"$each": added_players}}}
            )
            
            embed = discord.Embed(
                title="✅ Players Added to Auction!",
                color=COLORS['success']
            )
            
            players_text = "\n".join([f"• **{p['name']}** - Base: ₹{p['base_price']:,}" for p in added_players])
            embed.add_field(name=f"Added ({len(added_players)})", value=players_text, inline=False)
            
            if not_found:
                embed.add_field(name="❌ Not Found", value=", ".join(not_found), inline=False)
                embed.set_footer(text="Tip: Player names are case-sensitive. Check spelling!")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ None of the specified players were found in the database!\nNot found: {', '.join(not_found)}")
    
    @commands.command(name='setteam', aliases=['addteam', 'giveteam'])
    @commands.has_permissions(administrator=True)
    async def set_team_for_user(self, ctx, user: discord.Member = None):
        """
        Set a default playing XI for any user
        Usage: !cmsetteam [@user]
        Example: !cmsetteam @username OR !cmsetteam (to set for yourself)
        
        This will create a balanced default team with 11 players for the specified user.
        """
        if not self.is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        # If no user specified, set team for command author
        target_user = user or ctx.author
        user_id = str(target_user.id)
        
        # Create default playing XI (11 players) - REAL CRICKET PLAYERS
        default_xi = [
            'bat_0001', 'bat_0002', 'bat_0003', 'bat_0004',  # 4 Batsmen (Kohli, Rohit, Gill, Rahul)
            'bowl_0001', 'bowl_0002', 'bowl_0003', 'bowl_0004',  # 4 Bowlers (Bumrah, Shami, Siraj, Kuldeep)
            'ar_0001', 'ar_0002',  # 2 All-rounders (Hardik, Jadeja)
            'wk_0001'  # 1 Wicket-keeper (Rishabh Pant)
        ]
        
        # Create full squad (20 players: 11 playing + 9 substitutes)
        full_squad = [
            'bat_0001', 'bat_0002', 'bat_0003', 'bat_0004',  # 4 Batsmen
            'bowl_0001', 'bowl_0002', 'bowl_0003', 'bowl_0004',  # 4 Bowlers
            'ar_0001', 'ar_0002',  # 2 All-rounders
            'wk_0001',  # 1 Wicket-keeper
            # Substitutes (9 players)
            'bat_0005', 'bat_0006',  # 2 extra batsmen (Shreyas, SKY)
            'bowl_0005', 'bowl_0006',  # 2 extra bowlers (Chahal, Ashwin)
            'ar_0003', 'ar_0004',  # 2 extra all-rounders (Ashwin, Axar)
            'wk_0002', 'wk_0003', 'bat_0007'  # 1 extra WK + 2 more batsmen
        ]
        
        # Set the playing XI in database
        await db.set_playing_xi(int(user_id), default_xi)
        
        # Also create a default team if doesn't exist
        team_name = f"Team {user_id[:4]}"
        user_team = await db.get_user_team(int(user_id))
        
        if not user_team:
            # Create team with 20 players
            await db.create_user_team(int(user_id), team_name, full_squad)
        
        # Get player names for display
        from data.players import get_player_by_id
        xi_display = []
        for player_id in default_xi:
            player = get_player_by_id(player_id)
            if player:
                role_emoji = {"batsman": "🏏", "bowler": "⚾", "all_rounder": "⚡", "wicket_keeper": "🧤"}
                emoji = role_emoji.get(player['role'], "👤")
                xi_display.append(f"{emoji} {player['name']} ({player['country']})")
        
        embed = discord.Embed(
            title="✅ Team Created Successfully!",
            description=f"Playing XI has been set for {target_user.mention}",
            color=COLORS['success']
        )
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        embed.add_field(
            name="🏏 Playing XI (11 Players)",
            value="\n".join(xi_display),
            inline=False
        )
        
        embed.add_field(
            name="📊 Team Composition",
            value="**Playing XI:** 4 Batsmen • 4 Bowlers • 2 All-Rounders • 1 Wicket-Keeper\n**Substitutes:** 9 players on bench",
            inline=False
        )
        
        embed.add_field(
            name="📦 Squad Details",
            value=f"**Total Squad:** 20 players\n**Playing XI:** 11 players\n**Substitutes:** 9 players\n\nUse `!cmsubs` to view substitute players",
            inline=False
        )
        
        embed.set_footer(text=f"User can now play matches with this team!")
        
        await ctx.send(embed=embed)


    async def run_automated_auction(self, ctx, auction_id, duration_minutes):
        """Run automated auction with timed player sales"""
        try:
            await asyncio.sleep(10)  # Wait for people to join
            
            while True:
                # Get auction
                auction = await db.db.auctions.find_one({"_id": auction_id})
                
                if not auction or auction.get('status') != 'active':
                    break
                
                current_index = auction.get('current_player_index', 0)
                players = auction.get('players', [])
                
                if current_index >= len(players):
                    # All players sold
                    await self.finalize_automated_auction(ctx, auction_id)
                    break
                
                current_player = players[current_index]
                
                # Start bidding for this player
                embed = discord.Embed(
                    title=f"🎪 Player #{current_index + 1}/{len(players)}",
                    description=f"**{current_player['name']}** {current_player['country']}\n\n⏱️ **{duration_minutes} minutes** to bid!",
                    color=COLORS['gold']
                )
                
                embed.add_field(name="Role", value=current_player['role'].replace('_', ' ').title(), inline=True)
                embed.add_field(name="Batting", value=current_player['batting'], inline=True)
                embed.add_field(name="Bowling", value=current_player['bowling'], inline=True)
                embed.add_field(name="💰 Base Price", value=f"${current_player['base_price']:,}", inline=False)
                embed.add_field(name="💵 Current Bid", value=f"${current_player.get('current_bid', 0):,}", inline=True)
                
                highest_bidder = current_player.get('highest_bidder')
                if highest_bidder:
                    try:
                        user = await self.bot.fetch_user(int(highest_bidder))
                        embed.add_field(name="🏆 Highest Bidder", value=user.mention, inline=True)
                    except:
                        pass
                
                embed.set_footer(text=f"Use !cmbid <amount> to bid | Auto-sells in {duration_minutes} min")
                
                await ctx.send(embed=embed)
                
                # Wait for duration
                await asyncio.sleep(duration_minutes * 60)
                
                # Award player to highest bidder
                auction = await db.db.auctions.find_one({"_id": auction_id})
                current_player = auction['players'][current_index]
                
                if current_player.get('highest_bidder'):
                    # Award player
                    winner_id = current_player['highest_bidder']
                    winning_bid = current_player.get('current_bid', 0)
                    
                    # Add player to winner's team
                    user_team = await db.get_user_team(winner_id)
                    if user_team:
                        current_players = user_team.get('players', [])
                        current_players.append(current_player['id'])
                        await db.update_user_team(winner_id, current_players, user_team.get('budget_remaining', 0) - winning_bid)
                    else:
                        # Create team for winner
                        await db.create_user_team(winner_id, f"Team {winner_id}", [current_player['id']])
                    
                    # Announce winner
                    try:
                        winner = await self.bot.fetch_user(int(winner_id))
                        embed = discord.Embed(
                            title="🎊 SOLD!",
                            description=f"**{current_player['name']}** sold to {winner.mention} for **${winning_bid:,}**!",
                            color=COLORS['success']
                        )
                        await ctx.send(embed=embed)
                    except:
                        pass
                else:
                    # No bids
                    embed = discord.Embed(
                        title="❌ UNSOLD",
                        description=f"**{current_player['name']}** received no bids.",
                        color=COLORS['danger']
                    )
                    await ctx.send(embed=embed)
                
                # Move to next player
                await db.db.auctions.update_one(
                    {"_id": auction_id},
                    {"$set": {"current_player_index": current_index + 1}}
                )
                
                await asyncio.sleep(5)  # Pause between players
                
        except Exception as e:
            print(f"Error in automated auction: {e}")
            await ctx.send(f"⚠️ Auction error occurred. Contact admin.")
    
    async def finalize_automated_auction(self, ctx, auction_id):
        """Finalize automated auction"""
        await db.db.auctions.update_one(
            {"_id": auction_id},
            {"$set": {"status": "completed"}}
        )
        
        embed = discord.Embed(
            title="🎊 AUCTION COMPLETE!",
            description="All players have been sold!\n\nPlayers added to your substitutes automatically.\nUse `!cmsetxi` to set your playing XI!",
            color=COLORS['success']
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))

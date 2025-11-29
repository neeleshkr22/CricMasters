"""
Auction Commands for Cric Mater Bot
"""
import discord
from discord.ext import commands
import asyncio

from config import COLORS, AUCTION_SETTINGS
from database.db import db


class AuctionCommands(commands.Cog):
    """Player auction commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='bid')
    async def place_bid(self, ctx, amount: int):
        """
        Place a bid in active auction
        Usage: cmbid 5000000
        """
        # Get active auction
        auction = await db.get_active_auction(ctx.guild.id)
        
        if not auction:
            await ctx.send("❌ No active auction in this server!")
            return
        
        # Check if user is participant
        participant = next(
            (p for p in auction.get('participants', []) if p['user_id'] == str(ctx.author.id)),
            None
        )
        
        if not participant:
            await ctx.send("❌ You are not registered for this auction! Contact an admin.")
            return
        
        # Place bid
        success, message = await db.place_bid(str(auction['_id']), ctx.author.id, amount)
        
        if success:
            # Get current player
            current_index = auction.get('current_player_index', 0)
            player = auction['players'][current_index]
            
            embed = discord.Embed(
                title="💰 Bid Placed!",
                description=f"**{ctx.author.display_name}** bid **${amount:,}** for **{player['name']}**!",
                color=COLORS['success']
            )
            
            embed.add_field(name="Current Highest Bid", value=f"${amount:,}", inline=True)
            embed.add_field(name="Budget Remaining", value=f"${participant['budget'] - amount:,}", inline=True)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ {message}")
    
    @commands.command(name='auctionstats')
    async def auction_stats(self, ctx):
        """
        View current auction status
        Usage: cmauctionstats
        """
        auction = await db.get_active_auction(ctx.guild.id)
        
        if not auction:
            await ctx.send("❌ No active auction in this server!")
            return
        
        current_index = auction.get('current_player_index', 0)
        total_players = len(auction['players'])
        current_player = auction['players'][current_index]
        
        embed = discord.Embed(
            title="🎪 Auction Status",
            description=f"Player {current_index + 1} of {total_players}",
            color=COLORS['gold']
        )
        
        # Current player info
        embed.add_field(
            name="📋 Current Player",
            value=f"**{current_player['name']}** {current_player['country']}\n"
                  f"Role: {current_player['role'].replace('_', ' ').title()}\n"
                  f"BAT: {current_player['batting']} | BOWL: {current_player['bowling']}",
            inline=False
        )
        
        # Bidding info
        current_bid = current_player.get('current_bid', 0)
        highest_bidder = current_player.get('highest_bidder')
        
        if highest_bidder:
            bidder = await self.bot.fetch_user(int(highest_bidder))
            embed.add_field(
                name="💰 Current Bid",
                value=f"**${current_bid:,}**\nby {bidder.mention}",
                inline=True
            )
        else:
            embed.add_field(
                name="💰 Base Price",
                value=f"**${current_player.get('base_price', 0):,}**",
                inline=True
            )
        
        # Participants
        participants = auction.get('participants', [])
        embed.add_field(
            name="👥 Participants",
            value=f"{len(participants)} teams registered",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='myauction')
    async def my_auction_team(self, ctx):
        """
        View your auction team
        Usage: cmmyauction
        """
        auction = await db.get_active_auction(ctx.guild.id)
        
        if not auction:
            await ctx.send("❌ No active auction in this server!")
            return
        
        participant = next(
            (p for p in auction.get('participants', []) if p['user_id'] == str(ctx.author.id)),
            None
        )
        
        if not participant:
            await ctx.send("❌ You are not registered for this auction!")
            return
        
        players = participant.get('players', [])
        budget = participant.get('budget', AUCTION_SETTINGS['initial_budget'])
        
        embed = discord.Embed(
            title=f"🎪 {ctx.author.display_name}'s Auction Team",
            description=f"**Budget Remaining:** ${budget:,}\n**Players:** {len(players)}/11",
            color=COLORS['primary']
        )
        
        if players:
            player_list = ""
            total_spent = AUCTION_SETTINGS['initial_budget'] - budget
            
            for idx, player in enumerate(players, 1):
                role_emoji = {
                    'batsman': '🏏',
                    'bowler': '⚡',
                    'all_rounder': '💎',
                    'wicket_keeper': '🧤'
                }.get(player['role'], '👤')
                
                player_list += f"{role_emoji} **{player['name']}** - ${player.get('current_bid', 0):,}\n"
            
            embed.add_field(name="Players", value=player_list, inline=False)
            embed.add_field(name="💵 Total Spent", value=f"${total_spent:,}", inline=True)
        else:
            embed.description += "\n\n*No players purchased yet*"
        
        await ctx.send(embed=embed)
    
    @commands.command(name='joinauction')
    async def join_auction(self, ctx):
        """
        Join an active auction
        Usage: cmjoinauction
        """
        auction = await db.get_active_auction(ctx.guild.id)
        
        if not auction:
            await ctx.send("❌ No active auction in this server!")
            return
        
        # Check if already joined
        participant = next(
            (p for p in auction.get('participants', []) if p['user_id'] == str(ctx.author.id)),
            None
        )
        
        if participant:
            await ctx.send("⚠️ You have already joined this auction!")
            return
        
        # Add participant
        await db.add_auction_participant(
            str(auction['_id']),
            ctx.author.id,
            ctx.author.display_name
        )
        
        embed = discord.Embed(
            title="✅ Joined Auction!",
            description=f"**{ctx.author.display_name}** has joined the auction!",
            color=COLORS['success']
        )
        
        embed.add_field(name="💵 Starting Budget", value=f"₹{AUCTION_SETTINGS['initial_budget']:,}", inline=True)
        embed.add_field(name="👥 Team Size", value=AUCTION_SETTINGS['team_size'], inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='tradeplayer')
    async def trade_player(self, ctx, target_user: discord.Member, give_player: str, receive_player: str = None):
        """
        Trade a player with another user
        Usage: cmtradeplayer @user "Player Name" ["Player Name"]
        If no receive_player, it's a free transfer
        """
        if target_user.bot:
            await ctx.send("❌ Cannot trade with bots!")
            return
        
        if target_user.id == ctx.author.id:
            await ctx.send("❌ You cannot trade with yourself!")
            return
        
        # Get both users' inventories
        sender_inventory = await db.get_user_inventory(ctx.author.id)
        receiver_inventory = await db.get_user_inventory(target_user.id)
        
        # Find player to give
        sender_players = sender_inventory.get('players', [])
        give_player_obj = None
        
        for item in sender_players:
            for player in item.get('players', []):
                if give_player.lower() in player['name'].lower():
                    give_player_obj = player
                    break
            if give_player_obj:
                break
        
        if not give_player_obj:
            await ctx.send(f"❌ You don't own a player named '{give_player}'!")
            return
        
        # Check if receive player exists (if specified)
        receive_player_obj = None
        if receive_player:
            receiver_players = receiver_inventory.get('players', [])
            
            for item in receiver_players:
                for player in item.get('players', []):
                    if receive_player.lower() in player['name'].lower():
                        receive_player_obj = player
                        break
                if receive_player_obj:
                    break
            
            if not receive_player_obj:
                await ctx.send(f"❌ {target_user.display_name} doesn't own '{receive_player}'!")
                return
        
        # Create trade offer
        trade_id = await db.db.trades.insert_one({
            "guild_id": str(ctx.guild.id),
            "sender_id": str(ctx.author.id),
            "sender_name": ctx.author.display_name,
            "receiver_id": str(target_user.id),
            "receiver_name": target_user.display_name,
            "give_player": give_player_obj,
            "receive_player": receive_player_obj,
            "status": "pending",
            "created_at": discord.utils.utcnow()
        })
        
        # Create trade embed
        embed = discord.Embed(
            title="🔄 Player Trade Offer",
            description=f"**{ctx.author.display_name}** wants to trade with **{target_user.display_name}**!",
            color=COLORS['warning']
        )
        
        embed.add_field(
            name=f"📤 {ctx.author.display_name} gives",
            value=f"**{give_player_obj['name']}** {give_player_obj['country']}\n"
                  f"Role: {give_player_obj['role'].title()}\n"
                  f"BAT: {give_player_obj['batting']} | BOWL: {give_player_obj['bowling']}\n"
                  f"Rarity: {give_player_obj['rarity'].title()}",
            inline=True
        )
        
        if receive_player_obj:
            embed.add_field(
                name=f"📥 {target_user.display_name} gives",
                value=f"**{receive_player_obj['name']}** {receive_player_obj['country']}\n"
                      f"Role: {receive_player_obj['role'].title()}\n"
                      f"BAT: {receive_player_obj['batting']} | BOWL: {receive_player_obj['bowling']}\n"
                      f"Rarity: {receive_player_obj['rarity'].title()}",
                inline=True
            )
        else:
            embed.add_field(
                name=f"📥 {target_user.display_name} gives",
                value="**Nothing** (Free Transfer)",
                inline=True
            )
        
        embed.add_field(
            name="⏳ Waiting for Response",
            value=f"{target_user.mention}, use:\n"
                  f"`cmaccepttrade {trade_id.inserted_id}` to accept\n"
                  f"`cmrejecttrade {trade_id.inserted_id}` to reject",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # DM the receiver
        try:
            dm = await target_user.create_dm()
            dm_embed = discord.Embed(
                title="🔄 New Trade Offer!",
                description=f"**{ctx.author.display_name}** wants to trade players with you!",
                color=COLORS['info']
            )
            dm_embed.add_field(name="Server", value=ctx.guild.name, inline=False)
            dm_embed.add_field(
                name="Trade Details",
                value=f"Check #{ctx.channel.name} in {ctx.guild.name}",
                inline=False
            )
            await dm.send(embed=dm_embed)
        except:
            pass
    
    @commands.command(name='accepttrade')
    async def accept_trade(self, ctx, trade_id: str):
        """
        Accept a trade offer
        Usage: cmaccepttrade [trade_id]
        """
        from bson import ObjectId
        
        try:
            # Get trade
            trade = await db.db.trades.find_one({"_id": ObjectId(trade_id)})
            
            if not trade:
                await ctx.send("❌ Trade not found!")
                return
            
            if trade['receiver_id'] != str(ctx.author.id):
                await ctx.send("❌ This trade is not for you!")
                return
            
            if trade['status'] != "pending":
                await ctx.send("❌ This trade is no longer available!")
                return
            
            # Execute trade
            sender_id = int(trade['sender_id'])
            receiver_id = int(trade['receiver_id'])
            give_player = trade['give_player']
            receive_player = trade.get('receive_player')
            
            # Remove players from inventories
            await db.db.economy.update_one(
                {"user_id": str(sender_id)},
                {"$pull": {"items.players": {"players": {"$elemMatch": {"id": give_player['id']}}}}}
            )
            
            if receive_player:
                await db.db.economy.update_one(
                    {"user_id": str(receiver_id)},
                    {"$pull": {"items.players": {"players": {"$elemMatch": {"id": receive_player['id']}}}}}
                )
            
            # Add players to new inventories
            await db.add_item_to_inventory(receiver_id, 'players', {'players': [give_player]})
            
            if receive_player:
                await db.add_item_to_inventory(sender_id, 'players', {'players': [receive_player]})
            
            # Mark trade as completed
            await db.db.trades.update_one(
                {"_id": ObjectId(trade_id)},
                {"$set": {"status": "completed", "completed_at": discord.utils.utcnow()}}
            )
            
            embed = discord.Embed(
                title="✅ Trade Completed!",
                description=f"Player trade between **{trade['sender_name']}** and **{trade['receiver_name']}** is complete!",
                color=COLORS['success']
            )
            
            embed.add_field(
                name=f"📤 {trade['sender_name']} traded",
                value=f"**{give_player['name']}** {give_player['country']}",
                inline=True
            )
            
            if receive_player:
                embed.add_field(
                    name=f"📤 {trade['receiver_name']} traded",
                    value=f"**{receive_player['name']}** {receive_player['country']}",
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"📥 {trade['receiver_name']} received",
                    value="Free Transfer!",
                    inline=True
                )
            
            await ctx.send(embed=embed)
            
            # DM both users
            try:
                sender = await self.bot.fetch_user(sender_id)
                dm = await sender.create_dm()
                await dm.send(embed=embed)
            except:
                pass
            
        except Exception as e:
            await ctx.send(f"❌ Error completing trade: {str(e)}")
    
    @commands.command(name='rejecttrade')
    async def reject_trade(self, ctx, trade_id: str):
        """
        Reject a trade offer
        Usage: cmrejecttrade [trade_id]
        """
        from bson import ObjectId
        
        try:
            # Get trade
            trade = await db.db.trades.find_one({"_id": ObjectId(trade_id)})
            
            if not trade:
                await ctx.send("❌ Trade not found!")
                return
            
            if trade['receiver_id'] != str(ctx.author.id):
                await ctx.send("❌ This trade is not for you!")
                return
            
            if trade['status'] != "pending":
                await ctx.send("❌ This trade is no longer available!")
                return
            
            # Mark trade as rejected
            await db.db.trades.update_one(
                {"_id": ObjectId(trade_id)},
                {"$set": {"status": "rejected", "rejected_at": discord.utils.utcnow()}}
            )
            
            embed = discord.Embed(
                title="❌ Trade Rejected",
                description=f"**{ctx.author.display_name}** rejected the trade offer.",
                color=COLORS['danger']
            )
            
            await ctx.send(embed=embed)
            
            # DM the sender
            try:
                sender = await self.bot.fetch_user(int(trade['sender_id']))
                dm = await sender.create_dm()
                dm_embed = discord.Embed(
                    title="❌ Trade Rejected",
                    description=f"**{ctx.author.display_name}** rejected your trade offer for **{trade['give_player']['name']}**.",
                    color=COLORS['danger']
                )
                await dm.send(embed=dm_embed)
            except:
                pass
            
        except Exception as e:
            await ctx.send(f"❌ Error rejecting trade: {str(e)}")
    
    @commands.command(name='mytrades')
    async def my_trades(self, ctx):
        """
        View your pending trades
        Usage: cmmytrades
        """
        # Get all pending trades for user
        trades = await db.db.trades.find({
            "$or": [
                {"sender_id": str(ctx.author.id)},
                {"receiver_id": str(ctx.author.id)}
            ],
            "status": "pending"
        }).to_list(length=10)
        
        if not trades:
            await ctx.send("✅ You have no pending trades!")
            return
        
        embed = discord.Embed(
            title="🔄 Your Pending Trades",
            description=f"Total: {len(trades)} trades",
            color=COLORS['info']
        )
        
        for trade in trades:
            trade_type = "Sent" if trade['sender_id'] == str(ctx.author.id) else "Received"
            other_user = trade['receiver_name'] if trade_type == "Sent" else trade['sender_name']
            
            # Safely get player names
            give_player_data = trade.get('give_player')
            receive_player_data = trade.get('receive_player')
            
            if trade_type == "Sent":
                give_player = give_player_data.get('name', 'Unknown') if give_player_data and isinstance(give_player_data, dict) else 'Unknown'
                receive_player = receive_player_data.get('name', 'Nothing') if receive_player_data and isinstance(receive_player_data, dict) else 'Nothing'
            else:
                give_player = receive_player_data.get('name', 'Nothing') if receive_player_data and isinstance(receive_player_data, dict) else 'Nothing'
                receive_player = give_player_data.get('name', 'Unknown') if give_player_data and isinstance(give_player_data, dict) else 'Unknown'
            
            embed.add_field(
                name=f"{trade_type} - {other_user}",
                value=f"**Give:** {give_player}\n**Get:** {receive_player}\n**ID:** `{trade['_id']}`",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='viewauction', aliases=['auctionlist', 'currentauction'])
    async def view_auction(self, ctx):
        """
        View the current auction with all players, prices, and bids
        Usage: !cmauction or !viewauction
        """
        auction = await db.get_active_auction(ctx.guild.id)
        
        if not auction:
            await ctx.send("❌ No active auction in this server!")
            return
        
        embed = discord.Embed(
            title="🎪 CURRENT AUCTION",
            description="Active players up for bidding",
            color=COLORS['gold']
        )
        
        # Show participants
        participants = auction.get('participants', [])
        if participants:
            participant_names = [p['username'] for p in participants[:10]]  # Show first 10
            embed.add_field(
                name=f"👥 Participants ({len(participants)})",
                value=", ".join(participant_names) if participant_names else "None",
                inline=False
            )
        
        # Show current player being bid on
        current_player_index = auction.get('current_player_index', 0)
        players_list = auction.get('players', [])
        
        if players_list and current_player_index < len(players_list):
            player = players_list[current_player_index]
            
            player_info = f"**{player['name']}** ({player.get('role', 'All-Rounder')})\n"
            player_info += f"⭐ Rating: {player.get('rating', 'N/A')}\n"
            player_info += f"🏏 Batting: {player.get('batting', 0)} | ⚾ Bowling: {player.get('bowling', 0)}\n\n"
            
            if player.get('current_bid', 0) > 0:
                highest_bidder = player.get('highest_bidder')
                bidder = ctx.guild.get_member(int(highest_bidder)) if highest_bidder else None
                bidder_name = bidder.display_name if bidder else "Unknown"
                player_info += f"💰 **Current Bid:** ₹{player['current_bid']:,} by {bidder_name}"
            else:
                player_info += f"💰 **Base Price:** ₹{player.get('base_price', 100000):,}\n⏳ Awaiting bids..."
            
            embed.add_field(name="🔥 CURRENT PLAYER", value=player_info, inline=False)
        
        # Show remaining players (upcoming)
        all_players = auction.get('players', [])
        if all_players and current_player_index < len(all_players):
            remaining = all_players[current_player_index + 1:]  # Skip current player
            if remaining:
                # Show first 10 remaining players
                player_names = []
                for i, player in enumerate(remaining[:10], 1):
                    player_names.append(f"{i}. **{player['name']}** - ₹{player.get('base_price', 100000):,}")
                
                if player_names:
                    embed.add_field(
                        name=f"📋 Upcoming Players ({len(remaining)})",
                        value="\n".join(player_names) + (f"\n... and {len(remaining) - 10} more" if len(remaining) > 10 else ""),
                        inline=False
                    )
        
        # Show sold players (players before current)
        if current_player_index > 0:
            sold = all_players[:current_player_index]
            recent_sold = []
            for player in sold[-5:]:  # Last 5 sold
                if player.get('highest_bidder'):
                    buyer_id = player['highest_bidder']
                    buyer = ctx.guild.get_member(int(buyer_id)) if buyer_id else None
                    buyer_name = buyer.display_name if buyer else "Unknown"
                    recent_sold.append(f"✅ **{player['name']}** → {buyer_name} (₹{player['current_bid']:,})")
            
            if recent_sold:
                embed.add_field(
                    name="🤝 Recently Sold",
                    value="\n".join(recent_sold),
                    inline=False
                )
        
        embed.set_footer(text="Use !cmbid <amount> to place a bid on the current player")
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AuctionCommands(bot))

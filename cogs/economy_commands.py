"""
Economy Commands for Cric Mater Bot
Coins, Shop, Packs, and Rewards System
"""
import discord
from discord.ext import commands
import random
from datetime import datetime, timedelta

from config import COLORS, ECONOMY_SETTINGS, SHOP_ITEMS, PLAYER_RARITIES
from database.db import db
from data.players import get_all_players, get_player_by_id
from utils.image_generator import image_gen


class EconomyCommands(commands.Cog):
    """Economy and shop commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='bal')
    async def balance(self, ctx, member: discord.Member = None):
        """
        View your or someone's coin balance
        Usage: cmbal [@user]
        """
        target = member or ctx.author
        balance = await db.get_user_balance(target.id)
        
        # Get economy data
        user_data = await db.db.economy.find_one({"user_id": str(target.id)})
        
        embed = discord.Embed(
            title=f"💰 {target.display_name}'s Balance",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="🪙 Coins", value=f"{balance:,}", inline=True)
        
        if user_data:
            embed.add_field(name="📈 Total Earned", value=f"{user_data.get('total_earned', 0):,}", inline=True)
            embed.add_field(name="📉 Total Spent", value=f"{user_data.get('total_spent', 0):,}", inline=True)
            
            # Active boosts
            boosts = await db.get_active_boosts(target.id)
            if boosts:
                boost_text = "\n".join([f"• {b['type']}: +{b['value']}" for b in boosts])
                embed.add_field(name="⚡ Active Boosts", value=boost_text, inline=False)
            
            # Items count
            items = user_data.get('items', [])
            embed.add_field(name="🎒 Items Owned", value=len(items), inline=True)
        
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text="Use cmshop to buy items!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='daily')
    async def daily_reward(self, ctx):
        """
        Claim your daily login reward
        Usage: cmdaily
        """
        success, result = await db.claim_daily_reward(ctx.author.id)
        
        if success:
            embed = discord.Embed(
                title="🎁 Daily Reward Claimed!",
                description=f"You received **{result:,} coins**!",
                color=COLORS['success']
            )
            embed.set_footer(text="Come back tomorrow for more!")
        else:
            # Calculate time remaining
            hours = int(result // 3600)
            minutes = int((result % 3600) // 60)
            
            embed = discord.Embed(
                title="⏰ Daily Reward Not Ready",
                description=f"You can claim your next reward in **{hours}h {minutes}m**",
                color=COLORS['warning']
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='shop')
    async def shop(self, ctx, category: str = None):
        """
        View the shop and buy items
        Usage: cmshop [category]
        Categories: boosts, consumables, packs
        """
        if not category:
            # Show shop categories
            embed = discord.Embed(
                title="🏪 Cric Mater Shop",
                description="Choose a category to browse!",
                color=COLORS['primary']
            )
            
            embed.add_field(
                name="⚡ Stat Boosts",
                value="`cmshop boosts`\nTemporary stat increases for matches",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Consumables",
                value="`cmshop consumables`\nOne-time use items for advantages",
                inline=False
            )
            
            embed.add_field(
                name="📦 Player Packs",
                value="`cmshop packs`\nOpen packs to get random players",
                inline=False
            )
            
            balance = await db.get_user_balance(ctx.author.id)
            embed.set_footer(text=f"Your balance: {balance:,} coins")
            
            await ctx.send(embed=embed)
            return
        
        # Show specific category
        category = category.lower()
        
        if category == 'boosts':
            items = SHOP_ITEMS['stat_boosts']
            title = "⚡ Stat Boosts"
            desc = "Temporary boosts to improve your players' performance!"
        elif category == 'consumables':
            items = SHOP_ITEMS['consumables']
            title = "🎯 Consumables"
            desc = "One-time use items for special advantages!"
        elif category == 'packs':
            items = SHOP_ITEMS['packs']
            title = "📦 Player Packs"
            desc = "Open packs to get random players!"
        else:
            await ctx.send("❌ Invalid category! Use: boosts, consumables, or packs")
            return
        
        embed = discord.Embed(
            title=title,
            description=desc,
            color=COLORS['primary']
        )
        
        for item_id, item_data in items.items():
            value = f"**Price:** {item_data['price']:,} coins\n"
            
            if 'boost' in item_data:
                value += f"**Effect:** +{item_data['boost']} stats for {item_data['duration']} matches\n"
            elif 'effect' in item_data:
                value += f"**Effect:** {item_data['effect']}\n"
            elif 'players' in item_data:
                value += f"**Contains:** {item_data['players']} {item_data['rarity']} players\n"
            
            value += f"**Buy:** `cmbuy {item_id}`"
            
            embed.add_field(
                name=f"{item_data['name']}",
                value=value,
                inline=True
            )
        
        balance = await db.get_user_balance(ctx.author.id)
        embed.set_footer(text=f"Your balance: {balance:,} coins")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='buy')
    async def buy_item(self, ctx, item_id: str):
        """
        Buy an item from the shop
        Usage: cmbuy [item_id]
        Example: cmbuy batting_boost
        """
        # Find item in shop
        item_data = None
        category = None
        
        # Economy balancing: ensure fair pack prices and rewards
        for cat, items in SHOP_ITEMS.items():
            if item_id in items:
                item_data = items[item_id].copy()
                category = cat
                # Adjust pack prices and rewards for fairness
                if category == 'packs':
                    # Example: bronze pack is cheapest, diamond is most expensive
                    if item_id == 'bronze_pack':
                        item_data['price'] = max(1000, item_data.get('price', 1000))
                    elif item_id == 'silver_pack':
                        item_data['price'] = max(5000, item_data.get('price', 5000))
                    elif item_id == 'gold_pack':
                        item_data['price'] = max(20000, item_data.get('price', 20000))
                    elif item_id == 'diamond_pack':
                        item_data['price'] = max(50000, item_data.get('price', 50000))
                break
        
        if not item_data:
            await ctx.send("❌ Item not found! Use `cmshop` to see available items.")
            return
        else:
            await ctx.send(f"🛒 You selected: {item_data['name']} for {item_data['price']} coins.")
        
        # Check balance
        balance = await db.get_user_balance(ctx.author.id)
        price = item_data['price']
        
        if balance < price:
            await ctx.send(f"❌ Insufficient coins! You need {price:,} coins but have {balance:,}.")
            return
        else:
            await ctx.send(f"💰 Purchase successful! {price} coins deducted.")
        
        # Process purchase
        success = await db.remove_coins(ctx.author.id, price, f"Bought {item_data['name']}")
        
        if not success:
            await ctx.send("❌ Purchase failed! Please try again.")
            return
        
        # Add item to inventory
        if category == 'stat_boosts':
            await db.add_boost(
                ctx.author.id,
                item_id,
                item_data['boost'],
                item_data['duration']
            )
            
            embed = discord.Embed(
                title="✅ Boost Purchased!",
                description=f"You bought **{item_data['name']}**!",
                color=COLORS['success']
            )
            embed.add_field(name="Effect", value=f"+{item_data['boost']} stats", inline=True)
            embed.add_field(name="Duration", value=f"{item_data['duration']} matches", inline=True)
            
        elif category == 'consumables':
            await db.add_item_to_inventory(ctx.author.id, item_id, item_data)
            
            embed = discord.Embed(
                title="✅ Item Purchased!",
                description=f"You bought **{item_data['name']}**!",
                color=COLORS['success']
            )
            embed.add_field(name="Effect", value=item_data['effect'], inline=False)
            
        elif category == 'packs':
            # Open pack immediately
            players = await self.generate_pack_contents(item_data)
            await db.add_item_to_inventory(ctx.author.id, 'players', {'players': players})

            # Add players to user's team subs
            user_team = await db.get_user_team(ctx.author.id)
            player_ids = [p['id'] for p in players]

            if user_team:
                current_players = user_team.get('players', [])
                # Add new players to subs (max 20 total squad size)
                new_squad = current_players + player_ids
                if len(new_squad) > 20:
                    new_squad = new_squad[:20]  # Cap at 20
                await db.update_user_team(ctx.author.id, new_squad, user_team.get('budget_remaining', 0))

                # Check and auto-fill Playing XI if empty
                playing_xi = await db.get_playing_xi(ctx.author.id)
                if not playing_xi or len(playing_xi) == 0:
                    # Add up to 11 new cards to Playing XI
                    await db.set_playing_xi(ctx.author.id, player_ids[:11])
            else:
                # Create new team with these players if user doesn't have one
                team_name = f"{ctx.author.name}'s Team"
                await db.create_user_team(ctx.author.id, team_name, player_ids[:20])
                # Also set Playing XI if team is new
                await db.set_playing_xi(ctx.author.id, player_ids[:11])

            embed = discord.Embed(
                title="📦 Pack Opened!",
                description=f"You opened a **{item_data['name']}**!",
                color=COLORS['gold']
            )

            for player in players:
                rarity_data = PLAYER_RARITIES[player['rarity']]
                embed.add_field(
                    name=f"{rarity_data['emoji']} {player['name']}",
                    value=f"{player['role'].title()} | {player['country']}\nBAT: {player['batting']} | BOWL: {player['bowling']}",
                    inline=True
                )

            embed.add_field(
                name="✅ Added to Team",
                value="Players added to your squad!\nUse `!cmteam` to view your team.\nUse `!cmsetxi` to set your playing XI.\nUse `!cmswap` to swap players.",
                inline=False
            )

            embed.set_footer(text=f"New balance: {balance - price:,} coins")
        
        await ctx.send(embed=embed)
    
    async def generate_pack_contents(self, pack_data):
        """Generate random players for a pack based on OVR"""
        from utils.ovr_calculator import calculate_ovr
        all_players = get_all_players()
        # Per new economy rules, each purchased/opened pack yields exactly ONE player card
        num_players = 1
        pack_rarity = pack_data['rarity']
        
        # Improved rarity weights for fair progression
        rarity_weights = {
            'common': {'common': 90, 'rare': 8, 'epic': 1.5, 'legendary': 0.5},
            'rare': {'common': 60, 'rare': 30, 'epic': 8, 'legendary': 2},
            'epic': {'common': 20, 'rare': 40, 'epic': 30, 'legendary': 10},
            'legendary': {'common': 5, 'rare': 20, 'epic': 35, 'legendary': 40},
        }
        
        weights = rarity_weights[pack_rarity]
        selected_players = []
        
        for _ in range(num_players):
            # Determine rarity
            rarity = random.choices(
                list(weights.keys()),
                weights=list(weights.values())
            )[0]
            
            # Select player based on rarity (OVR-based)
            if rarity == 'legendary':
                eligible = [p for p in all_players if calculate_ovr(p) >= 90]
            elif rarity == 'epic':
                eligible = [p for p in all_players if 85 <= calculate_ovr(p) < 90]
            elif rarity == 'rare':
                eligible = [p for p in all_players if 80 <= calculate_ovr(p) < 85]
            else:  # common
                eligible = [p for p in all_players if calculate_ovr(p) < 80]
            
            if not eligible:
                eligible = all_players
            
            player = random.choice(eligible).copy()
            player['rarity'] = rarity
            
            # Apply rarity boost (small percentage increase)
            boost = PLAYER_RARITIES[rarity]['boost']
            player['batting'] = min(99, int(player['batting'] * (1 + boost)))
            player['bowling'] = min(99, int(player['bowling'] * (1 + boost)))
            
            selected_players.append(player)
        
        return selected_players
    
    @commands.command(name='inventory')
    async def view_inventory(self, ctx):
        """
        View your inventory
        Usage: cminventory
        """
        items = await db.get_user_inventory(ctx.author.id)
        boosts = await db.get_active_boosts(ctx.author.id)
        
        embed = discord.Embed(
            title=f"🎒 {ctx.author.display_name}'s Inventory",
            color=COLORS['primary']
        )
        
        # Active boosts
        if boosts:
            boost_text = ""
            for boost in boosts:
                expiry = boost['expiry']
                time_left = (expiry - datetime.utcnow()).days
                boost_text += f"• **{boost['type']}**: +{boost['value']} ({time_left} days left)\n"
            embed.add_field(name="⚡ Active Boosts", value=boost_text, inline=False)
        
        # Consumables
        consumables = [item for item in items if item.get('data', {}).get('effect')]
        if consumables:
            cons_text = ""
            for item in consumables[:10]:
                cons_text += f"• {item['data'].get('name', 'Item')}\n"
            embed.add_field(name="🎯 Consumables", value=cons_text or "None", inline=True)
        
        # Player cards
        player_items = [item for item in items if item.get('item_id') == 'players']
        total_players = sum(len(item.get('data', {}).get('players', [])) for item in player_items)
        
        if total_players > 0:
            embed.add_field(name="👥 Player Cards", value=f"{total_players} cards", inline=True)
        
        if not items and not boosts:
            embed.description = "Your inventory is empty! Visit `cmshop` to buy items."
        
        balance = await db.get_user_balance(ctx.author.id)
        embed.set_footer(text=f"Balance: {balance:,} coins")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='records')
    async def match_records(self, ctx, member: discord.Member = None):
        """
        View detailed match records
        Usage: cmrecords [@user]
        """
        target = member or ctx.author
        
        # Get recent matches
        matches = await db.get_user_matches(target.id, limit=10)
        stats = await db.get_user_stats(target.id)
        
        if not stats:
            await ctx.send(f"❌ {target.mention} hasn't played any matches yet!")
            return
        
        embed = discord.Embed(
            title=f"📊 {target.display_name}'s Match Records",
            color=COLORS['info']
        )
        
        # Overall stats
        embed.add_field(name="🎮 Matches", value=stats['matches_played'], inline=True)
        embed.add_field(name="🏆 Wins", value=stats['wins'], inline=True)
        embed.add_field(name="💔 Losses", value=stats['losses'], inline=True)
        embed.add_field(name="📈 Win Rate", value=f"{stats['win_rate']:.1f}%", inline=True)
        embed.add_field(name="🏏 Total Runs", value=stats['total_runs'], inline=True)
        embed.add_field(name="⚡ Total Wickets", value=stats['total_wickets'], inline=True)
        embed.add_field(name="🔥 Highest Score", value=stats['highest_score'], inline=True)
        
        # Recent matches
        if matches:
            recent_text = ""
            for match in matches[:5]:
                result = "W" if match.get('winner') == str(target.id) else "L"
                score = match.get('team1_score', {}).get('runs', 0)
                recent_text += f"{result} - {score} runs\n"
            
            embed.add_field(name="📋 Recent Matches", value=recent_text, inline=False)
        
        # Coins earned
        balance = await db.get_user_balance(target.id)
        embed.add_field(name="💰 Total Coins", value=f"{balance:,}", inline=True)
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='trade')
    async def trade(self, ctx, target: discord.Member, amount: int):
        """
        Trade/send coins to another user
        Usage: !cmtrade @user <amount>
        """
        if target.bot:
            await ctx.send("❌ Cannot trade with bots!")
            return
        
        if target.id == ctx.author.id:
            await ctx.send("❌ Cannot trade with yourself!")
            return
        
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        
        # Check sender balance
        sender_balance = await db.get_user_balance(ctx.author.id)
        
        if sender_balance < amount:
            await ctx.send(f"❌ Insufficient balance! You have {sender_balance:,} coins.")
            return
        
        # Perform trade
        try:
            # Deduct from sender
            await db.update_user_balance(ctx.author.id, -amount)
            # Add to receiver
            await db.update_user_balance(target.id, amount)
            
            embed = discord.Embed(
                title="💸 Trade Successful!",
                description=f"{ctx.author.mention} sent **{amount:,}** coins to {target.mention}",
                color=COLORS['success']
            )
            
            sender_new_balance = await db.get_user_balance(ctx.author.id)
            receiver_new_balance = await db.get_user_balance(target.id)
            
            embed.add_field(name=f"{ctx.author.display_name}'s Balance", value=f"{sender_new_balance:,} coins", inline=True)
            embed.add_field(name=f"{target.display_name}'s Balance", value=f"{receiver_new_balance:,} coins", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Trade failed: {str(e)}")


async def setup(bot):
    await bot.add_cog(EconomyCommands(bot))

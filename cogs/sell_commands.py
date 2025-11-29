"""
Enhanced sell command for player management
"""
import discord
from discord.ext import commands

from config import COLORS
from database.db import db
from data.players import get_player_by_id
from utils.ovr_calculator import calculate_ovr, get_market_value


class SellCommands(commands.Cog):
    """Sell players for coins"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='sell')
    async def sell_player(self, ctx, player_id: str = None):
        """
        Sell a player for 55% of their market value
        Usage: !cmsell <player_id>
        Example: !cmsell bat_001
        
        Or use: !cmsell to see your sellable players
        
        Rules:
        - Can't sell players in your Playing XI
        - Can't sell admin-assigned players (from cmassignteam)
        - Players from packs/auctions/claims can be sold
        - Get 55% of player's market value back
        """
        user_id = str(ctx.author.id)
        
        # Get user team
        user_team = await db.get_user_team(user_id)
        if not user_team:
            await ctx.send("❌ You don't have a team yet!")
            return
        
        all_players = user_team.get('players', [])
        if not all_players:
            await ctx.send("❌ You don't have any players!")
            return
        
        # Get playing XI
        playing_xi = await db.get_playing_xi(user_id)
        if not playing_xi:
            playing_xi = []
        
        # Get admin-assigned players (players that can't be sold)
        admin_assigned = user_team.get('admin_assigned_players', [])
        
        # Calculate sellable players (not in XI, not admin-assigned)
        sellable_players = [p for p in all_players if p not in playing_xi and p not in admin_assigned]
        
        # If no player_id provided, show sellable players
        if not player_id:
            if not sellable_players:
                embed = discord.Embed(
                    title="❌ No Players to Sell",
                    description="All your players are either in your Playing XI or are admin-assigned and cannot be sold.",
                    color=COLORS['danger']
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="💰 Sellable Players",
                description=f"You have **{len(sellable_players)}** players you can sell.\n\nUse `!cmsell <player_id>` to sell a player for 55% value.",
                color=COLORS['primary']
            )
            
            # Group by role
            batsmen = []
            bowlers = []
            all_rounders = []
            wicket_keepers = []
            
            for pid in sellable_players:
                player = get_player_by_id(pid)
                if player:
                    overall = calculate_ovr(player)
                    market_value = get_market_value(overall)
                    
                    sell_value = int(market_value * 0.55)
                    
                    player_text = f"`{pid}` - {player['name']} {player['country']}\nOVR: {overall:.1f} | Sell: {sell_value:,} coins"
                    
                    if player['role'] == 'batsman':
                        batsmen.append(player_text)
                    elif player['role'] == 'bowler':
                        bowlers.append(player_text)
                    elif player['role'] == 'all_rounder':
                        all_rounders.append(player_text)
                    elif player['role'] == 'wicket_keeper':
                        wicket_keepers.append(player_text)
            
            if wicket_keepers:
                embed.add_field(name="🧤 Wicket Keepers", value="\n".join(wicket_keepers[:5]), inline=False)
            if batsmen:
                embed.add_field(name="🏏 Batsmen", value="\n".join(batsmen[:5]), inline=False)
            if all_rounders:
                embed.add_field(name="⚡ All-Rounders", value="\n".join(all_rounders[:5]), inline=False)
            if bowlers:
                embed.add_field(name="⚾ Bowlers", value="\n".join(bowlers[:5]), inline=False)
            
            if len(sellable_players) > 20:
                embed.set_footer(text=f"Showing first 20 of {len(sellable_players)} sellable players")
            else:
                embed.set_footer(text="Use !cmsubs to see all your substitute players")
            
            await ctx.send(embed=embed)
            return
        
        # Validate player_id
        if player_id not in all_players:
            await ctx.send(f"❌ You don't own player `{player_id}`!")
            return
        
        # Check if player is in Playing XI
        if player_id in playing_xi:
            await ctx.send("❌ You can't sell a player in your Playing XI! Use `!cmswap` to move them to substitutes first.")
            return
        
        # Check if player is admin-assigned
        if player_id in admin_assigned:
            await ctx.send("❌ This player was assigned by an admin and cannot be sold!")
            return
        
        # Get player details
        player = get_player_by_id(player_id)
        if not player:
            await ctx.send(f"❌ Player `{player_id}` not found in database!")
            return
        
        # Calculate sell value
        overall = calculate_ovr(player)
        market_value = get_market_value(overall)
        
        sell_value = int(market_value * 0.55)
        
        # Confirmation embed
        embed = discord.Embed(
            title="💰 Confirm Sale",
            description=f"Are you sure you want to sell this player?",
            color=COLORS['warning']
        )
        
        embed.add_field(
            name=f"{player['name']} {player['country']}",
            value=f"**Role:** {player['role'].replace('_', ' ').title()}\n"
                  f"**BAT:** {player['batting']} | **BOWL:** {player['bowling']}\n"
                  f"**Overall:** {overall:.1f}",
            inline=False
        )
        
        embed.add_field(name="💵 Market Value", value=f"{market_value:,} coins", inline=True)
        embed.add_field(name="💰 You Get (55%)", value=f"{sell_value:,} coins", inline=True)
        
        embed.set_footer(text="React with ✅ to sell or ❌ to cancel (30s)")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        
        def check(reaction, user):
            return user.id == ctx.author.id and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == msg.id
        
        try:
            import asyncio
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            if str(reaction.emoji) == "❌":
                embed = discord.Embed(
                    title="❌ Sale Cancelled",
                    description=f"You kept **{player['name']}** in your team.",
                    color=COLORS['danger']
                )
                await ctx.send(embed=embed)
                return
            
            # Sell the player
            # Remove from team
            updated_players = [p for p in all_players if p != player_id]
            await db.update_user_team(user_id, updated_players, user_team.get('budget_remaining', 0))
            
            # Add coins
            await db.award_match_coins(user_id, sell_value)
            
            # Success embed
            embed = discord.Embed(
                title="✅ Player Sold!",
                description=f"You sold **{player['name']}** {player['country']}!",
                color=COLORS['success']
            )
            
            embed.add_field(name="💰 Coins Received", value=f"{sell_value:,} coins", inline=True)
            
            # Show new balance
            user_balance = await db.get_user_balance(user_id)
            embed.add_field(name="💵 New Balance", value=f"{user_balance:,} coins", inline=True)
            
            embed.set_footer(text="Use !cmshop to buy new packs or join auctions!")
            
            await ctx.send(embed=embed)
            
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏰ Sale Timeout",
                description="Sale cancelled due to no response.",
                color=COLORS['danger']
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(SellCommands(bot))

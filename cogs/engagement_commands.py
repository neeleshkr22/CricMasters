"""
Engagement Commands - Keep users active and engaged
"""
import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import random

from config import COLORS
from database.db import db
from utils.ovr_calculator import calculate_ovr


class EngagementCommands(commands.Cog):
    """Commands to keep users engaged"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='claim')
    async def hourly_claim(self, ctx):
        """
        Claim hourly coins and build your streak!
        Usage: !cmclaim
        
        Rewards:
        - Base: 1,000 coins every hour
        - 3-day streak: +500 bonus
        - 7-day streak: +1,000 bonus + Gold Pack
        - 30-day streak: +5,000 bonus + Legendary Pack
        """
        user_id = str(ctx.author.id)
        
        # Get user economy data
        user = await db.get_economy_user(user_id)
        
        if not user:
            await ctx.send("❌ You need to register first! Use `!cmdebut`")
            return
        
        # Check last claim
        last_claim = user.get('last_claim')
        current_time = datetime.utcnow()
        
        if last_claim:
            time_diff = current_time - last_claim
            
            if time_diff.total_seconds() < 3600:  # 1 hour
                minutes_left = 60 - int(time_diff.total_seconds() / 60)
                embed = discord.Embed(
                    title="⏰ Too Soon!",
                    description=f"You can claim again in **{minutes_left} minutes**!",
                    color=COLORS['warning']
                )
                embed.set_footer(text="Come back soon!")
                await ctx.send(embed=embed)
                return
        
        # Calculate streak
        current_streak = user.get('claim_streak', 0)
        last_claim_date = last_claim.date() if last_claim else None
        yesterday = (current_time - timedelta(days=1)).date()
        
        if last_claim_date == yesterday or last_claim_date == current_time.date():
            # Continue streak
            if last_claim_date == yesterday:
                current_streak += 1
        else:
            # Reset streak
            current_streak = 1
        
        # Calculate rewards
        base_coins = 1000
        bonus_coins = 0
        bonus_items = []
        
        if current_streak >= 3:
            bonus_coins += 500
        if current_streak >= 7:
            bonus_coins += 1000
            bonus_items.append("🎁 Gold Pack")
        if current_streak >= 30:
            bonus_coins += 5000
            bonus_items.append("💎 Legendary Pack")
        
        total_coins = base_coins + bonus_coins
        
        # Generate random player card with rarity-based selection
        from data.players import get_all_players
        from utils.ovr_calculator import calculate_ovr
        all_players = get_all_players()
        
        # Determine rarity first (harder to get better cards)
        rarity_roll = random.randint(1, 1000)
        if rarity_roll <= 700:  # 70%
            rarity = 'common'
            # Filter players with OVR 60-79
            eligible_players = [p for p in all_players if 60 <= calculate_ovr(p) < 80]
        elif rarity_roll <= 900:  # 20%
            rarity = 'rare'
            # Filter players with OVR 80-84
            eligible_players = [p for p in all_players if 80 <= calculate_ovr(p) < 85]
        elif rarity_roll <= 980:  # 8%
            rarity = 'epic'
            # Filter players with OVR 85-89
            eligible_players = [p for p in all_players if 85 <= calculate_ovr(p) < 90]
        else:  # 2%
            rarity = 'legendary'
            # Filter top players with OVR 90+
            eligible_players = [p for p in all_players if calculate_ovr(p) >= 90]
        
        # If no eligible players in rarity tier, fallback to all players
        if not eligible_players:
            eligible_players = all_players
        
        random_player = random.choice(eligible_players).copy()
        
        random_player['rarity'] = rarity
        
        # Apply rarity boost (small percentage increase)
        from config import PLAYER_RARITIES
        rarity_boost = PLAYER_RARITIES[rarity]['boost']
        random_player['batting'] = min(99, int(random_player['batting'] * (1 + rarity_boost)))
        random_player['bowling'] = min(99, int(random_player['bowling'] * (1 + rarity_boost)))
        
        # Update database
        await db.db.economy.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "last_claim": current_time,
                    "claim_streak": current_streak
                },
                "$inc": {"coins": total_coins, "balance": total_coins}
            }
        )
        
        # Add player to team and auto-add to Playing XI if less than 11 players
        user_team = await db.get_user_team(user_id)
        if user_team:
            current_players = user_team.get('players', [])
            current_players.append(random_player['id'])
            await db.update_user_team(user_id, current_players, user_team.get('budget_remaining', 0))
            
            # Auto-add to Playing XI if less than 11 players
            playing_xi = await db.get_playing_xi(user_id)
            if not playing_xi:
                playing_xi = []
            
            if len(playing_xi) < 11:
                playing_xi.append(random_player['id'])
                await db.set_playing_xi(user_id, playing_xi)
        else:
            # Create team if doesn't exist
            await db.create_user_team(user_id, f"{ctx.author.name}'s Team", [random_player['id']])
            # Set first player in Playing XI
            await db.set_playing_xi(user_id, [random_player['id']])
        
        # Award bonus packs
        if "🎁 Gold Pack" in bonus_items:
            await db.add_item_to_inventory(user_id, "gold_pack", {"name": "Gold Pack", "type": "pack"})
        if "💎 Legendary Pack" in bonus_items:
            await db.add_item_to_inventory(user_id, "legendary_pack", {"name": "Legendary Pack", "type": "pack"})
        
        # Create embed
        rarity_data = PLAYER_RARITIES[rarity]
        embed = discord.Embed(
            title="💰 Hourly Claim!",
            description=f"You claimed **{total_coins:,} coins** + 1 Player Card!",
            color=COLORS['success']
        )
        
        embed.add_field(name="💵 Base Reward", value=f"{base_coins:,} coins", inline=True)
        if bonus_coins > 0:
            embed.add_field(name="🎁 Streak Bonus", value=f"+{bonus_coins:,} coins", inline=True)
        
        # Show player card
        overall = calculate_ovr(random_player)
        embed.add_field(
            name=f"🎴 {rarity_data['emoji']} Player Card",
            value=f"**{random_player['name']}** {random_player['country']}\n"
                  f"{random_player['role'].replace('_', ' ').title()}\n"
                  f"BAT: {random_player['batting']} | BOWL: {random_player['bowling']}\n"
                  f"Overall: {overall:.1f} | {rarity.upper()}",
            inline=False
        )
        
        embed.add_field(name="🔥 Current Streak", value=f"**{current_streak} days**", inline=False)
        
        if bonus_items:
            embed.add_field(name="🎁 Bonus Items", value="\n".join(bonus_items), inline=False)
        
        # Show next milestone
        next_milestone = None
        if current_streak < 3:
            next_milestone = f"3 days (+500 coins bonus)"
        elif current_streak < 7:
            next_milestone = f"7 days (+1,000 coins + Gold Pack)"
        elif current_streak < 30:
            next_milestone = f"30 days (+5,000 coins + Legendary Pack)"
        
        if next_milestone:
            embed.add_field(name="🎯 Next Milestone", value=next_milestone, inline=False)
        
        embed.set_footer(text="Claim again in 1 hour! Don't break your streak!")
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='challenge')
    async def challenge_user(self, ctx, opponent: discord.Member = None, bet: int = 0):
        """
        Challenge another user to a quick 5-over match!
        Usage: !cmchallenge @user <bet_amount>
        Examples:
            !cmchallenge @Neelesh          # Free friendly match
            !cmchallenge @Neelesh 10000    # 10k coin bet match
        
        How it works:
        - Quick 5-over match
        - Winner takes the bet pot
        - Both players must have enough coins
        - Accept within 60 seconds
        """
        if not opponent:
            await ctx.send("❌ Mention a user to challenge! Example: `!cmchallenge @user 5000`")
            return
        
        if opponent.bot:
            await ctx.send("❌ You can't challenge bots!")
            return
        
        if opponent.id == ctx.author.id:
            await ctx.send("❌ You can't challenge yourself!")
            return
        
        challenger_id = str(ctx.author.id)
        opponent_id = str(opponent.id)
        
        # Get both users
        challenger = await db.get_economy_user(challenger_id)
        opponent_data = await db.get_economy_user(opponent_id)
        
        if not challenger:
            await ctx.send("❌ You need to register first! Use `!cmdebut`")
            return
        
        if not opponent_data:
            await ctx.send(f"❌ {opponent.mention} needs to register first! Tell them to use `!cmdebut`")
            return
        
        # Check teams
        challenger_team = await db.get_user_team(challenger_id)
        opponent_team = await db.get_user_team(opponent_id)
        
        if not challenger_team or not challenger_team.get('players'):
            await ctx.send("❌ You need a team first! Use `!cmauction` or open packs.")
            return
        
        if not opponent_team or not opponent_team.get('players'):
            await ctx.send(f"❌ {opponent.mention} needs a team first!")
            return
        
        # Validate bet
        if bet < 0:
            await ctx.send("❌ Bet amount must be positive!")
            return
        
        if bet > 0:
            if challenger.get('coins', 0) < bet:
                await ctx.send(f"❌ You don't have enough coins! You have {challenger.get('coins', 0):,} coins.")
                return
            
            if opponent_data.get('coins', 0) < bet:
                await ctx.send(f"❌ {opponent.mention} doesn't have enough coins!")
                return
        
        # Create challenge embed
        embed = discord.Embed(
            title="⚔️ CHALLENGE ISSUED!",
            description=f"{ctx.author.mention} challenges {opponent.mention} to a match!",
            color=COLORS['warning']
        )
        
        embed.add_field(name="🎯 Match Type", value="5 Overs", inline=True)
        embed.add_field(name="💰 Bet Amount", value=f"{bet:,} coins" if bet > 0 else "Friendly (No bet)", inline=True)
        embed.add_field(name="🏆 Winner Gets", value=f"{bet * 2:,} coins" if bet > 0 else "Glory", inline=True)
        
        embed.set_footer(text=f"{opponent.name}, react with ✅ to accept or ❌ to decline (60s)")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        
        def check(reaction, user):
            return user.id == opponent.id and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == msg.id
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            
            if str(reaction.emoji) == "❌":
                embed = discord.Embed(
                    title="❌ Challenge Declined",
                    description=f"{opponent.mention} declined the challenge!",
                    color=COLORS['danger']
                )
                await ctx.send(embed=embed)
                return
            
            # Challenge accepted!
            embed = discord.Embed(
                title="✅ Challenge Accepted!",
                description=f"Match is starting between {ctx.author.mention} and {opponent.mention}!",
                color=COLORS['success']
            )
            await ctx.send(embed=embed)
            
            # Deduct bet amounts
            if bet > 0:
                await db.deduct_coins(challenger_id, bet)
                await db.deduct_coins(opponent_id, bet)
            
            # Start the match
            # Note: This will use your existing match system but with 5 overs
            await ctx.send(f"🏏 Starting match! Use `!cmplay @{opponent.name}` to begin.\n💡 **Note:** Admin needs to adjust match to 5 overs for quick challenge mode.")
            
            # TODO: Integrate with actual match system
            # For now, just refund if no match system integration
            if bet > 0:
                await ctx.send("⚠️ Challenge mode under development. Coins refunded.")
                await db.award_match_coins(challenger_id, bet)
                await db.award_match_coins(opponent_id, bet)
            
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏰ Challenge Expired",
                description=f"{opponent.mention} didn't respond in time!",
                color=COLORS['danger']
            )
            await ctx.send(embed=embed)


    @commands.command(name='cd', aliases=['cooldown', 'cooldowns'])
    async def check_cooldowns(self, ctx):
        """
        Check cooldowns for all time-gated commands
        Usage: !cmcd or !cmcooldown
        """
        user_id = str(ctx.author.id)
        current_time = datetime.utcnow()
        
        # Get user data
        user_data = await db.get_economy_user(user_id)
        
        if not user_data:
            await ctx.send("❌ You need to register first! Use `!cmdebut`")
            return
        
        embed = discord.Embed(
            title="⏰ COOLDOWNS",
            description="Time remaining until you can use these commands again",
            color=COLORS['primary']
        )
        
        cooldowns = []
        
        # 1. Claim cooldown (1 hour)
        last_claim = user_data.get('last_claim')
        if last_claim:
            time_diff = current_time - last_claim
            if time_diff.total_seconds() < 3600:
                seconds_left = 3600 - int(time_diff.total_seconds())
                minutes_left = seconds_left // 60
                seconds = seconds_left % 60
                cooldowns.append(("💰 Claim", f"in {minutes_left}m {seconds}s", False))
            else:
                cooldowns.append(("💰 Claim", "✅ Ready", True))
        else:
            cooldowns.append(("💰 Claim", "✅ Ready", True))
        
        # 2. Daily pack cooldown (24 hours)
        last_pack = user_data.get('last_pack_claim')
        if last_pack:
            time_diff = current_time - last_pack
            if time_diff.total_seconds() < 86400:
                seconds_left = 86400 - int(time_diff.total_seconds())
                hours_left = seconds_left // 3600
                minutes_left = (seconds_left % 3600) // 60
                cooldowns.append(("🎁 Daily Pack", f"in {hours_left}h {minutes_left}m", False))
            else:
                cooldowns.append(("🎁 Daily Pack", "✅ Ready", True))
        else:
            cooldowns.append(("🎁 Daily Pack", "✅ Ready", True))
        
        # 3. Claim streak info
        current_streak = user_data.get('claim_streak', 0)
        if last_claim:
            last_claim_date = last_claim.date()
            today = current_time.date()
            
            if last_claim_date == today:
                # Already claimed today, show tomorrow
                tomorrow = current_time + timedelta(days=1)
                tomorrow_midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
                time_until_midnight = tomorrow_midnight - current_time
                hours = int(time_until_midnight.total_seconds() // 3600)
                minutes = int((time_until_midnight.total_seconds() % 3600) // 60)
                cooldowns.append(("🔥 Streak Continues", f"in {hours}h {minutes}m", False))
            else:
                yesterday = (current_time - timedelta(days=1)).date()
                if last_claim_date == yesterday:
                    # Can claim today to continue streak
                    cooldowns.append(("🔥 Streak Continues", "✅ Claim now!", True))
                else:
                    # Streak broken
                    cooldowns.append(("🔥 Streak", "❌ Broken - Start new", False))
        
        # 4. Weekly leaderboard reset
        weekday = current_time.weekday()  # 0=Monday
        days_until_monday = (7 - weekday) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        cooldowns.append(("🏆 Weekly Reset", f"in {days_until_monday} days", False))
        
        # 5. Monthly leaderboard reset
        import calendar
        days_in_month = calendar.monthrange(current_time.year, current_time.month)[1]
        days_until_end = days_in_month - current_time.day
        cooldowns.append(("🏆 Monthly Reset", f"in {days_until_end} days", False))
        
        # Add fields
        for name, status, is_ready in cooldowns:
            embed.add_field(
                name=name,
                value=status,
                inline=True
            )
        
        # Show current streak
        if current_streak > 0:
            embed.add_field(
                name="🔥 Current Streak",
                value=f"**{current_streak} days**",
                inline=False
            )
            
            # Show next milestone
            if current_streak < 3:
                next_milestone = "3 days (+500 coins)"
            elif current_streak < 7:
                next_milestone = "7 days (+1,000 coins + Gold Pack)"
            elif current_streak < 30:
                next_milestone = "30 days (+5,000 coins + Legendary Pack)"
            else:
                next_milestone = "Max rewards unlocked!"
            
            embed.add_field(
                name="🎯 Next Milestone",
                value=next_milestone,
                inline=False
            )
        
        embed.set_footer(text="Use !cmclaim to claim your hourly reward!")
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(EngagementCommands(bot))

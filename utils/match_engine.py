"""
Professional Cricket Match Engine
Complete ball-by-ball interactive match system with professional graphics
"""
import discord
from discord.ui import Button, View, Select
import random
import asyncio
from datetime import datetime
import logging
import traceback

from config import COLORS
from data.players import get_player_by_id
from utils.match_tracker import MatchTracker
from utils.match_graphics import match_graphics
from utils.stadium_manager import stadium_manager
from utils.celebration_manager import celebration_gifs
from utils.ovr_calculator import calculate_ovr
from database.db import Database

# Setup logging
logger = logging.getLogger('match_engine')
logger.setLevel(logging.DEBUG)

class BowlerSelectView(View):
    """Dropdown to select bowler from playing XI"""
    
    def __init__(self, bowling_user_id, bowling_team_xi, callback):
        super().__init__(timeout=60)
        self.bowling_user_id = bowling_user_id
        self.callback = callback
        self.selected_bowler = None
        
        # Create dropdown with all 11 players
        options = []
        for player_id in bowling_team_xi:
            player = get_player_by_id(player_id)
            if player:
                role_emoji = {"batsman": "🏏", "wicket_keeper": "🧤", "all_rounder": "⭐", "bowler": "⚾"}.get(player['role'], "👤")
                options.append(discord.SelectOption(
                    label=player['name'],
                    value=player_id,
                    description=f"Bowling: {player.get('bowling', 0)} | {player['country']}",
                    emoji=role_emoji
                ))
        
        select = Select(
            placeholder="Click to select bowler",
            options=options[:25],  # Discord limit
            custom_id="bowler_select"
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.bowling_user_id:
            await interaction.response.send_message("⚠️ Only the bowling team can select!", ephemeral=True)
            return
        
        self.selected_bowler = interaction.data['values'][0]
        
        # Disable dropdown
        for item in self.children:
            item.disabled = True
        
        try:
            await interaction.response.defer()
            await interaction.edit_original_response(view=self)
        except:
            pass
        
        await self.callback(interaction, self.selected_bowler)
        self.stop()


class PaceTypeSelectView(View):
    """First step for fast bowlers: Select pace type (Quick/Slow/Swing)"""
    
    def __init__(self, bowling_user_id, callback):
        super().__init__(timeout=60)
        self.bowling_user_id = bowling_user_id
        self.callback = callback
        
        pace_types = [
            ("Quick", "⚡", discord.ButtonStyle.danger),
            ("Outswing", "↗️", discord.ButtonStyle.primary),
            ("Inswing", "↖️", discord.ButtonStyle.primary),
            ("Reverse Swing", "↪️", discord.ButtonStyle.success),
            ("Slow", "🐌", discord.ButtonStyle.secondary)
        ]
        
        for pace, emoji, style in pace_types:
            button = Button(label=pace, emoji=emoji, style=style)
            button.callback = self.create_callback(pace)
            self.add_item(button)
    
    def create_callback(self, pace_type):
        async def button_callback(interaction: discord.Interaction):
            if interaction.user.id != self.bowling_user_id:
                await interaction.response.send_message("⚠️ Only the bowling team can select!", ephemeral=True)
                return
            
            # Instantly disable buttons and defer
            for item in self.children:
                item.disabled = True
            
            try:
                await interaction.response.defer()
                await interaction.edit_original_response(view=self)
            except:
                pass
            
            await self.callback(interaction, pace_type)
            self.stop()
        
        return button_callback


class BallLengthSelectView(View):
    """Second step for fast bowlers: Select ball length"""
    
    def __init__(self, bowling_user_id, pace_type, callback):
        super().__init__(timeout=60)
        self.bowling_user_id = bowling_user_id
        self.pace_type = pace_type
        self.callback = callback
        
        lengths = [
            ("Good Length", "📏", discord.ButtonStyle.primary),
            ("Full", "⬇️", discord.ButtonStyle.success),
            ("Yorker", "💥", discord.ButtonStyle.danger),
            ("Bouncer", "⬆️", discord.ButtonStyle.danger),
            ("Full Toss", "🎯", discord.ButtonStyle.secondary)
        ]
        
        for length, emoji, style in lengths:
            button = Button(label=length, emoji=emoji, style=style)
            button.callback = self.create_callback(length)
            self.add_item(button)
    
    def create_callback(self, length):
        async def button_callback(interaction: discord.Interaction):
            if interaction.user.id != self.bowling_user_id:
                await interaction.response.send_message("⚠️ Only the bowling team can select!", ephemeral=True)
                return
            
            # Combine pace type + length
            delivery = f"{self.pace_type} {length}"
            
            # Instantly disable and defer
            for item in self.children:
                item.disabled = True
            
            try:
                await interaction.response.defer()
                await interaction.edit_original_response(view=self)
            except:
                pass
            
            await self.callback(interaction, delivery)
            self.stop()
        
        return button_callback


class BowlingTypeSelectView(View):
    """Buttons to select bowling delivery type based on bowler's specialty"""
    
    def __init__(self, bowling_user_id, bowler_specialty, callback):
        super().__init__(timeout=60)
        self.bowling_user_id = bowling_user_id
        self.callback = callback
        self.selected_delivery = None
        
        # Delivery options based on bowler specialty
        # Off Spinners: Ashwin, Nathan Lyon, etc.
        if bowler_specialty == "off_spin":
            deliveries = [
                ("Off Spin", "🔃", discord.ButtonStyle.primary),
                ("Carrom Ball", "💫", discord.ButtonStyle.success),
                ("Doosra", "🌀", discord.ButtonStyle.danger),
                ("Arm Ball", "➡️", discord.ButtonStyle.secondary),
                ("Topspin", "↕️", discord.ButtonStyle.primary)
            ]
        # Leg Spinners: Kuldeep, Rashid Khan, Chahal, etc.
        elif bowler_specialty == "leg_spin":
            deliveries = [
                ("Leg Spin", "🔄", discord.ButtonStyle.primary),
                ("Googly", "🌪️", discord.ButtonStyle.danger),
                ("Flipper", "⚡", discord.ButtonStyle.success),
                ("Slider", "↘️", discord.ButtonStyle.secondary),
                ("Drifter", "〰️", discord.ButtonStyle.primary)
            ]
        # Fast Bowlers: Will use combo system now
        else:
            deliveries = []
        
        # Add buttons (max 5 per row)
        for i, (delivery, emoji, style) in enumerate(deliveries[:5]):
            button = Button(label=delivery, emoji=emoji, style=style, custom_id=f"bowl_{i}")
            button.callback = self.create_callback(delivery)
            self.add_item(button)
    
    def create_callback(self, delivery):
        async def button_callback(interaction: discord.Interaction):
            if interaction.user.id != self.bowling_user_id:
                await interaction.response.send_message("⚠️ Only the bowling team can select!", ephemeral=True)
                return
            
            self.selected_delivery = delivery
            
            # Instantly disable and defer
            for item in self.children:
                item.disabled = True
            
            try:
                await interaction.response.defer()
                await interaction.edit_original_response(view=self)
            except:
                pass
            
            await self.callback(interaction, delivery)
            self.stop()
        
        return button_callback


class BatsmanSelectView(View):
    """Dropdown to select batsman from playing XI"""
    
    def __init__(self, batting_user_id, batting_xi, available_batsmen, callback):
        super().__init__(timeout=60)
        self.batting_user_id = batting_user_id
        self.callback = callback
        self.selected_batsman = None
        
        # Create dropdown with available batsmen
        options = []
        for player_id in batting_xi:
            if player_id in available_batsmen:
                player = get_player_by_id(player_id)
                if player:
                    role_emoji = {"batsman": "🏏", "wicket_keeper": "🧤", "all_rounder": "⭐", "bowler": "⚾"}.get(player['role'], "👤")
                    options.append(discord.SelectOption(
                        label=player['name'],
                        value=player_id,
                        description=f"Batting: {player['batting']} | {player['country']}",
                        emoji=role_emoji
                    ))
        
        if not options:
            options.append(discord.SelectOption(label="No batsmen available", value="none"))
        
        select = Select(
            placeholder="Select batsman",
            options=options[:25],
            custom_id="batsman_select"
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.batting_user_id:
            await interaction.response.send_message("⚠️ Only the batting team can select!", ephemeral=True)
            return
        
        self.selected_batsman = interaction.data['values'][0]
        
        # Disable dropdown
        for item in self.children:
            item.disabled = True
        
        try:
            await interaction.response.defer()
            await interaction.edit_original_response(view=self)
        except:
            pass
        
        await self.callback(interaction, self.selected_batsman)
        self.stop()


class ShotSelectView(View):
    """8 shot selection buttons for batsman"""
    
    def __init__(self, batting_user_id, bowler_name, ball_speed, callback):
        super().__init__(timeout=60)
        self.batting_user_id = batting_user_id
        self.callback = callback
        self.selected_shot = None
        
        # Create 8 shot buttons in 2 rows
        shots_row1 = [
            ("Drive", "🏏", discord.ButtonStyle.success),
            ("Loft", "🚀", discord.ButtonStyle.danger),
            ("Defend", "🛡️", discord.ButtonStyle.secondary),
            ("Sweep", "🌊", discord.ButtonStyle.primary)
        ]
        
        shots_row2 = [
            ("Cut", "✂️", discord.ButtonStyle.primary),
            ("Leave", "👋", discord.ButtonStyle.secondary),
            ("Pull", "💪", discord.ButtonStyle.success),
            ("Flick", "⚡", discord.ButtonStyle.success)
        ]
        
        for shot, emoji, style in shots_row1:
            button = Button(label=shot, emoji=emoji, style=style, custom_id=f"shot_{shot.lower()}")
            button.callback = self.create_callback(shot.lower())
            self.add_item(button)
        
        for shot, emoji, style in shots_row2:
            button = Button(label=shot, emoji=emoji, style=style, custom_id=f"shot_{shot.lower()}")
            button.callback = self.create_callback(shot.lower())
            self.add_item(button)
    
    def create_callback(self, shot):
        async def button_callback(interaction: discord.Interaction):
            if interaction.user.id != self.batting_user_id:
                await interaction.response.send_message("⚠️ Only the batsman can choose!", ephemeral=True)
                return
            
            self.selected_shot = shot
            
            # Instantly disable and defer
            for item in self.children:
                item.disabled = True
            
            try:
                await interaction.response.defer()
                await interaction.edit_original_response(view=self)
            except:
                pass
            
            await self.callback(interaction, shot)
            self.stop()
        
        return button_callback


class ProfessionalMatchEngine:
    """Professional cricket match engine with full graphics"""
    
    def __init__(self, channel, batting_user_id, bowling_user_id, batting_xi, bowling_xi, 
                 overs, venue, innings, target, guild, difficulty="easy", batting_team_name=None, bowling_team_name=None):
        self.channel = channel
        self.batting_user_id = batting_user_id
        self.bowling_user_id = bowling_user_id
        self.batting_user = guild.get_member(batting_user_id)
        self.bowling_user = guild.get_member(bowling_user_id)
        self.batting_xi = batting_xi
        self.bowling_xi = bowling_xi
        self.batting_team_name = batting_team_name or f"{self.batting_user.display_name}'s Team"
        self.bowling_team_name = bowling_team_name or f"{self.bowling_user.display_name}'s Team"
        self.overs = overs
        self.venue = venue
        self.innings = innings
        self.target = target
        self.guild = guild
        self.difficulty = difficulty  # "easy" or "hard"
        
        # Initialize match tracker
        self.tracker = MatchTracker()
        
        # Current match state
        self.striker_id = None
        self.non_striker_id = None
        self.runs = 0
        self.wickets = 0
        self.balls = 0
        self.max_balls = overs * 6
        
        # Current bowler
        self.current_bowler_id = None
        
        # Available batsmen (not yet out)
        self.available_batsmen = batting_xi.copy()
        self.batsmen_selected = False
    
    async def start_innings(self):
        """Start the innings"""
        try:
            logger.info(f"Starting innings {self.innings}")
            
            # Show innings start with team XI
            logger.debug("Showing team XI")
            await self.show_team_xi()
            
            # Select opening batsmen
            logger.debug("Selecting openers")
            await self.select_openers()
            
            if not self.striker_id or not self.non_striker_id:
                await self.channel.send("❌ Failed to select openers!")
                return
            
            # Ball-by-ball loop
            logger.info(f"Starting ball-by-ball loop: {self.max_balls} balls, target: {self.target}")
            while self.balls < self.max_balls and self.wickets < 10:
                if self.target and self.runs >= self.target:
                    logger.info("Target reached!")
                    break
                
                # Select bowler at start of over
                ball_in_over = self.balls % 6
                logger.debug(f"Ball {self.balls + 1}, ball_in_over: {ball_in_over}")
                
                if ball_in_over == 0 or self.current_bowler_id is None:
                    logger.debug("Selecting bowler...")
                    await self.select_bowler()
                    
                    if not self.current_bowler_id:
                        logger.error("No bowler selected, breaking")
                        break
                    
                    logger.info(f"Bowler selected: {self.current_bowler_id}")
                
                # Select shot and play ball
                try:
                    logger.debug("Selecting shot...")
                    await self.select_shot()
                    logger.debug(f"Ball complete. Score: {self.runs}/{self.wickets}")
                except Exception as e:
                    error_msg = f"❌ Error in ball {self.balls + 1}: {str(e)}\n```{traceback.format_exc()}```"
                    logger.error(error_msg)
                    await self.channel.send(error_msg[:2000])  # Discord limit
                    break
                
                # Check if innings ended
                if self.balls >= self.max_balls or self.wickets >= 10:
                    logger.info(f"Innings ended: balls={self.balls}, wickets={self.wickets}")
                    break
                
                if self.target and self.runs >= self.target:
                    logger.info("Target chased!")
                    break
            
            # Show final innings summary
            logger.info("Showing innings summary")
            await self.show_innings_complete()
            
        except Exception as e:
            error_msg = f"❌ Fatal error in innings: {str(e)}\n```{traceback.format_exc()}```"
            logger.error(error_msg)
            await self.channel.send(error_msg[:2000])
    
    async def show_team_xi(self):
        """Show professional team XI display"""
        from utils.ovr_calculator import calculate_ovr
        
        # Calculate team OVR
        total_ovr = 0
        player_count = 0
        for player_id in self.batting_xi:
            player = get_player_by_id(player_id)
            if player:
                total_ovr += calculate_ovr(player)
                player_count += 1
        team_ovr = int(total_ovr / player_count) if player_count > 0 else 0
        
        embed = discord.Embed(
            title=f"🏏 {self.batting_team_name}",
            description=f"**( {self.batting_team_name} ) • OVR: {team_ovr}**\n\nCard | Player | OVR | BAT | BOWL | Country",
            color=0x2ecc71
        )
        
        # Group players by role
        for category, emoji in [("Batters", "🏏"), ("WK", "🧤"), ("All-Rounders", "⭐"), ("Bowlers", "⚾")]:
            players_text = []
            
            for player_id in self.batting_xi:
                player = get_player_by_id(player_id)
                if not player:
                    continue
                
                ovr = int(calculate_ovr(player))
                
                # Get rarity card emoji
                if ovr >= 90:
                    card = "☢️"
                elif ovr >= 85:
                    card = "💎"
                elif ovr >= 80:
                    card = "🏆"
                else:
                    card = "🎖️"
                
                if category == "Batters" and player['role'] == 'batsman':
                    players_text.append(f"{card}| {player['name']} | {ovr} | {player['batting']} | {player.get('bowling', 0)} | {player['country']}")
                elif category == "WK" and player['role'] == 'wicket_keeper':
                    players_text.append(f"{card}| {player['name']} | {ovr} | {player['batting']} | {player.get('bowling', 0)} | {player['country']}")
                elif category == "All-Rounders" and player['role'] == 'all_rounder':
                    players_text.append(f"{card}| {player['name']} | {ovr} | {player['batting']} | {player['bowling']} | {player['country']}")
                elif category == "Bowlers" and player['role'] == 'bowler':
                    players_text.append(f"{card}| {player['name']} | {ovr} | {player.get('batting', 0)} | {player['bowling']} | {player['country']}")
            
            if players_text:
                embed.add_field(name=f"{category} {emoji}", value="\n".join(players_text), inline=False)
        
        embed.set_footer(text=f"{self.batting_user.display_name} • Playing XI", icon_url=self.batting_user.display_avatar.url)
        
        await self.channel.send(embed=embed)
    
    async def select_openers(self):
        """Let batting team select opening batsmen"""
        # Select striker
        embed = discord.Embed(
            title="🏏 Select Opening Batsman (Striker)",
            description=f"{self.batting_user.mention}, choose your opening batsman:",
            color=COLORS['primary']
        )
        
        async def striker_callback(interaction, selected):
            self.striker_id = selected
            self.available_batsmen.remove(selected)
        
        view = BatsmanSelectView(self.batting_user_id, self.batting_xi, self.available_batsmen, striker_callback)
        await self.channel.send(embed=embed, view=view)
        await view.wait()
        
        if not self.striker_id:
            await self.channel.send(f"⏱️ **{self.batting_user.mention} didn't select opener!**\n❌ **Match Forfeited!** -500 coins penalty!")
            db = Database()
            await db.connect()
            await db.deduct_coins(self.batting_user_id, 500, "Match forfeit - opener timeout")
            await db.close()
            return
        
        # Select non-striker
        embed2 = discord.Embed(
            title="🏏 Select Non-Striker",
            description=f"{self.batting_user.mention}, choose the non-striker:",
            color=COLORS['primary']
        )
        
        async def non_striker_callback(interaction, selected):
            self.non_striker_id = selected
            self.available_batsmen.remove(selected)
        
        view2 = BatsmanSelectView(self.batting_user_id, self.batting_xi, self.available_batsmen, non_striker_callback)
        await self.channel.send(embed=embed2, view=view2)
        await view2.wait()
        
        if not self.non_striker_id:
            await self.channel.send(f"⏱️ **{self.batting_user.mention} didn't select non-striker!**\n❌ **Match Forfeited!** -500 coins penalty!")
            db = Database()
            await db.connect()
            await db.deduct_coins(self.batting_user_id, 500, "Match forfeit - non-striker timeout")
            await db.close()
            return
    
    async def select_new_batsman(self):
        """Let batting team select new batsman after wicket"""
        embed = discord.Embed(
            title="🏏 Wicket! Select New Batsman",
            description=f"{self.batting_user.mention}, choose the next batsman:",
            color=COLORS['danger']
        )
        
        async def callback(interaction, selected):
            self.striker_id = selected
            self.available_batsmen.remove(selected)
        
        view = BatsmanSelectView(self.batting_user_id, self.batting_xi, self.available_batsmen, callback)
        await self.channel.send(embed=embed, view=view)
        await view.wait()
        
        if not self.striker_id:
            await self.channel.send(f"⏱️ **{self.batting_user.mention} didn't select new batsman!**\n❌ **Match Forfeited!** -500 coins penalty!")
            db = Database()
            await db.connect()
            await db.deduct_coins(self.batting_user_id, 500, "Match forfeit - batsman selection timeout")
            await db.close()
            # Match ends here, wickets = 10 will end the loop
            self.wickets = 10
    
    async def select_bowler(self):
        """Let bowling team select a bowler"""
        over = self.balls // 6
        ball_in_over = (self.balls % 6) + 1
        
        prompt_embed = discord.Embed(
            title=f"Over is up, choose your next bowler @{self.bowling_user.name}",
            color=COLORS['primary']
        )
        
        async def callback(interaction, selected_bowler):
            self.current_bowler_id = selected_bowler
        
        view = BowlerSelectView(self.bowling_user_id, self.bowling_xi, callback)
        
        msg = await self.channel.send(embed=prompt_embed, view=view)
        await view.wait()
        
        if not self.current_bowler_id:
            await self.channel.send(f"⏱️ **{self.bowling_user.mention} didn't select bowler!**\n❌ **Match Forfeited!** -500 coins penalty!")
            db = Database()
            await db.connect()
            await db.deduct_coins(self.bowling_user_id, 500, "Match forfeit - bowler selection timeout")
            await db.close()
            return
    
    async def select_shot(self):
        """Let batsman select a shot"""
        try:
            logger.debug(f"select_shot called for ball {self.balls + 1}")
            
            bowler = get_player_by_id(self.current_bowler_id)
            if not bowler:
                logger.error(f"Bowler not found: {self.current_bowler_id}")
                await self.channel.send(f"❌ Error: Bowler not found!")
                return
            
            ball_speed = random.randint(130, 155)
            
            # Let bowler choose delivery type
            bowl_type_choice = None
            
            async def bowl_callback(interaction, selected_delivery):
                nonlocal bowl_type_choice
                bowl_type_choice = selected_delivery
                logger.info(f"Delivery selected: {selected_delivery}")
            
            # Determine bowler specialty based on name/type
            bowler_name = bowler['name'].lower()
            if any(name in bowler_name for name in ['ashwin', 'lyon', 'moeen', 'jadeja']):
                bowler_specialty = "off_spin"
            elif any(name in bowler_name for name in ['kuldeep', 'chahal', 'rashid', 'zampa', 'adil']):
                bowler_specialty = "leg_spin"
            elif bowler.get('bowl_type') == 'spin':
                # Default spinners to off spin if not identified
                bowler_specialty = "off_spin"
            else:
                bowler_specialty = "fast"
            
            # Fast bowlers use two-step combo selection
            if bowler_specialty == "fast":
                # Step 1: Select pace type
                pace_type = None
                
                async def pace_callback(interaction, selected_pace):
                    nonlocal pace_type
                    pace_type = selected_pace
                
                pace_view = PaceTypeSelectView(self.bowling_user_id, pace_callback)
                pace_msg = await self.channel.send(f"⚾ **{bowler['name']}**, choose pace & length:", view=pace_view)
                await pace_view.wait()
                
                if not pace_type:
                    await self.channel.send(f"⏱️ **{self.bowling_user.mention} didn't select pace type!**\n❌ **Match Forfeited!** -500 coins penalty!")
                    db = Database()
                    await db.connect()
                    await db.deduct_coins(self.bowling_user_id, 500, "Match forfeit - pace selection timeout")
                    await db.close()
                    return
                
                # Step 2: Select length (edit same message)
                async def length_callback(interaction, combined_delivery):
                    nonlocal bowl_type_choice
                    bowl_type_choice = combined_delivery
                
                length_view = BallLengthSelectView(self.bowling_user_id, pace_type, length_callback)
                try:
                    await pace_msg.edit(view=length_view)
                except:
                    await self.channel.send(view=length_view)
                await length_view.wait()
            else:
                # Spinners use single selection
                delivery_view = BowlingTypeSelectView(self.bowling_user_id, bowler_specialty, bowl_callback)
                await self.channel.send(f"⚾ **{bowler['name']}**, choose your delivery:", view=delivery_view)
                await delivery_view.wait()
            
            if not bowl_type_choice:
                # Punish for not selecting - end match
                await self.channel.send(f"⏱️ **{self.bowling_user.mention} didn't select delivery in time!**\n❌ **Match Forfeited!** -500 coins penalty!")
                db = Database()
                await db.connect()
                await db.deduct_coins(self.bowling_user_id, 500, "Match forfeit - delivery selection timeout")
                await db.close()
                return
            
            commentary = f"{bowler['name']}: {bowl_type_choice} at {ball_speed} kmph"
            logger.debug(f"Commentary: {commentary}")
            
            # Shot selection (removed scorecard display for faster flow)
            shot_choice = None
            
            async def callback(interaction, selected_shot):
                nonlocal shot_choice
                shot_choice = selected_shot
                batsman = get_player_by_id(self.striker_id)
                logger.info(f"Shot selected: {selected_shot} by {batsman['name']}")
                # Response handled by View's edit_message
            
            batsman = get_player_by_id(self.striker_id)
            if not batsman:
                logger.error(f"Batsman not found: {self.striker_id}")
                await self.channel.send(f"❌ Error: Batsman not found!")
                return
            
            logger.debug("Creating shot selection view")
            view = ShotSelectView(self.batting_user_id, bowler['name'], ball_speed, callback)
            
            shot_msg = await self.channel.send(f"🏏 **{batsman['name']}** facing {ball_speed}km/h", view=view)
            logger.debug("Waiting for shot selection...")
            await view.wait()
            
            if not shot_choice:
                await self.channel.send(f"⏱️ **{self.batting_user.mention} didn't select shot!**\n❌ **Match Forfeited!** -500 coins penalty!")
                db = Database()
                await db.connect()
                await db.deduct_coins(self.batting_user_id, 500, "Match forfeit - shot selection timeout")
                await db.close()
                return
            
            # Calculate outcome
            logger.debug(f"Processing ball with shot: {shot_choice}, bowl: {bowl_type_choice}")
            await self.process_ball(shot_choice, bowl_type_choice, ball_speed)
            
            # Show live scorecard after the ball
            if self.wickets < 10:
                # In easy mode, show the ball type. In hard mode, hide it
                if self.difficulty == "easy":
                    commentary = f"🎯 {bowler['name']}: **{bowl_type_choice}** at {ball_speed} kmph | {batsman['name']}: {shot_choice}"
                else:
                    commentary = f"{bowler['name']}: Mystery ball at {ball_speed} kmph | {batsman['name']}: {shot_choice}"
                await self.show_live_scorecard(commentary)
            
        except Exception as e:
            logger.error(f"Error in select_shot: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def process_ball(self, shot, bowl_type, ball_speed):
        """Process the ball and show result"""
        outcome = self.calculate_outcome(shot, bowl_type)
        
        self.balls += 1
        over = (self.balls - 1) // 6
        ball_in_over = ((self.balls - 1) % 6) + 1
        
        batsman = get_player_by_id(self.striker_id)
        bowler = get_player_by_id(self.current_bowler_id)
        
        # Track the ball
        self.tracker.add_ball(self.striker_id, self.current_bowler_id, 
                             outcome if outcome != 'wicket' and outcome != 'dot' else 0,
                             outcome if outcome == 'wicket' or outcome == 'dot' else outcome,
                             shot)
        
        # Handle outcome
        if outcome == 'wicket':
            self.wickets += 1
            
            # Show wicket celebration
            await self.show_wicket(batsman, bowler, ball_speed)
            
            # Select next batsman if not all out
            if self.wickets < 10 and self.available_batsmen:
                await self.select_new_batsman()
        
        elif outcome == 'dot':
            await self.show_ball_result("⚪ Dot Ball", f"{batsman['name']} defends", ball_speed)
        
        else:
            self.runs += outcome
            
            # Swap batsmen on odd runs
            if outcome in [1, 3]:
                self.striker_id, self.non_striker_id = self.non_striker_id, self.striker_id
            
            # Check for milestones
            batsman_stats = self.tracker.get_batsman_stats(self.striker_id)
            if batsman_stats:
                if batsman_stats['runs'] == 50:
                    await self.show_milestone(batsman, 50, batsman_stats)
                elif batsman_stats['runs'] == 100:
                    await self.show_milestone(batsman, 100, batsman_stats)
            
            # Show run result
            if outcome == 4:
                await self.show_ball_result("🎯 FOUR!", f"{batsman['name']} finds the boundary!", ball_speed, use_embed=True)
            elif outcome == 6:
                await self.show_ball_result("🚀 SIX!", f"{batsman['name']} clears the ropes!", ball_speed, use_embed=True)
            else:
                # Text only for 1,2,3 runs
                await self.channel.send(f"✅ **{outcome} RUN{'S' if outcome > 1 else ''}** - {batsman['name']} rotates strike")
    
    def calculate_outcome(self, shot, bowl_type):
        """Calculate outcome based on shot and bowl"""
        outcomes = {
            'defend': [('dot', 70), (1, 25), ('wicket', 5)],
            'drive': [(4, 30), (2, 25), (1, 20), ('dot', 15), ('wicket', 10)],
            'loft': [(6, 25), (4, 20), (1, 15), ('wicket', 40)],
            'sweep': [(4, 30), (2, 25), (1, 20), ('wicket', 25)],
            'cut': [(4, 35), (2, 20), (1, 25), ('dot', 10), ('wicket', 10)],
            'leave': [('dot', 95), ('wicket', 5)],
            'pull': [(6, 20), (4, 30), (1, 20), ('wicket', 30)],
            'flick': [(2, 30), (1, 40), (4, 15), ('wicket', 15)]
        }
        
        weights = outcomes.get(shot, [('dot', 50), (1, 30), ('wicket', 20)])
        choices, probs = zip(*weights)
        return random.choices(choices, weights=probs)[0]
    
    async def show_live_scorecard(self, commentary):
        """Show professional live scorecard with both batsmen"""
        striker_stats = self.tracker.get_batsman_stats(self.striker_id)
        non_striker_stats = self.tracker.get_batsman_stats(self.non_striker_id)
        bowler_stats = self.tracker.get_bowler_stats(self.current_bowler_id)
        
        if not striker_stats:
            striker_stats = {'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'strike_rate': 0}
        if not non_striker_stats:
            non_striker_stats = {'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'strike_rate': 0}
        if not bowler_stats:
            bowler_stats = {'overs': 0, 'runs': 0, 'wickets': 0, 'economy': 0}
        
        striker = get_player_by_id(self.striker_id)
        non_striker = get_player_by_id(self.non_striker_id)
        bowler = get_player_by_id(self.current_bowler_id)
        
        # Create beautiful scorecard embed
        embed = discord.Embed(
            title=f"⚡ {self.batting_user.name} {self.runs}/{self.wickets} ({(self.balls // 6)}.{self.balls % 6})",
            description=f"🎯 vs {self.bowling_user.name} {'| Target: ' + str(self.target) if self.target else ''}",
            color=discord.Color.blue()
        )
        
        # Batsmen stats - Beautiful formatting
        batsmen_text = f"```\n"
        batsmen_text += f"{'BATSMAN':<20} R    B   4s  6s   SR\n"
        batsmen_text += f"{'─' * 45}\n"
        batsmen_text += f"★ {striker['name']:<17} {striker_stats['runs']:<4} {striker_stats['balls']:<3} {striker_stats['fours']:<3} {striker_stats['sixes']:<3} {striker_stats['strike_rate']:>6.1f}\n"
        batsmen_text += f"  {non_striker['name']:<17} {non_striker_stats['runs']:<4} {non_striker_stats['balls']:<3} {non_striker_stats['fours']:<3} {non_striker_stats['sixes']:<3} {non_striker_stats['strike_rate']:>6.1f}\n"
        batsmen_text += f"```"
        embed.add_field(name="🏏 BATTING", value=batsmen_text, inline=False)
        
        # Partnership & Run Rate
        partnership = self.tracker.get_partnership()
        current_rr = (self.runs / (self.balls / 6)) if self.balls > 0 else 0
        req_rr = ((self.target - self.runs) / ((self.max_balls - self.balls) / 6)) if self.target and self.balls < self.max_balls else 0
        
        rates_text = f"```\n"
        rates_text += f"Partnership: {partnership['runs']}({partnership['balls']})\n"
        
        if self.target:
            rates_text += f"CRR: {current_rr:.2f}  |  RRR: {req_rr:.2f}\n"
        else:
            rates_text += f"CRR: {current_rr:.2f}  |  RRR: ---\n"
        
        rates_text += f"```"
        embed.add_field(name="📊 PARTNERSHIP", value=rates_text, inline=False)
        
        # Bowler stats
        bowler_text = f"```\n"
        bowler_text += f"{bowler['name']:<20} O: {bowler_stats['overs']:.1f}  R: {bowler_stats['runs']}  W: {bowler_stats['wickets']}\n"
        bowler_text += f"```"
        embed.add_field(name="⚾ BOWLING", value=bowler_text, inline=False)
        
        # Timeline - Last 12 balls
        timeline = self.tracker.innings_data['timeline'][-12:]
        timeline_emojis = []
        for ball in timeline:
            if ball == 'W':
                timeline_emojis.append('🔴')
            elif ball == '6':
                timeline_emojis.append('6️⃣')
            elif ball == '4':
                timeline_emojis.append('4️⃣')
            elif ball == '•':
                timeline_emojis.append('⚫')
            else:
                timeline_emojis.append(ball)
        
        timeline_text = " ".join(timeline_emojis) if timeline_emojis else "First ball..."
        embed.add_field(name="📈 THIS OVER", value=timeline_text, inline=False)
        
        # Commentary
        embed.add_field(name="📡 COMMENTARY", value=commentary, inline=False)
        
        # Target info
        if self.target:
            need = self.target - self.runs
            balls_left = self.max_balls - self.balls
            target_footer = f"Need {need} runs from {balls_left} balls"
            embed.set_footer(text=target_footer)
        
        await self.channel.send(embed=embed)
    
    async def show_ball_result(self, title, description, ball_speed, use_embed=True):
        """Show ball result"""
        if use_embed:
            embed = discord.Embed(
                title=title,
                description=description,
                color=COLORS['success']
            )
            await self.channel.send(embed=embed)
        else:
            await self.channel.send(f"**{title}** - {description}")
    
    async def show_wicket(self, batsman, bowler, ball_speed):
        """Show wicket with GIF and scorecard"""
        batsman_stats = self.tracker.get_batsman_stats(self.striker_id)
        
        # Get celebration GIF
        gif_url = celebration_gifs.get_wicket_gif(bowler['name'])
        
        # Show wicket commentary
        dismissals = ["bowled", "caught", "lbw", "stumped", "run out"]
        dismissal = random.choice(dismissals)
        
        await self.channel.send(f"🔴 **OUT!** {dismissal.title()} by {bowler['name']}! {batsman['name']} IS OUT 🔥")
        
        if gif_url:
            embed = discord.Embed(color=discord.Color.red())
            embed.set_image(url=gif_url)
            await self.channel.send(embed=embed)
        
        # Create wicket card
        wicket_card = match_graphics.create_wicket_card(
            batsman['name'],
            batsman_stats['runs'],
            batsman_stats['balls'],
            batsman_stats['fours'],
            batsman_stats['sixes'],
            batsman_stats['strike_rate'],
            dismissal,
            bowler['name']
        )
        
        await self.channel.send(file=discord.File(wicket_card, "wicket.png"))
    
    async def show_milestone(self, batsman, milestone, stats):
        """Show milestone celebration"""
        # Get batting GIF
        if milestone == 50:
            gif_url = celebration_gifs.get_fifty_gif(batsman['name'])
        else:
            gif_url = celebration_gifs.get_century_gif(batsman['name'])
        
        milestone_text = "FIFTY" if milestone == 50 else "CENTURY"
        await self.channel.send(f"🎉 **{milestone_text}!** {batsman['name']} reaches {milestone}! 🔥🔥🔥")
        
        if gif_url:
            embed = discord.Embed(color=discord.Color.gold())
            embed.set_image(url=gif_url)
            await self.channel.send(embed=embed)
        
        # Create milestone card
        milestone_card = match_graphics.create_milestone_card(
            batsman['name'],
            stats['runs'],
            stats['balls'],
            stats['fours'],
            stats['sixes'],
            stats['strike_rate'],
            milestone
        )
        
        await self.channel.send(file=discord.File(milestone_card, f"{milestone}.png"))
    
    async def show_innings_complete(self):
        """Show innings complete with full analytics and scorecard"""
        # Create comprehensive innings scorecard
        embed = discord.Embed(
            title=f"📊 INNINGS {self.innings} COMPLETE",
            description=f"**{self.batting_user.name}** - **{self.runs}/{self.wickets}** ({(self.balls // 6)}.{self.balls % 6} overs)",
            color=discord.Color.green() if self.innings == 1 else discord.Color.blue()
        )
        
        # Batting Scorecard
        batting_text = "```\n"
        batting_text += f"{'BATSMAN':<20} R    B   4s  6s   SR\n"
        batting_text += f"{'─' * 50}\n"
        
        for batsman_id in self.batting_xi:
            stats = self.tracker.get_batsman_stats(batsman_id)
            if stats and stats.get('balls', 0) > 0:
                player = get_player_by_id(batsman_id)
                batting_text += f"{player['name']:<20} {stats['runs']:<4} {stats['balls']:<3} {stats['fours']:<3} {stats['sixes']:<3} {stats['strike_rate']:>6.1f}\n"
        
        batting_text += f"{'─' * 50}\n"
        batting_text += f"{'EXTRAS':<20} {0}\n"  # TODO: Track extras
        batting_text += f"{'TOTAL':<20} {self.runs}/{self.wickets}\n"
        batting_text += f"```"
        embed.add_field(name="🏏 BATTING", value=batting_text, inline=False)
        
        # Bowling Figures
        bowling_text = "```\n"
        bowling_text += f"{'BOWLER':<20} O    R   W   Econ\n"
        bowling_text += f"{'─' * 50}\n"
        
        for bowler_id in self.bowling_xi:
            stats = self.tracker.get_bowler_stats(bowler_id)
            if stats and stats['overs'] > 0:
                player = get_player_by_id(bowler_id)
                bowling_text += f"{player['name']:<20} {stats['overs']:.1f}  {stats['runs']:<3} {stats['wickets']:<3} {stats['economy']:>5.2f}\n"
        
        bowling_text += f"```"
        embed.add_field(name="⚾ BOWLING", value=bowling_text, inline=False)
        
        # Match Summary
        run_rate = (self.runs / (self.balls / 6)) if self.balls > 0 else 0
        summary = f"**Run Rate:** {run_rate:.2f}\n"
        summary += f"**Overs:** {(self.balls // 6)}.{self.balls % 6}/{self.overs}.0\n"
        
        if self.innings == 1:
            summary += f"\n🎯 **Target:** {self.runs + 1} runs"
            embed.add_field(name="📈 SUMMARY", value=summary, inline=False)
        else:
            if self.runs >= self.target:
                summary += f"\n🏆 **{self.batting_user.name} WINS by {10 - self.wickets} wickets!**"
            else:
                summary += f"\n🏆 **{self.bowling_user.name} WINS by {self.target - self.runs - 1} runs!**"
            embed.add_field(name="📈 RESULT", value=summary, inline=False)
        
        await self.channel.send(embed=embed)
        
        # Show wagon wheel
        if self.tracker.innings_data['shot_zones']:
            wagon_wheel = match_graphics.create_wagon_wheel(self.tracker.innings_data['shot_zones'])
            await self.channel.send(file=discord.File(wagon_wheel, "wagon_wheel.png"))
        
        # If innings 1, start innings 2
        if self.innings == 1:
            # Swap teams and start next innings
            next_engine = ProfessionalMatchEngine(
                self.channel,
                self.bowling_user_id,  # Swap
                self.batting_user_id,   # Swap
                self.bowling_xi,        # Swap
                self.batting_xi,        # Swap
                self.overs,
                self.venue,
                2,  # Innings 2
                self.runs + 1,  # Target
                self.guild,
                self.difficulty  # Pass difficulty to 2nd innings
            )
            await next_engine.start_innings()
        else:
            # Match complete - determine winner and show final scorecard
            await self.show_final_scorecard()
    
    async def show_final_scorecard(self):
        """Show comprehensive final match scorecard with both innings"""
        # Determine winner
        if self.runs >= self.target:
            winner = self.batting_user
            winner_team = f"{self.batting_user.name}"
            result_text = f"🏆 **{winner.mention} WON BY {10 - self.wickets} WICKETS!** 🏆"
        else:
            winner = self.bowling_user
            winner_team = f"{self.bowling_user.name}"
            result_text = f"🏆 **{winner.mention} WON BY {self.target - self.runs - 1} RUNS!** 🏆"
        
        # Create comprehensive scorecard embed
        embed = discord.Embed(
            title="📊 FINAL MATCH SCORECARD 📊",
            description=result_text,
            color=discord.Color.gold()
        )
        
        # Get innings 1 data from the first engine (stored when creating second innings)
        # For now, we'll show current innings data
        # TODO: Store innings 1 data to display both innings
        
        # Show current (2nd) innings batting
        batting_text = "```\n"
        batting_text += f"{'BATSMAN':<20} R    B   4s  6s   SR\n"
        batting_text += f"{'─' * 50}\n"
        
        for batsman_id in self.batting_xi:
            stats = self.tracker.get_batsman_stats(batsman_id)
            if stats and stats.get('balls', 0) > 0:
                player = get_player_by_id(batsman_id)
                batting_text += f"{player['name']:<20} {stats['runs']:<4} {stats['balls']:<3} {stats['fours']:<3} {stats['sixes']:<3} {stats['strike_rate']:>6.1f}\n"
        
        batting_text += f"{'─' * 50}\n"
        batting_text += f"{'TOTAL':<20} {self.runs}/{self.wickets} ({(self.balls // 6)}.{self.balls % 6} overs)\n"
        batting_text += f"```"
        embed.add_field(name=f"🏏 {self.batting_user.name.upper()} INNINGS", value=batting_text, inline=False)
        
        # Show bowling figures
        bowling_text = "```\n"
        bowling_text += f"{'BOWLER':<20} O    R   W   Econ\n"
        bowling_text += f"{'─' * 50}\n"
        
        for bowler_id in self.bowling_xi:
            stats = self.tracker.get_bowler_stats(bowler_id)
            if stats and stats['overs'] > 0:
                player = get_player_by_id(bowler_id)
                bowling_text += f"{player['name']:<20} {stats['overs']:.1f}  {stats['runs']:<3} {stats['wickets']:<3} {stats['economy']:>5.2f}\n"
        
        bowling_text += f"```"
        embed.add_field(name=f"⚾ {self.bowling_user.name.upper()} BOWLING", value=bowling_text, inline=False)
        
        # Match info
        match_info = f"**Stadium:** {self.venue}\n"
        match_info += f"**Overs:** {self.overs}\n"
        match_info += f"**Target:** {self.target}\n"
        match_info += f"**Match Date:** {datetime.now().strftime('%d %B %Y')}"
        embed.add_field(name="📌 MATCH INFO", value=match_info, inline=False)
        
        # Show wagon wheel for final innings
        if self.tracker.innings_data['shot_zones']:
            wagon_wheel = match_graphics.create_wagon_wheel(self.tracker.innings_data['shot_zones'])
            await self.channel.send(file=discord.File(wagon_wheel, "final_wagon_wheel.png"))
        
        # Show Manhattan for final innings
        if self.tracker.innings_data['runs_per_over']:
            manhattan = match_graphics.create_manhattan_graph(self.tracker.innings_data['runs_per_over'])
            await self.channel.send(file=discord.File(manhattan, "final_manhattan.png"))
        
        await self.channel.send(embed=embed)
        
        # Show winner celebration GIF
        win_gif = celebration_gifs.get_match_win_gif(winner_team)
        if win_gif:
            win_embed = discord.Embed(color=discord.Color.gold())
            win_embed.set_image(url=win_gif)
            await self.channel.send(embed=win_embed)
        
        # Save match history to database
        await self.save_match_history(winner)
    
    async def save_match_history(self, winner):
        """Save match result to database"""
        db = Database()
        await db.connect()
        
        try:
            # Determine match result details
            if self.runs >= self.target:
                # Batting team won
                winner_id = str(self.batting_user_id)
                loser_id = str(self.bowling_user_id)
                win_by = f"{10 - self.wickets} wickets"
                winner_score = f"{self.runs}/{self.wickets}"
                loser_score = f"{self.target - 1}/{10}"
            else:
                # Bowling team won
                winner_id = str(self.bowling_user_id)
                loser_id = str(self.batting_user_id)
                win_by = f"{self.target - self.runs - 1} runs"
                winner_score = f"{self.target - 1}/{10}"
                loser_score = f"{self.runs}/{self.wickets}"
            
            # Prepare match data
            match_data = {
                "team1_user": str(self.batting_user_id),
                "team1_name": self.batting_user.name,
                "team1_score": f"{self.runs}/{self.wickets}",
                "team1_overs": f"{(self.balls // 6)}.{self.balls % 6}",
                "team2_user": str(self.bowling_user_id),
                "team2_name": self.bowling_user.name,
                "team2_score": f"{self.target - 1}/{10}",  # Assuming innings 1 all out or full overs
                "team2_overs": f"{self.overs}.0",
                "winner_id": winner_id,
                "winner_name": winner.name,
                "win_by": win_by,
                "venue": self.venue,
                "overs": self.overs,
                "match_type": f"{self.overs}-over match",
                "created_at": datetime.utcnow()
            }
            
            # Save to database
            await db.save_match(match_data)
            
            # Update win/loss records
            await db.update_match_result(winner_id, won=True)
            await db.update_match_result(loser_id, won=False)
            
            # Award coins
            await db.award_match_coins(winner_id, 5000, "Match victory")
            await db.award_match_coins(loser_id, 1000, "Participation reward")
            
        except Exception as e:
            logger.error(f"Error saving match history: {e}")
        finally:
            await db.close()

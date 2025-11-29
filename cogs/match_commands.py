"""
Match Commands - Start and manage cricket matches
"""
import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import asyncio
from datetime import datetime

from config import *
from database.db import db
from data.players import get_player_by_id
from utils.stadium_manager import stadium_manager


class MatchJoinView(View):
    """Interactive view for players to join a match"""
    
    def __init__(self, creator_id, overs, match_info, venue, weather, umpire, pitch, cog):
        super().__init__(timeout=180)
        self.creator_id = creator_id
        self.overs = overs
        self.match_info = match_info
        self.venue = venue
        self.weather = weather
        self.umpire = umpire
        self.pitch = pitch
        self.cog = cog
        self.players = [creator_id]
        self.match_started = False
    
    @discord.ui.button(label="Join Match", style=discord.ButtonStyle.success, emoji="✅")
    async def join_button(self, interaction: discord.Interaction, button: Button):
        """Handle player joining the match"""
        
        if interaction.user.id in self.players:
            await interaction.response.send_message("⚠️ You've already joined!", ephemeral=True)
            return
        
        if len(self.players) >= 2:
            await interaction.response.send_message("⚠️ Match is full!", ephemeral=True)
            return
        
        self.players.append(interaction.user.id)
        
        await interaction.response.send_message(
            f"✅ {interaction.user.mention} joined the match! ({len(self.players)}/2 players)",
            ephemeral=False
        )
        
        if len(self.players) == 2:
            self.match_started = True
            button.disabled = True
            button.label = "Match Starting..."
            await interaction.message.edit(view=self)
            
            player1 = interaction.guild.get_member(self.players[0])
            player2 = interaction.guild.get_member(self.players[1])
            
            toss_embed = discord.Embed(
                title="🪙 Toss Time!",
                description=f"**{player1.mention}** - Choose Head or Tail:\n\n{player2.mention} will get the opposite",
                color=COLORS['primary']
            )
            
            view = TossCoinView(self.players, self.overs, self.venue, self.cog)
            await interaction.followup.send(embed=toss_embed, view=view)


class TossCoinView(View):
    """View for player to choose Head or Tail"""
    
    def __init__(self, players, overs, venue, cog):
        super().__init__(timeout=60)
        self.players = players
        self.overs = overs
        self.venue = venue
        self.cog = cog
    
    @discord.ui.button(label="Head", style=discord.ButtonStyle.primary, emoji="🔵")
    async def head_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.players[0]:
            await interaction.response.send_message("⚠️ Only the first player can choose!", ephemeral=True)
            return
        
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        
        await interaction.response.send_message(f"**{interaction.user.mention}** chose **HEAD** 🔵", ephemeral=False)
        await asyncio.sleep(1)
        
        await interaction.followup.send("🪙 Flipping the coin...")
        await asyncio.sleep(2)
        
        coin_result = random.choice(["head", "tail"])
        
        if coin_result == "head":
            toss_winner = self.players[0]
            result_emoji = "🔵"
        else:
            toss_winner = self.players[1]
            result_emoji = "🔴"
        
        winner_user = interaction.guild.get_member(toss_winner)
        
        result_embed = discord.Embed(
            title=f"🪙 It's {coin_result.upper()}! {result_emoji}",
            description=f"**{winner_user.mention}** won the toss!\n\nChoose to bat or bowl first:",
            color=COLORS['success']
        )
        
        view = TossChoiceView(toss_winner, self.players, self.overs, self.venue, self.cog)
        await interaction.followup.send(embed=result_embed, view=view)
        self.stop()
    
    @discord.ui.button(label="Tail", style=discord.ButtonStyle.danger, emoji="🔴")
    async def tail_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.players[0]:
            await interaction.response.send_message("⚠️ Only the first player can choose!", ephemeral=True)
            return
        
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        
        await interaction.response.send_message(f"**{interaction.user.mention}** chose **TAIL** 🔴", ephemeral=False)
        await asyncio.sleep(1)
        
        await interaction.followup.send("🪙 Flipping the coin...")
        await asyncio.sleep(2)
        
        coin_result = random.choice(["head", "tail"])
        
        if coin_result == "tail":
            toss_winner = self.players[0]
            result_emoji = "🔴"
        else:
            toss_winner = self.players[1]
            result_emoji = "🔵"
        
        winner_user = interaction.guild.get_member(toss_winner)
        
        result_embed = discord.Embed(
            title=f"🪙 It's {coin_result.upper()}! {result_emoji}",
            description=f"**{winner_user.mention}** won the toss!\n\nChoose to bat or bowl first:",
            color=COLORS['success']
        )
        
        view = TossChoiceView(toss_winner, self.players, self.overs, self.venue, self.cog)
        await interaction.followup.send(embed=result_embed, view=view)
        self.stop()


class TossChoiceView(View):
    """View for toss winner to choose bat/bowl"""
    
    def __init__(self, toss_winner, players, overs, venue, cog):
        super().__init__(timeout=60)
        self.toss_winner = toss_winner
        self.players = players
        self.overs = overs
        self.venue = venue
        self.cog = cog
        self.difficulty = "easy"  # Default to easy mode
    
    @discord.ui.button(label="🟢 Easy Mode", style=discord.ButtonStyle.success, emoji="👀", row=0)
    async def easy_mode_button(self, interaction: discord.Interaction, button: Button):
        """Select Easy Mode - Shows ball type"""
        if interaction.user.id not in self.players:
            await interaction.response.send_message("⚠️ Only players can choose difficulty!", ephemeral=True)
            return
        
        self.difficulty = "easy"
        await interaction.response.send_message("✅ **Easy Mode** selected! Ball delivery type will be visible.", ephemeral=False)
        
        # Update button states
        for child in self.children:
            if "Easy" in child.label:
                child.style = discord.ButtonStyle.success
            elif "Hard" in child.label:
                child.style = discord.ButtonStyle.secondary
        await interaction.message.edit(view=self)
    
    @discord.ui.button(label="🔴 Hard Mode", style=discord.ButtonStyle.secondary, emoji="🎯", row=0)
    async def hard_mode_button(self, interaction: discord.Interaction, button: Button):
        """Select Hard Mode - Hides ball type"""
        if interaction.user.id not in self.players:
            await interaction.response.send_message("⚠️ Only players can choose difficulty!", ephemeral=True)
            return
        
        self.difficulty = "hard"
        await interaction.response.send_message("🔥 **Hard Mode** selected! Ball delivery will be hidden for challenge!", ephemeral=False)
        
        # Update button states
        for child in self.children:
            if "Hard" in child.label:
                child.style = discord.ButtonStyle.danger
            elif "Easy" in child.label:
                child.style = discord.ButtonStyle.secondary
        await interaction.message.edit(view=self)
    
    @discord.ui.button(label="Bat First", style=discord.ButtonStyle.primary, emoji="🏏", row=1)
    async def bat_button(self, interaction: discord.Interaction, button: Button):
        """Choose to bat first"""
        
        if interaction.user.id != self.toss_winner:
            await interaction.response.send_message("⚠️ Only the toss winner can choose!", ephemeral=True)
            return
        
        await interaction.response.send_message(
            f"🏏 {interaction.user.mention} chose to **bat first**!\n🎮 **Difficulty:** {self.difficulty.upper()} Mode",
            ephemeral=False
        )
        
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        
        await self.cog.start_interactive_innings(
            interaction.channel, 
            batting_user_id=self.toss_winner,
            bowling_user_id=[p for p in self.players if p != self.toss_winner][0],
            overs=self.overs,
            venue=self.venue,
            innings=1,
            target=None,
            guild=interaction.guild,
            difficulty=self.difficulty
        )
    
    @discord.ui.button(label="Bowl First", style=discord.ButtonStyle.danger, emoji="⚾", row=1)
    async def bowl_button(self, interaction: discord.Interaction, button: Button):
        """Choose to bowl first"""
        
        if interaction.user.id != self.toss_winner:
            await interaction.response.send_message("⚠️ Only the toss winner can choose!", ephemeral=True)
            return
        
        opponent_id = [p for p in self.players if p != self.toss_winner][0]
        
        await interaction.response.send_message(
            f"⚾ {interaction.user.mention} chose to **bowl first**!\n🎮 **Difficulty:** {self.difficulty.upper()} Mode",
            ephemeral=False
        )
        
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        
        await self.cog.start_interactive_innings(
            interaction.channel,
            batting_user_id=opponent_id,
            bowling_user_id=self.toss_winner,
            overs=self.overs,
            venue=self.venue,
            innings=1,
            target=None,
            guild=interaction.guild,
            difficulty=self.difficulty
        )


class MatchCommands(commands.Cog):
    """Cricket match commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_matches = {}
    
    async def start_interactive_innings(self, channel, batting_user_id, bowling_user_id, overs, venue, innings, target, guild, difficulty="easy"):
        """Start professional interactive innings"""
        try:
            await channel.send(f"🏏 **Match Starting...** Loading teams...\n🎮 **Mode:** {difficulty.upper()}")
            
            from utils.match_engine import ProfessionalMatchEngine
            from database.db import db
            
            batting_xi = await db.get_playing_xi(batting_user_id)
            bowling_xi = await db.get_playing_xi(bowling_user_id)
            
            # Get team names
            batting_team_data = await db.get_user_team(batting_user_id)
            bowling_team_data = await db.get_user_team(bowling_user_id)
            batting_team_name = batting_team_data.get('team_name') if batting_team_data else None
            bowling_team_name = bowling_team_data.get('team_name') if bowling_team_data else None
            
            if not batting_xi or len(batting_xi) < 11:
                batting_xi = ['bat_0001', 'bat_0002', 'bat_0003', 'bat_0004', 'bowl_0001', 'bowl_0002', 'bowl_0003', 'ar_0001', 'ar_0002', 'wk_0001', 'wk_0002']
            if not bowling_xi or len(bowling_xi) < 11:
                bowling_xi = ['bat_0005', 'bat_0006', 'bat_0007', 'bat_0008', 'bowl_0004', 'bowl_0005', 'bowl_0006', 'ar_0003', 'ar_0004', 'wk_0003', 'wk_0004']
            
            await channel.send(f"✅ Teams loaded! Starting {overs} over match...")
            
            engine = ProfessionalMatchEngine(
                channel, batting_user_id, bowling_user_id,
                batting_xi, bowling_xi, overs, venue, innings, target, guild, difficulty,
                batting_team_name, bowling_team_name
            )
            
            await engine.start_innings()
            
        except Exception as e:
            await channel.send(f"❌ **Error starting match:** {str(e)}")
            import traceback
            traceback.print_exc()
    
    @commands.command(name='play')
    async def start_match(self, ctx, overs: int = 20):
        """
        Start a cricket match
        Usage: !cmplay [overs]
        """
        
        if overs < 1 or overs > 50:
            await ctx.send("❌ Overs must be between 1 and 50!")
            return
        
        if ctx.channel.id in self.active_matches:
            await ctx.send("⚠️ A match is already in progress in this channel!")
            return
        
        if overs <= 10:
            match_info = {"name": "T10", "format": "T10"}
        elif overs <= 20:
            match_info = {"name": "T20", "format": "T20"}
        else:
            match_info = {"name": "ODI", "format": "ODI"}
        
        venue = random.choice(VENUES)
        weather = random.choice(WEATHER_CONDITIONS)
        umpire = random.choice(UMPIRES)
        pitch = random.choice(PITCH_CONDITIONS)
        
        stadium_gif = stadium_manager.get_stadium_gif(venue['name'])
        
        embed = discord.Embed(
            title="🏏 Cric Mater Match",
            description=f"**{match_info['name']} Match - {overs} Overs**",
            color=COLORS['primary'],
            timestamp=datetime.utcnow()
        )
        
        if stadium_gif:
            embed.set_image(url=stadium_gif)
        
        embed.add_field(name="📍 Venue", value=f"{venue['name']}, {venue['location']}", inline=True)
        embed.add_field(name=f"{weather['emoji']} Weather", value=weather['condition'], inline=True)
        embed.add_field(name="🎓 Umpire", value=umpire, inline=True)
        embed.add_field(name=f"{pitch['emoji']} Pitch", value=f"{pitch['type']} - {pitch['desc']}", inline=False)
        embed.set_footer(text="⚠️ Statpadding with alt accounts or leaving games = ban")
        
        view = MatchJoinView(ctx.author.id, overs, match_info, venue, weather, umpire, pitch, self)
        
        await ctx.send(embed=embed, view=view)
        
        self.active_matches[ctx.channel.id] = {
            'overs': overs,
            'match_info': match_info,
            'venue': venue,
            'weather': weather,
            'umpire': umpire,
            'pitch': pitch,
            'creator': ctx.author.id,
            'status': 'waiting',
            'view': view
        }
    
    @commands.command(name='end')
    async def end_match(self, ctx):
        """
        End the current match
        Usage: !cmend
        """
        
        if ctx.channel.id not in self.active_matches:
            await ctx.send("❌ No match is currently active in this channel!")
            return
        
        match_data = self.active_matches[ctx.channel.id]
        
        if ctx.author.id != match_data['creator']:
            await ctx.send("⚠️ Only the match creator can end the match!")
            return
        
        del self.active_matches[ctx.channel.id]
        
        embed = discord.Embed(
            title="🛑 Match Ended",
            description=f"**{ctx.author.mention}** has ended the match.\n\nThe match has been cancelled.",
            color=discord.Color.red()
        )
        
        embed.set_footer(text="Start a new match with !cmplay")
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(MatchCommands(bot))

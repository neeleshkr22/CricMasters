"""
Stats Commands - View statistics and leaderboards
"""
import discord
from discord.ext import commands
from datetime import datetime

from config import COLORS
from database.db import db


class StatsCommands(commands.Cog):
    """Statistics and leaderboard commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='stats')
    async def view_stats(self, ctx, member: discord.Member = None):
        """
        View match statistics
        Usage: !cmstats [@user]
        """
        target = member or ctx.author
        stats = await db.get_user_stats(target.id)
        
        if not stats:
            await ctx.send(f"❌ {target.mention} hasn't played any matches yet!")
            return
        
        embed = discord.Embed(
            title=f"📊 {target.display_name}'s Statistics",
            color=COLORS['info']
        )
        
        embed.add_field(name="🎮 Matches", value=stats['matches_played'], inline=True)
        embed.add_field(name="🏆 Wins", value=stats['wins'], inline=True)
        embed.add_field(name="💔 Losses", value=stats['losses'], inline=True)
        embed.add_field(name="📈 Win Rate", value=f"{stats['win_rate']:.1f}%", inline=True)
        embed.add_field(name="🏏 Total Runs", value=stats['total_runs'], inline=True)
        embed.add_field(name="⚡ Total Wickets", value=stats['total_wickets'], inline=True)
        embed.add_field(name="🔥 Highest Score", value=stats['highest_score'], inline=True)
        
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text=f"Team: {stats.get('team_name', 'Unknown Team')}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx):
        """
        View top players
        Usage: !cmleaderboard
        """
        top_teams = await db.get_leaderboard(limit=10)
        
        if not top_teams:
            await ctx.send("❌ No teams found!")
            return
        
        embed = discord.Embed(
            title="🏆 Cric Mater Leaderboard",
            description="Top 10 Players",
            color=COLORS['gold']
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for idx, team in enumerate(top_teams, 1):
            medal = medals[idx-1] if idx <= 3 else f"`{idx}.`"
            
            matches = team.get('matches_played', 0)
            wins = team.get('wins', 0)
            win_rate = (wins / matches * 100) if matches > 0 else 0
            
            value = f"Matches: {matches} | Wins: {wins} | Win Rate: {win_rate:.1f}%"
            
            # Get team display name
            team_display_name = team.get('team_name')
            if not team_display_name:
                # Fetch Discord username if custom team name not set
                user_id = team.get('user_id')
                if user_id:
                    try:
                        member = ctx.guild.get_member(int(user_id))
                        if member:
                            team_display_name = f"{member.display_name}'s Team"
                        else:
                            # Try bot.get_user if not in guild
                            user = self.bot.get_user(int(user_id))
                            if user:
                                team_display_name = f"{user.name}'s Team"
                            else:
                                team_display_name = "Unknown Team"
                    except:
                        team_display_name = "Unknown Team"
                else:
                    team_display_name = "Unknown Team"
            
            embed.add_field(
                name=f"{medal} {team_display_name}",
                value=value,
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='matchhistory', aliases=['history', 'matches', 'cmstats'])
    async def match_history(self, ctx, member: discord.Member = None):
        """
        View match history
        Usage: !cmmatchhistory [@user]
        """
        target = member or ctx.author
        
        matches = await db.get_user_matches(target.id, limit=10)
        
        if not matches:
            await ctx.send(f"❌ {target.mention} hasn't played any matches yet!")
            return
        
        stats = await db.get_user_stats(target.id)
        
        embed = discord.Embed(
            title=f"📊 {target.name}'s Match History",
            color=COLORS['primary']
        )
        
        if stats:
            win_rate = stats.get('win_rate', 0)
            overview = f"**Matches Played:** {stats.get('matches_played', 0)}\n"
            overview += f"**Wins:** {stats.get('wins', 0)}\n"
            overview += f"**Losses:** {stats.get('losses', 0)}\n"
            overview += f"**Win Rate:** {win_rate:.1f}%"
            embed.add_field(name="📈 Overall Stats", value=overview, inline=False)
        
        embed.add_field(name="📋 Recent Matches (Last 10)", value="", inline=False)
        
        for idx, match in enumerate(matches[:10], 1):
            is_winner = match.get('winner_id') == str(target.id)
            result_emoji = "✅" if is_winner else "❌"
            
            if match.get('team1_user') == str(target.id):
                opponent_name = match.get('team2_name', 'Unknown')
                user_score = match.get('team1_score', 'N/A')
                opp_score = match.get('team2_score', 'N/A')
            else:
                opponent_name = match.get('team1_name', 'Unknown')
                user_score = match.get('team2_score', 'N/A')
                opp_score = match.get('team1_score', 'N/A')
            
            win_by = match.get('win_by', 'N/A')
            venue = match.get('venue', 'Unknown Venue')
            match_date = match.get('created_at', datetime.utcnow())
            
            if isinstance(match_date, datetime):
                date_str = match_date.strftime('%d %b %Y')
            else:
                date_str = 'Unknown Date'
            
            result = f"{result_emoji} **vs {opponent_name}**\n"
            result += f"Score: {user_score} vs {opp_score}\n"
            
            if is_winner:
                result += f"🏆 Won by {win_by}\n"
            else:
                result += f"💔 Lost by {win_by}\n"
            
            result += f"📍 {venue} | 📅 {date_str}"
            
            embed.add_field(
                name=f"Match #{idx}",
                value=result,
                inline=False
            )
        
        embed.set_footer(text=f"Keep playing to improve your stats! | Total matches: {len(matches)}")
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(StatsCommands(bot))

"""
Utility Commands - Ping, Help, Info
"""
import discord
from discord.ext import commands
from config import COLORS


class UtilityCommands(commands.Cog):
    """Utility and information commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """
        Check bot latency
        Usage: !cmping
        """
        latency = round(self.bot.latency * 1000)
        
        # Determine status based on latency
        if latency < 100:
            status = "🟢 Excellent"
            color = COLORS['success']
        elif latency < 200:
            status = "🟡 Good"
            color = COLORS['warning']
        else:
            status = "🔴 Poor"
            color = COLORS['danger']
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**Latency:** {latency}ms\n**Status:** {status}",
            color=color
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='help', aliases=['info', 'commands'])
    async def help_command(self, ctx):
        """
        Show all available commands
        Usage: !cmhelp
        """
        embed = discord.Embed(
            title="🏏 Cric Masters - Command Guide",
            description="Your complete guide to cricket management!",
            color=COLORS['primary']
        )
        
        # Basic Commands
        basic = """
        `!cmping` - Check bot latency
        `!cmhelp` - Show this help menu
        `!cmdebut` - Register and start your cricket journey
        """
        embed.add_field(name="📱 Basic", value=basic, inline=False)
        
        # Engagement Commands (NEW!)
        engagement = """
        `!cmclaim` - Hourly coins + FREE player card!
        `!cmcd` - Check all cooldown timers
        `!cmchallenge @user <bet>` - Quick 5-over PvP match
        `!cmpack` - Daily free pack (Bronze/Silver/Gold)
        **Build streaks for bonus packs!**
        """
        embed.add_field(name="🎁 Daily Rewards & Cards", value=engagement, inline=False)
        
        # Match Commands
        match = """
        `!cmplay [overs]` - Start a match (1-50 overs)
        `!cmend` - End current match
        `!cmxi` - View your playing XI
        `!cmsubs` - View substitute players
        `!cmsetxi` - Auto-select balanced XI
        """
        embed.add_field(name="🏏 Matches", value=match, inline=False)
        
        # Team Commands
        team = """
        `!cmteam [@user]` - View team details
        `!cmsetteamname <name>` - Change your team name
        `!cmswap <xi#> <sub#>` - Swap XI and sub player
        `!cmstats [@user]` - View match statistics
        `!cmleaderboard` - Top teams ranking
        `!cmmatchhistory [@user]` - View match history
        """
        embed.add_field(name="👥 Team Management", value=team, inline=False)
        
        # Economy Commands
        economy = """
        `!cmbal [@user]` - Check coin balance
        `!cmshop` - View shop items & packs
        `!cmbuy <item>` - Buy from shop
        `!cmsell [player_id]` - Sell players for 55% value
        `!cminventory [@user]` - View inventory
        `!cmtrade @user <amount>` - Send coins to user
        """
        embed.add_field(name="💰 Economy", value=economy, inline=False)
        
        # Auction Commands
        auction = """
        `!cmjoinauction` - Join active auction
        `!cmviewauction` - View auction details
        `!cmbid <amount>` - Bid on current player
        `!cmmyauction` - View your auction team
        `!cmtradeplayer @user "Give" "Get"` - Trade players
        `!cmtrades` - View active trades
        """
        embed.add_field(name="🎪 Auctions & Trading", value=auction, inline=False)
        
        # Legendary Commands
        legendary = """
        `!cmjoinlegendary` - Join legendary auction
        `!cmlegendarystats` - View legendary auction stats
        `!cmprizes` - View leaderboard prizes
        **Historic cricket legends!**
        """
        embed.add_field(name="👑 Legendary Players", value=legendary, inline=False)
        
        # Mini-Games & Fun
        games = """
        `!cmleaderboard [period]` - View rankings (daily/weekly/monthly)
        """
        embed.add_field(name="🏆 Leaderboards", value=games, inline=False)
        
        # Admin note
        admin_note = """
        🔐 **Admins:** Check `ADMIN_GUIDE.md` for admin commands
        `!cmauction <players> <time>` - Start automated auction
        """
        embed.add_field(name="⚙️ Administration", value=admin_note, inline=False)
        
        embed.set_footer(text="💡 !cmclaim every hour = Coins + FREE player card!")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))

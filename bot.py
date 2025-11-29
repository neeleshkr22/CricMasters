"""
Cric Mater Discord Bot - Main Bot File
"""
import discord
from discord.ext import commands
import asyncio
import sys

from config import DISCORD_TOKEN
from database.db import db


# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='cm', intents=intents, help_command=None)


@bot.event
async def on_ready():
    """Bot startup event"""
    print(f'✅ Logged in as {bot.user.name} ({bot.user.id})')
    print(f'📊 Connected to {len(bot.guilds)} servers')
    
    # Connect to database
    await db.connect()
    
    # Load cogs
    await load_cogs()
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="🏏 cmhelp | Cricket Matches"
        )
    )
    
    print('🎮 Bot is ready!')


async def load_cogs():
    """Load all cogs"""
    cogs = [
        'cogs.match_commands',
        'cogs.team_commands',
        'cogs.stats_commands',
        'cogs.utility_commands',
        'cogs.admin_commands',
        'cogs.auction_commands',
        'cogs.economy_commands',
        'cogs.legendary_commands',
        'cogs.engagement_commands',
        'cogs.sell_commands',
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'✅ Loaded {cog}')
        except Exception as e:
            print(f'❌ Failed to load {cog}: {e}')


@bot.check
async def globally_check_bans(ctx):
    """Check if user is banned before executing any command"""
    # Skip check for DM commands
    if ctx.guild is None:
        return True
    
    # Check if user is banned
    ban = await db.db.bans.find_one({"user_id": str(ctx.author.id)})
    
    if ban:
        await ctx.send("🔨 **You are banned from using this bot!**\n"
                      f"**Reason:** {ban.get('reason', 'No reason provided')}")
        return False
    
    return True


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `cmhelp` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param.name}")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ This command is on cooldown. Try again in {error.retry_after:.1f}s")
    elif isinstance(error, commands.CheckFailure):
        # User is banned, already handled in check
        pass
    else:
        print(f'Error: {error}')
        await ctx.send(f"❌ An error occurred: {str(error)}")


@bot.event
async def on_disconnect():
    """Handle bot disconnect"""
    print('⚠️ Bot disconnected')


@bot.event
async def on_resumed():
    """Handle bot reconnection"""
    print('✅ Bot reconnected')


async def main():
    """Main entry point"""
    try:
        async with bot:
            await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        print('\n⚠️ Shutting down bot...')
        await db.close()
        await bot.close()
    except Exception as e:
        print(f'❌ Fatal error: {e}')
        await db.close()
        await bot.close()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

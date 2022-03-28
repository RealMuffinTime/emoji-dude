import asyncio
import datetime
import discord
import secret_dev as secret
import utils
from discord.ext import commands

# TODO Index check, members in channel before bot start

# Version 1.0.2 ->
#
# New stuff
#  -
# Changes
#  - voice channel manager fix

bot = None
cogs = None
prefix = None
start_timestamp = None
version = None


def get_bot():
    global bot
    if bot is None:
        bot = commands.Bot(
            command_prefix=get_prefix(),
            description='a emoji spamming dude',
            owner_id=412235309204635649,
            case_insensitive=True
        )
    return bot


def get_cogs():
    global cogs
    if cogs is None:
        cogs = ['cogs.commands', 'cogs.events']
    return cogs


def get_prefix():
    global prefix
    if prefix is None:
        prefix = ['ed.']
    return prefix


def get_version():
    global version
    if version is None:
        version = "1.0.2"
    return version


async def cron():
    while True:
        await asyncio.sleep(10)


async def update_guild_count():
    try:
        guild_count = len(get_bot().guilds)
        guild_count_db = len(await utils.execute_sql("SELECT * FROM stat_bot_guilds WHERE action = 'add';", True)) - len(
            await utils.execute_sql("SELECT * FROM stat_bot_guilds WHERE action = 'remove';", True))
        if guild_count < guild_count_db:
            diff = guild_count_db - guild_count
            for count in range(diff):
                await utils.execute_sql("INSERT INTO stat_bot_guilds (action) VALUES ('remove');", False)
        elif guild_count > guild_count_db:
            diff = guild_count - guild_count_db
            for count in range(diff):
                await utils.execute_sql("INSERT INTO stat_bot_guilds (action) VALUES ('add');", False)

    except Exception as e:
        utils.on_error("update_guild_count()", str(e).strip('.'))


@get_bot().event
async def on_ready():
    utils.log("info", "Logged in as %s." % str(get_bot().user))
    for guild in get_bot().guilds:
        utils.log("info", " - %s (%s)" % (guild.name, guild.id))
    get_bot().remove_command('help')
    await get_bot().change_presence(
        activity=discord.Streaming(
            name="Happily this isn't shown, because then you would know, that this is a rick roll. :)",
            details="nobody beats me in emoting",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            type=discord.ActivityType.streaming))
    for cog in get_cogs():
        if get_bot().get_cog(type(cog).__name__) is None:
            get_bot().load_extension(cog)
    for guild in get_bot().guilds:
        await utils.execute_sql(f"INSERT IGNORE INTO set_guilds VALUES ('{guild.id}', NULL)", False)
    await update_guild_count()
    await cron()


try:
    get_bot().run(secret.bot_token, bot=True, reconnect=False)
except Exception as e:
    utils.on_error("run()", str(e))

import asyncio
import datetime
import discord
import utils
from discord.ext import commands

# TODO Index check, members in channel before bot start

# Version 1.1.0 ->
#
# New stuff
#  -
# Changes
#  -

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


async def check_afk():
    afk_members = await utils.execute_sql(f"SELECT user_id, last_seen, last_guild FROM set_users WHERE last_seen IS NOT NULL", True)
    for afk_member in afk_members:
        if utils.get_curr_timestamp(True) - afk_member[1] >= datetime.timedelta(seconds=120):
            last_guild = get_bot().get_guild(afk_member[2])
            if last_guild is not None:
                member = await last_guild.fetch_member(afk_member[0])
                if member.voice is None:
                    await utils.execute_sql(f"INSERT INTO set_users VALUES ('{member.id}', 0, NULL, NULL, NULL)  ON DUPLICATE KEY UPDATE last_seen = NULL, last_channel = NULL, last_guild = NULL", False)
                else:
                    if member.voice.self_deaf is True:
                        if not member.voice.self_stream or not member.voice.self_video:
                            last_channel = member.voice.channel
                            await utils.execute_sql(
                                f"INSERT INTO set_users VALUES ('{member.id}', 0, NULL, '{last_channel.id}', '{last_guild.id}')  ON DUPLICATE KEY UPDATE last_seen = NULL, last_channel = '{last_channel.id}', last_guild = '{last_guild.id}'",
                                False)
                            await member.move_to(last_guild.afk_channel)
                        else:
                            await utils.execute_sql(
                                f"INSERT INTO set_users VALUES ('{member.id}', 0, NULL, NULL, NULL)  ON DUPLICATE KEY UPDATE last_seen = NULL, last_channel = NULL, last_guild = NULL",
                                False)


async def cron():
    while True:
        await check_afk()
        await asyncio.sleep(30)


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
    get_bot().run(utils.secret.bot_token, bot=True, reconnect=False)
except Exception as e:
    utils.on_error("run()", str(e))

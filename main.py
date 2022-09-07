import asyncio
import datetime
import discord
import traceback
import utils
from discord.ext import commands

# TODO managed_channel deleting already deleted channel (more info needed)
# TODO managed_afk permission check for not logging as error and move entirely to events

# Version 1.1.0 ->
#
# New stuff
#  - user gets not afk managed when stream or video active
#  - managed channel adds new channel under last current existing
#  - managed channel checks for channels after start of bot
# Changes
#  - multiple reworks of afk management
#  - (error) logging optimization

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
        version = "1.1.0"
    return version


async def check_afk():
    afk_members = await utils.execute_sql(f"SELECT set_users.user_id, set_users.last_seen, set_users.last_guild, set_guilds.managed_afk_timeout, set_users.afk_managed FROM set_users "
                                          f"INNER JOIN set_guilds ON set_users.last_guild = set_guilds.guild_id "
                                          f"WHERE last_seen IS NOT NULL", True)
    for afk_member in afk_members:
        if afk_member[4] == 0 and utils.get_curr_timestamp(True) - afk_member[1] >= datetime.timedelta(seconds=afk_member[3]):
            last_guild = get_bot().get_guild(afk_member[2])
            member = await last_guild.fetch_member(afk_member[0])
            if member.voice is None:
                await utils.execute_sql(f"INSERT INTO set_users VALUES ('{member.id}', 0, 0, NULL, NULL, NULL) "
                                        f"ON DUPLICATE KEY UPDATE afk_managed = 0, last_seen = NULL, last_channel = NULL, last_guild = NULL", False)
            elif member.voice.self_deaf is True and not member.voice.self_stream and not member.voice.self_video:
                last_channel = member.voice.channel
                try:
                    await member.move_to(last_guild.afk_channel)
                    await utils.execute_sql(
                        f"INSERT INTO set_users VALUES ('{member.id}', 0, 1, '{afk_member[1]}', '{last_channel.id}', '{last_guild.id}') "
                        f"ON DUPLICATE KEY UPDATE afk_managed = 1, last_seen = '{afk_member[1]}', last_channel = '{last_channel.id}', last_guild = '{last_guild.id}'",
                        False)
                except Exception:
                    trace = traceback.format_exc().rstrip("\n").split("\n")
                    utils.on_error("check_afk()", *trace)


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
    except Exception:
        trace = traceback.format_exc().rstrip("\n").split("\n")
        utils.on_error("update_guild_count()", *trace)


@get_bot().event
async def on_ready():
    utils.get_start_timestamp()
    utils.log("info", "Logged in as %s." % str(get_bot().user))
    get_bot().remove_command('help')
    for cog in get_cogs():
        if get_bot().get_cog(type(cog).__name__) is None:
            get_bot().load_extension(cog)
    for guild in get_bot().guilds:
        utils.log("info", " - %s (%s)" % (guild.name, guild.id))
        await get_bot().get_cog("Events").managed_channel_command(guild)
    await get_bot().change_presence(
        activity=discord.Streaming(
            name="Happily this isn't shown, because then you would know, that this is a rick roll. :)",
            details="nobody beats me in emoting",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            type=discord.ActivityType.streaming))
    for guild in get_bot().guilds:
        await utils.execute_sql(f"INSERT IGNORE INTO set_guilds (guild_id) VALUES ('{guild.id}')", False)
    await update_guild_count()
    await cron()


try:
    get_bot().run(utils.secret.bot_token, bot=True, reconnect=False)
except Exception as e:
    trace = traceback.format_exc().rstrip("\n").split("\n")
    utils.on_error("run()", *trace)

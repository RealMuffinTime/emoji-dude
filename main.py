import asyncio
import datetime
import discord
import logging
import logging.handlers
import os
import utils
from discord.ext import commands

# TODO add stats, add logs is wip
# TODO slash commands
# TODO describe settings in command description
# TODO counting & word counting & good stats
# TODO change managed channel system
# TODO managed_afk move entirely to events
# TODO good counting feature, count 1 2 4 8 15 16 23 42
# TODO optimize permission return

bot = commands.Bot(
    activity=discord.Streaming(
        name="Happily this isn't shown, because then you would know, that this is a rick roll. :)",
        details="nobody beats me in emoting",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        type=discord.ActivityType.streaming),
    case_insensitive=True,
    command_prefix=['ed.'],
    description='a emoji spamming dude',
    intents=discord.Intents.all(),
    owner_id=412235309204635649
)

bot.version = "v2.4.1"

cogs = ['cogs.commands', 'cogs.events']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handlerFile = logging.handlers.RotatingFileHandler(
    filename=f"log/{os.environ['BOT_ENVIR']}_{utils.get_start_timestamp().replace(' ', '_').replace(':', '-')}.log",
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,
    backupCount=21,
)
handlerStream = logging.StreamHandler()

formatter = logging.Formatter('[{asctime} {levelname}] {message}', '%Y-%m-%d %H:%M:%S', style='{')
handlerFile.setFormatter(formatter)
handlerStream.setFormatter(formatter)

logger.addHandler(handlerFile)
logger.addHandler(handlerStream)


async def main():
    async with bot:
        bot.remove_command('help')
        for cog in cogs:
            if bot.get_cog(type(cog).__name__) is None:
                await bot.load_extension(cog)
        await bot.start(os.environ['BOT_TOKEN'], reconnect=False)


async def check_afk():
    afk_members = await utils.execute_sql(f"SELECT set_users.user_id, set_users.last_seen, set_users.last_guild, set_guilds.managed_afk_seconds_timeout, set_users.afk_managed FROM set_users "
                                          f"INNER JOIN set_guilds ON set_users.last_guild = set_guilds.guild_id "
                                          f"WHERE last_seen IS NOT NULL", True)
    for afk_member in afk_members:
        data = await utils.execute_sql(f"SELECT managed_afk_bool_enabled FROM set_guilds WHERE guild_id ='{afk_member[2]}'", True)
        if data[0][0]:
            if afk_member[4] == 0 and utils.get_curr_timestamp(True) - afk_member[1] >= datetime.timedelta(seconds=afk_member[3]):
                last_guild = bot.get_guild(afk_member[2])
                member = await last_guild.fetch_member(afk_member[0])
                if member.voice is None:
                    await utils.execute_sql(f"INSERT INTO set_users VALUES ('{member.id}', 0, 0, NULL, NULL, NULL) "
                                            f"ON DUPLICATE KEY UPDATE afk_managed = 0, last_seen = NULL, last_channel = NULL, last_guild = NULL", False)
                elif member.voice.self_deaf is True and not member.voice.self_stream and not member.voice.self_video:
                    last_channel = member.voice.channel
                    try:
                        if last_guild.afk_channel is not None and last_guild.afk_channel.permissions_for(last_guild.me).move_members and last_channel.permissions_for(last_guild.me).move_members:
                            await member.move_to(last_guild.afk_channel)
                            await utils.execute_sql(
                                f"INSERT INTO set_users VALUES ('{member.id}', 0, 1, '{afk_member[1]}', '{last_channel.id}', '{last_guild.id}') "
                                f"ON DUPLICATE KEY UPDATE afk_managed = 1, last_seen = '{afk_member[1]}', last_channel = '{last_channel.id}', last_guild = '{last_guild.id}'",
                                False)
                    except Exception:
                        utils.error("check_afk()")


async def cron():
    while True:
        # SQL requests needed, to keep online status data
        await check_afk()
        await asyncio.sleep(30)


async def update_guild_count():
    try:
        guild_count = len(bot.guilds)
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
        logger.info("Updated guild count.")
    except Exception:
        utils.error("update_guild_count()")


@bot.event
async def on_ready():
    logging.info(f"Logged in as {str(bot.user)}, on version {bot.version}, in session {str(utils.session_id)}.")
    for guild in bot.guilds:
        logging.info(f" - {guild.name} {guild.id}")
        await utils.execute_sql(f"INSERT IGNORE INTO set_guilds (guild_id) VALUES ('{guild.id}')", False)
        await bot.get_cog("Events").managed_channel_command(guild)
    await update_guild_count()
    await cron()

asyncio.run(main())

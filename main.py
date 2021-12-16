import asyncio
import datetime
import discord
import mariadb
import secret_dev as secret
import uuid
from discord.ext import commands

# TODO add :billed_cap: on every message of user id 443404465928667137

# Version 1.0.2
#
# New stuff
#  - Added a limit in `ed.clear <limit>`, you can now specify the amount of messages to delete
# Changes
#  - Typo fixing
#  - Decreased the maximum emoji amount in 'ed.emojis' to 27

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
        cogs = ['cogs.basic']  # , 'cogs.embed']
    return cogs


def get_prefix():
    global prefix
    if prefix is None:
        prefix = ['ed.']
    return prefix


def get_start_timestamp():
    global start_timestamp
    if start_timestamp is None:
        start_timestamp = str(datetime.datetime.now().replace(microsecond=0))
    return start_timestamp


def get_curr_timestamp():
    return str(datetime.datetime.now().replace(microsecond=0))


def get_version():
    global version
    if version is None:
        version = "1.0.2"
    return version


@get_bot().event
async def on_ready():
    log("info", "Logged in as %s." % str(get_bot().user))
    for guild in get_bot().guilds:
        log("info", " - %s (%s)" % (guild.name, guild.id))
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


def on_error(error_type, message):
    error_uuid = str(uuid.uuid4())
    log("error", error_type + " error uuid: " + error_uuid + ", " + message)
    return error_uuid


def log(status, message):
    try:
        status_prefix = None
        if status == "error":
            status_prefix = "%s [  ERROR  ] "
        if status == "info":
            status_prefix = "%s [  INFO   ] "
        print(status_prefix % get_curr_timestamp() + message)
        log_file = open(r"log/%s_%s.txt" % (secret.secret, get_start_timestamp().replace(" ", "_").replace(":", "-")), "a", encoding="utf8")
        log_file.write(status_prefix % get_curr_timestamp() + message + "\n")
        log_file.close()
    except Exception as e:
        status_prefix = "%s [  ERROR  ] " % get_curr_timestamp()
        print(status_prefix + "There is an error in a error reporter, HAHA, how ironic, %s" % str(e))


try:
    get_bot().run(secret.bot_token, bot=True, reconnect=False)
except Exception as e:
    on_error("run()", str(e))

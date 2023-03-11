import datetime
import discord
import traceback
import utils
from discord.ext import commands

emojis = [["LOL", "lollipop", ["🍭"]], ["POOP", "poop", ["💩"]], ["COOL", "cool", ["🇨", "🇴", "🅾", "🇱"]]]


class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', description='The help command!', aliases=['commands', 'command'], usage='<category/command>')
    async def help_command(self, ctx, parameter=None):
        try:
            if str(ctx.channel.type) == "private":
                color = discord.Colour.random()
            else:
                if ctx.channel.permissions_for(ctx.author.guild.me).embed_links is False:
                    await ctx.send(content="**Help Command**\nI don't have permission to use embed messages.\nPlease provide the `Embed Links` permission.", delete_after=15)
                    return
                color = ctx.channel.guild.me.color.value

            embed = discord.Embed(color=color)

            embed.title = f"Help page of {self.bot.user}"

            help_object = self.bot.get_command("help")
            embed.description = f"Help command syntax: `{ctx.prefix}{help_object.name} {help_object.usage if help_object.usage is not None else ''}`"

            cogs = [c for c in self.bot.cogs.keys()]
            lower_cogs = [c.lower() for c in cogs]

            commands = [c.name for c in self.bot.commands]
            lower_commands = [c.lower() for c in commands]

            if parameter is None:
                for cog in cogs:
                    cog_commands = self.bot.get_cog(cog).get_commands()
                    commands_list = ''

                    for command in cog_commands:
                        commands_list += f'**{command.name}** - *{command.description}*\n'

                    embed.add_field(
                        name="\u200b\n" + cog,
                        value=commands_list,
                        inline=False
                    )

            elif parameter.lower() in lower_cogs:
                cog = self.bot.get_cog(cogs[lower_cogs.index(parameter.lower())])
                embed.title += f" - Category {cog.qualified_name}"
                commands_list = cog.get_commands()

                for command in commands_list:

                    command_name = command.callback.__name__.replace("_command", "")
                    status = " - *Enabled*"
                    if not command_name.startswith("help") and not command_name.startswith("sett"):
                        enabled = await utils.execute_sql(f"SELECT {command_name} FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
                        if not enabled[0][0]:
                            status = " - *Disabled*"

                    description = f"Description: {command.description}\n"

                    aliases = f"Aliases: `{', '.join(command.aliases)}`\n"

                    syntax = f"Syntax: `{ctx.prefix}{command.name}{' ' + command.usage if command.usage is not None else ''}`"

                    embed.add_field(
                        name="\u200b\n" + command.name + status,
                        value=description + (aliases if len(command.aliases) > 0 else '') + syntax,
                        inline=False
                    )

            elif parameter.lower() in lower_commands:
                command = self.bot.get_command(commands[lower_commands.index(parameter.lower())])

                embed.title += f" - Command {command.name}"

                description = f"Description: {command.description}\n"

                aliases = f"Aliases: `{', '.join(command.aliases)}`\n"

                syntax = f"Syntax: `{ctx.prefix}{command.name}{' ' + command.usage if command.usage is not None else ''}`"

                embed.add_field(
                    name="\u200b\nDetails",
                    value=description + (aliases if len(command.aliases) > 0 else '') + syntax,
                    inline=False
                )

                if ctx.guild is not None:
                    names = await utils.execute_sql(f"DESCRIBE set_guilds", True)
                    values = await utils.execute_sql(f"SELECT * FROM set_guilds WHERE guild_id = '{ctx.guild.id}'", True)

                    command_name = command.callback.__name__.replace("_command", "")

                    settings = ""
                    i = 0
                    while i < len(values[0]):
                        if names[i][0].startswith(command_name) and not names[i][0].endswith("running"):
                            name = names[i][0][1 + len(command_name):].replace("_", " ").title()
                            value = values[0][i]
                            if name == "":
                                name = "Enabled"
                                if value == 1:
                                    value = "Yes"
                                else:
                                    value = "No"
                            settings += f'**{name}:** `{value}`\n'
                        i += 1

                    if settings == "":
                        settings = "*There are no changeable settings regarding this command.*\n"

                    if ctx.author.guild_permissions.administrator is True or ctx.author.guild_permissions.manage_guild is True:
                        admin = "*You are an admin, you can change these settings.*"
                    else:
                        admin = "*If you would be an admin, you could change settings here.\nHAHA, but you are NOT.*"

                    embed.add_field(
                        name="\u200b\nSettings",
                        value=settings + admin,
                        inline=False
                    )

            else:
                await ctx.send("**Help Command**\nInvalid category or command specified.", delete_after=10)
                return

            await ctx.send(embed=embed)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("help_command()", *trace)

    @commands.command(name='settings', description='Not implemented yet.')
    async def settings_command(self, ctx):
        try:
            await ctx.send(content="**Settings**\nNot implemented yet.")
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("settings_command()", *trace)

    @commands.command(name='ping', description='some pongs')
    async def ping_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT ping FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                start = datetime.datetime.now()
                msg = await ctx.send(content='**Ping?**')
                await msg.edit(content=f'**Pong!**\n'
                                       f'One Message round-trip took **{int((datetime.datetime.now() - start).microseconds / 1000)}ms**.\n'
                                       f'Ping of the bot **{int(self.bot.latency * 1000)}ms**.')
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("ping_command()", *trace)

    @commands.command(name='backupchannel', aliases=['bc'], description='can be used to back up channel to another one')
    async def backup_channel_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT backup_channel FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                if ctx.author.id == 412235309204635649:
                    content = ctx.message.content.split(" ")
                    if len(content) == 3:
                        try:
                            from_channel = discord.utils.get(ctx.guild.channels, id=int(content[1]))
                            to_channel = discord.utils.get(ctx.guild.channels, id=int(content[2]))
                        except Exception as e:
                            await ctx.send("**BackupChannel**\nInvalid channels.")
                            return

                        status_message = await ctx.send(f"**BackupChannel**\nBeginning backup from <#{from_channel.id}> to <#{to_channel.id}>.\nSearching for messages...")
                        backup_messages = [message async for message in from_channel.history(limit=None, oldest_first=True)]

                        await status_message.edit(content=f"**BackupChannel**\nBeginning backup of <#{from_channel.id}> to <#{to_channel.id}>.\nFound {len(backup_messages)} messages.")

                        for message in backup_messages:
                            timestamp = int(message.created_at.timestamp())
                            if message.edited_at is not None:
                                timestamp = int(message.edited_at.timestamp())

                            allowed_mentions = discord.AllowedMentions().none()
                            await to_channel.send(f"--- At <t:{timestamp}:f> wrote <@!{message.author.id}> ---", allowed_mentions=allowed_mentions)
                            await to_channel.send(message.content, allowed_mentions=allowed_mentions)
                    else:
                        await ctx.send("**BackupChannel**\nInvalid input.")
                        return
                else:
                    await ctx.send("**BackupChannel**\nYou have no permission to use this command.", delete_after=15)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("backup_channel_command()", *trace)

    @commands.command(name='screenshare', aliases=['ss'], description='can be used to share your screen in voice channels')
    async def screenshare_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT screenshare FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                if ctx.author.voice:
                    channel = ctx.author.voice.channel
                    await ctx.send("**Screenshare**\n"
                                   f"If you want to share your screen in <#{channel.id}>, use this link:\n"
                                   f"<https://discordapp.com/channels/{ctx.guild.id}/{channel.id}/>")
                    return
                else:
                    await ctx.send("**Screenshare**\nYou are not in a voice channel!")
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("screenshare_command()", *trace)

    @commands.command(name='clean', description='cleans all messages affecting this bot')
    async def clean_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT clean FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                if ctx.channel.permissions_for(ctx.guild.me).manage_messages and ctx.channel.permissions_for(ctx.guild.me).read_message_history is True:
                    message = await ctx.send(content='**CleanUp**\nDeleting...')

                    def check(m):
                        if m == message:
                            return False
                        elif m.content.startswith("ed."):
                            return True
                        elif m.author == self.bot.user:
                            return True
                        else:
                            return False

                    deleted = await ctx.channel.purge(check=check)

                    await message.edit(content=f'**CleanUp**\nDeleted **{len(deleted) - 1}** message(s).', delete_after=5)
                else:
                    await ctx.send('**CleanUp**\nMissing permission to delete messages.\nPlease provide the `Manage Messages` and `Read Message History` permission.', delete_after=15)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("clean_command()", *trace)

    @commands.command(name='clear', description='clears messages', usage='<amount> or until message by replying')
    async def clear_command(self, ctx, amount=None):
        try:
            data = await utils.execute_sql(f"SELECT clear FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                if ctx.channel.permissions_for(ctx.guild.me).manage_messages and ctx.channel.permissions_for(ctx.guild.me).read_message_history is True:
                    if ctx.message.reference is not None and ctx.message.reference.resolved is not None and type(
                            ctx.message.reference.resolved) == discord.Message:
                        amount = 0
                        async for message in ctx.channel.history(limit=420):  # incrementing search to be added
                            if message == ctx.message.reference.resolved:
                                break
                            amount += 1
                    else:
                        try:
                            amount = int(amount)
                        except Exception:
                            await ctx.send(content='**ClearUp**\nIncorrect command usage.')
                            return
                    message = await ctx.send(content='**ClearUp**\nDeleting...')

                    def is_clear_message(m):
                        if m == message:
                            return False
                        return True

                    deleted = await ctx.channel.purge(limit=amount + 2, check=is_clear_message, bulk=True)

                    await message.edit(content=f'**ClearUp**\nDeleted **{len(deleted) - 1}** message(s).', delete_after=5)
                else:
                    await ctx.send('**ClearUp**\nMissing permission to delete messages.\nPlease provide the `Manage Messages` and `Read Message History` permission.', delete_after=15)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("clear_command()", *trace)

    @commands.command(name='emojis', aliases=['e'], description='sends many emojis, cip cap 27', usage='<emoji> <amount>')
    async def emojis_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT emojis FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                if ctx.author.bot:
                    return

                msg = ctx.message.content
                prefix = ctx.prefix
                alias = ctx.invoked_with
                text = msg[len(prefix) + len(alias) + 1:]

                if text == '':
                    await ctx.send(content='**Emojis**\nYou need to specify the emoji and the number of these.')
                else:
                    parameters = text.split(" ")
                    if len(parameters) == 2:
                        for emoji in emojis:
                            if parameters[0].upper() in emoji[0]:
                                index = 0
                                send_text = ""
                                warning = ""
                                try:
                                    index = int(parameters[1])
                                except Exception:
                                    await ctx.send('**Emojis**\nDid not find specified emoji.')
                                    return
                                if index > 27:
                                    index = 27
                                    warning = f"**Emojis**\nUnfortunately, I only send 27 {emoji[1]}s :disappointed_relieved:."
                                for i in range(index):
                                    send_text += ":" + emoji[1] + ":"
                                if send_text + warning != "":
                                    await ctx.send(send_text + warning)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("emojis_command()", *trace)


async def setup(bot):
    await bot.add_cog(Commands(bot))

import datetime
import discord
import emoji as emojilib
import traceback
import utils
from discord.ext import commands


class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', description='The help command!', aliases=['commands', 'command'], usage='<category/command>')
    async def help_command(self, ctx, parameter=None):
        try:

            text = await self.generate_help_text(ctx, parameter)

            await ctx.reply(content=text[0], embed=text[1], delete_after=text[2], mention_author=False)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("help_command()", *trace)

    async def generate_help_text(self, ctx, parameter):
        try:
            if str(ctx.channel.type) == "private":
                color = discord.Colour.random()
            else:
                if ctx.channel.permissions_for(ctx.author.guild.me).embed_links is False:
                    content = "**Help Command**\nI don't have permission to use embed messages.\nPlease provide the `Embed Links` permission."
                    return content, None, 15
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
                    if not command_name.startswith("help"):
                        enabled = await utils.execute_sql(f"SELECT {command_name}_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
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

                embed.title += f" - {command.cog.qualified_name.strip('s')} {command.name}"

                description = f"Description: {command.description}\n"

                aliases = f"Aliases: `{', '.join(command.aliases)}`\n"

                syntax = f"Syntax: `{ctx.prefix}{command.name}{' ' + command.usage if command.usage is not None else ''}`"

                embed.add_field(
                    name="\u200b\nDetails",
                    value=description + (aliases if len(command.aliases) > 0 else '') + syntax,
                    inline=False
                )

                if ctx.guild is not None:
                    description = await utils.execute_sql(f"DESCRIBE set_guilds", True)
                    values = await utils.execute_sql(f"SELECT * FROM set_guilds WHERE guild_id = '{ctx.guild.id}'", True)

                    command_name = command.callback.__name__.replace("_command", "")
                    print(command_name)

                    settings = ""
                    i = 0
                    while i < len(values[0]):
                        config = description[i][0]
                        if config.startswith(command_name):
                            config = config[len(command_name) + 1:]

                            value = values[0][i]
                            if not config.startswith("ignore"):
                                if config.startswith("bool"):
                                    setting = config[5:].replace("_", " ").title()
                                    if value == 1:
                                        value = "`Yes`"
                                    else:
                                        value = "`No`"
                                elif config.startswith("voice_channel"):
                                    setting = config[14:].replace("_", " ").title()
                                    if value is not None:
                                        value = (await ctx.guild.fetch_channel(value)).mention
                                elif config.startswith("seconds"):
                                    setting = config[7:].replace("_", " ").title()
                                    value = f"`{str(value)}s`"
                                else:
                                    setting = config
                                settings += f'**{setting}:** {value}\n'
                        i += 1

                    if settings == "":
                        settings = "*There are no changeable settings regarding this command.*\n"
                    else:
                        if ctx.author.guild_permissions.administrator is True or ctx.author.guild_permissions.manage_guild is True:
                            settings += "*You are an admin, you can change these settings.*"
                        else:
                            settings += "*If you would be an admin, you could change settings here.\nHAHA, but you are NOT.*"

                    embed.add_field(
                        name="\u200b\nSettings",
                        value=settings,
                        inline=False
                    )

            else:
                content = "**Help Command**\nInvalid category or command specified."
                return content, None, 10

            return None, embed, None

        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("help_command()", *trace)


    @commands.command(name='ping', description='some pongs')
    async def ping_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT ping_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                start = datetime.datetime.now()
                msg = await ctx.reply(content='**Ping?**', mention_author=False)
                await msg.edit(content=f'**Pong!**\n'
                                       f'One Message round-trip took **{int((datetime.datetime.now() - start).microseconds / 1000)}ms**.\n'
                                       f'Ping of the bot **{int(self.bot.latency * 1000)}ms**.', allowed_mentions=discord.AllowedMentions.none())
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("ping_command()", *trace)

    @commands.command(name='backupchannel', aliases=['bc'], description='can be used to back up channel to another one')
    async def backup_channel_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT backup_channel_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                if ctx.author.id == 412235309204635649:
                    content = ctx.message.content.split(" ")
                    if len(content) == 3:
                        try:
                            from_channel = discord.utils.get(ctx.guild.channels, id=int(content[1]))
                            to_channel = discord.utils.get(ctx.guild.channels, id=int(content[2]))
                        except Exception as e:
                            await ctx.reply("**BackupChannel**\nInvalid channels.", mention_author=False)
                            return

                        status_message = await ctx.reply(f"**BackupChannel**\nBeginning backup from <#{from_channel.id}> to <#{to_channel.id}>.\nSearching for messages...", mention_author=False)
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
                        await ctx.reply("**BackupChannel**\nInvalid input.", mention_author=False)
                        return
                else:
                    await ctx.reply("**BackupChannel**\nYou have no permission to use this command.", delete_after=15, mention_author=False)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("backup_channel_command()", *trace)

    @commands.command(name='screenshare', aliases=['ss'], description='can be used to share your screen in voice channels')
    async def screenshare_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT screenshare_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                if ctx.author.voice:
                    channel = ctx.author.voice.channel
                    await ctx.reply(f"**Screenshare**\n"
                                    f"If you want to share your screen in <#{channel.id}>, use this link:\n"
                                    f"<https://discordapp.com/channels/{ctx.guild.id}/{channel.id}/>", mention_author=False)
                    return
                else:
                    await ctx.reply("**Screenshare**\nYou are not in a voice channel!", mention_author=False)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("screenshare_command()", *trace)

    @commands.command(name='clean', description='cleans all messages affecting this bot')
    async def clean_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT clean_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                if ctx.channel.permissions_for(ctx.guild.me).manage_messages and ctx.channel.permissions_for(ctx.guild.me).read_message_history is True:
                    message = await ctx.reply(content='**CleanUp**\nDeleting...', mention_author=False)

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
                    await ctx.reply('**CleanUp**\nMissing permission to delete messages.\n'
                                    'Please provide the `Manage Messages` and `Read Message History` permission.', delete_after=15, mention_author=False)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("clean_command()", *trace)

    @commands.command(name='clear', description='clears messages', usage='<amount> or until message by replying')
    async def clear_command(self, ctx, amount=None):
        try:
            data = await utils.execute_sql(f"SELECT clear_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                if ctx.channel.permissions_for(ctx.guild.me).manage_messages and ctx.channel.permissions_for(ctx.guild.me).read_message_history is True:
                    if ctx.message.reference is not None and ctx.message.reference.resolved is not None and type(
                            ctx.message.reference.resolved) == discord.Message:
                        amount = 0
                        async for message in ctx.channel.history():  # incrementing search to be added
                            if message == ctx.message.reference.resolved:
                                break
                            amount += 1
                    else:
                        try:
                            amount = int(amount)
                        except Exception:
                            await ctx.reply(content='**ClearUp**\nIncorrect command usage.', mention_author=False)
                            return
                    message = await ctx.reply(content='**ClearUp**\nDeleting...', mention_author=False)

                    def is_clear_message(m):
                        if m == message:
                            return False
                        return True

                    deleted = await ctx.channel.purge(limit=amount + 2, check=is_clear_message, bulk=True)

                    await message.edit(content=f'**ClearUp**\nDeleted **{len(deleted) - 1}** message(s).', delete_after=5)
                else:
                    await ctx.reply('**ClearUp**\nMissing permission to delete messages.\n'
                                    'Please provide the `Manage Messages` and `Read Message History` permission.', delete_after=15, mention_author=False)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("clear_command()", *trace)

    @commands.command(name='emojis', aliases=['e'], description='sends many emojis (also animated ones), cip cap 27', usage='<emoji> <amount>')
    async def emojis_command(self, ctx, emoji_call, amount=1):
        try:
            data = await utils.execute_sql(f"SELECT emojis_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                emojis_split = emojilib.demojize(emoji_call).replace("<", "|").replace(">", "|").split("|")
                i = 0
                while i < len(emojis_split):
                    partial_emoji = discord.PartialEmoji.from_str(emojis_split[i])
                    if str(partial_emoji) != str(emojis_split[i]):
                        emoji = discord.utils.get(ctx.guild.emojis, id=partial_emoji.id)
                        if emoji is None:
                            emoji = discord.utils.get(self.bot.emojis, id=partial_emoji.id)
                            if emoji is None:
                                emojis_split[i] = ""
                                i += 1
                                continue
                        emojis_split[i] = str(emoji)

                    else:
                        other_emoji_split = emojis_split[i].split(":")
                        j = 0
                        while j < len(other_emoji_split):
                            emoji = discord.utils.get(ctx.guild.emojis, name=other_emoji_split[j])
                            if emoji is None:
                                emoji = discord.utils.get(self.bot.emojis, name=other_emoji_split[j])
                                if emoji is None:
                                    emoji = emojilib.emojize(":" + other_emoji_split[j] + ":")
                                    if emoji == ":" + other_emoji_split[j] + ":":
                                        other_emoji_split[j] = ""
                                        j += 1
                                        continue
                            other_emoji_split[j] = str(emoji)

                            j += 1

                        emojis_split[i] = "".join(other_emoji_split)
                    i += 1

                emojis = "".join(emojis_split)

                if emojis == "":
                    await ctx.reply('**Emojis**\nDid not find specified emoji.', mention_author=False, delete_after=10)
                    return

                try:
                    amount = int(amount)
                    if amount < 0:
                        amount = amount * (-1)
                    if amount > 27 or amount == 0:
                        amount = 27
                except Exception:
                    await ctx.reply(content='**Emojis**\nPlease provide a usable number.', mention_author=False, delete_after=10)
                    return

                output = ""
                for i in range(amount):
                    output += str(emojis) + " "

                if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                    await ctx.message.delete()
                if ctx.message.reference is not None and ctx.message.reference.resolved is not None and type(ctx.message.reference.resolved) == discord.Message:
                    await ctx.message.reference.resolved.reply(output)
                else:
                    await ctx.send(output)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("emojis_command()", *trace)


async def setup(bot):
    await bot.add_cog(Commands(bot))

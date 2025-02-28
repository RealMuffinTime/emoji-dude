import asyncio
import datetime
import discord
import emoji as emojilib
import unicodedata
import utils
from discord.ext import commands


class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", description="PONG! Pings and message round-trips.")
    async def ping_command(self, ctx):
        status = "ongoing"
        guild_id = None
        try:
            if ctx.guild:
                guild_id = ctx.guild.id
                data = await utils.execute_sql(f"SELECT ping_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            else:
                data = [[True]]
            if data[0][0]:
                start = datetime.datetime.now()
                msg = await ctx.reply(content="**Ping?**", mention_author=False)
                await msg.edit(content=f"**Pong!**\n"
                                       f"One Message round-trip took **{int((datetime.datetime.now() - start).microseconds / 1000)}ms**.\n"
                                       f"Ping of the bot **{int(self.bot.latency * 1000)}ms**.", allowed_mentions=discord.AllowedMentions.none())
                status = "success"
            else:
                return
        except Exception:
            utils.error("ping_command()")
            status = "error"

        await utils.stat_bot_commands("ping", status, ctx.author.id, guild_id)

    @commands.command(name="backupchannel",
                      description="Can be used to back up a channel to another one.\n" 
                                  "This command is initially disabled, since it is currently only available to bot creators.",
                      usage="<from_channel_id> <to_channel_id>")
    async def backup_channel_command(self, ctx):
        status = "ongoing"
        guild_id  = None
        try:
            if ctx.guild:
                guild_id = ctx.guild.id
                data = await utils.execute_sql(f"SELECT backup_channel_bool_enabled, backup_channel_role_moderator FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
                enabled, moderator = data[0][0], data[0][1] if data[0][1] is not None else 0
                if enabled:
                    if ctx.author.id == 412235309204635649:
                        content = ctx.message.content.split(" ")
                        from_channel, to_channel = None, None
                        try:
                            from_channel = ctx.guild.get_channel(int(content[1]))
                            to_channel = ctx.guild.get_channel(int(content[2]))
                        except Exception as e:
                            await ctx.reply(f"**BackupChannel** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                            "Invalid channels.", mention_author=False, delete_after=10)
                            status = "fault"

                        if from_channel and to_channel:
                            if (from_channel.permissions_for(ctx.author).manage_messages and to_channel.permissions_for(ctx.author).manage_messages) or ctx.channel.permissions_for(ctx.author).administrator or ctx.author.get_role(moderator):
                                if len(content) == 3:
                                    status = "success"
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
                                    await ctx.reply(f"**BackupChannel** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                                    "Invalid input.", mention_author=False, delete_after=10)
                                    status = "fault"
                            else:
                                await ctx.reply(f"**BackupChannel** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                                "You have no permission for these channels.", mention_author=False, delete_after=10)
                                status = "fault"
                    else:
                        await ctx.reply(f"**BackupChannel** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                        "You are not an author of this bot.", delete_after=10, mention_author=False)
                        status = "fault"
                else:
                    return
            else:
                await ctx.reply(f"**BackupChannel** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                "This command does not work in DMs.", delete_after=10, mention_author=False)
                status = "fault"
        except Exception:
            utils.error("backup_channel_command()")
            status = "error"

        await utils.stat_bot_commands("backup_channel", status, ctx.author.id, guild_id)

    @commands.command(name="clear",
                      description="Deletes messages up to a specific point, filtered by user, if given.\n"
                                  "You need to reply to a message, then the bot deletes all messages up to the replied one.",
                      usage="<user>", aliases=["clean"])
    async def clear_command(self, ctx, member=None):
        status = "ongoing"
        guild_id = None
        try:
            if ctx.guild:
                guild_id = ctx.guild.id
                data = await utils.execute_sql(f"SELECT clear_bool_enabled, clear_role_moderator FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
                enabled, moderator = data[0][0], data[0][1] if data[0][1] is not None else 0
                if enabled:
                    if ctx.channel.permissions_for(ctx.author).manage_messages or ctx.channel.permissions_for(
                            ctx.author).administrator or ctx.author.get_role(moderator) is not None:
                        if ctx.channel.permissions_for(ctx.guild.me).manage_messages and ctx.channel.permissions_for(ctx.guild.me).read_message_history is True:
                            if member is not None:
                                try:
                                    member = (await ctx.guild.fetch_member(member.strip("<>!@"))).id
                                except:
                                    await ctx.reply(content=f"**Clear** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                                            "Invalid user specified.", delete_after=10, mention_author=False)
                                    status = "fault"

                            if status != "fault":
                                if ctx.message.reference is not None and ctx.message.reference.resolved is not None and type(
                                        ctx.message.reference.resolved) == discord.Message:
                                    bulk_messages = []
                                    slow_messages = []

                                    async for message in ctx.channel.history():  # TODO incrementing search to be added, current max is 99 messages
                                        if (member is None or (member is not None and (message.author.id == member or (message.content.startswith("ed.") and member == ctx.guild.me.id)))) and message != ctx.message:
                                            if message.created_at > datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14):
                                                bulk_messages.append(message)
                                            else:
                                                slow_messages.append(message)
                                        if message == ctx.message.reference.resolved or discord.utils.snowflake_time(ctx.message.reference.message_id) >= discord.utils.snowflake_time(ctx.message.id):
                                            last_message = None
                                            break
                                        else:
                                            last_message = message
                                else:
                                    await ctx.reply(content=f"**Clear** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                                            "Please reply to a message to select a limit.", delete_after=10, mention_author=False)
                                    status = "fault"

                                if status != "fault":
                                    status_message = await ctx.reply(content="**Clear**\n"
                                                                             f"Deleting **{len(bulk_messages)}** message{'s' if len(bulk_messages) > 1 or len(bulk_messages) == 0 else ''} in fast mode...\n"
                                                                             f"Deleting **{len(slow_messages)}** message{'s' if len(slow_messages) > 1 or len(slow_messages) == 0 else ''} in slow mode...", mention_author=False)

                                    await ctx.channel.delete_messages(bulk_messages)

                                    await status_message.edit(content=f"**Clear**\n"
                                                                      f"Deleted **{len(bulk_messages)}** message{'s' if len(bulk_messages) > 1 or len(bulk_messages) == 0 else ''} in fast mode.\n"
                                                                      f"Deleting **{len(slow_messages)}** message{'s' if len(slow_messages) > 1 or len(slow_messages) == 0 else ''} in slow mode...", allowed_mentions=discord.AllowedMentions.none())

                                    for message in slow_messages:
                                        try:
                                            await message.delete()
                                        except:
                                            pass
                                        if (slow_messages.index(message) + 1) % 5 == 0:
                                            await status_message.edit(content=f"**Clear**\n"
                                                                              f"Deleted **{len(bulk_messages)}** message{'s' if len(bulk_messages) > 1 or len(bulk_messages) == 0 else ''} in fast mode.\n"
                                                                              f"Deleted **{slow_messages.index(message) + 1}/{len(slow_messages)}** message{'s' if len(slow_messages) > 1 or len(slow_messages) == 0 else ''} in slow mode...\n"
                                                                              f"Deleting in slow mode can take a long time because of Discord limitations.", allowed_mentions=discord.AllowedMentions.none())

                                    await ctx.message.delete()
                                    await status_message.edit(content=f"**Clear** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                                                      f"Deleted **{len(bulk_messages)}** message{'s' if len(bulk_messages) > 1 or len(bulk_messages) == 0 else ''} in fast mode.\n"
                                                                      f"Deleted **{len(slow_messages)}** message{'s' if len(slow_messages) > 1 or len(slow_messages) == 0 else ''} in slow mode.", delete_after=10, allowed_mentions=discord.AllowedMentions.none())
                                    status = "success"

                        else:
                            await ctx.reply(f"**Clear** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                            "Missing permission to delete messages.\n"
                                            "Please provide the `Manage Messages` and `Read Message History` permission.", delete_after=10, mention_author=False)
                            status = "fault"
                    else:
                        await ctx.reply(f"**Clear** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                        "You dont have permissions to delete messages.", delete_after=10, mention_author=False)
                        status = "fault"
                else:
                    return
            else:
                await ctx.reply(f"**Clear** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                "This command does not work in DMs.", delete_after=10, mention_author=False)
                status = "fault"

        except Exception:
            utils.error("clear_command()")
            status = "error"

        await utils.stat_bot_commands("clear", status, ctx.author.id, guild_id)

    @commands.command(name="emojis", aliases=["e"],
                      description="Sends many emojis, possible to be multiplied by 1-27 times.\n"
                                  "All emojis of Discord are supported, also custom ones and custom animated ones.\n"
                                  "If you don't have Nitro, you need to insert animated emojis as following `:name_of_animated_emoji:`.\n"
                                  "`<emoji_combinations>` can be just one, or multiple, but there must be no space between these emojis!\n"
                                  "You can reply to a previous message so the bot can reply to that message with these emojis.",
                      usage="<emoji_combinations> <amount>")
    async def emojis_command(self, ctx, *args):
        status = "ongoing"
        guild_id = None
        try:
            if ctx.guild:
                guild_id = ctx.guild.id
                data = await utils.execute_sql(f"SELECT emojis_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
                user = ctx.guild.me
            else:
                data = [[True]]
                user = ctx.channel.me

            if data[0][0]:
                emojis_args = []
                for emoji_list in args:
                    for emoji in list(emoji_list):
                        emoji_name = unicodedata.name(emoji)
                        if emoji_name.startswith("REGIONAL INDICATOR SYMBOL LETTER"):
                            emoji = f":regional_indicator_{emoji_name.split(' ')[-1].lower()}:"
                        emojis_args.append(emoji)

                try:
                    amount = int(args[-1])
                    emojis_args.pop()
                except ValueError:
                    amount = 1


                emojis = []
                for emoji in emojis_args:
                    emojis.append(emojilib.demojize(emoji))
                emojis_str = "".join(emojis)
                emojis_split = emojis_str.replace("<", "|").replace(">", "|").split("|")

                i = 0
                while i < len(emojis_split):
                    partial_emoji = discord.PartialEmoji.from_str(emojis_split[i])
                    if str(partial_emoji) != str(emojis_split[i]):
                        if ctx.guild:
                            emoji = discord.utils.get(ctx.guild.emojis, id=partial_emoji.id)
                        else:
                            emoji = None
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
                            if not other_emoji_split[j].startswith("regional_indicator"):
                                if ctx.guild:
                                    emoji = discord.utils.get(ctx.guild.emojis, name=other_emoji_split[j])
                                else:
                                    emoji = None
                                if emoji is None:
                                    emoji = discord.utils.get(self.bot.emojis, name=other_emoji_split[j])
                                    if emoji is None:
                                        emoji = emojilib.emojize(":" + other_emoji_split[j] + ":")
                                        if emoji == ":" + other_emoji_split[j] + ":":
                                            other_emoji_split[j] = ""
                                            j += 1
                                            continue
                                other_emoji_split[j] = str(emoji)
                            else:
                                other_emoji_split[j] = ":" + other_emoji_split[j] + ":"

                            j += 1

                        emojis_split[i] = "".join(other_emoji_split)
                    i += 1

                emojis = ""
                for emojis_splitter in emojis_split:
                    if not len(emojis + emojis_splitter) > 2000:
                        emojis += emojis_splitter
                    else:
                        break

                if emojis == "":
                    await ctx.reply(f"**Emojis** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                    "Did not find specified emoji.", mention_author=False, delete_after=10)
                    status = "fault"

                if status != "fault":
                    try:
                        amount = int(amount)
                        if amount < 0:
                            amount = amount * (-1)
                        if amount > 27 or amount == 0:
                            amount = 27
                    except Exception:
                        await ctx.reply(content=f"**Emojis** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                                "Please provide a usable number.", mention_author=False, delete_after=10)
                        status = "fault"

                    if status != "fault":
                        output = ""
                        for i in range(amount):
                            if not len(output + emojis) > 2000:
                                output += str(emojis)
                            else:
                                break

                        if ctx.channel.permissions_for(user).manage_messages:
                            await ctx.message.delete()
                        if ctx.message.reference is not None and ctx.message.reference.resolved is not None and type(ctx.message.reference.resolved) == discord.Message:
                            await ctx.message.reference.resolved.reply(output)
                        else:
                            await ctx.send(output)
                        status = "success"
            else:
                return
        except Exception:
            utils.error("emojis_command()")
            status = "error"

        await utils.stat_bot_commands("emojis", status, ctx.author.id, guild_id)

    @commands.command(name="help",
                      description="Shows a help menu with categorys and their commands.\n"
                                  "There are currently two categorys `commands` and `events`.\n"
                                  "When admins request the help page for a command, they can update command specific settings.\n"
                                  "This command can not be deactivated.",
                      aliases=["commands", "command", "settings", "setting"], usage="<category/command>")
    async def help_command(self, ctx, parameter=None):
        status = "ongoing"
        guild_id = None
        try:
            if ctx.guild:
                guild_id = ctx.guild.id
                data = await utils.execute_sql(f"SELECT help_ignore_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            else:
                data = [[True]]
            if data[0][0]:
                content, embed, delete, status = await self.generate_help_text(ctx, parameter)
                view = await self.generate_help_view(ctx, parameter)

                await ctx.reply(content=content, embed=embed, view=view, delete_after=delete, mention_author=False)
                if status != "fault":
                    status = "success"
            else:
                return

        except Exception:
            utils.error("help_command()")
            status = "error"

        await utils.stat_bot_commands("help", status, ctx.author.id, guild_id)

    async def generate_help_text(self, ctx, parameter):
        status = "ongoing"
        if ctx.guild:
            if ctx.channel.permissions_for(ctx.author.guild.me).embed_links is False:
                content = (f"**Help Command** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                           f"I don't have permission to use embed messages.\nPlease provide the `Embed Links` permission.")
                return content, None, 10, "fault"
            color = ctx.channel.guild.me.color.value
        else:
            color = discord.Colour.random()

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
                commands_list = ""

                for command in cog_commands:
                    description = command.description.split('\n')[0]
                    commands_list += f"**{command.name}** - *{description}*\n"

                embed.add_field(
                    name="\u200b\n" + cog,
                    value=commands_list,
                    inline=False
                )

            version = self.bot.version
            guilds = str(len(self.bot.guilds))
            start = str(int(utils.get_start_timestamp(raw=True).timestamp()))
            session = str(utils.session_id)
            embed.add_field(
                    name="\u200b\nSome Statistics",
                    value=f"**Version** - *{version}*\n"
                          f"**Guilds** - *{guilds}*\n"
                          f"**Startup** - *<t:{start}:R>*\n"
                          f"**Session** - *{session}*",
                    inline=False
                )

        elif parameter.lower() in lower_cogs:
            cog = self.bot.get_cog(cogs[lower_cogs.index(parameter.lower())])
            embed.title += f" - Category {cog.qualified_name}"
            commands_list = cog.get_commands()

            for command in commands_list:

                command_name = command.callback.__name__.replace("_command", "")
                command_status = " - *Enabled*"
                if not command_name.startswith("help"):
                    enabled = await utils.execute_sql(f"SELECT {command_name}_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
                    if not enabled[0][0]:
                        command_status = " - *Disabled*"

                description = f"{command.description}\n"

                aliases = f"Aliases: `{', '.join(command.aliases)}`\n"

                syntax = ""
                if parameter.lower() != "events":
                    syntax = f"Syntax: `{ctx.prefix}{command.name}{' ' + command.usage if command.usage is not None else ''}`"

                embed.add_field(
                    name="\u200b\n" + command.name + command_status,
                    value=description + (aliases if len(command.aliases) > 0 else "") + syntax,
                    inline=False
                )

        elif parameter.lower() in lower_commands:
            command = self.bot.get_command(commands[lower_commands.index(parameter.lower())])

            embed.title += f" - {command.cog.qualified_name.strip('s')} {command.name}"

            description = f"{command.description}\n"

            aliases = f"Aliases: `{', '.join(command.aliases)}`\n"

            syntax = ""
            if command.cog_name.lower() != "events":
                syntax = f"Syntax: `{ctx.prefix}{command.name}{' ' + command.usage if command.usage is not None else ''}`"

            embed.add_field(
                name="\u200b\nDetails",
                value=description + (aliases if len(command.aliases) > 0 else "") + syntax,
                inline=False
            )

            if ctx.guild is not None:
                description = await utils.execute_sql(f"DESCRIBE set_guilds", True)
                values = await utils.execute_sql(f"SELECT * FROM set_guilds WHERE guild_id = '{ctx.guild.id}'", True)

                command_name = command.callback.__name__.replace("_command", "")

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
                                    try:
                                        value = (await ctx.guild.fetch_channel(value)).mention
                                    except:
                                        value = None

                            elif config.startswith("text_channel"):
                                setting = config[13:].replace("_", " ").title()
                                if value is not None:
                                    try:
                                        value = (await ctx.guild.fetch_channel(value)).mention
                                    except:
                                        value = None

                            elif config.startswith("role"):
                                setting = config[5:].replace("_", " ").title()
                                if value is not None:
                                    try:
                                        value = ctx.guild.get_role(value).mention
                                    except:
                                        value = None

                            elif config.startswith("seconds"):
                                setting = config[7:].replace("_", " ").title()
                                value = f"`{str(value)}s`"

                            elif config.startswith("variable"):
                                setting = config[8:].replace("_", " ").title()
                                value = f"{str(value)}".replace("%user%", ctx.author.mention)

                            else:
                                setting = config

                            settings += f"**{setting}:** {value}\n"
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
            content = (f"**Help Command** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                       "Invalid category or command specified.")
            return content, None, 10, "fault"

        embed.add_field(name="", value=f"[{self.bot.user.display_name} in the web](https://bots.muffintime.tk/{self.bot.user.display_name.replace(' ', '-')}/)", inline=False)

        return None, embed, None, status

    async def generate_help_view(self, ctx, parameter, index=0):
        if parameter is not None and ctx.guild is not None:
            values = await utils.execute_sql(f"SELECT * FROM set_guilds WHERE guild_id = '{ctx.guild.id}'", True)
            moderator = values[0][10] if values[0][10] is not None else 0

            if ctx.channel.permissions_for(ctx.author).administrator or ctx.author.get_role(moderator) is not None:
                description = await utils.execute_sql(f"DESCRIBE set_guilds", True)
                cogs = [c for c in self.bot.cogs.keys()]
                lower_cogs = [c.lower() for c in cogs]

                if parameter.lower() in lower_cogs:
                    return None

                commands = [c.name for c in self.bot.commands]
                lower_commands = [c.lower() for c in commands]

                if parameter.lower() not in lower_commands:
                    return None

                command = self.bot.get_command(commands[lower_commands.index(parameter.lower())])
                command_name = command.callback.__name__.replace("_command", "")

                options = []

                settings = []
                i = 0
                while i < len(description):
                    if description[i][0].startswith(command_name):
                        if not description[i][0][len(command_name) + 1:].startswith("ignore"):
                            settings.append(i)
                    i += 1

                if settings:
                    config = description[settings[index]][0][len(command_name) + 1:]
                    value = values[0][settings[index]]
                    select = None

                    if config.startswith("bool"):
                        select = "custom"
                        options_id = "bool"
                        name = config[5:].replace("_", " ").title()
                        options.append(discord.SelectOption(label="Yes", description="Enable this feature.", emoji="✅", default=True if value == 1 else False))
                        options.append(discord.SelectOption(label="No", description="Disable this feature.", emoji="❌", default=False if value == 1 else True))

                    elif config.startswith("voice_channel"):
                        select = "voice"
                        name = config[14:].replace("_", " ").title()
                        try:
                            options.append(discord.SelectDefaultValue.from_channel(ctx.guild.get_channel(value)))
                        except:
                            options.append(None)

                    elif config.startswith("text_channel"):
                        select = "text"
                        name = config[13:].replace("_", " ").title()
                        try:
                            options.append(discord.SelectDefaultValue.from_channel(ctx.guild.get_channel(value)))
                        except:
                            options.append(None)

                    elif config.startswith("role"):
                        select = "role"
                        name = config[5:].replace("_", " ").title()
                        try:
                            options.append(discord.SelectDefaultValue.from_role(ctx.guild.get_role(value)) if value is not None else None)
                        except:
                            options.append(None)

                    elif config.startswith("seconds"):
                        select = "custom"
                        name = config[8:].replace("_", " ").title()
                        time_spans = [[60, 1], [60, 5], [60, 15], [60, 30], [60, 60]]
                        custom = True
                        for span in time_spans:
                            default = False
                            if span[0] * span[1] == value:
                                custom = False
                                default = True
                            options.append(discord.SelectOption(label=str(span[1]) + "min", description="Use this duration.", emoji="⌛", default=default))

                        options.append(discord.SelectOption(label="Custom value...", description="Set a new custom duration.", emoji="⌛", default=False))
                        if custom:
                            options.append(discord.SelectOption(label=f"Custom value: {value}s", description="Use this duration.", emoji="⌛", default=True))

                    elif config.startswith("variable"):
                        select = "custom"
                        name = config[9:].replace("_", " ").title()
                        options.append(discord.SelectOption(label="Custom message...", description="Set a new custom message.", emoji="🗨", default=False))
                        options.append(discord.SelectOption(label=f"Custom message: {value}", description="Use the current message.", emoji="🗨", default=True))

                    else:
                        name = config

                    current_label = "Setting: " + name

                    if index == 0:
                        previous_disabled = True
                    else:
                        previous_disabled = False

                    if index == len(settings) - 1:
                        next_disabled = True
                    else:
                        next_disabled = False

                    return Commands.SettingsView(self, ctx, parameter, index, options, previous_disabled, current_label, next_disabled, select)
        return None

    class SettingsView(discord.ui.View):
        class Button(discord.ui.Button):
            def __init__(self, commands_object, ctx, parameter, index, label, style, disabled, custom_id, url=None):
                self.commands_object = commands_object
                self.ctx = ctx
                self.parameter = parameter
                self.index = index
                super().__init__(label=label, style=style, disabled=disabled, custom_id=custom_id, url=url)

            async def callback(self, interaction: discord.Interaction):
                if interaction.data["custom_id"] == "previous":
                    self.index -= 1
                elif interaction.data["custom_id"] == "next":
                    self.index += 1

                content, embed, delete, status = await Commands.generate_help_text(self.commands_object, self.ctx, self.parameter)
                view = await Commands.generate_help_view(self.commands_object, self.ctx, self.parameter, self.index)
                await interaction.response.edit_message(content=content, embed=embed, view=view, delete_after=delete)

        class RoleSelect(discord.ui.RoleSelect):
            def __init__(self, commands_object, ctx, parameter, index, default):
                self.commands_object = commands_object
                self.ctx = ctx
                self.parameter = parameter
                self.index = index
                if default[0] is not None:
                    super().__init__(min_values=0, max_values=1, default_values=default)
                else:
                    super().__init__(min_values=0, max_values=1)


            async def callback(self, interaction: discord.Interaction):
                description = await utils.execute_sql(f"DESCRIBE set_guilds", True)
                values = await utils.execute_sql(f"SELECT * FROM set_guilds WHERE guild_id = '{interaction.guild.id}'", True)

                commands = [c.name for c in self.commands_object.bot.commands]
                lower_commands = [c.lower() for c in commands]
                command = self.commands_object.bot.get_command(commands[lower_commands.index(self.parameter.lower())])
                command_name = command.callback.__name__.replace("_command", "")

                settings = []
                i = 0
                while i < len(description):
                    if description[i][0].startswith(command_name):
                        if not description[i][0][len(command_name) + 1:].startswith("ignore"):
                            settings.append(i)
                    i += 1

                config = description[settings[self.index]][0][len(command_name) + 1:]

                data = interaction.data["values"]

                if len(data) == 1:
                    data = f"'{data[0]}'"
                else:
                    data = "NULL"
                await utils.execute_sql(f"UPDATE set_guilds SET {description[settings[self.index]][0]} = {data} WHERE guild_id ='{interaction.guild.id}'", False)

                content, embed, delete, status = await Commands.generate_help_text(self.commands_object, self.ctx, self.parameter)
                view = await Commands.generate_help_view(self.commands_object, self.ctx, self.parameter, self.index)
                await interaction.response.edit_message(content=content, embed=embed, view=view, delete_after=delete)

        class ChannelSelect(discord.ui.ChannelSelect):
            def __init__(self, commands_object, ctx, parameter, index, default, channel_type):
                self.commands_object = commands_object
                self.ctx = ctx
                self.parameter = parameter
                self.index = index
                if default[0] is not None:
                    super().__init__(min_values=0, max_values=1, default_values=default, channel_types=channel_type)
                else:
                    super().__init__(min_values=0, max_values=1, channel_types=channel_type)

            async def callback(self, interaction: discord.Interaction):
                description = await utils.execute_sql(f"DESCRIBE set_guilds", True)
                values = await utils.execute_sql(f"SELECT * FROM set_guilds WHERE guild_id = '{interaction.guild.id}'", True)

                commands = [c.name for c in self.commands_object.bot.commands]
                lower_commands = [c.lower() for c in commands]
                command = self.commands_object.bot.get_command(commands[lower_commands.index(self.parameter.lower())])
                command_name = command.callback.__name__.replace("_command", "")

                settings = []
                i = 0
                while i < len(description):
                    if description[i][0].startswith(command_name):
                        if not description[i][0][len(command_name) + 1:].startswith("ignore"):
                            settings.append(i)
                    i += 1

                config = description[settings[self.index]][0][len(command_name) + 1:]

                data = interaction.data["values"]

                if len(data) == 1:
                    data = f"'{data[0]}'"
                else:
                    data = "NULL"
                await utils.execute_sql(f"UPDATE set_guilds SET {description[settings[self.index]][0]} = {data} WHERE guild_id ='{interaction.guild.id}'", False)

                content, embed, delete, status = await Commands.generate_help_text(self.commands_object, self.ctx, self.parameter)
                view = await Commands.generate_help_view(self.commands_object, self.ctx, self.parameter, self.index)
                await interaction.response.edit_message(content=content, embed=embed, view=view, delete_after=delete)

        class Select(discord.ui.Select):
            def __init__(self, commands_object, ctx, parameter, index, options):
                self.commands_object = commands_object
                self.ctx = ctx
                self.parameter = parameter
                self.index = index
                super().__init__(min_values=1, max_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                description = await utils.execute_sql(f"DESCRIBE set_guilds", True)
                values = await utils.execute_sql(f"SELECT * FROM set_guilds WHERE guild_id = '{interaction.guild.id}'", True)

                commands = [c.name for c in self.commands_object.bot.commands]
                lower_commands = [c.lower() for c in commands]
                command = self.commands_object.bot.get_command(commands[lower_commands.index(self.parameter.lower())])
                command_name = command.callback.__name__.replace("_command", "")

                settings = []
                i = 0
                while i < len(description):
                    if description[i][0].startswith(command_name):
                        if not description[i][0][len(command_name) + 1:].startswith("ignore"):
                            settings.append(i)
                    i += 1

                config = description[settings[self.index]][0][len(command_name) + 1:]

                data = interaction.data["values"][0]
                if config.startswith("bool"):
                    if data.startswith("No"):
                        data = 0
                    else:
                        data = 1
                    await utils.execute_sql(f"UPDATE set_guilds SET {description[settings[self.index]][0]} = {data} WHERE guild_id ='{interaction.guild.id}'", False)

                elif config.startswith("seconds"):
                    if data.endswith("min"):
                        data = int(data.replace("min", "")) * 60
                        await utils.execute_sql(f"UPDATE set_guilds SET {description[settings[self.index]][0]} = '{data}' WHERE guild_id ='{interaction.guild.id}'", False)
                    else:
                        await interaction.response.send_modal(
                            Commands.Modal(self.commands_object, self.ctx, self.parameter, self.index, "Set a new duration",
                                           "Select the new duration in seconds", str(values[0][settings[self.index]]),
                                           "Custom duration in seconds..."))

                elif config.startswith("variable"):
                    await interaction.response.send_modal(
                        Commands.Modal(self.commands_object, self.ctx, self.parameter, self.index, "Set a new message",
                                       "Write your custom message", str(values[0][settings[self.index]]),
                                       "Message..."))

                content, embed, delete, status = await Commands.generate_help_text(self.commands_object, self.ctx, self.parameter)
                view = await Commands.generate_help_view(self.commands_object, self.ctx, self.parameter, self.index)
                try:
                    await interaction.response.edit_message(content=content, embed=embed, view=view, delete_after=delete)
                except discord.errors.InteractionResponded:
                    await interaction.edit_original_response(content=content, embed=embed, view=view)

        def __init__(self, commands_object, ctx, parameter, index, options, previous_disabled, current_label, next_disabled, select):
            self.ctx = ctx
            super().__init__()

            if select == "custom":
                self.add_item(Commands.SettingsView.Select(commands_object, ctx, parameter, index, options))
            elif select == "role":
                self.add_item(Commands.SettingsView.RoleSelect(commands_object, ctx, parameter, index, options))
            elif select == "voice":
                self.add_item(Commands.SettingsView.ChannelSelect(commands_object, ctx, parameter, index, options, [discord.ChannelType.voice]))
            elif select == "text":
                self.add_item(Commands.SettingsView.ChannelSelect(commands_object, ctx, parameter, index, options, [discord.ChannelType.text]))

            previous_style = discord.ButtonStyle.green
            self.add_item(Commands.SettingsView.Button(commands_object, ctx, parameter, index, "◀ Previous", previous_style, previous_disabled, "previous"))

            current_style = discord.ButtonStyle.blurple
            self.add_item(Commands.SettingsView.Button(commands_object, ctx, parameter, index, current_label, current_style, False, None, "https://www.youtube.com/watch?v=dQw4w9WgXcQ"))

            next_style = discord.ButtonStyle.green
            self.add_item(Commands.SettingsView.Button(commands_object, ctx, parameter, index, "Next ▶", next_style, next_disabled, "next"))

        async def interaction_check(self, interaction: discord.Interaction):
            if self.ctx.author.id == interaction.user.id:
                return True
            return False

    class Modal(discord.ui.Modal):
        class TextInput(discord.ui.TextInput):
            def __init__(self, label, default, placeholder):
                super().__init__(label=label, default=default, placeholder=placeholder)

        def __init__(self, commands_object, ctx, parameter, index, title, label, default, placeholder):
            self.commands_object = commands_object
            self.ctx = ctx
            self.parameter = parameter
            self.index = index
            super().__init__(title=title)

            self.add_item(Commands.Modal.TextInput(label, default, placeholder))

        async def on_submit(self, interaction) -> None:
            self.stop()

            description = await utils.execute_sql(f"DESCRIBE set_guilds", True)
            values = await utils.execute_sql(f"SELECT * FROM set_guilds WHERE guild_id = '{interaction.guild.id}'", True)

            commands = [c.name for c in self.commands_object.bot.commands]
            lower_commands = [c.lower() for c in commands]
            command = self.commands_object.bot.get_command(commands[lower_commands.index(self.parameter.lower())])
            command_name = command.callback.__name__.replace("_command", "")

            settings = []
            i = 0
            while i < len(description):
                if description[i][0].startswith(command_name):
                    if not description[i][0][len(command_name) + 1:].startswith("ignore"):
                        settings.append(i)
                i += 1

            data = interaction.data["components"][0]["components"][0]["value"]

            config = description[settings[self.index]][0][len(command_name) + 1:]

            if config.startswith("seconds"):
                try:
                    data = int(data)
                    await utils.execute_sql(f"UPDATE set_guilds SET {description[settings[self.index]][0]} = '{data}' WHERE guild_id ='{interaction.guild.id}'", False)
                except:
                    pass
            elif config.startswith("variable"):
                await utils.execute_sql(f"UPDATE set_guilds SET {description[settings[self.index]][0]} = %s WHERE guild_id ='{interaction.guild.id}'", False, str(data))

            content, embed, delete, status = await Commands.generate_help_text(self.commands_object, self.ctx, self.parameter)
            view = await Commands.generate_help_view(self.commands_object, self.ctx, self.parameter, self.index)
            try:
                await interaction.response.edit_message(content=content, embed=embed, view=view, delete_after=delete)
            except discord.errors.InteractionResponded:
                await interaction.edit_original_response(content=content, embed=embed, view=view)

        async def interaction_check(self, interaction: discord.Interaction):
            if self.ctx.author.id == interaction.user.id:
                return True
            return False

    @commands.command(name="screenshare", aliases=["ss"],
                      description="Sends a screenshare link for your voice channel.\n"
                                  "This command is initially disabled, since Discord released an update and removed usefulness."
                                  "Why do I keep it then?")
    async def screenshare_command(self, ctx):
        status = "ongoing"
        guild_id = None
        try:
            if ctx.guild:
                guild_id = ctx.guild.id
                data = await utils.execute_sql(f"SELECT screenshare_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
                if data[0][0]:
                    if ctx.author.voice:
                        channel = ctx.author.voice.channel
                        await ctx.reply(f"**Screenshare**\n"
                                        f"If you want to share your screen in <#{channel.id}>, use this link:\n"
                                        f"<https://discordapp.com/channels/{ctx.guild.id}/{channel.id}/>", mention_author=False)
                        status = "success"
                    else:
                        await ctx.reply(f"**Screenshare** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                        "You are not in a voice channel!", mention_author=False, delete_after=10)
                        status = "fault"
                else:
                    return
            else:
                await ctx.reply(f"**BackupChannel** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                "This command does not work in DMs.", delete_after=10, mention_author=False)
                status = "fault"
        except Exception:
            utils.error("screenshare_command()")
            status = "error"

        await utils.stat_bot_commands("screenshare", status, ctx.author.id, guild_id)


async def setup(bot):
    await bot.add_cog(Commands(bot))

import asyncio
import datetime
import discord
import emoji as emojilib
import traceback
import utils
from discord.ext import commands


class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", description="PONG! Pings and message round-trips.")
    async def ping_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT ping_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                start = datetime.datetime.now()
                msg = await ctx.reply(content="**Ping?**", mention_author=False)
                await msg.edit(content=f"**Pong!**\n"
                                       f"One Message round-trip took **{int((datetime.datetime.now() - start).microseconds / 1000)}ms**.\n"
                                       f"Ping of the bot **{int(self.bot.latency * 1000)}ms**.", allowed_mentions=discord.AllowedMentions.none())
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("ping_command()", *trace)

    @commands.command(name="backupchannel",
                      description="Can be used to back up a channel to another one.\n" 
                                  "This command is initially disabled, since it is currently only available to bot creators.",
                      usage="<from_channel_id> <to_channel_id>")
    async def backup_channel_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT backup_channel_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                if ctx.author.id == 412235309204635649:
                    content = ctx.message.content.split(" ")
                    if len(content) == 3:
                        try:
                            from_channel = ctx.guild.get_channel(int(content[1]))
                            to_channel = ctx.guild.get_channel(int(content[2]))
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
                    await ctx.reply(f"**BackupChannel** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                    "You have no permission to use this command.", delete_after=10, mention_author=False)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("backup_channel_command()", *trace)

    @commands.command(name="clean", description="Deletes all messages affecting this bot.")
    async def clean_command(self, ctx):
        try:
            data = await utils.execute_sql(f"SELECT clean_bool_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                if ctx.channel.permissions_for(ctx.guild.me).manage_messages and ctx.channel.permissions_for(ctx.guild.me).read_message_history is True:
                    message = await ctx.reply(content="**CleanUp**\nDeleting...", mention_author=False)

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

                    await message.edit(content=f"**CleanUp** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                               f"Deleted **{len(deleted) - 1}** message(s).", delete_after=10)
                else:
                    await ctx.reply(f"**CleanUp** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                    "Missing permission to delete messages.\n"
                                    "Please provide the `Manage Messages` and `Read Message History` permission.", delete_after=10, mention_author=False)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("clean_command()", *trace)

    @commands.command(name="clear",
                      description="Deletes a specific amount of messages.\n"
                                  "You can also reply to a message, then the bot deletes all messages up to the replied one.",
                      usage="<amount>")
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
                            await ctx.reply(content=f"**ClearUp** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>"
                                                    "\nIncorrect command usage.", delete_after=10, mention_author=False)
                            return
                    message = await ctx.reply(content="**ClearUp**\nDeleting...", mention_author=False)

                    def is_clear_message(m):
                        if m == message:
                            return False
                        return True

                    deleted = await ctx.channel.purge(limit=amount + 2, check=is_clear_message, bulk=True)

                    await message.edit(content=f"**ClearUp**\nDeleted **{len(deleted) - 1}** message(s).", delete_after=5)
                else:
                    await ctx.reply(f"**ClearUp** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                    "Missing permission to delete messages.\n"
                                    "Please provide the `Manage Messages` and `Read Message History` permission.", delete_after=10, mention_author=False)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("clear_command()", *trace)

    @commands.command(name="emojis", aliases=["e"],
                      description="Sends many emojis, possible to be multiplied by 1-27 times.\n"
                                  "All emojis of Discord are supported, also custom ones and custom animated ones.\n"
                                  "If you don't have Nitro, you need to insert animated emojis as following `:name_of_animated_emoji:`.\n"
                                  "`<emoji_combinations>` can be just one, or multiple, but there must be no space between these emojis!\n"
                                  "You can reply to a previous message so the bot can reply to that message with these emojis.",
                      usage="<emoji_combinations> <amount>")
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
                    await ctx.reply(f"**Emojis** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                    "Did not find specified emoji.", mention_author=False, delete_after=10)
                    return

                try:
                    amount = int(amount)
                    if amount < 0:
                        amount = amount * (-1)
                    if amount > 27 or amount == 0:
                        amount = 27
                except Exception:
                    await ctx.reply(content=f"**Emojis** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                            "Please provide a usable number.", mention_author=False, delete_after=10)
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

    @commands.command(name="help",
                      description="Shows a help menu with categorys and their commands.\n"
                                  "There are currently two categorys `commands` and `events`.\n"
                                  "When admins request the help page for a command, they can update command specific settings.\n"
                                  "This command can not be deactivated.",
                      aliases=["commands", "command", "settings", "setting"], usage="<category/command>")
    async def help_command(self, ctx, parameter=None):
        try:
            data = await utils.execute_sql(f"SELECT help_ignore_enabled FROM set_guilds WHERE guild_id ='{ctx.guild.id}'", True)
            if data[0][0]:
                content, embed, delete = await self.generate_help_text(ctx, parameter)
                view = await self.generate_help_view(ctx, parameter)

                await ctx.reply(content=content, embed=embed, view=view, delete_after=delete, mention_author=False)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("help_command()", *trace)

    async def generate_help_text(self, ctx, parameter):
        try:
            if str(ctx.channel.type) == "private":
                color = discord.Colour.random()
            else:
                if ctx.channel.permissions_for(ctx.author.guild.me).embed_links is False:
                    content = (f"**Help Command** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                               f"I don't have permission to use embed messages.\nPlease provide the `Embed Links` permission.")
                    return content, None, 10
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
                    commands_list = ""

                    for command in cog_commands:
                        commands_list += f"**{command.name}** - *{command.description}*\n"

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
                        value=description + (aliases if len(command.aliases) > 0 else "") + syntax,
                        inline=False
                    )

            elif parameter.lower() in lower_commands:
                command = self.bot.get_command(commands[lower_commands.index(parameter.lower())])

                embed.title += f" - {command.cog.qualified_name.strip('s')} {command.name}"

                description = f"{command.description}\n"

                aliases = f"Aliases: `{', '.join(command.aliases)}`\n"

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
                                        value = (await ctx.guild.fetch_channel(value)).mention
                                elif config.startswith("seconds"):
                                    setting = config[7:].replace("_", " ").title()
                                    value = f"`{str(value)}s`"
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
                return content, None, 10

            return None, embed, None

        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("help_command()", *trace)

    async def generate_help_view(self, ctx, parameter, index=0):
        if parameter is not None and ctx.guild is not None:
            description = await utils.execute_sql(f"DESCRIBE set_guilds", True)
            values = await utils.execute_sql(f"SELECT * FROM set_guilds WHERE guild_id = '{ctx.guild.id}'", True)

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
            text_label = None
            text_default = None

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

                if config.startswith("bool"):
                    options_id = "bool"
                    name = config[5:].replace("_", " ").title()
                    if value == 1:
                        default = True
                    else:
                        default = False
                    options.append(discord.SelectOption(label="Yes", description="Enable this feature.", emoji="✅", default=default))
                    options.append(discord.SelectOption(label="No", description="Disable this feature.", emoji="❌", default=not default))

                elif config.startswith("voice_channel"):
                    name = config[14:].replace("_", " ").title()
                    voice_channels = [channel for channel in (await ctx.guild.fetch_channels()) if str(channel.type) == "voice" or str(channel.type) == "stage_voice"]
                    for channel in voice_channels:
                        default = False
                        if channel.id == value:
                            default = True
                        options.append(discord.SelectOption(label=f"{channel.name} - ID: {channel.id}", description=f"Use this voice channel.", emoji="🔉", default=default))

                elif config.startswith("seconds"):
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

                return Commands.SettingsView(self, ctx, parameter, index, options, previous_disabled, current_label, next_disabled)
        return None

    class SettingsView(discord.ui.View):
        class Button(discord.ui.Button):
            def __init__(self, commands_object, ctx, parameter, index, label, style, disabled, custom_id):
                self.commands_object = commands_object
                self.ctx = ctx
                self.parameter = parameter
                self.index = index
                super().__init__(label=label, style=style, disabled=disabled, custom_id=custom_id)

            async def callback(self, interaction: discord.Interaction):
                if interaction.data["custom_id"] == "previous":
                    self.index -= 1
                elif interaction.data["custom_id"] == "next":
                    self.index += 1

                content, embed, delete = await Commands.generate_help_text(self.commands_object, self.ctx, self.parameter)
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

                elif config.startswith("voice_channel"):
                    await utils.execute_sql(f"UPDATE set_guilds SET {description[settings[self.index]][0]} = '{data.split()[-1]}' WHERE guild_id ='{interaction.guild.id}'", False)

                elif config.startswith("seconds"):
                    if data.endswith("min"):
                        data = int(data.replace("min", "")) * 60
                        await utils.execute_sql(f"UPDATE set_guilds SET {description[settings[self.index]][0]} = '{data}' WHERE guild_id ='{interaction.guild.id}'", False)
                    else:
                        await interaction.response.send_modal(Commands.Modal(self.commands_object, self.ctx, self.parameter, self.index, "Set a new duration", "Select the new duration in seconds", str(values[0][settings[self.index]]), "Custom duration in seconds..."))

                content, embed, delete = await Commands.generate_help_text(self.commands_object, self.ctx, self.parameter)
                view = await Commands.generate_help_view(self.commands_object, self.ctx, self.parameter, self.index)
                await interaction.response.edit_message(content=content, embed=embed, view=view, delete_after=delete)

        def __init__(self, commands_object, ctx, parameter, index, options, previous_disabled, current_label, next_disabled):
            super().__init__()

            self.add_item(Commands.SettingsView.Select(commands_object, ctx, parameter, index, options))

            previous_style = discord.ButtonStyle.green
            self.add_item(Commands.SettingsView.Button(commands_object, ctx, parameter, index, "◀ Previous", previous_style, previous_disabled, "previous"))

            current_style = discord.ButtonStyle.blurple
            self.add_item(Commands.SettingsView.Button(commands_object, ctx, parameter, index, current_label, current_style, True, "current"))

            next_style = discord.ButtonStyle.green
            self.add_item(Commands.SettingsView.Button(commands_object, ctx, parameter, index, "Next ▶", next_style, next_disabled, "next"))

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
            try:
                data = int(data)
                await utils.execute_sql(f"UPDATE set_guilds SET {description[settings[self.index]][0]} = '{data}' WHERE guild_id ='{interaction.guild.id}'", False)
            except:
                message = await interaction.response.edit_message(content=f"**Help Command** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                                                          "Invalid value entered.", embed=None, view=None)
                await asyncio.sleep(10)

            content, embed, delete = await Commands.generate_help_text(self.commands_object, self.ctx, self.parameter)
            view = await Commands.generate_help_view(self.commands_object, self.ctx, self.parameter, self.index)
            try:
                await interaction.response.edit_message(content=content, embed=embed, view=view, delete_after=delete)
            except discord.errors.InteractionResponded:
                await interaction.edit_original_response(content=content, embed=embed, view=view)

    @commands.command(name="screenshare", aliases=["ss"],
                      description="Sends a screenshare link for your voice channel.\n"
                                  "This command is initially disabled, since Discord released an update and removed usefulness."
                                  "Why do I keep it then?")
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
                    await ctx.reply(f"**Screenshare** - Dismissed <t:{int(datetime.datetime.now().timestamp()) + 10}:R>\n"
                                    "You are not in a voice channel!", mention_author=False, delete_after=10)
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("screenshare_command()", *trace)


async def setup(bot):
    await bot.add_cog(Commands(bot))

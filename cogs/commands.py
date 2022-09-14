import datetime
import discord
import traceback
import utils
from discord.ext import commands


emojis = [["LOL", "lollipop", ["🍭"]], ["POOP", "poop", ["💩"]], ["COOL", "cool", ["🇨", "🇴", "🅾", "🇱"]]]


class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', description='The help command!', aliases=['commands', 'command', 'start'], usage='<category>')
    async def help_command(self, ctx, cog='all'):
        try:
            # The third parameter comes into play when
            # only one word argument has to be passed by the user

            # Prepare the embed
            if str(ctx.channel.type) == "private":
                color = discord.Colour.random()
            else:
                if ctx.channel.permissions_for(ctx.author.guild.me).embed_links is False:
                    await ctx.send(channel=ctx.channel, author=ctx.author,
                                   message="Can't answer:\nI don't have permission to embed links.", delete=10)
                    return
                color = ctx.channel.guild.me.color.value

            help_embed = discord.Embed(color=color)

            help_embed.set_footer(
                text=f'Requested by {ctx.message.author.name}',
                icon_url=ctx.message.author.avatar
            )

            # Get a list of all cogs
            cogs = [c for c in self.bot.cogs.keys()]

            # If cog is not specified by the user, we list all cogs and commands

            if cog == 'all':

                help_embed.title = f"Help page of {self.bot.user}"

                for cog in cogs:
                    # Get a list of all commands under each cog

                    cog_commands = self.bot.get_cog(cog).get_commands()
                    commands_list = ''
                    for command in cog_commands:
                        commands_list += f'**{command.name}** - *{command.description}*\n'

                    # Add the cog's details to the embed.

                    help_embed.add_field(
                        name=cog,
                        value=commands_list,
                        inline=False
                    ).add_field(
                        name='\u200b', value='\u200b', inline=False
                    )

                    # Also added a blank field '\u200b' is a whitespace character.
                pass
            else:

                # If the cog was specified

                lower_cogs = [c.lower() for c in cogs]

                # If the cog actually exists.
                if cog.lower() in lower_cogs:

                    # Get a list of all commands in the specified cog
                    cog_object = self.bot.get_cog(cogs[lower_cogs.index(cog.lower())])
                    help_embed.title = f"Help page for {cog.title()}"
                    commands_list = cog_object.get_commands()
                    help_text = ''

                    # Add details of each command to the help text
                    # Command Name
                    # Description
                    # [Aliases]
                    #
                    # Format
                    for command in commands_list:
                        help_text += f'**{command.name}**\n Description: {command.description}\n'

                        # Also add aliases, if there are any
                        if len(command.aliases) > 0:
                            help_text += f"Aliases: `{', '.join(command.aliases)}`\n"

                        # Finally the format
                        help_text += f'Format: `{ctx.prefix}{command.name} {command.usage if command.usage is not None else ""}`\n\n'

                    help_embed.description = help_text
                else:
                    # Notify the user of invalid cog and finish the command
                    await ctx.send('Invalid cog specified.\nUse `help` command to list all cogs.')
                    return

            await ctx.send(embed=help_embed)
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
            start = datetime.datetime.now()
            msg = await ctx.send(content='**Ping?**')
            await msg.edit(content=f'**Pong!**\n'
                                   f'One Message round-trip took **{int((datetime.datetime.now() - start).microseconds / 1000)}ms**.\n'
                                   f'Ping of the bot **{int(self.bot.latency * 1000)}ms**.')
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("ping_command()", *trace)

    @commands.command(name='backupchannel', aliases=['bc'], description='can be used to back up channel to another one')
    async def backupchannel_command(self, ctx):
        try:
            if ctx.author.id == 412235309204635649:
                content = ctx.message.content.split(" ")
                if len(content) == 3:
                    try:
                        from_channel = discord.utils.get(ctx.guild.channels, id=int(content[1]))
                        to_channel = discord.utils.get(ctx.guild.channels, id=int(content[2]))
                    except Exception as e:
                        await ctx.send("**BackupChannel**\nInvalid channels.")
                        return
                    status_message = await ctx.send(
                        f"**BackupChannel**\nBeginning backup from <#{from_channel.id}> to <#{to_channel.id}>.\nSearching for messages...")
                    backup_messages = await from_channel.history(limit=None, oldest_first=True).flatten()
                    await status_message.edit(
                        content=f"**BackupChannel**\nBeginning backup of <#{from_channel.id}> to <#{to_channel.id}>.\nFound {len(backup_messages)} messages.")
                    allowed_mentions = discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=False)
                    for message in backup_messages:
                        timestamp = int(message.created_at.timestamp())
                        if message.edited_at is not None:
                            timestamp = int(message.edited_at.timestamp())
                            await to_channel.send(f"--- At <t:{timestamp}:f> wrote <@!{message.author.id}> ---",
                                                  allowed_mentions=allowed_mentions)
                            await to_channel.send(message.content, allowed_mentions=allowed_mentions)
                else:
                    await ctx.send("**BackupChannel**\nInvalid input.")
                    return
            else:
                await ctx.send("**BackupChannel**\nNo permission to use this command.")
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("backupchannel_command()", *trace)

    @commands.command(name='screenshare', aliases=['ss'], description='can be used to share your screen in voice channels')
    async def screenshare_command(self, ctx):
        try:
            user = ctx.author
            if user.voice:
                server_id = str(int(ctx.guild.id))
                channel_id = str(int(user.voice.channel.id))
                channel = str(user.voice.channel.name)
                await ctx.send("**Screenshare**\n"
                               f"If you want to share your screen in {channel}"
                               ", use this link\n"
                               f"> <https://discordapp.com/channels/{server_id}/{channel_id}/>\n"
                               "Otherwise ignore this message")
                return
            else:
                await ctx.send("**Screenshare**\nYou are not in a voice channel!")
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("screenshare_command()", *trace)

    @commands.command(name='clean', description='cleans all messages affecting this bot')
    async def clean_command(self, ctx):
        try:
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
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("clean_command()", *trace)

    @commands.command(name='clear', description='clears messages', usage='<amount>')
    async def clear_command(self, ctx, amount):
        try:
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
        except Exception:
            trace = traceback.format_exc().rstrip("\n").split("\n")
            utils.on_error("clear_command()", *trace)

    @commands.command(name='emojis', aliases=['e'], description='sends many emojis, cip cap 27', usage='<emoji> <amount>')
    async def emojis_command(self, ctx):  # , emoji, amount
        try:
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

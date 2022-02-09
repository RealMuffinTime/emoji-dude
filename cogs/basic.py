import datetime
import discord
import discord.utils
from discord.ext import commands
import secret_dev as secret

emojis = [["LOL", "lollipop", "🍭"], ["POOP", "poop", "💩"], ["COOL", "cool", "🇨", "🇴", "🅾", "🇱"]]


class Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        author = ctx.author
        if author.bot:
            return
        if ctx.content.startswith("ed."):
            return
        if ctx.channel.permissions_for(ctx.guild.me).add_reactions:
            for emoji in emojis:
                if emoji[0] in ctx.content.upper():
                    await ctx.add_reaction(emoji[2])
                    if emoji[0] == "COOL":
                        await ctx.add_reaction(emoji[3])
                        await ctx.add_reaction(emoji[4])
                        await ctx.add_reaction(emoji[5])

    # @commands.Cog.listener()
    # async def on_member_remove(self, ctx):
    #     channel = self.bot.get_channel(646043498717380610)
    #     await channel.send("\nsomeone let us alone...\n{}".format())
    #
    # @commands.Cog.listener()
    # async def on_member_join(self, role: discord.Role, member: discord.Member = None):
    #     await self.bot.add_role(member, role)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        keyword = None
        for managed_guild in secret.managed_channels:
            if managed_guild[0] == guild.id:
                keyword = managed_guild[1]
                guild = discord.utils.get(self.bot.guilds, id=managed_guild[0])
                break
        if keyword is None:
            return
        empty_channels = []
        for channel in guild.voice_channels:
            if channel.name.startswith(keyword):
                if len(channel.voice_states.keys()) == 0:
                    empty_channels.append(channel)

        if not empty_channels:
            highest_channel = None
            for channel in guild.voice_channels:
                if channel.name.startswith(keyword):
                    pair = channel.name.split(" ")
                    pair[0] = channel
                    pair[-1] = int(pair[-1])
                    if highest_channel is None:
                        highest_channel = pair
                    elif pair[-1] > highest_channel[-1]:
                        highest_channel = pair
            channel = highest_channel[0]
            if channel.permissions_for(channel.guild.me).manage_channels:
                await guild.create_voice_channel(name=keyword + " " + str(highest_channel[-1] + 1), category=channel.category)
        else:
            lowest_channel = None
            for channel in empty_channels:
                pair = channel.name.split(" ")
                pair[0] = channel
                pair[-1] = int(pair[-1])
                if lowest_channel is None:
                    lowest_channel = pair
                elif pair[-1] < lowest_channel[-1]:
                    lowest_channel = pair
            empty_channels.remove(lowest_channel[0])
            for channel in empty_channels:
                if channel.permissions_for(channel.guild.me).manage_channels:
                    await channel.delete()

    @commands.command(name='ping', description='some pongs')
    async def ping_command(self, ctx):
        start = datetime.datetime.now()
        msg = await ctx.send(content='**Ping?**')
        await msg.edit(content=f'**Pong!**\n'
                               f'One Message round-trip took **{int((datetime.datetime.now() - start).microseconds / 1000)}ms**.\n'
                               f'Ping of the bot **{int(self.bot.latency * 1000)}ms**.')

    @commands.command(name='backupchannel', aliases=['bc'], description='can be used to backup channel to another one')
    async def backupchannel_command(self, ctx):
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
                    try:
                        await to_channel.send(f"--- At <t:{timestamp}:f> wrote <@!{message.author.id}> ---",
                                              allowed_mentions=allowed_mentions)
                        await to_channel.send(message.content, allowed_mentions=allowed_mentions)
                    except Exception as e:
                        print(e)
            else:
                await ctx.send("**BackupChannel**\nInvalid input.")
                return
        else:
            await ctx.send("**BackupChannel**\nNo permission to use this command.")

    @commands.command(name='screenshare', aliases=['ss'], description='can be used to share your screen in voice channels')
    async def screenshare_command(self, ctx):
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

    @commands.command(name='clean', description='cleans all messages affecting this bot')
    async def clean_command(self, ctx):
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

        await message.edit(content=f'**CleanUp**\nDeleted **{len(deleted) - 1}** message(s)', delete_after=5)

    @commands.command(name='clear', description='clears messages')
    async def clear_command(self, ctx):
        limit = ctx.message.content.split(" ")[-1]
        try:
            limit = int(limit)
        except Exception:
            await ctx.send(content='**ClearUp**\nIncorrect command usage.')
            return
        message = await ctx.send(content='**ClearUp**\nDeleting...')

        def is_clear_message(m):
            if m == message:
                return False
            return False

        deleted = await ctx.channel.purge(limit=limit + 2, check=is_clear_message, bulk=True)

        await message.edit(content=f'**ClearUp**\nDeleted **{len(deleted) - 1}** message(s)', delete_after=5)

    @commands.command(name='emojis', aliases=['e'], description='sends much emojis, cip cap 27')
    async def emojis_command(self, ctx):
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


def setup(bot):
    bot.add_cog(Basic(bot))

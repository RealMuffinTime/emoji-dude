from datetime import datetime as d
from discord.ext import commands

import discord

emojis = [["LOL", "lollipop", "🍭"], ["POOP", "poop", "💩"], ["COOL", "cool", "🇨", "🇴", "🅾", "🇱"]]


async def emojis_syntax(ctx):
    await ctx.send("Incorrect syntax, please type the emoji:")


class Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        discord_user = ctx.author
        if discord_user.bot:
            return
        if ctx.content.startswith("ed."):
            return
        text = ctx.content
        for emoji in emojis:
            if emoji[0] in text.upper():
                await ctx.add_reaction(emoji[2])
                if emoji[0] == "COOL":
                    await ctx.add_reaction(emoji[3])
                    await ctx.add_reaction(emoji[4])
                    await ctx.add_reaction(emoji[5])

    """"@commands.Cog.listener()
    async def on_member_remove(self, ctx):
        channel = self.bot.get_channel(646043498717380610)
        await channel.send("\nsomeone let us alone...\n{}".format())

    @commands.Cog.listener()
    async def on_member_join(self, role: discord.Role, member: discord.Member = None):
        await self.bot.add_role(member, role)"""

    @commands.command(name='ping', description='some pongs')
    async def ping_command(self, ctx):
        start = d.timestamp(d.now())
        msg = await ctx.send(content='**Pinging...**')
        await msg.edit(content='**Pong!**\nOne Message round-trip took '
                               '**{}ms**.'.format(int((d.timestamp(d.now()) - start) * 1000)) +
                               '\nPing of the bot **{}ms**'.format(int(self.bot.latency * 1000)))

    @commands.command(name='screenshare', aliases=['ss'],
                      description='can be used to share your screen in voice channels')
    async def screenshare_command(self, ctx):
        user = ctx.author
        if user.voice:
            server_id = str(int(ctx.guild.id))
            channel_id = str(int(user.voice.channel.id))
            channel = str(user.voice.channel.name)
            await ctx.channel.send("**Screenshare**\n" +
                                   "If you want to share your screen in " + channel +
                                   ", use this link\n"
                                   "> <https://discordapp.com/channels/" + server_id + "/" + channel_id + "/>\n" +
                                   "Otherwise ignore this message")
        else:
            await ctx.channel.send("**Screenshare:**\n" +
                                   ":x:You are not in a voice channel! \nYou must be in a voice channel to share your "
                                   "screen")

    @commands.command(name='clean', aliases=['c'], description='cleans all messages affecting this bot')
    async def clean_command(self, ctx):
        await ctx.send(content='**CleanUp**\nDeleting...')

        def is_me(m):
            return m.author == self.bot.user

        deleted_user = 0
        async for message in ctx.channel.history():
            if message.content.startswith("ed."):
                await message.delete()
                deleted_user += 1

        deleted_bot = await ctx.channel.purge(check=is_me)
        message = await ctx.channel.send(
            '**CleanUp**\nDeleted **{}** message(s)'.format(len(deleted_bot) - 2 + deleted_user))
        await message.delete(delay=3)

    @commands.command(name='emojis', aliases=['e'], description='sends much emojis')
    async def emojis_command(self, ctx):
        if ctx.author.bot:
            return

        msg = ctx.message.content
        prefix = ctx.prefix
        alias = ctx.invoked_with
        text = msg[len(prefix) + len(alias) + 1:]

        if text == '':
            await ctx.send(content='You need to specify the emoji and the number of these!')
            print("further")
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
                            await emojis_syntax(ctx)
                            return
                        if index > 150:
                            index = 150
                            warning = "\nUnfortunately, I can maximally send 150 " + emoji[1] + \
                                      "s :disappointed_relieved: "
                        for i in range(index):
                            send_text += ":" + emoji[1] + ":"
                        if send_text + warning != "":
                            await ctx.channel.send(send_text + warning)
                        else:
                            await emojis_syntax(ctx)
                            return
                await emojis_syntax(ctx)
                return
            await emojis_syntax(ctx)
            return


def setup(bot):
    bot.add_cog(Basic(bot))

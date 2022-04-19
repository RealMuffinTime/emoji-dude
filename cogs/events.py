import datetime

from discord.ext import commands
import utils

emojis = [["LOL", "lollipop", "🍭"], ["POOP", "poop", "💩"], ["COOL", "cool", "🇨", "🇴", "🅾", "🇱"]]


class Events(commands.Cog):

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
        if not member.bot:
            if before.self_deaf is True and after.self_deaf is True:
                last_seen = await utils.execute_sql(f"SELECT last_seen FROM set_users WHERE user_id ='{str(member.id)}'", True)
                if after.channel is not guild.afk_channel:
                    await utils.execute_sql(
                        f"INSERT INTO set_users VALUES ('{member.id}', 0, '{last_seen[0][0]}', '{after.channel.id}', '{member.guild.id}') "
                        f"ON DUPLICATE KEY UPDATE last_seen = '{last_seen[0][0]}', last_channel = '{after.channel.id}', last_guild = '{member.guild.id}'",
                        False)
            elif after.self_deaf is True and after.channel is not None:
                await utils.execute_sql(
                    f"INSERT INTO set_users VALUES ('{member.id}', 0, '{utils.get_curr_timestamp()}', '{after.channel.id}', '{member.guild.id}') "
                    f"ON DUPLICATE KEY UPDATE last_seen = '{utils.get_curr_timestamp()}', last_channel = '{after.channel.id}', last_guild = '{member.guild.id}'",
                    False)

            if before.self_deaf is True and after.self_deaf is False:
                if after.channel is guild.afk_channel:
                    last_channel = await utils.execute_sql(f"SELECT last_channel FROM set_users WHERE user_id ='{str(member.id)}'", True)
                    print(last_channel)
                    last_channel = guild.get_channel(last_channel[0][0])
                    if last_channel is not None:
                        try:
                            await member.move_to(last_channel)
                            await utils.execute_sql(f"INSERT INTO set_users VALUES ('{member.id}', 0, NULL, NULL, NULL)  ON DUPLICATE KEY UPDATE last_seen = NULL, last_channel = NULL, last_guild = NULL", False)
                            return
                        except Exception as e:
                            utils.log("error", e)
                else:
                    await utils.execute_sql(
                        f"INSERT INTO set_users VALUES ('{member.id}', 0, NULL, NULL, NULL)  ON DUPLICATE KEY UPDATE last_seen = NULL, last_channel = NULL, last_guild = NULL",
                        False)

        keyword = None
        keyword = (await utils.execute_sql(f"SELECT auto_channel FROM set_guilds WHERE guild_id ='{str(guild.id)}'", True))[0][0]
        if keyword:
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
                    await guild.create_voice_channel(name=keyword + " " + str(highest_channel[-1] + 1),
                                                     category=channel.category)
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

    @commands.command(name='AutoChannel', description='the bot creates and removes voice channels when needed')
    async def auto_channel_command(self, ctx):
        return

    @commands.command(name='AutoAFK', description='the bot moves muted users to the afk channel and back')
    async def auto_afk_command(self, ctx):
        return

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await utils.execute_sql(f"INSERT INTO set_guilds VALUES ('{guild.id}', NULL)  ON DUPLICATE KEY UPDATE auto_channel = NULL", False)
        await utils.execute_sql("INSERT INTO stat_bot_guilds (action) VALUES ('add');", False)
        utils.log("info", f"Guild join '{str(guild.name)} {str(guild.id)}'.")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await utils.execute_sql(f"UPDATE set_guilds SET auto_channel = NULL WHERE guild_id = '{guild.id}';", False)
        await utils.execute_sql("INSERT INTO stat_bot_guilds (action) VALUES ('remove');", False)
        utils.log("info", f"Guild leave '{str(guild.name)} {str(guild.id)}'.")


def setup(bot):
    bot.add_cog(Events(bot))

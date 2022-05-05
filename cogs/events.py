import datetime

from discord.ext import commands
import utils

emojis = [["LOL", "lollipop", ["🍭"]], ["POOP", "poop", ["💩"]], ["COOL", "cool", ["🇨", "🇴", "🅾", "🇱"]]]


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
                    for reaction in emoji[2]:
                        await ctx.add_reaction(reaction)

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
            member_status = await utils.execute_sql(f"SELECT afk_managed, last_seen, last_channel FROM set_users WHERE user_id ='{str(member.id)}'", True)
            if after.self_deaf is True and after.channel is not None:
                if before.self_deaf is True:
                    if before.channel is member.guild.afk_channel:
                        last_seen = member_status[0][1]
                        if member_status is None:
                            last_seen = utils.get_curr_timestamp()
                        await utils.execute_sql(
                            f"INSERT INTO set_users VALUES ('{member.id}', 0, 0, '{utils.get_curr_timestamp()}', '{after.channel.id}', '{member.guild.id}') "
                            f"ON DUPLICATE KEY UPDATE afk_managed = 0, last_seen = '{last_seen}', last_channel = '{after.channel.id}', last_guild = '{member.guild.id}'",
                            False)
                    elif after.channel is member.guild.afk_channel:
                        channel = None
                        if member_status[0][2] is not None:
                            channel = member_status[0][2]
                        elif before.channel is not None:
                            channel = before.channel.id
                        if channel is not None:
                            await utils.execute_sql(
                                f"INSERT INTO set_users VALUES ('{member.id}', 0, 1, '{utils.get_curr_timestamp()}', '{channel}', '{member.guild.id}') "
                                f"ON DUPLICATE KEY UPDATE afk_managed = 1, last_seen = '{member_status[0][1]}', last_channel = '{channel}', last_guild = '{member.guild.id}'",
                                False)
                    else:
                        await utils.execute_sql(
                            f"INSERT INTO set_users VALUES ('{member.id}', 0, 0, '{utils.get_curr_timestamp()}', '{after.channel.id}', '{member.guild.id}') "
                            f"ON DUPLICATE KEY UPDATE last_channel = '{after.channel.id}', last_guild = '{member.guild.id}'",
                            False)
                else:
                    await utils.execute_sql(
                        f"INSERT INTO set_users VALUES ('{member.id}', 0, 0, '{utils.get_curr_timestamp()}', '{after.channel.id}', '{member.guild.id}') "
                        f"ON DUPLICATE KEY UPDATE afk_managed = 0, last_seen = '{utils.get_curr_timestamp()}', last_channel = '{after.channel.id}', last_guild = '{member.guild.id}'",
                        False)
            else:
                await utils.execute_sql(f"INSERT INTO set_users VALUES ('{member.id}', 0, 0, NULL, NULL, NULL) "
                                        f"ON DUPLICATE KEY UPDATE afk_managed = 0, last_seen = NULL, last_channel = NULL, last_guild = NULL",
                                        False)

            if before.self_deaf is True and after.self_deaf is False:
                await utils.execute_sql(f"INSERT INTO set_users VALUES ('{member.id}', 0, 0, NULL, NULL, NULL) "
                                        f"ON DUPLICATE KEY UPDATE afk_managed = 0, last_seen = NULL, last_channel = NULL, last_guild = NULL",
                                        False)
                if member_status[0][0] == 1:
                    last_channel = guild.get_channel(member_status[0][2])
                    if last_channel is not None:
                        try:
                            await member.move_to(last_channel)
                            return
                        except Exception as e:
                            utils.on_error("on_voice_state_update()", str(e))

        keyword = None
        keyword = (await utils.execute_sql(f"SELECT managed_channel FROM set_guilds WHERE guild_id ='{str(guild.id)}'", True))[0][0]
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

    @commands.command(name='ManagedChannel', description='the bot creates and removes voice channels when needed')
    async def managed_channel_command(self, ctx):
        return

    @commands.command(name='ManagedAFK', description='the bot moves muted users to the afk channel and back')
    async def managed_afk_command(self, ctx):
        return

    @commands.command(name='AutoReaction', description='the bot reacts to specific parts of message with emotes')
    async def auto_reaction_command(self, ctx):
        return

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await utils.execute_sql(f"INSERT INTO set_guilds VALUES ('{guild.id}', NULL)  ON DUPLICATE KEY UPDATE managed_channel = NULL", False)
        await utils.execute_sql("INSERT INTO stat_bot_guilds (action) VALUES ('add');", False)
        utils.log("info", f"Guild join '{str(guild.name)} {str(guild.id)}'.")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await utils.execute_sql(f"UPDATE set_guilds SET managed_channel = NULL WHERE guild_id = '{guild.id}';", False)
        await utils.execute_sql("INSERT INTO stat_bot_guilds (action) VALUES ('remove');", False)
        utils.log("info", f"Guild leave '{str(guild.name)} {str(guild.id)}'.")


def setup(bot):
    bot.add_cog(Events(bot))

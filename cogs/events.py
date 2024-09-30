import logging
import discord
import utils
from discord.ext import commands


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await utils.execute_sql(f"INSERT IGNORE INTO set_guilds (guild_id) VALUES ('{guild.id}')", False)
        await utils.execute_sql("INSERT INTO stat_bot_guilds (action) VALUES ('add');", False)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await utils.execute_sql("INSERT INTO stat_bot_guilds (action) VALUES ('remove');", False)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 669895353557975080:
            await member.add_roles(member.guild.get_role(739037531802435594))

    @commands.Cog.listener()
    async def on_raw_member_remove(self, data):
        if data.guild_id == 669895353557975080:
            channel = self.bot.get_channel(699947018562568223)
            await channel.send(f"{data.user.mention} has parted ways with us...")

    @commands.Cog.listener()
    async def on_message(self, ctx):
        try:
            await self.auto_poll_thread_creation_command(ctx)
            if ctx.author.bot:
                return
            if ctx.content.startswith("ed."):
                return
            await self.auto_reaction_command(ctx)
        except Exception:
            utils.on_error("on_message()")

    @commands.Cog.listener()
    async def on_raw_message_edit(self, data):
        try:
            await self.auto_poll_thread_creation_command(data)
        except Exception:
            utils.on_error("on_raw_message_edit()")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        await self.managed_channel_command(member.guild)

        await self.managed_afk_command(member, before, after)

    @commands.command(name='AutoPollThreadCreation', description='Automatically creates threads on polls, Discord or  `Simple Poll#9879` bot polls are supported.')
    async def auto_poll_thread_creation_command(self, ctx):
        if isinstance(ctx, discord.RawMessageUpdateEvent):
            try:
                guild = self.bot.get_guild(ctx.guild_id)
                channel = guild.get_channel(ctx.channel_id)
                message = await channel.fetch_message(ctx.message_id)

                webhook_id = int(ctx.data['webhook_id'])
                if webhook_id != 324631108731928587:
                    return

                name = message.clean_content.replace("*", "").replace(":bar_chart: ", "")
                duration = 1440
            except AttributeError as e:
                return
        elif isinstance(ctx, discord.message.Message) and type(ctx.channel) == discord.TextChannel:
            message = ctx
            if not message.poll:
                return

            name = message.poll.question
            duration = round((message.poll.expires_at - message.poll.created_at).total_seconds()/60)
        else:
            return

        data = await utils.execute_sql(
            f"SELECT auto_poll_thread_creation_bool_enabled FROM set_guilds WHERE guild_id ='{message.guild.id}'", True)
        if data[0][0] and message.thread == None:
            if message.channel.permissions_for(message.guild.me).create_public_threads and message.channel.permissions_for(
                    message.guild.me).read_message_history:
                thread = await message.create_thread(
                    name=name,
                    auto_archive_duration=duration)
                await thread.leave()


    @commands.command(name='AutoReaction', description='The bot reacts to specific parts in a message with emotes.\n'
                                                       'Supported phrases are `cum`, `poop`,  `cool` and derivations.')
    async def auto_reaction_command(self, ctx):
        if isinstance(ctx, discord.Message):
            if ctx.guild:
                data = await utils.execute_sql(f"SELECT auto_reaction_bool_enabled FROM set_guilds WHERE guild_id ='{str(ctx.guild.id)}'", True)
                user = ctx.guild.me
            else:
                data = [[True]]
                user = ctx.channel.me
            if data[0][0]:
                if ctx.channel.permissions_for(user).add_reactions and ctx.channel.permissions_for(user).read_message_history:
                    emojis = [
                        ["cum", "komm", "nut", ["💦"]],
                        ["shit", "poop", "scheiß", ["💩"]],
                        ["cool", ["🇨", "🇴", "🅾", "🇱"]],
                        ["cap", "kappe", ["🧢"]]
                    ]

                    for emoji in emojis:
                        for text in emoji:
                            if type(text) is str and text in ctx.content.lower():
                                for reaction in emoji[-1]:
                                    try:
                                        await ctx.add_reaction(reaction)
                                    except discord.errors.Forbidden:
                                        pass

    @commands.command(name='ManagedAFK', description='Auto moves full muted users after a specific amount of time to the guild set AFK channel.\n'
                                                     'The last used channel is saved, so when a user is no longer full mute, he will be automatically moved to his last voice channel.\n'
                                                     'You need to set an AFK channel and give permissions to move members.')
    async def managed_afk_command(self, member, before, after):
        if isinstance(member, discord.member.Member):
            data = await utils.execute_sql(f"SELECT managed_afk_bool_enabled FROM set_guilds WHERE guild_id ='{member.guild.id}'", True)
            if data[0][0]:
                try:
                    guild = member.guild
                    if not member.bot:
                        member_status = await utils.execute_sql(f"SELECT afk_managed, last_seen, last_channel FROM set_users WHERE user_id ='{str(member.id)}'", True)
                        if after.self_deaf is True and after.channel is not None:
                            if before.self_deaf is True:
                                if before.channel is member.guild.afk_channel:
                                    last_seen = member_status[0][1]
                                    if last_seen is None:
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
                                    if guild.afk_channel.permissions_for(guild.me).move_members and last_channel.permissions_for(guild.me).move_members:
                                        await member.move_to(last_channel)
                except Exception:
                    utils.on_error("managed_afk_command()")

    @commands.command(name='ManagedChannel', description='Automatically creates voice channels when needed, and removes unused.')
    async def managed_channel_command(self, guild):
        if isinstance(guild, discord.guild.Guild):
            data = await utils.execute_sql(f"SELECT managed_channel_bool_enabled, managed_channel_voice_channel_channel, managed_channel_ignore_running FROM set_guilds WHERE guild_id ='{guild.id}'", True)
            if data[0][0]:
                try:
                    if data[0][2] == 0:
                        await utils.execute_sql(f"UPDATE set_guilds SET managed_channel_ignore_running = 1 WHERE guild_id ='{str(guild.id)}'", False)

                        reset_channel = False
                        if guild.get_channel(data[0][1]) is not None:
                            key_channel = guild.get_channel(data[0][1]).name.split(" ")
                            key_channel.pop(-1)
                            keyword = " ".join(key_channel)

                            if keyword:
                                empty_channels = []
                                used_channels = []
                                for channel in guild.voice_channels:
                                    if channel.name.startswith(keyword):
                                        if len(channel.voice_states.keys()) == 0:
                                            empty_channels.append(channel)
                                        else:
                                            used_channels.append(channel)

                                if empty_channels:
                                    lowest_channel = None
                                    for channel in empty_channels:
                                        pair = [channel, int(channel.name.split(" ")[-1])]
                                        if lowest_channel is None or pair[1] < lowest_channel[1]:
                                            lowest_channel = pair
                                    empty_channels.remove(lowest_channel[0])
                                    for channel in empty_channels:
                                        if channel.permissions_for(channel.guild.me).manage_channels:
                                            logging.debug("info", "Delete: " + channel.name + " " + str(channel.id))
                                            await channel.delete()
                                else:
                                    highest_channel = None
                                    for channel in used_channels:
                                        pair = [channel, int(channel.name.split(" ")[-1])]
                                        if highest_channel is None or pair[1] > highest_channel[1]:
                                            highest_channel = pair
                                    channel = highest_channel[0]
                                    if channel.permissions_for(channel.guild.me).manage_channels:
                                        # Discord has issues with channel display
                                        new_channel = await guild.create_voice_channel(name=keyword + " " + str(highest_channel[1] + 1), category=channel.category, position=channel.position)
                                        logging.debug("info", "Create: " + new_channel.name + " " + str(new_channel.id))
                            else:
                                reset_channel = True
                        else:
                            reset_channel = True

                        if reset_channel:
                            await utils.execute_sql(f"UPDATE set_guilds SET managed_channel_voice_channel_channel = NULL WHERE guild_id ='{str(guild.id)}'", False)

                        await utils.execute_sql(f"UPDATE set_guilds SET managed_channel_ignore_running = 0 WHERE guild_id ='{str(guild.id)}'", False)

                except Exception:
                    await utils.execute_sql(f"UPDATE set_guilds SET managed_channel_ignore_running = 0 WHERE guild_id ='{str(guild.id)}'", False)
                    utils.on_error("managed_channel_command()")


async def setup(bot):
    await bot.add_cog(Events(bot))

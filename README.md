# emoji dude

- You can invite the bot [here](https://discord.com/api/oauth2/authorize?client_id=580065523098976256&permissions=2112&scope=bot).
- Uses the [discord.py](https://github.com/Rapptz/discord.py) library.
- If you have questions, feel free to ask.

### Overview

A tiny emoji writing and utility Discord Bot in Phyton. \
Every feature can be enabled/disabled. \
All Commands are enabled and all Events are disabled by default. \
Support & Bugs on: <https://discord.gg/Da9haye>

#### When running yourself

To run the bot yourself you need to set environment variables. As example: `BOT_TOKEN=JBDKfKSDU4e77eurj`
- With `BOT_ENVIR` you set the environment the bot runs in, this should be either `dev` or `production`.
- With `BOT_TOKEN` you set the Discord token for your bot.
- With `BOT_DATABASE_HOST` you set the hostname for your database.
- With `BOT_DATABASE_PORT` you set the port for your database.
- With `BOT_DATABASE_USER` you set the user which connects to your database.
- With `BOT_DATABASE_PASS` you set the password for the user to connect to your database.
- With `BOT_DATABASE_NAME` you set the database name you will be using.

#### Commands

##### `ed.ping`
* PONG! Pings and message round-trips.

##### `ed.backupchannel <from_channel_id> <to_channel_id>`
* Can be used to back up a channel to another one.
* This command is initially disabled, since it is currently only available to bot creators.

##### `ed.clean`
* Deletes all messages affecting this bot.

##### `ed.clear <amount>`
* Deletes a specific amount of messages.
* You can also reply to a message, then the bot deletes all messages up to the replied one.

##### `ed.emojis <emoji_combinations> <amount>`
* Sends many emojis, possible to be multiplied by 1-27 times.
* All emojis of Discord are supported, also custom ones and custom animated ones.
* If you don't have Nitro, you need to insert animated emojis as following `:name_of_animated_emoji:`.
* `<emoji_combinations>` can be just one, or multiple, but there must be no space between these emojis!
* You can reply to a previous message so the bot can reply to that message with these emojis.

##### `ed.help <category/command>`
* Shows a help menu with categorys and their commands.
* There are currently two categorys `commands` and `events`.
* When admins request the help page for a command, they can update command specific settings.
* This command can not be deactivated.

##### `ed.screenshare`
* Sends a screenshare link for your voice channel.
* This command is initially disabled, since Discord released an update this is no longer useful.

#### Events

##### AutoPollThreadCreation
* Automatically creates a thread, when the `Simple Poll#9879` bot creates new polls.

##### AutoReaction
* The bot reacts to specific parts in a message with emotes.
* Supported phrases are `cum`, `poop`,  `cool` and derivations.

##### ManagedAFK
* Auto moves full muted users after specific amount of time to the guild set AFK channel.
* The last used channel is saved, so when a user is no longer full mute, he will be automatically moved to his last voice channel.
* You need to set an AFK channel and give permissions to move members.

##### ManagedChannel
* Automatically creates voice channels when needed, and removes unused.

*© 2020 - 2023*
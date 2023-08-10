# emoji dude

- You can invite the bot [here](https://discord.com/api/oauth2/authorize?client_id=580065523098976256&permissions=2112&scope=bot).
- Uses the [discord.py](https://github.com/Rapptz/discord.py) library.
- If you have questions, feel free to ask.

### Overview

A tiny emoji writing and utility Discord Bot in Phyton. \
Every feature can be enabled/disabled. \
All Commands are enabled and all Events are disabled by default. \
Support & Bugs on: <https://discord.gg/Da9haye>

by **MuffinTime#4484**

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
* PONG!

##### `ed.backupchannel`
* Can be used to back up a channel to another one
* `ed.backupchannel <from_channelid> <to_channelid>`, <br> as example: `ed.backupchannel 699947018562568223 699937067123212329`
* (Currently, this command can be only used by bot creators)

##### `ed.clean`
* Cleans all messages affecting this bot

##### `ed.clear`
* Clears a specific amount of messages
* `ed.clear <amount>`, as example: `ed.clear 69`
* You can also reply to a message, then the bot deletes all messages up to the replied one.

##### `ed.emojis`
* Sends many emojis, multipliable by 1-27 times
* `ed.emojis <emoji combinations> <amount>`, as example: `ed.emojis 👾 21`
* All emojis of Discord are supported, also custom ones and custom animated ones.
* (If you don't have Nitro, you need to insert as following `:name_of_animated_emoji:`).
* `<emoji combinations>` can be just one, or multiple, but there must be no space between these emojis!
* You can reply to a previous message so the bot can reply to that message with these emojis.

##### `ed.help`
* `ed.help`, shows a help menu with categorys and their commands
* `ed.help <category>`, as example: `ed.help events`, there are currently two categorys `commands`/`events`
* `ed.help <command>`, as example: `ed.help AutoReaction`, when used by admins, they can update command specific settings
* This command can not be deactivated.

##### `ed.screenshare`
* Sends a screenshare link for your VoiceChannel
* This command is initially disabled (Because of a Discord update this is no longer useful)

#### Events

##### AutoPollThreadCreation
* Automatically creates a thread, when the Simple Poll#9879 bot creates new polls.

##### AutoReaction
* The bot reacts to specific parts in a message with emotes
* Supported phrases are lol/poop/cool

##### ManagedAFK
* Auto moves full muted users after specific amount of time to the guild set AFK channel
* The last used channel is saved, so when a user is no longer full mute, he will be automatically moved to his last VoiceChannel
* You need to set an AFK channel and give permissions to move members
* (Currently, it's not possible to set the timeout yourself, contact if needed)

##### ManagedChannel
* Automatically creates VoiceChannels when needed
* (Currently, it's not possible to activate this yourself, contact if needed)

*© 2020 - 2023*
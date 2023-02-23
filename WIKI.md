# emoji dude

Every feature can be enabled/disabled. All Commands are enabled and all Events are disabled by default.

## Commands

### `ed.ping`
* PONG!

### `ed.backupchannel`
* Can be used to back up a channel to another one
* `ed.backupchannel <from_channelid> <to_channelid>`, <br> as example: `ed.backupchannel 699947018562568223 699937067123212329`
* (Currently, this command can be only used by bot creators)

### `ed.clean`
* Cleans all messages affecting this bot

### `ed.clear`
* Clears a specific amount of messages
* `ed.clear <amount>`, as example: `ed.clear 69`

### `ed.emojis`
* Sends many emojis, you can choose between 1-27 emotes
* Supported emojis are lol/poop/cool
* `ed.emojis <emoji> <amount>`, as example: `ed.emojis poop 21`

### `ed.help`
* `ed.help`, shows a help menu with categorys and their commands
* `ed.help <category>`, as example: `ed.help events`, there are currently two categorys `commands`/`events`
* `ed.help <command>`, as example: `ed.help AutoReaction`, when used by admins, they can update command specific settings
* This command can not be deactivated.

### `ed.screenshare`
* Sends a screenshare link for your VoiceChannel
* This command is initially disabled (Because of a Discord update this is no longer useful)

## Events

### AutoPollThreadCreation
* Automatically creates a thread, when the Simple Poll#9879 Bot creates new polls.

### AutoReaction
* The bot reacts to specific parts in a message with emotes
* Supported phrases are lol/poop/cool

### ManagedAFK
* Auto moves full muted users after specific amount of time to the guild set AFK channel
* The last used channel is saved, so when a user is no longer full mute, he will be automatically moved to his last VoiceChannel
* You need to set an AFK channel and give permissions to move members
* (Currently, it's not possible to set the timeout yourself, contact if needed)

### ManagedChannel
* Automatically creates VoiceChannels when needed
* (Currently, it's not possible to activate this yourself, contact if needed)


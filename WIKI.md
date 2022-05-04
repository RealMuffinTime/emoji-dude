# emoji dude

## Supported emojis / Usage

* :lollipop: / lol
* :poop: / poop
* :cool: / cool


## Usage

### If you want reactions type
* ...lol..., ...poop..., etc.

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

### `ed.emojis `
* Sends many emojis, you can choose between 1-27 emotes
* `ed.emojis <emoji> <amount>`, as example: `ed.emojis poop 21`

### `ed.help`
* Shows a help menu, there are currently two category's `commands`/`events`
* `ed.help <category>`, as example: `ed.help events`

### `ed.screenshare`
* Sends a screenshare link for your VoiceChannel (Because of an Discord update this is no longer useful)

### `ed.settings`
* The settings, not yet implemented

## Events

### ManagedAFK
* Auto moves full muted users after specific amount of time to the guild set AFK channel
* The last used channel is saved, so when a user is no longer full mute, he will be automatically moved to his last VoiceChannel
* You need to set an AFK channel and give permissions to move members
* (Currently, it's not possible to set the timeout yourself, contact if needed)

### ManagedChannel
* Automatically creates VoiceChannels when needed
* (Currently, it's not possible to activate this yourself, contact if needed)

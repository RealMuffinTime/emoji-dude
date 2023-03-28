### Version 2.2.0
###### New stuff
 - `clear` command deletes messages up to a replied message on command usage
 - the bot shows now a reply to messages
###### Changes
 - massive update to the `emojis` command
 - add permission check for clean and clear command

### Version 2.1.0
###### New stuff
 - settings are now available, settings got integrated into the `help` command
 - the `help` command shows now also info to specific commands, there are also the settings located
 - features can be enabled/disabled
###### Changes
 - the `help` command got UI improvements
 - `screenshare` command got also UI improvements
 - `managed_afk` add permission check
 - internal changes to `managed_channel`

### Version 2.0.1
###### Changes
 - added a check for running managed_channels only once at a time

### Version 2.0.0
###### New stuff
 - user gets not afk managed when stream or video active
 - managed channel adds new channel under last current existing
 - managed channel checks for channels after start of bot
###### Changes
 - optimized help command: dynamic title, dynamic prefix
 - moved to discord.py v2
 - multiple reworks of afk management
 - (error) logging optimization

### Version 1.1.0
###### New stuff
 - added afk management
 - added database support
 - added initial help command
 - added placeholder for settings command
 - added initial backup command
###### Changes
 - voice channel manager fix
 - rework of cogs
 - overall improvements

### Version 1.0.2
###### New stuff
 - Added a limit in `ed.clear <limit>`, you can now specify the amount of messages to delete
 - Adds :billed_cap: on every message of user with id 443404465928667137
 - Added a voice channel manager for some specific channels and guilds
###### Changes
 - Typo fixing
 - Decreased the maximum emoji amount in 'ed.emojis' to 27

### Version 1.0.1
###### New stuff
 - Added clear command
###### Changes
 - Code improvements

### Version 1.0.0
###### New stuff
 - `ed.ping` a ping command
 - `ed.clean` deletes commands/message regarding to/by the bot 
 - `ed.screenshare` the old way to share your screen on servers, no longer needed
 - `ed.emojis <emoji> <amount>` sends emojis (lol, poop or cool) of an amount, between 1 - 150
 - Reacts on messages containing lol, cool, poop
 - Streaming status
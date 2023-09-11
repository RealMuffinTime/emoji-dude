### Version 2.4.0 - 2023-09-11
###### New stuff
- Some commands are now only accessible by admins only, or can have a specific moderators role for this
- Add dismiss to temporary messages
- Added some statistics to the base help page
###### Changes
- Added `cum`: 💦, `cap`: 🧢 and removed `lol`: 🍭 emojis in `AutoReaction`
- Update descriptions of commands and events
- Disable `backupchannel initially`
- Remove syntax in help page of `events` category 
- Removed `clean` command, it got integrated into the `clear` command
- Improved `clear` command logic and usability
###### Internal changes
- Add internal `help` enabled check
- Cleanup `main.py`
- sort command definitions alphabetically
- Ignore forbidden error in emoji creation

### Version 2.3.0 - 2023-09-01
###### New stuff
- Add settings view to help page, all command settings can now be updated by the user!!!
###### Changes
- Fix new channel not being directly under previous channel in `managedchannel`
###### Internal changes
- Move activity setup to client init 
- Add raw return for start_timestamp
- Store secrets in environment variables
- Create log folder automatically

### Version 2.2.1 - 2023-07-27
###### Changes
- Improvements to the logging of the online status
- Added join/leave messages for guild `669895353557975080`

### Version 2.2.0 - 2023-03-28
###### New stuff
- `clear` command deletes messages up to a replied message on command usage
- The bot shows now a reply to messages
###### Changes
- Massive update to the `emojis` command
- Add permission check for clean and clear command

### Version 2.1.0 - 2023-02-23
###### New stuff
- Settings are now available, settings got integrated into the `help` command
- The `help` command shows now also info to specific commands, there are also the settings located
- Features can be enabled/disabled
###### Changes
- The `help` command got UI improvements
- `screenshare` command got also UI improvements
- `managedafk` add permission check
- internal changes to `managedchannel`

### Version 2.0.1 - 2022-09-20
###### Changes
- Added a check for running managed_channels only once at a time

### Version 2.0.0 - 2022-09-14
###### New stuff
- User gets not afk managed when stream or video active
- Managed channel adds new channel under last current existing
- Managed channel checks for channels after start of bot
###### Changes
- Optimized help command: dynamic title, dynamic prefix
- Moved to discord.py v2
- Multiple reworks of afk management
- (error) logging optimization

### Version 1.1.0 - 2022-04-14
###### New stuff
- Added afk management
- Added database support
- Added initial help command
- Added placeholder for settings command
- Added initial backup command
###### Changes
- Voice channel manager fix
- Rework of cogs
- Overall improvements

### Version 1.0.2 - 2021-12-17
###### New stuff
- Added a limit in `ed.clear <limit>`, you can now specify the amount of messages to delete
- Adds :billed_cap: on every message of user with id 443404465928667137
- Added a voice channel manager for some specific channels and guilds
###### Changes
- Typo fixing
- Decreased the maximum emoji amount in 'ed.emojis' to 27

### Version 1.0.1 - 2021-09-15
###### New stuff
- Added clear command
###### Changes
- Code improvements

### Version 1.0.0 - 2020-12-21
###### New stuff
- `ed.ping` a ping command
- `ed.clean` deletes commands/message regarding to/by the bot 
- `ed.screenshare` the old way to share your screen on servers, no longer needed
- `ed.emojis <emoji> <amount>` sends emojis (lol, poop or cool) of an amount, between 1 - 150
- Reacts on messages containing lol, cool, poop
- Streaming status
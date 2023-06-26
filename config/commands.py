from pyrogram.types import BotCommand

class BotCommands:
    def __init__(self, CMD_SUFFIX):
        self.StartCommand = f'start{CMD_SUFFIX}'
        self.MirrorCommand = [f'mirror{CMD_SUFFIX}', f'm{CMD_SUFFIX}']
        self.YtdlCommand = [f'ytdl{CMD_SUFFIX}', f'y{CMD_SUFFIX}']
        self.LeechCommand = [f'leech{CMD_SUFFIX}', f'l{CMD_SUFFIX}']
        self.YtdlLeechCommand = [f'ytdlleech{CMD_SUFFIX}', f'yl{CMD_SUFFIX}']
        self.CancelMirror = f'cancel{CMD_SUFFIX}'
        self.CancelAllCommand = f'cancelall{CMD_SUFFIX}'
        self.StatusCommand = f'status{CMD_SUFFIX}'
        self.UsersCommand = f'users{CMD_SUFFIX}'
        self.AuthorizeCommand = f'authorize{CMD_SUFFIX}'
        self.UnAuthorizeCommand = f'unauthorize{CMD_SUFFIX}'
        self.AddSudoCommand = f'addsudo{CMD_SUFFIX}'
        self.RmSudoCommand = f'rmsudo{CMD_SUFFIX}'
        self.RestartCommand = f'restart{CMD_SUFFIX}'
        self.StatsCommand = f'stats{CMD_SUFFIX}'
        self.HelpCommand = f'help{CMD_SUFFIX}'
        self.LogCommand = f'log{CMD_SUFFIX}'
        self.BotSetCommand = f'bsetting{CMD_SUFFIX}'
        self.UserSetCommand = f'usetting{CMD_SUFFIX}'
        self.BtSelectCommand = f'btsel{CMD_SUFFIX}'



def getCommandString(BotCommands):
    return f'''
NOTE: Try each command without any argument to see more detalis.
/{BotCommands.MirrorCommand[0]} or /{BotCommands.MirrorCommand[1]}: Start mirroring to Google Drive.
/{BotCommands.YtdlCommand[0]} or /{BotCommands.YtdlCommand[1]}: Mirror yt-dlp supported link.
/{BotCommands.LeechCommand[0]} or /{BotCommands.LeechCommand[1]}: Start leeching to Telegram.
/{BotCommands.YtdlLeechCommand[0]} or /{BotCommands.YtdlLeechCommand[1]}: Leech yt-dlp supported link.
/{BotCommands.UserSetCommand} [query]: Users settings.
/{BotCommands.BotSetCommand} [query]: Bot settings.
/{BotCommands.BtSelectCommand}: Select files from torrents by gid or reply.
/{BotCommands.CancelMirror}: Cancel task by gid or reply.
/{BotCommands.CancelAllCommand} [query]: Cancel all [status] tasks.
/{BotCommands.StatusCommand}: Shows a status of all the downloads.
/{BotCommands.StatsCommand}: Show stats of the machine where the bot is hosted in.
/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Only Owner & Sudo).
/{BotCommands.UnAuthorizeCommand}: Unauthorize a chat or a user to use the bot (Only Owner & Sudo).
/{BotCommands.UsersCommand}: show users settings (Only Owner & Sudo).
/{BotCommands.AddSudoCommand}: Add sudo user (Only Owner).
/{BotCommands.RmSudoCommand}: Remove sudo users (Only Owner).
/{BotCommands.RestartCommand}: Restart and update the bot (Only Owner & Sudo).
/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports (Only Owner & Sudo).
'''


async def set_commands(client, SET_COMMANDS, BotCommands):
    if SET_COMMANDS:
        await client.set_bot_commands([
            BotCommand(
                f'{BotCommands.MirrorCommand[0]}', f'or /{BotCommands.MirrorCommand[1]} Mirror'),
            BotCommand(
                f'{BotCommands.LeechCommand[0]}', f'or /{BotCommands.LeechCommand[1]} Leech'),
            BotCommand(
                f'{BotCommands.YtdlCommand[0]}', f'or /{BotCommands.YtdlCommand[1]} Mirror yt-dlp supported link'),
            BotCommand(
                f'{BotCommands.YtdlLeechCommand[0]}', f'or /{BotCommands.YtdlLeechCommand[1]} Leech through yt-dlp supported link'),
            BotCommand(
                f'{BotCommands.StatusCommand[0]}', f'or /{BotCommands.StatusCommand[1]} Get mirror status message'),
            BotCommand(f'{BotCommands.StatsCommand}', 'Check bot stats'),
            BotCommand(f'{BotCommands.BtSelectCommand}',
                       'Select files to download only torrents'),
            BotCommand(f'{BotCommands.CancelMirror}', 'Cancel a Task'),
            BotCommand(
                f'{BotCommands.CancelAllCommand[0]}', f'Cancel all tasks which added by you or {BotCommands.CancelAllCommand[1]} to in bots.'),
            BotCommand(f'{BotCommands.UserSetCommand}', 'Users settings'),
            BotCommand(f'{BotCommands.BotSetCommand}', 'Bot settings'),
            BotCommand(f'{BotCommands.LogCommand}', 'Bot Logs'),
            BotCommand(f'{BotCommands.RestartCommand}', 'Restart Bot'),
            BotCommand(f'{BotCommands.AddSudoCommand}', 'Add Sudo User'),
            BotCommand(f'{BotCommands.RmSudoCommand}', 'Remove Sudo User'),
            BotCommand(f'{BotCommands.AuthorizeCommand}', 'Authorize Chat or User'),
            BotCommand(f'{BotCommands.UnAuthorizeCommand}', 'Unauthorize Chat or User'),
            BotCommand(f'{BotCommands.HelpCommand}', 'Get detailed help'),
        ])
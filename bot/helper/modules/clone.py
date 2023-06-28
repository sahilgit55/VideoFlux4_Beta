from asyncio import create_subprocess_exec, gather
from asyncio.subprocess import PIPE
from configparser import ConfigParser
from aiofiles import open as aiopen
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from bot import config_dict, LOGGER, bot, BotCommands
from bot.helper.pyrogram.message_utils import sendMessage
from bot.helper.utils.other_utils import cmd_exec


async def get_remote_options(config_path, remote):
        config = ConfigParser()
        async with aiopen(config_path, 'r') as f:
            contents = await f.read()
            config.read_string(contents)
        options = config.options(remote)
        return {opt: config.get(remote, opt) for opt in options}

async def clone(_, message):
    input_list = message.text.split(' ')
    try:
        name  = input_list[2]
    except:
        name = ""
    rclone_path = config_dict['RCLONE_PATH']
    g_id = "{" f"{input_list[1]}" "}"
    cmd = [
            "gclone",
            "copy",
            "--config=rclone.conf",
            f"{rclone_path.split(':')[0]}:{g_id}",
            f"{rclone_path}/{name}",
            "-v",
            "--drive-server-side-across-configs",
            "--transfers=16",
            "--checkers=20",
        ]
    LOGGER.info(cmd)
    stdout, stderr, returncode = await cmd_exec(cmd)
    LOGGER.info(str(stdout))
    LOGGER.info(str(stderr))
    LOGGER.info(str(returncode))
    await sendMessage(message, "OK")
    return




bot.add_handler(MessageHandler(
    clone, filters=command(BotCommands.CloneCommand)))
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from re import search as re_search
from urllib.parse import parse_qs, urlparse
from asyncio import create_subprocess_exec, create_subprocess_shell, sleep
from asyncio.subprocess import PIPE

from bot import config_dict, LOGGER, bot, BotCommands
from bot.helper.pyrogram.message_utils import sendMessage, editMessage
from bot.helper.utils.other_utils import sync_to_async, is_share_link, is_gdrive_link
from bot.helper.other.direct_link_generator import direct_link_generator
from bot.helper.other.exceptions import DirectDownloadLinkException


def getIdFromUrl(link):
        if "folders" in link or "file" in link:
            regex = r"https:\/\/drive\.google\.com\/(?:drive(.*?)\/folders\/|file(.*?)?\/d\/)([-\w]+)"
            res = re_search(regex, link)
            if res is None:
                raise IndexError("G-Drive ID not found.")
            return res.group(3)
        parsed = urlparse(link)
        return parse_qs(parsed.query)['id'][0]


async def cmd_exec_status(cmd, message, shell=False):
    if shell:
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    else:
        proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stderr = ''
    while True:
                try:
                    async for line in proc.stderr:
                            line = line.decode('utf-8').strip()
                            print(line)
                            stderr += line
                            await editMessage(message, str(line))
                            await sleep(7)
                except ValueError:
                        continue
                else:
                        break
    await proc.wait()
    if proc.returncode!=0:
            await editMessage(message, f"Task Failed!\n\n{stderr}")
    return proc.returncode

async def clone(_, message):
    input_list = message.text.split(' ')
    try:
        link = input_list[1]
    except:
        await sendMessage(message, 'Invalid Link')
        return
    try:
        name  = input_list[2]
    except:
        name = ""
    if is_share_link(link):
        try:
            link = await sync_to_async(direct_link_generator, link)
            LOGGER.info(f"Generated link: {link}")
        except DirectDownloadLinkException as e:
            LOGGER.error(str(e))
            if str(e).startswith('ERROR:'):
                await sendMessage(message, str(e))
                return
    if is_gdrive_link(link):
        try:
            file_id = getIdFromUrl(link)
        except (KeyError, IndexError):
            await sendMessage(message, 'Google Drive ID could not be found in the provided link')
            return
        LOGGER.info(f"File ID: {file_id}")
        g_id = "{" f"{file_id}" "}"
        cmd = [
                "./gclone",
                "copy",
                "--config=rclone.conf",
                f"{config_dict['RCLONE_GD_NAME']}:{g_id}",
                f"{config_dict['RCLONE_PATH']}/{name}",
                "-v",
                "--drive-server-side-across-configs",
                "--transfers=16",
                "--checkers=20",
            ]
        LOGGER.info(cmd)
        msg = await sendMessage(message, "Cloning, Please Wait...")
        proc_result = await cmd_exec_status(cmd, msg)
        if proc_result==0:
                await editMessage(msg, "Successfully Copied")
    return




bot.add_handler(MessageHandler(
    clone, filters=command(BotCommands.CloneCommand)))
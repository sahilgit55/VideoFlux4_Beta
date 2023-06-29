from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from re import search as re_search, findall as refindall
from urllib.parse import parse_qs, urlparse
from asyncio import create_subprocess_exec, create_subprocess_shell, sleep
from asyncio.subprocess import PIPE

from bot import config_dict, LOGGER, bot, BotCommands, bot_loop
from bot.helper.pyrogram.message_utils import sendMessage, editMessage
from bot.helper.utils.other_utils import sync_to_async, is_share_link, is_gdrive_link, get_progress_bar_from_percentage, new_task
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


class CloneHelper:
    
    def __init__(self, cmd):
        self.cmd = cmd
        self.currentmsg = ''
        self.log = ''
        self.returncode = None
        self.complete = False
    
    def set_msg(self, msg):
        self.log += msg + "\n"
        datam = refindall("Transferred:.*ETA.*", msg)
        if datam is not None:
            if len(datam) > 0:
                progress = datam[0].replace("Transferred:", "").strip().split(",")
                percentage= progress[1].strip("% ")
                dwdata = progress[0].strip().split('/')
                eta = progress[3].strip().replace('ETA', '').strip()
                text =f'Copying: {get_progress_bar_from_percentage(percentage)} {percentage}%\n'\
                        f'Copied: {dwdata[0].strip()} of {dwdata[1].strip()}\n'\
                        f'Speed: {progress[2]} | ETA: {eta}'
                self.currentmsg = text
        return
    
    def set_returncode(self, returncode):
        self.returncode = returncode
        return
    
    def completed(self):
        self.complete = True
        return

@new_task
async def cmd_exec_status(cloneob, shell=False):
    LOGGER.info(cloneob.cmd)
    if shell:
        proc = await create_subprocess_shell(cloneob.cmd, stdout=PIPE, stderr=PIPE)
    else:
        proc = await create_subprocess_exec(*cloneob.cmd, stdout=PIPE, stderr=PIPE)
    while True:
        try:
            async for line in proc.stderr:
                    line = line.decode('utf-8').strip()
                    if len(str(line)):
                        print(line)
                        try:
                            cloneob.set_msg(line)
                        except Exception as e:
                            LOGGER.info(str(e))
        except ValueError:
                continue
        else:
                break
    await proc.wait()
    cloneob.set_returncode(proc.returncode)
    cloneob.completed()
    return


async def update_status(cloneob, msg):
    pre_msg = ''
    while True:
            if cloneob.currentmsg and pre_msg!=cloneob.currentmsg:
                    await editMessage(msg, cloneob.currentmsg)
                    pre_msg = cloneob.currentmsg
            if cloneob.complete:
                LOGGER.info("Clone Completed")
                break
            await sleep(int(config_dict['STATUS_UPDATE_INTERVAL']))
    if cloneob.returncode==0:
            await editMessage(msg, f"Copying Completed")
    else:
            await editMessage(msg, f"Copying Failed\nReturn Code: {cloneob.returncode}\n\n{cloneob.log}")
    return


@new_task
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
        msg = await sendMessage(message, "Cloning, Please Wait...")
        cloneob = CloneHelper(cmd)
        bot_loop.create_task(update_status(cloneob, msg))
        await cmd_exec_status(cloneob)
    return




bot.add_handler(MessageHandler(
    clone, filters=command(BotCommands.CloneCommand)))
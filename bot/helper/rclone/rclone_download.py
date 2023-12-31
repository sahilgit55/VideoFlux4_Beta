#!/usr/bin/env python3
from asyncio import gather
from json import loads
from random import SystemRandom
from string import ascii_letters, digits
from re import escape

from bot import download_dict, download_dict_lock, queue_dict_lock, non_queued_dl, LOGGER
from bot.helper.utils.other_utils import cmd_exec
from bot.helper.pyrogram.message_utils import sendMessage, sendStatusMessage
from bot.helper.other.task_manager import is_queued
from bot.helper.status.rclone_status import RcloneStatus
from bot.helper.status.queue_status import QueueStatus
from bot.helper.rclone.rclone_transfer import RcloneTransferHelper


async def getRespData(cmd1, cmd2, remote, rc_path, cmd_type=1):
    LOGGER.info(str(cmd1))
    LOGGER.info(str(cmd2))
    res1, res2 = await gather(cmd_exec(cmd1), cmd_exec(cmd2))
    if res1[2] != res2[2] != 0:
        if res1[2] != -9:
            err = res1[1] or res2[1]
            msg = f'Error: While getting rclone stat/size. Path: {remote}:{rc_path}. Stderr: {err[:4000]}'
        return None, msg
    try:
            if cmd_type==1:
                    rstat = loads(res1[0])
            else:
                    rstat = loads(res1[0])[0]
            rsize = loads(res2[0])
            return rstat, rsize
    except Exception as e:
            LOGGER.error(str(e))
            LOGGER.error(str(res1))
            LOGGER.error(str(res2))
            return None, None



async def add_rclone_download(rc_path, config_path, path, name, listener):
    _rc_path = rc_path
    _remote = None
    _name = None
    
    remote, rc_path = rc_path.split(':', 1)
    rc_path = rc_path.strip('/')
    
    cmd1 = ['rclone', 'lsjson', '--fast-list', '--stat', '--no-mimetype',
        '--no-modtime', '--config', config_path, f'{remote}:{rc_path}']
    cmd2 = ['rclone', 'size', '--fast-list', '--json',
            '--config', config_path, f'{remote}:{rc_path}']
    
    rstat, rsize = await getRespData(cmd1, cmd2, remote, rc_path, cmd_type=1)
    if not rstat:
        if rsize:
                await sendMessage(listener.message, rsize)
        
        rc_list = _rc_path.strip('/').split('/')
        _remote = ''.join(f'{j}/' for j in rc_list[:-1])
        _name = rc_list[-1]
        cmd1 = ["rclone",
                        "lsjson",
                        f"--config={config_path}",
                        f'{_remote}',
                        "--files-only",
                        "-f",
                        f"+ {escape(_name)}",
                        "-f",
                        "- *"]
        cmd2 = ["rclone",
                "size",
                '--json',
                f"--config={config_path}",
                f'{_remote}',
                "-f",
                f"+ {escape(_name)}",
                "-f",
                "- *"]
        rstat, rsize = await getRespData(cmd1, cmd2, remote, rc_path, cmd_type=2)
        if not rstat:
            await sendMessage(listener.message, 'Task failed! Check log')
            return

    if rstat['IsDir']:
        if not name:
            name = rc_path.rsplit('/', 1)[-1] if rc_path else remote
        path += name
    else:
        name = rc_path.rsplit('/', 1)[-1]
    size = rsize['bytes']
    gid = ''.join(SystemRandom().choices(ascii_letters + digits, k=12))

    added_to_queue, event = await is_queued(listener.uid)
    if added_to_queue:
        LOGGER.info(f"Added to Queue/Download: {name}")
        async with download_dict_lock:
            download_dict[listener.uid] = QueueStatus(
                name, size, gid, listener, 'dl')
        await listener.onDownloadStart()
        await sendStatusMessage(listener.message)
        await event.wait()
        async with download_dict_lock:
            if listener.uid not in download_dict:
                return
        from_queue = True
    else:
        from_queue = False

    RCTransfer = RcloneTransferHelper(listener, name)
    async with download_dict_lock:
        download_dict[listener.uid] = RcloneStatus(
            RCTransfer, listener.message, gid, 'dl')
    async with queue_dict_lock:
        non_queued_dl.add(listener.uid)

    if from_queue:
        LOGGER.info(f'Start Queued Download with rclone: {rc_path}')
    else:
        await listener.onDownloadStart()
        await sendStatusMessage(listener.message)
        LOGGER.info(f"Download with rclone: {rc_path}")

    await RCTransfer.download(remote, rc_path, config_path, path, _remote=_remote, _name= _name)

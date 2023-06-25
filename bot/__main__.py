#!/usr/bin/env python3
from signal import signal, SIGINT
from aiofiles.os import path as aiopath, remove as aioremove
from asyncio import gather

from bot import bot, LOGGER, bot_name
from bot.helper.utils.file_utils import start_cleanup, exit_clean_up
from bot.helper.utils.other_utils import sync_to_async
from bot.helper.modules import basic_cmds, auth

from bot.helper.aria.aria2_listener import start_aria2_listener
from bot.helper.modules import mirror_leech, cancel_task, status, user_settings, bot_settings, yt_dl, t_select


async def restart_notification():
    if await aiopath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text='Restarted Successfully!')
        except:
            pass
        await aioremove(".restartmsg")


async def main():
    await gather(start_cleanup(), restart_notification())
    await sync_to_async(start_aria2_listener, wait=False)
    LOGGER.info(f'✅@{bot_name} Started Successfully!✅')
    LOGGER.info(f"⚡Bot By Sahil Nolia⚡")
    signal(SIGINT, exit_clean_up)


bot.loop.run_until_complete(main())
bot.loop.run_forever()
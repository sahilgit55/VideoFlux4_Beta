#!/usr/bin/env python3
from aiofiles.os import path as aiopath
from aiofiles import open as aiopen
from os import execl as osexecl
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from time import time
from sys import executable
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from asyncio import gather, create_subprocess_exec
from heroku3 import from_key
from uuid import uuid4

from bot import bot, botStartTime, log_file, BotCommands, commands_string, config_dict, LOGGER, user_data
from bot.helper.pyrogram.message_utils import sendFile, sendMessage
from bot.helper.pyrogram.button_build import ButtonMaker
from bot.helper.utils.other_utils import sync_to_async, cmd_exec, get_readable_file_size, get_readable_time, get_logs_msg
from bot.helper.utils.file_utils import clean_all
from bot.helper.pyrogram.filters import CustomFilters


async def stats(_, message):
    if await aiopath.exists('.git'):
        last_commit = await cmd_exec("git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'", True)
        last_commit = last_commit[0]
    else:
        last_commit = 'No UPSTREAM_REPO'
    total, used, free, disk = disk_usage('/')
    swap = swap_memory()
    memory = virtual_memory()
    stats = f'<b>Commit Date:</b> {last_commit}\n\n'\
            f'<b>Bot Uptime:</b> {get_readable_time(time() - botStartTime)}\n'\
            f'<b>OS Uptime:</b> {get_readable_time(time() - boot_time())}\n\n'\
            f'<b>Total Disk Space:</b> {get_readable_file_size(total)}\n'\
            f'<b>Used:</b> {get_readable_file_size(used)} | <b>Free:</b> {get_readable_file_size(free)}\n\n'\
            f'<b>Upload:</b> {get_readable_file_size(net_io_counters().bytes_sent)}\n'\
            f'<b>Download:</b> {get_readable_file_size(net_io_counters().bytes_recv)}\n\n'\
            f'<b>CPU:</b> {cpu_percent(interval=0.5)}%\n'\
            f'<b>RAM:</b> {memory.percent}%\n'\
            f'<b>DISK:</b> {disk}%\n\n'\
            f'<b>Physical Cores:</b> {cpu_count(logical=False)}\n'\
            f'<b>Total Cores:</b> {cpu_count(logical=True)}\n\n'\
            f'<b>SWAP:</b> {get_readable_file_size(swap.total)} | <b>Used:</b> {swap.percent}%\n'\
            f'<b>Memory Total:</b> {get_readable_file_size(memory.total)}\n'\
            f'<b>Memory Free:</b> {get_readable_file_size(memory.available)}\n'\
            f'<b>Memory Used:</b> {get_readable_file_size(memory.used)}\n'
    await sendMessage(message, stats)


async def start(_, message):
    if len(message.command) > 1:
        userid = message.from_user.id
        input_token = message.command[1]
        if userid not in user_data:
            return await sendMessage(message, 'Who are you?')
        data = user_data[userid]
        if 'token' not in data or data['token'] != input_token:
            return await sendMessage(message, 'This token is already expired')
        data['token'] = str(uuid4())
        data['time'] = time()
        user_data[userid].update(data)
        return await sendMessage(message, 'Token refreshed successfully!')
    else:
        text = f"Hi {message.from_user.mention(style='md')}, I Am Alive."
        buttons = ButtonMaker()
        buttons.ubutton("⭐ Bot By 𝚂𝚊𝚑𝚒𝚕 ⭐", "https://t.me/nik66")
        buttons.ubutton("❤ Join Channel ❤", "https://t.me/nik66x")
        await sendMessage(message, text, buttons=buttons.build_menu(1))
        return


async def restart(_, message):
    if len(config_dict['HEROKU_APP_NAME']) and len(config_dict['HEROKU_API_KEY']):
            restart_message = await sendMessage(message, "Restarting Heroku Dyno")
            async with aiopen(".restartmsg", "w") as f:
                    await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
            heroku_conn = from_key(config_dict['HEROKU_API_KEY'])
            for dyno in heroku_conn.app(config_dict['HEROKU_APP_NAME']).dynos():
                LOGGER.info(str(dyno))
                LOGGER.info(str(dyno.command))
                dyno.restart()
    else:
        restart_message = await sendMessage(message, "Restarting...")
        await sync_to_async(clean_all)
        proc1 = await create_subprocess_exec('pkill', '-9', '-f', 'gunicorn|aria2c|rclone|ffmpeg')
        proc2 = await create_subprocess_exec('python3', 'update.py')
        await gather(proc1.wait(), proc2.wait())
        async with aiopen(".restartmsg", "w") as f:
            await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
        osexecl(executable, executable, "-m", "bot")


async def log(_, message):
    await sendMessage(message, get_logs_msg(log_file))
    await sendFile(message, log_file)
    return


async def bot_help(_, message):
    await sendMessage(message, commands_string)



bot.add_handler(MessageHandler(
    start, filters=command(BotCommands.StartCommand)))
bot.add_handler(MessageHandler(
    log, filters=command(BotCommands.LogCommand) & CustomFilters.sudo))
bot.add_handler(MessageHandler(
    restart, filters=command(BotCommands.RestartCommand) & CustomFilters.sudo))
bot.add_handler(MessageHandler(
    bot_help, filters=command(BotCommands.HelpCommand) & CustomFilters.authorized))
bot.add_handler(MessageHandler(
    stats, filters=command(BotCommands.StatsCommand) & CustomFilters.authorized))

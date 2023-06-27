from pyrogram import Client as tgClient, enums
from asyncio import Lock
from faulthandler import enable as faulthandler_enable
from socket import setdefaulttimeout
from uvloop import install

faulthandler_enable()
install()
setdefaulttimeout(600)

from config import config_dict, user_data, LOGGER, log_file, DOWNLOAD_DIR, OWNER_ID, BotCommands, commands_string, DATABASE_URL, DB_NAME, bot_id, botStartTime, GLOBAL_EXTENSION_FILTER,BASE_URL, getMaxLeechSize, set_commands, SET_COMMANDS
from config.aria_config import aria2, aria2_options, aria2c_global

Interval = []

download_dict_lock = Lock()
status_reply_dict_lock = Lock()
queue_dict_lock = Lock()
non_queued_dl = set()
non_queued_up = set()

download_dict = {}
status_reply_dict = {}
queued_dl = {}
queued_up = {}


if len(config_dict['USER_SESSION_STRING']):
    LOGGER.info("Creating client from USER_SESSION_STRING")
    user = tgClient('user', config_dict['TELEGRAM_API'], config_dict['TELEGRAM_HASH'], session_string=config_dict['USER_SESSION_STRING'],
                    parse_mode=enums.ParseMode.HTML,
                    max_concurrent_transmissions=1000
                    ).start()
    IS_PREMIUM_USER = user.me.is_premium
else:
    IS_PREMIUM_USER = False
    user = ''


bot = tgClient('bot', config_dict['TELEGRAM_API'], config_dict['TELEGRAM_HASH'],
                            bot_token=config_dict['BOT_TOKEN'],
                            workers=1000,
                            parse_mode=enums.ParseMode.HTML,
                            max_concurrent_transmissions=1000
                            ).start()

bot_loop = bot.loop
bot_name = bot.me.username
MAX_SPLIT_SIZE = getMaxLeechSize(IS_PREMIUM_USER)
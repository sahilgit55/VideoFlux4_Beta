from config.logger import LOGGER, log_file
from config.commands import BotCommands, getCommandString
from os import environ, getcwd
from os.path import exists
from dotenv import load_dotenv, dotenv_values
from requests import get
from pymongo import MongoClient
from time import time

botStartTime = time()
config_dict = {}
user_data = {}
aria2_options = {}
GLOBAL_EXTENSION_FILTER = ['aria2']


def dwFromUrl(url, filename):
        r = get(url, allow_redirects=True, stream=True, timeout=60)
        with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024 * 10):
                        if chunk:
                                fd.write(chunk)
        return


def loadConfig(config_file):
        current_config = dict(dotenv_values(config_file))
        if len(current_config['DATABASE_URL']):
                DB_NAME = current_config['DB_NAME']
                LOGGER.info(f"Connecting With Database: {DB_NAME}")
                bot_id = current_config['BOT_TOKEN'].split(':', 1)[0]
                conn = MongoClient(current_config['DATABASE_URL'])
                db = conn[DB_NAME]
                if config_dict := db.settings.config.find_one({'_id': bot_id}):
                        del config_dict['_id']
                        for key, value in config_dict.items():
                                environ[key] = str(value)
                        LOGGER.info("Config Loaded From Database")
                else:
                        load_dotenv(config_file, override=True)
                        LOGGER.info("Config Loaded From Local")
                if pf_dict := db.settings.files.find_one({'_id': bot_id}):
                        del pf_dict['_id']
                        for key, value in pf_dict.items():
                                if value:
                                        file_ = key.replace('__', '.')
                                        with open(file_, 'wb+') as f:
                                                f.write(value)
                if a2c_options := db.settings.aria2c.find_one({'_id': bot_id}):
                        del a2c_options['_id']
                        global aria2_options
                        aria2_options = a2c_options
                conn.close()
        else:
                load_dotenv(config_file, override=True)
                LOGGER.info("Config Loaded From Local")
        return

if exists('config.env'):
        loadConfig('config.env')
else:
        CONFIG_FILE_URL = environ.get("CONFIG_FILE_URL", '')
        if len(CONFIG_FILE_URL) and str(CONFIG_FILE_URL).startswith("http"):
                LOGGER.info(f"Downloading Config File From URL {CONFIG_FILE_URL}")
                dwFromUrl(CONFIG_FILE_URL, "config.env")
                loadConfig('config.env')
        else:
                LOGGER.error('config.env File Not Found')
                exit(1)


RCLONE_CONFIG_URL = environ.get("RCLONE_CONFIG_URL", '')
if len(RCLONE_CONFIG_URL) and str(RCLONE_CONFIG_URL).startswith("http"):
        LOGGER.info(f"Downloading Rclone Config File From URL {RCLONE_CONFIG_URL}")
        dwFromUrl(RCLONE_CONFIG_URL, "rclone.conf")
else:
        LOGGER.info(f"Invalid Rclone Config URL {RCLONE_CONFIG_URL}")


def getConfig(variable, value):
        try:
                if variable=='DATABASE_URL':
                        DATABASE_URL = environ.get("DATABASE_URL","")
                        return False if len(DATABASE_URL) == 0 else DATABASE_URL
                elif variable=='QUEUE_ALL':
                        QUEUE_ALL = environ.get("QUEUE_ALL","")
                        return '' if len(QUEUE_ALL) == 0 else int(QUEUE_ALL)
                elif variable=='QUEUE_UPLOAD':
                        QUEUE_UPLOAD = environ.get("QUEUE_UPLOAD","")
                        return '' if len(QUEUE_UPLOAD) == 0 else int(QUEUE_UPLOAD)
                elif variable=='QUEUE_DOWNLOAD':
                        QUEUE_DOWNLOAD = environ.get("QUEUE_DOWNLOAD","")
                        return '' if len(QUEUE_DOWNLOAD) == 0 else int(QUEUE_DOWNLOAD)
                elif variable=='DUMP_CHAT_ID':
                        DUMP_CHAT_ID = environ.get("DUMP_CHAT_ID","")
                        return '' if len(DUMP_CHAT_ID) == 0 else int(DUMP_CHAT_ID)
                elif variable=='AUTO_DELETE_MESSAGE_DURATION':
                        AUTO_DELETE_MESSAGE_DURATION = environ.get("AUTO_DELETE_MESSAGE_DURATION","")
                        return 30 if len(AUTO_DELETE_MESSAGE_DURATION) == 0 else int(AUTO_DELETE_MESSAGE_DURATION)
                elif variable=='TORRENT_TIMEOUT':
                        TORRENT_TIMEOUT = environ.get("TORRENT_TIMEOUT","")
                        return '' if len(TORRENT_TIMEOUT) == 0 else int(TORRENT_TIMEOUT)
        except Exception as e:
                LOGGER.error(f'Error Getting Variable {variable}:  {str(e)}')
                return value


class Config:
        TELEGRAM_API = int(environ.get("TELEGRAM_API",""))
        TELEGRAM_HASH = environ.get("TELEGRAM_HASH","")
        BOT_TOKEN = environ.get("BOT_TOKEN","")
        USER_SESSION_STRING = environ.get("USER_SESSION_STRING", False)
        
        
        OWNER_ID = int(environ.get("OWNER_ID",""))
        AUTHORIZED_CHATS = environ.get('AUTHORIZED_CHATS', '')
        SUDO_USERS = environ.get('SUDO_USERS', '')
        
        
        DATABASE_URL = getConfig('DATABASE_URL', False)
        DB_NAME = environ.get("DB_NAME","nik66bots")
        
        
        UPSTREAM_REPO = environ.get("UPSTREAM_REPO","")
        UPSTREAM_BRANCH = environ.get("UPSTREAM_BRANCH","master")
        
        
        DEFAULT_UPLOAD = environ.get("DEFAULT_UPLOAD", 'rc')
        RCLONE_PATH = environ.get("RCLONE_PATH", '')
        RCLONE_FLAGS = environ.get("RCLONE_FLAGS", '')
        USE_SERVICE_ACCOUNTS = environ.get("USE_SERVICE_ACCOUNTS", '').lower() == 'true'
        IS_TEAM_DRIVE = environ.get('IS_TEAM_DRIVE', '').lower() == 'true'
        INDEX_URL = environ.get('INDEX_URL', '').rstrip("/")
        
        
        QUEUE_ALL = getConfig('QUEUE_ALL', '')
        QUEUE_DOWNLOAD = getConfig('QUEUE_DOWNLOAD', '')
        QUEUE_UPLOAD = getConfig('QUEUE_UPLOAD', '')
        
        
        AS_DOCUMENT = environ.get("AS_DOCUMENT", '').lower() == 'true'
        MEDIA_GROUP = environ.get("MEDIA_GROUP", '').lower() == 'true'
        LEECH_FILENAME_PREFIX = environ.get("LEECH_FILENAME_PREFIX", '')
        LEECH_SPLIT_SIZE = environ.get("LEECH_SPLIT_SIZE", '')
        EQUAL_SPLITS = environ.get("EQUAL_SPLITS", '').lower() == 'true'
        DUMP_CHAT_ID = getConfig('DUMP_CHAT_ID', '')
        
        
        BASE_URL = environ.get("BASE_URL", '').rstrip("/")
        WEB_PINCODE = environ.get("WEB_PINCODE", '').lower() == 'true'
        
        
        STATUS_UPDATE_INTERVAL = int(environ.get("STATUS_UPDATE_INTERVAL", 10))
        STATUS_LIMIT = int(environ.get("STATUS_LIMIT", 10))
        
        
        CMD_SUFFIX = environ.get("CMD_SUFFIX","")
        AUTO_DELETE_MESSAGE_DURATION = getConfig('AUTO_DELETE_MESSAGE_DURATION', 30)
        
        
        TORRENT_TIMEOUT = getConfig('TORRENT_TIMEOUT', '')
        UPTOBOX_TOKEN = environ.get("UPTOBOX_TOKEN", '')
        EXTENSION_FILTER = environ.get('EXTENSION_FILTER', '')
        YT_DLP_OPTIONS = environ.get('YT_DLP_OPTIONS', '')



for var in vars(Config):
    if not var.startswith('__'):
        config_dict[var] = vars(Config)[var]

for id_ in config_dict['AUTHORIZED_CHATS'].split():
        user_data[int(id_.strip())] = {'is_auth': True}

for id_ in config_dict['SUDO_USERS'].split():
        user_data[int(id_.strip())] = {'is_sudo': True}


DOWNLOAD_DIR = f"{getcwd()}/downloads/"
config_dict['DOWNLOAD_DIR'] = DOWNLOAD_DIR
OWNER_ID = config_dict['OWNER_ID']
DATABASE_URL = config_dict['DATABASE_URL']
DB_NAME = config_dict['DB_NAME']
bot_id = config_dict['BOT_TOKEN'].split(':', 1)[0]
BotCommands = BotCommands(config_dict['CMD_SUFFIX'])
commands_string = getCommandString(BotCommands)

if len(config_dict['EXTENSION_FILTER']) > 0:
    fx = config_dict['EXTENSION_FILTER'].split()
    for x in fx:
        if x.strip().startswith('.'):
            x = x.lstrip('.')
        GLOBAL_EXTENSION_FILTER.append(x.strip().lower())


def getMaxLeechSize(IS_PREMIUM_USER):
        MAX_SPLIT_SIZE = 4194304000 if IS_PREMIUM_USER else 2097152000
        LEECH_SPLIT_SIZE = config_dict['LEECH_SPLIT_SIZE']
        if len(LEECH_SPLIT_SIZE) == 0 or int(LEECH_SPLIT_SIZE) > MAX_SPLIT_SIZE:
                config_dict['LEECH_SPLIT_SIZE'] = MAX_SPLIT_SIZE
        else:
                config_dict['LEECH_SPLIT_SIZE'] = int(LEECH_SPLIT_SIZE)
        return MAX_SPLIT_SIZE

if DOWNLOAD_DIR.startswith('/content/'):
        config_dict['BASE_URL_PORT'] = False
else:
        config_dict['BASE_URL_PORT'] = environ.get("PORT", '80')

config_dict['HEROKU_APP_NAME'] = environ.get("HEROKU_APP_NAME", False)
config_dict['HEROKU_API_KEY'] = environ.get("HEROKU_API_KEY", False)
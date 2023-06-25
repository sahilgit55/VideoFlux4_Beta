from logging import FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info
from os import path as ospath, environ
from subprocess import run as srun
from requests import get
from dotenv import load_dotenv
from pymongo import MongoClient

def dwFromUrl(url, filename):
        r = get(url, allow_redirects=True, stream=True, timeout=60)
        with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024 * 10):
                        if chunk:
                                fd.write(chunk)
        return

if ospath.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)


basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[FileHandler('log.txt'), StreamHandler()],
            level=INFO)


CONFIG_FILE_URL = environ.get("CONFIG_FILE_URL", '')
if len(CONFIG_FILE_URL) and str(CONFIG_FILE_URL).startswith("http"):
        log_info(f"Downloading Config File From URL {CONFIG_FILE_URL}")
        dwFromUrl(CONFIG_FILE_URL, "config.env")

load_dotenv('config.env', override=True)

BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    log_error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

bot_id = BOT_TOKEN.split(':', 1)[0]

DATABASE_URL = environ.get('DATABASE_URL', '')
DB_NAME = environ.get("DB_NAME","videoflux")
if len(DATABASE_URL) == 0:
    DATABASE_URL = None

if DATABASE_URL is not None:
    conn = MongoClient(DATABASE_URL)
    db = conn[DB_NAME]
    config_dict = db.settings.config.find_one({'_id': bot_id})
    if config_dict is not None:
        environ['UPSTREAM_REPO'] = config_dict['UPSTREAM_REPO']
        environ['UPSTREAM_BRANCH'] = config_dict['UPSTREAM_BRANCH']
    conn.close()

UPSTREAM_REPO = environ.get('UPSTREAM_REPO', '')
if len(UPSTREAM_REPO) == 0:
    UPSTREAM_REPO = None

UPSTREAM_BRANCH = environ.get('UPSTREAM_BRANCH', '')
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = 'master'

if UPSTREAM_REPO is not None:
    if ospath.exists('.git'):
        srun(["rm", "-rf", ".git"])

    update = srun([f"git init -q \
                     && git config --global user.email nik66x@gmail.com \
                     && git config --global user.name {DB_NAME} \
                     && git add . \
                     && git commit -sm update -q \
                     && git remote add origin {UPSTREAM_REPO} \
                     && git fetch origin -q \
                     && git reset --hard origin/{UPSTREAM_BRANCH} -q"], shell=True)

    if update.returncode == 0:
        log_info('Successfully updated with latest commit from UPSTREAM_REPO')
    else:
        log_error(
            'Something went wrong while updating, check UPSTREAM_REPO if valid or not!')

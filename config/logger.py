from logging import StreamHandler, getLogger, basicConfig, ERROR, INFO
from logging.handlers import RotatingFileHandler

log_file = 'BotLog.txt'

basicConfig(level=INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
                        datefmt="%H:%M(%d-%b)",
                        handlers=[RotatingFileHandler(log_file, maxBytes=50000000, backupCount=10, encoding="utf-8"), StreamHandler()]
                        )


getLogger("pyrogram").setLevel(ERROR)
LOGGER = getLogger()
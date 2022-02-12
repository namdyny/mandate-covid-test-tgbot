
from lib2to3.pgen2 import parse
from server.manager import *


if __name__ == '__main__':
    tg_bot = TelegramBot()
    tg_bot.thread_update_worker()
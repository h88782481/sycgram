from pyrogram import Client
from tools.configparser import BotConfigParser
from loguru import logger

def create_user_bot():
    logger.debug("正在创建User_Bot会话.")
    bot_config = BotConfigParser().get_config()
    api_id = bot_config["pyrogram"].get("api_id")
    api_hash = bot_config["pyrogram"].get("api_hash")
    #ipv6 = bot_config["pyrogram"].get("ipv6")

    bot = Client(
        "./data/app",
        api_id=api_id,
        api_hash=api_hash,
        plugins=dict(root="plugins"),
        #ipv6 = ipv6,
        # proxy={
        #     "scheme": "socks5",
        #     "hostname": "127.0.0.1",
        #     "port": 10808,
        #     # "username": "username",
        #     # "password": "password"
        # },
    )
    logger.debug("User_Bot会话创建成功.")
    logger.complete()
    return bot

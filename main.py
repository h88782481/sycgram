from pyrogram.methods.utilities.idle import idle
from core import user_bot
from tools.initializer import init_logger


async def main():
    init_logger()
    await user_bot.start()
    await idle()
    await user_bot.stop()


if __name__ == '__main__':
    user_bot.run(main())

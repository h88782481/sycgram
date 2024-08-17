
from typing import Dict, List

# Some params of sycgram
SYCGRAM: str = "sycgram"
SYCGRAM_INFO: str = f"{SYCGRAM.title()} | INFO"
SYCGRAM_ERROR: str = f"{SYCGRAM.title()} | ERROR"
SYCGRAM_WARNING: str = f"{SYCGRAM.title()} | WARNING"
COMMAND_YML: str = './data/command.yml'
CMD_YML_REMOTE: str = "https://raw.githubusercontent.com/h88782481/sycgram/main/data/command.yml"
UPDATE_CMD: str = "docker run --rm " \
    "-v /var/run/docker.sock:/var/run/docker.sock " \
    "containrrr/watchtower " \
    "--trace " \
    "--cleanup " \
    "--run-once " \
    f"{SYCGRAM}"


# ------------- Load --------------
DOWNLOAD_PATH: str = './data/download/'


# ------------- sticker --------------
# STICKER_BOT: int = 429000
STICKER_BOT: str = "@Stickers"
STICKER_IMG: str = './data/img/tmp.png'
STICKER_DESCRIP: str = b'A Telegram user has created the Sticker\xc2\xa0Set.'.decode(
    'utf-8')
GT_120_STICKERS: str = "哇!这些贴纸大概够一套了, " \
                       "让它休息一下吧。目前一套贴纸不能超过120个。"
UNACCEPTABLE_SET_NAME: str = '对不起，这个短名字不能使用。'
TAKEN_SET_NAME: str = '对不起，这个短名字已经有人用了。'
INVALID_SET_NAME: str = '选择了无效的集合。'
STICKER_ERROR_LIST: List[str] = [
    GT_120_STICKERS,
    UNACCEPTABLE_SET_NAME,
    TAKEN_SET_NAME,
    INVALID_SET_NAME,
]

# ------------- Store -------------
STORE_CC_DATA: str = 'data:cc'
STORE_NOTES_DATA: str = 'data:notes'
STORE_TRACE_DATA: str = 'data:trace'
STORE_GHOST_DATA: str = 'data:ghost'
STORE_GHOST_CACHE: str = 'cache:ghost'


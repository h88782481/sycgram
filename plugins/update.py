import asyncio
import sys
from subprocess import PIPE, Popen

from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.types import Message
from tools.constants import (SYCGRAM, SYCGRAM_ERROR, SYCGRAM_INFO,
                             SYCGRAM_WARNING, UPDATE_CMD)
from tools.updates import (get_alias_of_cmds, is_latest_version,
                           pull_and_update_command_yml, reset_cmd_alias,
                           update_cmd_alias, update_cmd_prefix)
from pyrogram.enums import ParseMode 

"""
重启
"""
@Client.on_message(command("restart"))
async def restart(_: Client, message: Message):
    
    text = f"**{SYCGRAM_INFO}**\n> # `重新启动 {SYCGRAM} ...`"
    await message.edit_text(text=text, parse_mode=ParseMode.MARKDOWN)
    sys.exit()

"""
更新sycgram到主分支的最新版本
"""
@Client.on_message(command("update"))
async def update(_: Client, message: Message):
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 2 or command_len < 1:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    version_info = f"**{SYCGRAM_INFO}**\n> # `当前版本为最新版本.`"
    if command_len == 2 and message.command[1] == "force":
        try:
            res = await is_latest_version()
        except Exception as e:
            logger.error(e)
            return await message.edit_text(f"发生了错误：{e}")
        if res:
            return await message.edit_text(version_info, parse_mode=ParseMode.MARKDOWN)
        else:
            text = f"**{SYCGRAM_INFO}**\n> # `更新到最新版本.`"
    else :
        text = f"**{SYCGRAM_INFO}**\n> # `强制更新到最新版本.`"

    await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    try:
        await pull_and_update_command_yml()
        p = Popen(UPDATE_CMD, stdout=PIPE, shell=True)
        p.communicate()
    except asyncio.exceptions.TimeoutError:
        text = f"**{SYCGRAM_WARNING}**\n> # `更新超时!`"
    except Exception as e:
        text = f"**{SYCGRAM_ERROR}**\n> # `{e}`"
    else:
        text = version_info
    finally:
        await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)

"""
更改所有指令的前缀
"""
@Client.on_message(command("prefix"))
async def prefix(_: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len != 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    punctuation = list("""!#$%&*+,-./:;=?@^~！？。，；·\\""")
    
    if message.command[1] == "reset":
        try:
            await pull_and_update_command_yml(is_update=False)
        except Exception as e:
            logger.error(e)
            return await message.edit_text(f"发生了错误：{e}")
        else:
            await message.edit_text("✅ 重置 command.yml 到默认配置.")
            sys.exit()
            
    elif message.command[1] not in punctuation:
        text = f"**{SYCGRAM_WARNING}**\n> # `前缀必须是{' '.join(punctuation)}其中之一`"
        return await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    
    try:
        update_cmd_prefix(message.command[1])
    except Exception as e:
        logger.error(e)
        return await message.edit_text(f"发生了错误：{e}")
    else:
        text = f"**{SYCGRAM_INFO}**\n> # `正在重新更新所有命令的前缀。`"
        await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        sys.exit()

"""
修改指令别名
"""
@Client.on_message(command("alias"))
async def alias(_: Client, message: Message):
    command_len = len(message.command)
    if command_len == 4 and message.command[1] == 'set':
        try:
            update_cmd_alias(message.command[2], message.command[3])
        except Exception as e:
            logger.error(e)
            await message.edit_text(f"发生了错误：{e}")
        else:
            text = f"**{SYCGRAM_INFO}**\n> # `更新别名由 <{message.command[2]}> 到 <{message.command[3]}> ...`"
            await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
            sys.exit()

    elif command_len == 3 and message.command[1] == 'reset':
        try:
            reset_cmd_alias(message.command[2])
        except Exception as e:
            logger.error(e)
            await message.edit_text(f"发生了错误：{e}")
        else:
            text = f"**{SYCGRAM_INFO}**\n> # `重新设置别名为 <{message.command[2]}> ...`"
            await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
            sys.exit()

    elif command_len == 2 and message.command[1] == 'list':
        try:
            data = get_alias_of_cmds()
            tmp = ''.join(f"`{k}` | `{v}`\n" for k, v in data.items())
            text = f"**⭐️ 指令别名：**\n**源名** | **别名**\n{tmp}"
        except Exception as e:
            logger.error(e)
            await message.edit_text(f"发生了错误：{e}")
        else:
            await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()

import asyncio
import os

from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.types import Message
from tools.constants import DOWNLOAD_PATH, SYCGRAM

"""
上传文件
"""
@Client.on_message(command("upload"))
async def upload(client: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len != 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    replied_msg_id = message.reply_to_message.id if message.reply_to_message else None
    _, filename = os.path.split(message.command[1])
    
    try:
        res = await client.send_document(
            chat_id=message.chat.id,
            document=message.command[1],
            caption=f"```From {SYCGRAM}```",
            file_name=filename,
            reply_to_message_id=replied_msg_id
        )
    except Exception as e:
        return await message.edit_text(f"发生错误: `{e}`")
    else:
        if res:
            await message.delete()
        else:
            await message.edit_text("⚠️ 可能上传失败 ...")

"""
下载目标消息的文件
"""
@Client.on_message(command("download"))
async def download(_: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #判断是否回复了一条消息
    replied_msg = message.reply_to_message
    if replied_msg == None:
        await message.edit_text("你需要回复一条消息.")
        await asyncio.sleep(2)
        return await message.delete()

    try:
        res = await replied_msg.download(file_name=DOWNLOAD_PATH if not message.command[1] else message.command[1])
    except ValueError:
        return await message.edit_text(f"发生错误!")
    except Exception as e:
        logger.error(e)
        return await message.edit_text(f"发生错误: `{e}`")
    else:
        if res:
            await message.edit_text("✅ 下载成功。")
            await asyncio.sleep(3)
            await message.delete()
        else:
            await message.edit_text("⚠️ 可能下载失败 ...")

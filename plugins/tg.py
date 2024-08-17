import asyncio
from core import command
from loguru import logger
from typing import Any, Dict
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message
from tools.sessions import get_session
from pyrogram.enums import ParseMode 

TG_API = 'https://www.cnuseful.com/api/index/lickDog'
async def get_api(session) -> Dict[str, Any]:
    try:
        response = await session.get(TG_API, timeout=5.5)
        if response.status_code==200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"发生了错误：{e}")
        return None
    
    
"""
肯德基
"""   
@Client.on_message(command("tg"))
async def diss(_: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len != 1:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    session = await get_session()
    await message.edit_text(f"👅 正在准备开舔...")
    json = await get_api(session)
    try:
        await message.edit_text(json.get("data"), parse_mode=ParseMode.MARKDOWN)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await message.edit_text(json.get("data"), parse_mode=ParseMode.MARKDOWN)
    except RPCError as e:
        logger.error(e)
        await message.edit_text(f"发生了错误：{e}")
    finally:
        await logger.complete()


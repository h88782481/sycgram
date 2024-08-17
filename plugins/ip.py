import asyncio
from loguru import logger
from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.sessions import get_session

IP_API = f"http://ip-api.com/json/"
async def get_api(ip: str,session) -> str:
    try:
        response = await session.get(IP_API+ip, timeout=5.5)
        if response.status_code==200:
            data = response.json()
            tmp = '\n'.join(f"{k}：`{v}`" for k, v in data.items())
            return tmp if tmp else "😂 没有响应 ~"
        return None
    except Exception as e:
        logger.error(f"发生了错误：{e}")
        return None
    
"""
查询ip信息
"""
@Client.on_message(command('ip'))
async def ip(_: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len != 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    session = await get_session()
    
    try:
        text = await get_api("" if message.command[1]=="me" else message.command[1],session)
        await message.edit_text(text)
    except Exception as e:
        await message.edit_text(f"发生了错误：{e}")
    finally:
        await logger.complete()


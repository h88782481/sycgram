import asyncio

from core import command
from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message
from time import time
from typing import Union
from tools.constants import STORE_GHOST_DATA, STORE_GHOST_CACHE
from pyrogram.enums.chat_type import ChatType
from tools.storage import SimpleStore
from pyrogram.enums import ParseMode 
from tools.utils import get_fullname, get_sender_name

GHOST_INTERVAL: float = 1.5

"""
是否自动标记为已读
"""
async def get_ghost_to_read(cid: Union[int, str]) -> bool:
    
    async with SimpleStore() as store:
        ghost_cache = store.get_data(STORE_GHOST_CACHE)
        if ghost_cache == None:
            ghost_cache = {}
        ghost_list = store.get_data(STORE_GHOST_DATA)
        if ghost_list == None:
            ghost_list = {}
        if cid in ghost_list.keys() and (
            not ghost_cache.get(cid) or
            time() - ghost_cache.get(cid) > GHOST_INTERVAL
        ):
            ghost_cache[cid] = time()
            return True
        return False
    
"""
自动标记对话为<已读>
"""
@Client.on_message(filters.incoming, group=-2)
async def ghost_event(client: Client, message: Message):
    
    if await get_ghost_to_read(message.chat.id):
        try:
            await client.get_chat_history(message.chat.id)
        except RPCError as e:
            logger.error(e)
        else:
            if message.text or message.caption:
                chat_name = message.chat.title or ChatType.PRIVATE
                sender_name = get_sender_name(message)
                text = message.text or message.caption
                text = f"Ghost | {chat_name} | {sender_name} | {text}"
                logger.debug(text)
        finally:
            await logger.complete()

"""
将该对话标记为可自动<已读>状态
"""
@Client.on_message(command('ghost'))
async def ghost(_: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 2 or command_len < 0:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #初始化
    store = SimpleStore(auto_flush=False)
    ghost_data = store.get_data(STORE_GHOST_DATA)
    if ghost_data == None:
        ghost_data = {}
    chat = message.chat
    
    #如果只有一个参数，将此对话标记为可自动<已读>状态
    if command_len == 1:
        if chat.id in ghost_data:
            text = "❌ 已关闭此对话的ghost"
            ghost_data.pop(chat.id, None)
        else:
            text = "✅ 已开启此对话的ghost"
            ghost_data[chat.id] = chat.title or get_fullname(message.from_user)
        store.set_data(STORE_GHOST_DATA,ghost_data)
        store.flush()
        await message.edit_text(text)
        await asyncio.sleep(3)
        return await message.delete()
    
    #查看当前对话状态或者ghost名单
    if command_len == 2:
        if message.command[1] == 'status':
            text = f"此对话是否开启ghost：{'✅' if chat.id in ghost_data else '❌'}"
            await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(3)    
            return await message.delete()
        
        elif message.command[1] == 'list':
            tmp = '\n'.join(f'```{k} {v}```' for k, v in ghost_data.items())
            text = f"📢 已开启ghost的对话名单：\n{tmp}"
            await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(3)    
            return await message.delete()
        
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()

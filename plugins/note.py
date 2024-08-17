import asyncio
from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import BadRequest, FloodWait
from pyrogram.types import Message
from tools.constants import STORE_NOTES_DATA
from tools.storage import SimpleStore

"""
回复一条消息，根据序号保存/删除该消息文本
"""
@Client.on_message(command('note'))
async def note(_: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 3 or command_len < 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    #初始化
    store = SimpleStore(auto_flush=False)
    notes_data = store.get_data(STORE_NOTES_DATA)
    text = ""
    
    #两个参数的情况
    if command_len == 2:
        if message.command[1] == "list":
            tmp = '\n'.join(
                    f'`{k} | {v[0:30]} ...`' for k, v in notes_data.items())
            text = f"已保存的笔记：\n{tmp}"
        elif message.command[1] == 'clear':
            notes_data.clear()
            text = "✅ 所有保存的笔记已被删除."
        else:
            res = notes_data.get(message.command[1])
            text = res if res else f"😱 没有找到{message.command[1]}对应的笔记."
            
    #三个参数的情况
    if command_len == 3:
        if message.command[1] == "save":
            if message.reply_to_message != None:
                notes_data[message.command[2]] = message.reply_to_message.text or message.reply_to_message.caption
                text = "😊 笔记保存成功."
            else:
                text = "请回复一条消息."
        elif message.command[1] == "del":
            if notes_data.pop(message.command[2], None):
                text = "😊 笔记删除成功."
            else:
                text = "❓ 找不到需要删除的笔记."
                
    #完成
    try:
        await message.edit_text(text)
    except BadRequest as e:
        logger.error(e)  # 存在消息过长的问题，应拆分发送。（就不拆 😊）
    except FloodWait as e:
        logger.warning(e)
        await asyncio.sleep(e.x)
        await message.edit_text(text)
    finally:
        store.set_data(STORE_NOTES_DATA,notes_data)
        store.flush()
        await logger.complete()

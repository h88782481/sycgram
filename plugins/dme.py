import asyncio
import time
from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from tools.utils import convert_string_to_int

"""
计算输入的参数是否超过搜索限制数
"""
def get_iter_limit(num: int) -> int:
    return num * 3 if num * 3 < 1000 else 1000
 
"""
尝试按块删除消息以处理速率限制.
""" 
async def delete_messages(client: Client, chat_id: int, ids: list):
    try:
        await client.delete_messages(chat_id, ids)
    except FloodWait as e:
        logger.warning(f"限制等待触发. 休息 {e.x+0.5} 秒.")
        await asyncio.sleep(e.x+0.5)
        await delete_messages(client, chat_id, ids)  # 等待后重试
    except Exception as e:
        logger.error(f"删除消息失败: {e}")
    ids.clear()
    
"""
删除历史消息
"""
@Client.on_message(command('dme'))
async def dme(client: Client, message: Message):
    command_len = len(message.command)
    
    
    #判断参数数量是否正确并且第二个参数是否为正整数
    if command_len > 2 or command_len < 0:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    del_num = 1
    if command_len == 2:
        del_num = convert_string_to_int(message.command[1])
        
    if del_num == None or del_num < 0:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
       
    #删除逻辑
    counter = 0
    ids_to_delete = []
    await message.edit_text("🧹 正在删除历史消息...")
    start_time = time.time()
    
    # 第一阶段，暴力扫描最近的消息，这些消息有可能无法搜索到
    async for msg in client.get_chat_history(message.chat.id, limit=get_iter_limit(del_num)):
        if msg.from_user.is_self:
            logger.info(f'{message.command[0]} | 扫描到历史消息 | id: {msg.id}')
            ids_to_delete.append(msg.id)
            counter += 1
            if len(ids_to_delete) == 100:
                await delete_messages(client, ids_to_delete, ids_to_delete)
            if counter == del_num:
                break
            
    # 第二阶段，对于老的消息直接扫描性能不好，还会触发限制，使用搜索功能来提速 
    if counter < del_num:
        async for msg in client.search_messages(chat_id=message.chat.id, offset=counter, from_user='me', limit=del_num - counter):
            ids_to_delete.append(msg.id)
            counter += 1
            if len(ids_to_delete) == 100:  # 如果累积到100条，就进行一次删除
                await delete_messages(client, message.chat.id, ids_to_delete)
            if counter == del_num + 1:  # 如果达到了用户想要删除的消息数量，退出循环
                break

    # 循环结束后，删除剩余的消息（如果有）
    if len(ids_to_delete) != 0:
        await delete_messages(client, message.chat.id, ids_to_delete)
        
    end_time = time.time() - start_time
    result_text = f"🧹 删除了 {counter} 条消息,共耗费 {end_time:.3f} 秒."
    res = await message.reply(result_text)
    await asyncio.sleep(3)
    await res.delete()
    logger.success(f"{message.command[0]} | {result_text}")
    await logger.complete()

        

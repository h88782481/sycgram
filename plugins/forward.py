import asyncio
from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import RPCError
from pyrogram.types import Message
from tools.utils import convert_string_to_int

"""
转发目标消息
"""
@Client.on_message(command('f'))
async def forward(_: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 2 or command_len < 0:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #判断是否回复了一条消息
    replied_msg = message.reply_to_message
    if replied_msg == None:
        await message.edit_text("请回复一条消息.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #判断有没有第二个数字参数，如果没有默认为1
    num = 1
    if command_len == 2:
        num = convert_string_to_int(message.command[1])
        
    #判断第二个参数是否为正整数       
    if num == None or num < 0:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #判断消息是否受到保护
    if replied_msg.has_protected_content or replied_msg.chat.has_protected_content:
        await message.edit_text("😮‍💨 请不要转发受保护的消息!")
        await asyncio.sleep(3)
        return await message.delete()
    
    for _ in range(num):
        try:
            
            await replied_msg.forward(message.chat.id, disable_notification=True)
        except RPCError as e:
            logger.error(e)
    await logger.complete()

"""
无引用转发
"""
@Client.on_message(command('cp'))
async def copy_forward(client: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 3 or command_len < 0:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #判断是否回复了一条消息
    replied_msg = message.reply_to_message
    if replied_msg == None:
        await message.edit_text("请回复一条消息.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #判断有没有第二个数字参数，如果没有默认为1
    num = 1
    if command_len == 2:
        num = convert_string_to_int(message.command[1])
    
    #判断第二个参数是否为正整数    
    if num == None or num < 0:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #判断消息是否受到保护
    if replied_msg.has_protected_content or replied_msg.chat.has_protected_content:
        await message.edit_text("😮‍💨 请不要转发受保护的消息!")
        await asyncio.sleep(3)
        return await message.delete()

    for _ in range(num):
        try:
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=message.chat.id,
                message_id=message.reply_to_message.id,
                disable_notification=True
            )
        except RPCError as e:
            logger.error(e)
    await logger.complete()

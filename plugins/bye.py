import asyncio
from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums.chat_type import ChatType

"""
删除当前对话的消息（仅私人聊天）
"""
@Client.on_message(command("bye"))
async def calculate(client: Client, message: Message):
    command_len = len(message.command)
    
    #判断参数数量是否正确
    if command_len == 2:
        await message.edit_text("请确认是否真的要删除当前对话消息,如果真的需要删除请重新输入指令并在命令后加上true参数.")
        await asyncio.sleep(5)
        return await message.delete()
        
    #判断第二个参数是否为true
    if message.command[1] == "true" and message.chat.type == ChatType.PRIVATE:
        await message.edit_text("即将删除当前对话消息...")
        cid = message.chat.id
        logger.info(f" {message.command[0]} | 这个对话的id是 {cid}")
        await client.delete_messages(chat_id=cid, message_ids=[
            message.id async for message in client.get_chat_history(cid)
        ])
        await message.chat.archive()
        await logger.complete()
    
    
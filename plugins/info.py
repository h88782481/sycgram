import asyncio
from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.utils import get_fullname

"""
直接使用或者回复目标消息，从而获取各种IDs
"""
@Client.on_message(command("id"))
async def get_id(_: Client, message: Message):
       
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len != 1:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
 
    text = f"消息ID: `{message.id}`\n\n" \
           f"群聊标题: `{message.chat.title or message.chat.first_name}`\n" \
           f"群聊类型: `{message.chat.type}`\n" \
           f"群聊ID: `{message.chat.id}`"

    replied_msg = message.reply_to_message
    
    if replied_msg and replied_msg.from_user:
        user = replied_msg.from_user
        text = f"回复消息ID: `{replied_msg.id}`\n\n" \
               f"用户昵称: `{get_fullname(user)}`\n"\
               f"用户名: `@{user.username}`\n" \
               f"用户ID: `{user.id}`\n\n" \
               f"{text}"
    elif replied_msg and replied_msg.sender_chat:
        sender_chat = replied_msg.sender_chat
        text = f"回复消息ID: `{replied_msg.id}`\n\n" \
               f"群聊标题: `{sender_chat.title}`\n" \
               f"消息类型: `{sender_chat.type}`\n" \
               f"群聊ID: `{sender_chat.id}`\n\n" \
               f"{text}"

    await message.edit_text(text)

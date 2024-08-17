import asyncio
from typing import Union
from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message
from pyrogram.enums import ParseMode 
from pyrogram.enums.chat_type import ChatType

async def kick_one(client: Client, cid: Union[int, str], uid: Union[int, str]):
    me = await client.get_chat_member(cid, 'me')
    if me.can_restrict_members and await client.ban_chat_member(cid, uid):
        return True
    return False

"""
回复一条消息，将在所有共同且拥有管理踢人权限的群组中踢出目标消息的主人
"""
@Client.on_message(command('sb'))
async def sb(client: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len != 1:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #判断是否回复了一条消息
    replied_msg = message.reply_to_message
    if replied_msg == None:
        await message.edit_text("请回复一条消息.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #判断是否在群聊中使用
    if message.chat.type in [ChatType.BOT, ChatType.PRIVATE]:
        await message.edit_text("请在群聊中使用.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #开始踢出群聊
    counter, target = 0, replied_msg.from_user
    common_groups = await target.get_common_chats()
    logger.info(
        f"开始从各个群聊中踢出此用户 <{target.first_name}{target.last_name} <{target.id}>")
    for chat in common_groups:
        try:
            if await kick_one(client, chat.id, target.id):
                counter = counter + 1

        except FloodWait as e:
            await asyncio.sleep(e.x)
            if await kick_one(client, chat.id, target.id):
                counter = counter + 1
                logger.success(
                    f"已将该用户踢出 <{chat.tile} {chat.id}>"
                )

        except RPCError as e:
            logger.warning(
                f"此群聊中没有管理员权限 <{chat.title} {chat.id}>")
            logger.warning(e)

    # 删除该用户的所有消息
    await client.delete_user_history(message.chat.id, target.id)

    # 完毕
    text = f"😂 在 {counter} 个公共群聊中踢出了 {target.mention(style=ParseMode.MARKDOWN)} 。"
    await message.edit_text(text)
    await asyncio.sleep(10)
    await message.delete()
    await logger.complete()

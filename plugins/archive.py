import asyncio
from core import command
from pyrogram import Client
from pyrogram.types import Message

"""
归档当前对话
"""
@Client.on_message(command("archive"))
async def archive(client: Client, message: Message):
    
    #判断参数数量是否正确
    if len(message.command) != 1:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(2)
        return await message.delete()
    
    #参数正确逻辑
    if await client.archive_chats(message.chat.id):
        await message.edit_text(f"✅ 归档 `{message.chat.title}` 成功.")
    else:
        await message.edit_text(f"❌ 归档失败 `{message.chat.title}` !")
        
    await asyncio.sleep(2)
    await message.delete()

"""
撤销归档当前对话
"""
@Client.on_message(command("unarchive"))
async def unarchive(client: Client, message: Message):
    
    #判断参数数量是否正确
    if len(message.command) != 1:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(2)
        return await message.delete()
    
    #参数正确逻辑
    if await client.unarchive_chats(message.chat.id):
        await message.edit_text(f"✅ 取消归档 `{message.chat.title}` 成功.")
    else:
        await message.edit_text(f"❌ 取消归档失败 `{message.chat.title}` !")
        
    await asyncio.sleep(2)
    await message.delete()

import asyncio
from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.utils import basher

"""
计算器
"""
@Client.on_message(command("cal"))
async def calculate(_: Client, message: Message):
    command_len = len(message.command)
    
    #判断参数数量是否正确
    if command_len == 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
        
    #计算逻辑
    args = message.command[1]
    try:
        res = await basher(f"""echo "scale=4;{args}" | bc""", 3)
    except asyncio.exceptions.TimeoutError:
        return await message.edit_text("连接超时!")
    
    if not res.get('output'):
        await message.edit_text(f"错误:{res.get('error')}")
        return

    text = f"""输入:`{args}`\n输出:`{res.get('output')}`"""
    await message.edit_text(text)
        

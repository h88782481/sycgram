import asyncio
from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.utils import basher

"""
查询系统信息
"""
@Client.on_message(command("sysinfo"))
async def sysinfo(_: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len != 1:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    res = await basher("neofetch --config none --stdout")
    if not res.get('error'):
        await message.edit_text(f"```{res.get('output')}```")
    else:
        await message.edit_text(f"```{res.get('error')}```")

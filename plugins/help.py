import asyncio
from core import CMDS_DATA, command, CMDS_PREFIX
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode 

"""
指令用法提示。
"""
@Client.on_message(command('help'))
async def helper(_: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 2 or command_len < 0:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    data = CMDS_DATA
    cmd_alias = dict(zip((v.get('cmd') for v in data.values()), data.keys()))
    
    #如果只有一个参数，显示全部指令
    if command_len == 1:
        tmp = '、'.join(f"`{k}`" for k in data.keys())
        text = f"📢 **指令列表：**\n{tmp}\n\n**发送** `{CMDS_PREFIX}help <cmd>` **查看某指令的详细用法**"
        await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        
    #如果有两个参数，显示第二个参数指令的用法
    if command_len == 2:
        if not data.get(message.command[1]) and message.command[1] not in cmd_alias:
            text = f"❗️ 这个指令不存在 >>> `{message.command[1]}`"
        else:
            key = message.command[1] if data.get(message.command[1]) else cmd_alias.get(message.command[1])
            text = f"格式：`{data.get(key).get('format')}`\n" \
                f"用法：`{data.get(key).get('usage')}`"
            await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
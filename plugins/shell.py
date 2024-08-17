import asyncio
from getpass import getuser
from io import BytesIO
from platform import node
from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.utils import basher
from pyrogram.enums import ParseMode 

"""
执行shell脚本
"""
@Client.on_message(command("sh"))
async def shell(_: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len != 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()

    try:
        res = await basher(message.command[1], timeout=30)
    except asyncio.exceptions.TimeoutError:
        return await message.edit_text("与服务器连接超时!")

    _output: str = res.get('output') if not res.get(
        'error') else res.get('error')
    
    header = f"**{getuser()}@{node()}**\n"
    
    all_bytes = len(header.encode() + message.command[1].encode() + _output.encode())
    
    if all_bytes >= 2048:
        await message.delete()
        return await message.reply_document(
            document=BytesIO(_output.encode()),
            caption=f"{header}> # `{message.command[1]}`",
            file_name="output.log",
            parse_mode=ParseMode.MARKDOWN
        )

    await message.edit_text(
        f"{header}> # `{message.command[1]}`\n```{_output.strip()}```",
        parse_mode=ParseMode.MARKDOWN
    )

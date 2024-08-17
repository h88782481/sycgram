import asyncio
from core import command
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode 

"""
根据名称和数据中心ID构建返回文本。
"""
def get_dc_location(name: str, dc_id: int) -> str:
    locations = {
        1: "美国佛罗里达州迈阿密",
        2: "荷兰北荷兰省阿姆斯特丹",
        3: "美国佛罗里达州迈阿密",
        4: "荷兰北荷兰省阿姆斯特丹",
        5: "新加坡"
    }
    location = locations.get(dc_id)
    
    if location:
        return f"{name} 的数据中心为：`DC{dc_id}`\n该数据中心位于：`{location}`"
    else:
        return "❗️无法获取该用户/群组的数据中心 ..."

"""
查看目标消息或当前对话的DC区
"""
@Client.on_message(command('dc'))
async def dc(_: Client, message: Message):
    
    #判断参数数量是否正确
    if len(message.command) != 1:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(2)
        return await message.delete()
    
    #判断有没有回复消息
    dc_id = message.reply_to_message.from_user.dc_id if message.reply_to_message else message.chat.dc_id
    name = message.reply_to_message.from_user.mention(style=ParseMode.MARKDOWN) if message.reply_to_message else f"`{message.chat.title or message.chat.first_name}`"
    await message.edit_text(get_dc_location(name,dc_id))

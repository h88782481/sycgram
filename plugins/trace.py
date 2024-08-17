import asyncio

from core import command,is_traced
from loguru import logger
from pyrogram import Client
from pyrogram.errors import BadRequest, FloodWait, RPCError
from pyrogram.types import Message
from tools.constants import STORE_TRACE_DATA
from tools.storage import SimpleStore
from pyrogram.enums import ParseMode 

@Client.on_message(is_traced(), group=-4)
async def trace_event(client: Client, message: Message):
    user = message.from_user
    store = SimpleStore(auto_flush=False)
    trace_data = store.get_data(STORE_TRACE_DATA)
    try:
        emoji = trace_data.get(user.id)
        await client.send_reaction(
            message.chat.id, message.id, emoji
        )
    except BadRequest:
        failure = f"在 <{message.chat.title}> 群组中不能使用 {emoji} 来回应."
        trace_data.pop(user.id, None)
        store.set_data(STORE_TRACE_DATA, trace_data)
        store.flush()
        await client.send_message('me', failure)
    except RPCError as e:
        logger.error(e)

"""
群组中追着丢emoji
"""
@Client.on_message(command('trace'))
async def trace(client: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    store = SimpleStore(auto_flush=False)
    trace_data = store.get_data(STORE_TRACE_DATA)

    #初始化
    if trace_data == None:
        trace_data = {}
        store.set_data(STORE_TRACE_DATA, trace_data)
        store.flush()

    if command_len == 2 and message.command[1]=="list":
        tmp = '\n'.join(f"`{k}` | {v}" for k, v in trace_data.items())
        text = f"📢 trace名单：\n{tmp}"
        return await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    elif command_len == 2 and message.command[1]=="clear":
        trace_data.clear()
        store.set_data(STORE_TRACE_DATA, trace_data)
        store.flush()
        text = "✅ 已清空trace名单"
        return await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        replied_msg = message.reply_to_message
        if replied_msg == None:
            await message.edit_text("你需要回复一条消息.")
            await asyncio.sleep(2)
            return await message.delete()
        emoji = '💩'
        if command_len !=1 :
            emoji = message.command[1]
        user = replied_msg.from_user
        try:
            await client.send_reaction(
                message.chat.id,
                replied_msg.id,
                emoji
            )
        except RPCError as e:
            logger.warning(e)
            return await message.edit_text(f"❗️ 不能在聊天中使用 {emoji}.")
        # 追踪列表中没有，则添加
        if not trace_data.get(user.id):
            trace_data[user.id] = emoji
            store.set_data(STORE_TRACE_DATA, trace_data)
            store.flush()
            text = f"✅ 添加 {user.mention(style=ParseMode.MARKDOWN)} 到trace列表"
            logger.success(text)
        # 追踪列表有，则删除
        elif trace_data.pop(user.id, False):
            text = f"✅ 将 {user.mention(style=ParseMode.MARKDOWN)} 从trace列表移除"
            store.set_data(STORE_TRACE_DATA, trace_data)
            store.flush()
            logger.success(text)
        # 删除失败
        else:
            text = f"❌ 将 {user.mention(style=ParseMode.MARKDOWN)} 从trace列表移除失败!!!"
            logger.warning(text)
            
        try:
            return await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            return await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        except RPCError as e:
            logger.error(e)
            return await message.edit_text(f"发生错误: `{e}`")
        finally:
            await logger.complete()
            await asyncio.sleep(3)
            await message.delete()


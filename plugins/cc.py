import asyncio
from random import random
from typing import List, Union
from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message
from tools.constants import STORE_CC_DATA
from tools.storage import SimpleStore
from tools.utils import convert_string_to_int
from pyrogram.enums.chat_type import ChatType

CC_MAX_TIMES: int = 233

async def emoji_sender(client: Client, chat_id: Union[int, str], msg_id: int, emoji: str = '') -> bool:
    try:
        await client.send_reaction(chat_id, msg_id, emoji)
    except FloodWait as e:
        raise e
    except RPCError:
        return False
    else:
        return True

"""
给对方发过的n条消息丢emoji
"""
@Client.on_message(command('cc'))
async def cc(client: Client, message: Message):
    
    #判断参数数量是否正确
    if len(message.command) != 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(2)
        return await message.delete()
    
    #初始化
    store = SimpleStore(auto_flush=False)
    if store.get_data(STORE_CC_DATA) == None:
        store.set_data(STORE_CC_DATA, '💩')
        store.flush()
     
    #参数为reset
    if message.command[1] == "reset":
        store.set_data(STORE_CC_DATA, '💩')
        store.flush()
        await message.edit_text(f"默认的表情将更改成 `💩`")
        await asyncio.sleep(2)
        return await message.delete()
    
    #参数为正整数
    cc_parameter = message.command[1]
    cc_int = convert_string_to_int(cc_parameter)
    if cc_int != None and cc_int >= 1:
        cc_emoji = store.get_data(STORE_CC_DATA)
        replied_msg = message.reply_to_message
        if replied_msg == None:
            await message.edit_text("你需要回复一条消息.")
            await asyncio.sleep(2)
            return await message.delete()

        # 攻击次数
        cc_int = cc_int if 1 <= cc_int <= CC_MAX_TIMES else CC_MAX_TIMES
        cc_msgs: List[int] = []
        from_user_id = replied_msg.from_user.id if replied_msg.from_user else replied_msg.sender_chat.id

        # 遍历和搜索消息
        if message.chat.type in [ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP]:
            async for target in client.search_messages(
                chat_id=message.chat.id, limit=1000,
                from_user=from_user_id,
            ):
                if target.id > 1 and (target.from_user or target.sender_chat):
                    cc_msgs.append(target.id)
                    if len(cc_msgs) == cc_int:
                        break
        else:
            async for target in client.get_chat_history(message.chat.id, limit=1000):
                logger.info(f"traget 类型: {type(target)}")
                if target.id > 1 and target.from_user and \
                        target.from_user.id == replied_msg.from_user.id:
                    cc_msgs.append(target.id)
                    if len(cc_msgs) == cc_int:
                        break

        if len(cc_msgs) > 0:
            await message.edit_text("🔥攻击中 ...")
            shot = 0
            for n, cc_msg_id in enumerate(cc_msgs):
                try:
                    res = await emoji_sender(
                        client=client,
                        chat_id=message.chat.id,
                        msg_id=cc_msg_id,
                        emoji=cc_emoji
                    )
                except FloodWait as e:
                    await asyncio.sleep(e + 1)
                    res = await emoji_sender(
                        client=client,
                        chat_id=message.chat.id,
                        msg_id=cc_msg_id,
                        emoji=cc_emoji
                    )

                if not res and shot == 0:
                    await message.edit_text(f"这个聊天不允许使用 {cc_emoji} 做出反应.")
                    await asyncio.sleep(2)
                    logger.complete()
                    return await message.delete()

                shot = shot + 1
                logger.success(f"{message.command[0]} | 攻击次数 | {n+1}")
                await asyncio.sleep(random() / 5)
            # 完成
            text = f"✅ 完成，命中率是 {shot/cc_int*100}%"
        else:
            # 完成
            text = "❓ 无法找到攻击目标！"
        await message.delete()
        res = await client.send_message(message.chat.id, text)
        await asyncio.sleep(3)
        logger.complete()
        return await res.delete()
    
    #参数为emoji
    store.set_data(STORE_CC_DATA, cc_parameter)
    store.flush()
    await message.edit_text(f"默认的表情将更改成 `{cc_parameter}`")
    await asyncio.sleep(2)
    await message.delete()
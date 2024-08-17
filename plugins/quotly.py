import base64
import asyncio
from core import command
from loguru import logger
from pyrogram import Client
from pyrogram.types import Message
from tools.sessions import get_session
from tools.utils import convert_string_to_int

QUOTLY_API: str = 'https://bot.lyo.su/quote/generate'

async def forward_info(replied_msg: Message):
    # 判断转发来源
    # 转发自频道
    if replied_msg.forward_from_chat:
        sid = replied_msg.forward_from_chat.id
        title = replied_msg.forward_from_chat.title
        name = title
    # 转发自用户或机器人
    elif replied_msg.forward_from:
        sid = replied_msg.forward_from.id
        try:
            try:
                name = first_name = replied_msg.forward_from.first_name
            except TypeError:
                name = '死号'
            if replied_msg.forward_from.last_name:
                last_name = replied_msg.forward_from.last_name
                name = f'{first_name} {last_name}'
        except AttributeError:
            pass
        title = name
    # 拒绝查看转发消息来源时
    elif replied_msg.forward_sender_name:
        title = name = sender_name = replied_msg.forward_sender_name
        sid = 0
    # 不是转发的消息
    elif replied_msg.from_user:
        try:
            sid = replied_msg.from_user.id
            try:
                name = first_name = replied_msg.from_user.first_name
            except TypeError:
                name = '死号'
            if replied_msg.from_user.last_name:
                last_name = replied_msg.from_user.last_name
                name = f'{first_name} {last_name}'
        except AttributeError:
            pass
        title = name
    return sid,title,name

@Client.on_message(command('q'))
async def quote(client: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #判断是否回复了一条消息
    replied_msg = message.reply_to_message
    if replied_msg == None:
        await message.edit_text("请回复一条消息.")
        await asyncio.sleep(3)
        return await message.delete()
    
    json_data = {
        "type": "quote",
        "format": "webp",
        "backgroundColor": "#1b1429",
        "width": 768,
        "height": 768,
        "scale": 2,
        "messages": []
    }
    
    session = await get_session()
    num = 1
    if command_len == 2:
        num = convert_string_to_int(message.command[1])
        if num == None or num < 0:
            await message.edit_text("❗️你应该输入一个正整数.")
            await asyncio.sleep(3)
            await message.delete()
            return
        
    #将本条消息加入转换队列
    sid, title ,name = await forward_info(replied_msg)
    messages_json = {
        "entities": [],
        "avatar": True,
        "from": {
            "id": sid,
            "language_code": "zh",
            "title": title,
            "name": name
        },
        "text": replied_msg.text
    }
    # 将要转成图片的消息加到消息列表里
    json_data["messages"].append(messages_json)

    if num > 1:
        messages = Client.get_chat_history(
            client,
            chat_id=replied_msg.chat.id, 
            limit=num-1,
            offset_id=replied_msg.id)
        async for msg in messages:
            sid, title ,name = await forward_info(msg)
            messages_json = {
                "entities": [],
                "avatar": True,
                "from": {
                    "id": sid,
                    "language_code": "zh",
                    "title": title,
                    "name": name
                },
                "text": msg.text
            }
            json_data["messages"].append(messages_json)
        json_data["messages"].reverse()
        
    await message.edit('等待Lyosu语录生成返回结果...')
    response = await session.post(QUOTLY_API, json=json_data)
    req = response.json()
    if req['ok'] == True:
        try:
            buffer = base64.b64decode(req['result']['image'].encode('utf-8'))
            open('Quotly.webp', 'wb').write(buffer)
            await message.edit("已在Lyosu生成并保存语录, 正在上传中...")
            await message.reply_document('Quotly.webp',force_document=False,reply_to_message_id=replied_msg.id)
            await message.delete()
            return
        except:
            await message.edit("请求成功但出现错误❗️")
            await asyncio.sleep(3)
            await message.delete()
            return
    else:
        await message.edit_text(f"请求出现错误!")
        await asyncio.sleep(3)
        await message.delete()

@Client.on_message(command('faq'))
async def fake_quote(_: Client, message: Message):
    
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len != 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #判断是否回复了一条消息
    replied_msg = message.reply_to_message
    if replied_msg == None:
        await message.edit_text("请回复一条消息.")
        await asyncio.sleep(3)
        return await message.delete()
    
    session = await get_session()
    
    json_data = {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1429",
        "width": 768,
        "height": 768,
        "scale": 2.5,
        "messages": []
    }
    
    #将本条消息加入转换队列
    replied_msg = message.reply_to_message
    sid, title ,name = await forward_info(replied_msg)
    messages_json = {
        "entities": [],
        "avatar": True,
        "from": {
            "id": sid,
            "language_code": "zh",
            "title": title,
            "name": name
        },
        "text": message.command[1]
    }
    # 将要转成图片的消息加到消息列表里
    json_data["messages"].append(messages_json)

    await message.edit('等待Lyosu语录生成返回结果...')
    response = await session.post(QUOTLY_API, json=json_data)
    req = response.json()
    if req['ok'] == True:
        try:
            buffer = base64.b64decode(req['result']['image'].encode('utf-8'))
            open('Quotly.webp', 'wb').write(buffer)
            await message.edit("已在Lyosu生成并保存语录, 正在上传中...")
            await message.reply_document('Quotly.webp',force_document=False,reply_to_message_id=replied_msg.id)
            await message.delete()
            return
        except:
            await message.edit("请求成功但出现错误❗️")
            await asyncio.sleep(3)
            await message.delete()
            return
    else:
        await message.edit_text(f"请求出现错误!")
        await asyncio.sleep(3)
        await message.delete()
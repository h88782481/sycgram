import asyncio
from core import command
from loguru import logger
from typing import Dict
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from tools.sessions import get_session
from pyrogram.enums import ParseMode 
from bs4 import BeautifulSoup
from urllib import parse

GOOGLE_API = "https://www.google.com/search?q="

"""
请求谷歌
"""
async def google_search(content: str,session) -> Dict[str, str]:
    result: Dict[str, str] = {}
    try:
        response = await session.get(GOOGLE_API+parse.quote(content), timeout=9.9)
        if response.status_code==200:
            soup = BeautifulSoup(response.text, 'lxml')
            for p in soup.find_all('h3'):
                if p.parent.has_attr('href'):
                    result[p.text] = p.parent.attrs.get('href')
                    logger.info(f"Google | 搜索 | {result[p.text]}")
                    if len(result) > 10:
                        break
            return result
        else:
            return None 
    except Exception as e:
        logger.error(f"发生了错误：{e}")
        return None   
    finally:
        await logger.complete()
        
"""
谷歌搜索并展示第一页结果和链接
"""
@Client.on_message(command("google"))
async def google(_: Client, message: Message):
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 2 or command_len < 0:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    session = await get_session()
    
    #如果只有一个参数，判断是否回复了一条消息
    if command_len == 1:
        #判断是否回复了一条消息
        if message.reply_to_message == None:
            await message.edit_text("请回复一条消息.")
            await asyncio.sleep(3)
            return await message.delete()
        try:
            res = await google_search(message.reply_to_message.text, session)
            links = '\n\n'.join(
                f"[{title[0:30]}]({url})" for title, url in res.items()
            )
            text = f"🔎 | **谷歌搜索结果** | `{message.reply_to_message.text}`\n{links}"
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(e)
            await message.edit_text("无法连接到谷歌!")
        finally:
            await logger.complete()
    
    #如果有两个参数，用谷歌搜索第二个参数文本
    if command_len == 2:
        try:
            res = await google_search(message.command[1], session)
            links = '\n\n'.join(
                f"[{title[0:30]}]({url})" for title, url in res.items()
            )
            text = f"🔎 | **谷歌搜索结果** | `{message.command[1]}`\n{links}"
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(e)
            await message.edit_text("无法连接到谷歌!")
        finally:
            await logger.complete()
        
    
    
    

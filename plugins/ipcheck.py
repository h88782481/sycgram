import asyncio
from time import time
from loguru import logger
from core import command
from typing import Any, Dict
from pyrogram import Client
from pyrogram.types import Message
from tools.sessions import get_session

"""
检测IP或者域名
"""
async def check_ip(ip: str, session) -> Dict[str, Any]:
    url = "https://www.vps234.com"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
        'origin': url,
        'referer': f'{url}/ipchecker/',
        'x-requested-with': 'XMLHttpRequest'
    }
    try:
        response = await session.post(
            f"{url}/ipcheck/getdata/", 
            data={
                'idName': f'itemblockid{int(round(time() * 1000))}',
                'ip': ip,
            },
            headers=headers,
            timeout=5.5)
        if response.status_code==200:
            return response.json()
    except Exception as e:
        logger.error(f"发生了错误：{e}")
        return None


"""
检测端口
"""
async def check_ip_port(ip: str, port: str, session) -> Dict[str, str]:
    url = "https://www.toolsdaquan.com/toolapi/public/ipchecking"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
        'referer': 'https://www.toolsdaquan.com/ipcheck/',
        'x-requested-with': 'XMLHttpRequest'
    }
    try:
        response1 = await session.post(
            f"{url}/{ip}/{port}", 
            headers=headers
        )
        if response1.status_code==200:
            inner_data = response1.json()
        response2 = await session.post(
            f"{url}2/{ip}/{port}", 
            headers=headers
        ) 
        if response2.status_code==200:
            outer_data = response2.json()
            inner_data.update(outer_data)
        return inner_data
    except Exception as e:
        logger.error(f"发生了错误：{e}")
        return None

"""
检测IP或者域名是否被阻断
"""
@Client.on_message(command("ipcheck"))
async def ip_checker(_: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 3 or command_len < 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    session = await get_session()
    
    #两个参数的情况
    if command_len == 2:
        try:
            resp = await check_ip(message.command[1],session)
            if resp == None:
                return await message.edit_text("发生错误,请查看日志!")
            data = resp.get('data')
            if resp.get('error') or not data.get('success') or resp == None:
                res = f"⚠️ Api连接失败。返回结果是 `{resp.get('msg')}`"
            else:  
                _data = data.get('data')
                in_icmp = "✅" if _data.get('innerICMP') else "❌"
                in_tcp = "✅" if _data.get('innerTCP') else "❌"
                out_icmp = "✅" if _data.get('outICMP') else "❌"
                out_tcp = "✅" if _data.get('outTCP') else "❌"
                res = f"```查询结果\n" \
                    f"Inner ICMP：{in_icmp}\n" \
                    f"Inner TCP： {in_tcp}\n" \
                    f"Outer ICMP：{out_icmp}\n" \
                    f"Outer TCP： {out_tcp}```"
            await message.edit_text(f"🔎 查询：地址`{message.command[1]}`\n{res}")
        except Exception as e:
            await message.edit_text(f"发生了错误：{e}")
        
    #三个参数的情况 
    if command_len == 3:
        try:
            resp = await check_ip_port(message.command[1], message.command[2], session)
            if resp == None:
                return await message.edit_text("发生错误,请查看日志!")
            def is_opened(key):
                return resp.get(key) == 'success'
            in_icmp = "✅" if is_opened('icmp') else "❌"
            in_tcp = "✅" if is_opened('tcp') else "❌"
            out_icmp = "✅" if is_opened('outside_icmp') else "❌"
            out_tcp = "✅" if is_opened('outside_tcp') else "❌"
            res = f"```查询结果\n" \
                f"Inner ICMP：{in_icmp}\n" \
                f"Inner TCP： {in_tcp}\n" \
                f"Outer ICMP：{out_icmp}\n" \
                f"Outer TCP： {out_tcp}```"
            await message.edit_text(f"🔎 查询：地址`{message.command[1]}` 端口：`{message.command[2]}`\n{res}")
        except Exception as e:
            await message.edit_text(f"发生了错误：{e}")


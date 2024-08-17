import asyncio
from core import command
from pyrogram import Client
from pyrogram.types import Message
from tools.sessions import get_session
from loguru import logger
from binance.spot import Spot
from binance.error import ClientError
from typing import Dict
from tools.utils import convert_string_to_float

EXCHANGE_API = "https://api.exchangerate-api.com/v4/latest/usd"

"""
获取真实货币的汇率表。
"""
async def get_from_exchanger(session) -> Dict:
    try:
        response = await session.get(EXCHANGE_API, timeout=5.5)
        if response.status_code==200:
            data = response.json()
            return data["rates"]
        return None
    except Exception as e:
        logger.error(f"发生了错误：{e}")
        return None
      
"""
货币转换器
"""
@Client.on_message(command('bc'))
async def coin(_: Client, message: Message):
    
    #判断参数数量是否正确
    if len(message.command) != 4:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(2)
        return await message.delete()
    
    session = await get_session()
    
    #初始化工作
    usd_rate = await get_from_exchanger(session)
    binance_client = Spot()
    if usd_rate == None:
        await message.edit_text("初始化错误,请重试,具体原因请查看log.")
        await asyncio.sleep(2)
        return await message.delete()

    #判断第一个参数是否为正数
    number = convert_string_to_float(message.command[1])
    if number == None or number <= 0.0:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(2)
        return await message.delete()

    #获取两个货币符号
    _from = message.command[2].upper()
    _to = message.command[3].upper()
    
     #真实货币-真实货币
    if (_from in usd_rate) and (_to in usd_rate):
        return await message.edit((
            f'{message.command[1]} {message.command[2].upper()} ='
            f'{number * usd_rate[_to] / usd_rate[_from]:.2f} '
            f'{message.command[3].upper()}'))
        
    #真实货币-加密货币
    if _from in usd_rate:
        usd_number = number / usd_rate[_from]
        try:
            x_usdt_data = binance_client.klines(f"{_to}USDT", "1m")[:1][0]
        except ClientError as ce:
            logger.error(f"发生了错误：{ce}")
            await message.edit(f'无法获取 {_from} 到 {_to} 的汇率.')
            await asyncio.sleep(2)
            return await message.delete()
        
        return await message.edit((
            f'{message.command[1]} **{_from}** = '
            f'{1 / float(x_usdt_data[1]) * usd_number:.8f} **{_to}**\n'
            f'{message.command[1]} **{_from}** = '
            f'{usd_number:.2f} **USD**'))
        
    
    #加密货币-真实货币
    if _to in usd_rate:
        usd_number = number * usd_rate[_to]
        try:
            x_usdt_data = binance_client.klines(f"{_from}USDT", "1m")[:1][0]
        except ClientError as ce:
            logger.error(f"发生了错误：{ce}")
            await message.edit(f'无法获取 {_from} 到 {_to} 的汇率.')
            await asyncio.sleep(2)
            return await message.delete()
        
        return await message.edit((
            f'{message.command[1]} **{_from}** = '
            f'{float(x_usdt_data[1]) * usd_number:.2f} **{_to}**\n'
            f'{message.command[1]} **{_from}** = '
            f'{float(x_usdt_data[1]):.2f} **USD**'))
        

    #加密货币-加密货币
    try:
        from_to_data = binance_client.klines(f"{_from}{_to}", "1m")[:1][0]
    except ClientError as ce:
        logger.error(f"发生了错误：{ce}")
        await message.edit(f'无法获取 {_from} 到 {_to} 的汇率.')
        await asyncio.sleep(2)
        return await message.delete()
    
    await message.edit((
            f'{message.command[1]} **{_from}** = '
            f'{float(from_to_data[1]) * number} **{_to}**\n'))
    await logger.complete()
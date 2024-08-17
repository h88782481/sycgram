import asyncio
from os.path import exists
from PIL import Image
import contextlib
from httpx import ReadTimeout
from core import command
from pyrogram import Client
from tools.sessions import get_session
from tools.utils import convert_string_to_int
from pyrogram.types import Message
from speedtest import (
    Speedtest,
    ShareResultsConnectFailure,
    ShareResultsSubmitFailure,
    NoMatchedServers,
    SpeedtestBestServerFailure,
    SpeedtestHTTPError,
)

"""
将字节转换为可读格式.
"""
def unit_convert(byte):
    
    power = 1000
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "Mb/s", 3: "Gb/s", 4: "Tb/s"}
    while byte > power:
        byte /= power
        zero += 1
    return f"{round(byte, 2)} {units[zero]}"

async def run_speedtest(session, server):
    test = Speedtest()
    if server:
        servers = test.get_closest_servers()
        for i in servers:
            if i["id"] == str(server):
                test.servers = [i]
                break
    test.get_best_server(servers=test.servers)
    test.download()
    test.upload()
    with contextlib.suppress(ShareResultsConnectFailure):
        test.results.share()
    result = test.results.dict()
    des = (
        f"**Speedtest** \n"
        f"测速点: `{result['server']['name']} - "
        f"{result['server']['cc']}` \n"
        f"服务商: `{result['server']['sponsor']}` \n"
        f"上传速度: `{unit_convert(result['upload'])}` \n"
        f"下载速度: `{unit_convert(result['download'])}` \n"
        f"延迟: `{result['ping']}` \n"
        f"时间戳: `{result['timestamp']}`"
    )
    if result["share"]:
        data = await session.get(
            result["share"].replace("http:", "https:"), follow_redirects=True
        )
        with open("speedtest.png", mode="wb") as f:
            f.write(data.content)
        with contextlib.suppress(Exception):
            img = Image.open("speedtest.png")
            c = img.crop((17, 11, 727, 389))
            c.save("speedtest.png")
    return des, "speedtest.png" if exists("speedtest.png") else None

async def get_all_ids():
    test = Speedtest()
    servers = test.get_closest_servers()
    return (
        (
            "附近的测速点有：\n\n"
            + "\n".join(
                f"`{i['id']}` - `{int(i['d'])}km` - `{i['name']}` - `{i['sponsor']}`"
                for i in servers
            ),
            None,
        )
        if servers
        else ("附近没有测速点", None)
    )

"""
使用speedtest测试网速
"""
@Client.on_message(command('speedtest'))
async def speedtest(client: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 2:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    session = await get_session()
    await message.edit_text("⚡️ Speedtest正在测速,请稍后...")
    try:
        #两个参数,第二个参数为list
        if command_len == 2 and message.command[1] == "list":
            des, photo = await get_all_ids()
        #有一个参数或者有两个参数且第二个为测速id
        else:
            if command_len == 1:
                server=None
            else:
                server = convert_string_to_int(message.command[1])
            des, photo = await run_speedtest(session, server)
    except SpeedtestHTTPError:
        return await message.edit_text("speedtest_连接失败")
    except (ValueError, TypeError):
        return await message.edit_text("参数错误")
    except (SpeedtestBestServerFailure, NoMatchedServers):
        return await message.edit_text("speedtest_服务器错误")
    except (ShareResultsSubmitFailure, RuntimeError, ReadTimeout):
        return await message.edit_text("speedtest_连接错误")
    if not photo:
        return await message.edit_text(des)
    try:
        await client.send_photo(
            message.chat.id,
            photo,
            caption=des,
            message_thread_id=message.message_thread_id or message.reply_to_message_id,
        )
    except Exception:
        return await message.edit_text(des)
    
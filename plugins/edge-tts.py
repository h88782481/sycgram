import os
import json
import asyncio
import edge_tts
from core import command
from pyrogram import Client
from pyrogram.types import Message

CONFIG_PATH = os.path.join(os.getcwd(), "data", "tts_config.json")
AUDIO_PATH = os.path.join(os.getcwd(), "data", "tts.mp3")

#tts默认配置
default_config = {
    "voice": "zh-CN-XiaoxiaoNeural", #音色
    "rate": "+0%", #语速
    "volume" : "+0%" #音量
}

#检查是否有配置文件并读取
async def config_check() -> dict:
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f)
        return default_config

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

#保存tts配置文件
async def config_set(short_name: str, config) -> bool:
    config["voice"] = short_name
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)


"""
智能语言转换
"""
@Client.on_message(command('tts'))
async def tts(client: Client, message: Message):
    
    #判断参数数量是否正确
    command_len = len(message.command)
    if command_len > 3 or command_len < 0:
        await message.edit_text("参数错误,使用前请查看help.")
        await asyncio.sleep(3)
        return await message.delete()
    
    #初始化配置文件
    config = await config_check()
    replied_msg = message.reply_to_message
    
    #如果只有一个参数，检查是否回复了一条文本消息，如果回复了一条文本消息，将其转换成语音
    if command_len == 1:
        if replied_msg == None:
            await message.edit_text("请回复一条文本消息.")
            await asyncio.sleep(3)
            return await message.delete()
        
        if replied_msg.text == None:
            await message.edit_text("请回复一条文本消息.")
            await asyncio.sleep(3)
            return await message.delete()
        
        mp3_buffer = edge_tts.Communicate(text=replied_msg.text,
                                      voice=config["voice"],
                                      rate=config["rate"],
                                      volume=config['volume'])
        await mp3_buffer.save(audio_fname=AUDIO_PATH)
        await message.reply_voice(AUDIO_PATH,reply_to_message_id=replied_msg.id)
        return await message.delete()
    
    #如果有两个参数，将第二个参数转换成语音
    if command_len == 2:
        mp3_buffer = edge_tts.Communicate(text=message.command[1],
                                      voice=config["voice"],
                                      rate=config["rate"],
                                      volume=config['volume'])
        await mp3_buffer.save(audio_fname=AUDIO_PATH)
        
        if replied_msg == None:
            await message.reply_voice(AUDIO_PATH)
            return await message.delete()
        else:
            await message.reply_voice(
                AUDIO_PATH, reply_to_message_id=replied_msg.id)
            return await message.delete()
    
    #如果有三个参数，查看第二个参数是否为set或list
    if command_len == 3:
        if message.command[1] == "list":
            voice_model = await edge_tts.list_voices()
            s = "ShortName               |       Gender      |           FriendlyName\r\n"
            for model in voice_model:
                if message.command[2] in model["ShortName"] or message.command[2] in model["Locale"]:
                    s += "{} | {} | {} \r\n".format(model["ShortName"],
                                                        model["Gender"],
                                                        model["FriendlyName"])
            return await message.edit_text(s)
        elif message.command[1] == "set":
            await config_set(message.command[2],config)
            return await message.edit_text(f"成功建立{message.command[2]}语音模型.")
        else:
            await message.edit_text("参数错误,使用前请查看help.")
            await asyncio.sleep(3)
            return await message.delete()


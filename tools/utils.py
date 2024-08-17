import asyncio
from pyrogram.types import Message, User
from pyrogram.enums import ParseMode 
from typing import Any, Dict

"""
字符串转整数
"""
def convert_string_to_int(s: str):
    try:
        return int(s)
    except ValueError:
        return None
 
"""
字符串转浮点数
"""
def convert_string_to_float(s: str):
    try:
        return float(s)
    except ValueError:
        return None        
    
    
"""
发送命令到服务器执行
"""     
async def basher(cmd: str, timeout: int = 10) -> Dict[str, Any]:
    return await asyncio.wait_for(execute(cmd), timeout=timeout)


"""
从服务器接收命令执行结果
"""     
async def execute(command: str) -> Dict[str, Any]:
    executor = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await executor.communicate()
    except Exception as e:
        return {'output': '', 'error': str(e)}
    else:
        return {
            'output': stdout.decode('utf-8', 'ignore').strip(),
            'error': stderr.decode('utf-8', 'ignore').strip()
        }
        
"""
获取用户全称
"""         
def get_fullname(user: User) -> str:
    if user:
        if user.last_name:
            return f"{user.first_name} {user.last_name}"
        return user.first_name

    else:
        return "匿名"
    
"""
获取发送方用户全称
"""     
def get_sender_name(msg: Message) -> str:
    if msg.from_user:
        return get_fullname(msg.from_user)
    return msg.sender_chat.title


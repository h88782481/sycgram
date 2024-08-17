import yaml
from typing import Any, Dict
from pyrogram import filters
from pyrogram.types import Message
from tools.constants import STORE_TRACE_DATA, COMMAND_YML
from tools.storage import SimpleStore

CMDS_DATA: Dict[str, Any] = yaml.full_load(open(COMMAND_YML, 'rb'))
CMDS_PREFIX = CMDS_DATA['help'].get("all_prefixes")


"""
匹配UserBot指令
"""
def command(key: str):
    # 直接访问cmd值，因为已知它一定存在
    cmd_alias = CMDS_DATA[key].get("cmd")
    # 仅当别名与key不同，才添加到cmd列表中
    cmd = [key] if cmd_alias == key else [key, cmd_alias]
    return filters.me & filters.text & filters.command(cmd, CMDS_PREFIX)

"""
正则匹配用户输入指令及参数
"""
def is_traced():
    async def func(flt, _, msg: Message):
        store = SimpleStore(auto_flush=False)
        trace_data = store.get_data(STORE_TRACE_DATA)
        if not trace_data:
            return False
        elif not trace_data.get(msg.from_user.id):
            return False
        return True
    # "data" kwarg is accessed with "flt.data" above
    return filters.incoming & filters.create(func)

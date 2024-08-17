import json
import re
from typing import Any, Dict
import yaml
from loguru import logger
from .constants import CMD_YML_REMOTE, COMMAND_YML, SYCGRAM
from .utils import basher
from tools.sessions import get_session

"""
更新配置文件
"""
def update_cmd_yml(cmd_yml: Dict[str, Any]):
    with open(COMMAND_YML, 'w', encoding='utf-8') as f:
        yaml.dump(cmd_yml, f, allow_unicode=True)

"""
修改指令前缀
"""
def modify_cmd_prefix(pfx: str) -> Dict[str, Any]:
    with open(COMMAND_YML, "rb") as f:
        cmd_yml: Dict[str, Any] = yaml.full_load(f)
        old_pfx = cmd_yml['help']['all_prefixes']
        cmd_yml['help']['all_prefixes'] = pfx
        # 读取每个指令的kv
        for every_cmd in cmd_yml.values():
            get_cmd = every_cmd['cmd']
            old_cmd = rf"[{old_pfx}]{get_cmd}"
            new_cmd = f"{pfx}{get_cmd}"
            every_cmd['format'] = re.sub(old_cmd, new_cmd, every_cmd['format'])

    # 返回已修改过所有指令前缀的一个大字典
    return cmd_yml

"""
更新指令前缀
"""
def update_cmd_prefix(pfx: str) -> None:
    try:
        cmd_yml = modify_cmd_prefix(pfx)
    except Exception as e:
        raise e
    else:
        update_cmd_yml(cmd_yml=cmd_yml)

"""
找到原别名
"""
def modify_cmd_alias(source: str, new_cmd: str) -> Dict[str, Any]:
    with open(COMMAND_YML, "rb") as f:
        cmd_yml: Dict[str, Any] = yaml.full_load(f)
        if not cmd_yml.get(source):
            raise ValueError(f"该别名 {source} 未找到")
        pfx = cmd_yml.get('help').get('all_prefixes')
        old_cmd = cmd_yml[source]['cmd']
        old_fmt = rf"[{pfx}]{old_cmd}"
        new_fmt = f"{pfx}{new_cmd}"

        cmd_yml[source]['cmd'] = new_cmd
        cmd_yml[source]['format'] = re.sub(
            old_fmt, new_fmt, cmd_yml[source]['format'])
        return cmd_yml

"""
设置新别名
"""
def update_cmd_alias(source: str, new_cmd: str) -> None:
    try:
        cmd_yml = modify_cmd_alias(source, new_cmd)
    except Exception as e:
        raise e
    else:
        update_cmd_yml(cmd_yml=cmd_yml)

"""
重置别名
"""
def reset_cmd_alias(source: str) -> None:
    try:
        cmd_yml = modify_cmd_alias(source, new_cmd=source)
    except Exception as e:
        raise e
    else:
        update_cmd_yml(cmd_yml=cmd_yml)

"""
获取所有别名
"""
def get_alias_of_cmds() -> Dict[str, str]:
    with open(COMMAND_YML, "rb") as f:
        cmd_yml: Dict[str, Dict[str, str]] = yaml.full_load(f)
        return dict(zip(cmd_yml.keys(), (v.get('cmd') for v in cmd_yml.values())))

"""
获取远程仓库配置文件
"""
async def pull_and_update_command_yml(is_update: bool = True) -> None:
    session = await get_session()
    # 读取远程command.yml
    response = await session.get(CMD_YML_REMOTE, timeout=5.5)
    if response.status_code == 200:
        data = yaml.full_load(await response.text())
        if is_update:
            with open(COMMAND_YML, "rb") as f:
                cmd_yml: Dict[str, Dict[str, str]] = yaml.full_load(f)
                data.update(cmd_yml)
        # 合并到本地，以本地为主
        update_cmd_yml(data)
    
"""
获取远程仓库版本
"""
async def get_remote_version() -> str:
    session = await get_session()
    api = "https://api.github.com/repos/h88782481/sycgram/tags"
    response = await session.get(api, timeout=5.5)
    if response.status_code == 200:
        res = await response.json()
        return res[0].get('name')
       

"""
获取本地仓库版本
"""
async def get_local_version() -> str:
    
    f = "{{json .Config.Labels}}"
    cmd = f"docker inspect ghcr.io/h88782481/{SYCGRAM}:latest -f '{f}'"
    res = await basher(cmd, timeout=10)
    if not res.get('error'):
        try:
            data = json.loads(res.get('output'))
        except Exception as e:
            raise e
        else:
            return data.get('org.opencontainers.image.version')
    raise ValueError(res.get('error'))

"""
检测是否为最新版本镜像
"""
async def is_latest_version() -> bool:
    
    remote_v = await get_remote_version()
    local_v = await get_local_version()
    logger.info(f"远程镜像版本为 {remote_v}")
    logger.info(f"本地镜像版本为 {local_v}")
    return remote_v == local_v

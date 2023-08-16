import json
import os

from functions.config import static,ADMIN
with open(os.path.join(static, 'qq_name_list.json'), 'r', encoding='utf-8') as fp:
    kid_list = json.load(fp)


async def check_perm(kid: str):
    if kid in ADMIN:
        return True
    else:
        return False


async def check_bind(kid: str):
    if kid in kid_list:
        return kid_list[kid]['qq']
    else:
        return None


async def ban_reason(id):
    with open(os.path.join(static, 'ban_list.json'), 'r', encoding='utf-8') as fp:
        ban_list = json.load(fp)
    id = str(id)
    if id in ban_list:
        return ban_list[id]
    else:
        return "请咨询开发者获得详细封禁理由."

async def set_username(kid: str, username: str):
    if str(kid) in kid_list:
        if kid_list[str(kid)]['id'] == username:
            return None
        kid_list[str(kid)]['id'] = username
        json_str = json.dumps(kid_list, indent=4, ensure_ascii=False)
        with open(os.path.join(static, 'qq_name_list.json'), 'w', encoding='utf-8') as json_file:
            json_file.write(json_str)


async def bind_qq(kid: str, qqid: int):
    if len(str(qqid)) < 6 or len(str(qqid)) > 14:
        return "你是不是在消遣洒家？"
    if str(kid) in kid_list:
        kid_list[str(kid)]['qq'] = qqid
    else:
        kid_list[str(kid)] = {'qq': qqid, 'id': ''}
    json_str = json.dumps(kid_list, indent=4, ensure_ascii=False)
    with open(os.path.join(static, 'qq_name_list.json'), 'w', encoding='utf-8') as json_file:
        json_file.write(json_str)
    qqid = str(qqid)
    return f"好耶！已将你的QQ设置为：{qqid[:2]}{'*'*(len(qqid)-2)}{qqid[-2:]}，yoooo↗"
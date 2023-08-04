import json
import os
import time
RATE = 10 #单位秒
static = r'D:\iidxCore\hoshino\modules\maimaiDX\static'
GLOBAL = True


def format_data():
    with open(os.path.join(static,'qq_name_list.json'), 'r', encoding='utf-8') as fp:
        name_list = json.load(fp)
    for qq in name_list:
        name_list[qq]={"id":name_list[qq],"last_call":0}
    json_str = json.dumps(name_list, indent=4, ensure_ascii=False)
    with open(os.path.join(static,'qq_name_list.json'), 'w', encoding='utf-8') as fp:
        fp.write(json_str)


async def check_rate(qqid):
    with open(os.path.join(static,'qq_name_list.json'), 'r', encoding='utf-8') as fp:
        name_list = json.load(fp)
    timestamp = int(time.time())
    state = False
    if GLOBAL:
        qqid = "global"
    if qqid in name_list:
        print(f"timestamp: {timestamp}")
        print(f"lastcall: {name_list[qqid]['last_call']}")
        if timestamp - name_list[qqid]['last_call'] > RATE:
            state = True
        name_list[qqid]['last_call'] = timestamp
    else:
        state = True
        name_list[qqid] = {"id": "", "last_call": timestamp}
    json_str = json.dumps(name_list, indent=4, ensure_ascii=False)
    with open(os.path.join(static,'qq_name_list.json'), 'w', encoding='utf-8') as fp:
        fp.write(json_str)
    return state


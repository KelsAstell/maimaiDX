import json
import os
import random
from time import sleep
from .. import static
import requests


def get_music_list(qqid):
    url = 'https://www.diving-fish.com/api/maimaidxprober/player/records'
    token = read_token(qqid)
    if not token['success']:
        return '找不到Token'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,es;q=0.7,ru;q=0.6,de;q=0.5,ja;q=0.4',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'jwt_token=' + token['token'],
        'Host': 'www.diving-fish.com',
        'Origin': 'https://www.diving-fish.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.diving-fish.com/maimaidx/prober/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    req = requests.get(url, headers=headers)
    if req.status_code == 200:
        json_str = json.dumps(req.json()['records'], indent=4, ensure_ascii=False)
        with open(os.path.join(static, 'data', f'{qqid}.json'), 'w', encoding='utf-8') as json_file:
            json_file.write(json_str)
            return '获取' + req.json()['username'] + '乐曲完成表成功'
    else:
        return '网络错误, 谢谢艾斯.'


def write_token_to_file(qqid,token):
    with open(os.path.join(static, 'token.json'), 'r', encoding='utf-8') as fp:
        token_list = json.load(fp)
    token_list[qqid] = token
    json_str = json.dumps(token_list, indent=4, ensure_ascii=False)
    with open(os.path.join(static, 'token.json'), 'w', encoding='utf-8') as json_file:
        json_file.write(json_str)
        return '已保存你的token'


def read_token(qqid):
    with open(os.path.join(static, 'token.json'), 'r', encoding='utf-8') as fp:
        token_list = json.load(fp)
    if str(qqid) in token_list:
        return {"success": True,"token": token_list[str(qqid)]}
    else:
        return {"success": False, "token": '0'}


def update_records_by_id(qqid, song_id, level_index):
    with open(os.path.join(static, 'data', f'{qqid}.json'), 'r', encoding='utf-8') as fp2:
        music_list = json.load(fp2)
    url = 'https://www.diving-fish.com/api/maimaidxprober/player/update_record'
    token = read_token(qqid)
    if not token['success']:
        return '无效的Token'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,es;q=0.7,ru;q=0.6,de;q=0.5,ja;q=0.4',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'jwt_token=' + token['token'],
        'Host': 'www.diving-fish.com',
        'Origin': 'https://www.diving-fish.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.diving-fish.com/maimaidx/prober/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    for song in music_list:
        if song['song_id'] == song_id and song['level_index'] == level_index:
            ach = 100.75 if random.randint(1, 10) > 4 else 101
            payload = {
                "achievements": ach,
                "ds": song['ds'],
                "dxScore": 2200 + random.randint(23, 456),
                "fc": "app" if ach == 101 else "ap",
                "fs": "fsdp",
                "level": song['level'],
                "level_index": song['level_index'],
                "level_label": song['level_label'],
                "ra": song['ra'],
                "rate": "sssp",
                "song_id": song['song_id'],
                "title": song['title'],
                "type": song['type'],
                "fit_diff": 0.1 * random.random() + song['ds'],
                "dxScore_perc": 88.72205538872205 + 5 * random.random(),
                "rank": 1
            }
            ret = requests.post(url, headers=headers, json=payload)
            if ret.status_code == 200:
                return f'{song["title"]}\n难度-{song["level_label"]}\n{ret.json()["message"]}'
            else:
                return ret
    return '你还没游玩过这个.'



#write_token_to_file(484894005, "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IkFTVEVMTCIsImV4cCI6MTY4OTMxNTk1NX0.NGNGf2bLg2Dptf4SSEkviw8qN5bYqfOPckCzAVKBY-8")

#print(get_music_list(484894005))

#update_records_by_id(484894005, 11354, 2)


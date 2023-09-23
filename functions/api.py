import json
import os
import traceback
from io import BytesIO
from typing import Union

import aiohttp

from .config import static
from .log_utils import Log

player_error = '''未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。'''

maimaiapi = 'https://www.diving-fish.com/api/maimaidxprober'


async def download_music_pictrue(id: Union[int, str]):
    try:
        if os.path.exists(file := os.path.join(static, 'mai', 'cover', f'{id}.png')):
            return file
        async with aiohttp.request('GET', f'https://www.diving-fish.com/covers/{id}.png', timeout=aiohttp.ClientTimeout(total=60)) as req:
            Log.info(f'从水鱼获取了ID:{id}的封面, 正在尝试下载到本地.')
            if req.status == 200:
                with open(os.path.join(static, 'mai', 'cover', f'{id}.png'), 'wb') as file:
                    file.write(await req.read())
                return BytesIO(await req.read())
            else:
                return os.path.join(static, 'mai', 'cover', '11000.png')
    except:
        return os.path.join(static, 'mai', 'cover', '11000.png')


async def get_music_alias(api: str, params: dict = None):
    try:
        async with aiohttp.request('GET', f'https://api.yuzuai.xyz/maimaidx/MaimaiDXAlias', params=params,
                                   timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status == 400:
                data = '参数输入错误'
            elif resp.status == 500:
                data = '别名服务器错误，请联系插件开发者'
            else:
                data = await resp.json()
    except Exception as e:
        print(f"Error:{traceback.format_exc()}")
        data = f'获取别名时发生错误，请联系BOT管理员: {type(e)}'
    return data


async def botmarket_online():
    """Botmarket通信"""
    with open('./bot_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    api = "http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid': f"{config['market_uuid']}"}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)
    Log.info(f'[Botmarket] BOT ONLINE. Welcome to Maimai!')


async def get_player_data(project: str, payload: dict):
    # with open(os.path.join(temp_path, 'best_50.json'), 'r', encoding='utf-8') as fp:
    #     b50 = json.load(fp)
    # return {'success': True, 'data': b50}
    success = False
    if project == 'best':
        p = 'player'
    elif project == 'plate':
        p = 'plate'
    else:
        return {'success': success, 'data': '不支持的查询项'}
    try:
        async with aiohttp.request('POST', f'{maimaiapi}/query/{p}', json=payload,
                                   timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status == 400:
                data = player_error
            elif resp.status == 403:
                data = '该用户不想让你看TA的游戏记录。'
            elif resp.status == 200:
                success = True
                data = await resp.json()
                if 'qq' in payload and 'username' in data:
                    with open(os.path.join(static, 'qq_name_list.json'), 'r', encoding='utf-8') as fp:
                        name_list = json.load(fp)
                    if str(payload['qq']) in name_list:
                        name_list[str(payload['qq'])]['id'] = data['username']
                    json_str = json.dumps(name_list, indent=4, ensure_ascii=False)
                    with open(os.path.join(static, 'qq_name_list.json'), 'w', encoding='utf-8') as json_file:
                        json_file.write(json_str)
            else:
                data = '未知错误，请联系BOT管理员'
    except Exception as e:
        print(f"Error:{traceback.format_exc()}")
        data = f'获取玩家数据时发生错误，请联系艾斯: {type(e)}'
    return {'success': success, 'data': data}


async def get_rating_ranking_data():
    try:
        async with aiohttp.request('GET', f'{maimaiapi}/rating_ranking',
                                   timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                data = '未知错误，请联系艾斯'
            else:
                data = await resp.json()
    except Exception as e:
        print(f"Error:{traceback.format_exc()}")
        data = f'获取排名时发生错误，请联系艾斯: {type(e)}'
    return data


async def get_xray_alias():
    try:
        async with aiohttp.request('GET', f'https://download.fanyu.site/maimai/alias.json',
                                   timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                data = '别名服务器错误，请联系艾..不对，这个要找Xray Bot开发者'
            else:
                data = await resp.json()
    except Exception as e:
        print(f"Error:{traceback.format_exc()}")
        data = f'获取别名时发生错误，请联系艾斯: {type(e)}'
    return data
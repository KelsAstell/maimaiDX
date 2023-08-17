import random
from collections import namedtuple
from copy import deepcopy
from typing import List, Optional, Tuple, Any

import aiofiles
from numpy.core.defchararray import upper
from pydantic import BaseModel, Field

from functions.api import *
from functions.config import *
from functions.log_utils import Log

cover_dir = os.path.join(static, 'mai', 'cover')


class Stats(BaseModel):

    cnt: Optional[float] = None
    diff: Optional[str] = None
    fit_diff: Optional[float] = None
    avg: Optional[float] = None
    avg_dx: Optional[float] = None
    std_dev: Optional[float] = None
    dist: Optional[List[int]] = None
    fc_dist: Optional[List[float]] = None


Notes1 = namedtuple('Notes', ['tap', 'hold', 'slide', 'brk'])
Notes2 = namedtuple('Notes', ['tap', 'hold', 'slide', 'touch', 'brk'])


class Chart(BaseModel):
    notes: Optional[Union[Any, Notes1, Notes2]]
    #notes: Optional[Union[Notes1, Notes2]]
    charter: Optional[str] = None


class BasicInfo(BaseModel):

    title: Optional[str]
    artist: Optional[str]
    genre: Optional[str]
    bpm: Optional[int]
    release_date: Optional[str]
    version: Optional[str] = Field(alias='from')
    is_new: Optional[bool]


def cross(checker: Union[List[str], List[float]], elem: Optional[Union[str, float, List[str], List[float], Tuple[float, float]]], diff: List[int]) -> Tuple[bool, List[int]]:
    ret = False
    diff_ret = []
    if not elem or elem is Ellipsis:
        return True, diff
    if isinstance(elem, List):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if __e in elem:
                diff_ret.append(_j)
                ret = True
    elif isinstance(elem, Tuple):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem[0] <= __e <= elem[1]:
                diff_ret.append(_j)
                ret = True
    else:
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem == __e:
                diff_ret.append(_j)
                ret = True
    return ret, diff_ret


def in_or_equal(checker: Union[str, int], elem: Optional[Union[str, float, List[str], List[float], Tuple[float, float]]]) -> bool:
    if elem is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem


class Music(BaseModel):

    id: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    ds: Optional[List[float]] = []
    level: Optional[List[str]] = []
    cids: Optional[List[int]] = []
    charts: Optional[List[Chart]] = []
    basic_info: Optional[BasicInfo] = None
    stats: Optional[List[Optional[Stats]]] = []
    diff: Optional[List[int]] = []


class MusicList(List[Music]):
    
    def by_id(self, music_id: str) -> Optional[Music]:
        for music in self:
            if music.id == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[Music]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self):
        return random.choice(self)

    def filter(self,
               *,
               level: Optional[Union[str, List[str]]] = ...,
               ds: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
               title_search: Optional[str] = ...,
               artist_search: Optional[str] = ...,
               charter_search: Optional[str] = ...,
               genre: Optional[Union[str, List[str]]] = ...,
               bpm: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
               type: Optional[Union[str, List[str]]] = ...,
               diff: List[int] = ...,
               ):
        new_list = MusicList()
        for music in self:
            diff2 = diff
            music = deepcopy(music)
            ret, diff2 = cross(music.level, level, diff2)
            if not ret:
                continue
            ret, diff2 = cross(music.ds, ds, diff2)
            if not ret:
                continue
            ret, diff2 = search_charts(music.charts, charter_search, diff2)
            if not ret:
                continue
            if not in_or_equal(music.basic_info.genre, genre):
                continue
            if not in_or_equal(music.type, type):
                continue
            if not in_or_equal(music.basic_info.bpm, bpm):
                continue
            if title_search is not Ellipsis and title_search.lower() not in music.title.lower():
                continue
            if artist_search is not Ellipsis and artist_search.lower() not in music.basic_info.artist.lower():
                continue
            music.diff = diff2
            new_list.append(music)
        return new_list


def search_charts(checker: List[Chart], elem: str, diff: List[int]):
    ret = False
    diff_ret = []
    if not elem or elem is Ellipsis:
        return True, diff
    for _j in (range(len(checker)) if diff is Ellipsis else diff):
        if elem.lower() in checker[_j].charter.lower():
            diff_ret.append(_j)
            ret = True
    return ret, diff_ret


async def parse_xray_data(xray_data):
    async with aiofiles.open(os.path.join(static, 'all_alias.json'), 'r', encoding='utf-8') as f:
        origin = json.loads(await f.read())
        '''
        读取原始数据进行合并操作, 防止覆盖已有数据
        '''
    for keys in xray_data:
        if len(xray_data[keys]) != 0:
            for song_id in xray_data[keys]:
                if song_id in origin:
                    if keys not in origin[song_id]["Alias"]:
                        origin[song_id]["Alias"].append(keys)
    print('别名库合并完成, yoooo↗')
    return origin


async def merge_local_alias(remote_data):
    async with aiofiles.open(os.path.join(static, 'all_alias.json'), 'r', encoding='utf-8') as f:
        origin = json.loads(await f.read())
        '''
        读取原始数据进行合并操作, 防止覆盖已有数据
        '''
    for key in remote_data:
        if key in origin:
            origin[key]["Alias"] = list(set(origin[key]["Alias"] + remote_data[key]["Alias"]))
    print('别名库合并完成, yoooo↗')
    return origin


class Alias(BaseModel):

    ID: Optional[int] = None
    Name: Optional[str] = None
    Alias: Optional[List[str]] = None


class AliasList(List[Alias]):

    def by_id(self, music_id: int) -> Optional[List[Alias]]:
        alias_list = []
        for music in self:
            if music.ID == int(music_id):
                alias_list.append(music)
        return alias_list
    
    def by_alias(self, music_alias: str) -> Optional[List[Alias]]:
        alias_list = []
        for music in self:
            if music_alias in music.Alias:
                alias_list.append(music)
        return alias_list


async def download_music_pictrue(id: Union[int, str]) -> Union[str, BytesIO]:
    try:
        if os.path.exists(file := os.path.join(static, 'mai', 'cover', f'{id}.png')):
            return file
        async with aiohttp.request('GET', f'https://www.diving-fish.com/covers/{id}.png', timeout=aiohttp.ClientTimeout(total=60)) as req:
            if req.status == 200:
                return BytesIO(await req.read())
            else:
                return os.path.join(static, 'mai', 'cover', '11000.png')
    except:
        return os.path.join(static, 'mai', 'cover', '11000.png')


async def get_music_list() -> MusicList:
    """
    获取所有数据
    """
    try:
        async with aiohttp.request('GET', 'https://www.diving-fish.com/api/maimaidxprober/music_data', timeout=aiohttp.ClientTimeout(total=30)) as obj_data:
            if obj_data.status != 200:
                print('maimaiDX曲目数据获取失败，请检查网络环境。已切换至本地暂存文件')
                async with aiofiles.open(os.path.join(static, 'music_data.json'), 'r', encoding='utf-8') as f:
                    data = json.loads(await f.read())
            else:
                data = await obj_data.json()
                print('曲目数据更新完成')
                async with aiofiles.open(os.path.join(static, 'music_data.json'), 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=4))
    except Exception:
        print(f"Error:{traceback.format_exc()}")
        print('maimaiDX曲目数据获取失败，请检查网络环境。已切换至本地暂存文件')
        async with aiofiles.open(os.path.join(static, 'music_data.json'), 'r', encoding='utf-8') as f:
            data = json.loads(await f.read())
    try:
        async with aiohttp.request('GET', 'https://www.diving-fish.com/api/maimaidxprober/chart_stats', timeout=aiohttp.ClientTimeout(total=30)) as obj_stats:
            if obj_stats.status != 200:
                print('maimaiDX数据获取错误，请检查网络环境。已切换至本地暂存文件')
                async with aiofiles.open(os.path.join(static, 'chart_stats.json'), 'r', encoding='utf-8') as f:
                    stats = json.loads(await f.read())
            else:
                stats = await obj_stats.json()
                async with aiofiles.open(os.path.join(static, 'chart_stats.json'), 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(stats, ensure_ascii=False, indent=4))
    except Exception:
        print(f"Error:{traceback.format_exc()}")
        print('maimaiDX数据获取错误，请检查网络环境。已切换至本地暂存文件')
        async with aiofiles.open(os.path.join(static, 'chart_stats.json'), 'r', encoding='utf-8') as f:
            stats = json.loads(await f.read())

    total_list: MusicList = MusicList(data)
    for num, music in enumerate(total_list):
        if music['id'] in stats['charts']:
            _stats = [_data if _data else None for _data in stats['charts'][music['id']]] if {} in stats['charts'][music['id']] else stats['charts'][music['id']]
        else:
            _stats = None
        total_list[num] = Music(stats=_stats,**total_list[num])

    return total_list


async def get_music_alias_list() -> AliasList:
    if upper(update_channel) == 'XRAY':
        data = await get_xray_alias()
    elif upper(update_channel) == 'OFFICIAL':
        data = await get_music_alias('all')
    else:
        async with aiofiles.open(os.path.join(static, 'all_alias.json'), 'r', encoding='utf-8') as f:
            data = json.loads(await f.read())
    if isinstance(data, str):
        Log.error('获取所有曲目别名信息错误，请检查网络环境。已切换至本地暂存文件')
        async with aiofiles.open(os.path.join(static, 'all_alias.json'), 'r', encoding='utf-8') as f:
            data = json.loads(await f.read())
    else:
        if upper(update_channel) == 'XRAY':
            if os.path.isfile(os.path.join(static, 'all_alias.json')):
                data = parse_xray_data(data)
                Log.info('当前使用的曲目别名信息库由 XrayBot 提供')
            else:
                data = await get_music_alias('all')
                Log.warn('你似乎是第一次使用本插件，若要启用 XrayBot 的别名库，需要重新运行一次')
        else:
            if os.path.isfile(os.path.join(static, 'all_alias.json')):
                data = await merge_local_alias(data)
                Log.info('合并本地别名数据完成')
        async with aiofiles.open(os.path.join(static, 'all_alias.json'), 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=4))
    
    total_alias_list = AliasList(data)
    for _ in range(len(total_alias_list)):
        total_alias_list[_] = Alias(ID=total_alias_list[_], Name=data[total_alias_list[_]]['Name'], Alias=data[total_alias_list[_]]['Alias'])

    return total_alias_list


async def get_local_music_list() -> MusicList:
    try:
        Log.info(f'已跳过曲目数据更新')
        async with aiofiles.open(os.path.join(static, 'music_data.json'), 'r', encoding='utf-8') as f:
            data = json.loads(await f.read())
    except Exception:
        print(f"Error:{traceback.format_exc()}")
        Log.error('本地曲目文件读取失败')
    try:
        async with aiofiles.open(os.path.join(static, 'chart_stats.json'), 'r', encoding='utf-8') as f:
            stats = json.loads(await f.read())
    except Exception:
        print(f"Error:{traceback.format_exc()}")
        Log.error('本地曲目统计数据读取失败')

    total_list: MusicList = MusicList(data)
    for num, music in enumerate(total_list):
        if music['id'] in stats['charts']:
            _stats = stats['charts'][music['id']]
        else:
            _stats = None
        total_list[num] = Music(stats=_stats, **total_list[num])

    return total_list


async def get_local_music_alias_list() -> AliasList:
    async with aiofiles.open(os.path.join(static, 'all_alias.json'), 'r', encoding='utf-8') as f:
        data = json.loads(await f.read())
    total_alias_list = AliasList(data)
    for _ in range(len(total_alias_list)):
        total_alias_list[_] = Alias(ID=total_alias_list[_], Name=data[total_alias_list[_]]['Name'], Alias=data[total_alias_list[_]]['Alias'])

    return total_alias_list


class MaiMusic:

    total_list: Optional[MusicList]

    def __init__(self) -> None:
        """
        封装所有曲目信息以及猜歌数据，便于更新
        """

    async def get_music(self) -> MusicList:
        """
        获取所有曲目数据
        """
        self.total_list = await get_music_list() if upper(update_channel)!='OFFLINE' else await get_local_music_list()

    async def get_music_alias(self) -> AliasList:
        """
        获取所有曲目别名
        """
        self.total_alias_list = await get_music_alias_list() if upper(update_channel)!='OFFLINE' else await get_local_music_alias_list()


mai = MaiMusic()

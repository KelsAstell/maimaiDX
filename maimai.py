import asyncio
import re
from random import sample
from string import ascii_uppercase, digits

import aiofiles
from nonebot import NoneBot, on_websocket_connect

from hoshino import Service, priv
from hoshino.service import sucmd
from hoshino.typing import CommandSession, CQEvent, MessageSegment
from numpy.core.defchararray import upper
from . import *
from .libraries.image import *
from .libraries.maimaidx_api_data import *
from .libraries.maimaidx_music import alias, guess, mai
from .libraries.maimaidx_project import *
from .libraries.tool import *
from .libraries.music_alias import *
from .libraries.random_reply import *
from .libraries.one_key_ap import *
from hoshino.rate_limit import check_rate



SV_HELP = '请使用 iiDX? 查看帮助'
sv = Service('iiDX', manage_priv=priv.ADMIN, enable_on_default=False, help_=SV_HELP)
sv_help = os.path.join(static, 'maimaidx_help.png')


def song_level(ds1: float, ds2: float, stats1: str = None, stats2: str = None) -> list:
    result = []
    music_data = mai.total_list.filter(ds=(ds1, ds2))
    if stats1:
        if stats2:
            stats1 = stats1 + ' ' + stats2
            stats1 = stats1.title()
        for music in sorted(music_data, key=lambda i: int(i.id)):
            for i in music.diff:
                result.append((music.id, music.title, music.ds[i], diffs[i], music.level[i]))
    else:
        for music in sorted(music_data, key=lambda i: int(i.id)):
            for i in music.diff:
                result.append((music.id, music.title, music.ds[i], diffs[i], music.level[i]))
    return result


@on_websocket_connect
async def get_music(event: CQEvent):
    """
    bot启动时开始获取所有数据
    """
    log.info('正在加载所有曲目信息')
    await mai.get_music()
    log.info('正在加载曲目别名信息')
    await mai.get_music_alias()
    log.info('初始化完成, yoooo↗')
    mai.guess()


@sv.on_prefix(['嗦梨进度', '嗦🍐进度', '🍐进度'])
async def let_me_solips(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    id = '11353'
    for i in ev.message:
        if i.type == 'at' and i.data['qq'] != 'all':
            qqid = int(i.data['qq'])
    payload = {'qq': qqid}
    msg = await solips_play_data(payload, id)
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['更新token', 'settoken', '设置token'])
async def upd_token(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    args: str = ev.message.extract_plain_text().strip()
    args_list = args.split("=")
    if len(args_list) > 1:
        if not priv.check_priv(ev, priv.SUPERUSER):
            await bot.send(ev, '只有管理员能修改他人Token', at_sender=True)
            return None
        await bot.send(ev, write_token_to_file(args_list[0],args_list[1]), at_sender=True)
        return None
    for i in ev.message:
        if i.type == 'at' and i.data['qq'] != 'all':
            qqid = int(i.data['qq'])
    await bot.send(ev, write_token_to_file(qqid,args_list[0]), at_sender=True)
    return None


@sv.on_prefix(['获取游玩记录', '游玩记录'])
async def get_records(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    for i in ev.message:
        if i.type == 'at' and i.data['qq'] != 'all':
            qqid = int(i.data['qq'])
    await bot.send(ev, get_music_list(qqid), at_sender=True)
    
    
@sv.on_prefix(['一键AP', '1keyap'])
async def onekey_ap(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    args: str = ev.message.extract_plain_text().strip()
    args_list = args.split("-")
    dic = {"master":3,"mst":3,"advanced":1,"adv":1,"basic":0,"bas":0,"exp":2,"expert":2,"remaster":4,"rem":4}
    for i in ev.message:
        if i.type == 'at' and i.data['qq'] != 'all':
            qqid = int(i.data['qq'])
    if os.path.exists(os.path.join(static, 'data', f'{qqid}.json')):
        await bot.send(ev, update_records_by_id(qqid, int(args_list[0]), dic[args_list[1]]), at_sender=True)
    

@sv.on_fullmatch(['iiDX?', 'iidx?'])
async def dx_help(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    await bot.send(ev, MessageSegment.image(image_to_base64(sv_help)), at_sender=True)


@sv.on_rex(r'.*mai.*什么最新最热')
async def random_day_song(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    await bot.send(ev, await draw_music_info(mai.total_list.random()))


@sv.on_fullmatch(['重载别名','重载别名库','重载抽象别名'])
async def reload_alias(bot: NoneBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return None
    await mai.get_music_alias()
    
@sv.on_fullmatch(['重载乐曲','重载乐曲库','重载抽象乐曲'])
async def reload_music(bot: NoneBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return None
    await mai.get_music()
    

@sv.on_fullmatch(['极极国王进度'])
async def jiji_king(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    if random.randint(1,10)%2:
        await bot.send(ev, f'你已经是极极国王了', at_sender=True)
    else:
        await bot.send(ev, f'你先别急, 让我先急')

@sv.on_suffix(['神进度?'])
async def shen(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    name: str = ev.message.extract_plain_text().strip().lower()
    if random.randint(1,10)%2:
        await bot.send(ev, f'你已经是{name}神了！', at_sender=True)
    else:
        await bot.send(ev, f'你还不是{name}神捏, 继续努力哦')


@sv.on_suffix(['是什么抽象歌', '是啥抽象歌'])
async def what_song(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    name: str = ev.message.extract_plain_text().strip().lower()
    data = mai.total_alias_list.by_alias(name)
    if not data:
        await bot.finish(ev, randomNotFound(), at_sender=True)
    if len(data) != 1:
        msg = f'找到{len(data)}个相同别名的曲目：\n'
        for songs in data:
            msg += f'{songs.ID}：{songs.Name}\n'
        await bot.finish(ev, msg.strip(), at_sender=True)

    music = mai.total_list.by_id(str(data[0].ID))
    await bot.send(ev, '您要找的是不是：' + (await draw_music_info(music)), at_sender=True)


@sv.on_suffix(['有什么抽象别称', '有什么抽象别名'])
async def how_song(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    name: str = ev.message.extract_plain_text().strip().lower()
    
    alias = mai.total_alias_list.by_alias(name)
    if not alias:
        if name.isdigit():
            alias_id = mai.total_alias_list.by_id(name)
            if not alias_id:
                await bot.finish(ev, randomNotFound(), at_sender=True)
            else:
                alias = alias_id
        else:
            await bot.finish(ev, randomNotFound(), at_sender=True)
    if len(alias) != 1:
        msg = []
        for songs in alias:
            alias_list = '\n'.join(songs.Alias)
            msg.append(f'ID：{songs.ID}\n{alias_list}')
        await bot.finish(ev, f'找到{len(alias)}个相同别名的曲目：\n' + '\n======\n'.join(msg), at_sender=True)
    
    if len(alias[0].Alias) == 1:
        await bot.finish(ev, '挠头, 这玩意还没有别名', at_sender=True)

    msg = f'该曲目有以下别名：\nID：{alias[0].ID}\n'
    msg += '\n'.join(alias[0].Alias)
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['ib50', 'ib40', '我的舞萌芯', '我的舞萌心'])
async def best_50(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    args: str = ev.message.extract_plain_text().strip()
    for i in ev.message:
        if i.type == 'at' and i.data['qq'] != 'all':
            qqid = int(i.data['qq'])
    if args:
        payload = {'username': args}
        if upper(payload['username']) == 'EMOBOT':
            payload = {'username': 'ASTELL'}
    else:
        payload = {'qq': qqid}
    payload['b50'] = True
    await bot.send(ev, await generate(payload), at_sender=True)


@sv.on_prefix(['info', 'INFO'])
async def maiinfo(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    id = '1'
    args: str = ev.message.extract_plain_text().strip()
    for i in ev.message:
        if i.type == 'at' and i.data['qq'] != 'all':
            qqid = int(i.data['qq'])
    if not args:
        await bot.finish(ev, '你要查啥?' if random.randint(1,10)%2 else '查不了空气', at_sender=True)
    payload = {'qq': qqid}
    if mai.total_list.by_id(args):
        id = args
    elif by_t := mai.total_list.by_title(args):
        id = by_t.id
    else:
        alias = mai.total_alias_list.by_alias(args)
        if not alias:
            await bot.finish(ev, '没找到捏', at_sender=True)
        elif len(alias) != 1:
            msg = f'找到相同别名的曲目，请使用以下ID查询：\n'
            for songs in alias:
                msg += f'{songs.ID}：{songs.Name}\n'
            await bot.finish(ev, msg.strip(), at_sender=True)
        else:
            id = str(alias[0].ID)
    play_data = await music_play_data(payload, id)
    pic = play_data["msg"]
    await bot.send(ev, pic, at_sender=True)
    abs_data = is_abstract(id)
    if abs_data["abstract"] and play_data['sss']:
        await asyncio.sleep(4)
        await bot.send(ev, abs_data["reply"], at_sender=True)



@sv.on_prefix(['global'])
async def globinfo(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    args: str = ev.message.extract_plain_text().strip()
    if not args:
        await bot.finish(ev, '请输入曲目id或曲名', at_sender=True)
    if args[0] not in '绿黄红紫白':
        level_index = 3
    else:
        level_index = '绿黄红紫白'.index(args[0])
        args = args[1:].strip()
        if not args:
            await bot.finish(ev, '请输入曲目id或曲名', at_sender=True)
    if mai.total_list.by_id(args):
        id = args
    elif by_t := mai.total_list.by_title(args):
        id = by_t.id
    else:
        alias = mai.total_alias_list.by_alias(args)
        if not alias:
            await bot.finish(ev, '未找到曲目', at_sender=True)
        elif len(alias) != 1:
            msg = f'找到相同别名的曲目，请使用以下ID查询：\n'
            for songs in alias:
                msg += f'{songs.ID}：{songs.Name}\n'
            await bot.finish(ev, msg.strip(), at_sender=True)
        else:
            id = str(alias[0].ID)
    music = mai.total_list.by_id(id)
    if not music.stats:
        await bot.finish(ev, '该乐曲还没有统计信息', at_sender=True)
    if len(music.ds) == 4 and level_index == 4:
        await bot.finish(ev, '该乐曲没有这个等级', at_sender=True)
    if not music.stats[level_index]:
        await bot.finish(ev, '该等级没有统计信息', at_sender=True)
    stats = music.stats[level_index]
    await bot.send(ev, await music_global_data(music, level_index) + f'''
游玩次数：{round(stats.cnt)}
拟合难度：{stats.fit_diff:.2f}
平均达成率：{stats.avg:.2f}%
平均 DX 分数：{stats.avg_dx:.1f}
谱面成绩标准差：{stats.std_dev:.2f}''', at_sender=True)


@sv.on_rex(r'^([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉熊華华爽舞霸宙星])([極极将舞神者]舞?)抽象进度\s?(.+)?')
async def plate_process(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    match: Match[str] = ev['match']
    nickname = ''
    for i in ev.message:
        if i.type == 'at' and i.data['qq'] != 'all':
            qqid = int(i.data['qq'])

    if f'{match.group(1)}{match.group(2)}' == '真将':
        await bot.finish(ev, '真系没有真将哦', at_sender=True)
    elif match.group(3):
        nickname = match.group(3)
        payload = {'username': match.group(3).strip()}
    else:
        payload = {'qq': qqid}

    if qqid != ev.user_id:
        nickname = (await bot.get_stranger_info(user_id=qqid))['nickname']
    
    if match.group(1) in ['霸', '舞']:
        payload['version'] = list(set(version for version in list(plate_to_version.values())[:-9]))
    elif match.group(1) == '真':
        payload['version'] = list(set(version for version in list(plate_to_version.values())[0:2]))
    else:
        payload['version'] = [plate_to_version[match.group(1)]]

    data = await player_plate_data(payload, match, nickname)
    await bot.send(ev, data, at_sender=True)


@sv.on_rex(r'^([0-9]+\+?)抽象分数列表\s?([0-9]+)?\s?(.+)?')
async def level_achievement_list(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    match: Match[str] = ev['match']
    nickname = ''
    for i in ev.message:
        if i.type == 'at' and i.data['qq'] != 'all':
            qqid = int(i.data['qq'])
        
    if match.group(1) not in levelList:
        await bot.finish(ev, '无此等级', at_sender=True)
    elif match.group(3):
        nickname = match.group(3)
        payload = {'username': match.group(3).strip()}
    else:
        payload = {'qq': qqid}

    if qqid != ev.user_id:
        nickname = (await bot.get_stranger_info(user_id=qqid))['nickname']

    payload['version'] = list(set(version for version in plate_to_version.values()))

    data = await level_achievement_list_data(payload, match, nickname)
    await bot.send(ev, data, at_sender=True)


@sv.on_prefix(['我有多菜','他有多菜','她有多菜','祂有多菜'])
async def rating_ranking(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    for i in ev.message:
        if i.type == 'at' and i.data['qq'] != 'all':
            qqid = int(i.data['qq'])
    if not check_rate(str(qqid)):
        return None
    args: str = ev.message.extract_plain_text().strip()
    if args:
        name = args.lower()
    else:
        query = name_linked(str(qqid))
        print(int(ev.user_id))
        print(query)
        if query["success"]:
            data = await rating_ranking_data(query["username"].lower(), 1)
            await bot.send(ev, data, at_sender=True)
            return None
        return None
    page = 1
    if args.isdigit():
        page = int(args)
    else:
        name = args.lower()
    data = await rating_ranking_data(name, page)
    await bot.send(ev, data, at_sender=True)


@sv.on_prefix(['rapk', 'ra比较', '仇人对战'])
async def rating_compare(bot: NoneBot, ev: CQEvent):
    qqid1 = ev.user_id
    if not check_rate(qqid1):
        return None
    qqid2 = ''
    for i in ev.message:
        if i.type == 'at' and i.data['qq'] != 'all':
            qqid2 = int(i.data['qq'])
    args: str = ev.message.extract_plain_text().strip()
    usernames = args.split()
    if len(usernames) == 2 and not usernames[0] == usernames[1]:
        name1 = usernames[0].lower()
        name2 = usernames[1].lower()
        data = await rating_pk(name1, name2)
        await bot.send(ev, data, at_sender=True)
    elif len(usernames) == 1:
        if not qqid2:
            query = name_linked(str(ev.user_id))
            if query["success"]:
                name1 = usernames[0].lower()
                name2 = query["username"].lower()
                data = await rating_pk(name1, name2)
                await bot.send(ev, data, at_sender=True)
            else:
                return None
        else:
            query = name_linked(str(qqid2))
            if query["success"]:
                name1 = usernames[0].lower()
                name2 = query["username"].lower()
                data = await rating_pk(name1, name2)
                await bot.send(ev, data, at_sender=True)
            else:
                return None
    elif qqid1 and qqid2:
        query1 = name_linked(str(qqid1))
        query2 = name_linked(str(qqid2))
        if query1["success"] and query2["success"]:
            name1 = query1["username"].lower()
            name2 = query2["username"].lower()
            data = await rating_pk(name1, name2)
            await bot.send(ev, data, at_sender=True)
        else:
            return None
    else:
        return None


@sv.on_prefix(['你有多菜'])
async def rating_ranking(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    await bot.send(ev, '我超，我是乌蒙大神！\n截止至 2077年02月30日11时45分14秒\n爷在火猫网站未注册用户ra排行第1\n超过了100%的玩家')


async def guess_music_loop(bot: NoneBot, ev: CQEvent):
    gid = str(ev.group_id)
    _guess = guess.Group[gid]['object']
    if ev.group_id not in guess.config['enable'] or _guess.is_end:
        return
    await bot.send(ev,MessageSegment.image(_guess.b64image))
    await give_answer(bot, ev)


async def give_answer(bot: NoneBot, ev: CQEvent):
    gid = str(ev.group_id)
    await asyncio.sleep(30)
    _guess = guess.Group[gid]['object']
    if ev.group_id not in guess.config['enable'] or _guess.is_end:
        return
    _guess.is_end = True
    guess.end(gid)
    msg = f'''答案是：
{await draw_music_info(_guess.music)}'''
    await bot.finish(ev, msg)


@sv.on_fullmatch('抽象猜歌','猜抽象歌','曹冲称象','猜歌抽象')
async def guess_music(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    if not check_rate(str(qqid)):
        return None
    gid = str(ev.group_id)
    if ev.group_id not in guess.config['enable']:
        await bot.finish(ev, '该群已关闭猜歌功能，开启请输入 开启抽象猜歌')
    if gid in guess.Group:
        return None
    guess.add(gid)
    await mai.start()
    guess.start(gid, mai, 0)
    await guess_music_loop(bot, ev)


@sv.on_message()
async def guess_music_solve(bot: NoneBot, ev: CQEvent):
    gid = str(ev.group_id)
    if gid not in guess.Group:
        return
    ans: str = ev.message.extract_plain_text().strip().lower()
    _guess = guess.Group[gid]['object']
    if ans.lower() in _guess.answer:
        _guess.is_end = True
        guess.end(gid)
        msg = f'''猜对了！
{await draw_music_info(_guess.music)}'''
        await bot.finish(ev, msg, at_sender=True)


@sv.on_fullmatch('重置抽象猜歌')
async def reset_guess(bot: NoneBot, ev: CQEvent):
    gid = str(ev.group_id)
    if not priv.check_priv(ev, priv.ADMIN):
        msg = '仅允许管理员开启'
    elif gid in guess.Group:
        msg = '已重置该群猜歌'
        guess.end(gid)
    else:
        msg = '该群未处在猜歌状态'
    await bot.send(ev, msg)


@sv.on_fullmatch('开启抽象猜歌')
async def guess_on(bot: NoneBot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.ADMIN):
        return None
    elif gid in guess.config['enable']:
        msg = '已开启猜歌功能'
    else:
        guess.guess_change(gid, True)
        msg = '已开启猜歌功能'

    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch('关闭抽象猜歌')
async def guess_off(bot: NoneBot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.ADMIN):
        return None
    elif gid in guess.config['disable']:
        msg = '已关闭猜歌功能'
    else:
        guess.guess_change(gid, False)
        if str(gid) in guess.Group:
            guess.end(str(gid))
        msg = '已关闭猜歌功能'

    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix('更新歌曲名称','更改歌曲名称')
async def update_name(bot: NoneBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return None
    text = str(ev.message.extract_plain_text().strip())
    text = text.split("-")
    if len(text) > 1:
        await bot.send(ev, updateAlias('change_name',int(text[0]),text[1]))
        await mai.get_music_alias()
    else:
        await bot.send(ev, '用法: 更改歌曲名称 ID-名字')


@sv.on_prefix('批量删除抽象别名','删除抽象别名')
async def batch_delete(bot: NoneBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return None
    text = str(ev.message.extract_plain_text().strip())
    text = text.split("-")
    if len(text) > 1:
        await bot.send(ev, updateAlias('batch_delete',int(text[0]),text[1]))
        await mai.get_music_alias()
    else:
        await bot.send(ev, '用法: 批量删除抽象别名 ID-别名1/别名2..')


@sv.on_prefix('批量添加抽象别名','添加抽象别名')
async def batch_add(bot: NoneBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return None
    text = str(ev.message.extract_plain_text().strip())
    text = text.split("-")
    await bot.send(ev, su_batch_add_alias(int(text[0]), text[1]))
    await mai.get_music_alias()


@sv.on_prefix('添加新歌','添加最新最热','添加最旧最冷')
async def zxzr(bot: NoneBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return None
    text = str(ev.message.extract_plain_text().strip())
    text = text.split("-")
    if len(text) == 2:
        await bot.send(ev, su_add_new(int(text[0]), text[1]))
        await mai.get_music_alias()
    else:
        await bot.send(ev, '用法: 添加最新最热 ID-歌曲名')

@sv.on_prefix('kohad-','KohaD-')
async def zxzr(bot: NoneBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return None
    text = str(ev.message.extract_plain_text().strip())
    await bot.send(ev, kohd(text))
    await mai.get_music_alias()

@sv.on_fullmatch('同步别名库','联网更新别名库')
async def upd_alias_list(bot: NoneBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return None
    await bot.send(ev, await merge_remote_alias())
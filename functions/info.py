import time
from re import Match
from typing import Dict

from .best_50 import *
from .api import *
from .music import Music, download_music_pictrue, mai, RaMusic
from .random_reply import *

with open(os.path.join(static, 'abstract_reply.json'), 'r', encoding='utf-8') as f:
    abstract_list = json.load(f)

SONGS_PER_PAGE = 25
fcl = {'fc': 'FC', 'fcp': 'FCp', 'ap': 'AP', 'app': 'APp'}
fsl = {'fs': 'FS', 'fsp': 'FSp', 'fsd': 'FSD', 'fsdp': 'FSDp'}
level_labels = ['绿', '黄', '红', '紫', '白']
game_names = ['音乐世界', '冰与火', '自己', '古树旋律', '中二节奏', '舞立方Show', 'e舞成名', '跳舞的线', '搓盘子',
              '艾斯', '杨辣子', 'Arcaea', 'Dynamix', 'hso..呸, osu!', 'KohaD', 'Beatmania IIDX', 'jubeat', '太鼓达人',
              'WACCA', '喵斯快跑', '同步音律喵赛克', 'Phi', '节奏大师']
realAchievementList = {}
for acc in [i / 10 for i in range(10, 151)]:
    realAchievementList[f'{acc:.1f}'] = generateAchievementList(acc)
plate_to_version = {
    '初': 'maimai',
    '真': 'maimai PLUS',
    '超': 'maimai GreeN',
    '檄': 'maimai GreeN PLUS',
    '橙': 'maimai ORANGE',
    '暁': 'maimai ORANGE PLUS',
    '晓': 'maimai ORANGE PLUS',
    '桃': 'maimai PiNK',
    '櫻': 'maimai PiNK PLUS',
    '樱': 'maimai PiNK PLUS',
    '紫': 'maimai MURASAKi',
    '菫': 'maimai MURASAKi PLUS',
    '堇': 'maimai MURASAKi PLUS',
    '白': 'maimai MiLK',
    '雪': 'MiLK PLUS',
    '輝': 'maimai FiNALE',
    '辉': 'maimai FiNALE',
    '熊': 'maimai でらっくす',
    '華': 'maimai でらっくす PLUS',
    '华': 'maimai でらっくす PLUS',
    '爽': 'maimai でらっくす Splash',
    '煌': 'maimai でらっくす Splash PLUS',
    '宙': 'maimai でらっくす UNiVERSE',
    '星': 'maimai でらっくす UNiVERSE PLUS',
    'fes': 'maimai でらっくす FESTiVAL',
    'fesp': 'maimai でらっくす FESTiVAL PLUS'
}

maimaidir = os.path.join(static, 'mai', 'pic')

SIYUAN = os.path.join(static, 'SourceHanSansSC-Bold.otf')
TBFONT = os.path.join(static, 'Torus SemiBold.otf')
category = {
    '流行&动漫': 'anime',
    '舞萌': 'maimai',
    'niconico & VOCALOID': 'niconico',
    '东方Project': 'touhou',
    '其他游戏': 'game',
    '绿洲计划': 'oasis',
    'homo': 'homo',
    '音击&中二节奏': 'ongeki'
}
ABSTRACT_REPLY = os.path.join(static, 'abstract_reply.json')
with open(ABSTRACT_REPLY, 'r', encoding='utf-8') as fp:
    abstract_reply = json.load(fp)
nls_data = ["我超，", "woc，", "好耶，", "6，"]


async def draw_music_info(music: Music):
    im = Image.open(os.path.join(maimaidir, 'music_bg.png')).convert('RGBA')
    genre = Image.open(os.path.join(maimaidir, f'music-{category[music.basic_info.genre]}.png'))
    cover = Image.open(await download_music_pictrue(music.id)).resize((360, 360))
    ver = Image.open(os.path.join(maimaidir, f'{music.type}.png')).resize((94, 35))
    line = Image.new('RGBA', (400, 2), (255, 255, 255, 255))

    im.alpha_composite(genre, (150, 170))
    im.alpha_composite(cover, (170, 260))
    im.alpha_composite(ver, (435, 585))
    im.alpha_composite(line, (150, 710))

    dr = ImageDraw.Draw(im)
    tb = DrawText(dr, TBFONT)
    sy = DrawText(dr, SIYUAN)

    tb.draw(200, 195, 24, music.id, anchor='mm')
    sy.draw(410, 195, 22, music.basic_info.genre, anchor='mm')
    sy.draw_partial_opacity(350, 660, 30, music.title, 1, anchor='mm')
    sy.draw_partial_opacity(350, 690, 12, music.basic_info.artist, 1, anchor='mm')
    sy.draw_partial_opacity(150, 725, 15, f'Version: {music.basic_info.version}', 1, anchor='lm')
    sy.draw_partial_opacity(550, 725, 15, f'BPM: {music.basic_info.bpm}', 1, anchor='rm')
    for n, i in enumerate(list(map(str, music.ds))):
        if n == 4:
            color = (195, 70, 231, 255)
        else:
            color = (255, 255, 255, 255)
        tb.draw(160 + 95 * n, 814, 25, i, color, 'mm')
    sy.draw(350, 980, 14, f'Modified by Kels_Astell | Generated by {BOTNAME}', (255, 255, 255, 255), 'mm', 1,
            (159, 81, 220, 255))

    return im


async def solips_play_data(payload: dict):
    payload['version'] = list(set(version for version in plate_to_version.values()))
    data = await get_player_data('plate', payload)

    if isinstance(data, str):
        return data

    player_data: list[dict[str, Union[float, str, int]]] = []
    for i in data['data']['verlist']:
        if i['id'] == 11353:
            player_data.append(i)
    if not player_data:
        return '你还没有嗦🍐'
    total_ra = 0
    msg = "嗦梨统计:\n"
    player_data.sort(key=lambda a: a['level_index'])
    music = mai.total_list.by_id('11353')
    lv_dict = {0: "Basic", 1: "Advanced", 2: "Expert", 3: "Master", 4: "Re:Master"}
    for _data in player_data:
        ds: float = music.ds[_data['level_index']]
        lv: int = _data['level_index']
        ra, rate = computeRa(ds, _data['achievements'], israte=True)
        msg += f"{lv_dict[lv]}难度{rate.replace('p', '+')}, 恰了{ra}分.\n"
        if ra >= 321:
            msg += "我超, 嗦梨大神!\n"
        total_ra += ra

    return msg + f"你的嗦梨总共毛到了{total_ra}分."


async def music_play_data(payload: dict, songs: str):
    payload['version'] = list(set(version for version in plate_to_version.values()))
    data = await get_player_data('plate', payload)
    if isinstance(data, str):
        return data
    # print(data)
    player_data: list[dict[str, Union[float, str, int]]] = []
    for i in data['data']['verlist']:
        if i['id'] == int(songs):
            player_data.append(i)
    player_data.sort(key=lambda a: a['level_index'])
    music = mai.total_list.by_id(songs)

    im = Image.open(os.path.join(maimaidir, 'info_bg.png')).convert('RGBA')
    genre = Image.open(os.path.join(maimaidir, f'info-{category[music.basic_info.genre]}.png'))
    cover = Image.open(await download_music_pictrue(music.id)).resize((210, 210))
    version = Image.open(os.path.join(maimaidir, f'{music.type}.png')).resize((108, 40))

    dr = ImageDraw.Draw(im)
    tb = DrawText(dr, TBFONT)
    sy = DrawText(dr, SIYUAN)

    im.alpha_composite(genre, (45, 145))
    im.alpha_composite(cover, (69, 184))
    im.alpha_composite(version, (725, 360))

    tb.draw(430, 167, 20, music.id, anchor='mm')
    sy.draw(610, 167, 20, music.basic_info.genre, anchor='mm')
    sy.draw(295, 225, 30, music.title, anchor='lm')
    sy.draw(295, 260, 15, f'作曲: {music.basic_info.artist}', anchor='lm')
    sy.draw(295, 310, 15, f'BPM: {music.basic_info.bpm}', anchor='lm')
    sy.draw(295, 330, 15, f'版本: {music.basic_info.version}', anchor='lm')

    y = 120
    TEXT_COLOR = [(14, 117, 54, 255), (199, 69, 12, 255), (175, 0, 50, 255), (103, 20, 141, 255), (103, 20, 141, 255)]
    sss = False
    for _data in player_data:
        ds: float = music.ds[_data['level_index']]
        lv: int = _data['level_index']
        ra, rate = computeRa(ds, _data['achievements'], israte=True)
        if lv >= 3 and rate in ["SSSp", "SSS"] and songs in abstract_list:
            sss = True
        rank = Image.open(os.path.join(maimaidir, f'UI_TTR_Rank_{rate}.png')).resize((120, 57))
        im.alpha_composite(rank, (430, 515 + y * lv))
        if _data['fc']:
            fc = Image.open(os.path.join(maimaidir, f'UI_CHR_PlayBonus_{fcl[_data["fc"]]}.png')).resize((76, 76))
            im.alpha_composite(fc, (575, 511 + y * lv))
        if _data['fs']:
            fs = Image.open(os.path.join(maimaidir, f'UI_CHR_PlayBonus_{fsl[_data["fs"]]}.png')).resize((76, 76))
            im.alpha_composite(fs, (650, 511 + y * lv))

        p, s = f'{_data["achievements"]:.4f}'.split('.')
        r = tb.get_box(p, 36)
        tb.draw(90, 545 + y * lv, 30, str(ds), anchor='mm')
        tb.draw(200, 567 + y * lv, 36, p, TEXT_COLOR[lv], 'ld')
        tb.draw(200 + r[2], 565 + y * lv, 30, f'.{s}%', TEXT_COLOR[lv], 'ld')
        tb.draw(790, 545 + y * lv, 30, ra, TEXT_COLOR[lv], 'mm')

    sy.draw(450, 1180, 20, f'Modified by Kels_Astell | Generated by {BOTNAME}', (159, 81, 220, 255), 'mm', 2,
            (255, 255, 255, 255))
    if songs in abstract_list:
        comment = random.choice(abstract_list[str(songs)])
    else:
        comment = ''
    return {"sss": sss, "msg": im, "comment": comment, "song_name": music.title}


def getCharWidth(o) -> int:
    widths = [
        (126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
        (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1), (8426, 0), (9000, 1), (9002, 2), (11021, 1),
        (12350, 2), (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1), (55203, 2), (63743, 1),
        (64106, 2), (65039, 1), (65059, 0), (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
        (120831, 1), (262141, 2), (1114109, 1),
    ]
    if o == 0xe or o == 0xf:
        return 0
    for num, wid in widths:
        if o <= num:
            return wid
    return 1


def coloumWidth(s: str) -> int:
    res = 0
    for ch in s:
        res += getCharWidth(ord(ch))
    return res


def changeColumnWidth(s: str, len: int) -> str:
    res = 0
    sList = []
    for ch in s:
        res += getCharWidth(ord(ch))
        if res <= len:
            sList.append(ch)
    return ''.join(sList)


async def music_play_data_dev(qqid: int, songs: str):
    data = await get_player_data_dev(qqid=qqid)
    if isinstance(data, str):
        return data
    player_data: list[dict[str, Union[float, str, int]]] = []
    #print(data)
    for i in data['data']['records']:
        if i['song_id'] == int(songs):
            player_data.append(i)
    # if not player_data:
    #     return '您未游玩该曲目'

    DXSTAR_DEST = [0, 540, 530, 520, 510, 500]

    player_data.sort(key=lambda a: a['level_index'])
    music = mai.total_list.by_id(songs)

    im = Image.open(os.path.join(maimaidir, 'info_bg_2.png')).convert('RGBA')
    dxstar = [Image.open(os.path.join(maimaidir, f'UI_RSL_DXScore_Star_0{_ + 1}.png')).resize((20, 20)) for _ in range(3)]

    dr = ImageDraw.Draw(im)
    tb = DrawText(dr, TBFONT)
    sy = DrawText(dr, SIYUAN)

    im.alpha_composite(Image.open(await download_music_pictrue(music.id)).resize((235, 235)), (65, 165))
    im.alpha_composite(Image.open(os.path.join(maimaidir, f'{music.basic_info.version}.png')).resize((300, 144)), (550, 265))
    im.alpha_composite(Image.open(os.path.join(maimaidir, f'{music.type}.png')).resize((80, 30)), (65, 368))

    color = (140, 44, 213, 255)
    title = music.title
    if coloumWidth(title) > 35:
        title = changeColumnWidth(title, 34) + '...'
    sy.draw(320, 185, 24, f"{title}", color, 'lm')
    sy.draw(320, 220, 18, music.basic_info.artist, color, 'lm')
    tb.draw(320, 245, 20, f'BPM: {music.basic_info.bpm}', color, 'lm')
    tb.draw(320, 270, 18, f'ID: {music.id}', color, 'lm')
    tb.draw(320, 318, 18, f'Player Info', color, 'lm')
    tb.draw(320, 343, 18, f'Name: {data["data"]["nickname"]}', color, 'lm')
    tb.draw(320, 368, 18, f'Rating: {data["data"]["rating"]}', color, 'lm')
    #sy.draw(500, 380, 16, music.basic_info.genre, color, 'mm')

    y = 120
    TEXT_COLOR = [(14, 117, 54, 255), (199, 69, 12, 255), (175, 0, 50, 255), (103, 20, 141, 255),
                  (103, 20, 141, 255)]
    sss = False
    plate_type = plate_ver = ""
    for _data in player_data:
        ds: float = _data['ds']
        lv: int = _data['level_index']
        dxscore = _data['dxScore']
        ra, rate = computeRa(ds, _data['achievements'], israte=True)
        #print(len(player_data))
        if lv >= 3:
            plate_type = []
            sss = False
            if _data['fc'] in ["ap", "app"]:
                plate_type.append("神")
            if _data['fc'] in ["fc", "fcp"]:
                plate_type.append("極")
            if rate in ["SSSp", "SSS"]:
                if songs in abstract_list:
                    sss = True
                plate_type.append("将")
        rank = Image.open(os.path.join(maimaidir, f'UI_TTR_Rank_{rate}.png')).resize((120, 57))
        im.alpha_composite(rank, (358, 518 + y * lv))

        _dxscore = sum(music.charts[lv].notes) * 3
        diff_sum_dx = dxscore / _dxscore * 100
        dxtype, dxnum = dxScore(diff_sum_dx)
        for _ in range(dxnum):
            im.alpha_composite(dxstar[dxtype], (DXSTAR_DEST[dxnum] + 20 * _, 550 + y * lv))

        if _data['fc']:
            fc = Image.open(os.path.join(maimaidir, f'UI_CHR_PlayBonus_{fcl[_data["fc"]]}.png')).resize((76, 76))
            im.alpha_composite(fc, (605, 511 + y * lv))
        if _data['fs']:
            fs = Image.open(os.path.join(maimaidir, f'UI_CHR_PlayBonus_{fsl[_data["fs"]]}.png')).resize((76, 76))
            im.alpha_composite(fs, (670, 511 + y * lv))

        p, s = f'{_data["achievements"]:.4f}'.split('.')
        r = tb.get_box(p, 36)
        tb.draw(90, 545 + y * lv, 30, ds, anchor='mm')
        tb.draw(175, 567 + y * lv, 36, p, TEXT_COLOR[lv], 'ld')
        tb.draw(175 + r[2], 565 + y * lv, 30, f'.{s}%', TEXT_COLOR[lv], 'ld')
        tb.draw(550, (535 if dxnum != 0 else 548) + y * lv, 20, f'{dxscore}/{_dxscore}', TEXT_COLOR[lv], 'mm')
        tb.draw(790, 545 + y * lv, 30, ra, TEXT_COLOR[lv], 'mm')

    sy.draw(450, 1180, 20, f'Modified by Kels_Astell | Generated by {BOTNAME}', (159, 81, 220, 255), 'mm', 2,
            (255, 255, 255, 255))
    for key, val in plate_to_version.items():
        if val == music.basic_info.version:
            plate_ver = key
    if plate_type:
        plate_path = os.path.join(maimaidir, f'{plate_ver}{plate_type[0]}.png')
        print(plate_path)
        if os.path.exists(plate_path):
            im.alpha_composite(Image.open(plate_path).resize((540, 87)), (60, 410))
            text = "本曲目已达成: "
            for i in plate_type:
                text += f'{plate_ver}{i} '
            sy.draw(320, 393, 18, f'{text}条件', color, 'lm')
        else:
            plate_path = os.path.join(maimaidir, f'不存在.png')
            im.alpha_composite(Image.open(plate_path).resize((540, 87)), (60, 410))
    else:
        plate_path = os.path.join(maimaidir, f'不存在.png')
        im.alpha_composite(Image.open(plate_path).resize((540, 87)), (60, 410))
    if songs in abstract_list:
        comment = random.choice(abstract_list[str(songs)])
    else:
        comment = ''
    return {"sss": sss, "msg": im, "comment": comment, "song_name": music.title}


async def query_chart_data(match: Match) -> str:
    if match.group(1) != '':
        try:
            level_index = level_labels.index(match.group(1))
            level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re: MASTER']
            name = match.group(2)
            music = mai.total_list.by_id(name)
            chart = music.charts[level_index]
            ds = music.ds[level_index]
            level = music.level[level_index]
            if len(chart.notes) == 4:
                result = f'''{level_name[level_index]} {level}({ds})
TAP: {chart.notes.tap}
HOLD: {chart.notes.hold}
SLIDE: {chart.notes.slide}
BREAK: {chart.notes.brk}
谱师: {chart.charter}'''
            else:
                result = f'''{level_name[level_index]} {level}({ds})
TAP: {chart.notes.tap}
HOLD: {chart.notes.hold}
SLIDE: {chart.notes.slide}
TOUCH: {chart.notes.touch}
BREAK: {chart.notes.brk}
谱师: {chart.charter}'''
            if music.stats and music.stats[level_index]:
                result += f'\n拟合难度: {music.stats[level_index].fit_diff:.2f}'
            msg = f'''{music.id}. {music.title}
{result}'''
        except:
            msg = randomNotFound()
    else:
        try:
            name = match.group(2)
            music = mai.total_list.by_id(name)
            if music:
                msg = await draw_music_info(music)
            else:
                msg = randomNotFound()

        except Exception as e:
            print(traceback.format_exc())
            msg = randomNotFound()

    return msg


async def rise_score_data(payload: dict, match: Match, nickname: Optional[str] = None):
    """
    上分数据
    - `payload` : 传递给查分器的数据
    - `match` : 正则结果
    - `nickname` : 用户昵称
    """
    dx_ra_lowest = 999
    sd_ra_lowest = 999
    player_dx_list = []
    player_sd_list = []
    music_dx_list = []
    music_sd_list = []

    player_data = await get_player_data('best', payload)

    if isinstance(player_data, str):
        return player_data

    for dx in player_data['charts']['dx']:
        dx_ra_lowest = min(dx_ra_lowest, dx['ra'])
        player_dx_list.append([int(dx['song_id']), int(dx["level_index"]), int(dx['ra'])])
    for sd in player_data['charts']['sd']:
        sd_ra_lowest = min(sd_ra_lowest, sd['ra'])
        player_sd_list.append([int(sd['song_id']), int(sd["level_index"]), int(sd['ra'])])
    player_dx_id_list = [[d[0], d[1]] for d in player_dx_list]
    player_sd_id_list = [[s[0], s[1]] for s in player_sd_list]

    for music in mai.total_list:
        for i, ds in enumerate(music.ds):
            for achievement in realAchievementList[f'{ds:.1f}']:
                if match.group(1) and music['level'][i] != match.group(1): continue
                if f'{achievement:.1f}' == '100.5':
                    index_score = 12
                else:
                    index_score = [index for index, acc in enumerate(achievementList[:-1]) if
                                   acc <= achievement < achievementList[index + 1]][0]
                if music.is_new:
                    music_ra = computeRa(ds, achievement)
                    if music_ra < dx_ra_lowest: continue
                    if [int(music.id), i] in player_dx_id_list:
                        player_ra = player_dx_list[player_dx_id_list.index([int(music.id), i])][2]
                        if music_ra - player_ra == int(match.group(2)) and [int(music.id), i,
                                                                            music_ra] not in player_dx_list:
                            music_dx_list.append(
                                [music, diffs[i], ds, achievement, scoreRank[index_score + 1].upper(), music_ra])
                    else:
                        if music_ra - dx_ra_lowest == int(match.group(2)) and [int(music.id), i,
                                                                               music_ra] not in player_dx_list:
                            music_dx_list.append(
                                [music, diffs[i], ds, achievement, scoreRank[index_score + 1].upper(), music_ra])
                else:
                    music_ra = computeRa(ds, achievement)
                    if music_ra < sd_ra_lowest: continue
                    if [int(music.id), i] in player_sd_id_list:
                        player_ra = player_sd_list[player_sd_id_list.index([int(music.id), i])][2]
                        if music_ra - player_ra == int(match.group(2)) and [int(music.id), i,
                                                                            music_ra] not in player_sd_list:
                            music_sd_list.append(
                                [music, diffs[i], ds, achievement, scoreRank[index_score + 1].upper(), music_ra])
                    else:
                        if music_ra - sd_ra_lowest == int(match.group(2)) and [int(music.id), i,
                                                                               music_ra] not in player_sd_list:
                            music_sd_list.append(
                                [music, diffs[i], ds, achievement, scoreRank[index_score + 1].upper(), music_ra])

    if len(music_dx_list) == 0 and len(music_sd_list) == 0:
        return '没有找到这样的乐曲'
    elif len(music_dx_list) + len(music_sd_list) > 60:
        return f'结果过多({len(music_dx_list) + len(music_sd_list)} 条)，请缩小查询范围。'

    appellation = nickname if nickname else '您'
    msg = ''
    if len(music_sd_list) != 0:
        msg += f'为{appellation}推荐以下标准乐曲：\n'
        for music, diff, ds, achievement, rank, ra in sorted(music_sd_list, key=lambda i: int(i[0]['id'])):
            msg += f'{music["id"]}. {music["title"]} {diff} {ds} {achievement} {rank} {ra}\n'
    if len(music_dx_list) != 0:
        msg += f'\n为{appellation}推荐以下new乐曲：\n'
        for music, diff, ds, achievement, rank, ra in sorted(music_dx_list, key=lambda i: int(i[0]['id'])):
            msg += f'{music["id"]}. {music["title"]} {diff} {ds} {achievement} {rank} {ra}\n'

    return msg.strip()


async def player_plate_data(payload: dict, match: Match, nickname: Optional[str]):
    song_played = []
    song_remain_basic = []
    song_remain_advanced = []
    song_remain_expert = []
    song_remain_master = []
    song_remain_re_master = []
    song_remain_difficult = []

    data = await get_player_data('plate', payload)

    if isinstance(data, str):
        return data
    if match.group(1) == '真':
        verlist = list(filter(lambda x: x['title'] != 'ジングルベル', data['verlist']))
    else:
        verlist = data['verlist']
    if match.group(2) in ['将', '者']:
        for song in verlist:
            if song['level_index'] == 0 and song['achievements'] < (100.0 if match.group(2) == '将' else 80.0):
                song_remain_basic.append([song['id'], song['level_index']])
            if song['level_index'] == 1 and song['achievements'] < (100.0 if match.group(2) == '将' else 80.0):
                song_remain_advanced.append([song['id'], song['level_index']])
            if song['level_index'] == 2 and song['achievements'] < (100.0 if match.group(2) == '将' else 80.0):
                song_remain_expert.append([song['id'], song['level_index']])
            if song['level_index'] == 3 and song['achievements'] < (100.0 if match.group(2) == '将' else 80.0):
                song_remain_master.append([song['id'], song['level_index']])
            if match.group(1) in ['舞', '霸'] and song['level_index'] == 4 and song['achievements'] < (
            100.0 if match.group(2) == '将' else 80.0):
                song_remain_re_master.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    elif match.group(2) in ['極', '极']:
        for song in verlist:
            if song['level_index'] == 0 and not song['fc']:
                song_remain_basic.append([song['id'], song['level_index']])
            if song['level_index'] == 1 and not song['fc']:
                song_remain_advanced.append([song['id'], song['level_index']])
            if song['level_index'] == 2 and not song['fc']:
                song_remain_expert.append([song['id'], song['level_index']])
            if song['level_index'] == 3 and not song['fc']:
                song_remain_master.append([song['id'], song['level_index']])
            if match.group(1) == '舞' and song['level_index'] == 4 and not song['fc']:
                song_remain_re_master.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    elif match.group(2) == '舞舞':
        for song in verlist:
            if song['level_index'] == 0 and song['fs'] not in ['fsd', 'fsdp']:
                song_remain_basic.append([song['id'], song['level_index']])
            if song['level_index'] == 1 and song['fs'] not in ['fsd', 'fsdp']:
                song_remain_advanced.append([song['id'], song['level_index']])
            if song['level_index'] == 2 and song['fs'] not in ['fsd', 'fsdp']:
                song_remain_expert.append([song['id'], song['level_index']])
            if song['level_index'] == 3 and song['fs'] not in ['fsd', 'fsdp']:
                song_remain_master.append([song['id'], song['level_index']])
            if match.group(1) == '舞' and song['level_index'] == 4 and song['fs'] not in ['fsd', 'fsdp']:
                song_remain_re_master.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    elif match.group(2) == '神':
        for song in verlist:
            if song['level_index'] == 0 and song['fc'] not in ['ap', 'app']:
                song_remain_basic.append([song['id'], song['level_index']])
            if song['level_index'] == 1 and song['fc'] not in ['ap', 'app']:
                song_remain_advanced.append([song['id'], song['level_index']])
            if song['level_index'] == 2 and song['fc'] not in ['ap', 'app']:
                song_remain_expert.append([song['id'], song['level_index']])
            if song['level_index'] == 3 and song['fc'] not in ['ap', 'app']:
                song_remain_master.append([song['id'], song['level_index']])
            if match.group(1) == '舞' and song['level_index'] == 4 and song['fc'] not in ['ap', 'app']:
                song_remain_re_master.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    for music in mai.total_list:
        if match.group(1) == '真' and music.title == 'ジングルベル':
            continue
        if music.basic_info.version in payload['version']:
            if [int(music.id), 0] not in song_played:
                song_remain_basic.append([int(music.id), 0])
            if [int(music.id), 1] not in song_played:
                song_remain_advanced.append([int(music.id), 1])
            if [int(music.id), 2] not in song_played:
                song_remain_expert.append([int(music.id), 2])
            if [int(music.id), 3] not in song_played:
                song_remain_master.append([int(music.id), 3])
            if match.group(1) in ['舞', '霸'] and len(music.level) == 5 and [int(music.id), 4] not in song_played:
                song_remain_re_master.append([int(music.id), 4])
    song_remain_basic = sorted(song_remain_basic, key=lambda i: int(i[0]))
    song_remain_advanced = sorted(song_remain_advanced, key=lambda i: int(i[0]))
    song_remain_expert = sorted(song_remain_expert, key=lambda i: int(i[0]))
    song_remain_master = sorted(song_remain_master, key=lambda i: int(i[0]))
    song_remain_re_master = sorted(song_remain_re_master, key=lambda i: int(i[0]))
    for song in song_remain_basic + song_remain_advanced + song_remain_expert + song_remain_master + song_remain_re_master:
        music = mai.total_list.by_id(str(song[0]))
        if music.ds[song[1]] > 13.6:
            song_remain_difficult.append([music.id, music.title, diffs[song[1]], music.ds[song[1]], song[1]])

    appellation = nickname if nickname else '您'

    msg = f'''{appellation}的{match.group(1)}{match.group(2)}剩余进度如下：
基础剩余{len(song_remain_basic)}首
高级剩余{len(song_remain_advanced)}首
专家剩余{len(song_remain_expert)}首
大师剩余{len(song_remain_master)}首
'''
    song_remain: list[
        list] = song_remain_basic + song_remain_advanced + song_remain_expert + song_remain_master + song_remain_re_master
    song_record = [[s['id'], s['level_index']] for s in verlist]
    if match.group(1) in ['舞', '霸']:
        msg += f'Re:Master剩余{len(song_remain_re_master)}首\n'
    if len(song_remain_difficult) > 0:
        if len(song_remain_difficult) < 60:
            msg += '剩余定数大于13.6的曲目：\n'
            for i, s in enumerate(sorted(song_remain_difficult, key=lambda i: i[3])):
                self_record = ''
                if [int(s[0]), s[-1]] in song_record:
                    record_index = song_record.index([int(s[0]), s[-1]])
                    if match.group(2) in ['将', '者']:
                        self_record = str(verlist[record_index]['achievements']) + '%'
                    elif match.group(2) in ['極', '极', '神']:
                        if verlist[record_index]['fc']:
                            self_record = comboRank[combo_rank.index(verlist[record_index]['fc'])].upper()
                    elif match.group(2) == '舞舞':
                        if verlist[record_index]['fs']:
                            self_record = syncRank[sync_rank.index(verlist[record_index]['fs'])].upper()
                msg += f'No.{i + 1} {s[0]}. {s[1]} {s[2]} {s[3]} {self_record}'.strip() + '\n'
            if len(song_remain_difficult) > 10:
                msg = msg.strip()
        else:
            msg += f'还有{len(song_remain_difficult)}首大于13.6定数的曲目，加油推分捏！\n'
    elif len(song_remain) > 0:
        for i, s in enumerate(song_remain):
            m = mai.total_list.by_id(str(s[0]))
            ds = m.ds[s[1]]
            song_remain[i].append(ds)
        if len(song_remain) < 60:
            msg += '剩余曲目：\n'
            for i, s in enumerate(sorted(song_remain, key=lambda i: i[2])):
                m = mai.total_list.by_id(str(s[0]))
                self_record = ''
                if [int(s[0]), s[-1]] in song_record:
                    record_index = song_record.index([int(s[0]), s[-1]])
                    if match.group(2) in ['将', '者']:
                        self_record = str(verlist[record_index]['achievements']) + '%'
                    elif match.group(2) in ['極', '极', '神']:
                        if verlist[record_index]['fc']:
                            self_record = comboRank[combo_rank.index(verlist[record_index]['fc'])].upper()
                    elif match.group(2) == '舞舞':
                        if verlist[record_index]['fs']:
                            self_record = syncRank[sync_rank.index(verlist[record_index]['fs'])].upper()
                msg += f'No.{i + 1} {m.id}. {m.title} {diffs[s[1]]} {m.ds[s[1]]} {self_record}'.strip() + '\n'
            if len(song_remain) > 10:
                msg = msg.strip()
        else:
            msg += '已经没有定数大于13.6的曲目了,加油清谱捏！\n'
    else:
        msg += f'恭喜{appellation}完成{match.group(1)}{match.group(2)}！'

    return msg


async def level_process_data(payload: dict, match: Match, nickname: Optional[str]):
    song_played = []
    song_remain = []

    data = await get_player_data('plate', payload)

    if isinstance(data, str):
        return data

    if match.group(2).lower() in scoreRank:
        achievement = achievementList[scoreRank.index(match.group(2).lower()) - 1]
        for song in data['verlist']:
            if song['level'] == match.group(1) and song['achievements'] < achievement:
                song_remain.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    elif match.group(2).lower() in comboRank:
        combo_index = comboRank.index(match.group(2).lower())
        for song in data['verlist']:
            if song['level'] == match.group(1) and (
                    (song['fc'] and combo_rank.index(song['fc']) < combo_index) or not song['fc']):
                song_remain.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    elif match.group(2).lower() in syncRank:
        sync_index = syncRank.index(match.group(2).lower())
        for song in data['verlist']:
            if song['level'] == match.group(1) and (
                    (song['fs'] and sync_rank.index(song['fs']) < sync_index) or not song['fs']):
                song_remain.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    for music in mai.total_list:
        for i, lv in enumerate(music.level[2:]):
            if lv == match.group(1) and [int(music.id), i + 2] not in song_played:
                song_remain.append([int(music.id), i + 2])
    song_remain = sorted(song_remain, key=lambda i: int(i[1]))
    song_remain = sorted(song_remain, key=lambda i: int(i[0]))
    songs = []
    for song in song_remain:
        music = mai.total_list.by_id(str(song[0]))
        songs.append([music.id, music.title, diffs[song[1]], music.ds[song[1]], song[1]])

    appellation = nickname if nickname else '您'

    msg = ''
    if len(song_remain) > 0:
        if len(song_remain) < 50:
            song_record = [[s['id'], s['level_index']] for s in data['verlist']]
            msg += f'{appellation}的{match.group(1)}全谱面{match.group(2).upper()}剩余曲目如下：\n'
            for i, s in enumerate(sorted(songs, key=lambda i: i[3])):
                self_record = ''
                if [int(s[0]), s[-1]] in song_record:
                    record_index = song_record.index([int(s[0]), s[-1]])
                    if match.group(2).lower() in scoreRank:
                        self_record = str(data['verlist'][record_index]['achievements']) + '%'
                    elif match.group(2).lower() in comboRank:
                        if data['verlist'][record_index]['fc']:
                            self_record = comboRank[combo_rank.index(data['verlist'][record_index]['fc'])].upper()
                    elif match.group(2).lower() in syncRank:
                        if data['verlist'][record_index]['fs']:
                            self_record = syncRank[sync_rank.index(data['verlist'][record_index]['fs'])].upper()
                msg += f'No.{i + 1} {s[0]}. {s[1]} {s[2]} {s[3]} {self_record}'.strip() + '\n'
            if len(songs) > 10:
                msg = msg.strip()
        else:
            msg = f'{appellation}还有{len(song_remain)}首{match.group(1)}曲目没有达成{match.group(2).upper()},加油推分捏！'
    else:
        msg = f'恭喜{appellation}达成{match.group(1)}全谱面{match.group(2).upper()}！'

    return msg


async def level_achievement_list_data(payload: dict, match: Match, nickname: Optional[str]):
    song_list = []

    data = await get_player_data('plate', payload)

    if isinstance(data, str):
        return data

    for song in data['verlist']:
        if song['level'] == match.group(1):
            song_list.append(song)

    page = max(min(int(match.group(2)), len(song_list) // SONGS_PER_PAGE + 1), 1) if match.group(2) else 1

    appellation = nickname if nickname else '您'

    msg = f'{appellation}的{match.group(1)}分数列表（从高至低）：\n'
    for i, s in enumerate(sorted(song_list, key=lambda i: i['achievements'], reverse=True)):
        if (page - 1) * SONGS_PER_PAGE <= i < page * SONGS_PER_PAGE:
            m = mai.total_list.by_id(str(s['id']))
            msg += f'No.{i + 1} {s["achievements"]:.4f} {m.id}. {m.title} {diffs[s["level_index"]]} {m.ds[s["level_index"]]}'
            if s["fc"]: msg += f' {comboRank[combo_rank.index(s["fc"])].upper()}'
            if s["fs"]: msg += f' {syncRank[sync_rank.index(s["fs"])].upper()}'
            msg += '\n'
    msg += f'第{page}页，共{len(song_list) // SONGS_PER_PAGE + 1}页'

    return msg.strip()


def name_linked(kid: str):
    with open(os.path.join(static, 'qq_name_list.json'), 'r', encoding='utf-8') as fp:
        name_list = json.load(fp)
    if kid in name_list:
        return {"success": True, "username": name_list[kid]['id']}
    else:
        return {"success": False}


async def rating_ranking_data(name: Optional[str], page: Optional[int]):
    rank_data = await get_rating_ranking_data()

    if isinstance(rank_data, str):
        return rank_data

    sorted_rank_data = sorted(rank_data, key=lambda r: r['ra'], reverse=True)
    json_str = json.dumps(sorted_rank_data, indent=4, ensure_ascii=False)
    with open(os.path.join(static, 'rank_data.json'), 'w', encoding='utf-8') as json_file:
        json_file.write(json_str)
    if name:
        if name in [r['username'].lower() for r in sorted_rank_data]:
            rank_index = [r['username'].lower() for r in sorted_rank_data].index(name) + 1
            nickname = sorted_rank_data[rank_index - 1]['username']
            ra = sorted_rank_data[rank_index - 1]['ra']
            rank_percent = round(100 - rank_index / len(rank_data) * 100, 2)
            data = ''
            if ra >= 16000:
                data = '\n我超，乌蒙大神！'
            data = data + f'截止至 {time.strftime("%Y年%m月%d日%H时%M分", time.localtime())}\n{nickname}的ra为{ra}\n在水鱼网站ra排行第{rank_index}\n超过了{rank_percent}%的玩家'
            return data
        else:
            data = '未找到该玩家'
            return data
    else:
        user_num = len(sorted_rank_data)
        msg = f'截止至 {time.strftime("%Y年%m月%d日%H时%M分", time.localtime())}，水鱼网站已注册用户ra排行：\n'
        if page * 50 > user_num:
            page = user_num // 50 + 1
        end = page * 50 if page * 50 < user_num else user_num
        for i, ranker in enumerate(sorted_rank_data[(page - 1) * 50:end]):
            msg += f'{i + 1 + (page - 1) * 50}. {ranker["username"]} {ranker["ra"]}\n'
        msg += f'第{page}页，共{user_num // 50 + 1}页'
        data = msg.strip()

    return data


async def rating_pk(name1: Optional[str], name2: Optional[str]):
    rank_data = await get_rating_ranking_data()

    if isinstance(rank_data, str):
        return rank_data

    sorted_rank_data = sorted(rank_data, key=lambda r: r['ra'], reverse=True)

    if name1 in [r['username'].lower() for r in sorted_rank_data] and name2 in [r['username'].lower() for r in
                                                                                sorted_rank_data]:
        rank_index1 = [r['username'].lower() for r in sorted_rank_data].index(name1) + 1
        rank_index2 = [r['username'].lower() for r in sorted_rank_data].index(name2) + 1
        nickname1 = sorted_rank_data[rank_index1 - 1]['username']
        nickname2 = sorted_rank_data[rank_index2 - 1]['username']
        data = f'{nickname1}在排行第{rank_index1}位.\n{nickname2}在排行第{rank_index2}位.\n让我们恭喜'
        if not rank_index1 == rank_index2:
            data += f'{nickname1}' if rank_index1 < rank_index2 else f'{nickname2}'
        else:
            data += '两位选手打成平手, 你们就是传说中的55开?'
    else:
        data = '未找到该玩家'
    return data


def is_abstract(music_id):
    if music_id in abstract_reply:
        rep = abstract_reply[music_id]
        random.shuffle(rep)
        random.shuffle(nls_data)
        return {"abstract": True, "reply": nls_data[0] + rep[0]}
    else:
        return {"abstract": False, "reply": "不知道是什么"}
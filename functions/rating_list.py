import os
import traceback
from typing import Dict, List

from PIL import Image, ImageDraw

from functions.api import get_player_data
from functions.best_50 import DrawText, computeRa
from functions.config import static, ratingdir, maimaidir
from functions.info import SIYUAN, plate_to_version
from functions.log_utils import Log
from functions.music import RaMusic, mai
levelList = ['1', '2', '3', '4', '5', '6', '7', '7+', '8', '8+', '9', '9+', '10', '10+', '11', '11+', '12', '12+', '13',
             '13+', '14', '14+', '15']
coverdir = os.path.join(static, 'mai','cover')


async def update_rating_table() -> str:
    """
    更新定数表
    """
    try:
        lv1 = ['6', '7', '8', '12', '13']
        lv2 = ['7+', '8+', '9', '9+', '10', '10+', '11', '11+']
        lv3 = ['12+', '13+', '14', '14+', '15']

        bg_color = [(111, 212, 61, 255), (248, 183, 9, 255), (255, 129, 141, 255), (159, 81, 220, 255),
                    (219, 170, 255, 255)]
        dx = Image.open(os.path.join(maimaidir, 'DX.png')).convert('RGBA').resize((44, 16))
        diff = [Image.new('RGBA', (75, 75), color) for color in bg_color]

        for ra in levelList[5:]:
            musiclist = mai.total_list.lvList(True)
            if ra in lv1:
                im = Image.open(os.path.join(ratingdir, 'Rating3.png')).convert('RGBA')
            elif ra in lv2:
                im = Image.open(os.path.join(ratingdir, 'Rating2.png')).convert('RGBA')
            elif ra in lv3:
                im = Image.open(os.path.join(ratingdir, 'Rating.png')).convert('RGBA')
            else:
                im = Image.open(os.path.join(ratingdir, 'Rating0.png')).convert('RGBA')
                Log.warn('未知定数表, 已使用本地临时文件替代.')
            dr = ImageDraw.Draw(im)
            sy = DrawText(dr, SIYUAN)

            if ra in levelList[-3:]:
                bg = os.path.join(ratingdir, '14.png')
                ralist = levelList[-3:]
            else:
                bg = os.path.join(ratingdir, f'{ra}.png')
                ralist = [ra]

            lvlist: Dict[str, List[RaMusic]] = {}
            for lvs in list(reversed(ralist)):
                for _ra in musiclist[lvs]:
                    lvlist[_ra] = musiclist[lvs][_ra]

            if ra in ['14', '14+', '15']:
                lvtext = '大比歌 定数表'
            else:
                lvtext = f'Level.{ra} 定数表'

            sy.draw(750, 120, 65, lvtext, (0, 0, 0, 255), 'mm')
            y = 120
            x = 0
            for lv in lvlist:
                y += 10
                sy.draw(100, y + 120, 50, lv, (0, 0, 0, 255), 'mm')
                for num, music in enumerate(lvlist[lv]):
                    if num % 15 == 0:
                        x = 200
                        y += 85
                    else:
                        x += 85
                    cover = os.path.join(coverdir, f'{music.id}.png')
                    if os.path.isfile(cover):
                        if int(music.lv) != 3:
                            cover_bg = diff[int(music.lv)]
                            cover_bg.alpha_composite(Image.open(cover).convert('RGBA').resize((65, 65)), (5, 5))
                        else:
                            cover_bg = Image.open(cover).convert('RGBA').resize((75, 75))
                        im.alpha_composite(cover_bg, (x, y))
                        if music.type == 'DX':
                            im.alpha_composite(dx, (x + 31, y))
                if not lvlist[lv]:
                    y += 85

            im.save(bg)
            Log.info(f'lv.{ra} 定数表更新完成')
        return '定数表已更新至国服最新最热.'
    except Exception as e:
        Log.error(traceback.format_exc())
        return f'定数表更新失败，Error: {e}'


async def rating_table_draw(payload: dict, args: str):
    payload['version'] = list(set(version for version in plate_to_version.values()))
    data = await get_player_data('plate', payload)
    if isinstance(data, str):
        return data

    if args in levelList[-3:]:
        bg = os.path.join(ratingdir, '14.png')
        ralist = levelList[-3:]
    else:
        bg = os.path.join(ratingdir, f'{args}.png')
        ralist = [args]

    fromid = {}
    for _data in data['data']['verlist']:
        if _data['level'] in ralist:
            if (music_id := str(_data['id'])) not in fromid:
                fromid[music_id] = {}
            fromid[music_id][str(_data['level_index'])] = {
                'achievements': _data['achievements'],
                'level': _data['level']
            }

    musiclist = mai.total_list.lvList(True)
    lvlist: Dict[str, List[RaMusic]] = {}
    for lv in list(reversed(ralist)):
        for _ra in musiclist[lv]:
            lvlist[_ra] = musiclist[lv][_ra]

    im = Image.open(bg).convert('RGBA')
    b2 = Image.new('RGBA', (75, 75), (0, 0, 0, 64))
    y = 138
    x = 0
    for ra in lvlist:
        y += 10
        for num, music in enumerate(lvlist[ra]):
            if num % 15 == 0:
                x = 198
                y += 85
            else:
                x += 85
            if music.id in fromid and music.lv in fromid[music.id]:
                ra, rate = computeRa(music.ds, fromid[music.id][music.lv]['achievements'], israte=True)
                im.alpha_composite(b2, (x + 2, y - 18))
                rank = Image.open(os.path.join(maimaidir, f'UI_TTR_Rank_{rate}.png')).resize((78, 36))
                im.alpha_composite(rank, (x, y))
    return im
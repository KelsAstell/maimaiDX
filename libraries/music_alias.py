import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json
import os

from .. import static, BOTNAME

nls_data = ['是不是', '可能是', '也许是', '差不多是', '大概是', '没准是']
#static = r'D:\Projects\IDEA\musicalis\static'
ALL_ALIAS = os.path.join(static, 'all_alias.json')


def su_add_new(song_id, alias):
    with open(ALL_ALIAS, 'r', encoding='utf-8') as fp:
        all_alias = json.load(fp)
    alias = str(alias)
    if song_id in all_alias:
        if alias not in all_alias[song_id]:
            all_alias[song_id]["Alias"].append(alias)
            json_str = json.dumps(all_alias, indent=4, ensure_ascii=False)
            with open(ALL_ALIAS, 'w', encoding='utf-8') as fp:
                fp.write(json_str)
                return f"为歌曲{all_alias[song_id]['Name']}添加别名\"{alias}\"成功"
        return "已经有这个名字了呢"
    new_data = {"Name": alias,"Alias": [alias]}
    all_alias[song_id] = new_data
    json_str = json.dumps(all_alias, indent=4, ensure_ascii=False)
    with open(ALL_ALIAS, 'w', encoding='utf-8') as fp:
        fp.write(json_str)
    return f"为歌曲ID{song_id}添加别名\"{alias}\"成功"


def kohd(song_id):
    with open(ALL_ALIAS, 'r', encoding='utf-8') as fp:
        all_alias = json.load(fp)
    song_id = str(song_id)
    if song_id in all_alias:
        del all_alias[song_id]
        json_str = json.dumps(all_alias, indent=4, ensure_ascii=False)
        with open(ALL_ALIAS, 'w', encoding='utf-8') as fp:
            fp.write(json_str)
        return f"ID" + song_id + '已删除，你就是KohaD?'
    return f"没找到这样的曲子"


def su_batch_add_alias(song_id, alias):
    with open(ALL_ALIAS, 'r', encoding='utf-8') as fp:
        all_alias = json.load(fp)
    song_id = str(song_id)
    alias = str(alias)
    if song_id in all_alias:
        alias = list(set(alias.split("/")))
        for nick in alias:
            if nick not in all_alias[song_id]["Alias"]:
                all_alias[song_id]['Alias'].append(nick)
        json_str = json.dumps(all_alias, indent=4, ensure_ascii=False)
        with open(ALL_ALIAS, 'w', encoding='utf-8') as fp:
            fp.write(json_str)
        return f'歌曲ID{song_id}的别名更新已完成'
    return "挠头, 你好像还没初始化过. 问问艾斯?"


# print(su_batch_add_alias(1,'aa2a/a4a/a0a'))

def image_to_base64(img: Image.Image, format='PNG') -> str:
    output_buffer = BytesIO()
    img.save(output_buffer, format)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode()
    return 'base64://' + base64_str


def drawAliasPicture(alias_text):
    font_path = os.path.join(static, "Alimama_ShuHeiTi_Bold.ttf")
    font_path_2 = os.path.join(static, "Source_Han_Sans_SC_Light_Light.otf")
    img = Image.open(os.path.join(static, "bg.png"))
    draw = ImageDraw.Draw(img)
    font_info = ImageFont.truetype(font_path, size=56)
    color = (255, 255, 255)
    draw.text((50, 70), alias_text, font=font_info,
              fill=color, spacing=28)
    font_info = ImageFont.truetype(font_path_2, size=32)
    color = (0, 0, 0)
    draw.text((50, 1290), f'iiDX别名扩展 By 大以巴狼艾斯 | By {BOTNAME}', font=font_info, fill=color,
              spacing=28, align="center")
    # img.show()
    return image_to_base64(img)


def updateAlias(operation, song_id, text):
    song_id = str(song_id)
    if operation == 'change_name':
        with open(ALL_ALIAS, 'r', encoding='utf-8') as fp:
            all_alias = json.load(fp)
        if song_id in all_alias:
            all_alias[song_id]["Name"] = text
            json_str = json.dumps(all_alias, indent=4, ensure_ascii=False)
            with open(ALL_ALIAS, 'w', encoding='utf-8') as fp:
                fp.write(json_str)
            return '歌曲名已完成变更'
        return 'ID不存在'
    elif operation == 'batch_delete':
        with open(ALL_ALIAS, 'r', encoding='utf-8') as fp:
            all_alias = json.load(fp)
        if song_id in all_alias:
            text = list(set(text.split("/")))
            for nick in text:
                if nick in all_alias[song_id]['Alias']:
                    all_alias[song_id]['Alias'].remove(nick)
            json_str = json.dumps(all_alias, indent=4, ensure_ascii=False)
            with open(ALL_ALIAS, 'w', encoding='utf-8') as fp:
                fp.write(json_str)
            return '更新完成'
        return 'ID不存在'


#print(updateAlias('change_name',114514,'bbb'))
#print(updateAlias('batch_delete',114514,'55/33/555'))
#print(su_add_new(114514,'野兽先辈原声大碟'))
#print(kohd(114514))
#print(su_batch_add_alias(114514,'55/33/aa777a'))


import asyncio
import io
import time
import aiohttp
import psutil
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from khl import Bot, Message
from khl.card import CardMessage, Card, Module, Element, Types
from khl.command import Rule

# from functions.api import get_player_data, botmarket_online
# from functions.best_50 import UserInfo, DrawBest
# from functions.bind import check_bind, bind_qq, set_username, check_perm, ban_reason
# from functions.alias_utils import updateAlias, su_batch_add_alias, merge_remote_alias, kohd, su_add_new
# from functions.config import BOTNAME
# from functions.info import music_play_data, name_linked, rating_ranking_data, rating_pk, draw_music_info, \
#     solips_play_data
from functions.bind import *
from functions.alias_utils import *
from functions.info import *
from functions.music import mai
from functions.random_reply import randomNotFound
from plugins.aioAPI.libraries.random_reply import randomKFC
from plugins.aioAPI.libraries.utils import *
from plugins.fish.libraries.fish_utils import *
from plugins.mcping.libraries.info import mcinfo, mcinfo_min
from plugins.mcping.libraries.remote import say, execute
from plugins.openAI.libraries.functions import openAI
from plugins.openAI.libraries.random_reply import randomThink
from plugins.potato.libraries.functions import *
from plugins.randompic.randompic import *

with open('./bot_config.json', 'r', encoding='utf-8') as f:
    bot_config = json.load(f)
NOT_BIND = "请使用**bind <QQ号>**进行绑定"

scheduler = AsyncIOScheduler(timezone=pytz.utc)

# init Bot
bot = Bot(token=bot_config['token'])


async def preinit():
    await mai.get_music()
    await mai.get_music_alias()
    bot.command.update_prefixes('')


async def prepare_image(pic):
    imgByteArr = io.BytesIO()
    pic = pic.convert('RGB')
    pic.save(imgByteArr, 'JPEG', optimize=True, quality=80, compress_level=5)
    return await bot.client.create_asset(io.BytesIO(imgByteArr.getvalue()))


async def prepare_gif(pic):
    imgByteArr = io.BytesIO()
    if pic.mode == 'RGB':
        pic.save(imgByteArr, format='JPEG', optimize=True, quality=80, compress_level=5)
    elif pic.mode == 'P':
        pic = pic.convert('RGB')
        pic.save(imgByteArr, format='JPEG', optimize=True, quality=80, compress_level=5)
    elif pic.mode == 'RGBA' or pic.mode == 'LA':
        pic = pic.convert('RGB')
        pic.save(imgByteArr, format='JPEG', optimize=True, quality=80, compress_level=5)
    else:
        # Handle GIF images
        pic.save(imgByteArr, format='GIF', optimize=True, quality=80, compress_level=5)
    return await bot.client.create_asset(io.BytesIO(imgByteArr.getvalue()))


async def info(qqid, args):
    payload = {}
    if isinstance(qqid, int):
        payload = {'qq': qqid}
    elif isinstance(qqid, str):
        payload = {'username': qqid}
    if mai.total_list.by_id(args):
        song_id = args
    elif by_t := mai.total_list.by_title(args):
        song_id = by_t.id
    else:
        alias = mai.total_alias_list.by_alias(args)
        if not alias:
            return "找不到拥有这个别名的歌曲"
        elif len(alias) != 1:
            msg = f'找到相同别名的曲目，请使用以下ID查询：\n'
            for songs in alias:
                msg += f'{songs.ID}：{songs.Name}\n'
            return msg
        else:
            song_id = str(alias[0].ID)
    play_data = await music_play_data(payload, song_id)
    pic = play_data["msg"]
    # pic.show()
    img_url = await prepare_image(pic)
    return {'url': img_url, 'sss': play_data['sss'], 'comment': play_data['comment']}


async def best_50(user):
    payload = {}
    if isinstance(user, int):
        payload = {'qq': user}
    elif isinstance(user, str):
        payload = {'username': user}
        if user.lower() in bot_config['user']['blacklist']:
            return "该用户已被Bot封禁, 无法查看Best50"
    payload['b50'] = True
    response = await get_player_data('best', payload)
    if response['success']:
        obj = response['data']
        mai_info = UserInfo(**obj)
        if isinstance(user, int):
            draw_best = DrawBest(mai_info, user)
        else:
            draw_best = DrawBest(mai_info)
        pic = await draw_best.draw()
        # pic.show()
        new_size = (round(pic.width / 2), round(pic.height / 2))
        pic = pic.resize(new_size)
        img_url = await prepare_image(pic)
        return {'name': obj['username'], 'url': img_url}
    else:
        return response['data']


@bot.command(name='bind', aliases=['绑定', 'bindqq'])
async def bind(msg: Message, qqid: int):
    uid = msg.author_id
    if qqid in bot_config['qq']['blacklist']:
        await msg.reply(
            CardMessage(
                Card(
                    Module.Header(f'OOPS! {msg.author.nickname}试图绑定已被封禁的ID'),
                    Module.Context(f'封禁名单由{BOTNAME} / ELISA Bot开发组维护.'),
                    Module.Divider(),
                    Module.Header(f'封禁理由如下:'),
                    Module.Context(Element.Text(await ban_reason(qqid))),color='#FF2400'
                )))
        return None
    await msg.reply(await bind_qq(uid, qqid))
    Log.info(f'[绑定] {msg.author.nickname} 将QQ绑定为 {qqid}')


@bot.command(name='cbind', aliases=['查绑定'])
async def cbind(msg: Message, args: str = ''):
    if msg.extra['mention']:
        if await check_perm(msg.author_id):
            qqid = await check_bind(msg.extra['mention'][0])
        else:
            qqid = await check_bind(msg.author_id)
    else:
        qqid = await check_bind(msg.author_id)
    if not qqid:
        text = f'还没有绑定捏, {NOT_BIND}'
    else:
        text = f'已绑定QQ为{qqid}'
    await msg.ctx.channel.send(CardMessage(
        Card(
            Module.Header(f'{msg.author.nickname}的绑定信息'),
            Module.Context(f'本消息仅对你可见.'),
            Module.Divider(),
            Module.Header(f'绑定信息如下:'),
            Module.Context(Element.Text(text)), color='#FFD700'
        )), temp_target_id=msg.author.id)
    Log.info(f'[绑定查询] {msg.author.nickname} 查询了绑定信息')
    return None


@bot.command(name='ib50', aliases=['b50', 'best50', 'best40', 'b40'],case_sensitive=False)
async def b50(msg: Message, args: str = ''):
    start_time = time.perf_counter()
    if msg.extra['mention']:
        qqid = await check_bind(msg.extra['mention'][0])
        # await msg.reply(f"kookID{msg.extra['mention'][0]}查询了{qqid}.")
        # return None
    else:
        qqid = await check_bind(msg.author_id)
    if args and not qqid:
        if args.lower() in bot_config['user']['blacklist']:
            await msg.reply(
                CardMessage(
                    Card(
                        Module.Header(f'OOPS! {msg.author.nickname}试图查询已被封禁的ID'),
                        Module.Context(f'封禁名单由{BOTNAME} / ELISA Bot开发组维护.'),
                        Module.Divider(),
                        Module.Header(f'封禁理由如下:'),
                        Module.Context(Element.Text(await ban_reason(args.lower()))),color='#FF2400'
                    )))
            return None
        data = await best_50(args.lower())
    elif qqid:
        data = await best_50(qqid)
    else:
        await msg.reply(NOT_BIND)
        return None
    if isinstance(data, str):
        await msg.reply(data)
        return None
    if not args:
        await set_username(msg.author_id, data['name'])
    eclipsed_time = time.perf_counter() - start_time
    await msg.reply(
        CardMessage(
            Card(
                Module.Header(f'{data["name"]}的Best50数据'),
                Module.Context(f'由{BOTNAME}在{eclipsed_time:.3f}秒内生成.'),
                Module.Divider(),
                Module.Container(Element.Image(data['url'])),color='#40E0D0'
            )))
    Log.info(f'[Best50] {msg.author.nickname} 生成了Best50数据, 耗时{eclipsed_time:.3f}秒')


@bot.command(name='info', aliases=['minfo'] ,case_sensitive=False)
async def music_info(msg: Message, args: str = '', at: str = ''):
    start_time = time.perf_counter()
    if msg.extra['mention']:
        qqid = await check_bind(msg.extra['mention'][0])
    else:
        qqid = await check_bind(msg.author_id)
    if args:
        if qqid:
            data = await info(qqid, args)
        else:
            await msg.reply(NOT_BIND)
            return None
    else:
        await msg.reply("抓抓呆毛, " + random.choice(
            ['你要查啥?', '你要查什么', '你要查what?']) + "\n命令格式：info <歌曲名/id/别名>")
        return None
    if isinstance(data, str):
        await msg.reply(data)
        Log.info(f'[MusicInfo] {msg.author.nickname} 生成了单曲数据, 但{data}.')
        return None
    eclipsed_time = time.perf_counter() - start_time
    await msg.reply(
        CardMessage(
            Card(
                Module.Header(f'单曲游玩数据'),
                Module.Context(f'由{BOTNAME}在{eclipsed_time:.3f}秒内生成.'),
                Module.Divider(),
                Module.Container(Element.Image(data['url']))
            )))
    Log.info(f'[MusicInfo] {msg.author.nickname} 生成了单曲数据, 耗时{eclipsed_time:.3f}秒')
    if data['sss']:
        await asyncio.sleep(3)
        await msg.reply(f"我超, {data['comment']}!")


@bot.command(name='原神', aliases=['solips', '嗦梨进度', '🍐', '嗦嗦', '嗦'])
async def solips_rating(msg: Message,text: str = ''):
    qqid = await check_bind(msg.author_id)
    if qqid:
        await msg.reply(await solips_play_data({'qq': qqid}))
        return None
    else:
        await msg.reply(NOT_BIND)


@bot.command(name='rating', aliases=['rainfo', 'ra', '我有多菜', '他有多菜', '她有多菜'])
async def ra(msg: Message, args: str = ''):
    if args:
        name = args.lower()
        data = await rating_ranking_data(name, 1)
        await msg.reply(data)
        return None
    else:
        query = name_linked(msg.author_id)
        if query["success"]:
            data = await rating_ranking_data(query["username"].lower(), 1)
            await msg.reply(data)
            return None
        else:
            await msg.reply(NOT_BIND)


@bot.command(name='rapk', aliases=['ra比较', '有人对战', '友人对战', '仇人对战'])
async def rapk(msg: Message, name1: str = '', name2: str = ''):
    Log.info(f'[raPK] {msg.author.nickname} 触发了raPK.')
    if name1 != name2 and name1:
        if name2:
            data = await rating_pk(name1.lower(), name2.lower())
            await msg.reply(data)
            return None
        else:
            query = name_linked(msg.author_id)
            if query["success"]:
                data = await rating_pk(name1.lower(), query["username"].lower())
                await msg.reply(data)
                return None
            else:
                await msg.reply('请使用**/b50**查询一次自己的成绩完成初始化')
        return None
    else:
        await msg.reply(
            CardMessage(
                Card(
                    Module.Header(f'指令帮助 - /rapk'),
                    Module.Context(f'这个指令比较复杂, 请按照以下说明操作EmoBot.'),
                    Module.Divider(),
                    Module.Container(Element.Text('```用法：'
                                                  '/rapk <玩家1> [玩家2]\n'
                                                  '如果玩家2为空, 则与发送本指令的玩家进行PK'
                                                  '执行本命令前, 至少需要查询过一次自己的best50成绩```'))
                )))


@bot.command(name='你有多菜')
async def genshin(msg: Message):
    await msg.reply('我是乌蒙大神🤩！\n截止至 2077年02月30日11时45分14秒\n爷在火猫网站ra排行第1\n超过了1000%的玩家')


@bot.command(name='更新歌曲名称', aliases=['更改歌曲名称', '更改歌曲名', '更新歌曲名'])
async def update_name(msg: Message, text: str = ''):
    if not await check_perm(msg.author_id):
        return None
    text = text.split("-")
    if len(text) > 1:
        await msg.reply(updateAlias('change_name', int(text[0]), text[1]))
        await mai.get_music_alias()
    else:
        await msg.reply('用法: 更改歌曲名称 ID-名字')


@bot.command(name='删除别名', aliases=['批量删除别名', '批量删除抽象别名', '删除抽象别名'])
async def batch_delete(msg: Message, text: str = ''):
    if not await check_perm(msg.author_id):
        return None
    text = text.split("-")
    if len(text) > 1:
        await msg.reply(updateAlias('batch_delete', int(text[0]), text[1]))
        await mai.get_music_alias()
    else:
        await msg.reply('用法: 删除别名 ID-别名1/别名2..')


@bot.command(name='添加别名', aliases=['批量添加别名', '批量添加抽象别名', '添加抽象别名'])
async def batch_add(msg: Message, text: str = ''):
    if not await check_perm(msg.author_id):
        return None
    text = text.split("-")
    if len(text) > 1:
        await msg.reply(su_batch_add_alias(int(text[0]), text[1]))
        await mai.get_music_alias()
    else:
        await msg.reply('用法: 添加别名 ID-别名1/别名2..')


@bot.command(name='初始化', aliases=['init'])
async def init_maimai(msg: Message, text: str = ''):
    if not await check_perm(msg.author_id):
        await msg.reply('权限不足')
        return None
    await preinit()
    await msg.reply('Finished.')


@bot.command(name='添加新歌', aliases=['添加最新最热', '添加最旧最冷'])
async def new_song(msg: Message, text: str = ''):
    if not await check_perm(msg.author_id):
        return None

    text = text.split("-")
    if len(text) == 2:
        await msg.reply(su_add_new(int(text[0]), text[1]))
        await mai.get_music_alias()
    else:
        await msg.reply('用法: 添加新歌 ID-歌曲名')


@bot.command(name='删除歌曲', aliases=['删歌', 'kohad'])
async def del_song(msg: Message, text: str = ''):
    if not await check_perm(msg.author_id):
        return None
    await msg.reply(kohd(text))
    await mai.get_music_alias()


@bot.command(name='同步别名库', aliases=['更新别名库'])
async def upd_alias_list(msg: Message):
    if not await check_perm(msg.author_id):
        return None
    await msg.reply(await merge_remote_alias())


@bot.command(name='查歌', aliases=['啥歌'])
async def what_song(msg: Message, text: str = ''):
    start_time = time.perf_counter()
    data = mai.total_alias_list.by_alias(text)
    if not data:
        await msg.reply(randomNotFound())
    if len(data) != 1:
        text = f'找到{len(data)}个相同别名的曲目：\n'
        for songs in data:
            text += f'{songs.ID}：{songs.Name}\n'
        await msg.reply(text.strip())
    music = mai.total_list.by_id(str(data[0].ID))
    eclipsed_time = time.perf_counter() - start_time
    img_url = await prepare_image(await draw_music_info(music))
    await msg.reply(
        CardMessage(
            Card(
                Module.Header(f'找到了以下乐曲'),
                Module.Context(f'由{BOTNAME}在{eclipsed_time:.3f}秒内生成.'),
                Module.Divider(),
                Module.Container(Element.Image(img_url))
            )))


@bot.command(name='钓鱼', aliases=['摸鱼'])
async def fish(msg: Message):
    qqid = await check_bind(msg.author_id)
    if not qqid:
        await msg.reply(NOT_BIND)
        return None
    await msg.reply(await roll(str(qqid)))


@bot.command(name='升级鱼竿', aliases=['升级钓竿'])
async def upgrade_rod(msg: Message):
    qqid = await check_bind(msg.author_id)
    if not qqid:
        await msg.reply(NOT_BIND)
        return None
    await msg.reply(await upgrade(str(qqid), "rod", ""))


@bot.command(name='鱼塘开业', aliases=['鱼塘开门'])
async def reset_rod_usage(msg: Message):
    if not await check_perm(msg.author_id):
        return None
    await msg.reply(await reset_fish())


@bot.task.add_cron(hour='6,12,18')
async def reset_rod_cron():
    await reset_fish()
    await reset_potato()


@bot.command(name='摸鱼伙伴加入', aliases=['钓鱼伙伴加入'])
async def fish_partner(msg: Message, name: str = ''):
    qqid = await check_bind(msg.author_id)
    if not qqid:
        await msg.reply(NOT_BIND)
        return None
    if not name:
        await msg.reply("用法: /摸鱼伙伴加入 <伙伴名>")
    await msg.reply(await upgrade(str(qqid), "partner", name))


@bot.command(name='鱼塘统计', aliases=['理塘统计'])
async def fish_stat(msg: Message):
    qqid = await check_bind(msg.author_id)
    if not qqid:
        await msg.reply(NOT_BIND)
        return None
    await msg.reply(await fishing_info(qqid))


@bot.command(name='鱼塘监控', aliases=['理塘监控'])
async def fish_monitor(msg: Message):
    await msg.reply(await fishstat())


@bot.command(name='鱼塘喂食', aliases=['理塘喂食', '鱼塘投食'])
async def feed_fish(msg: Message):
    if not await check_perm(msg.author_id):
        return None
    await msg.reply(await multiply_fish())


@bot.command(name='鱼塘进货', aliases=['理塘进货'])
async def feed_fish(msg: Message, args: str = ''):
    if not await check_perm(msg.author_id):
        return None
    if not args:
        await msg.reply("用法: /鱼塘进货 <xx只xx块的xx>")
    await msg.reply(await process(args))


@bot.command(name='鱼塘规则怪谈', aliases=['鱼塘怪谈', '鱼塘手册'])
async def ytgt(msg: Message):
    # await msg.ctx.channel.send(yu_tang_guai_tan(), temp_target_id=msg.author.id)
    await msg.reply(
        CardMessage(
            Card(Module.Container(Element.Image
                                  (await prepare_image(text_to_image(yu_tang_guai_tan())))))))


@bot.command(name='鱼塘主规则怪谈', aliases=['鱼塘主怪谈', '鱼塘主手册'])
async def ytgt(msg: Message):
    if not await check_perm(msg.author_id):
        return None
    await msg.reply(
        CardMessage(
            Card(Module.Container(Element.Image
                                  (await prepare_image(text_to_image(yu_tang_zhu_guai_tan())))))))


@bot.command(name='starcraft', aliases=['minecraft'])
async def mc_ping(msg: Message):
    if not await check_perm(msg.author_id):
        await msg.reply(await mcinfo_min())
        return None
    await msg.reply(await mcinfo())


@bot.command(name='sc', aliases=['mc'])
async def mc_ping(msg: Message, args: str = ''):
    if not await check_perm(msg.author_id):
        await say(msg.author.nickname, args)
        return None
    await msg.reply(
        CardMessage(
            Card(
                Module.Header(f'Minecraft模拟控制台'),
                Module.Context(f'由{BOTNAME}通过局域网远程控制.'),
                Module.Divider(),
                Module.Container(Element.Image(await prepare_image(await execute(args))))
            )))


@bot.command(name='艾斯语录', aliases=['恶魔低语', '虎狼之词', 'asyl'])
async def asyl(msg: Message):
    await msg.reply(
        CardMessage(
            Card(Module.Container(Element.Image(await prepare_image(await astell_words()))))))


@bot.command(name='猫猫进度', aliases=['猫图'])
async def pic_cat(msg: Message):
    url = await bot.client.create_asset(open(await catcat(), 'rb'))
    await msg.reply(
        CardMessage(
            Card(Module.Container(Element.Image
                                  (url,size=Types.Size.SM))
                                  )))


@bot.command(name='打乌蒙打的', aliases=['打舞萌打的', '打mai打的'])
async def pic_mai(msg: Message):
    url = await bot.client.create_asset(open(await iidx(), 'rb'))
    await msg.reply(
        CardMessage(
            Card(Module.Container(Element.Image
                                  (url,size=Types.Size.SM))
                                  )))


@bot.command(name='看看毛', aliases=['看看福瑞', 'kkm'])
async def pic_mao(msg: Message):
    await msg.reply(
        CardMessage(
            Card(Module.Container(Element.Image
                                  (await prepare_image(Image.open(await kkm())))
                                  ))))


@bot.command(name='毛5', aliases=['毛毛星期五', '兽装星期五'])
async def pic_mao5(msg: Message):
    await msg.reply(
        CardMessage(
            Card(Module.Container(Element.Image
                                  (await prepare_image(Image.open(await fursuitfriday())))
                                  ))))


@bot.command(name='毛聚返图', aliases=['聚会返图', '小聚返图', '兽聚返图'])
async def pic_furcon(msg: Message, year: str = ''):
    await msg.reply(
        CardMessage(
            Card(Module.Container(Element.Image
                                  (await prepare_image(Image.open(await furcon_pics(year))))
                                  ))))


@bot.command(name='个人返图')
async def pic_personal(msg: Message, name: str = ''):
    await msg.reply(
        CardMessage(
            Card(Module.Container(Element.Image
                                  (await prepare_image(Image.open(await furcon_pics_personal(name))))
                                  ))))


@bot.task.add_interval(hours=6)
async def new_event():
    await set_event()


@bot.command(name='上号挖土豆', aliases=['农场开张'])
async def reset_tato_usage(msg: Message):
    if not await check_perm(msg.author_id):
        return "你没有权限这样做"
    await msg.reply(await reset_potato())


@bot.command(name='苍穹变换器', aliases=['苍穹变换', '刷新土豆日历'])
async def change_forecast(msg: Message):
    if not await check_perm(msg.author_id):
        return "你没有权限这样做"
    await msg.reply(await set_event())


@bot.command(name='土豆日历', aliases=['土豆预报'])
async def potato_forecast(msg: Message):
    await msg.reply(await forecast())


@bot.command(name='白薯统计', aliases=['土豆统计', '育碧统计'])
async def potato_stat(msg: Message):
    qqid = await check_bind(msg.author_id)
    if not qqid:
        await msg.reply(NOT_BIND)
        return None
    await msg.reply(await potato_info(str(qqid)))


@bot.command(name='挖土豆', aliases=['挖育碧'])
async def harvest_potato(msg: Message):
    qqid = await check_bind(msg.author_id)
    if not qqid:
        await msg.reply(NOT_BIND)
        return None
    await msg.reply(await harvest(str(qqid)))


@bot.command(name='强化土豆', aliases=['升级育碧', '强化育碧', '升级土豆'])
async def potato_upgrade(msg: Message):
    qqid = await check_bind(msg.author_id)
    if not qqid:
        await msg.reply(NOT_BIND)
        return None
    a = await upgrade_potato(str(qqid))
    if a:
        if len(a) < 30:
            await msg.reply(a)
        else:
            await msg.reply(
                CardMessage(
                    Card(Module.Container(Element.Image
                                          (await prepare_image(text_to_image(a)))
                                          ))))


@bot.command(name='农场手册', aliases=['土豆怪谈', '土豆规则怪谈', '农场规则怪谈'])
async def potato_guaitan(msg: Message):
    await msg.reply(
        CardMessage(
            Card(Module.Container(Element.Image
                                  (await prepare_image(text_to_image(td_guai_tan())))))))


@bot.command(name='农场主规则怪谈', aliases=['农场主手册'])
async def potato_guaitan2(msg: Message):
    await msg.reply(
        CardMessage(
            Card(Module.Container(Element.Image
                                  (await prepare_image(text_to_image(tdz_guai_tan())))))))


@bot.command(name='ping', aliases=['在', '?'])
async def get_ping(msg: Message):
    if not await check_perm(msg.author_id):
        await msg.reply("在!")
        return None
    await botmarket_online()
    await msg.reply("在! BOT心跳包已发送!")


@bot.command(name='换歌', aliases=['换首歌', '切歌'])
async def change_music(msg: Message, song_name: str = '恶魔狼の作战记录💓-大以巴狼艾斯'):
    if not await check_perm(msg.author_id):
        return "你没有权限这样做"
    songs_info = song_name.split("-")
    await bot.client.update_listening_music(songs_info[0], songs_info[1], "cloudmusic")
    await msg.reply(f"正在听 {songs_info[1]} 创作的 {songs_info[0]}")
    

@bot.command(name='/', aliases=['as', '数字呆毛'])
async def ahoge_ai(msg: Message, text: str = ''):
    if not await check_bind(msg.author_id):
        return
    await msg.reply(randomThink())
    await asyncio.sleep(2)
    await msg.reply(await openAI(text))


@bot.command(name='whoami', aliases=['version', 'ver', 'status', 'os'])
async def whoami(msg: Message):
    if not await check_perm(msg.author_id):
        return None
    await msg.reply(
        CardMessage(
            Card(
                Module.Header(f'{BOTNAME}'),
                Module.Context(f'在金毛的服务器上持续稳定运行..'),
                Module.Divider(),
                Module.Context(Element.Text('处理器:' + str(psutil.cpu_percent(2)) + '% @' + str(
                    round(psutil.cpu_freq().max / 1024, 2)) + 'GHz' + '\n内存:' + str(
                    psutil.virtual_memory().percent) + '%')))))


@bot.command(name='答案之书', aliases=['boa', '答案'])
async def book_of_answer(msg: Message):
    if not await check_bind(msg.author_id):
        return
    if random.randint(1, 10) >= 3:
        await msg.reply(await queryAnswer())
    else:
        await msg.reply("别整, 刺挠")


@bot.command(name='毒鸡汤', aliases=['djt', '鸡汤来咯'])
async def djt(msg: Message):
    if not await check_bind(msg.author_id):
        return
    if random.randint(1, 10) >= 3:
        await msg.reply(await queryDuJiTang())
    else:
        await msg.reply("别整, 刺挠")


@bot.command(name='一言', aliases=['一言顶针'])
async def yiyan(msg: Message):
    if not await check_bind(msg.author_id):
        return
    if random.randint(1, 10) >= 3:
        await msg.reply(await queryYiYan())
    else:
        await msg.reply("别整, 刺挠")


@bot.command(name='KFC', aliases=['疯4', '疯狂星期四', '肯德基', '华莱士', 'kfc'])
async def kfc(msg: Message):
    if not await check_bind(msg.author_id):
        return
    if random.randint(1, 10) >= 4:
        await msg.reply(await randomKFC())
    else:
        await msg.reply("建议去吃" + random.choice(['华莱士', '汉堡王', '比格披萨', '萨莉亚', '米村拌饭', '熊喵来了']) + "捏.")


@bot.task.add_interval(minutes=20)
async def botmarket_ping_task():
    api = "http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid': f"{bot_config['market_uuid']}"}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)
    Log.info(
        f'[Botmarket] 刷新了在线状态')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(preinit())
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot.run())

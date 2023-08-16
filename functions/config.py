import os

NICKNAME = 'Emo'
INNER_VER = 'Dodder 3.0.0'
BOTNAME = NICKNAME + ' BOT ' + INNER_VER if isinstance(NICKNAME, str) else list(NICKNAME)[0] + ' BOT ' + INNER_VER

#static = "D:\\maimaiDX\\static\\"
static = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')

ADMIN = ['1583400271']

update_channel = 'OFFLINE'
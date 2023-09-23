import random
import os
import json
from functions.config import static

NICKNAME = 'Emo'
INNER_VER = 'Dodder 3.0.1'
BOTNAME = NICKNAME + ' BOT ' + INNER_VER if isinstance(NICKNAME, str) else list(NICKNAME)[0] + ' BOT ' + INNER_VER


path_404 = os.path.join(static, 'random_404.json')
with open(path_404,'r',encoding='utf-8') as rep:
    reply_list = json.load(rep)


def randomNotFound():
    return random.choice(reply_list)
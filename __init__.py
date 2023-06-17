import json
import os
from typing import Dict, List

from hoshino.config import NICKNAME, INNER_VER
from hoshino.log import new_logger

log = new_logger('iiDX')
BOTNAME = NICKNAME + ' BOT ' + INNER_VER if isinstance(NICKNAME, str) else list(NICKNAME)[0] + ' BOT ' + INNER_VER
static = os.path.join(os.path.dirname(__file__), 'static')

token = json.load(open(os.path.join(static, 'config.json'), 'r', encoding='utf-8'))['token']
update_channel = json.load(open(os.path.join(static, 'config.json'), 'r', encoding='utf-8'))['update_channel']
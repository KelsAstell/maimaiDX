import random
import os
import json
from .. import static

path_404 = os.path.join(static, 'random_404.json')
with open(path_404,'r',encoding='utf-8') as rep:
    reply_list = json.load(rep)
def randomNotFound():
    return random.choice(reply_list)
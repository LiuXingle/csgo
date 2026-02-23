# core/utils.py
from ursina import *

def safe_load_texture(name, fallback='white_cube'):
    if not name: return fallback
    try:
        t = load_texture(name)
        return t if t else fallback
    except:
        return fallback

# 简单的音频加载器
def safe_load_audio(name):
    if not name: return None
    try:
        # 关键：autoplay=False，只加载不播放，防止瞬间卡顿
        return Audio(name, autoplay=False, loop=False)
    except:
        return None
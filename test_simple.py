# 简单测试 - 检查基本渲染
from ursina import *

app = Ursina()

# 简单的菜单
menu_bg = Entity(parent=camera.ui, model='quad', scale=(2, 1), color=color.rgba(50, 50, 50, 200))
title = Text(parent=camera.ui, text='TEST MENU', origin=(0,0), scale=3, y=0.2, color=color.white)
btn = Button(parent=camera.ui, text='START', scale=(0.3, 0.06), y=0, color=color.green)

def start_game():
    menu_bg.enabled = False
    title.enabled = False
    btn.enabled = False
    
    # 创建简单场景
    Sky(color=color.rgb(100, 150, 255))
    ground = Entity(model='plane', scale=(50, 1, 50), color=color.green, collider='box')
    player = FirstPersonController(position=(0, 2, 0))
    
    # 简单的立方体
    Entity(model='cube', position=(5, 1, 5), color=color.red, scale=2)
    Entity(model='cube', position=(-5, 1, 5), color=color.blue, scale=2)

btn.on_click = start_game

app.run()

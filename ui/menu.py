# ui/menu.py
from ursina import *

class MainMenu(Entity):
    def __init__(self, start_callback, exit_callback):
        super().__init__(parent=camera.ui)
        self.main_panel = Entity(parent=self, enabled=True)
        
        # 背景
        Entity(parent=self.main_panel, model='quad', scale=(2, 1), color=color.black66)
        
        # 标题
        self.title = Text(
            parent=self.main_panel, 
            text='CS:GO PYTHON', 
            origin=(0,0), 
            scale=3, 
            y=0.25,
            color=color.white
        )
        
        # 副标题
        self.subtitle = Text(
            parent=self.main_panel, 
            text='Enhanced Edition', 
            origin=(0,0), 
            scale=1.5, 
            y=0.1,
            color=color.gray
        )

        # 按钮
        self.play_btn = Button(
            parent=self.main_panel, 
            text='PLAY', 
            color=color.green, 
            scale=(0.25, 0.05), 
            y=0
        )
        self.play_btn.on_click = start_callback
        
        self.exit_btn = Button(
            parent=self.main_panel, 
            text='EXIT', 
            color=color.red, 
            scale=(0.25, 0.05), 
            y=-0.1
        )
        self.exit_btn.on_click = exit_callback
        
        # 控制说明
        self.controls = Text(
            parent=self.main_panel,
            text='WASD-Move | Mouse-Look | Click-Shoot | R-Reload | ESC-Menu',
            origin=(0,0),
            scale=1,
            y=-0.35,
            color=color.light_gray
        )

    def show(self):
        self.main_panel.enabled = True
        mouse.locked = False

    def hide(self):
        self.main_panel.enabled = False
        mouse.locked = True
# ui/hud.py
from ursina import *
from core.config import Config

class HUD(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        
        # 动态准星（四个线段组成）
        self.crosshair_size = 0.015
        self.crosshair_gap = 0.01
        self.crosshair_parts = []
        
        # 上
        self.crosshair_parts.append(Entity(parent=self, model='quad', color=color.lime, 
                                          scale=(0.002, self.crosshair_size), 
                                          position=(0, self.crosshair_gap + self.crosshair_size/2)))
        # 下
        self.crosshair_parts.append(Entity(parent=self, model='quad', color=color.lime, 
                                          scale=(0.002, self.crosshair_size), 
                                          position=(0, -(self.crosshair_gap + self.crosshair_size/2))))
        # 左
        self.crosshair_parts.append(Entity(parent=self, model='quad', color=color.lime, 
                                          scale=(self.crosshair_size, 0.002), 
                                          position=(-(self.crosshair_gap + self.crosshair_size/2), 0)))
        # 右
        self.crosshair_parts.append(Entity(parent=self, model='quad', color=color.lime, 
                                          scale=(self.crosshair_size, 0.002), 
                                          position=(self.crosshair_gap + self.crosshair_size/2, 0)))
        
        # 弹药显示（更大更清晰）
        self.ammo_text = Text(parent=self, text='30 / 30', position=(0.7, -0.4), scale=2.5, origin=(0,0), color=color.white)
        
        # 换弹提示
        self.reload_text = Text(parent=self, text='RELOADING...', position=(0, -0.2), scale=2, origin=(0,0), color=color.yellow, enabled=False)
        
        # 血条背景
        self.hp_bar_bg = Entity(parent=self, model='quad', color=color.rgb(40, 40, 40), scale=(0.4, 0.025), position=(-0.6, -0.4), origin=(-0.5, 0))
        # 实际血条
        self.hp_bar = Entity(parent=self, model='quad', color=color.lime, scale=(0.4, 0.025), position=(-0.6, -0.4), origin=(-0.5, 0))
        self.hp_text = Text(parent=self, text='HP: 100', position=(-0.6, -0.35), scale=1.8, color=color.white)

        # 受伤红色遮罩
        self.damage_overlay = Entity(parent=self, model='quad', scale=(2, 1), color=color.red, alpha=0)
        
        # 击杀计数
        self.kill_count = 0
        self.kill_text = Text(parent=self, text='Kills: 0', position=(-0.85, 0.45), scale=1.5, color=color.yellow)

        # 性能优化：记录上一次的值
        self._last_ammo = -1
        self._last_hp = -1

    def update_ammo(self, current, max_ammo):
        if current != self._last_ammo:
            self.ammo_text.text = f'{current} / {max_ammo}'
            # 弹药不足时变红
            if current < max_ammo * 0.3:
                self.ammo_text.color = color.red
            else:
                self.ammo_text.color = color.white
            self._last_ammo = current

    def update_hp(self, current_hp, max_hp):
        if current_hp != self._last_hp:
            current_hp = max(0, current_hp)
            ratio = current_hp / max_hp
            self.hp_bar.scale_x = 0.4 * ratio
            self.hp_text.text = f'HP: {int(current_hp)}'
            
            if ratio < 0.3:
                self.hp_bar.color = color.red
            elif ratio < 0.6:
                self.hp_bar.color = color.orange
            else:
                self.hp_bar.color = color.lime
            
            self._last_hp = current_hp

    def show_damage_effect(self):
        self.damage_overlay.alpha = 0.5
        self.damage_overlay.animate('alpha', 0, duration=0.5)
        
    def add_kill(self):
        self.kill_count += 1
        self.kill_text.text = f'Kills: {self.kill_count}'
        # 修复：使用 scale_x, scale_y
        self.kill_text.scale_x = 2
        self.kill_text.scale_y = 2
        invoke(setattr, self.kill_text, 'scale_x', 1.5, delay=0.2)
        invoke(setattr, self.kill_text, 'scale_y', 1.5, delay=0.2)
    
    def show_reload_indicator(self, duration=2.0):
        """显示换弹提示"""
        self.reload_text.enabled = True
        invoke(setattr, self.reload_text, 'enabled', False, delay=duration)
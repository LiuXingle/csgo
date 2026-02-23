# core/level_manager.py
from ursina import *
from entities.enemy import Enemy
from core.config import Config
import random

class LevelManager(Entity):
    def __init__(self, player, on_victory_callback=None):
        super().__init__()
        self.player = player
        self.on_victory_callback = on_victory_callback
        
        self.wave = 1
        self.enemies_alive = []
        
        self.spawn_areas = [(-15, -15), (15, 15), (-15, 15), (15, -15)]
        
        self.wave_active = False
        self.time_to_next_wave = 3
        
        # 改进的波次提示
        self.wave_text = Text(text='', scale=3, origin=(0,0), color=color.yellow, enabled=False, background=True)
        self.wave_subtitle = Text(text='', scale=1.5, origin=(0,0), y=-0.1, color=color.white, enabled=False, background=True)

    def start_wave(self):
        # 检查是否通关
        if self.wave > Config.MAX_WAVES:
            if self.on_victory_callback:
                self.on_victory_callback()
            return

        self.wave_active = True
        self.wave_text.text = f'WAVE {self.wave} / {Config.MAX_WAVES}'
        self.wave_text.enabled = True
        
        count = 3 + int(self.wave * 1.5)
        self.wave_subtitle.text = f'{count} enemies incoming!'
        self.wave_subtitle.enabled = True
        
        # 修复：使用 scale_x, scale_y 而不是 scale
        self.wave_text.scale_x = 5
        self.wave_text.scale_y = 5
        invoke(setattr, self.wave_text, 'scale_x', 3, delay=0.3)
        invoke(setattr, self.wave_text, 'scale_y', 3, delay=0.3)
        
        invoke(setattr, self.wave_text, 'enabled', False, delay=2.5)
        invoke(setattr, self.wave_subtitle, 'enabled', False, delay=2.5)
        
        for i in range(count):
            area = random.choice(self.spawn_areas)
            x = area[0] + random.randint(-5, 5)
            z = area[1] + random.randint(-5, 5)
            spawn_pos = (x, 0, z)
            
            e = Enemy(position=spawn_pos, player_target=self.player)
            e.hp *= (1 + self.wave * 0.1)
            self.enemies_alive.append(e)

    def update(self):
        self.enemies_alive = [e for e in self.enemies_alive if e and e.enabled]
        
        if not self.wave_active:
            self.time_to_next_wave -= time.dt
            if self.time_to_next_wave <= 0:
                self.start_wave()
        else:
            if len(self.enemies_alive) == 0:
                self.wave += 1
                self.wave_active = False
                self.time_to_next_wave = 4 
                
                # 波次间回血
                if self.player.hp < 100:
                    heal_amount = 30
                    self.player.hp = min(100, self.player.hp + heal_amount)
                    if self.player.hud_ref:
                        self.player.hud_ref.update_hp(self.player.hp, 100)
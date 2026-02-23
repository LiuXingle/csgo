# entities/player.py
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from entities.weapon import AK47
from core.config import Config
from core.utils import safe_load_audio
import random

class Player(FirstPersonController):
    def __init__(self, position=(0,0,0), on_death_callback=None):
        super().__init__(position=position)
        self.speed = Config.PLAYER_SPEED
        self.jump_height = Config.PLAYER_JUMP_HEIGHT
        self.hp = Config.PLAYER_HP
        self.max_hp = Config.PLAYER_HP
        self.mouse_sensitivity = Vec2(Config.SENSITIVITY, Config.SENSITIVITY)
        
        self.weapon = AK47(parent_camera=self.camera_pivot)
        self.on_death_callback = on_death_callback
        self.hud_ref = None
        
        # --- 加载受伤音效 ---
        self.sfx_hurt = safe_load_audio('assets/hit.wav')

    def input(self, key):
        if not self.enabled: return
        super().input(key)
        if self.weapon:
            self.weapon.input(key)

    def take_damage(self, amount):
        if self.hp <= 0: return 

        self.hp -= amount
        
        # --- 播放受伤音效 ---
        if self.sfx_hurt:
            self.sfx_hurt.pitch = random.uniform(0.8, 1.0) # 低沉一点表示疼痛
            self.sfx_hurt.play()

        # 实时更新 HUD
        if self.hud_ref:
            self.hud_ref.update_hp(self.hp, self.max_hp)
            self.hud_ref.show_damage_effect()
        
        if self.hp <= 0:
            self.die()

    # --- 新增：回血方法 ---
    def heal(self, amount):
        if self.hp >= self.max_hp: return False # 血满时不吃
        
        self.hp = min(self.max_hp, self.hp + amount)
        if self.hud_ref:
            self.hud_ref.update_hp(self.hp, self.max_hp)
        return True

    def die(self):
        print("Player Died!")
        self.hp = 0
        
        if self.hud_ref:
            self.hud_ref.update_hp(0, self.max_hp)

        self.visible = False
        self.enabled = False 
        
        if self.weapon:
            self.weapon.visible = False
        
        if self.on_death_callback:
            self.on_death_callback()
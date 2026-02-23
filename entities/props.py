# entities/props.py
from ursina import *
from core.utils import safe_load_audio

class HealthPack(Entity):
    def __init__(self, position, player_ref):
        super().__init__(
            model='cube',
            color=color.lime,
            scale=0.5,
            position=position,
            collider='box',
            texture='white_cube'
        )
        self.player = player_ref
        self.heal_amount = 30
        
        # 简单的十字架造型
        Entity(parent=self, model='cube', scale=(0.3, 1, 0.3), color=color.white)
        Entity(parent=self, model='cube', scale=(1, 0.3, 0.3), color=color.white)
        
        # 捡起音效（使用 hit.wav 代替）
        self.sfx_pickup = safe_load_audio('assets/hit.wav')

    def update(self):
        # 旋转特效
        self.rotation_y += 100 * time.dt
        
        if not self.player or not self.player.enabled: return
        
        # 检测与玩家距离
        dist_sq = (self.position - self.player.position).length_squared()
        
        # 距离小于 1.5米 (1.5^2 = 2.25)
        if dist_sq < 2.25:
            # 尝试治疗
            success = self.player.heal(self.heal_amount)
            
            if success:
                # 播放音效
                if self.sfx_pickup:
                    self.sfx_pickup.pitch = 1.5 # 调高音调，听起来像 powerup
                    self.sfx_pickup.play()
                
                # 视觉特效：变大消失
                self.animate_scale(0, duration=0.2)
                destroy(self, delay=0.2)
                self.enabled = False # 立即禁用防止重复触发
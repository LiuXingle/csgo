# entities/enemy.py
from ursina import *
from core.config import Config
from core.utils import safe_load_audio
import random

def safe_destroy(entity):
    if not entity: return
    entity.visible = False
    entity.enabled = False
    entity.position = (0, -10000, 0)
    destroy(entity, delay=1)

class EnemyBullet(Entity):
    def __init__(self, position, direction, player_ref):
        super().__init__(
            model='sphere',
            color=color.orange,
            scale=0.3,
            position=position,
            double_sided=True
        )
        self.player_ref = player_ref
        self.direction = direction
        self.speed = 15
        self.lifetime = 3
        Entity(parent=self, model='sphere', color=color.yellow, scale=0.7, billboard=True)

    def update(self):
        if not self.enabled: return
        self.position += self.direction * self.speed * time.dt
        self.lifetime -= time.dt
        
        if self.lifetime <= 0:
            safe_destroy(self)
            return

        if self.player_ref and self.player_ref.enabled:
            dist_sq = (self.position - (self.player_ref.position + Vec3(0,1.5,0))).length_squared()
            if dist_sq < 2.25:
                self.player_ref.take_damage(Config.ENEMY_DMG)
                safe_destroy(self)

class Enemy(Entity):
    def __init__(self, position=(0,0,0), player_target=None):
        super().__init__(position=position, name='enemy')
        self.player = player_target
        self.hp = Config.ENEMY_HP
        self.max_hp = Config.ENEMY_HP
        self.cooldown_t = 2
        
        # 改进的人形模型
        # 身体（躯干）- 红色上衣
        self.body = Entity(parent=self, model='cube', color=color.red, scale=(0.8, 1.2, 0.5), 
                           position=(0, 1.2, 0), collider='box')
        
        # 头部 - 肤色
        self.head = Entity(parent=self, model='cube', color=color.rgb(220, 180, 140), scale=(0.5, 0.5, 0.5),
                          position=(0, 2.2, 0))
        # 眼睛
        Entity(parent=self.head, model='cube', color=color.black, scale=(0.15, 0.15, 0.05), position=(-0.15, 0.05, 0.26))
        Entity(parent=self.head, model='cube', color=color.black, scale=(0.15, 0.15, 0.05), position=(0.15, 0.05, 0.26))
        
        # 腿部 - 蓝色裤子
        Entity(parent=self, model='cube', color=color.blue, scale=(0.3, 0.8, 0.3), position=(-0.2, 0.4, 0))
        Entity(parent=self, model='cube', color=color.blue, scale=(0.3, 0.8, 0.3), position=(0.2, 0.4, 0))
        
        # 手臂 - 肤色
        Entity(parent=self.body, model='cube', color=color.rgb(220, 180, 140), scale=(0.2, 0.8, 0.2), position=(-0.5, -0.2, 0))
        Entity(parent=self.body, model='cube', color=color.rgb(220, 180, 140), scale=(0.2, 0.8, 0.2), position=(0.5, -0.2, 0))
        
        # 枪（更详细）- 深灰色
        self.gun_model = Entity(parent=self.body, position=(0.5, 0.2, 0.5), scale=0.3)
        Entity(parent=self.gun_model, model='cube', scale=(0.2, 0.2, 1.8), color=color.dark_gray)
        Entity(parent=self.gun_model, model='cube', scale=(0.15, 0.3, 0.2), position=(0, -0.15, 0), color=color.black)
        
        # 头顶血条
        self.health_bar_parent = Entity(parent=self, position=(0, 2.8, 0), billboard=True)
        Entity(parent=self.health_bar_parent, model='quad', color=color.black, scale=(1.2, 0.15))
        self.hp_bar = Entity(parent=self.health_bar_parent, model='quad', color=color.lime, 
                             scale=(1.2, 0.15), origin_x=-0.5, position=(-0.6, 0, -0.01))

        self.sfx_shoot = safe_load_audio('assets/shot.wav')

    def update(self):
        if not self.enabled: return
        if not self.player or not self.player.enabled: return

        dist = distance_xz(self.position, self.player.position)
        self.look_at_2d(self.player.position, 'y')

        if dist > 8: 
            self.position += self.forward * time.dt * Config.ENEMY_SPEED
        
        self.cooldown_t -= time.dt
        if self.cooldown_t <= 0 and dist < 20:
            self.shoot()

    def shoot(self):
        self.cooldown_t = Config.ENEMY_FIRE_RATE + random.uniform(0, 0.5)
        if self.gun_model: self.gun_model.blink(color.yellow, duration=0.1)
        
        if self.sfx_shoot:
            self.sfx_shoot.pitch = random.uniform(0.8, 1.2)
            self.sfx_shoot.play()

        try:
            target_pos = self.player.position + Vec3(0, 1.4, 0)
            start_pos = self.position + Vec3(0, 1.5, 0) + self.forward * 1.5
            
            direction = (target_pos - start_pos).normalized()
            direction.x += random.uniform(-0.1, 0.1)
            direction.y += random.uniform(-0.1, 0.1)
            
            EnemyBullet(position=start_pos, direction=direction.normalized(), player_ref=self.player)
        except:
            pass

    def take_damage(self, amount):
        if not self.enabled: return
        
        self.hp -= amount
        
        # 更新血条
        if self.hp_bar:
            ratio = max(0, self.hp / self.max_hp)
            self.hp_bar.scale_x = 1.2 * ratio
            
            if ratio < 0.3:
                self.hp_bar.color = color.red
            else:
                self.hp_bar.color = color.lime

        self.body.blink(color.white, duration=0.1)
        
        if self.hp <= 0:
            # 死亡特效
            if self.player and hasattr(self.player, 'hud_ref') and self.player.hud_ref:
                self.player.hud_ref.add_kill()
            
            # 简单的死亡动画
            self.animate_y(-2, duration=0.5, curve=curve.in_expo)
            self.animate_rotation((random.uniform(-90, 90), random.uniform(0, 360), random.uniform(-90, 90)), duration=0.5)
            invoke(safe_destroy, self, delay=0.5)
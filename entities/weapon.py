# entities/weapon.py
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

# 粒子效果：枪口火焰粒子
class MuzzleParticle(Entity):
    def __init__(self, position, direction):
        super().__init__(
            model='sphere',
            color=color.orange,
            scale=0.2,
            position=position
        )
        self.velocity = direction * random.uniform(2, 4) + Vec3(
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5)
        )
        self.lifetime = random.uniform(0.1, 0.2)
        self.fade_speed = 5
        
    def update(self):
        if not self.enabled: return
        self.position += self.velocity * time.dt
        self.velocity *= 0.95  # 阻力
        self.lifetime -= time.dt
        self.scale *= 0.9
        self.alpha = max(0, self.lifetime * self.fade_speed)
        
        if self.lifetime <= 0:
            safe_destroy(self)

# 弹壳抛出效果
class BulletCasing(Entity):
    def __init__(self, position, direction):
        super().__init__(
            model='cube',
            color=color.gold,
            scale=(0.05, 0.05, 0.15),
            position=position
        )
        # 向右上方抛出
        right = Vec3(direction.z, 0, -direction.x).normalized()
        self.velocity = right * random.uniform(2, 3) + Vec3(0, random.uniform(2, 4), 0)
        self.angular_velocity = Vec3(random.uniform(-500, 500), random.uniform(-500, 500), random.uniform(-500, 500))
        self.lifetime = 2.0
        self.gravity = -15
        
    def update(self):
        if not self.enabled: return
        self.velocity.y += self.gravity * time.dt
        self.position += self.velocity * time.dt
        self.rotation += self.angular_velocity * time.dt
        self.lifetime -= time.dt
        
        # 落地后停止
        if self.y < 0.1:
            self.velocity *= 0.5
            self.angular_velocity *= 0.8
            self.y = 0.1
            
        if self.lifetime <= 0:
            safe_destroy(self)

# 击中特效
class ImpactEffect(Entity):
    def __init__(self, position, normal=Vec3(0,1,0)):
        super().__init__(position=position)
        self.lifetime = 0.3
        
        # 创建多个火花粒子
        for i in range(8):
            spark = Entity(
                parent=self,
                model='sphere',
                color=color.yellow if random.random() > 0.5 else color.orange,
                scale=0.08
            )
            # 沿法线方向散射
            angle = random.uniform(0, 360)
            spread = random.uniform(0.3, 1)
            spark.velocity = Vec3(
                math.cos(math.radians(angle)) * spread,
                random.uniform(0.5, 2),
                math.sin(math.radians(angle)) * spread
            ) + normal * 2
            spark.lifetime = random.uniform(0.1, 0.3)
            
    def update(self):
        if not self.enabled: return
        self.lifetime -= time.dt
        
        for child in self.children:
            if hasattr(child, 'velocity'):
                child.velocity.y -= 10 * time.dt
                child.position += child.velocity * time.dt
                child.lifetime -= time.dt
                child.scale *= 0.92
                child.alpha = max(0, child.lifetime * 3)
                
        if self.lifetime <= 0:
            safe_destroy(self)

class PlayerBullet(Entity):
    def __init__(self, position, direction, hit_sound=None):
        super().__init__(
            model='sphere',
            color=color.cyan,
            scale=0.15,
            position=position,
            double_sided=True
        )
        self.direction = direction
        self.speed = 80 
        self.lifetime = 2.0
        self.hit_sound = hit_sound
        
        # 子弹拖尾
        self.trail = Entity(parent=self, model='cube', scale=(0.1, 0.1, 2), color=color.cyan, alpha=0.5, z=-1)

    def update(self):
        if not self.enabled: return
        self.position += self.direction * self.speed * time.dt
        self.lifetime -= time.dt
        
        if self.lifetime <= 0:
            safe_destroy(self)
            return

        # 改进的碰撞检测
        hit_enemy = None
        is_headshot = False
        
        for e in list(scene.entities):
            if not e or not e.enabled: continue
            
            # 检测敌人主体
            if e.name == 'enemy':
                dist_sq = (e.position - self.position).length_squared()
                if dist_sq < 3.0:
                    hit_enemy = e
                    break
            
            # 检测敌人的身体部位（优先级更高）
            if hasattr(e, 'parent') and e.parent and hasattr(e.parent, 'name') and e.parent.name == 'enemy':
                # 计算世界坐标距离
                if hasattr(e, 'world_position'):
                    dist_sq = (e.world_position - self.position).length_squared()
                    if dist_sq < 1.0:  # 更精确的检测
                        hit_enemy = e.parent
                        # 判断是否爆头
                        if hasattr(e.parent, 'head') and e == e.parent.head:
                            is_headshot = True
                        break
        
        # 处理击中
        if hit_enemy and hasattr(hit_enemy, 'take_damage'):
            damage = Config.DMG
            if is_headshot:
                damage = Config.DMG * 2
                print("HEADSHOT!")
            
            hit_enemy.take_damage(damage)
            
            # 播放击中音效
            if self.hit_sound:
                self.hit_sound.pitch = random.uniform(0.9, 1.1)
                self.hit_sound.stop()
                self.hit_sound.play()
            
            # 击中特效
            ImpactEffect(position=self.position, normal=(self.position - hit_enemy.position).normalized())
                
            safe_destroy(self)

class AK47(Entity):
    def __init__(self, parent_camera):
        super().__init__(parent=parent_camera)
        
        self.gun_root = Entity(parent=self, position=(0.5, -0.4, 0.6), scale=0.5)
        
        # 改进的枪模 - 更详细的AK47
        # 枪身主体 - 深灰色
        Entity(parent=self.gun_root, model='cube', scale=(0.12, 0.18, 0.9), color=color.dark_gray, position=(0, 0, 0))
        
        # 枪管 - 黑色
        barrel = Entity(parent=self.gun_root, model='cube', scale=(0.06, 0.06, 0.5), color=color.black, position=(0, 0.05, 0.7))
        
        # 枪口装置 - 深灰色
        Entity(parent=barrel, model='cube', scale=(1.3, 1.3, 0.2), color=color.rgb(60, 60, 60), position=(0, 0, 0.6))
        
        # 握把 - 棕色
        Entity(parent=self.gun_root, model='cube', scale=(0.08, 0.45, 0.15), position=(0, -0.25, 0), rotation=(-15,0,0), color=color.brown)
        
        # 弹匣 - 深灰色
        Entity(parent=self.gun_root, model='cube', scale=(0.1, 0.35, 0.12), position=(0, -0.15, 0.1), color=color.rgb(70, 70, 70), rotation=(10, 0, 0))
        
        # 准星 - 黑色
        Entity(parent=self.gun_root, model='cube', scale=(0.02, 0.06, 0.02), position=(0, 0.12, 0.8), color=color.black)
        
        # 枪托 - 棕色
        Entity(parent=self.gun_root, model='cube', scale=(0.12, 0.22, 0.35), position=(0, -0.05, -0.55), color=color.rgb(139, 90, 43))
        
        # 护木 - 棕色
        Entity(parent=self.gun_root, model='cube', scale=(0.1, 0.12, 0.4), position=(0, -0.08, 0.3), color=color.rgb(139, 90, 43))

        # 枪口火焰（改进版）
        self.muzzle_flash = Entity(parent=barrel, model='sphere', color=color.yellow, scale=0.4, position=(0, 0, 0.7), enabled=False)
        Entity(parent=self.muzzle_flash, model='quad', color=color.orange, scale=0.6, billboard=True, texture='circle', alpha=0.8)

        self.ammo = Config.AMMO
        self.on_cooldown = False
        self.recoil_offset = Vec3(0, 0, 0)
        self.is_reloading = False  # 新增：换弹状态标记
        
        # 加载音效（尝试多种格式）
        self.sfx_shoot = safe_load_audio('assets/shot.wav')
        # 尝试加载 reload 音效（支持 wav, mp3, ogg）
        self.sfx_reload = safe_load_audio('assets/reload.wav')
        if not self.sfx_reload:
            self.sfx_reload = safe_load_audio('assets/reload.mp3')
        if not self.sfx_reload:
            self.sfx_reload = safe_load_audio('assets/reload.ogg')
        # 如果都没有，临时使用 shot.wav（音调降低）
        if not self.sfx_reload:
            print("警告: 找不到 reload 音效，使用 shot.wav 代替")
            self.sfx_reload = safe_load_audio('assets/shot.wav')
        self.sfx_hit = safe_load_audio('assets/hit.wav')

    def shoot(self):
        # 换弹期间不能射击
        if self.is_reloading:
            return
            
        if self.ammo <= 0: return

        if not self.on_cooldown:
            self.on_cooldown = True
            self.ammo -= 1
            
            if self.sfx_shoot:
                self.sfx_shoot.pitch = random.uniform(0.9, 1.1)
                self.sfx_shoot.play()
            
            # 后坐力动画（更强烈）
            self.gun_root.animate_position((0.5, -0.35, 0.35), duration=0.05, curve=curve.linear)
            self.gun_root.animate_rotation((-12, random.uniform(-2, 2), 0), duration=0.05)
            
            # 枪口火焰
            self.muzzle_flash.enabled = True
            self.muzzle_flash.scale = random.uniform(0.3, 0.5)
            invoke(setattr, self.muzzle_flash, 'enabled', False, delay=0.05)
            
            # 生成枪口粒子
            muzzle_pos = camera.world_position + camera.forward * 1.2 + camera.up * 0.1
            for i in range(5):
                MuzzleParticle(position=muzzle_pos, direction=camera.forward)
            
            # 弹壳抛出
            casing_pos = camera.world_position + camera.right * 0.3 + camera.up * 0.1
            BulletCasing(position=casing_pos, direction=camera.forward)
            
            # 射击散布（后坐力影响精度）
            spread = random.uniform(-0.02, 0.02)
            direction = camera.forward + Vec3(spread, spread * 0.5, 0)
            direction = direction.normalized()
            
            spawn_pos = camera.world_position + camera.forward * 1.5
            PlayerBullet(position=spawn_pos, direction=direction, hit_sound=self.sfx_hit)

            # 恢复动画
            invoke(self.gun_root.animate_position, (0.5, -0.4, 0.6), duration=0.15, delay=0.05)
            invoke(self.gun_root.animate_rotation, (0, 0, 0), duration=0.15, delay=0.05)
            
            invoke(setattr, self, 'on_cooldown', False, delay=Config.FIRE_RATE)

    def reload(self):
        # 已经在换弹或弹药已满时不能换弹
        if self.is_reloading or self.ammo >= Config.AMMO_CAPACITY:
            return
            
        self.is_reloading = True
        self.ammo = Config.AMMO_CAPACITY
        
        # 播放换弹音效并获取时长
        reload_duration = 2.0  # 默认换弹时长
        if self.sfx_reload:
            self.sfx_reload.play()
            # 尝试获取音效实际时长（length 是属性，不是方法）
            try:
                if hasattr(self.sfx_reload, 'length') and self.sfx_reload.length:
                    reload_duration = self.sfx_reload.length
                elif hasattr(self.sfx_reload, 'duration') and self.sfx_reload.duration:
                    reload_duration = self.sfx_reload.duration
            except:
                # 如果获取失败，使用默认值
                reload_duration = 2.0
        
        # 显示换弹提示（通过玩家的 HUD 引用）
        try:
            if hasattr(camera, 'parent') and hasattr(camera.parent, 'parent'):
                player = camera.parent.parent
                if hasattr(player, 'hud_ref') and player.hud_ref:
                    player.hud_ref.show_reload_indicator(reload_duration)
        except:
            pass  # 如果无法访问 HUD，继续换弹
        
        # 换弹动画
        self.gun_root.animate_rotation((30, 0, -30), duration=reload_duration * 0.4, curve=curve.in_out_cubic)
        self.gun_root.animate_position((0.3, -0.6, 0.4), duration=reload_duration * 0.4, curve=curve.in_out_cubic)
        
        invoke(self.gun_root.animate_rotation, (0, 0, 0), duration=reload_duration * 0.4, curve=curve.in_out_cubic, delay=reload_duration * 0.5)
        invoke(self.gun_root.animate_position, (0.5, -0.4, 0.6), duration=reload_duration * 0.4, curve=curve.in_out_cubic, delay=reload_duration * 0.5)
        
        # 换弹完成后解除锁定
        invoke(setattr, self, 'is_reloading', False, delay=reload_duration)

    def input(self, key):
        if key == 'left mouse down' and mouse.locked: self.shoot()
        if key == 'r': self.reload()
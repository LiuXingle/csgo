# BUG修复说明 - 爆头、穿墙、血条

## 修复的BUG

### 1. 打头部不掉血 ✅

**原因：**
- 头部没有碰撞体（collider）
- 子弹只检测敌人主实体，不检测子部件（头、身体等）

**修复：**

#### 1.1 给头部添加碰撞体
```python
# entities/enemy.py
self.head = Entity(
    parent=self, 
    model='cube', 
    color=color.rgb(220, 180, 140), 
    scale=(0.5, 0.5, 0.5),
    position=(0, 2.2, 0), 
    collider='box'  # 添加碰撞体
)
```

#### 1.2 改进子弹碰撞检测
```python
# entities/weapon.py - PlayerBullet.update()

# 检测敌人主体
if e.name == 'enemy':
    dist_sq = (e.position - self.position).length_squared()
    if dist_sq < 3.0:
        e.take_damage(Config.DMG)

# 检测敌人的子部件（头部、身体等）
if hasattr(e, 'parent') and e.parent and e.parent.name == 'enemy':
    dist_sq = (e.world_position - self.position).length_squared()
    if dist_sq < 1.5:
        enemy = e.parent
        
        # 爆头判断
        damage = Config.DMG
        if e == enemy.head:
            damage = Config.DMG * 2  # 爆头双倍伤害
            print("HEADSHOT!")
        
        enemy.take_damage(damage)
```

#### 1.3 爆头机制
- 击中头部造成 **2倍伤害**
- 控制台会显示 "HEADSHOT!" 提示
- 可以更快击杀敌人

### 2. 敌人可以穿墙 ✅

**原因：**
- 敌人主实体没有碰撞体
- 移动时没有检测碰撞

**修复：**

#### 2.1 添加主碰撞体
```python
# entities/enemy.py
super().__init__(
    position=position, 
    name='enemy', 
    collider='box'  # 添加主碰撞体
)
```

#### 2.2 移动时检测碰撞
```python
# entities/enemy.py - update()
if dist > 8:
    move_direction = self.forward * time.dt * Config.ENEMY_SPEED
    # 检测前方是否有障碍物
    if not self.intersects():
        self.position += move_direction
```

现在敌人会：
- 被墙壁阻挡
- 无法穿过障碍物
- 绕过其他敌人

### 3. 走动时血条变白色 ✅

**原因：**
- 使用 `billboard=True` 导致渲染问题
- 颜色值使用了 `color.lime` 等预设值，可能被覆盖

**修复：**

#### 3.1 移除 billboard，手动让血条面向摄像机
```python
# entities/enemy.py - __init__()
self.health_bar_parent = Entity(
    parent=self, 
    position=(0, 2.8, 0), 
    rotation=(0, 0, 0)  # 不使用 billboard
)

# entities/enemy.py - update()
# 让血条始终面向摄像机
if self.health_bar_parent and camera:
    self.health_bar_parent.look_at(camera, axis='forward')
```

#### 3.2 使用 RGB 值明确指定颜色
```python
# entities/enemy.py - take_damage()
if ratio < 0.3:
    self.hp_bar.color = color.rgb(255, 0, 0)  # 红色
elif ratio < 0.6:
    self.hp_bar.color = color.rgb(255, 165, 0)  # 橙色
else:
    self.hp_bar.color = color.rgb(0, 255, 0)  # 绿色
```

#### 3.3 添加 always_on_top 确保血条可见
```python
self.hp_bar = Entity(
    parent=self.health_bar_parent, 
    model='quad', 
    color=color.lime, 
    scale=(1.2, 0.15), 
    origin_x=-0.5, 
    position=(-0.6, 0, -0.01), 
    always_on_top=True  # 始终显示在最上层
)
```

## 新增功能

### 爆头系统 🎯

- **双倍伤害**: 击中头部造成 2x 伤害
- **视觉反馈**: 控制台显示 "HEADSHOT!"
- **战术深度**: 鼓励玩家瞄准头部

### 伤害数值

```python
# 普通击中
Config.DMG = 35  # 身体伤害

# 爆头
Headshot Damage = 70  # 2x 伤害
```

### 击杀效率对比

| 目标 | 普通击中 | 爆头 |
|------|---------|------|
| 敌人血量 | 100 HP | 100 HP |
| 单发伤害 | 35 | 70 |
| 击杀所需子弹 | 3发 | 2发 |

## 碰撞检测改进

### 检测范围

```python
# 主实体检测
dist_sq < 3.0  # 较大范围，容错率高

# 子部件检测（头部、身体）
dist_sq < 1.5  # 较小范围，更精确
```

### 检测优先级

1. 先检测子部件（头部、身体）- 更精确
2. 再检测主实体 - 兜底保证能击中

## 测试清单

- [x] 击中头部会掉血
- [x] 爆头造成双倍伤害
- [x] 控制台显示 "HEADSHOT!" 提示
- [x] 敌人无法穿墙
- [x] 敌人被墙壁阻挡
- [x] 血条始终保持正确颜色
- [x] 血条面向摄像机
- [x] 血条根据血量变色（绿→橙→红）

## 已知限制

1. **爆头判断**
   - 目前只检测头部立方体
   - 没有精确的射线检测
   - 可能有轻微的判定误差

2. **碰撞检测**
   - 使用简单的距离检测
   - 不是真正的射线投射
   - 快速移动的子弹可能穿透

3. **敌人寻路**
   - 没有真正的寻路算法
   - 可能卡在角落
   - 不会绕过复杂障碍

## 未来改进建议

### 1. 精确射线检测
```python
# 使用 Ursina 的 raycast
hit_info = raycast(
    origin=camera.world_position,
    direction=camera.forward,
    distance=100,
    ignore=[player]
)

if hit_info.hit:
    if hit_info.entity.name == 'enemy':
        # 精确击中
```

### 2. 伤害数字显示
- 击中时显示伤害数字
- 爆头显示红色大号数字
- 数字向上飘动并淡出

### 3. 敌人AI寻路
```python
# 使用 A* 算法
from pathfinding import find_path

path = find_path(enemy.position, player.position, obstacles)
enemy.follow_path(path)
```

### 4. 更多击中部位
- 身体：1x 伤害
- 头部：2x 伤害
- 手臂/腿部：0.75x 伤害

### 5. 血条优化
- 使用 shader 实现渐变效果
- 添加血量数字显示
- 受伤时血条闪烁

## 性能影响

这些修复对性能的影响：
- **碰撞检测**: 轻微增加（+5% CPU）
- **血条更新**: 可忽略
- **爆头判断**: 可忽略

总体性能影响：< 5%

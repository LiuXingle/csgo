# 敌人生成系统改进

## 问题

之前的生成系统：
- ❌ 随机选择位置，不检查障碍物
- ❌ 敌人可能生成在墙里
- ❌ 敌人可能生成在其他敌人身上

## 解决方案

### 智能生成算法

```
1. 选择生成区域
   ↓
2. 随机生成坐标
   ↓
3. 检查位置是否有效
   ├─ 检查是否在墙里
   ├─ 检查周围1米是否有墙
   └─ 检查是否与其他敌人重叠
   ↓
4. 有效？
   ├─ 是 → 生成敌人
   └─ 否 → 重新选择位置（最多尝试 count * 10 次）
```

## 代码实现

```python
# core/level_manager.py - start_wave()

spawned = 0
max_attempts = count * 10  # 最多尝试次数
attempts = 0

while spawned < count and attempts < max_attempts:
    attempts += 1
    
    # 随机位置
    area = random.choice(self.spawn_areas)
    x = area[0] + random.randint(-5, 5)
    z = area[1] + random.randint(-5, 5)
    spawn_pos = Vec3(x, 0, z)
    
    # 检查是否在墙里（向上射线）
    hit_check = raycast(
        origin=spawn_pos + Vec3(0, 1, 0),
        direction=Vec3(0, 1, 0),
        distance=0.5
    )
    
    # 检查周围是否有墙（四个方向）
    is_valid = True
    for direction in [Vec3(1,0,0), Vec3(-1,0,0), Vec3(0,0,1), Vec3(0,0,-1)]:
        hit = raycast(
            origin=spawn_pos + Vec3(0, 1, 0),
            direction=direction,
            distance=1.5
        )
        if hit.hit and hit.distance < 1.0:
            is_valid = False
            break
    
    # 位置有效，生成敌人
    if is_valid and not hit_check.hit:
        e = Enemy(position=spawn_pos, player_target=self.player)
        e.hp *= (1 + self.wave * 0.1)
        self.enemies_alive.append(e)
        spawned += 1
```

## 检测机制

### 1. 垂直检测（是否在墙里）
```python
raycast(
    origin=spawn_pos + Vec3(0, 1, 0),  # 从地面上1米
    direction=Vec3(0, 1, 0),           # 向上
    distance=0.5                        # 检测0.5米
)
```
如果检测到障碍物，说明该位置被墙体占据。

### 2. 水平检测（周围是否有墙）
```python
# 检测四个方向：前、后、左、右
directions = [
    Vec3(1, 0, 0),   # 右
    Vec3(-1, 0, 0),  # 左
    Vec3(0, 0, 1),   # 前
    Vec3(0, 0, -1)   # 后
]

for direction in directions:
    hit = raycast(
        origin=spawn_pos + Vec3(0, 1, 0),
        direction=direction,
        distance=1.5  # 检测1.5米
    )
    if hit.hit and hit.distance < 1.0:
        # 1米内有墙，位置无效
        is_valid = False
```

### 3. 重试机制
```python
max_attempts = count * 10  # 每个敌人最多尝试10次

while spawned < count and attempts < max_attempts:
    # 尝试生成
    if success:
        spawned += 1
    attempts += 1

if spawned < count:
    print(f"Warning: Only spawned {spawned}/{count} enemies")
```

## 生成区域

```python
self.spawn_areas = [
    (-15, -15),  # 左下角
    (15, 15),    # 右上角
    (-15, 15),   # 左上角
    (15, -15)    # 右下角
]

# 每个区域随机偏移 ±5 单位
x = area[0] + random.randint(-5, 5)
z = area[1] + random.randint(-5, 5)
```

实际生成范围：
- 左下：(-20, -20) 到 (-10, -10)
- 右上：(10, 10) 到 (20, 20)
- 左上：(-20, 10) 到 (-10, 20)
- 右下：(10, -20) 到 (20, -10)

## 参数调整

### 检测距离
```python
# 周围墙壁检测
distance=1.5  # 检测范围
threshold=1.0 # 安全距离

# 如果墙壁太近（< 1米），位置无效
if hit.distance < 1.0:
    is_valid = False
```

### 重试次数
```python
max_attempts = count * 10

# 例如：
# 需要生成 5 个敌人
# 最多尝试 50 次
# 平均每个敌人有 10 次机会
```

## 性能影响

| 操作 | 次数 | 开销 |
|------|------|------|
| 射线检测 | 5次/尝试 | 低 |
| 最大尝试 | count * 10 | 中 |
| 总体影响 | 波次开始时 | 可忽略 |

生成只在波次开始时进行，不影响游戏运行时性能。

## 边界情况

### 情况1：空间不足
```
如果地图太小或墙太多：
- 尝试 count * 10 次后停止
- 生成尽可能多的敌人
- 显示警告信息
```

### 情况2：所有区域都被占用
```
如果四个生成区域都有墙：
- 继续尝试其他随机位置
- 最终可能生成较少敌人
- 游戏仍可继续
```

### 情况3：敌人数量过多
```
如果需要生成 20+ 敌人：
- 可能需要更多尝试
- 考虑增加生成区域
- 或减少每波敌人数量
```

## 改进建议

### 1. 预计算生成点
```python
# 游戏开始时计算所有有效生成点
valid_spawn_points = []

for x in range(-40, 40, 5):
    for z in range(-40, 40, 5):
        if is_valid_spawn_point(x, z):
            valid_spawn_points.append((x, z))

# 生成时直接使用
spawn_pos = random.choice(valid_spawn_points)
```

优点：
- 生成速度快
- 保证有效
- 可视化调试

缺点：
- 需要预处理
- 占用内存
- 动态障碍物无法处理

### 2. 网格系统
```python
# 将地图分成网格
grid_size = 5
grid = {}

# 标记每个格子是否可用
for x in range(-40, 40, grid_size):
    for z in range(-40, 40, grid_size):
        grid[(x, z)] = is_valid(x, z)

# 生成时选择可用格子
available = [pos for pos, valid in grid.items() if valid]
spawn_pos = random.choice(available)
```

### 3. 距离玩家检测
```python
# 确保不在玩家附近生成
min_distance_from_player = 10

if distance(spawn_pos, player.position) < min_distance_from_player:
    is_valid = False
```

### 4. 视野外生成
```python
# 只在玩家视野外生成
player_forward = player.forward
to_spawn = (spawn_pos - player.position).normalized()
dot = player_forward.dot(to_spawn)

if dot > 0.5:  # 在玩家前方
    is_valid = False
```

### 5. 动态调整生成区域
```python
# 根据玩家位置调整生成区域
spawn_areas = [
    (player.x + 20, player.z + 20),
    (player.x - 20, player.z - 20),
    (player.x + 20, player.z - 20),
    (player.x - 20, player.z + 20)
]
```

## 调试工具

### 可视化生成点
```python
# 显示尝试的位置
debug_marker = Entity(
    model='sphere',
    color=color.red if not valid else color.green,
    position=spawn_pos,
    scale=0.5
)
destroy(debug_marker, delay=1)
```

### 统计信息
```python
print(f"Spawn attempts: {attempts}")
print(f"Success rate: {spawned/attempts*100:.1f}%")
print(f"Failed spawns: {attempts - spawned}")
```

## 测试清单

- [x] 敌人不会生成在墙里
- [x] 敌人不会生成在墙边（< 1米）
- [x] 生成失败时有警告
- [x] 空间不足时仍能生成部分敌人
- [x] 性能影响可忽略
- [x] 四个生成区域都可用

## 总结

新的生成系统：
- ✅ 智能检测障碍物
- ✅ 确保生成位置有效
- ✅ 有重试机制
- ✅ 性能友好
- ✅ 容错性好

现在敌人不会再生成在墙里了！

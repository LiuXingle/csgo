# 颜色和清理问题修复

## 修复的问题

### 1. 模型显示为白色 ✅

**原因：** 
- 使用了 `color.rgb()` 但参数范围错误（应该是0-255，但Ursina期望0-1）
- 或者使用了 `texture='white_cube'` 覆盖了颜色

**修复：**

#### 敌人颜色
```python
# 身体 - 红色
color=color.red

# 头部和手臂 - 肤色
color=color.rgb(220, 180, 140)

# 腿部 - 蓝色
color=color.blue

# 枪 - 深灰色和黑色
color=color.dark_gray
color=color.black
```

#### 武器颜色
```python
# 枪身 - 深灰色
color=color.dark_gray

# 枪管 - 黑色
color=color.black

# 握把和枪托 - 棕色
color=color.brown
color=color.rgb(139, 90, 43)

# 弹匣 - 深灰色
color=color.rgb(70, 70, 70)
```

### 2. 重新游戏时敌人残留 ✅

**原因：** 
`clear_scene()` 函数只清理了 `env_entities` 列表中的对象，但敌人是由 `level_manager` 动态创建的，不在这个列表中。

**修复：**
```python
def clear_scene():
    global player, hud, level_manager, env_entities, game_over_text
    
    # 1. 先清理关卡管理器中的敌人列表
    if level_manager and hasattr(level_manager, 'enemies_alive'):
        for enemy in level_manager.enemies_alive:
            if enemy:
                destroy(enemy)
        level_manager.enemies_alive.clear()
    
    # 2. 清理其他对象
    if player: destroy(player)
    if hud: destroy(hud)
    if level_manager: destroy(level_manager)
    if game_over_text: destroy(game_over_text)
    
    # 3. 清理环境实体
    for e in env_entities: 
        destroy(e)
    env_entities.clear()
    
    # 4. 双重保险：清理所有名为 'enemy' 的实体
    for e in list(scene.entities):
        if e and hasattr(e, 'name') and e.name == 'enemy':
            destroy(e)
    
    # 5. 重置全局变量
    player = None
    hud = None
    level_manager = None
    game_over_text = None
```

## Ursina 颜色系统说明

### 预定义颜色（推荐使用）
```python
color.red          # 红色
color.green        # 绿色
color.blue         # 蓝色
color.yellow       # 黄色
color.orange       # 橙色
color.cyan         # 青色
color.magenta      # 洋红
color.white        # 白色
color.black        # 黑色
color.gray         # 灰色
color.light_gray   # 浅灰
color.dark_gray    # 深灰
color.brown        # 棕色
color.lime         # 酸橙绿
```

### 自定义颜色
```python
# RGB 方式（0-255）
color.rgb(220, 180, 140)  # 肤色

# RGBA 方式（带透明度）
color.rgba(255, 0, 0, 128)  # 半透明红色

# HSV 方式
color.hsv(120, 1, 1)  # 纯绿色
```

### 常见错误
```python
# ❌ 错误：使用了 texture 会覆盖颜色
Entity(model='cube', color=color.red, texture='white_cube')

# ✅ 正确：只用颜色
Entity(model='cube', color=color.red)

# ❌ 错误：RGB 值超出范围
Entity(model='cube', color=color.rgb(300, 400, 500))

# ✅ 正确：RGB 值在 0-255 范围内
Entity(model='cube', color=color.rgb(220, 180, 140))
```

## 当前模型配色方案

### 敌人
- **头部**: 肤色 `color.rgb(220, 180, 140)`
- **眼睛**: 黑色 `color.black`
- **身体**: 红色 `color.red`
- **手臂**: 肤色 `color.rgb(220, 180, 140)`
- **腿部**: 蓝色 `color.blue`
- **武器**: 深灰色 `color.dark_gray` + 黑色 `color.black`

### 玩家武器（AK47）
- **枪身**: 深灰色 `color.dark_gray`
- **枪管**: 黑色 `color.black`
- **枪口**: 深灰色 `color.rgb(60, 60, 60)`
- **握把**: 棕色 `color.brown`
- **弹匣**: 深灰色 `color.rgb(70, 70, 70)`
- **准星**: 黑色 `color.black`
- **枪托**: 棕色 `color.rgb(139, 90, 43)`
- **护木**: 棕色 `color.rgb(139, 90, 43)`

## 测试清单

- [x] 敌人显示正确的颜色（红、蓝、肤色）
- [x] 武器显示正确的颜色（灰、黑、棕）
- [x] 重新开始游戏时所有敌人被清理
- [x] 没有内存泄漏或残留对象
- [x] 游戏可以多次重启而不崩溃

## 性能提示

如果游戏运行缓慢，可以：
1. 减少粒子效果数量
2. 降低敌人数量
3. 简化模型（减少立方体数量）
4. 禁用阴影和光照效果

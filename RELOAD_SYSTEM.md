# 换弹系统改进说明

## 新增功能

### 1. 真实的换弹音效 ✅
- 使用 `assets/reload.wav` 音效文件
- 不再使用射击音效代替

### 2. 换弹期间禁止射击 ✅
- 添加 `is_reloading` 状态标记
- 换弹时按鼠标左键不会射击
- 必须等待换弹完成才能继续射击

### 3. 换弹时长与音效同步 ✅
- 自动检测音效文件时长
- 如果无法获取，默认使用 2.0 秒
- 动画和锁定时间与音效时长匹配

### 4. 视觉反馈 ✅
- 屏幕中央显示 "RELOADING..." 提示
- 黄色文字，醒目易见
- 换弹完成后自动消失

### 5. 智能换弹 ✅
- 弹药已满时按 R 不会换弹
- 已经在换弹时按 R 不会重复换弹
- 避免浪费时间和打断动画

## 技术实现

### 武器类改进

```python
class AK47(Entity):
    def __init__(self, parent_camera):
        # ...
        self.is_reloading = False  # 换弹状态标记
        self.sfx_reload = safe_load_audio('assets/reload.wav')
    
    def shoot(self):
        # 换弹期间不能射击
        if self.is_reloading:
            return
        # ... 射击逻辑
    
    def reload(self):
        # 检查是否可以换弹
        if self.is_reloading or self.ammo >= Config.AMMO_CAPACITY:
            return
        
        self.is_reloading = True
        
        # 获取音效时长
        reload_duration = 2.0  # 默认值
        if self.sfx_reload:
            self.sfx_reload.play()
            if hasattr(self.sfx_reload, 'length'):
                reload_duration = self.sfx_reload.length()
        
        # 显示 HUD 提示
        player.hud_ref.show_reload_indicator(reload_duration)
        
        # 播放动画
        # ... 动画代码
        
        # 换弹完成后解锁
        invoke(setattr, self, 'is_reloading', False, delay=reload_duration)
```

### HUD 改进

```python
class HUD(Entity):
    def __init__(self):
        # ...
        self.reload_text = Text(
            parent=self, 
            text='RELOADING...', 
            position=(0, -0.2), 
            scale=2, 
            origin=(0,0), 
            color=color.yellow, 
            enabled=False
        )
    
    def show_reload_indicator(self, duration=2.0):
        """显示换弹提示"""
        self.reload_text.enabled = True
        invoke(setattr, self.reload_text, 'enabled', False, delay=duration)
```

## 换弹流程

1. **玩家按下 R 键**
   - 检查是否已在换弹 → 是：忽略
   - 检查弹药是否已满 → 是：忽略
   - 否：开始换弹

2. **开始换弹**
   - 设置 `is_reloading = True`
   - 播放 reload.wav 音效
   - 获取音效时长
   - 显示 "RELOADING..." 提示
   - 播放枪械动画（旋转、移动）

3. **换弹期间**
   - 玩家无法射击（shoot() 直接返回）
   - 动画持续播放
   - 提示文字显示

4. **换弹完成**
   - 设置 `is_reloading = False`
   - 弹药补满到 30 发
   - 隐藏提示文字
   - 枪械恢复正常位置
   - 玩家可以继续射击

## 配置参数

### 默认换弹时长
```python
# entities/weapon.py
reload_duration = 2.0  # 秒
```

如果你的 reload.wav 音效时长不同，系统会自动适配。

### 动画时间分配
```python
# 前 40% 时间：枪械向下旋转
duration=reload_duration * 0.4

# 中间 10% 时间：暂停（换弹匣）
# 自动计算

# 后 40% 时间：枪械恢复位置
duration=reload_duration * 0.4
delay=reload_duration * 0.5
```

## 音效文件要求

### 文件位置
```
assets/reload.wav
```

### 推荐规格
- **格式**: WAV 或 OGG
- **时长**: 1.5 - 2.5 秒
- **采样率**: 44100 Hz
- **声道**: 单声道或立体声
- **音量**: 适中，与射击音效平衡

### 音效内容建议
1. 弹匣取出声（咔嚓）
2. 新弹匣插入声（咔）
3. 拉栓上膛声（咔嚓）

## 测试清单

- [x] 按 R 键开始换弹
- [x] 换弹期间无法射击
- [x] 显示 "RELOADING..." 提示
- [x] 播放 reload.wav 音效
- [x] 换弹动画流畅
- [x] 换弹完成后可以射击
- [x] 弹药已满时按 R 无反应
- [x] 换弹期间按 R 无反应
- [x] 音效时长与锁定时间匹配

## 已知限制

1. **音效时长检测**
   - Ursina 的 Audio 对象可能没有 `length()` 方法
   - 如果检测失败，使用默认 2.0 秒
   - 建议手动调整 `reload_duration` 以匹配实际音效

2. **自动换弹**
   - 目前不支持弹药耗尽时自动换弹
   - 玩家必须手动按 R 键

3. **换弹取消**
   - 换弹开始后无法取消
   - 必须等待完成

## 未来改进建议

1. **自动换弹**
   ```python
   if self.ammo == 0 and not self.is_reloading:
       self.reload()
   ```

2. **快速换弹**
   - 按两次 R 键快速换弹（减少 30% 时间）
   - 但会损失当前弹匣中的剩余子弹

3. **换弹进度条**
   - 在 HUD 上显示换弹进度
   - 圆形进度条或线性进度条

4. **换弹音效变化**
   - 根据剩余弹药数量选择不同音效
   - 空弹匣换弹 vs 战术换弹

5. **移动换弹**
   - 换弹时移动速度减慢 50%
   - 增加真实感和战术深度

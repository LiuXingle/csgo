# core/config.py

class Config:
    WINDOW_TITLE = "CS:GO Python Remastered"
    WINDOW_SIZE = (1280, 720)
    
    # --- 玩家参数 (兼容新旧两种写法) ---
    PLAYER_SPEED = 8
    PLAYER_JUMP_HEIGHT = 1.5    # 旧代码用
    PLAYER_JUMP = 1.5           # 新代码用
    PLAYER_MAX_HP = 100         # 旧代码用
    PLAYER_HP = 100             # 新代码用
    SENSITIVITY = 60
    
    # --- 武器参数 (兼容新旧写法) ---
    AMMO_CAPACITY = 30          # HUD和部分旧逻辑用
    AMMO = 30                   # 武器逻辑用
    
    DAMAGE = 35                 # 旧代码用
    DMG = 35                    # 新代码用
    
    FIRE_RATE = 0.1
    RECOIL = 1.5
    
    # --- 敌人参数 (兼容新旧写法) ---
    ENEMY_HP = 100
    ENEMY_MAX_HP = 100
    
    ENEMY_SPEED = 4
    ENEMY_DMG = 10              # 新代码用
    ENEMY_ATTACK_DAMAGE = 10    # 旧代码用
    
    ENEMY_ACCURACY = 0.1        # 射击散布
    ENEMY_FIRE_RATE = 1.5       # 射击间隔
    ENEMY_ATTACK_RANGE = 20     # 攻击距离
    
    # --- 关卡与波次设置 ---
    WAVE_COUNT_BASE = 3         # 第一波敌人数量
    WAVE_INC = 2                # 每波增加多少敌人
    WAVE_DIFFICULTY_MULTIPLIER = 1.1

    # --- 新增：最大波次 (打完第5波通关) ---
    MAX_WAVES = 5
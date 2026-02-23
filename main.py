# main.py
from ursina import *
from core.config import Config
from core.utils import safe_load_texture
from entities.player import Player
from entities.props import HealthPack
from core.level_manager import LevelManager
from ui.menu import MainMenu
from ui.hud import HUD

app = Ursina()
window.title = Config.WINDOW_TITLE
window.vsync = True

# 全局变量
game_state = "menu" 
player = None
hud = None
level_manager = None
env_entities = []
game_over_text = None

def clear_scene():
    global player, hud, level_manager, env_entities, game_over_text
    
    # 先清理关卡管理器中的敌人
    if level_manager and hasattr(level_manager, 'enemies_alive'):
        for enemy in level_manager.enemies_alive:
            if enemy:
                destroy(enemy)
        level_manager.enemies_alive.clear()
    
    if player: destroy(player)
    if hud: destroy(hud)
    if level_manager: destroy(level_manager)
    if game_over_text: destroy(game_over_text)
    
    for e in env_entities: 
        destroy(e)
    env_entities.clear()
    
    # 清理所有名为 'enemy' 的实体（双重保险）
    for e in list(scene.entities):
        if e and hasattr(e, 'name') and e.name == 'enemy':
            destroy(e)
    
    player = None
    hud = None
    level_manager = None
    game_over_text = None

def create_level():
    global player, hud, level_manager, env_entities
    
    # 环境生成
    sky = Sky(texture='sky_default')
    env_entities.append(sky)
    
    light = DirectionalLight(y=10, rotation=(90, 45, 0))
    env_entities.append(light)
    
    tex_ground = safe_load_texture('assets/floor.png', fallback='grass')
    ground = Entity(model='plane', scale=(100,1,100), texture=tex_ground, texture_scale=(50,50), collider='box')
    env_entities.append(ground)
    
    tex_wall = safe_load_texture('assets/wall.png', fallback='brick')
    borders = [(50, 0, 1, 100), (-50, 0, 1, 100), (0, 50, 100, 1), (0, -50, 100, 1)]
    for b in borders:
        wall = Entity(model='cube', position=(b[0], 5, b[1]), scale=(b[2], 10, b[3]), 
                      texture=tex_wall, texture_scale=(b[2]/2, 5), collider='box', color=color.gray)
        env_entities.append(wall)

    for i in range(15):
        rx = random.randint(-40, 40)
        rz = random.randint(-40, 40)
        if math.sqrt(rx**2 + rz**2) < 10:
            if rx > 0: rx += 15
            else: rx -= 15
        wall = Entity(model='cube', scale=(random.randint(4,8), random.randint(3,6), random.randint(4,8)), 
                      position=(rx, 1.5, rz), 
                      texture=tex_wall, collider='box', color=color.white)
        wall.rotation_y = random.randint(0, 90)
        env_entities.append(wall)

    player = Player(position=(0, 2, 0), on_death_callback=game_over)
    player.name = 'player'
    
    hud = HUD()
    player.hud_ref = hud
    
    for i in range(5):
        hx = random.randint(-40, 40)
        hz = random.randint(-40, 40)
        hp_pack = HealthPack(position=(hx, 1, hz), player_ref=player)
        env_entities.append(hp_pack)

    # --- 关键修改：传入 on_victory_callback ---
    level_manager = LevelManager(player, on_victory_callback=game_victory)

def start_game():
    global game_state
    menu.hide()
    clear_scene()
    create_level()
    game_state = "playing"
    mouse.locked = True
    mouse.visible = False

def return_to_menu():
    global game_state
    clear_scene()
    menu.show()
    game_state = "menu"
    mouse.locked = False
    mouse.visible = True

# --- 新增：胜利逻辑 ---
def game_victory():
    global game_state, game_over_text
    if game_state == "victory": return
    
    game_state = "victory"
    mouse.locked = False
    mouse.visible = True
    
    # 禁用玩家，防止胜利后还能开枪
    if player: 
        player.enabled = False
        if player.weapon: player.weapon.enabled = False

    # 显示绿色胜利文字
    game_over_text = Text(text='VICTORY!', scale=4, origin=(0,0), color=color.green, background=True)
    
    # 4秒后回菜单
    invoke(return_to_menu, delay=4)

def game_over():
    global game_state, game_over_text
    if game_state == "game_over": return
    
    game_state = "game_over"
    mouse.locked = False
    mouse.visible = True
    
    game_over_text = Text(text='GAME OVER', scale=4, origin=(0,0), color=color.red, background=True)
    invoke(return_to_menu, delay=3)

menu = MainMenu(start_callback=start_game, exit_callback=application.quit)

def input(key):
    global game_state
    if key == 'escape':
        if game_state == "playing": 
            return_to_menu()

def update():
    if game_state == "playing" and player and player.enabled and hud:
        hud.update_hp(player.hp, Config.PLAYER_HP)
        hud.update_ammo(player.weapon.ammo, Config.AMMO_CAPACITY)
        if player.y < -10: player.take_damage(999)

app.run()
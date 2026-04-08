# game_play.py - 适配10种棋子（红蓝各5类）+ 适配主页返回逻辑
import pygame
import sys
import game_core
import config
import os  # 确保导入os模块

# 系统默认字体
FONT_TITLE = pygame.font.SysFont("SimHei", 48)
FONT_TEXT = pygame.font.SysFont("SimHei", 20)
FONT_ATTR = pygame.font.SysFont("SimHei", 18)

# -------------------------- 【固定棋盘参数】 --------------------------
GRID_COLS = 9            # 9列
GRID_ROWS = 9            # 9行
GRID_SIZE = 59           # 每个格子 59px
LEFT_BLANK_WIDTH = 117   # 修正：左侧空白改为130px（可自行微调）
TOP_BLANK_HEIGHT = 10     # 新增：棋盘顶部8px空白
LINE_WIDTH = 4           # 新增：棋盘线条宽度2px

# ====================== 胜利判定变量 ======================
game_over = False  # 游戏是否结束
winner = None      # 胜利者：TURN_RED / TURN_BLUE / "平局"
win_type = ""      # 胜利类型："夺旗" / "全剿"

# 夺旗计时：红/蓝方在旗帜上停留的回合数
red_flag_hold = 0
blue_flag_hold = 0

# -------------------------- 地形定义（9x9山峰分布） --------------------------
# 0=不可通行，1=平地 2=山峰 3=树林 4=旗帜（可根据实际地图调整坐标）
TERRAIN_MAP = [
    [1, 1, 2, 0, 1, 0, 1, 3, 1],
    [2, 3, 1, 1, 4, 1, 1, 2, 2],
    [3, 1, 1, 0, 1, 0, 1, 1, 3],
    [1, 2, 1, 3, 1, 1, 2, 1, 1],
    [3, 3, 1, 1, 1, 2, 3, 1, 1],
    [1, 1, 1, 2, 1, 1, 1, 1, 2],
    [2, 1, 2, 0, 1, 0, 2, 1, 1],
    [3, 1, 1, 1, 4, 1, 1, 3, 1],
    [1, 3, 1, 0, 1, 0, 1, 1, 1],
]

TURN_RED = "red"
TURN_BLUE = "blue"

# -------------------------- 兵种属性 --------------------------
TROOP_STATS = {
    "infantry":       {"atk": 2, "def": 7},   # 步兵
    "heavy_cavalry":  {"atk": 3, "def": 7},   # 重骑兵
    "light_cavalry":  {"atk": 3, "def": 5},   # 轻骑兵
    "longbow":        {"atk": 2, "def": 4},   # 长弓手
    "crossbow":       {"atk": 3, "def": 4},   # 弩手
}

# -------------------------- 游戏核心类 --------------------------
class ChessPiece:
    """棋子类（支持阵营+兵种，加载对应图片）"""
    def __init__(self, faction, troop_type, grid_x, grid_y):
        self.faction = faction
        self.troop_type = troop_type
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.size = GRID_SIZE  # 棋子 = 格子大小（59px）
        self.is_selected = False
        
        # 核心：按「阵营+兵种」拼接图片路径
        self.image = None
        # 图片命名规则：红方步兵=red_infantry.png，蓝方重骑兵=blue_heavy_cavalry.png（可自定义）
        piece_img_name = f"{faction}_{troop_type}.png"
        piece_img_path = os.path.join(config.SOURCE_DIR, piece_img_name)
        
        try:
            self.image = pygame.image.load(piece_img_path).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, (self.size, self.size))
        except pygame.error:
            troop_colors = {
                "infantry": (255, 0, 0) if faction == "red" else (0, 0, 255),
                "heavy_cavalry": (200, 0, 0) if faction == "red" else (0, 0, 200),
                "light_cavalry": (255, 100, 100) if faction == "red" else (100, 100, 255),
                "longbow": (255, 150, 0) if faction == "red" else (0, 150, 255),
                "crossbow": (150, 0, 150) if faction == "red" else (0, 150, 150)
            }
            self.color = troop_colors.get(troop_type, (255, 255, 0))
            self.image = None
            
        stats = TROOP_STATS[troop_type]
        self.atk = stats["atk"]
        self.def_ = stats["def"]  # 用 def_ 因为 def 是关键字
        
        # 新增：暴露状态细分（区分"攻击后暴露"和"被发现暴露"）
        self.attack_exposed = False  # 攻击导致的暴露
        self.discovered_exposed = False  # 被发现导致的暴露
        
    def is_in_forest(self):
        """判断棋子是否在树林地形（TERRAIN_MAP中3=树林）"""
        if 0 <= self.grid_x < GRID_COLS and 0 <= self.grid_y < GRID_ROWS:
            return TERRAIN_MAP[self.grid_y][self.grid_x] == 3
        return False

    def draw(self, surface, grid_size, map_rect, current_turn=None):
        """绘制棋子（核心修正：像素坐标计算，适配顶部空白+线条宽度）"""
        # 修正逻辑：
        # 1. 左侧空白130px + 列数×格子大小 + 线条宽度补偿（竖线占2px，每列前1px）
        # 2. 顶部8px空白 + 行数×格子大小 + 线条宽度补偿（横线占2px，每行前1px）
        # 3. 格子大小用传入的grid_size（适配棋盘缩放），而非固定GRID_SIZE
        pixel_x = (
            LEFT_BLANK_WIDTH 
            + self.grid_x * grid_size 
            + (self.grid_x + 1) * LINE_WIDTH  # 补偿竖线宽度（每列1条竖线，共grid_x+1条）
            + grid_size // 2  # 居中
        )
        pixel_y = (
            TOP_BLANK_HEIGHT 
            + self.grid_y * grid_size 
            + (self.grid_y + 1) * LINE_WIDTH  # 补偿横线宽度（每行1条横线，共grid_y+1条）
            + grid_size // 2  # 居中
        )
        
        # 1. 绘制选中高亮框（黄色外圈）
        if self.is_selected:
            highlight_rect = pygame.Rect(
                pixel_x - self.size//2 - 2,
                pixel_y - self.size//2 - 2,
                self.size + 4,
                self.size + 4
            )
            pygame.draw.rect(surface, (255, 255, 0), highlight_rect, 2)
            
        # 树林逻辑：判断是否隐身/半透明
        is_stealthed = self.is_in_forest()
        # 攻击后取消隐身标记（新增属性）
        if self.attack_exposed or self.discovered_exposed:
            is_stealthed = False
            
        # 如果是敌方棋子且未暴露，强制隐身（即使不在树林）
        if current_turn and self.faction != current_turn and not is_stealthed:
            # 非己方棋子+不在树林 → 也需结合战争迷雾判断是否绘制
            pass  # 最终绘制权交给外层的可见性判断
        
        # 画棋子（完全居中格子）
        if self.image:
            img_rect = self.image.get_rect(center=(pixel_x, pixel_y))
            if is_stealthed:
                # 树林中：半透明（己方可见，敌方不可见）
                if self.faction == current_turn:
                    # 己方视角：50%透明度
                    transparent_img = self.image.copy()
                    transparent_img.set_alpha(128)  # 0=完全透明，255=不透明
                    surface.blit(transparent_img, img_rect)
                # 敌方视角：完全隐身（不绘制）
            else:
                # 非树林/攻击后：正常绘制
                surface.blit(self.image, img_rect)
        else:
            pygame.draw.circle(surface, self.color, (pixel_x, pixel_y), self.size//2)
            
    def draw_attributes(self, surface, mouse_pos):
        """在鼠标右侧绘制棋子属性框"""
        if not self.is_selected:
            return
        
        # 属性框位置：鼠标右侧10px，对齐鼠标y坐标
        box_x = mouse_pos[0] + 10
        box_y = mouse_pos[1] - 30
        box_width = 120
        box_height = 70
        
        # 绘制属性框背景
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(surface, (240, 240, 240), box_rect)  # 浅灰色背景
        pygame.draw.rect(surface, (0, 0, 0), box_rect, 2)     # 黑色边框
        
        # 绘制属性文本
        troop_names = {
            "infantry": "步兵",
            "heavy_cavalry": "重骑兵",
            "light_cavalry": "轻骑兵",
            "longbow": "长弓手",
            "crossbow": "弩手"
        }
        faction_name = "红方" if self.faction == "red" else "蓝方"
        troop_name = troop_names.get(self.troop_type, self.troop_type)
        
        # 文本内容
        text_name = FONT_ATTR.render(f"{faction_name}{troop_name}", True, (0, 0, 0))
        text_atk = FONT_ATTR.render(f"攻击：{self.atk}", True, (220, 0, 0))
        text_def = FONT_ATTR.render(f"兵力：{self.def_}", True, (0, 100, 0))
        
        # 绘制文本
        surface.blit(text_name, (box_x + 5, box_y + 5))
        surface.blit(text_atk, (box_x + 5, box_y + 25))
        surface.blit(text_def, (box_x + 5, box_y + 45))

    def move(self, dx, dy):
        """移动棋子"""
        self.grid_x += dx
        self.grid_y += dy
        
    def is_on_mountain(self):
        """判断棋子是否在山峰地形"""
        if 0 <= self.grid_x < GRID_COLS and 0 <= self.grid_y < GRID_ROWS:
            return TERRAIN_MAP[self.grid_y][self.grid_x] == 2
        return False

    def get_attack_range(self):
        """获取棋子攻击范围（适配长弓手山峰加成）"""
        if self.troop_type == "longbow" and self.is_on_mountain():
            return 2  # 长弓手在山峰上攻击范围2格
        return 1     # 其他情况攻击范围1格

class GameMap:
    def __init__(self, map_image_path):
        self.map_image = None
        try:
            self.map_image = pygame.image.load(map_image_path).convert()
            self.map_image = pygame.transform.scale(self.map_image, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            print(f"地图加载成功：{map_image_path}")
        except pygame.error as e:
            print(f"地图加载失败：{e}，使用纯色背景替代")
            self.map_image = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            self.map_image.fill((245, 245, 220))
        
        self.grid_cols = GRID_COLS
        self.grid_rows = GRID_ROWS
        self.grid_size = GRID_SIZE
        self.left_blank = LEFT_BLANK_WIDTH
        self.top_blank = TOP_BLANK_HEIGHT
        self.line_width = LINE_WIDTH

    def draw(self, surface):
        surface.blit(self.map_image, (0, 0))
    def mouse_to_grid(self, mouse_pos):
        """鼠标坐标 → 精准网格坐标（修正：适配顶部空白+线条宽度）"""
        mx, my = mouse_pos
        # 减去左侧空白 + 线条宽度补偿，再除以格子大小
        grid_x = (mx - self.left_blank - self.line_width) // (self.grid_size + self.line_width)
        # 减去顶部空白 + 线条宽度补偿，再除以格子大小
        grid_y = (my - self.top_blank - self.line_width) // (self.grid_size + self.line_width)

        if 0 <= grid_x < self.grid_cols and 0 <= grid_y < self.grid_rows:
            return (grid_x, grid_y)
        return (None, None)
    
    def is_valid_position(self, grid_x, grid_y):
        return 0 <= grid_x < self.grid_cols and 0 <= grid_y < self.grid_rows
    
    def get_distance(self, x1, y1, x2, y2):
        """计算两个格子之间的切比雪夫距离（8方向一格判定）"""
        return max(abs(x1 - x2), abs(y1 - y2))
    
def get_visible_grids(faction, pieces, game_map):
    """
    根据当前阵营计算可见格子列表
    :param faction: 当前回合阵营（red/blue）
    :param pieces: 所有棋子列表
    :param game_map: 游戏地图对象
    :return: 可见格子坐标列表 [(x1,y1), (x2,y2)...]
    """
    visible_grids = []
    # 遍历己方所有棋子
    for piece in pieces:
        if piece.faction == faction:
            # 遍历棋子周围8格（包括自身位置）
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    new_x = piece.grid_x + dx
                    new_y = piece.grid_y + dy
                    # 检查坐标合法性
                    if game_map.is_valid_position(new_x, new_y):
                        visible_grids.append((new_x, new_y))
    # 去重并返回
    return list(set(visible_grids))

def draw_war_fog(surface, game_map, visible_grids):
    """
    绘制战争迷雾：仅显示可见格子，其余区域覆盖半透明灰色
    :param surface: 绘制表面（游戏主屏幕）
    :param game_map: 游戏地图对象
    :param visible_grids: 可见格子列表
    """
    # 迷雾颜色：灰色半透明（RGBA）
    fog_color = (100, 100, 100, 180)
    fog_surface = pygame.Surface((game_map.grid_size, game_map.grid_size), pygame.SRCALPHA)
    fog_surface.fill(fog_color)

    # 遍历所有格子，非可见区域绘制迷雾
    for grid_y in range(game_map.grid_rows):
        for grid_x in range(game_map.grid_cols):
            if (grid_x, grid_y) not in visible_grids:
                # 计算格子的像素坐标（适配原有棋盘偏移逻辑）
                pixel_x = (
                    game_map.left_blank
                    + grid_x * game_map.grid_size
                    + (grid_x + 1) * game_map.line_width
                )
                pixel_y = (
                    game_map.top_blank
                    + grid_y * game_map.grid_size
                    + (grid_y + 1) * game_map.line_width
                )
                # 绘制该格子的迷雾
                surface.blit(fog_surface, (pixel_x, pixel_y))
    
def handle_attack(attacker, defender, pieces):
    """
    处理攻击逻辑：A攻击B → B反击A（特殊规则除外）→ 判断死亡
    :param attacker: 攻击方棋子（ChessPiece）
    :param defender: 防御方棋子（ChessPiece）
    :param pieces: 所有棋子列表（用于移除死亡棋子）
    """
    print(f"\n===== 攻击触发 =====")
    print(f"攻击方：{attacker.faction}方{attacker.troop_type} (攻{attacker.atk}, 防{attacker.def_})")
    print(f"防御方：{defender.faction}方{defender.troop_type} (攻{defender.atk}, 防{defender.def_})")
    
    # 1. 攻击方攻击防御方
    damage_to_defender = attacker.atk
    # 重骑兵受击减伤规则（除弩手外）
    if defender.troop_type == "heavy_cavalry" and attacker.troop_type != "crossbow":
        damage_to_defender = damage_to_defender - 1
        print(f"🔰 重骑兵减伤：{attacker.troop_type}的攻击伤害从{attacker.atk}降至{damage_to_defender}")
    
    defender.def_ -= damage_to_defender
    print(f"💥 {attacker.faction}方攻击 → {defender.faction}方剩余兵力：{defender.def_}")
    
    # 2. 防御方反击（特殊规则判断）
    can_counter_attack = True
    # 规则1：重骑兵攻击时，被攻击方不反击
    if attacker.troop_type == "heavy_cavalry":
        can_counter_attack = False
        print(f"🛡️ 重骑兵攻击，{defender.faction}方无法反击")
    # 规则4：长弓手/弩手在山峰上攻击时，被攻击方不反击
    elif (attacker.troop_type in ["longbow", "crossbow"]) and attacker.is_on_mountain():
        can_counter_attack = False
        print(f"⛰️ {attacker.troop_type}在山峰攻击，{defender.faction}方无法反击")
    
    if can_counter_attack:
        damage_to_attacker = defender.atk
        # 重骑兵受击减伤规则（除弩手外）
        if attacker.troop_type == "heavy_cavalry" and defender.troop_type != "crossbow":
            damage_to_attacker = max(1, damage_to_attacker - 1)
            print(f"🔰 重骑兵减伤：{defender.troop_type}的反击伤害从{defender.atk}降至{damage_to_attacker}")
        
        attacker.def_ -= damage_to_attacker
        print(f"⚡ {defender.faction}方反击 → {attacker.faction}方剩余兵力：{attacker.def_}")
        
    # 攻击方攻击后暴露1回合
    attacker.attack_exposed = True  # 标记暴露
    # 防御方（隐藏棋子）被攻击后永久暴露（直到回合结束）
    defender.discovered_exposed = True
    print(f"⚠️ {attacker.faction}方{attacker.troop_type}攻击后暴露，敌方可见1回合")
    print(f"⚠️ {defender.faction}方{defender.troop_type}被发现，暴露至本回合结束")
    
    # 3. 判断棋子死亡并移除
    dead_pieces = []
    if defender.def_ <= 0:
        dead_pieces.append(defender)
        print(f"☠️ {defender.faction}方{defender.troop_type}被消灭！")
    if attacker.def_ <= 0:
        dead_pieces.append(attacker)
        print(f"☠️ {attacker.faction}方{attacker.troop_type}被消灭！")
    
    # 从棋子列表中移除死亡棋子
    for dead_piece in dead_pieces:
        if dead_piece in pieces:
            pieces.remove(dead_piece)
            # 取消选中状态（如果死亡的是选中棋子）
            if dead_piece.is_selected:
                dead_piece.is_selected = False
                
def check_victory(pieces, terrain_map):
    """
    检查胜利条件：全剿 / 夺旗 / 平局
    返回：game_over, winner, win_type
    """
    # 1. 分离双方棋子（用def_ > 0判断存活，替代未声明的is_alive）
    red_pieces = [p for p in pieces if p.faction == TURN_RED and p.def_ > 0]
    blue_pieces = [p for p in pieces if p.faction == TURN_BLUE and p.def_ > 0]

    red_alive = len(red_pieces) > 0
    blue_alive = len(blue_pieces) > 0

    # 2. 全剿判定
    if not red_alive and not blue_alive:
        return True, "平局", "全剿"
    if not red_alive:
        return True, TURN_BLUE, "全剿"
    if not blue_alive:
        return True, TURN_RED, "全剿"

    # 3. 夺旗判定（修正坐标变量：cell_x/cell_y → grid_x/grid_y）
    red_on_flag = any(
        terrain_map[p.grid_y][p.grid_x] == 4 
        for p in red_pieces 
        if 0 <= p.grid_x < GRID_COLS and 0 <= p.grid_y < GRID_ROWS
    )
    blue_on_flag = any(
        terrain_map[p.grid_y][p.grid_x] == 4 
        for p in blue_pieces 
        if 0 <= p.grid_x < GRID_COLS and 0 <= p.grid_y < GRID_ROWS
    )

    # 全局变量（顶部已定义）
    global red_flag_hold, blue_flag_hold

    # 每回合结束时更新夺旗计时
    if red_on_flag:
        red_flag_hold += 1
    else:
        red_flag_hold = 0

    if blue_on_flag:
        blue_flag_hold += 1
    else:
        blue_flag_hold = 0

    # 同时夺旗 = 平局
    if red_flag_hold >= 3 and blue_flag_hold >= 3:
        return True, "平局", "夺旗"
    if red_flag_hold >= 3:
        return True, TURN_RED, "夺旗"
    if blue_flag_hold >= 3:
        return True, TURN_BLUE, "夺旗"

    # 游戏继续
    return False, None, ""

# -------------------------- 游戏主逻辑 --------------------------
def run_game_play():
    global game_over, winner, win_type
    game_core.audio_manager.resume_music()
    
    # ====================== 回合制 & 军饷系统 ======================
    current_turn = TURN_RED   # 红方先动
    total_round = 1           # 总回合
    red_supply = 5            # 初始军饷
    blue_supply = 5
    cost = 1  #移动费用

    # 1. 初始化地图
    map_path = os.path.join(config.SOURCE_DIR, "地图.png")
    game_map = GameMap(map_path)

    # 棋子初始化（9×9棋盘内合理位置）
    red_pieces = [
        ChessPiece("red", "infantry", 4, 6),
        ChessPiece("red", "heavy_cavalry", 4, 8),
        ChessPiece("red", "light_cavalry", 5, 7),
        ChessPiece("red", "longbow", 4, 7),
        ChessPiece("red", "crossbow", 3, 7)
    ]
    blue_pieces = [
        ChessPiece("blue", "infantry", 4, 2),
        ChessPiece("blue", "heavy_cavalry", 4, 0),
        ChessPiece("blue", "light_cavalry", 3, 1),
        ChessPiece("blue", "longbow", 4, 1),
        ChessPiece("blue", "crossbow", 5, 1)
    ]

    # 所有棋子列表
    pieces = red_pieces + blue_pieces
    selected_piece = None

    # 3. 游戏主循环
    running = True
    clock = pygame.time.Clock()

    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 关闭窗口时先退出战棋界面，再退出程序（保证主页逻辑闭环）
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False  # 仅退出战棋循环，不退出pygame → 回到主页
                print("===== 返回游戏主页 =====")
            
            # 空格键结束当前回合
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # 1. 取消所有棋子选中状态（核心需求）
                for piece in pieces:
                    piece.is_selected = False
                selected_piece = None  # 重置选中棋子
                # 切换回合
                if current_turn == TURN_RED:
                    current_turn = TURN_BLUE
                    print("🔚 红方回合结束 → 蓝方回合开始")
                else:
                    # 蓝方结束 = 一整回合结束，增发军饷
                    current_turn = TURN_RED
                    total_round += 1

                    # 按回合发放军饷
                    if total_round <= 4:
                        add = 5
                    elif total_round <= 10:
                        add = 8
                    else:
                        add = 12

                    red_supply += add
                    blue_supply += add

                    print(f"========================================")
                    print(f"📦 第 {total_round} 回合结束！双方获得 +{add} 军饷")
                    print(f"🧧 红方军饷：{red_supply} | 蓝方军饷：{blue_supply}")
                    print(f"========================================")
                    print(f"🔄 新回合开始 → 红方回合")
                    
                if current_turn == TURN_RED:
                    ended_turn = TURN_BLUE
                else:
                    ended_turn = TURN_RED
                reset_count = 0
                    
                for piece in pieces:
                    if piece.faction != ended_turn:  # 仅重置刚结束回合方的棋子
                        if piece.attack_exposed or piece.discovered_exposed:
                            piece.attack_exposed = False
                            piece.discovered_exposed = False
                            reset_count += 1
                if reset_count > 0:
                    print(f"🔍 {ended_turn}方回合结束，重置{reset_count}个棋子的暴露状态，树林隐身恢复")
                
                # ============== 【回合结束 → 检查胜利】 ==============
                if not game_over:
                    game_over, winner, win_type = check_victory(pieces, TERRAIN_MAP)

                if game_over:
                    # 打印结果
                    if winner == "平局":
                        print("🏆 双方同时达成胜利条件 → 平局！")
                        text = "平局！"
                    else:
                        fac = "红方" if winner == TURN_RED else "蓝方"
                        print(f"🏆 {fac}{win_type}成功！")
                        text = f"{fac}{win_type}胜利！"
                        
                     # 字体、颜色、位置（右上角）
                    font = pygame.font.SysFont(None, 48)
                    text_surface = font.render(text, True, (255, 215, 0))  # 金色
                    game_core.screen.blit(text_surface, (game_core.screen.get_width() - 280, 20))
                        
            # 锁定所有操作
            if game_over:
                return  # 或 continue，直接跳过所有操作
            
            # 鼠标选中棋子
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                grid_x, grid_y = game_map.mouse_to_grid(mouse_pos)
                if grid_x is None:
                    if selected_piece:
                        selected_piece.is_selected = False
                        selected_piece = None
                    continue

                clicked_piece = None
                for piece in pieces:
                    if piece.grid_x == grid_x and piece.grid_y == grid_y:
                        clicked_piece = piece
                        break
                
                # ========== 可见性判断 ==========
                # 1. 计算当前回合的可见格子
                visible_grids = get_visible_grids(current_turn, pieces, game_map)
                # 2. 若点击的是敌方棋子，且不在可见格子内 → 禁止选中
                if clicked_piece and clicked_piece.faction != current_turn:
                    if (clicked_piece.grid_x, clicked_piece.grid_y) not in visible_grids:
                        clicked_piece = None  # 置空，视为未点击到任何棋子
                # ========== 隐藏敌方判断保留 ==========
                if clicked_piece is not None:
                    # 如果点击的是【敌方】+【在树林里】+【未暴露】→ 视为点到空气，直接忽略
                    is_hidden_enemy = (
                        clicked_piece.faction != current_turn
                        and clicked_piece.is_in_forest()
                        and not clicked_piece.attack_exposed
                        and not clicked_piece.discovered_exposed
                    )
                    if is_hidden_enemy:
                        clicked_piece = None  # 强制清空，不选中
                
                if clicked_piece:
                    # 情况1：已选中己方棋子，点击敌方棋子 → 触发攻击
                    if selected_piece and selected_piece != clicked_piece:
                        if selected_piece.faction != clicked_piece.faction:
                            # 判断攻击范围是否合法
                            attack_range = selected_piece.get_attack_range()
                            distance = game_map.get_distance(
                                selected_piece.grid_x, selected_piece.grid_y,
                                clicked_piece.grid_x, clicked_piece.grid_y
                            )
                            if distance <= attack_range:
                                # 检查当前回合是否为攻击方回合
                                if selected_piece.faction == current_turn:
                                    if current_turn == TURN_RED:
                                        if red_supply < 1:
                                            print("❌ 红方军饷不足，无法攻击！")
                                            continue  # 不退出，只是不能攻击
                                        red_supply -= 1  # 攻击消耗1军饷
                                    else:
                                        if blue_supply < 1:
                                            print("❌ 蓝方军饷不足，无法攻击！")
                                            continue
                                        blue_supply -= 1
                                    handle_attack(selected_piece, clicked_piece, pieces)
                                    # 攻击后取消选中
                                    selected_piece.is_selected = False
                                    selected_piece = None
                                else:
                                    print(f"❌ 现在是{current_turn}方回合，无法操控{selected_piece.faction}方棋子攻击！")
                            else:
                                print(f"❌ 攻击范围不足！{selected_piece.troop_type}攻击范围{attack_range}格，目标距离{distance}格")
                        else:
                            # 点击己方其他棋子 → 切换选中
                            selected_piece.is_selected = False
                            selected_piece = clicked_piece
                            selected_piece.is_selected = True
                            print(f"选中{clicked_piece.faction}方{clicked_piece.troop_type}棋子：({grid_x}, {grid_y})")
                    else:
                        # 情况2：未选中棋子/点击已选中棋子 → 选中当前棋子
                        if selected_piece:
                            selected_piece.is_selected = False
                        selected_piece = clicked_piece
                        selected_piece.is_selected = True
                        print(f"选中{clicked_piece.faction}方{clicked_piece.troop_type}棋子：({grid_x}, {grid_y})")
                else:
                    # 点击空白处 → 取消选中
                    if selected_piece:
                        selected_piece.is_selected = False
                        selected_piece = None

            # 方向键移动选中的棋子
            if event.type == pygame.KEYDOWN and selected_piece:
                dx, dy = 0, 0
                if event.key == pygame.K_KP8: dy = -1
                elif event.key == pygame.K_KP2: dy = 1
                elif event.key == pygame.K_KP4: dx = -1
                elif event.key == pygame.K_KP6: dx = 1
                
                elif event.key == pygame.K_KP7: dx = -1; dy = -1  # 左上
                elif event.key == pygame.K_KP9: dx = 1; dy = -1  # 右上
                elif event.key == pygame.K_KP1: dx = -1; dy = 1  # 左下
                elif event.key == pygame.K_KP3: dx = 1; dy = 1  # 右下
                else:
                    pass
                
                if dx == 0 and dy == 0:
                    pass
                
                elif selected_piece.faction != current_turn:
                    print(f"👉 现在是【{current_turn}方】回合，不能移动敌方棋子！")
                    
                elif current_turn == TURN_RED and red_supply < cost:
                    print("❌ 红方军饷不足，无法移动！")
                    
                elif current_turn == TURN_BLUE and blue_supply < cost:
                    print("❌ 蓝方军饷不足，无法移动！")
                    
                else:
                    new_x = selected_piece.grid_x + dx
                    new_y = selected_piece.grid_y + dy
                    if game_map.is_valid_position(new_x, new_y):
                        # 检查目标位置是否有敌方隐藏棋子（树林中）
                        hidden_enemy = None
                        for piece in pieces:
                            if (piece.faction != selected_piece.faction and 
                                piece.grid_x == new_x and piece.grid_y == new_y and 
                                piece.is_in_forest() and not (piece.attack_exposed or piece.discovered_exposed)):
                                hidden_enemy = piece
                                break
                            
                        if hidden_enemy:
                            # 移动到有隐藏敌方棋子的树林 → 触发攻击
                            print(f"\n🚨 发现树林中隐藏的{hidden_enemy.faction}方{hidden_enemy.troop_type}！触发强制攻击")
                            # 消耗军饷（移动+攻击合并消耗1）
                            if current_turn == TURN_RED:
                                red_supply -= cost
                            else:
                                blue_supply -= cost
                            # 触发攻击（移动方为攻击方，隐藏棋子为防御方）
                            handle_attack(selected_piece, hidden_enemy, pieces)
                            # 攻击后不移动（停在原位置）
                            print(f"⚔️ 强制攻击后，{selected_piece.faction}方棋子停在原位置")
                        else:    
                            # 简单碰撞检测（防止棋子重叠）
                            collision = False
                            for piece in pieces:
                                if piece != selected_piece and piece.grid_x == new_x and piece.grid_y == new_y:
                                    collision = True
                                    print(f"【提示】移动失败：{new_x},{new_y} 位置已有棋子")
                                    break
                            if not collision:
                                if current_turn == TURN_RED:
                                    red_supply -= cost
                                else:
                                    blue_supply -= cost
                                selected_piece.move(dx, dy)
                                print(f"✅ 移动成功！剩余军饷：{red_supply if current_turn==TURN_RED else blue_supply}")
                                print(f"{selected_piece.faction}方{selected_piece.troop_type}棋子移动到：({new_x}, {new_y})")
        

        # 绘制界面
        game_core.screen.fill(config.WHITE)
        game_map.draw(game_core.screen)
        
        # 绘制战争迷雾
        visible_grids = get_visible_grids(current_turn, pieces, game_map)
        draw_war_fog(game_core.screen, game_map, visible_grids)
        
        for piece in pieces:
            # 核心：仅绘制己方棋子 或 敌方棋子在可见区域内（保留战争迷雾逻辑）
            if piece.faction == current_turn or (piece.grid_x, piece.grid_y) in visible_grids:
                # 传递current_turn，且只调用一次draw
                piece.draw(game_core.screen, game_map.grid_size, game_map.map_image.get_rect(), current_turn)
            
        if selected_piece:
            selected_piece.draw_attributes(game_core.screen, mouse_pos)
        
        text_turn = FONT_TEXT.render(f"第{total_round}回合", True, (0,0,0))
        text_red = FONT_TEXT.render(f"軍餉：{red_supply}", True, (255,0,0))
        text_blue = FONT_TEXT.render(f"軍餉：{blue_supply}", True, (0,0,255))
        
        # 获取军饷文本的矩形区域（用于绘制高亮框）
        red_rect = text_red.get_rect(topleft=(700, 550))
        blue_rect = text_blue.get_rect(topleft=(20, 60))
        
        # 根据当前回合绘制军饷高亮框
        if current_turn == TURN_RED:
            # 红方回合：红方军饷框高亮（黄色边框，加padding）
            highlight_red_rect = pygame.Rect(
                red_rect.x - 5, red_rect.y - 5,
                red_rect.width + 10, red_rect.height + 10
            )
            pygame.draw.rect(game_core.screen, (255, 255, 0), highlight_red_rect, 3)
        else:
            # 蓝方回合：蓝方军饷框高亮（黄色边框，加padding）
            highlight_blue_rect = pygame.Rect(
                blue_rect.x - 5, blue_rect.y - 5,
                blue_rect.width + 10, blue_rect.height + 10
            )
            pygame.draw.rect(game_core.screen, (255, 255, 0), highlight_blue_rect, 3)
        
        game_core.screen.blit(text_turn, (20,20))
        game_core.screen.blit(text_red, (700,550))
        game_core.screen.blit(text_blue, (20,60))
        
        pygame.display.flip()
        clock.tick(60)
    
    # 循环结束后：清空屏幕（可选），返回主页前的清理
    game_core.screen.fill(config.WHITE)
    pygame.display.flip()
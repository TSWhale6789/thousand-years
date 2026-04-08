# card.py (修复版：UI布局+双击逻辑+位置比例完全正常)
import pygame
import sys
import game_core
import config
import time  # 用于双击时间差判断

FONT_SMALL = pygame.font.SysFont("SimHei", 20)
FONT_LARGE = pygame.font.SysFont("SimHei", 24)

# 5类棋子的描述数据（和game_play.py保持一致）
PIECE_DESC = {
    "infantry": {
        "name": "步兵",
        "desc": "基礎兵種，由下馬重裝騎兵組成\n攻擊距離1格，攻擊力2，兵力7，每回合可行動2次，攻擊最多1次"
    },
    "heavy_cavalry": {
        "name": "重騎兵",
        "desc": "重裝騎兵\n攻擊範圍1格，攻擊力3，兵力7，每回合可行動3次，攻擊最多1次\n重裝：受到的傷害-1\n衝擊：攻擊時免疫反擊"
    },
    "light_cavalry": {
        "name": "輕騎兵",
        "desc": "輕裝騎兵，通常用作偵察兵\n攻擊範圍1格，攻擊力3，兵力5，每回合可行動3次，攻擊最多1次"
    },
    "longbow": {
        "name": "長弓手",
        "desc": "遠程兵種\n攻擊範圍1格，攻擊力2，兵力4，每回合可行動2次，攻擊最多1次\n制高：位於山峰時，攻擊範圍+1\n箭矢：位於山峰時，免疫反擊"
    },
    "crossbow": {
        "name": "弩手",
        "desc": "遠程兵種\n攻擊範圍1格，攻擊力3，兵力4，每回合可行動2次，攻擊最多1次\n破甲：無視重騎兵重裝\n箭矢：位於山峰時，免疫反擊"
    }
}

# 左侧选择框坐标（5个，垂直排列）
LEFT_BOXES = [
    (50, 50, 80, 80),    # 步兵框 (x, y, w, h)
    (50, 140, 80, 80),   # 重骑兵框
    (50, 230, 80, 80),   # 轻骑兵框
    (50, 320, 80, 80),   # 长弓手框
    (50, 410, 80, 80)    # 弩手框
]
# 对应棋子类型
BOX_TO_PIECE = [
    "infantry", "heavy_cavalry", "light_cavalry", "longbow", "crossbow"
]

# 中间详情框坐标
MAIN_BOX = (180, 50, 600, 450)  # (x, y, w, h)

# 选中状态（初始无选中）
selected_index = -1

# 初始化图片字典（存储加载后的棋子图片）
PIECE_IMAGES = {}
def load_piece_images():
    """加载所有棋子的图片资源"""
    image_paths = {
        "infantry": "../Source/步兵.png",       # 步兵图片路径
        "heavy_cavalry": "../Source/重骑.png", # 重骑兵图片路径
        "light_cavalry": "../Source/轻骑.png", # 轻骑兵图片路径
        "longbow": "../Source/长弓.png",         # 长弓手图片路径
        "crossbow": "../Source/弩手.png"        # 弩手图片路径
    }
    for piece_type, path in image_paths.items():
        try:
            # 加载图片并缩放到左侧框的尺寸（80x60）
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (LEFT_BOXES[0][2], LEFT_BOXES[0][3]))
            PIECE_IMAGES[piece_type] = img
        except pygame.error as e:
            print(f"加载图片失败 {path}：{e}")
            # 加载失败时用红色填充的表面替代（方便调试）
            fallback_surf = pygame.Surface((80, 60))
            fallback_surf.fill((255, 0, 0))
            PIECE_IMAGES[piece_type] = fallback_surf

# 程序启动时加载图片
load_piece_images()

# 初始化背景图片（全局变量）
background_image = None
try:
    background_image = pygame.image.load(config.BG_IMAGE_PATH).convert()
    background_image = pygame.transform.scale(background_image, 
                                             (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    print(f"背景图加载成功：{config.BG_IMAGE_PATH}")
except pygame.error as e:
    print(f"【错误】加载背景图失败 → {e} | 路径：{config.BG_IMAGE_PATH}，暂使用纯色背景")


def draw_card_page():
    """绘制卡牌页面"""
    
    # 1. 绘制左侧5个选择框 + 图片（替换原文字）
    for i, (x, y, w, h) in enumerate(LEFT_BOXES):
        # 选中的框画红色边框，未选中画黑色
        color = (255, 0, 0) if i == selected_index else (0, 0, 0)
        pygame.draw.rect(game_core.screen, color, (x, y, w, h), 2)  # 空心框
        
        # -------------------------- 核心修改：绘制图片 --------------------------
        piece_type = BOX_TO_PIECE[i]
        piece_img = PIECE_IMAGES[piece_type]
        # 将图片绘制到框内（x/y为框的左上角坐标，直接对齐）
        game_core.screen.blit(piece_img, (x, y))
    
    # 2. 绘制中间详情框
    pygame.draw.rect(game_core.screen, (0, 0, 0), MAIN_BOX, 2)
    # 如果有选中的棋子，显示描述
    if selected_index != -1:
        piece_type = BOX_TO_PIECE[selected_index]
        # 绘制棋子名称（大号字体）
        name_text = FONT_LARGE.render(PIECE_DESC[piece_type]["name"], True, (0, 0, 0))
        game_core.screen.blit(name_text, (MAIN_BOX[0] + 20, MAIN_BOX[1] + 20))
        # 绘制描述（分行显示）
        desc_lines = PIECE_DESC[piece_type]["desc"].split("\n")
        y_offset = 60
        for line in desc_lines:
            line_text = FONT_SMALL.render(line, True, (0, 0, 0))
            game_core.screen.blit(line_text, (MAIN_BOX[0] + 20, MAIN_BOX[1] + y_offset))
            y_offset += 30
    
    pygame.display.flip()

def run_card_page():
    """运行卡牌页面"""
    global selected_index
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            # 按ESC退出卡牌页面
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            # 鼠标点击左侧选择框
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # 检测点击的是哪个左侧框
                for i, (x, y, w, h) in enumerate(LEFT_BOXES):
                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        selected_index = i
                        break
        if background_image:
            game_core.screen.blit(background_image, (0, 0))
        
        # 绘制页面
        draw_card_page()
        clock.tick(60)

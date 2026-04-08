# config.py - 游戏配置文件（统一管理路径/常量）
import os

# -------------------------- 字体配置 --------------------------
# 自定义字体文件路径（根据你存放的字体文件修改名称）
CUSTOM_FONT_PATH = "../Source/Fonts/Old English Text MT.ttf"
# 各模块字号配置
FONT_TITLE_SIZE = 48    # 主页标题字号
FONT_BUTTON_SIZE = 24   # 按钮文字字号

# -------------------------- 路径配置 --------------------------
# 项目根目录（自动适配不同环境）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 素材文件夹路径
SOURCE_DIR = os.path.join(BASE_DIR, "../Source")

# 背景图路径
BG_IMAGE_PATH = os.path.join(SOURCE_DIR, "木板背景.jpg")
# 按钮图片路径
ROOM_BTN_IMG = os.path.join(SOURCE_DIR, "选项.png")
CARD_BTN_IMG = os.path.join(SOURCE_DIR, "选项.png")
JOIN_BTN_IMG = os.path.join(SOURCE_DIR, "选项.png")
CREATE_BTN_IMG = os.path.join(SOURCE_DIR, "选项.png")
# 背景音乐路径
BG_MUSIC_PATH = os.path.join(SOURCE_DIR, "Jordi Savall,Montserrat Figueras,Anonymous - Greensleeves To A Ground.mp3")


# -------------------------- UI配置 --------------------------
# 窗口大小
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
# 颜色配置
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
HOVER_GRAY = (150, 150, 150)
SELECTED_COLOR = (100, 200, 255)  # IP框选中色
UNSELECTED_COLOR = (255, 255, 255)  # IP框未选中色

# -------------------------- 战棋素材路径 --------------------------
MAP_BG_PATH = os.path.join(SOURCE_DIR, "地图.png")          # 你的整块9×9地图

red_heavy_cavalry = os.path.join(SOURCE_DIR, "red/重骑_red.png")
red_light_cavalry = os.path.join(SOURCE_DIR, "red/轻骑_red.png")
red_infantry = os.path.join(SOURCE_DIR, "red/步兵_red.png")
red_archer = os.path.join(SOURCE_DIR, "red/长弓_red.png")
red_crossbowman = os.path.join(SOURCE_DIR, "red/弩手_red.png")

# 蓝方
blue_heavy_cavalry = os.path.join(SOURCE_DIR, "blue/重骑_blue.png")
blue_light_cavalry = os.path.join(SOURCE_DIR, "blue/轻骑_blue.png")
blue_infantry = os.path.join(SOURCE_DIR, "blue/步兵_blue.png")
blue_archer = os.path.join(SOURCE_DIR, "blue/长弓_blue.png")
blue_crossbowman = os.path.join(SOURCE_DIR, "blue/弩手_blue.png")
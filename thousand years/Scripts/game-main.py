import pygame
import sys
import game_core  # 导入公共核心
from room_list import run_room_list  # 导入房间列表页面

FONT_TITLE = pygame.font.SysFont("SimHei", 48)
FONT_BUTTON = pygame.font.SysFont("SimHei", 24)

# -------------------------- 资源路径配置 --------------------------
# 背景图路径
BG_IMAGE_PATH = "../Source/木板背景.jpg"
# 按钮图片路径（普通状态/悬停状态，可只配普通状态）
ROOM_BTN_IMG = "../Source/选项.png"       # 房间按钮普通图片

CARD_BTN_IMG = "../Source/选项.png"       # 卡牌按钮普通图片

# 背景音乐路径
BG_MUSIC_PATH = "../Source/Jordi Savall,Montserrat Figueras,Anonymous - Greensleeves To A Ground.mp3"

# -------------------------- 带图片的按钮类（核心拓展） --------------------------
class ImageButton:
    def __init__(self, x, y, width, height, text="", font=None, img_path=None, color_normal=game_core.GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color_normal = color_normal
        self.current_color = color_normal
        self.img = None            
        self.current_img = None  
        self.target_size = (width, height)

        if img_path:
            try:
                self.img = pygame.image.load(img_path).convert_alpha()
                self.img = pygame.transform.smoothscale(self.img, self.target_size)
                self.current_img = self.img
                print(f"按钮图片 {img_path} 已缩放至 {self.target_size}")
            except pygame.error as e:
                print(f"提示：加载按钮图片失败 → {e}，将使用纯色背景")

    def draw(self, surface):
        if self.current_img:
            surface.blit(self.current_img, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.current_color, self.rect, 0)
            pygame.draw.rect(surface, game_core.BLACK, self.rect, 2)
        
        if self.text and self.font:
            text_surf = self.font.render(self.text, True, game_core.BLACK)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
            
# -------------------------- 加载全局资源 --------------------------
# 加载背景图
background_image = None
try:
    background_image = pygame.image.load(BG_IMAGE_PATH).convert()
    background_image = pygame.transform.scale(background_image, (game_core.WINDOW_WIDTH, game_core.WINDOW_HEIGHT))
except pygame.error as e:
    print(f"提示：加载背景图失败 → {e}，暂使用纯色背景")

# 初始化音频
game_core.audio_manager.load_music(BG_MUSIC_PATH)
game_core.audio_manager.play_music()

# 初始化按钮
button_width = 240
button_height = 100
room_button = ImageButton(
    x=(game_core.WINDOW_WIDTH - button_width) // 2,
    y=200,
    width=button_width,
    height=button_height,
    text="房间",
    font=FONT_BUTTON,
    img_path=ROOM_BTN_IMG,
)
card_button = ImageButton(
    x=(game_core.WINDOW_WIDTH - button_width) // 2,
    y=320,
    width=button_width,
    height=button_height,
    text="卡牌",
    font=FONT_BUTTON,
    img_path=CARD_BTN_IMG,
)
button_list = [room_button, card_button]

# -------------------------- 游戏主循环 --------------------------
def run_main():
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            # 点击房间按钮 → 跳转到房间列表
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if room_button.rect.collidepoint(mouse_pos):
                    print("进入房间列表页面")
                    run_room_list()  # 启动房间列表页面
                if card_button.rect.collidepoint(mouse_pos):
                    print("点击了卡牌按钮（待实现）")

        # 绘制背景
        game_core.screen.fill(game_core.WHITE)
        if background_image:
            game_core.screen.blit(background_image, (0, 0))

        # 绘制标题
        title_surf = FONT_TITLE.render("游戏标题", True, game_core.BLACK)
        title_rect = title_surf.get_rect(center=(game_core.WINDOW_WIDTH//2, 160))
        game_core.screen.blit(title_surf, title_rect)

        for btn in button_list:
            btn.draw(game_core.screen)

        # 更新屏幕
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_main()
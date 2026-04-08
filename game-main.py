# game-main.py (修改后：房间按钮改开始游戏+跳转card.py+恢复系统字体)
import pygame
import sys
import game_core
import config

# 恢复系统默认字体（取消自定义字体）
FONT_TITLE = pygame.font.Font("../Source/Fonts/Old English Text MT.ttf", 48)
FONT_BUTTON = pygame.font.SysFont("SimHei", 24)

# 带图片的按钮类
class ImageButton:
    def __init__(self, x, y, width, height, text="", font=None, img_path=None, color_normal=config.GRAY):
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
                print(f"按钮图片加载成功：{img_path}（缩放至 {self.target_size}）")
            except pygame.error as e:
                print(f"【错误】加载按钮图片失败 → {e} | 路径：{img_path}，将使用纯色背景")

    def draw(self, surface):
        if self.current_img:
            surface.blit(self.current_img, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.current_color, self.rect, 0)
            pygame.draw.rect(surface, config.BLACK, self.rect, 2)
        
        if self.text and self.font:
            game_core.draw_text(surface, self.text, self.font, config.BLACK, 
                               self.rect.centerx, self.rect.centery, "center")

# 加载全局资源
background_image = None
try:
    background_image = pygame.image.load(config.BG_IMAGE_PATH).convert()
    background_image = pygame.transform.scale(background_image, 
                                             (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    print(f"背景图加载成功：{config.BG_IMAGE_PATH}")
except pygame.error as e:
    print(f"【错误】加载背景图失败 → {e} | 路径：{config.BG_IMAGE_PATH}，暂使用纯色背景")

# 初始化音频
game_core.audio_manager.load_music(config.BG_MUSIC_PATH)
game_core.audio_manager.play_music()

# 初始化按钮：房间按钮改为开始游戏按钮
button_width = 240
button_height = 100
start_button = ImageButton(
    x=(config.WINDOW_WIDTH - button_width) // 2,
    y=200,
    width=button_width,
    height=button_height,
    text="开始游戏",  # 核心修改：按钮文字改为开始游戏
    font=FONT_BUTTON,
    img_path=config.ROOM_BTN_IMG,  # 复用原房间按钮素材
)
card_button = ImageButton(
    x=(config.WINDOW_WIDTH - button_width) // 2,
    y=320,
    width=button_width,
    height=button_height,
    text="卡牌预备",  # 可选：卡牌按钮改文案，突出预备定位
    font=FONT_BUTTON,
    img_path=config.CARD_BTN_IMG,
)
button_list = [start_button, card_button]

# 主页主循环
def run_main():
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            # 点击按钮逻辑
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # 点击开始游戏按钮 → 跳转卡牌预备界面（card.py）
                if start_button.rect.collidepoint(mouse_pos):
                    print("===== 进入游戏界面 =====")
                    import game_play  # 替换原来的 import card
                    game_play.run_game_play()
                # 点击卡牌预备按钮 → 同样跳转卡牌界面（可选：也可保留原逻辑）
                if card_button.rect.collidepoint(mouse_pos):
                    print("===== 进入卡牌预备界面 =====")
                    import card
                    card.run_card_page()

        # 绘制界面
        game_core.screen.fill(config.WHITE)
        if background_image:
            game_core.screen.blit(background_image, (0, 0))

        # 绘制标题
        game_core.draw_text(game_core.screen, "A Hundred Years", FONT_TITLE, config.BLACK,
                           config.WINDOW_WIDTH//2, 160, "center")

        # 绘制按钮
        for btn in button_list:
            btn.draw(game_core.screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    run_main()
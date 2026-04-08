# game_core.py
import pygame
import config  # 导入配置文件

# 初始化pygame
pygame.init()
pygame.mixer.init()  # 单独初始化音频，避免冲突

# 唯一游戏窗口（全局复用）
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("游戏")

# 音频管理（保证背景音乐连续）
class AudioManager:
    def __init__(self):
        self.bg_music_path = None
        self.volume = 0.3
        self.is_playing = False

    def load_music(self, path):
        """加载背景音乐"""
        self.bg_music_path = path
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.volume)
            print(f"背景音乐加载成功：{path}")
        except pygame.error as e:
            print(f"【错误】加载音乐失败: {e} | 路径：{path}")

    def play_music(self, loop=-1):
        """播放音乐（loop=-1表示循环）"""
        if self.bg_music_path and not self.is_playing:
            try:
                pygame.mixer.music.play(loop)
                self.is_playing = True
                print("背景音乐开始播放")
            except pygame.error as e:
                print(f"【错误】播放音乐失败: {e}")

    def pause_music(self):
        """暂停音乐"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            print("背景音乐已暂停")

    def resume_music(self):
        """恢复音乐（切换页面时不中断）"""
        if not self.is_playing and self.bg_music_path:
            pygame.mixer.music.unpause()
            self.is_playing = True
            print("背景音乐已恢复")

# 全局音频管理器实例
audio_manager = AudioManager()

# 新增：通用工具函数（供其他文件调用）
def draw_text(surface, text, font, color, x, y, align="center"):
    """
    通用文字绘制函数
    :param surface: 绘制表面
    :param text: 文字内容
    :param font: 字体
    :param color: 颜色
    :param x: x坐标
    :param y: y坐标
    :param align: 对齐方式（center/left/right）
    """
    text_surf = font.render(text, True, color)
    if align == "center":
        text_rect = text_surf.get_rect(center=(x, y))
    elif align == "left":
        text_rect = text_surf.get_rect(topleft=(x, y))
    else:
        text_rect = text_surf.get_rect(topright=(x, y))
    surface.blit(text_surf, text_rect)
    
# 自定义字体加载（失败兜底系统默认字体）
def load_custom_font(font_path, font_size):
    """
    加载自定义字体
    :param font_path: 字体文件路径
    :param font_size: 字号
    :return: Pygame Font对象
    """
    try:
        # 加载自定义字体
        custom_font = pygame.font.Font(font_path, font_size)
        print(f"自定义字体加载成功：{font_path}（字号：{font_size}）")
        return custom_font
    except pygame.error as e:
        # 加载失败，兜底使用系统默认字体（思源黑体→黑体→默认字体）
        print(f"【警告】加载自定义字体失败 → {e}，将使用系统默认字体")
        fallback_fonts = ["SimHei", "Microsoft YaHei", None]  # 兜底字体列表
        for font_name in fallback_fonts:
            try:
                fallback_font = pygame.font.SysFont(font_name, font_size)
                print(f"兜底字体加载成功：{font_name if font_name else 'Pygame默认字体'}")
                return fallback_font
            except:
                continue
        # 终极兜底：返回Pygame内置默认字体
        return pygame.font.Font(None, font_size)
import pygame

# 全局常量
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# 初始化pygame
pygame.init()
pygame.mixer.init()  # 单独初始化音频，避免冲突

# 唯一游戏窗口（全局复用）
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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
        except pygame.error as e:
            print(f"加载音乐失败: {e}")

    def play_music(self, loop=-1):
        """播放音乐（loop=-1表示循环）"""
        if self.bg_music_path and not self.is_playing:
            pygame.mixer.music.play(loop)
            self.is_playing = True

    def pause_music(self):
        """暂停音乐"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False

    def resume_music(self):
        """恢复音乐（切换页面时不中断）"""
        if not self.is_playing and self.bg_music_path:
            pygame.mixer.music.unpause()
            self.is_playing = True

# 全局音频管理器实例
audio_manager = AudioManager()
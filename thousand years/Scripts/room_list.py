import pygame
import sys
import socket
import threading
import game_core  # 导入公共核心

# 字体配置
FONT_TITLE = pygame.font.SysFont("SimHei", 36)
FONT_TEXT = pygame.font.SysFont("SimHei", 20)
FONT_BUTTON = pygame.font.SysFont("SimHei", 24)

# 颜色配置
TRANSPARENT = (0, 0, 0, 0)  # 透明色
SELECTED_COLOR = (100, 200, 255)  # IP框选中背景色
UNSELECTED_COLOR = (255, 255, 255)  # IP框未选中背景色

# 局域网联机配置
UDP_BROADCAST_PORT = 12345
TCP_SERVER_PORT = 12346
DISCOVERY_INTERVAL = 2  # 每隔2秒广播/扫描房间
local_ip = ""  # 本地IP（自动获取）
room_ips = []  # 发现的房间IP列表
selected_ip = None  # 选中的IP
is_self_created = False  # 是否是自己创建的房间

# 资源路径配置（修改为你的实际路径）
BG_IMAGE_PATH = "../Source/木板背景.jpg"  # 房间页面背景图
JOIN_BTN_IMG = "../Source/选项.png"       # 加入按钮图片
CREATE_BTN_IMG = "../Source/选项.png"      # 创建按钮图片

# 获取本地IP（局域网）
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

local_ip = get_local_ip()

# UDP广播：发现局域网内的房间
def discover_rooms():
    global room_ips
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.settimeout(1)
    while True:
        try:
            # 发送扫描指令
            udp_socket.sendto(b"SCAN_ROOM", ("255.255.255.255", UDP_BROADCAST_PORT))
            # 接收响应
            data, addr = udp_socket.recvfrom(1024)
            if data == b"ROOM_EXISTS" and addr[0] not in room_ips:
                room_ips.append(addr[0])
        except:
            pass
        pygame.time.wait(DISCOVERY_INTERVAL * 1000)

# TCP创建房间
def create_room():
    global is_self_created
    is_self_created = True
    # 将自己的IP加入列表（显示长框）
    if local_ip not in room_ips:
        room_ips.append(local_ip)
    
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_server.bind((local_ip, TCP_SERVER_PORT))
    tcp_server.listen(5)
    print(f"房间创建成功！IP: {local_ip}:{TCP_SERVER_PORT}")
    
    # 同时启动UDP响应（告知扫描者有房间）
    def udp_response():
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            try:
                data, addr = udp_socket.recvfrom(1024)
                if data == b"SCAN_ROOM":
                    udp_socket.sendto(b"ROOM_EXISTS", addr)
            except:
                pass
    threading.Thread(target=udp_response, daemon=True).start()
    
    # 等待客户端连接
    conn, addr = tcp_server.accept()
    print(f"玩家 {addr[0]} 加入房间！")
    conn.close()
    tcp_server.close()

# 加入房间
def join_room(target_ip):
    try:
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client.connect((target_ip, TCP_SERVER_PORT))
        print(f"成功加入 {target_ip} 的房间！")
        tcp_client.close()
    except:
        print(f"加入 {target_ip} 房间失败！")
        if target_ip in room_ips:
            room_ips.remove(target_ip)  # 移除无效IP
        if selected_ip == target_ip:
            selected_ip = None  # 取消选中

# 带图片的按钮类（复用主页的图片缩放逻辑）
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

# 初始化房间列表UI元素
def init_ui():
    # 标题
    title_rect = pygame.Rect(0, 20, game_core.WINDOW_WIDTH, 50)
    # 房间列表框（仅边框，透明背景）
    list_box_rect = pygame.Rect(100, 100, 600, 300)
    # IP长框（和列表框同宽，高度40）
    ip_box_height = 40
    ip_box_rect = pygame.Rect(list_box_rect.x, list_box_rect.y, list_box_rect.width, ip_box_height)
    # 按钮（改用ImageButton）
    join_btn = ImageButton(250, 450, 120, 50, "加入", FONT_BUTTON, JOIN_BTN_IMG)
    create_btn = ImageButton(430, 450, 120, 50, "创建", FONT_BUTTON, CREATE_BTN_IMG)
    return title_rect, list_box_rect, ip_box_rect, join_btn, create_btn

# 加载背景图
def load_background():
    background = None
    try:
        background = pygame.image.load(BG_IMAGE_PATH).convert()
        background = pygame.transform.scale(background, (game_core.WINDOW_WIDTH, game_core.WINDOW_HEIGHT))
    except pygame.error as e:
        print(f"加载房间页面背景图失败 → {e}，使用纯色背景")
    return background

# 房间列表主循环
def run_room_list():
    global room_ips, selected_ip
    # 恢复背景音乐（保证连续）
    game_core.audio_manager.resume_music()
    
    # 加载背景图
    background = load_background()
    
    # 初始化UI
    title_rect, list_box_rect, ip_box_rect, join_btn, create_btn = init_ui()
    
    # 启动房间发现线程
    discover_thread = threading.Thread(target=discover_rooms, daemon=True)
    discover_thread.start()

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            # 返回主页（按ESC键）
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            # 鼠标点击事件
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # 点击创建按钮
                if create_btn.rect.collidepoint(mouse_pos):
                    threading.Thread(target=create_room, daemon=True).start()
                # 点击加入按钮
                if join_btn.rect.collidepoint(mouse_pos):
                    if selected_ip:
                        join_room(selected_ip)
                    else:
                        print("请先选中一个房间IP！")
                # 点击IP长框（选中/取消选中）
                if room_ips:
                    # 遍历所有IP框（仅第一个，按设计图单行长框）
                    ip_rect = pygame.Rect(ip_box_rect.x, ip_box_rect.y, ip_box_rect.width, ip_box_rect.height)
                    if ip_rect.collidepoint(mouse_pos):
                        selected_ip = room_ips[0] if selected_ip != room_ips[0] else None

        # 绘制界面
        game_core.screen.fill(game_core.WHITE)
        # 绘制背景图
        if background:
            game_core.screen.blit(background, (0, 0))
        
        # 1. 绘制标题
        title_surf = FONT_TITLE.render("房间一览", True, game_core.BLACK)
        title_draw_rect = title_surf.get_rect(center=title_rect.center)
        game_core.screen.blit(title_surf, title_draw_rect)
        
        # 2. 绘制房间列表框（透明背景，仅边框）
        pygame.draw.rect(game_core.screen, game_core.BLACK, list_box_rect, 2)
        
        # 3. 绘制IP长框（选中/未选中状态）
        if room_ips:
            # 仅绘制第一个IP（符合设计图单行长框）
            current_ip = room_ips[0]
            ip_rect = pygame.Rect(ip_box_rect.x, ip_box_rect.y, ip_box_rect.width, ip_box_rect.height)
            # 绘制IP框背景（选中/未选中）
            bg_color = SELECTED_COLOR if selected_ip == current_ip else UNSELECTED_COLOR
            pygame.draw.rect(game_core.screen, bg_color, ip_rect, 0)
            pygame.draw.rect(game_core.screen, game_core.BLACK, ip_rect, 1)  # IP框边框
            # 绘制IP文字
            ip_surf = FONT_TEXT.render(current_ip, True, game_core.BLACK)
            ip_text_rect = ip_surf.get_rect(center=ip_rect.center)
            game_core.screen.blit(ip_surf, ip_text_rect)
        
        # 4. 绘制按钮（图片按钮）
        join_btn.draw(game_core.screen)
        create_btn.draw(game_core.screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    run_room_list()
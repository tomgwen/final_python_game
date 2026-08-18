"""
石器時代：荒野求生 - 遊戲結束動畫 (Game Over)
純文字版：白色醒目大字 + 阿強倒地動畫 + 夜幕圖層
"""

import pygame
import os
import sys
import math
import random

# =========================================================
# 基本設定 
# =========================================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 700
FPS = 60

BLACK = (10, 10, 12)
TEXT_COLOR = (210, 210, 210)
WHITE = (255, 255, 255)       # 醒目白色字體
GOLD_LIGHT = (255, 204, 108)

def create_fonts():
    font_path = None
    for path in (r"C:\Windows\Fonts\msjh.ttc", r"C:\Windows\Fonts\msjhbd.ttc", r"C:\Windows\Fonts\mingliu.ttc"):
        if os.path.exists(path):
            font_path = path
            break
    if font_path is None:
        match = pygame.font.match_font("Microsoft JhengHei")
        if match: font_path = match

    def make(size: int):
        return pygame.font.Font(font_path, size) if font_path else pygame.font.Font(None, size)
    
    # 建立大標題與一般內文字型
    return {"title": make(68), "body": make(24), "small": make(18)}

def load_sprite(filename, col, row, width=48, height=48, scale=90):
    try:
        img_path = os.path.join("assets", filename)
        if not os.path.exists(img_path): return None
        sheet = pygame.image.load(img_path).convert_alpha()
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.blit(sheet, (0, 0), (col * width, row * height, width, height))
        return pygame.transform.smoothscale(surf, (scale, scale))
    except:
        return None

def generate_hex_background():
    bg_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_surf.fill((17, 19, 22))
    HEX_SIZE = 45
    for r in range(-2, SCREEN_HEIGHT // 30 + 2):
        for q in range(-2, SCREEN_WIDTH // 60 + 2):
            x = HEX_SIZE * math.sqrt(3) * (q + r / 2) + 50
            y = HEX_SIZE * 1.5 * r + 50
            rng = random.Random(q * 100 + r)
            roll = rng.random()
            if roll < 0.35: color = (42, 80, 49)
            elif roll < 0.55: color = (103, 103, 99)
            else: color = (86, 120, 71)
            points = [(int(x + HEX_SIZE * math.cos(math.radians(30 + i * 60))),
                       int(y + HEX_SIZE * math.sin(math.radians(30 + i * 60)))) for i in range(6)]
            pygame.draw.polygon(bg_surf, color, points)
            pygame.draw.polygon(bg_surf, (57, 61, 64), points, 1)
    return bg_surf

def load_forest_background():
    for ext in [".png", ".jpg", ".jpeg"]:
        img_path = os.path.join("assets", f"forest{ext}")
        if os.path.exists(img_path):
            try:
                bg_img = pygame.image.load(img_path).convert()
                return pygame.transform.smoothscale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except: pass
    return generate_hex_background()

def play_adventure_bgm():
    if not pygame.mixer.get_init(): pygame.mixer.init()
    for ext in [".mp3", ".ogg", ".wav"]:
        music_path = os.path.join("assets", "audio", f"adventure{ext}")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
                return True
            except: pass
    return False

# =========================================================
# 主要播放函數
# =========================================================
def play_game_over():
    pygame.init()
    pygame.mixer.init() 
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("石器時代：荒野求生 - 遊戲結束")
    clock = pygame.time.Clock()
    fonts = create_fonts()

    # 1. 載入森林背景
    forest_bg = load_forest_background()
    
    # 2. 建立夜幕圖層 (森林之上、其他元素之下)
    night_tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    night_tint.fill((20, 8, 8, 160))

    play_adventure_bgm()

    start_time = pygame.time.get_ticks()
    action = "quit"
    running = True

    CHAR_Y = SCREEN_HEIGHT // 2 + 80

    while running:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                action = "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    action = "quit"
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    running = False
                    action = "restart"
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                running = False
                action = "restart"

        # -----------------------------------------------------
        # 繪製圖層 (背景 -> 夜幕 -> 角色 -> 文字UI)
        # -----------------------------------------------------
        screen.blit(forest_bg, (0, 0))
        screen.blit(night_tint, (0, 0))

        alpha = min(255, int((elapsed / 1500) * 255))

        # 3. 繪製阿強倒地動作
        row = 9
        if elapsed < 800: col = 0
        elif elapsed < 1600: col = 1
        else: col = 2
            
        player_img = load_sprite("player_2.png", col, row, scale=130)
        if player_img:
            p_rect = player_img.get_rect(center=(SCREEN_WIDTH // 2, CHAR_Y))
            screen.blit(player_img, p_rect)

        # 4. 繪製醒目的純白色 GAME OVER 標題（帶有黑色微陰影，立體感十足）
        title_surf = pygame.Surface((SCREEN_WIDTH, 120), pygame.SRCALPHA)
        
        shadow_txt = fonts["title"].render("GAME OVER", True, (0, 0, 0))
        main_txt = fonts["title"].render("GAME OVER", True, WHITE)
        
        t_rect = main_txt.get_rect(center=(SCREEN_WIDTH // 2, 60))
        s_rect = shadow_txt.get_rect(center=(SCREEN_WIDTH // 2 + 4, 64))
        
        title_surf.blit(shadow_txt, s_rect)
        title_surf.blit(main_txt, t_rect)
        title_surf.set_alpha(alpha)
        
        screen.blit(title_surf, (0, SCREEN_HEIGHT // 2 - 170))

        # 5. 下方字幕與操作提示
        if elapsed > 1000:
            sub_alpha = min(255, int(((elapsed - 1000) / 1000) * 255))
            
            desc_txt = fonts["body"].render("阿強倒在了荒野之中，生命的火熄滅了……", True, TEXT_COLOR)
            desc_rect = desc_txt.get_rect(center=(SCREEN_WIDTH // 2, CHAR_Y + 95))
            
            prompt_txt = fonts["small"].render("按下 [Enter] 或 [滑鼠左鍵] 重新開始 | [Esc] 離開", True, GOLD_LIGHT)
            prompt_rect = prompt_txt.get_rect(center=(SCREEN_WIDTH // 2, CHAR_Y + 155))
            
            # 半透明背景框
            box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 340, CHAR_Y + 75, 680, 110)
            box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
            box_surf.fill((0, 0, 0, 190))
            box_surf.set_alpha(sub_alpha)
            screen.blit(box_surf, box_rect.topleft)
            
            if current_time % 1200 < 600:
                screen.blit(prompt_txt, prompt_rect)
            screen.blit(desc_txt, desc_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.mixer.music.fadeout(1000)
    return action

if __name__ == "__main__":
    result = play_game_over()
    print(f"[測試結果] 玩家選擇的動作是: {result}")
    pygame.quit()
    sys.exit()
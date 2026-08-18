"""
石器時代：荒野求生 - 開場故事動畫
(模組化版本：專門提供給 main.py 呼叫)
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
GOLD_LIGHT = (255, 204, 108)

STORY_PAGES = [
    [
        "387 年前，外星文明降臨地球。",
        "他們摧毀了人類賴以生存的一切：能源、通訊、城市。",
        "人類文明在短短幾年內崩潰，先進的機械被掩埋在大地之下。"
    ],
    [
        "數百年過去。",
        "森林覆蓋了城市，荒野取代了道路。",
        "石頭重新成為工具，木頭重新成為建材。"
    ],
    [
        "直到最後……只剩下一個人。",
        "阿強不知道自己為什麼還活著，身邊只有一本生存手冊。",
        "他不知道這是哪裡，但他知道一件事……"
    ]
]

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
    return {"title": make(32), "body": make(24), "small": make(18)}

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
# 主要播放函數 (回傳 True 代表進入遊戲，False 代表關閉遊戲)
# =========================================================
def play_intro():
    pygame.init()
    pygame.mixer.init() 
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("石器時代：荒野求生")
    clock = pygame.time.Clock()
    fonts = create_fonts()

    forest_bg = load_forest_background()
    night_tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    night_tint.fill((10, 15, 25, 140))

    phase = "story"      
    page_index = 0
    state_start_time = pygame.time.get_ticks()
    bgm_started = False
    
    FADE_IN_TIME = 1000
    HOLD_TIME = 3500
    FADE_OUT_TIME = 1000
    TOTAL_PAGE_TIME = FADE_IN_TIME + HOLD_TIME + FADE_OUT_TIME
    CHAR_Y = SCREEN_HEIGHT // 2 + 130 

    running = True
    start_game = False  # 預設為 False，只有在最後一頁按下確認才會變 True

    while running:
        current_time = pygame.time.get_ticks()
        
        # 事件處理 (支援滑鼠左鍵與空白鍵跳過)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if phase == "story":
                    phase = "wakeup"
                    state_start_time = current_time
                elif phase == "wakeup":
                    phase = "done"
                elif phase == "done":
                    start_game = True
                    running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if phase == "story":
                        phase = "wakeup"
                        state_start_time = current_time
                    elif phase == "wakeup":
                        phase = "done"
                    elif phase == "done":
                        start_game = True
                        running = False

        screen.fill(BLACK)

        if phase == "story":
            elapsed = current_time - state_start_time
            if elapsed < FADE_IN_TIME:
                alpha = int((elapsed / FADE_IN_TIME) * 255)
            elif elapsed < FADE_IN_TIME + HOLD_TIME:
                alpha = 255
            elif elapsed < TOTAL_PAGE_TIME:
                fade_out_elapsed = elapsed - (FADE_IN_TIME + HOLD_TIME)
                alpha = 255 - int((fade_out_elapsed / FADE_OUT_TIME) * 255)
            else:
                alpha = 0
                page_index += 1
                state_start_time = current_time
                if page_index >= len(STORY_PAGES):
                    phase = "wakeup"
                    state_start_time = current_time

            if page_index < len(STORY_PAGES):
                lines = STORY_PAGES[page_index]
                text_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                start_y = SCREEN_HEIGHT // 2 - (len(lines) * 40) // 2
                for i, line in enumerate(lines):
                    color = GOLD_LIGHT if "阿強" in line else TEXT_COLOR
                    txt_img = fonts["body"].render(line, True, color)
                    rect = txt_img.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 50))
                    text_surf.blit(txt_img, rect)
                text_surf.set_alpha(alpha)
                screen.blit(text_surf, (0, 0))

        elif phase == "wakeup":
            if not bgm_started:
                play_adventure_bgm()
                bgm_started = True
            elapsed = current_time - state_start_time
            screen.blit(forest_bg, (0, 0))
            screen.blit(night_tint, (0, 0))
            
            row = 9
            dialogue_text = ""
            dialogue_color = TEXT_COLOR
            
            if elapsed < 2000:
                col = 0
                dialogue_text = "（風聲）呼—— 呼——"
            elif elapsed < 4000:
                col = 1
                dialogue_text = "「……這是哪裡？」"
            elif elapsed < 6000:
                col = 2
                dialogue_text = "「……這是哪裡？」"
            else:
                row = 0; col = 0
                dialogue_text = "「不管怎樣……我必須活下去。」"
                dialogue_color = GOLD_LIGHT
                
            player_img = load_sprite("player_2.png", col, row, scale=144)
            if player_img:
                screen.blit(player_img, player_img.get_rect(center=(SCREEN_WIDTH//2, CHAR_Y)))
            
            if dialogue_text:
                fade_alpha = min(255, int(((elapsed % 2000) / 500) * 255)) if elapsed < 6000 else min(255, int(((elapsed - 6000) / 800) * 255))
                dialogue = fonts["body"].render(dialogue_text, True, dialogue_color)
                dialogue.set_alpha(fade_alpha)
                screen.blit(dialogue, dialogue.get_rect(center=(SCREEN_WIDTH//2, CHAR_Y + 90)))
            if elapsed >= 9000:
                phase = "done"

        elif phase == "done":
            if not bgm_started:
                play_adventure_bgm()
                bgm_started = True
            screen.blit(forest_bg, (0, 0))
            screen.blit(night_tint, (0, 0))
            
            player_img = load_sprite("player_2.png", 0, 0, scale=144)
            if player_img:
                screen.blit(player_img, player_img.get_rect(center=(SCREEN_WIDTH//2, CHAR_Y)))

            txt = fonts["title"].render("按下 [Enter] 或 [滑鼠左鍵] 開始荒野求生", True, GOLD_LIGHT)
            bg_rect = txt.get_rect(center=(SCREEN_WIDTH//2, CHAR_Y + 110))
            bg_surface = pygame.Surface((bg_rect.width + 40, bg_rect.height + 20), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            screen.blit(bg_surface, (bg_rect.x - 20, bg_rect.y - 10))
            if current_time % 1200 < 600:
                screen.blit(txt, bg_rect)

        skip_txt = fonts["small"].render("按 [左鍵] 或 [Space] 跳過 | [Esc] 關閉", True, (150, 150, 150))
        screen.blit(skip_txt, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 40))

        pygame.display.flip()
        clock.tick(FPS)

    # 動畫結束，音樂平滑淡出
    pygame.mixer.music.fadeout(1500)
    
    # 回傳玩家的選擇 (True: 開始遊戲, False: 關閉遊戲)
    return start_game

# 只有在直接執行 intro.py 時才會觸發這裡 (方便單獨測試)
if __name__ == "__main__":
    play_intro()
    pygame.quit()
    sys.exit()
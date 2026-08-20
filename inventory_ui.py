import pygame
import icon_manager
import traceback
import os  # 💡 新增匯入 os 來處理檔案路徑

# 沿用遊戲的色彩風格
PANEL = (29, 32, 36)
PANEL_2 = (38, 42, 47)
BORDER = (66, 71, 76)
TEXT = (239, 235, 221)
MUTED = (168, 169, 165)
GOLD = (229, 157, 67)

# 💡 全域變數：用來暫存阿強的頭像，避免每幀重複讀取圖片
PLAYER_PORTRAIT = None

def draw_inventory_modal(surface, fonts, game):
    global PLAYER_PORTRAIT
    try:
        # 1. 畫全螢幕的半透明黑色遮罩
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 180))
        surface.blit(shade, (0, 0))

        # 2. 決定背包面板大小與置中位置
        screen_w, screen_h = surface.get_size()
        modal_w, modal_h = 500, 420
        modal_rect = pygame.Rect((screen_w - modal_w) // 2, (screen_h - modal_h) // 2, modal_w, modal_h)

        # 畫底框
        pygame.draw.rect(surface, PANEL, modal_rect, border_radius=12)
        pygame.draw.rect(surface, BORDER, modal_rect, 2, border_radius=12)

        # 標題與關閉提示
        title_surf = fonts["heading"].render("背包與裝備", True, GOLD)
        surface.blit(title_surf, (modal_rect.x + 20, modal_rect.y + 20))
        esc_surf = fonts["tiny"].render("按 ESC 或 I 關閉", True, MUTED)
        surface.blit(esc_surf, (modal_rect.right - 120, modal_rect.y + 25))

        # 3. 裝備槽位資料準備
        arrow_amt = 0
        try:
            arrow_amt = game.inventory.get("arrow")
            if arrow_amt is None:
                arrow_amt = 0
        except Exception:
            arrow_amt = 0

        slots = [
            {"id": "axe", "name": "石斧", "type": "tools", "pos": (modal_rect.centerx - 120, modal_rect.centery - 40), "owned": getattr(game, "has_axe", False)},
            {"id": "pickaxe", "name": "石鎬", "type": "tools", "pos": (modal_rect.centerx - 120, modal_rect.centery + 60), "owned": getattr(game, "has_pickaxe", False)},
            {"id": "spear", "name": "石矛", "type": "tools", "pos": (modal_rect.centerx + 120, modal_rect.centery - 40), "owned": getattr(game, "has_spear", False)},
            {"id": "bow", "name": "木弓", "type": "tools", "pos": (modal_rect.centerx + 120, modal_rect.centery + 60), "owned": getattr(game, "has_bow", False)},
            {"id": "arrow", "name": "箭矢", "type": "resources", "pos": (modal_rect.centerx, modal_rect.centery + 90), "owned": arrow_amt > 0, "amount": arrow_amt}
        ]

        # ==========================================
        # 💡 新增：載入並裁切阿強的像素大頭貼
        # ==========================================
        if PLAYER_PORTRAIT is None:
            try:
                img_path = os.path.join("assets", "images", "characters", "player.png")
                if os.path.exists(img_path):
                    sheet = pygame.image.load(img_path).convert_alpha()
                    # 阿強的正面第一格剛好在左上角的 (0, 0)，寬高為 48x48
                    raw_portrait = sheet.subsurface(pygame.Rect(0, 0, 48, 48))

                    # 💡 修改 1：把 140 縮小到 110，這樣就不會超出直徑 90 的圓圈
                    PLAYER_PORTRAIT = pygame.transform.scale(raw_portrait, (110, 110))
                else:
                    PLAYER_PORTRAIT = "fallback"
            except Exception:
                PLAYER_PORTRAIT = "fallback"

        # 畫中間的角色示意圖底框
        center_pos = (modal_rect.centerx, modal_rect.centery - 10)
        pygame.draw.circle(surface, PANEL_2, center_pos, 45)
        pygame.draw.circle(surface, BORDER, center_pos, 45, 2)

        # 如果圖示成功載入就貼上圖片，失敗就貼「阿強」文字
        if PLAYER_PORTRAIT and PLAYER_PORTRAIT != "fallback":
            # 💡 修改 2：因為圖片本身上方有留白，所以把 Y 軸微調往上提 8 個像素 (-8)，讓他視覺上完美置中
            portrait_rect = PLAYER_PORTRAIT.get_rect(center=(center_pos[0]-2, center_pos[1] - 17))
            surface.blit(PLAYER_PORTRAIT, portrait_rect)
        else:
            player_text = fonts["heading"].render("阿強", True, TEXT)
            surface.blit(player_text, player_text.get_rect(center=center_pos))

        # 4. 畫出每一個裝備槽
        mouse_pos = pygame.mouse.get_pos()
        hovered_slot = None

        for slot in slots:
            slot_rect = pygame.Rect(0, 0, 54, 54)
            slot_rect.center = slot["pos"]

            # 槽位背景
            pygame.draw.rect(surface, PANEL_2, slot_rect, border_radius=8)
            pygame.draw.rect(surface, BORDER, slot_rect, 1, border_radius=8)

            # 滑鼠懸停效果
            if slot_rect.collidepoint(mouse_pos):
                hovered_slot = slot
                pygame.draw.rect(surface, GOLD, slot_rect, 2, border_radius=8)

            # 畫 Icon
            icon = icon_manager.get_icon(slot["type"], slot["id"], (36, 36))
            surface.blit(icon, icon.get_rect(center=slot_rect.center))

            # 未擁有時加上變暗的遮罩
            if not slot["owned"]:
                veil = pygame.Surface((54, 54), pygame.SRCALPHA)
                # 💡 調整外觀：將遮罩透明度從 180 大幅降低到 90，保留暗化效果但確保看得到圖案
                veil.fill((15, 18, 20, 90))
                surface.blit(veil, slot_rect.topleft)

            # 箭矢數量顯示
            if slot["id"] == "arrow" and slot.get("amount", 0) > 0:
                amt_text = fonts["tiny"].render(str(slot["amount"]), True, TEXT)
                surface.blit(amt_text, (slot_rect.right - 18, slot_rect.bottom - 18))

        # 5. 底部資訊區 (顯示 Hover 到的物品資訊)
        info_rect = pygame.Rect(modal_rect.x + 20, modal_rect.bottom - 85, modal_w - 40, 65)
        pygame.draw.rect(surface, PANEL_2, info_rect, border_radius=8)
        pygame.draw.rect(surface, BORDER, info_rect, 1, border_radius=8)

        if hovered_slot:
            name_surf = fonts["body"].render(hovered_slot["name"], True, GOLD)
            surface.blit(name_surf, (info_rect.x + 15, info_rect.y + 10))

            status = "已裝備" if hovered_slot["owned"] else "未擁有"
            if hovered_slot["id"] == "arrow":
                status = f"擁有數量: {hovered_slot.get('amount', 0)}"

            status_surf = fonts["small"].render(status, True, MUTED if not hovered_slot["owned"] else TEXT)
            surface.blit(status_surf, (info_rect.x + 15, info_rect.y + 36))

            # 預留耐久度顯示
            if hovered_slot["owned"] and hasattr(game, "tool_durability"):
                try:
                    dur = game.tool_durability.get(hovered_slot["id"])
                    if dur is not None:
                        dur_surf = fonts["small"].render(f"耐久度: {dur}", True, TEXT)
                        surface.blit(dur_surf, (info_rect.right - 120, info_rect.y + 36))
                except Exception:
                    pass
        else:
            hint_surf = fonts["small"].render("將游標移至圖示上以查看裝備詳細資訊", True, MUTED)
            surface.blit(hint_surf, hint_surf.get_rect(center=info_rect.center))

    except Exception as e:
        traceback.print_exc()
        error_surf = fonts["heading"].render("UI發生錯誤！請查看下方終端機紅字", True, (255, 50, 50))
        surface.blit(error_surf, (surface.get_width() // 2 - 180, 100))

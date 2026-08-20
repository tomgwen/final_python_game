import pygame
import icon_manager
import traceback
import os  # ?’¡ ?°å??¯å…¥ os ä¾†è??†æ?æ¡ˆè·¯å¾?

# æ²¿ç”¨?Šæˆ²?„è‰²å½©é¢¨??
PANEL = (29, 32, 36)
PANEL_2 = (38, 42, 47)
BORDER = (66, 71, 76)
TEXT = (239, 235, 221)
MUTED = (168, 169, 165)
GOLD = (229, 157, 67)

# ?’¡ ?¨å?è®Šæ•¸ï¼šç”¨ä¾†æš«å­˜é˜¿å¼·ç??­å?ï¼Œé¿?æ?å¹€?è?è®€?–å???
PLAYER_PORTRAIT = None

def draw_inventory_modal(surface, fonts, game):
    global PLAYER_PORTRAIT
    try:
        # 1. ?«å…¨?¢å??„å??æ?é»‘è‰²?®ç½©
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 180))
        surface.blit(shade, (0, 0))

        # 2. æ±ºå??Œå??¢æ¿å¤§å??‡ç½®ä¸­ä?ç½?
        screen_w, screen_h = surface.get_size()
        modal_w, modal_h = 500, 420
        modal_rect = pygame.Rect((screen_w - modal_w) // 2, (screen_h - modal_h) // 2, modal_w, modal_h)

        # ?«å?æ¡?
        pygame.draw.rect(surface, PANEL, modal_rect, border_radius=12)
        pygame.draw.rect(surface, BORDER, modal_rect, 2, border_radius=12)

        # æ¨™é??‡é??‰æ?ç¤?
        title_surf = fonts["heading"].render("?Œå??‡è???, True, GOLD)
        surface.blit(title_surf, (modal_rect.x + 20, modal_rect.y + 20))
        esc_surf = fonts["tiny"].render("??ESC ??I ?œé?", True, MUTED)
        surface.blit(esc_surf, (modal_rect.right - 120, modal_rect.y + 25))

        # 3. è£å?æ§½ä?è³‡æ?æº–å?
        arrow_amt = 0
        try:
            arrow_amt = game.inventory.get("arrow")
            if arrow_amt is None:
                arrow_amt = 0
        except Exception:
            arrow_amt = 0

        slots = [
            {"id": "axe", "name": "?³æ–§", "type": "tools", "pos": (modal_rect.centerx - 120, modal_rect.centery - 40), "owned": getattr(game, "has_axe", False)},
            {"id": "pickaxe", "name": "?³é¬", "type": "tools", "pos": (modal_rect.centerx - 120, modal_rect.centery + 60), "owned": getattr(game, "has_pickaxe", False)},
            {"id": "spear", "name": "?³ç?", "type": "tools", "pos": (modal_rect.centerx + 120, modal_rect.centery - 40), "owned": getattr(game, "has_spear", False)},
            {"id": "bow", "name": "?¨å?", "type": "tools", "pos": (modal_rect.centerx + 120, modal_rect.centery + 60), "owned": getattr(game, "has_bow", False)},
            {"id": "arrow", "name": "ç®­çŸ¢", "type": "resources", "pos": (modal_rect.centerx, modal_rect.centery + 90), "owned": arrow_amt > 0, "amount": arrow_amt}
        ]

        # ==========================================
        # ?’¡ ?°å?ï¼šè??¥ä¸¦è£å??¿å¼·?„å?ç´ å¤§?­è²¼
        # ==========================================
        if PLAYER_PORTRAIT is None:
            try:
                img_path = os.path.join("assets", "images", "characters", "player.png")
                if os.path.exists(img_path):
                    sheet = pygame.image.load(img_path).convert_alpha()
                    # ?¿å¼·?„æ­£?¢ç¬¬ä¸€?¼å?å¥½åœ¨å·¦ä?è§’ç? (0, 0)ï¼Œå¯¬é«˜ç‚º 48x48
                    raw_portrait = sheet.subsurface(pygame.Rect(0, 0, 48, 48))

                    # ?’¡ ä¿®æ”¹ 1ï¼šæ? 140 ç¸®å???110ï¼Œé€™æ¨£å°±ä??ƒè??ºç›´å¾?90 ?„å???
                    PLAYER_PORTRAIT = pygame.transform.scale(raw_portrait, (110, 110))
                else:
                    PLAYER_PORTRAIT = "fallback"
            except Exception:
                PLAYER_PORTRAIT = "fallback"

        # ?«ä¸­?“ç?è§’è‰²ç¤ºæ??–å?æ¡?
        center_pos = (modal_rect.centerx, modal_rect.centery - 10)
        pygame.draw.circle(surface, PANEL_2, center_pos, 45)
        pygame.draw.circle(surface, BORDER, center_pos, 45, 2)

        # å¦‚æ??–ç¤º?å?è¼‰å…¥å°±è²¼ä¸Šå??‡ï?å¤±æ?å°±è²¼?Œé˜¿å¼·ã€æ?å­?
        if PLAYER_PORTRAIT and PLAYER_PORTRAIT != "fallback":
            # ?’¡ ä¿®æ”¹ 2ï¼šå??ºå??‡æœ¬èº«ä??¹æ??™ç™½ï¼Œæ?ä»¥æ? Y è»¸å¾®èª¿å?ä¸Šæ? 8 ?‹å?ç´?(-8)ï¼Œè?ä»–è?è¦ºä?å®Œç?ç½®ä¸­
            portrait_rect = PLAYER_PORTRAIT.get_rect(center=(center_pos[0]-2, center_pos[1] - 17))
            surface.blit(PLAYER_PORTRAIT, portrait_rect)
        else:
            player_text = fonts["heading"].render("?¿å¼·", True, TEXT)
            surface.blit(player_text, player_text.get_rect(center=center_pos))

        # 4. ?«å‡ºæ¯ä??‹è??™æ§½
        mouse_pos = pygame.mouse.get_pos()
        hovered_slot = None

        for slot in slots:
            slot_rect = pygame.Rect(0, 0, 54, 54)
            slot_rect.center = slot["pos"]

            # æ§½ä??Œæ™¯
            pygame.draw.rect(surface, PANEL_2, slot_rect, border_radius=8)
            pygame.draw.rect(surface, BORDER, slot_rect, 1, border_radius=8)

            # æ»‘é??¸å??ˆæ?
            if slot_rect.collidepoint(mouse_pos):
                hovered_slot = slot
                pygame.draw.rect(surface, GOLD, slot_rect, 2, border_radius=8)

            # ??Icon
            icon = icon_manager.get_icon(slot["type"], slot["id"], (36, 36))
            surface.blit(icon, icon.get_rect(center=slot_rect.center))

            # ?ªæ??‰æ?? ä?è®Šæ??„é®ç½?
            if not slot["owned"]:
                veil = pygame.Surface((54, 54), pygame.SRCALPHA)
                # ?’¡ èª¿æ•´å¤–è?ï¼šå??®ç½©?æ?åº¦å? 180 å¤§å??ä???90ï¼Œä??™æ??–æ??œä?ç¢ºä??‹å??°å?æ¡?
                veil.fill((15, 18, 20, 90))
                surface.blit(veil, slot_rect.topleft)

            # ç®­çŸ¢?¸é?é¡¯ç¤º
            if slot["id"] == "arrow" and slot.get("amount", 0) > 0:
                amt_text = fonts["tiny"].render(str(slot["amount"]), True, TEXT)
                surface.blit(amt_text, (slot_rect.right - 18, slot_rect.bottom - 18))

        # 5. åº•éƒ¨è³‡è??€ (é¡¯ç¤º Hover ?°ç??©å?è³‡è?)
        info_rect = pygame.Rect(modal_rect.x + 20, modal_rect.bottom - 85, modal_w - 40, 65)
        pygame.draw.rect(surface, PANEL_2, info_rect, border_radius=8)
        pygame.draw.rect(surface, BORDER, info_rect, 1, border_radius=8)

        if hovered_slot:
            name_surf = fonts["body"].render(hovered_slot["name"], True, GOLD)
            surface.blit(name_surf, (info_rect.x + 15, info_rect.y + 10))

            status = "å·²è??? if hovered_slot["owned"] else "?ªæ???
            if hovered_slot["id"] == "arrow":
                status = f"?æ??¸é?: {hovered_slot.get('amount', 0)}"

            status_surf = fonts["small"].render(status, True, MUTED if not hovered_slot["owned"] else TEXT)
            surface.blit(status_surf, (info_rect.x + 15, info_rect.y + 36))

            # ?ç??ä?åº¦é¡¯ç¤?
            if hovered_slot["owned"] and hasattr(game, "tool_durability"):
                try:
                    dur = game.tool_durability.get(hovered_slot["id"])
                    if dur is not None:
                        dur_surf = fonts["small"].render(f"?ä?åº? {dur}", True, TEXT)
                        surface.blit(dur_surf, (info_rect.right - 120, info_rect.y + 36))
                except Exception:
                    pass
        else:
            hint_surf = fonts["small"].render("å°‡æ¸¸æ¨™ç§»?³å?ç¤ºä?ä»¥æŸ¥?‹è??™è©³ç´°è?è¨?, True, MUTED)
            surface.blit(hint_surf, hint_surf.get_rect(center=info_rect.center))

    except Exception as e:
        traceback.print_exc()
        error_surf = fonts["heading"].render("UI?¼ç??¯èª¤ï¼è??¥ç?ä¸‹æ–¹çµ‚ç«¯æ©Ÿç?å­?, True, (255, 50, 50))
        surface.blit(error_surf, (surface.get_width() // 2 - 180, 100))

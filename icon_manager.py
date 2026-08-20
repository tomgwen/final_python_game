import pygame
import os

# ?¨å?å¿«å?å­—å…¸ï¼Œç”¨ä¾†å??¾å·²ç¶“è??¥ä¸¦ç¸®æ”¾?ç??–ç?
# ?¼å?: {(category, name, width, height): pygame.Surface}
ICON_CACHE = {}

def get_icon(category: str, name: str, size: tuple[int, int]):
    """
    ?–å??‡å??„å?ç¤ºã€‚å??œå¿«?–ä¸­å·²æ?ï¼Œå??´æ¥?å‚³ï¼›å¦?‡è??¥ã€ç¸®?¾ä¸¦å¿«å???
    :param category: "resources", "tools", "creatures", ??"objects"
    :param name: ?–ç¤ºæª”å? (ä¸ç”¨??.pngï¼Œä?å¦?"wood")
    :param size: é¡¯ç¤º?„å¯¬é«˜ï?ä¾‹å? (24, 24)
    :return: pygame.Surface
    """
    key = (category, name, size)

    # 1. æª¢æŸ¥å¿«å?ï¼šå??œé€™å¼µ?–ã€é€™å€‹å°ºå¯¸ä??å·²ç¶“è??¥é?äº†ï?å°±ç›´?¥æ‹¿ä¾†ç”¨
    if key in ICON_CACHE:
        return ICON_CACHE[key]

    # 2. çµ„å?è·¯å?ï¼šå??‰ä??›å?å­˜å¥½??assets/icons/... çµæ?
    file_path = os.path.join("assets", "icons", category, f"{name}.png")

    # 3. ?—è©¦è¼‰å…¥?–ç?
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError

        # è¼‰å…¥ä¸¦ä??é€æ?åº?(convert_alpha ?ˆèƒ½?€å¥?
        image = pygame.image.load(file_path).convert_alpha()
        # ç¸®æ”¾?³æ?å®šå¤§å°?
        scaled_image = pygame.transform.smoothscale(image, size)

        # å­˜å…¥å¿«å?
        ICON_CACHE[key] = scaled_image
        return scaled_image

    except (FileNotFoundError, pygame.error):
        # 4. ?²å?æ©Ÿåˆ¶ (Fallback)ï¼šæ‰¾ä¸åˆ°?–ç??‚ä?è¦è??Šæˆ²å´©æ½°
        print(f"[UI è­¦å?] ?¾ä??°å?ç¤ºæ?è¼‰å…¥å¤±æ?: {file_path}")

        # ?¢ç?ä¸€?‹ç´«?²ç??¹å?ä½œç‚º?¿ä»£é¡¯ç¤º (?Šæˆ²?‹ç™¼ä¸­å¸¸è¦‹ç? missing texture é¡è‰²)
        fallback_surface = pygame.Surface(size)
        fallback_surface.fill((255, 0, 255))

        # ?ŠéŒ¯èª¤ç?ç´«è‰²?¹å?ä¹Ÿå??²å¿«?–ï??¿å?æ¯ä?å¹€?½å°?ºè­¦?Šæ???
        ICON_CACHE[key] = fallback_surface
        return fallback_surface

import pygame
import os

# 全域快取字典，用來存放已經載入並縮放過的圖片
# 格式: {(category, name, width, height): pygame.Surface}
ICON_CACHE = {}

def get_icon(category: str, name: str, size: tuple[int, int]):
    """
    取得指定的圖示。如果快取中已有，則直接回傳；否則載入、縮放並快取。
    :param category: "resources", "tools", "creatures", 或 "objects"
    :param name: 圖示檔名 (不用加 .png，例如 "wood")
    :param size: 顯示的寬高，例如 (24, 24)
    :return: pygame.Surface
    """
    key = (category, name, size)
    
    # 1. 檢查快取：如果這張圖、這個尺寸之前已經載入過了，就直接拿來用
    if key in ICON_CACHE:
        return ICON_CACHE[key]
        
    # 2. 組合路徑：對應你剛剛存好的 assets/icons/... 結構
    file_path = os.path.join("assets", "icons", category, f"{name}.png")
    
    # 3. 嘗試載入圖片
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError
            
        # 載入並保持透明度 (convert_alpha 效能最好)
        image = pygame.image.load(file_path).convert_alpha()
        # 縮放至指定大小
        scaled_image = pygame.transform.smoothscale(image, size)
        
        # 存入快取
        ICON_CACHE[key] = scaled_image
        return scaled_image
        
    except (FileNotFoundError, pygame.error):
        # 4. 防呆機制 (Fallback)：找不到圖片時不要讓遊戲崩潰
        print(f"[UI 警告] 找不到圖示或載入失敗: {file_path}")
        
        # 產生一個紫色的方塊作為替代顯示 (遊戲開發中常見的 missing texture 顏色)
        fallback_surface = pygame.Surface(size)
        fallback_surface.fill((255, 0, 255)) 
        
        # 把錯誤的紫色方塊也存進快取，避免每一幀都印出警告洗版
        ICON_CACHE[key] = fallback_surface
        return fallback_surface
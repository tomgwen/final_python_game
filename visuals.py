import pygame
import os

class VisualManager:
    def __init__(self):
        self.images = {}
        self.load_assets()

    def load_assets(self):
        asset_paths = {
            # --- 石頭多樣性 (5種) ---
            "stone_01": os.path.join("assets", "images", "objects", "rockGrey_medium4.png"),
            "stone_02": os.path.join("assets", "images", "objects", "rockGrey_medium3.png"),
            "stone_03": os.path.join("assets", "images", "objects", "rockGrey_medium2.png"),
            "stone_04": os.path.join("assets", "images", "objects", "rockGrey_medium1.png"),
            "stone_05": os.path.join("assets", "images", "objects", "rockGrey_large.png"),
            
            # --- 樹木多樣性 (3種) ---
            "tree_01": os.path.join("assets", "images", "objects", "treeRound_large.png"),
            "tree_02": os.path.join("assets", "images", "objects", "treePine_large.png"),
            "tree_03": os.path.join("assets", "images", "objects", "treePine_small.png"),
            
            
            # 👇 新增：主角的 Sprite Sheet 路徑 👇
            "player": os.path.join("assets", "images", "characters", "player.png"),
        }

        for key, path in asset_paths.items():
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    
                    # 💡 重要修改：除了主角的精靈圖之外，其他物件都縮放為 40x40
                    # 因為精靈圖需要保留原始比例 (48x48)，我們才能精準地切圖
                    if key != "player":
                        img = pygame.transform.scale(img, (40, 40))
                        
                    self.images[key] = img
                except Exception as e:
                    print(f"Warning: Failed to load image {path}: {e}")
            else:
                print(f"Notice: Image not found at {path}")

    def get_image(self, name):
        return self.images.get(name, None)

    # 👇 新增：切圖刀函式 👇
    def get_sprite(self, sheet_name, col, row, width=48, height=48, scale_to=45):
        sheet = self.get_image(sheet_name)
        if not sheet:
            return None

        if col * width >= sheet.get_width() or row * height >= sheet.get_height():
            return None

        rect = pygame.Rect(col * width, row * height, width, height)
        sprite = sheet.subsurface(rect).copy()

        if scale_to:
            sprite = pygame.transform.scale(sprite, (scale_to, scale_to))

        return sprite
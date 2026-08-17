"""繁體中文 UI - 石器時代：荒野求生"""

from __future__ import annotations

import math
import os

import pygame

from constants import (
    BUILD_TRAP,
    BUILD_WALL,
    CAMP_POSITION,
    MAP_COLS,
    MAP_ROWS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


# ============================================================
# 顏色
# ============================================================

BG = (17, 19, 22)
TOP_BAR = (23, 26, 29)

PANEL = (29, 32, 36)
PANEL_LIGHT = (37, 41, 46)
BORDER = (66, 70, 74)

TEXT = (238, 234, 220)
MUTED = (167, 168, 162)

GOLD = (229, 157, 67)
GOLD_LIGHT = (255, 201, 105)

RED = (201, 72, 65)
GREEN = (86, 160, 96)
BLUE = (69, 119, 164)

GRASS = (86, 119, 69)
FOREST = (43, 80, 49)
ROCK = (103, 103, 98)
WATER = (49, 89, 126)

FOG = (32, 34, 36)


# ============================================================
# 地圖 UI
# ============================================================

HEX_SIZE = 30

MAP_ORIGIN_X = 62
MAP_ORIGIN_Y = 145

RIGHT_X = 830


# ============================================================
# 中文字型
# ============================================================

def create_fonts() -> dict[str, pygame.font.Font]:
    """建立支援繁體中文的字型。"""

    font_path = None

    # Windows 最穩定
    windows_fonts = [
        r"C:\Windows\Fonts\msjh.ttc",
        r"C:\Windows\Fonts\msjhbd.ttc",
        r"C:\Windows\Fonts\mingliu.ttc",
    ]

    for path in windows_fonts:
        if os.path.exists(path):
            font_path = path
            break

    # 其他系統 fallback
    if font_path is None:

        names = [
            "Microsoft JhengHei",
            "Microsoft JhengHei UI",
            "Noto Sans CJK TC",
            "Arial Unicode MS",
        ]

        for name in names:

            matched = pygame.font.match_font(name)

            if matched:
                font_path = matched
                break

    def make_font(size: int, bold: bool = False):

        if font_path:

            font = pygame.font.Font(
                font_path,
                size,
            )

        else:

            font = pygame.font.Font(
                None,
                size,
            )

        font.set_bold(bold)

        return font

    return {
        "title": make_font(38, True),
        "heading": make_font(23, True),
        "body": make_font(18),
        "small": make_font(15),
        "tiny": make_font(13),
    }


# ============================================================
# 基礎繪圖
# ============================================================

def draw_text(
    surface,
    font,
    text,
    x,
    y,
    color=TEXT,
):
    image = font.render(
        str(text),
        True,
        color,
    )

    surface.blit(
        image,
        (x, y),
    )


def draw_center_text(
    surface,
    font,
    text,
    center,
    color=TEXT,
):

    image = font.render(
        str(text),
        True,
        color,
    )

    rect = image.get_rect(
        center=center
    )

    surface.blit(
        image,
        rect,
    )


def draw_panel(
    surface,
    rect,
    color=PANEL,
    radius=14,
):

    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=radius,
    )

    pygame.draw.rect(
        surface,
        BORDER,
        rect,
        width=1,
        border_radius=radius,
    )


# ============================================================
# 六角格
# ============================================================

def axial_to_pixel(q, r):

    x = (
        MAP_ORIGIN_X
        + HEX_SIZE
        * math.sqrt(3)
        * (q + r / 2)
    )

    y = (
        MAP_ORIGIN_Y
        + HEX_SIZE
        * 1.5
        * r
    )

    return int(x), int(y)


def hex_points(center):

    cx, cy = center

    points = []

    for i in range(6):

        angle = math.radians(
            30 + 60 * i
        )

        points.append(
            (
                int(
                    cx
                    + HEX_SIZE
                    * math.cos(angle)
                ),
                int(
                    cy
                    + HEX_SIZE
                    * math.sin(angle)
                ),
            )
        )

    return points


# ============================================================
# 地形
# ============================================================

def terrain_color(kind):

    return {
        "grass": GRASS,
        "forest": FOREST,
        "rock": ROCK,
        "water": WATER,
    }.get(kind, GRASS)


def draw_grass(surface, center):

    x, y = center

    color = (127, 153, 89)

    for offset in (-10, 2, 13):

        pygame.draw.line(
            surface,
            color,
            (x + offset, y + 9),
            (x + offset + 2, y + 1),
            1,
        )

        pygame.draw.line(
            surface,
            color,
            (x + offset + 2, y + 4),
            (x + offset + 6, y),
            1,
        )


def draw_tree(
    surface,
    x,
    y,
    scale=1,
):

    pygame.draw.rect(
        surface,
        (91, 62, 39),
        pygame.Rect(
            x - 2 * scale,
            y,
            4 * scale,
            10 * scale,
        ),
    )

    pygame.draw.circle(
        surface,
        (34, 69, 40),
        (x, y - 5 * scale),
        8 * scale,
    )

    pygame.draw.circle(
        surface,
        (45, 86, 48),
        (x - 5 * scale, y),
        6 * scale,
    )

    pygame.draw.circle(
        surface,
        (53, 99, 54),
        (x + 5 * scale, y),
        6 * scale,
    )


def draw_forest(surface, center):

    x, y = center

    draw_tree(
        surface,
        x,
        y - 4,
    )

    draw_tree(
        surface,
        x - 12,
        y + 5,
    )

    draw_tree(
        surface,
        x + 12,
        y + 5,
    )


def draw_rock(surface, center):

    x, y = center

    pygame.draw.polygon(
        surface,
        (144, 142, 135),
        [
            (x - 14, y + 9),
            (x - 10, y - 5),
            (x, y - 13),
            (x + 12, y - 6),
            (x + 15, y + 9),
        ],
    )

    pygame.draw.line(
        surface,
        (185, 181, 170),
        (x - 5, y - 5),
        (x + 5, y - 8),
        2,
    )


def draw_water(surface, center):

    x, y = center

    for offset in (-8, 1, 10):

        pygame.draw.arc(
            surface,
            (105, 161, 195),
            pygame.Rect(
                x - 15,
                y + offset - 4,
                30,
                8,
            ),
            math.pi,
            math.pi * 2,
            1,
        )


def draw_terrain_detail(
    surface,
    terrain,
    center,
):

    if terrain == "forest":

        draw_forest(
            surface,
            center,
        )

    elif terrain == "rock":

        draw_rock(
            surface,
            center,
        )

    elif terrain == "water":

        draw_water(
            surface,
            center,
        )

    else:

        draw_grass(
            surface,
            center,
        )


# ============================================================
# 玩家角色
# ============================================================

def draw_player(
    surface,
    center,
    has_spear=False,
    has_axe=False,
):

    x, y = center

    bob = int(
        math.sin(
            pygame.time.get_ticks()
            / 180
        )
    )

    y += bob

    # 影子
    pygame.draw.ellipse(
        surface,
        (25, 24, 22),
        pygame.Rect(
            x - 15,
            y + 15,
            30,
            9,
        ),
    )

    # 腳
    pygame.draw.line(
        surface,
        (76, 52, 36),
        (x - 5, y + 8),
        (x - 9, y + 18),
        4,
    )

    pygame.draw.line(
        surface,
        (76, 52, 36),
        (x + 5, y + 8),
        (x + 9, y + 18),
        4,
    )

    # 獸皮衣服
    pygame.draw.polygon(
        surface,
        (148, 91, 51),
        [
            (x - 11, y - 6),
            (x + 11, y - 6),
            (x + 9, y + 10),
            (x, y + 15),
            (x - 9, y + 10),
        ],
    )

    # 腰帶
    pygame.draw.line(
        surface,
        (221, 159, 83),
        (x - 8, y + 2),
        (x + 8, y + 2),
        2,
    )

    # 手
    pygame.draw.line(
        surface,
        (203, 148, 99),
        (x - 8, y - 2),
        (x - 15, y + 6),
        4,
    )

    pygame.draw.line(
        surface,
        (203, 148, 99),
        (x + 8, y - 2),
        (x + 15, y + 5),
        4,
    )

    # 頭
    pygame.draw.circle(
        surface,
        (207, 154, 106),
        (x, y - 16),
        9,
    )

    # 頭髮
    pygame.draw.arc(
        surface,
        (52, 40, 33),
        pygame.Rect(
            x - 10,
            y - 26,
            20,
            17,
        ),
        math.pi,
        math.pi * 2,
        5,
    )

    # 眼睛
    pygame.draw.circle(
        surface,
        (30, 28, 26),
        (x - 3, y - 16),
        1,
    )

    pygame.draw.circle(
        surface,
        (30, 28, 26),
        (x + 3, y - 16),
        1,
    )

    # 石矛
    if has_spear:

        pygame.draw.line(
            surface,
            (112, 74, 42),
            (x + 13, y + 11),
            (x + 21, y - 25),
            3,
        )

        pygame.draw.polygon(
            surface,
            (192, 193, 184),
            [
                (x + 21, y - 32),
                (x + 17, y - 23),
                (x + 24, y - 24),
            ],
        )

    # 石斧
    elif has_axe:

        pygame.draw.line(
            surface,
            (112, 74, 42),
            (x + 15, y + 8),
            (x + 20, y - 15),
            3,
        )

        pygame.draw.polygon(
            surface,
            (165, 168, 164),
            [
                (x + 18, y - 17),
                (x + 30, y - 20),
                (x + 26, y - 10),
                (x + 18, y - 11),
            ],
        )


# ============================================================
# 營火 / 建築
# ============================================================

def draw_campfire(
    surface,
    center,
    lit=True,
):

    x, y = center

    pygame.draw.line(
        surface,
        (96, 58, 31),
        (x - 11, y + 8),
        (x + 11, y + 2),
        5,
    )

    pygame.draw.line(
        surface,
        (96, 58, 31),
        (x - 11, y + 2),
        (x + 11, y + 8),
        5,
    )

    if lit:

        pygame.draw.polygon(
            surface,
            (241, 92, 38),
            [
                (x, y - 20),
                (x - 10, y + 4),
                (x, y),
                (x + 10, y + 4),
            ],
        )

        pygame.draw.polygon(
            surface,
            (255, 203, 71),
            [
                (x, y - 11),
                (x - 5, y + 2),
                (x + 5, y + 2),
            ],
        )


def draw_wall(surface, center):

    x, y = center

    for offset in (-12, 0, 12):

        pygame.draw.rect(
            surface,
            (121, 80, 45),
            pygame.Rect(
                x + offset - 5,
                y - 12,
                10,
                25,
            ),
            border_radius=2,
        )

        pygame.draw.circle(
            surface,
            (164, 109, 59),
            (x + offset, y - 11),
            5,
        )


def draw_trap(
    surface,
    center,
    active=True,
):

    x, y = center

    if active:
        color = (217, 177, 69)
    else:
        color = (94, 90, 82)

    pygame.draw.circle(
        surface,
        color,
        center,
        13,
        2,
    )

    pygame.draw.line(
        surface,
        color,
        (x - 8, y - 8),
        (x + 8, y + 8),
        2,
    )

    pygame.draw.line(
        surface,
        color,
        (x + 8, y - 8),
        (x - 8, y + 8),
        2,
    )


# ============================================================
# HUD
# ============================================================

def draw_bar(
    surface,
    fonts,
    x,
    y,
    width,
    label,
    value,
    maximum,
    color,
):

    draw_text(
        surface,
        fonts["small"],
        f"{label}  {value}/{maximum}",
        x,
        y,
    )

    background = pygame.Rect(
        x,
        y + 23,
        width,
        13,
    )

    pygame.draw.rect(
        surface,
        (48, 51, 54),
        background,
        border_radius=6,
    )

    ratio = 0

    if maximum > 0:
        ratio = max(
            0,
            min(
                1,
                value / maximum,
            ),
        )

    fill = pygame.Rect(
        x,
        y + 23,
        int(width * ratio),
        13,
    )

    if fill.width > 0:

        pygame.draw.rect(
            surface,
            color,
            fill,
            border_radius=6,
        )


def resource_card(
    surface,
    fonts,
    rect,
    label,
    value,
    icon_color,
):

    pygame.draw.rect(
        surface,
        PANEL_LIGHT,
        rect,
        border_radius=10,
    )

    pygame.draw.circle(
        surface,
        icon_color,
        (
            rect.x + 24,
            rect.centery,
        ),
        10,
    )

    draw_text(
        surface,
        fonts["tiny"],
        label,
        rect.x + 44,
        rect.y + 9,
        MUTED,
    )

    draw_text(
        surface,
        fonts["heading"],
        value,
        rect.x + 44,
        rect.y + 25,
    )


def draw_key_line(
    surface,
    fonts,
    x,
    y,
    key,
    label,
):

    key_rect = pygame.Rect(
        x,
        y,
        72,
        27,
    )

    pygame.draw.rect(
        surface,
        (51, 55, 60),
        key_rect,
        border_radius=6,
    )

    pygame.draw.rect(
        surface,
        (89, 93, 98),
        key_rect,
        width=1,
        border_radius=6,
    )

    draw_center_text(
        surface,
        fonts["tiny"],
        key,
        key_rect.center,
        GOLD_LIGHT,
    )

    draw_text(
        surface,
        fonts["small"],
        label,
        x + 84,
        y + 4,
    )


# ============================================================
# 教學
# ============================================================

TUTORIAL = [
    {
        "title": "歡迎來到石器時代",
        "subtitle": "你的部落需要你活下去。",
        "lines": [
            "每天只有 6 點行動點數（AP）。",
            "白天探索荒野、採集資源並準備防禦。",
            "夜晚來臨後，狼與野豬會開始襲擊。",
            "你的目標是盡可能生存更多天。",
        ],
    },
    {
        "title": "探索與採集",
        "subtitle": "每一次行動都很重要。",
        "lines": [
            "W / E / D / X / Z / A：六方向移動。",
            "森林可以取得木材。",
            "岩地可以取得石頭，草地可以取得食物。",
            "水域無法通行，站在資源格按 G 採集。",
        ],
    },
    {
        "title": "打造生存基地",
        "subtitle": "天黑以前做好準備。",
        "lines": [
            "B：建造木牆，阻擋敵人的攻擊。",
            "T：建造陷阱，傷害夜晚來襲的敵人。",
            "1：石矛　2：石斧　3：獸皮護甲。",
            "F：加入柴火　C：吃食物。",
            "準備完成後按 N 結束白天。",
        ],
    },
    {
        "title": "撐過漫長黑夜",
        "subtitle": "入夜後，荒野將變得危險。",
        "lines": [
            "A：攻擊敵人。",
            "F：添加柴火，或重新點燃營火。",
            "SPACE：結束回合，讓敵人開始行動。",
            "生命降到 0 就會遊戲結束。",
            "遊戲中隨時按 H 可以重新查看教學。",
        ],
    },
]

TUTORIAL_PAGE_COUNT = len(
    TUTORIAL
)


def draw_tutorial(
    surface,
    fonts,
    page_index,
):

    overlay = pygame.Surface(
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
        ),
        pygame.SRCALPHA,
    )

    overlay.fill(
        (0, 0, 0, 190)
    )

    surface.blit(
        overlay,
        (0, 0),
    )

    card = pygame.Rect(
        205,
        100,
        870,
        520,
    )

    pygame.draw.rect(
        surface,
        (31, 34, 38),
        card,
        border_radius=22,
    )

    pygame.draw.rect(
        surface,
        (109, 91, 67),
        card,
        width=2,
        border_radius=22,
    )

    page = TUTORIAL[
        page_index
    ]

    draw_text(
        surface,
        fonts["title"],
        page["title"],
        260,
        150,
        GOLD_LIGHT,
    )

    draw_text(
        surface,
        fonts["body"],
        page["subtitle"],
        263,
        207,
        MUTED,
    )

    y = 275

    for line in page["lines"]:

        pygame.draw.circle(
            surface,
            GOLD,
            (
                275,
                y + 10,
            ),
            5,
        )

        draw_text(
            surface,
            fonts["body"],
            line,
            300,
            y,
        )

        y += 53

    center_x = (
        SCREEN_WIDTH // 2
    )

    for i in range(
        TUTORIAL_PAGE_COUNT
    ):

        color = (
            GOLD
            if i == page_index
            else (74, 77, 81)
        )

        pygame.draw.circle(
            surface,
            color,
            (
                center_x
                - 42
                + i * 28,
                550,
            ),
            6,
        )

    draw_text(
        surface,
        fonts["small"],
        "ENTER / SPACE：下一頁",
        285,
        582,
        GOLD_LIGHT,
    )

    draw_text(
        surface,
        fonts["small"],
        "BACKSPACE：上一頁",
        525,
        582,
        MUTED,
    )

    draw_text(
        surface,
        fonts["small"],
        "S / ESC：跳過教學",
        785,
        582,
        MUTED,
    )


# ============================================================
# 開始畫面
# ============================================================

def draw_menu(
    screen,
    fonts,
):

    screen.fill(BG)

    # 背景六角格
    for row in range(9):

        for col in range(15):

            x = (
                col * 90
                + 20
                + (row % 2) * 45
            )

            y = (
                row * 80
                + 20
            )

            pygame.draw.polygon(
                screen,
                (28, 31, 34),
                [
                    (
                        int(
                            x
                            + 30
                            * math.cos(
                                math.radians(
                                    30 + i * 60
                                )
                            )
                        ),
                        int(
                            y
                            + 30
                            * math.sin(
                                math.radians(
                                    30 + i * 60
                                )
                            )
                        ),
                    )
                    for i in range(6)
                ],
                1,
            )

    draw_center_text(
        screen,
        fonts["title"],
        "石器時代：荒野求生",
        (
            SCREEN_WIDTH // 2,
            175,
        ),
        GOLD_LIGHT,
    )

    draw_center_text(
        screen,
        fonts["body"],
        "探索．採集．建造．生存",
        (
            SCREEN_WIDTH // 2,
            225,
        ),
        MUTED,
    )

    # 營火裝飾
    draw_campfire(
        screen,
        (
            SCREEN_WIDTH // 2,
            340,
        ),
        True,
    )

    draw_center_text(
        screen,
        fonts["heading"],
        "ENTER",
        (
            SCREEN_WIDTH // 2,
            445,
        ),
        GOLD_LIGHT,
    )

    draw_center_text(
        screen,
        fonts["body"],
        "開始遊戲",
        (
            SCREEN_WIDTH // 2,
            480,
        ),
    )

    draw_center_text(
        screen,
        fonts["small"],
        "遊戲開始後會先進入新手教學",
        (
            SCREEN_WIDTH // 2,
            530,
        ),
        MUTED,
    )

    draw_center_text(
        screen,
        fonts["small"],
        "ESC：離開遊戲",
        (
            SCREEN_WIDTH // 2,
            590,
        ),
        MUTED,
    )


# ============================================================
# 遊戲主畫面
# ============================================================

def draw_game(
    screen,
    fonts,
    game,
    tutorial_active=False,
    tutorial_page=0,
    max_night_rounds=4,
):

    screen.fill(BG)

    # --------------------------------------------------------
    # 上方標題列
    # --------------------------------------------------------

    pygame.draw.rect(
        screen,
        TOP_BAR,
        pygame.Rect(
            0,
            0,
            SCREEN_WIDTH,
            64,
        ),
    )

    draw_text(
        screen,
        fonts["heading"],
        "石器時代：荒野求生",
        28,
        19,
        GOLD_LIGHT,
    )

    if game.phase == "day":

        phase_text = (
            f"第 {game.day} 天"
        )

        phase_color = GOLD

    elif game.phase == "night":

        phase_text = (
            f"第 {game.day} 夜"
        )

        phase_color = BLUE

    else:

        phase_text = (
            "遊戲結束"
        )

        phase_color = RED

    pill = pygame.Rect(
        670,
        16,
        130,
        32,
    )

    pygame.draw.rect(
        screen,
        phase_color,
        pill,
        border_radius=16,
    )

    draw_center_text(
        screen,
        fonts["small"],
        phase_text,
        pill.center,
        (25, 25, 25),
    )

    draw_text(
        screen,
        fonts["small"],
        "H  遊戲教學",
        1140,
        23,
        MUTED,
    )

    # --------------------------------------------------------
    # 地圖面板
    # --------------------------------------------------------

    map_rect = pygame.Rect(
        20,
        80,
        790,
        500,
    )

    draw_panel(
        screen,
        map_rect,
        (23, 26, 29),
        16,
    )

    # 夜晚營火光暈
    if (
        game.phase == "night"
        and game.campfire.lit
    ):

        camp_center = (
            axial_to_pixel(
                *CAMP_POSITION
            )
        )

        glow = pygame.Surface(
            (320, 320),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            glow,
            (255, 145, 45, 50),
            (160, 160),
            125,
        )

        pygame.draw.circle(
            glow,
            (255, 190, 70, 25),
            (160, 160),
            155,
        )

        screen.blit(
            glow,
            (
                camp_center[0]
                - 160,
                camp_center[1]
                - 160,
            ),
        )

    # 六角地圖
    for r in range(
        MAP_ROWS
    ):

        for q in range(
            MAP_COLS
        ):

            position = (
                q,
                r,
            )

            center = axial_to_pixel(
                q,
                r,
            )

            discovered = (
                position
                in game.discovered
            )

            if discovered:

                color = terrain_color(
                    game.terrain[
                        position
                    ]
                )

            else:

                color = FOG

            points = hex_points(
                center
            )

            pygame.draw.polygon(
                screen,
                color,
                points,
            )

            pygame.draw.polygon(
                screen,
                (57, 61, 63),
                points,
                1,
            )

            if discovered:

                draw_terrain_detail(
                    screen,
                    game.terrain[
                        position
                    ],
                    center,
                )

                amount = (
                    game.resources.get(
                        position,
                        0,
                    )
                )

                if amount > 0:

                    draw_text(
                        screen,
                        fonts["tiny"],
                        str(amount),
                        center[0] + 16,
                        center[1] + 12,
                        (239, 218, 147),
                    )

    # 夜晚遮罩
    if game.phase == "night":

        tint = pygame.Surface(
            (
                map_rect.width,
                map_rect.height,
            ),
            pygame.SRCALPHA,
        )

        tint.fill(
            (5, 10, 26, 90)
        )

        screen.blit(
            tint,
            map_rect.topleft,
        )

    # 建築物
    for building in (
        game.buildings
        .buildings
        .values()
    ):

        center = axial_to_pixel(
            *building.position
        )

        if (
            building.building_type
            == BUILD_WALL
        ):

            draw_wall(
                screen,
                center,
            )

        elif (
            building.building_type
            == BUILD_TRAP
        ):

            draw_trap(
                screen,
                center,
                building.active,
            )

    # 營地
    camp_center = axial_to_pixel(
        *CAMP_POSITION
    )

    draw_campfire(
        screen,
        camp_center,
        game.campfire.lit,
    )

    # 玩家
    player_center = axial_to_pixel(
        *game.player
    )

    draw_player(
        screen,
        player_center,
        game.has_spear,
        game.has_axe,
    )

    # --------------------------------------------------------
    # 生存紀錄
    # --------------------------------------------------------

    log_rect = pygame.Rect(
        20,
        595,
        790,
        105,
    )

    draw_panel(
        screen,
        log_rect,
        (23, 26, 29),
        14,
    )

    draw_text(
        screen,
        fonts["small"],
        "生存紀錄",
        38,
        610,
        GOLD_LIGHT,
    )

    y = 638

    for message in (
        game.logs[-3:]
    ):

        draw_text(
            screen,
            fonts["small"],
            "• " + message[:70],
            38,
            y,
            MUTED,
        )

        y += 20

    # --------------------------------------------------------
    # 右側 HUD
    # --------------------------------------------------------

    right_panel = pygame.Rect(
        RIGHT_X,
        80,
        430,
        620,
    )

    draw_panel(
        screen,
        right_panel,
        PANEL,
        16,
    )

    draw_text(
        screen,
        fonts["heading"],
        "生存狀態",
        855,
        105,
    )

    draw_bar(
        screen,
        fonts,
        855,
        145,
        175,
        "生命",
        game.survival.health,
        100,
        RED,
    )

    draw_bar(
        screen,
        fonts,
        1050,
        145,
        175,
        "護甲",
        game.survival.armor,
        50,
        BLUE,
    )

    draw_bar(
        screen,
        fonts,
        855,
        198,
        370,
        "飢餓",
        game.survival.hunger,
        100,
        GOLD,
    )

    # 資源卡
    resource_card(
        screen,
        fonts,
        pygame.Rect(
            855,
            255,
            175,
            58,
        ),
        "食物",
        game.inventory.get(
            "food"
        ),
        (178, 87, 63),
    )

    resource_card(
        screen,
        fonts,
        pygame.Rect(
            1050,
            255,
            175,
            58,
        ),
        "木材",
        game.inventory.get(
            "wood"
        ),
        (132, 87, 51),
    )

    resource_card(
        screen,
        fonts,
        pygame.Rect(
            855,
            324,
            175,
            58,
        ),
        "石頭",
        game.inventory.get(
            "stone"
        ),
        (145, 145, 143),
    )

    resource_card(
        screen,
        fonts,
        pygame.Rect(
            1050,
            324,
            175,
            58,
        ),
        "獸皮",
        game.inventory.get(
            "hide"
        ),
        (159, 116, 71),
    )

    # 營火狀態
    fire_rect = pygame.Rect(
        855,
        398,
        370,
        52,
    )

    pygame.draw.rect(
        screen,
        PANEL_LIGHT,
        fire_rect,
        border_radius=10,
    )

    draw_text(
        screen,
        fonts["small"],
        "營火",
        870,
        408,
        MUTED,
    )

    fire_status = (
        "燃燒中"
        if game.campfire.lit
        else "已熄滅"
    )

    draw_text(
        screen,
        fonts["body"],
        (
            f"{fire_status}"
            f"   燃料 "
            f"{game.campfire.fuel}/12"
        ),
        980,
        407,
        (
            GOLD_LIGHT
            if game.campfire.lit
            else RED
        ),
    )

    # --------------------------------------------------------
    # 操作區
    # --------------------------------------------------------

    if game.phase == "day":

        draw_text(
            screen,
            fonts["heading"],
            (
                f"行動點數  "
                f"{game.actions_left}/6"
            ),
            855,
            475,
            GOLD_LIGHT,
        )

        controls = [
            (
                "WEDXZA",
                "移動",
            ),
            (
                "G",
                "採集資源",
            ),
            (
                "C",
                "吃食物",
            ),
            (
                "B / T",
                "木牆 / 陷阱",
            ),
            (
                "1/2/3",
                "石矛 / 石斧 / 護甲",
            ),
            (
                "F",
                "加入柴火",
            ),
            (
                "N",
                "結束白天",
            ),
        ]

        y = 515

    elif game.phase == "night":

        draw_text(
            screen,
            fonts["heading"],
            (
                f"夜晚回合 "
                f"{game.night_round}/"
                f"{max_night_rounds}"
            ),
            855,
            475,
            (126, 164, 210),
        )

        draw_text(
            screen,
            fonts["small"],
            (
                "剩餘敵人："
                f"{len(game.alive_enemies())}"
            ),
            855,
            507,
            RED,
        )

        controls = [
            (
                "A",
                "攻擊敵人",
            ),
            (
                "F",
                "加入柴火",
            ),
            (
                "SPACE",
                "結束回合",
            ),
        ]

        y = 545

    else:

        draw_text(
            screen,
            fonts["heading"],
            "你沒有撐過這次生存挑戰",
            855,
            475,
            RED,
        )

        controls = [
            (
                "R",
                "重新開始",
            ),
            (
                "ESC",
                "離開遊戲",
            ),
        ]

        y = 530

    for key, label in controls:

        draw_key_line(
            screen,
            fonts,
            855,
            y,
            key,
            label,
        )

        y += 32

    if tutorial_active:

        draw_tutorial(
            screen,
            fonts,
            tutorial_page,
        )
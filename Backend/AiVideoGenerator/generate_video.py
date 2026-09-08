import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip, AudioFileClip


# ============================================================
# SIH - FINAL CORPORATE AI VIDEO GENERATOR
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

SCENE_DATA_FILE = BASE_DIR / "scene_data.json"
AUDIO_DIR = BASE_DIR / "audio"
SCENES_DIR = BASE_DIR / "scenes"
CHARACTER_FILE = BASE_DIR / "character" / "character_image.png"

FINAL_VIDEO = BASE_DIR / "final_SIH_storytelling_video.mp4"
FINAL_SRT = BASE_DIR / "final_SIH_storytelling_video.srt"
FINAL_VTT = BASE_DIR / "final_SIH_storytelling_video.vtt"

AUDIO_DIR.mkdir(exist_ok=True)
SCENES_DIR.mkdir(exist_ok=True)


# ============================================================
# VIDEO SETTINGS
# ============================================================

W = 1280
H = 720
FPS = 24


# ============================================================
# COLOURS
# ============================================================

WHITE = (255, 255, 255)
NAVY = (20, 39, 64)

DARK_BG = (18, 28, 42)
DARK_PANEL = (30, 45, 62)

BLUE = (57, 132, 224)
CYAN = (67, 190, 222)
GREEN = (70, 184, 130)
PURPLE = (145, 105, 215)
ORANGE = (238, 158, 73)

GREY = (103, 121, 140)
LIGHT_GREY = (220, 229, 237)
LIGHT_BG = (242, 247, 252)
LIGHT_BLUE = (120, 190, 245)


# ============================================================
# FONTS
# ============================================================

def get_font(size, bold=False):

    if bold:
        paths = [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
        ]
    else:
        paths = [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
        ]

    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


FONT_TOPIC = get_font(42, True)
FONT_TITLE = get_font(30, True)
FONT_CARD = get_font(23, True)
FONT_BODY = get_font(19, False)
FONT_SMALL = get_font(17, True)
FONT_SUBTITLE = get_font(27, True)
FONT_BIG = get_font(50, True)
FONT_TINY = get_font(15, True)


# ============================================================
# BASIC HELPERS
# ============================================================

def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, float(value)))


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def safe_box(box):
    x1, y1, x2, y2 = [
        int(round(float(v))) for v in box
    ]

    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))

    if x2 <= x1:
        x2 = x1 + 2

    if y2 <= y1:
        y2 = y1 + 2

    return x1, y1, x2, y2


def text_size(draw, text, font):
    box = draw.textbbox(
        (0, 0),
        str(text),
        font=font
    )

    return (
        box[2] - box[0],
        box[3] - box[1]
    )


def wrap_text(draw, text, font, max_width, max_lines=10):

    words = str(text).split()

    if not words:
        return []

    lines = []
    current = ""

    for word in words:

        test = (
            current + " " + word
        ).strip()

        width = text_size(
            draw,
            test,
            font
        )[0]

        if width <= max_width:
            current = test

        else:

            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    return lines[:max_lines]


def fit_font(
    draw,
    text,
    max_width,
    max_height,
    start_size,
    min_size=18,
    bold=True
):
    """
    Automatically reduce font size until text fits.
    """

    size = start_size

    while size >= min_size:

        font = get_font(size, bold)

        lines = wrap_text(
            draw,
            text,
            font,
            max_width,
            10
        )

        line_height = int(size * 1.18)

        total_height = len(lines) * line_height

        widest = 0

        for line in lines:
            widest = max(
                widest,
                text_size(
                    draw,
                    line,
                    font
                )[0]
            )

        if (
            widest <= max_width
            and total_height <= max_height
        ):
            return font, lines, line_height

        size -= 2

    font = get_font(min_size, bold)

    return (
        font,
        wrap_text(
            draw,
            text,
            font,
            max_width,
            10
        ),
        int(min_size * 1.18)
    )


def draw_text_block(
    draw,
    x,
    y,
    text,
    font,
    fill,
    width,
    gap=28,
    max_lines=5
):

    lines = wrap_text(
        draw,
        text,
        font,
        width,
        max_lines
    )

    for i, line in enumerate(lines):

        draw.text(
            (
                x,
                y + i * gap
            ),
            line,
            font=font,
            fill=fill
        )


def centered(
    draw,
    box,
    text,
    font,
    fill=NAVY
):

    x1, y1, x2, y2 = safe_box(box)

    tw, th = text_size(
        draw,
        text,
        font
    )

    draw.text(
        (
            x1 + (x2 - x1 - tw) / 2,
            y1 + (y2 - y1 - th) / 2
        ),
        str(text),
        font=font,
        fill=fill
    )


def rounded(
    draw,
    box,
    radius=18,
    fill=WHITE,
    outline=None,
    width=1
):

    draw.rounded_rectangle(
        safe_box(box),
        radius=max(1, int(radius)),
        fill=fill,
        outline=outline,
        width=max(1, int(width))
    )


# ============================================================
# BACKGROUND
# ============================================================

def scene_theme(scene, topic=""):
    text = scene_text(scene) + " " + str(topic).lower()
    explicit = str(scene.get("background_theme", "")).lower().strip()
    if explicit in {"water","environment","technology","security","finance","healthcare","infrastructure","government","business"}:
        return explicit
    rules = {
        "water":["water","reservoir","pipeline","leak","flow","pressure","municipal","irrigation"],
        "environment":["environment","climate","carbon","emission","waste","sustainability","forest"],
        "security":["security","cyber","threat","attack","privacy","malware","risk"],
        "healthcare":["health","medical","hospital","patient","clinical","disease"],
        "finance":["finance","revenue","profit","budget","cost","investment","bank","market"],
        "technology":["technology","software","ai","artificial intelligence","digital","cloud","algorithm"],
        "infrastructure":["infrastructure","construction","road","bridge","building","transport","project"],
        "government":["government","policy","public sector","ministry","municipal","compliance","regulation"],
        "business":["business","customer","sales","strategy","operations","management","employee"],
    }
    scores = {k: sum(text.count(x) for x in vals) for k, vals in rules.items()}
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "business"

def create_background(scene_no, dark=False, phase=0.0, scene=None):
    """Render a genuinely content-aware visual world for each scene/theme.

    The background is not a single reusable corporate gradient.  It uses
    theme-specific motifs, composition variants and optional dark emphasis.
    """
    scene = scene or {}
    topic = str(scene.get("topic", ""))
    theme = scene_theme(scene, topic)
    variant_seed = sum(ord(c) for c in (theme + str(scene_no))) + len(scene_text(scene))
    variant = variant_seed % 4
    p = float(phase)

    light_palettes = {
        "water": ((235,250,255), (90,205,230), (165,225,248), CYAN),
        "environment": ((239,250,243), (120,205,155), (180,230,195), GREEN),
        "technology": ((244,241,255), (150,130,235), (180,205,250), PURPLE),
        "security": ((238,246,252), (95,165,220), (165,145,220), CYAN),
        "finance": ((252,249,238), (225,190,90), (175,220,190), ORANGE),
        "healthcare": ((237,250,250), (85,195,185), (175,220,240), CYAN),
        "infrastructure": ((243,246,249), (175,190,205), (238,180,120), ORANGE),
        "government": ((238,246,255), (125,175,225), (185,200,240), BLUE),
        "business": ((247,244,252), (180,150,225), (170,205,245), PURPLE),
    }
    dark_palettes = {
        "water": ((13,39,53), (25,104,135), (45,82,125), CYAN),
        "environment": ((16,48,34), (30,105,66), (45,88,80), GREEN),
        "technology": ((27,23,55), (70,52,140), (55,85,145), PURPLE),
        "security": ((12,25,40), (25,88,130), (62,48,110), CYAN),
        "finance": ((39,35,24), (115,88,40), (45,98,70), ORANGE),
        "healthcare": ((12,43,43), (30,110,100), (42,73,115), CYAN),
        "infrastructure": ((32,34,38), (85,88,95), (115,70,40), ORANGE),
        "government": ((15,35,52), (35,78,120), (62,70,115), BLUE),
        "business": ((28,24,44), (74,52,112), (48,82,120), PURPLE),
    }

    base, g1, g2, accent = (dark_palettes if dark else light_palettes).get(
        theme, (dark_palettes if dark else light_palettes)["business"]
    )

    image = Image.new("RGBA", (W, H), base + (255,))
    draw = ImageDraw.Draw(image, "RGBA")

    # Soft depth blocks with scene-dependent placement.
    if variant == 0:
        draw.ellipse((-360, -300, 470, 470), fill=g1 + (95,))
        draw.ellipse((780, 275, 1510, 930), fill=g2 + (86,))
    elif variant == 1:
        draw.ellipse((720, -280, 1430, 470), fill=g1 + (92,))
        draw.ellipse((-320, 330, 520, 980), fill=g2 + (82,))
    elif variant == 2:
        draw.ellipse((250, -220, 1050, 560), fill=g1 + (72,))
        draw.ellipse((760, 260, 1450, 890), fill=g2 + (90,))
    else:
        draw.ellipse((-240, 110, 620, 900), fill=g1 + (80,))
        draw.ellipse((620, -250, 1370, 500), fill=g2 + (82,))

    # Distinct background language by subject.
    if theme == "security":
        # Clean security motif. No full-screen grid or long crossing lines.
        r = 118 + int(6 * math.sin(p * math.pi * 2))
        cx, cy = 1035, 315
        shield = [
            (cx, cy-r),
            (cx+r*.78, cy-r*.52),
            (cx+r*.62, cy+r*.45),
            (cx, cy+r),
            (cx-r*.62, cy+r*.45),
            (cx-r*.78, cy-r*.52)
        ]
        draw.polygon(
            shield,
            fill=(20,55,78,90) if not dark else (20,50,70,150),
            outline=accent+(135,)
        )
        draw.line(
            (cx-r*.36, cy, cx-r*.08, cy+r*.25, cx+r*.45, cy-r*.30),
            fill=GREEN+(190,),
            width=6
        )
        for px, py in [(875, 515), (1040, 565), (1150, 470)]:
            draw.ellipse((px-7, py-7, px+7, py+7), fill=accent+(95,))
    elif theme == "water":
        # Clean water identity without full-width crossing lines.
        # Keep the motif confined to small bubbles/ripples so it never
        # competes with scene titles or foreground cards.
        bubbles = [
            (1055, 150, 18),
            (1125, 205, 11),
            (1190, 145, 8),
            (1085, 245, 7),
        ]
        for bx, by, br in bubbles:
            pulse = int(2 * math.sin(p * 5 + bx / 80))
            rr = max(4, br + pulse)
            draw.ellipse(
                (bx-rr, by-rr, bx+rr, by+rr),
                outline=accent+(82,),
                width=3
            )
            draw.ellipse(
                (bx-3, by-3, bx+3, by+3),
                fill=WHITE+(115,)
            )
        # Two short, contained ripple accents in the lower-right corner.
        for k in range(2):
            x0 = 1115 + k * 62
            y0 = 560 + k * 28
            draw.arc(
                (x0-34, y0-12, x0+34, y0+12),
                15, 165,
                fill=accent+(55,),
                width=3
            )
    elif theme == "technology":
        for yy in range(135, 630, 72):
            for x in range(90, 560, 95):
                draw.line((x,yy,x+55,yy), fill=accent+(42,), width=3)
                draw.ellipse((x+48,yy-6,x+60,yy+6), fill=accent+(95,))
        for k in range(4):
            rr = 95 + k*42
            draw.arc((930-rr,300-rr,930+rr,300+rr), 25, 315, fill=accent+(58,), width=4)
        draw.ellipse((875,245,985,355), outline=accent+(110,), width=7)
        centered(draw,(875,270,985,330),"AI",get_font(30,True),WHITE if dark else NAVY)
    elif theme == "finance":
        heights = [80,135,105,175,145,205]
        for j, h in enumerate(heights):
            x = 80 + j*70
            draw.rounded_rectangle((x,560-h,x+42,560), radius=8, fill=accent+(58,))
        points=[(70,520),(180,475),(290,495),(410,405),(520,360),(610,300)]
        draw.line(points, fill=accent+(105,), width=5)
        for x,y in points:
            draw.ellipse((x-6,y-6,x+6,y+6), fill=accent+(145,))
    elif theme == "healthcare":
        pts=[(70,390),(170,390),(200,345),(230,430),(270,390),(390,390),(430,335),(470,445),(510,390),(640,390)]
        draw.line(pts, fill=accent+(86,), width=5)
        draw.rounded_rectangle((1010,195,1150,335), radius=22, outline=accent+(80,), width=5)
        draw.rectangle((1068,220,1092,310), fill=accent+(95,))
        draw.rectangle((1035,258,1125,282), fill=accent+(95,))
    elif theme == "infrastructure":
        # Contained structural motif; avoid a full-screen drafting grid.
        for j in range(3):
            x1 = 760 + j*120
            draw.line((x1, 565, x1+75, 350), fill=accent+(48,), width=3)
            draw.line((x1+75, 350, x1+150, 565), fill=accent+(48,), width=3)
    elif theme == "government":
        # Institutional columns / document seal language.
        for x in range(90,1210,135):
            draw.rectangle((x,220,x+54,570), fill=accent+(22,))
            draw.ellipse((x-8,195,x+62,235), fill=accent+(24,))
        draw.ellipse((970,170,1160,360), outline=accent+(62,), width=5)
        draw.ellipse((1005,205,1125,325), outline=accent+(42,), width=3)
    elif theme == "environment":
        for i in range(7):
            x=90+i*165
            draw.arc((x,400,x+120,560),195,345,fill=accent+(58,),width=5)
        for x,y in [(150,220),(320,180),(500,230),(660,170)]:
            draw.ellipse((x-24,y-24,x+24,y+24),outline=accent+(55,),width=4)
    else:
        # Clean business background: contained cards only, no long diagonal bands.
        for j in range(3):
            x = 880 + j*110 + int(math.sin(p*4+j)*5)
            y = 455 + j*55
            draw.rounded_rectangle(
                (x, y, x+92, y+54),
                radius=15,
                outline=accent+(55,),
                width=2
            )

    # Consistent but minimal identity marker.
    draw.rectangle((0, 0, W, 5), fill=accent + (255,))
    if dark:
        draw.rounded_rectangle((W-155, 26, W-42, 49), radius=11, fill=accent+(85,))
    else:
        draw.rounded_rectangle((W-155, 26, W-42, 49), radius=11, fill=accent+(52,))

    return image

def draw_topic_heading(
    image,
    topic,
    dark=False,
    scene_no=1
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    fg = WHITE if dark else NAVY

    sub = (
        (180, 200, 220)
        if dark
        else GREY
    )

    rounded(
        draw,
        (
            42,
            30,
            51,
            100
        ),
        4,
        BLUE + (255,)
    )

    topic = str(topic).strip()

    # IMPORTANT:
    # Automatically fit long topic.
    font, lines, line_height = fit_font(
        draw,
        topic,
        1120,
        58,
        42,
        26,
        True
    )

    y = 27

    # Keep top heading maximum 2 lines.
    for line in lines[:2]:

        draw.text(
            (
                70,
                y
            ),
            line,
            font=font,
            fill=fg
        )

        y += line_height

    draw.text(
        (
            72,
            82
        ),
        f"CONTENT TRANSFORMATION  •  {scene_no:02d}",
        font=FONT_TINY,
        fill=sub
    )


# ============================================================
# SCENE TITLE
# ============================================================

def draw_scene_title(
    image,
    scene,
    dark=False
):

    title = str(
        scene.get(
            "scene_title",
            ""
        )
    ).strip()

    if not title:
        return

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    fg = WHITE if dark else NAVY

    font, lines, line_height = fit_font(
        draw,
        title,
        1080,
        72,
        30,
        20,
        True
    )

    y = 132

    for line in lines[:2]:

        draw.text(
            (
                72,
                y
            ),
            line,
            font=font,
            fill=fg
        )

        y += line_height


# ============================================================
# PANEL
# ============================================================

def draw_panel(
    image,
    box_value,
    dark=False,
    accent=BLUE
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    x1, y1, x2, y2 = safe_box(
        box_value
    )

    # Shadow
    rounded(
        draw,
        (
            x1 + 8,
            y1 + 10,
            x2 + 8,
            y2 + 10
        ),
        22,
        (
            0,
            0,
            0,
            65 if dark else 28
        )
    )

    if dark:

        fill = (
            29,
            43,
            59,
            238
        )

        outline = (
            95,
            125,
            150,
            150
        )

    else:

        fill = (
            255,
            255,
            255,
            255
        )

        outline = (
            205,
            220,
            235,
            230
        )

    rounded(
        draw,
        (
            x1,
            y1,
            x2,
            y2
        ),
        22,
        fill,
        outline,
        1
    )

    draw.rounded_rectangle(
        (
            x1,
            y1,
            x1 + 7,
            y2
        ),
        radius=4,
        fill=accent + (230,)
    )


# ============================================================
# PILL
# ============================================================

def draw_pill(
    image,
    x,
    y,
    text,
    accent=BLUE,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    text = str(text)

    tw, th = text_size(
        draw,
        text,
        FONT_SMALL
    )

    rounded(
        draw,
        (
            x,
            y,
            x + tw + 34,
            y + 38
        ),
        19,
        (
            (30, 47, 64, 230)
            if dark
            else (255, 255, 255, 245)
        ),
        accent + (150,),
        1
    )

    draw.ellipse(
        safe_box(
            (
                x + 11,
                y + 13,
                x + 19,
                y + 21
            )
        ),
        fill=accent + (255,)
    )

    draw.text(
        (
            x + 27,
            y + 8
        ),
        text,
        font=FONT_SMALL,
        fill=WHITE if dark else NAVY
    )


# ============================================================
# CHARACTER
# ============================================================

def load_character():
    candidates = [
        CHARACTER_FILE,
        BASE_DIR / "character" / "charcater_image.png",
        BASE_DIR / "character" / "charcater_image.png.png",
    ]

    character_path = next((p for p in candidates if p.exists()), None)

    if character_path is None:
        print()
        print("WARNING: character image not found.")
        print("Fallback presenter will be used.")
        return None

    try:
        image = Image.open(character_path).convert("RGBA")
        data = np.array(image)
        rgb = data[:, :, :3]
        alpha = data[:, :, 3]

        white_mask = (
            (rgb[:, :, 0] > 247)
            & (rgb[:, :, 1] > 247)
            & (rgb[:, :, 2] > 247)
        )
        alpha[white_mask] = 0
        data[:, :, 3] = alpha

        print(f"Character loaded: {character_path.name}")
        return Image.fromarray(data, "RGBA")
    except Exception as e:
        print("Character loading failed:", e)
        return None


CHARACTER = load_character()


def paste_character(
    image,
    character,
    area
):

    if character is None:
        return False

    x1, y1, x2, y2 = safe_box(area)

    iw, ih = character.size

    scale = min(
        (x2 - x1) / iw,
        (y2 - y1) / ih
    )

    new_w = max(
        1,
        int(iw * scale)
    )

    new_h = max(
        1,
        int(ih * scale)
    )

    resized = character.resize(
        (
            new_w,
            new_h
        ),
        Image.Resampling.LANCZOS
    )

    x = (
        x1
        + (x2 - x1 - new_w) // 2
    )

    y = y2 - new_h

    image.alpha_composite(
        resized,
        (x, y)
    )

    return True


# ============================================================
# FALLBACK PERSON
# ============================================================

def draw_fallback_person(
    image,
    center,
    scale=1.0,
    accent=BLUE,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    cx, cy = center

    s = max(
        0.5,
        float(scale)
    )

    skin = (
        239,
        190,
        155
    )

    hair = (
        55,
        62,
        73
    )

    # Shadow
    draw.ellipse(
        safe_box(
            (
                cx - 80 * s,
                cy + 170 * s,
                cx + 80 * s,
                cy + 205 * s
            )
        ),
        fill=(
            0,
            0,
            0,
            70 if dark else 35
        )
    )

    r = 46 * s

    # Head
    draw.ellipse(
        safe_box(
            (
                cx - r,
                cy - 171 * s,
                cx + r,
                cy - 79 * s
            )
        ),
        fill=skin + (255,)
    )

    # Hair
    draw.pieslice(
        safe_box(
            (
                cx - r - 2,
                cy - 191 * s,
                cx + r + 2,
                cy - 95 * s
            )
        ),
        180,
        355,
        fill=hair + (255,)
    )

    eye_y = cy - 132 * s

    for ex in (-16, 16):

        draw.ellipse(
            safe_box(
                (
                    cx + ex * s - 3,
                    eye_y - 3,
                    cx + ex * s + 3,
                    eye_y + 3
                )
            ),
            fill=NAVY + (255,)
        )

    draw.arc(
        safe_box(
            (
                cx - 18 * s,
                cy - 119 * s,
                cx + 18 * s,
                cy - 99 * s
            )
        ),
        10,
        170,
        fill=(120, 70, 70, 255),
        width=max(
            1,
            int(3 * s)
        )
    )

    # Neck
    draw.rectangle(
        safe_box(
            (
                cx - 17 * s,
                cy - 84 * s,
                cx + 17 * s,
                cy - 52 * s
            )
        ),
        fill=skin + (255,)
    )

    # Body
    rounded(
        draw,
        (
            cx - 78 * s,
            cy - 58 * s,
            cx + 78 * s,
            cy + 135 * s
        ),
        28,
        accent + (245,)
    )

    # Shirt
    draw.polygon(
        [
            (
                cx - 28 * s,
                cy - 57 * s
            ),
            (
                cx,
                cy - 20 * s
            ),
            (
                cx + 28 * s,
                cy - 57 * s
            )
        ],
        fill=WHITE + (245,)
    )

    # Arms
    draw.line(
        (
            cx - 60 * s,
            cy - 20 * s,
            cx - 112 * s,
            cy + 75 * s
        ),
        fill=accent + (245,),
        width=max(
            8,
            int(20 * s)
        )
    )

    draw.line(
        (
            cx + 60 * s,
            cy - 20 * s,
            cx + 112 * s,
            cy + 75 * s
        ),
        fill=accent + (245,),
        width=max(
            8,
            int(20 * s)
        )
    )


# ============================================================
# DOCUMENT
# ============================================================

def draw_document(
    image,
    center,
    scale=1.0,
    progress=1.0,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    cx, cy = center

    p = ease_out(progress)

    w = max(
        30,
        int(110 * scale * p)
    )

    h = max(
        40,
        int(140 * scale * p)
    )

    x1, y1, x2, y2 = safe_box(
        (
            cx - w / 2,
            cy - h / 2,
            cx + w / 2,
            cy + h / 2
        )
    )

    rounded(
        draw,
        (
            x1,
            y1,
            x2,
            y2
        ),
        14,
        (34, 50, 68, 255) if dark else WHITE,
        CYAN + (255,),
        3
    )

    fold = max(
        8,
        int(min(w, h) * 0.18)
    )

    draw.polygon(
        [
            (
                x2 - fold,
                y1
            ),
            (
                x2,
                y1
            ),
            (
                x2,
                y1 + fold
            )
        ],
        fill=LIGHT_GREY + (220,)
    )

    for i in range(4):

        yy = (
            y1
            + 35
            + i * max(
                15,
                int(h * 0.15)
            )
        )

        if yy + 5 < y2 - 8:

            rounded(
                draw,
                (
                    x1 + 20,
                    yy,
                    x2 - 20,
                    yy + 6
                ),
                3,
                LIGHT_BLUE + (255,)
            )


# ============================================================
# AI ORB
# ============================================================

def draw_ai_orb(
    image,
    center,
    scale=1.0,
    progress=1.0,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    cx, cy = center

    pulse = (
        0.95
        + 0.05
        * math.sin(
            progress * math.pi * 2
        )
    )

    r = max(
        20,
        int(
            62
            * scale
            * pulse
        )
    )

    draw.ellipse(
        safe_box(
            (
                cx - r,
                cy - r,
                cx + r,
                cy + r
            )
        ),
        fill=(
            (30, 47, 66, 255)
            if dark
            else WHITE
        ),
        outline=BLUE + (255,),
        width=max(
            3,
            int(7 * scale)
        )
    )

    draw.ellipse(
        safe_box(
            (
                cx - r * 0.72,
                cy - r * 0.72,
                cx + r * 0.72,
                cy + r * 0.72
            )
        ),
        outline=CYAN + (170,),
        width=max(
            2,
            int(3 * scale)
        )
    )

    centered(
        draw,
        (
            cx - r,
            cy - 22,
            cx + r,
            cy + 22
        ),
        "AI",
        get_font(
            max(
                18,
                int(30 * scale)
            ),
            True
        ),
        WHITE if dark else NAVY
    )


# ============================================================
# CHECK
# ============================================================

def draw_check(
    image,
    center,
    scale=1.0,
    progress=1.0
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    cx, cy = center

    r = max(
        8,
        int(
            44
            * scale
            * ease_out(progress)
        )
    )

    draw.ellipse(
        safe_box(
            (
                cx - r,
                cy - r,
                cx + r,
                cy + r
            )
        ),
        fill=(
            225,
            249,
            238,
            255
        ),
        outline=GREEN + (255,),
        width=max(
            2,
            int(4 * scale)
        )
    )

    draw.line(
        (
            cx - r * 0.42,
            cy,
            cx - r * 0.10,
            cy + r * 0.35,
            cx + r * 0.52,
            cy - r * 0.42
        ),
        fill=GREEN + (255,),
        width=max(
            3,
            int(7 * scale)
        )
    )


# ============================================================
# ARROW
# ============================================================

def draw_arrow(
    draw,
    start,
    end,
    color=BLUE,
    width=5,
    progress=1.0
):

    p = ease_out(progress)

    x1, y1 = start
    x2, y2 = end

    ex = x1 + (x2 - x1) * p
    ey = y1 + (y2 - y1) * p

    draw.line(
        (
            x1,
            y1,
            ex,
            ey
        ),
        fill=color + (235,),
        width=max(
            1,
            int(width)
        )
    )

    if p > 0.65:

        angle = math.atan2(
            ey - y1,
            ex - x1
        )

        size = 14

        p1 = (
            ex - size * math.cos(angle - 0.55),
            ey - size * math.sin(angle - 0.55)
        )

        p2 = (
            ex - size * math.cos(angle + 0.55),
            ey - size * math.sin(angle + 0.55)
        )

        draw.polygon(
            [
                (
                    ex,
                    ey
                ),
                p1,
                p2
            ],
            fill=color + (235,)
        )


# ============================================================
# WORKFLOW
# ============================================================

def draw_workflow_scene(
    image,
    scene,
    progress,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    labels = [
        "SOURCE",
        "AI",
        "ANALYSIS",
        "RESULT"
    ]

    positions = [
        170,
        470,
        770,
        1070
    ]

    colors = [
        BLUE,
        PURPLE,
        CYAN,
        GREEN
    ]

    y = 330

    for i in range(4):

        x = positions[i]
        label = labels[i]
        accent = colors[i]

        draw_panel(
            image,
            (
                x - 88,
                y - 75,
                x + 88,
                y + 75
            ),
            dark,
            accent
        )

        p = clamp(
            progress * 1.7 - i * 0.18
        )

        if i == 0:

            draw_document(
                image,
                (
                    x,
                    y - 5
                ),
                0.72,
                p,
                dark
            )

        elif i == 1:

            draw_ai_orb(
                image,
                (
                    x,
                    y - 5
                ),
                0.82,
                p,
                dark
            )

        elif i == 2:

            for j in range(4):

                xx = (
                    x
                    - 42
                    + j * 28
                )

                yy = (
                    y
                    - 30
                    + math.sin(
                        j + progress * 4
                    ) * 12
                )

                draw.ellipse(
                    safe_box(
                        (
                            xx - 8,
                            yy - 8,
                            xx + 8,
                            yy + 8
                        )
                    ),
                    fill=CYAN + (255,)
                )

        else:

            draw_check(
                image,
                (
                    x,
                    y - 5
                ),
                0.82,
                p
            )

        centered(
            draw,
            (
                x - 75,
                y + 38,
                x + 75,
                y + 72
            ),
            label,
            FONT_SMALL,
            WHITE if dark else NAVY
        )

        if i < 3:

            draw_arrow(
                draw,
                (
                    x + 100,
                    y
                ),
                (
                    positions[i + 1] - 100,
                    y
                ),
                accent,
                5,
                progress
            )


# ============================================================
# DOCUMENT SCENE
# ============================================================

def draw_documents_scene(
    image,
    scene,
    progress,
    dark=False
):

    draw_panel(
        image,
        (
            70,
            190,
            430,
            545
        ),
        dark,
        BLUE
    )

    draw_document(
        image,
        (
            250,
            335
        ),
        1.5,
        progress,
        dark
    )

    draw_pill(
        image,
        110,
        490,
        "SOURCE CONTENT",
        BLUE,
        dark
    )

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    draw_arrow(
        draw,
        (
            455,
            350
        ),
        (
            570,
            350
        ),
        PURPLE,
        7,
        progress
    )

    draw_ai_orb(
        image,
        (
            635,
            350
        ),
        1.05,
        progress,
        dark
    )

    draw_panel(
        image,
        (
            805,
            160,
            1195,
            555
        ),
        dark,
        GREEN
    )

    cards = [
        (900, 235, "SUMMARY"),
        (1050, 235, "INSIGHT"),
        (900, 385, "ACTION"),
        (1050, 385, "OUTPUT")
    ]

    for i, (
        x,
        y,
        label
    ) in enumerate(cards):

        rounded(
            draw,
            (
                x - 68,
                y - 50,
                x + 68,
                y + 50
            ),
            14,
            (
                (45, 64, 82, 240)
                if dark
                else WHITE
            ),
            GREEN + (170,),
            2
        )

        draw_check(
            image,
            (
                x,
                y - 5
            ),
            0.38,
            clamp(
                progress * 1.7
                - i * 0.15
            )
        )

        centered(
            draw,
            (
                x - 55,
                y + 20,
                x + 55,
                y + 45
            ),
            label,
            FONT_TINY,
            WHITE if dark else NAVY
        )

    draw_arrow(
        draw,
        (
            710,
            350
        ),
        (
            795,
            350
        ),
        GREEN,
        7,
        progress
    )


# ============================================================
# DATA SCENE
# ============================================================

def draw_data_scene(
    image,
    scene,
    progress,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    draw_panel(
        image,
        (
            70,
            180,
            750,
            470
        ),
        dark,
        BLUE
    )

    draw_panel(
        image,
        (
            790,
            180,
            1195,
            470
        ),
        dark,
        GREEN
    )

    fg = WHITE if dark else NAVY

    draw.text(
        (
            95,
            205
        ),
        "Key trend",
        font=FONT_CARD,
        fill=fg
    )

    draw.text(
        (
            815,
            205
        ),
        "Comparison",
        font=FONT_CARD,
        fill=fg
    )

    left = 115
    right = 720
    top = 260
    bottom = 425

    for i in range(4):

        yy = (
            top
            + i * (bottom - top) / 3
        )

        draw.line(
            (
                left,
                yy,
                right,
                yy
            ),
            fill=(
                130,
                155,
                175,
                65
            ),
            width=1
        )

    values = [
        0.25,
        0.34,
        0.29,
        0.48,
        0.43,
        0.62,
        0.57,
        0.80
    ]

    points = []

    for i, value in enumerate(values):

        x = (
            left
            + i * (right - left)
            / (len(values) - 1)
        )

        y = (
            bottom
            - value * (bottom - top)
        )

        y = (
            bottom
            + (y - bottom)
            * ease_out(progress)
        )

        points.append(
            (
                x,
                y
            )
        )

    draw.line(
        points,
        fill=BLUE + (255,),
        width=6,
        joint="curve"
    )

    for x, y in points:

        draw.ellipse(
            safe_box(
                (
                    x - 6,
                    y - 6,
                    x + 6,
                    y + 6
                )
            ),
            fill=WHITE,
            outline=CYAN + (255,),
            width=3
        )

    values = [
        0.30,
        0.48,
        0.42,
        0.67,
        0.82
    ]

    spacing = (
        1195 - 790 - 90
    ) / len(values)

    base = 430

    for i, value in enumerate(values):

        p = clamp(
            progress * 1.5
            - i * 0.12
        )

        height = int(
            170
            * value
            * ease_out(p)
        )

        x = int(
            835 + i * spacing
        )

        rounded(
            draw,
            (
                x,
                base - height,
                x + max(
                    18,
                    int(spacing * 0.45)
                ),
                base
            ),
            8,
            GREEN + (235,)
        )

    draw_panel(
        image,
        (
            90,
            500,
            1190,
            615
        ),
        dark,
        ORANGE
    )

    insight = str(
        scene.get(
            "on_screen_text",
            "Key insight from the data"
        )
    )

    draw_text_block(
        draw,
        135,
        525,
        insight,
        FONT_BODY,
        fg,
        980,
        27,
        2
    )


# ============================================================
# SECURITY
# ============================================================

def draw_security_scene(
    image,
    scene,
    progress,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    draw_panel(
        image,
        (
            70,
            190,
            520,
            510
        ),
        dark,
        GREEN
    )

    fg = WHITE if dark else NAVY

    draw.text(
        (
            110,
            225
        ),
        "PROTECTED FLOW",
        font=FONT_BIG,
        fill=fg
    )

    draw_text_block(
        draw,
        110,
        315,
        scene.get(
            "visual_concept",
            "Secure information flow"
        ),
        FONT_BODY,
        WHITE if dark else GREY,
        340,
        30,
        5
    )

    cx = 900
    cy = 325
    r = 115

    points = [
        (
            cx,
            cy - r
        ),
        (
            cx + r * 0.72,
            cy - r * 0.55
        ),
        (
            cx + r * 0.62,
            cy + r * 0.35
        ),
        (
            cx,
            cy + r
        ),
        (
            cx - r * 0.62,
            cy + r * 0.35
        ),
        (
            cx - r * 0.72,
            cy - r * 0.55
        )
    ]

    draw.polygon(
        points,
        fill=(
            (32, 52, 72, 255)
            if dark
            else (225, 241, 255, 255)
        ),
        outline=CYAN + (255,)
    )

    draw.line(
        (
            cx - r * 0.35,
            cy,
            cx - r * 0.08,
            cy + r * 0.30,
            cx + r * 0.42,
            cy - r * 0.35
        ),
        fill=GREEN + (255,),
        width=7
    )

    for x, y in [
        (680, 210),
        (1090, 215),
        (690, 470),
        (1090, 475)
    ]:

        draw.line(
            (
                cx,
                cy,
                x,
                y
            ),
            fill=CYAN + (100,),
            width=3
        )

        draw.ellipse(
            safe_box(
                (
                    x - 17,
                    y - 17,
                    x + 17,
                    y + 17
                )
            ),
            fill=WHITE if not dark else DARK_PANEL,
            outline=BLUE + (255,),
            width=3
        )


# ============================================================
# PEOPLE
# ============================================================

def draw_people_scene(
    image,
    scene,
    progress,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    draw_panel(
        image,
        (
            70,
            180,
            550,
            500
        ),
        dark,
        BLUE
    )

    fg = WHITE if dark else NAVY

    draw.text(
        (
            110,
            220
        ),
        "PEOPLE",
        font=FONT_BIG,
        fill=fg
    )

    draw_text_block(
        draw,
        110,
        305,
        scene.get(
            "visual_concept",
            "Connected people and stakeholders"
        ),
        FONT_BODY,
        WHITE if dark else GREY,
        340,
        30,
        5
    )

    positions = [
        (760, 405),
        (900, 355),
        (1040, 405)
    ]

    colors = [
        BLUE,
        CYAN,
        PURPLE
    ]

    for pos, color in zip(
        positions,
        colors
    ):

        draw_fallback_person(
            image,
            pos,
            0.52,
            color,
            dark
        )

    draw.line(
        (
            760,
            500,
            1040,
            500
        ),
        fill=LIGHT_BLUE + (120,),
        width=3
    )


# ============================================================
# BUILDING
# ============================================================

def draw_building_scene(
    image,
    scene,
    progress,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    fg = WHITE if dark else NAVY

    draw_panel(
        image,
        (
            70,
            200,
            570,
            505
        ),
        dark,
        ORANGE
    )

    draw.text(
        (
            110,
            240
        ),
        "PROJECT VIEW",
        font=FONT_BIG,
        fill=fg
    )

    draw_text_block(
        draw,
        110,
        325,
        scene.get(
            "visual_concept",
            "Project and property overview"
        ),
        FONT_BODY,
        WHITE if dark else GREY,
        390,
        30,
        5
    )

    draw_panel(
        image,
        (
            650,
            150,
            1180,
            575
        ),
        dark,
        BLUE
    )

    x1 = 700
    x2 = 1120
    y1 = 190
    y2 = 540

    rounded(
        draw,
        (
            x1,
            y1,
            x2,
            y2
        ),
        18,
        (
            (35, 58, 78, 255)
            if dark
            else (225, 238, 248, 255)
        ),
        BLUE + (255,),
        3
    )

    for row in range(6):

        for col in range(5):

            rounded(
                draw,
                (
                    x1 + 35 + col * 72,
                    y1 + 35 + row * 50,
                    x1 + 73 + col * 72,
                    y1 + 62 + row * 50
                ),
                4,
                CYAN + (190,)
            )


# ============================================================
# FACTORY
# ============================================================

def draw_factory_scene(
    image,
    scene,
    progress,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    fg = WHITE if dark else NAVY

    draw_panel(
        image,
        (
            70,
            190,
            535,
            510
        ),
        dark,
        BLUE
    )

    draw.text(
        (
            105,
            230
        ),
        "OPERATIONS",
        font=FONT_BIG,
        fill=fg
    )

    draw_text_block(
        draw,
        105,
        315,
        scene.get(
            "visual_concept",
            "Operations and production flow"
        ),
        FONT_BODY,
        WHITE if dark else GREY,
        360,
        30,
        5
    )

    draw_panel(
        image,
        (
            610,
            160,
            1190,
            560
        ),
        dark,
        ORANGE
    )

    x1 = 690
    x2 = 1110
    y1 = 330
    y2 = 500

    rounded(
        draw,
        (
            x1,
            y1,
            x2,
            y2
        ),
        16,
        (
            (36, 54, 70, 255)
            if dark
            else WHITE
        ),
        ORANGE + (255,),
        3
    )

    draw.polygon(
        [
            (
                x1 + 25,
                y1
            ),
            (
                (x1 + x2) / 2,
                y1 - 95
            ),
            (
                x2 - 25,
                y1
            )
        ],
        fill=(
            (53, 72, 90, 255)
            if dark
            else (214, 225, 235, 255)
        )
    )

    draw.line(
        (
            x1 + 30,
            y2 - 45,
            x2 - 30,
            y2 - 45
        ),
        fill=BLUE + (255,),
        width=9
    )

    px = (
        x1
        + 40
        + int(
            (
                x2 - x1 - 80
            ) * clamp(progress)
        )
    )

    draw.ellipse(
        safe_box(
            (
                px - 12,
                y2 - 57,
                px + 12,
                y2 - 33
            )
        ),
        fill=ORANGE + (255,)
    )


# ============================================================
# TECHNOLOGY
# ============================================================

def draw_technology_scene(
    image,
    scene,
    progress,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    fg = WHITE if dark else NAVY

    draw_panel(
        image,
        (
            65,
            190,
            560,
            510
        ),
        dark,
        PURPLE
    )

    draw.text(
        (
            105,
            230
        ),
        "INTELLIGENT SYSTEM",
        font=get_font(40, True),
        fill=fg
    )

    draw_text_block(
        draw,
        105,
        320,
        scene.get(
            "visual_concept",
            "AI-powered digital intelligence"
        ),
        FONT_BODY,
        WHITE if dark else GREY,
        385,
        30,
        5
    )

    draw_ai_orb(
        image,
        (
            850,
            340
        ),
        1.65,
        progress,
        dark
    )

    for i in range(12):

        angle = (
            i / 12 * math.pi * 2
            + progress * math.pi * 0.35
        )

        radius = (
            175
            + 15 * math.sin(
                progress * 5 + i
            )
        )

        x = (
            850
            + math.cos(angle) * radius
        )

        y = (
            340
            + math.sin(angle) * radius
        )

        draw.ellipse(
            safe_box(
                (
                    x - 5,
                    y - 5,
                    x + 5,
                    y + 5
                )
            ),
            fill=CYAN + (220,)
        )


# ============================================================
# GENERAL CONCEPT
# ============================================================

def draw_concept_scene(
    image,
    scene,
    progress,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    fg = WHITE if dark else NAVY

    draw_panel(
        image,
        (
            70,
            185,
            760,
            540
        ),
        dark,
        BLUE
    )

    title = str(
        scene.get(
            "scene_title",
            "Key concept"
        )
    )

    font, lines, line_height = fit_font(
        draw,
        title,
        590,
        80,
        42,
        24,
        True
    )

    y = 225

    for line in lines[:2]:

        draw.text(
            (
                115,
                y
            ),
            line,
            font=font,
            fill=fg
        )

        y += line_height

    draw_text_block(
        draw,
        115,
        320,
        scene.get(
            "visual_concept",
            ""
        ),
        FONT_BODY,
        WHITE if dark else GREY,
        555,
        30,
        6
    )

    cards = [
        (
            920,
            240,
            BLUE,
            "IDEA"
        ),
        (
            1030,
            350,
            CYAN,
            "ACTION"
        ),
        (
            900,
            465,
            GREEN,
            "RESULT"
        )
    ]

    for x, y, accent, label in cards:

        rounded(
            draw,
            (
                x - 85,
                y - 45,
                x + 85,
                y + 45
            ),
            18,
            (
                (38, 55, 72, 240)
                if dark
                else WHITE
            ),
            accent + (230,),
            2
        )

        draw.ellipse(
            safe_box(
                (
                    x - 54,
                    y - 12,
                    x - 30,
                    y + 12
                )
            ),
            fill=accent + (255,)
        )

        centered(
            draw,
            (
                x - 20,
                y - 25,
                x + 70,
                y + 25
            ),
            label,
            FONT_SMALL,
            WHITE if dark else NAVY
        )


# ============================================================
# INTRO
# ============================================================

def draw_intro(
    image,
    scene,
    topic,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    fg = WHITE if dark else NAVY

    secondary = (
        (190, 208, 224)
        if dark
        else GREY
    )

    # --------------------------------------------------------
    # CHARACTER - INTRO ONLY
    # --------------------------------------------------------

    character_used = paste_character(
        image,
        CHARACTER,
        (
            12,
            185,
            355,
            615
        )
    )

    if not character_used:

        draw_fallback_person(
            image,
            (
                270,
                500
            ),
            1.45,
            BLUE,
            dark
        )

    # --------------------------------------------------------
    # INTRO PANEL
    # --------------------------------------------------------

    draw_panel(
        image,
        (
            425,
            170,
            1195,
            500
        ),
        dark,
        BLUE
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Fit long topic INSIDE panel.
    # --------------------------------------------------------

    topic_text = str(topic).strip()

    title_font, title_lines, title_gap = fit_font(
        draw,
        topic_text,
        600,
        105,
        50,
        25,
        True
    )

    title_y = 215

    for line in title_lines[:2]:

        draw.text(
            (
                465,
                title_y
            ),
            line,
            font=title_font,
            fill=fg
        )

        title_y += title_gap

    # --------------------------------------------------------
    # CONCEPT
    # --------------------------------------------------------

    concept = str(
        scene.get(
            "visual_concept",
            "AI-powered transformation of complex content into clear communication."
        )
    ).strip()

    if not concept:

        concept = (
            "AI-powered transformation "
            "of complex content into clear "
            "communication."
        )

    draw_text_block(
        draw,
        555,
        335,
        concept,
        FONT_BODY,
        secondary,
        550,
        30,
        4
    )

    draw_pill(
        image,
        555,
        445,
        "AI-POWERED EXPLAINER",
        CYAN,
        dark
    )


# ============================================================
# CONCLUSION
# ============================================================

def draw_conclusion(
    image,
    scene,
    topic,
    dark=False
):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    fg = WHITE if dark else NAVY

    secondary = (
        (190, 208, 224)
        if dark
        else GREY
    )

    draw_panel(
        image,
        (
            75,
            185,
            820,
            505
        ),
        dark,
        GREEN
    )

    draw.text(
        (
            120,
            230
        ),
        "KEY TAKEAWAY",
        font=FONT_BIG,
        fill=fg
    )

    draw_text_block(
        draw,
        120,
        330,
        scene.get(
            "visual_concept",
            ""
        ),
        FONT_BODY,
        secondary,
        600,
        30,
        5
    )

    draw_ai_orb(
        image,
        (
            960,
            315
        ),
        0.85,
        1,
        dark
    )

    safe_topic = str(topic)

    # Prevent pill overflow
    if len(safe_topic) > 25:
        safe_topic = safe_topic[:22] + "..."

    draw_pill(
        image,
        760,
        510,
        safe_topic,
        GREEN,
        dark
    )


# ============================================================
# DATA DETECTION
# ============================================================

def is_data_scene(scene):
    """Return True only when the scene explicitly requires quantitative graphics."""
    value = scene.get("show_chart", False)
    if isinstance(value, str):
        explicit = value.strip().lower() in {"true", "yes", "1"}
    else:
        explicit = bool(value)

    visual_type = str(scene.get("visual_type", "")).strip().lower()

    if not explicit:
        return False

    return visual_type in {"chart", "dashboard"} or bool(str(scene.get("chart_type", "")).strip())


# ============================================================
# SCENE TEXT HELPER
# ============================================================

def scene_text(scene):
    """Return all relevant scene text as one lowercase string for visual routing."""
    parts = [
        scene.get("scene_title", ""),
        scene.get("visual_type", ""),
        scene.get("visual_concept", ""),
        scene.get("narration", ""),
        scene.get("on_screen_text", ""),
    ]
    return " ".join(str(p) for p in parts if p).lower()


# ============================================================
# VISUAL ROUTER
# ============================================================

def choose_visual(scene, index):
    """Content-aware visual router using Gemini's scene plan."""
    text = scene_text(scene)
    vt = str(scene.get("visual_type", "")).strip().lower().replace("-", "_").replace(" ", "_")
    theme = str(scene.get("background_theme", "")).strip().lower()

    if index == 1 or vt == "intro":
        return "intro"
    if vt == "conclusion":
        return "conclusion"

    # Explicit chart request only.
    if vt in {"chart", "graph"} and bool(scene.get("show_chart", False)):
        return "data"

    visual_map = {
        "process": "workflow",
        "workflow": "workflow",
        "pipeline": "workflow",
        "timeline": "timeline",
        "comparison": "comparison",
        "dashboard": "dashboard",
        "network": "network",
        "security": "security",
        "healthcare": "people",
        "people": "people",
        "education": "people",
        "documents": "documents",
        "document": "documents",
        "pdf": "documents",
        "real_estate": "building",
        "building": "building",
        "construction": "building",
        "manufacturing": "factory",
        "factory": "factory",
        "production": "factory",
        "technology": "technology",
        "digital": "technology",
        "ai": "technology",
        "finance": "data" if scene.get("show_chart") else "comparison",
        "domain": "domain",
        "concept": "concept",
    }

    if vt in visual_map:
        visual = visual_map[vt]
        if visual == "data" and not scene.get("show_chart"):
            return "comparison"
        return visual

    # Domain-specific fallback.
    water_terms = ["water", "reservoir", "pipeline", "leak", "flow", "pressure", "municipal", "urban"]
    if theme == "water" or any(k in text for k in water_terms):
        return "domain"

    if any(k in text for k in ["map", "location", "geographic", "region", "district", "city"]):
        return "network"

    if any(k in text for k in ["security", "cyber", "privacy", "protection", "secure", "threat", "attack"]):
        return "security"

    if any(k in text for k in ["document", "pdf", "report", "file", "record", "compliance"]):
        return "documents"

    if any(k in text for k in ["timeline", "month", "phase", "milestone", "roadmap"]):
        return "timeline"

    if any(k in text for k in ["compare", "versus", "before", "after", "target", "baseline"]):
        return "comparison"

    if any(k in text for k in ["workflow", "process", "pipeline", "automation", "step", "input", "output"]):
        return "workflow"

    if any(k in text for k in ["customer", "employee", "team", "people", "user", "stakeholder", "worker"]):
        return "people"

    if any(k in text for k in ["building", "property", "real estate", "construction", "project"]):
        return "building"

    if any(k in text for k in ["factory", "manufacturing", "production", "machine", "plant"]):
        return "factory"

    if any(k in text for k in ["technology", "digital", "ai", "artificial intelligence", "platform", "software", "system"]):
        return "technology"

    return "concept"

def draw_timeline_scene(image, scene, progress, dark=False):
    draw = ImageDraw.Draw(image, "RGBA")
    fg = WHITE if dark else NAVY
    accent = GREEN if "implementation" in scene_text(scene) or "roadmap" in scene_text(scene) else BLUE

    draw_panel(image, (90, 205, 1190, 500), dark, accent)
    y = 345
    x_positions = [180, 470, 760, 1050]
    labels = ["START", "INTEGRATE", "PILOT", "SCALE"]

    draw.line((150, y, 1080, y), fill=LIGHT_BLUE + (130,), width=7)

    for i, (x, label) in enumerate(zip(x_positions, labels)):
        p = clamp(progress * 1.6 - i * 0.18)
        r = max(10, int(22 * ease_out(p)))
        draw.ellipse(safe_box((x-r, y-r, x+r, y+r)),
                     fill=accent + (255,), outline=WHITE + (220,), width=3)
        centered(draw, (x-78, y+35, x+78, y+72), label, FONT_SMALL, fg)

    caption = str(scene.get("on_screen_text", "")).strip()
    if caption:
        font, lines, gap = fit_font(draw, caption, 900, 55, 24, 18, True)
        y2 = 240
        for line in lines[:2]:
            centered(draw, (190, y2, 1090, y2+gap), line, font, fg)
            y2 += gap


def draw_comparison_scene(image, scene, progress, dark=False):
    draw = ImageDraw.Draw(image, "RGBA")
    fg = WHITE if dark else NAVY
    left_accent = BLUE
    right_accent = GREEN

    draw_panel(image, (70, 205, 595, 555), dark, left_accent)
    draw_panel(image, (685, 205, 1210, 555), dark, right_accent)

    left_title = "CURRENT"
    right_title = "TARGET"
    centered(draw, (120, 235, 545, 275), left_title, FONT_CARD, fg)
    centered(draw, (735, 235, 1160, 275), right_title, FONT_CARD, fg)

    for x, y, color, label in [
        (330, 350, left_accent, "BASELINE"),
        (950, 350, right_accent, "IMPROVED"),
    ]:
        p = ease_out(clamp(progress * 1.4))
        draw.ellipse(safe_box((x-70, y-70, x+70, y+70)), fill=color + (28,), outline=color+(220,), width=5)
        centered(draw, (x-105, y-20, x+105, y+25), label, FONT_SMALL, fg)
        draw.line((x-55, y+55, x+55, y+55), fill=color+(200,), width=max(2,int(10*p)))

    source = str(scene.get("visual_concept", "")).strip()
    draw_text_block(draw, 130, 445, source, FONT_BODY, WHITE if dark else GREY, 420, 28, 3)


def draw_dashboard_scene(image, scene, progress, dark=False):
    draw = ImageDraw.Draw(image, "RGBA")
    fg = WHITE if dark else NAVY
    accents = [BLUE, CYAN, GREEN, PURPLE]

    draw_panel(image, (65, 195, 1215, 560), dark, BLUE)

    cards = [
        (125, 250, 365, 360, "STATUS"),
        (395, 250, 635, 360, "ALERT"),
        (665, 250, 905, 360, "TREND"),
        (935, 250, 1175, 360, "ACTION"),
    ]
    for i, (x1, y1, x2, y2, label) in enumerate(cards):
        rounded(draw, (x1, y1, x2, y2), 18,
                (38,55,72,225) if dark else WHITE,
                accents[i] + (180,), 2)
        centered(draw, (x1+15, y1+14, x2-15, y1+45), label, FONT_SMALL, fg)
        p = ease_out(clamp(progress * 1.5 - i * 0.12))
        draw.ellipse(safe_box((x1+25, y1+55, x1+60, y1+90)),
                     fill=accents[i]+(220,))
        draw.line((x1+80, y1+73, x2-25, y1+73), fill=LIGHT_BLUE+(110,), width=5)
        draw.line((x1+80, y1+73, x1+80+(x2-x1-105)*p, y1+73),
                  fill=accents[i]+(220,), width=5)

    insight = str(scene.get("on_screen_text", "")).strip()
    if insight:
        draw_text_block(draw, 135, 405, insight, FONT_BODY, fg, 980, 28, 2)


def draw_network_scene(image, scene, progress, dark=False):
    draw = ImageDraw.Draw(image, "RGBA")
    fg = WHITE if dark else NAVY
    accent = CYAN

    draw_panel(image, (80, 190, 1200, 565), dark, accent)

    center = (640, 370)
    nodes = [(220, 275), (420, 500), (645, 230), (880, 500), (1070, 280)]

    for i, (x, y) in enumerate(nodes):
        draw.line((center[0], center[1], x, y), fill=LIGHT_BLUE+(120,), width=4)
        r = 20 + int(8 * ease_out(clamp(progress * 1.6 - i * 0.14)))
        draw.ellipse(safe_box((x-r, y-r, x+r, y+r)), fill=accent+(210,), outline=WHITE+(220,), width=2)

    r = 58 + int(10 * math.sin(progress * math.pi * 2))
    draw.ellipse(safe_box((center[0]-r, center[1]-r, center[0]+r, center[1]+r)),
                 fill=BLUE+(220,), outline=CYAN+(255,), width=6)
    centered(draw, (center[0]-r, center[1]-18, center[0]+r, center[1]+18), "CORE", FONT_SMALL, WHITE)

    label = str(scene.get("on_screen_text", "")).strip()
    if label:
        centered(draw, (360, 510, 920, 550), label, FONT_CARD, fg)


def draw_domain_scene(image, scene, topic, progress, dark=False):
    """Domain-aware city/water/infrastructure illustration."""
    draw = ImageDraw.Draw(image, "RGBA")
    fg = WHITE if dark else NAVY
    accent = CYAN if "water" in scene_text(scene) else GREEN

    draw_panel(image, (65, 190, 1215, 565), dark, accent)

    # Simple city skyline.
    base_y = 470
    building_x = 110
    for i, h in enumerate([125, 185, 145, 230, 165, 200, 135, 175]):
        w = 95
        x = building_x + i * 125
        draw.rectangle((x, base_y-h, x+w, base_y), fill=(230,240,248,235) if not dark else (45,62,78,235))
        for r in range(3):
            for c in range(2):
                wx = x + 18 + c*34
                wy = base_y-h+18+r*38
                draw.rounded_rectangle((wx, wy, wx+15, wy+12), radius=3, fill=accent+(210,))

    # Water/network line and nodes.
    y = 515
    points = [(130, y), (360, 500), (600, 520), (845, 485), (1110, 515)]
    draw.line(points, fill=accent+(180,), width=6)
    for j, (x, yy) in enumerate(points):
        rr = 18 + int(6 * ease_out(clamp(progress*1.5-j*0.15)))
        draw.ellipse(safe_box((x-rr, yy-rr, x+rr, yy+rr)), fill=BLUE+(220,), outline=WHITE+(220,), width=3)

    tank_x, tank_y = 690, 300
    draw.rounded_rectangle((620, 215, 760, 390), radius=28,
                           fill=WHITE+(235,) if not dark else DARK_PANEL+(240,),
                           outline=accent+(240,), width=4)
    draw.rectangle((645, 270, 735, 360), fill=accent+(100,))
    draw.line((660, 300, 720, 300), fill=accent+(220,), width=6)

    label = str(scene.get("on_screen_text", "")).strip()
    if label:
        centered(draw, (240, 215, 1050, 255), label, FONT_CARD, fg)


def draw_style_overlay(image, scene, progress, dark=False):
    """Add scene-style-specific composition so outputs do not look like one fixed template."""
    draw = ImageDraw.Draw(image, "RGBA")
    style = str(scene.get("visual_style", "infographic")).strip().lower().replace(" ", "_")
    accent_name = str(scene.get("background_theme", "neutral")).lower()
    accents = {
        "water": CYAN, "environment": GREEN, "technology": PURPLE,
        "security": CYAN, "finance": ORANGE, "healthcare": CYAN,
        "infrastructure": ORANGE, "government": BLUE, "business": PURPLE,
        "neutral": BLUE,
    }
    accent = accents.get(accent_name, BLUE)

    if style == "editorial":
        # Clean editorial framing: oversized rule and offset blocks.
        y = 118 + int(12 * math.sin(progress * math.pi))
        draw.rectangle((70, y, 72, 610), fill=accent + (185,))
        draw.rectangle((95, 535, 520, 540), fill=accent + (95,))
        draw.ellipse((1090, 105, 1175, 190), outline=accent + (70,), width=4)
    elif style == "technical":
        # Fine technical drafting grid.
        alpha = 46 if not dark else 68
        for x in range(90, 1210, 90):
            draw.line((x, 150, x, 620), fill=accent + (alpha,), width=1)
        for y in range(165, 620, 70):
            draw.line((80, y, 1210, y), fill=accent + (alpha,), width=1)
    elif style == "diagrammatic":
        # Central guide ring and connector ticks.
        cx, cy = 965, 350
        for rr in (92, 135, 178):
            draw.ellipse((cx-rr, cy-rr, cx+rr, cy+rr), outline=accent + (48,), width=3)
    elif style == "data_story":
        # Small metric bars as a visual grammar, not a forced chart.
        for i, h in enumerate((40, 72, 55, 95, 68)):
            x = 910 + i * 48
            yy = 565 - h
            draw.rounded_rectangle((x, yy, x+26, 565), radius=6, fill=accent+(55,))
    elif style == "map_network":
        # Geographic-ish contour and node language.
        pts = [(820,210),(900,260),(1040,220),(1125,315),(1060,420),(900,460),(820,390)]
        draw.line(pts + [pts[0]], fill=accent+(65,), width=4, joint="curve")
        for x,y in pts[::2]:
            draw.ellipse((x-8,y-8,x+8,y+8), fill=accent+(130,))
    elif style == "executive":
        # Executive report treatment: top-right KPI chips.
        for i, label in enumerate(("01","02","03")):
            x = 900 + i*92
            rounded(draw, (x, 105, x+72, 140), 14,
                    (255,255,255,190) if not dark else (38,55,72,210),
                    accent+(95,), 1)
            centered(draw, (x,105,x+72,140), label, FONT_TINY, WHITE if dark else NAVY)
    else:  # infographic / cinematic_cards
        # Lightweight floating accents rather than another full panel.
        offset = int(18 * math.sin(progress * math.pi * 2))
        draw.ellipse((1090+offset, 510, 1160+offset, 580), fill=accent+(26,))
        draw.rectangle((78, 122, 240, 126), fill=accent+(90,))


# REPLACED VISUAL ROUTER
def draw_visual(
    image,
    scene,
    topic,
    progress,
    scene_no,
    total_scenes,
    dark
):
    if scene_no == 1:
        draw_intro(image, scene, topic, dark)
        return

    if scene_no == total_scenes:
        draw_conclusion(image, scene, topic, dark)
        return

    visual = choose_visual(scene, scene_no)

    if visual == "workflow":
        draw_workflow_scene(image, scene, progress, dark)
    elif visual == "timeline":
        draw_timeline_scene(image, scene, progress, dark)
    elif visual == "comparison":
        draw_comparison_scene(image, scene, progress, dark)
    elif visual == "dashboard":
        draw_dashboard_scene(image, scene, progress, dark)
    elif visual == "network":
        draw_network_scene(image, scene, progress, dark)
    elif visual == "domain":
        draw_domain_scene(image, scene, topic, progress, dark)
    elif visual == "documents":
        draw_documents_scene(image, scene, progress, dark)
    elif visual == "data":
        draw_data_scene(image, scene, progress, dark)
    elif visual == "security":
        draw_security_scene(image, scene, progress, dark)
    elif visual == "people":
        draw_people_scene(image, scene, progress, dark)
    elif visual == "building":
        draw_building_scene(image, scene, progress, dark)
    elif visual == "factory":
        draw_factory_scene(image, scene, progress, dark)
    elif visual == "technology":
        draw_technology_scene(image, scene, progress, dark)
    else:
        draw_concept_scene(image, scene, progress, dark)


# ============================================================
# SUBTITLES
# ============================================================

def create_subtitles(
    text,
    duration
):

    words = str(text).split()

    if not words:
        return []

    # Smaller chunks = easier to read.
    chunk_size = 8

    chunks = []

    for i in range(
        0,
        len(words),
        chunk_size
    ):

        chunks.append(
            " ".join(
                words[
                    i:i + chunk_size
                ]
            )
        )

    total_words = len(words)

    current = 0.0

    result = []

    for chunk in chunks:

        count = len(
            chunk.split()
        )

        part = (
            duration
            * count
            / total_words
        )

        result.append(
            (
                current,
                min(
                    duration,
                    current + part
                ),
                chunk
            )
        )

        current += part

    return result


def get_active_subtitle(
    subtitles,
    t
):

    for (
        start,
        end,
        text
    ) in subtitles:

        if start <= t < end:
            return text

    return ""


def draw_subtitle(
    image,
    text
):

    if not text:
        return

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    # Black CC bar
    draw.rectangle(
        (
            0,
            H - 82,
            W,
            H
        ),
        fill=(
            0,
            0,
            0,
            225
        )
    )

    lines = wrap_text(
        draw,
        text,
        FONT_SUBTITLE,
        W - 120,
        2
    )

    line_height = 31

    total_height = (
        len(lines)
        * line_height
    )

    y = (
        H - 68
        - total_height / 2
    )

    for line in lines:

        tw, th = text_size(
            draw,
            line,
            FONT_SUBTITLE
        )

        draw.text(
            (
                (W - tw) / 2,
                y
            ),
            line,
            font=FONT_SUBTITLE,
            fill=WHITE
        )

        y += line_height


# ============================================================
# CAMERA MOTION
# ============================================================

def camera_motion(
    image,
    t,
    duration,
    scene_no
):

    # COMPLETELY OFF.
    # Prevents screen shaking and drifting.

    return image


# ============================================================
# TRANSITION
# ============================================================

def transition(
    image,
    t,
    duration
):

    # COMPLETELY OFF.
    # Prevents white flashes.

    return image


# ============================================================
# RENDER ONE SCENE
# ============================================================

def render_scene(scene, topic, total_scenes, target_duration):
    scene_no = int(scene.get("scene_number", 1))
    narration = str(scene.get("narration", ""))

    audio_file = AUDIO_DIR / f"scene_{scene_no}.mp3"
    output_file = SCENES_DIR / f"scene_{scene_no}_final.mp4"

    if not audio_file.exists():
        raise FileNotFoundError(
            f"\nAudio missing:\n{audio_file}\n\nRun main.py first."
        )

    audio = AudioFileClip(str(audio_file))
    audio_duration = float(audio.duration)
    requested_duration = float(target_duration)

    # Audio is the source of truth. Never cut spoken narration.
    actual_duration = max(requested_duration, audio_duration)
    subtitles = create_subtitles(narration, actual_duration)

    # Give the renderer the document topic so all visual decisions can use it.
    scene = dict(scene)
    scene["topic"] = topic

    background_mode = str(scene.get("background_mode", "auto")).strip().lower()
    if background_mode == "dark":
        dark = True
    elif background_mode == "light":
        dark = False
    else:
        theme = scene_theme(scene, topic)
        dark_slots = {
            "security": {1, 4, 7, 10, 13},
            "technology": {2, 6, 10, 14},
            "finance": {3, 7, 11, 15},
            "healthcare": {2, 5, 8, 11},
            "infrastructure": {3, 6, 9, 12},
            "government": {4, 8, 12, 16},
            "environment": {2, 6, 10, 14},
            "water": {3, 7, 11, 15},
            "business": {4, 8, 12, 16},
        }
        dark = scene_no in dark_slots.get(theme, {7, 14, 21})

    visual = (
        "intro" if scene_no == 1 else
        "conclusion" if scene_no == total_scenes else
        choose_visual(scene, scene_no)
    )

    print()
    print("=" * 70)
    print(f"RENDERING SCENE {scene_no}/{total_scenes}")
    print("=" * 70)
    print("Visual:", visual)
    print("Visual style:", scene.get("visual_style", "infographic"))
    print("Background theme:", scene.get("background_theme", "neutral"))
    print("Background:", "DARK" if dark else "LIGHT")
    print("Graph:", "YES" if is_data_scene(scene) else "NO")
    print("Character:", "YES - INTRO ONLY" if scene_no == 1 else "NO")
    print("Requested duration:", f"{requested_duration:.2f} sec")
    print("Audio duration:", f"{audio_duration:.2f} sec")
    print("Final scene duration:", f"{actual_duration:.2f} sec")

    if audio_duration > requested_duration:
        print("NOTE: narration is longer than allocated duration; scene extended to preserve complete speech.")

    def frame_function(t):
        progress = clamp(t / max(actual_duration, 0.01))

        image = create_background(scene_no, dark, progress, scene)
        draw_topic_heading(image, topic, dark, scene_no)
        draw_scene_title(image, scene, dark)
        draw_style_overlay(image, scene, progress, dark)
        draw_visual(image, scene, topic, progress, scene_no, total_scenes, dark)

        # Very subtle highlight, no camera shake or white flash.
        light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(light, "RGBA")
        lx = int(-250 + (W + 500) * progress)
        ld.ellipse((lx - 220, 90, lx + 220, 520), fill=(255, 255, 255, 10))
        light = light.filter(ImageFilter.GaussianBlur(80))
        image.alpha_composite(light)

        image = camera_motion(image, t, actual_duration, scene_no)
        draw_subtitle(image, get_active_subtitle(subtitles, t))
        image = transition(image, t, actual_duration)

        return np.array(image.convert("RGB"))

    clip = VideoClip(frame_function=frame_function, duration=actual_duration)
    clip = clip.with_audio(audio)

    clip.write_videofile(
        str(output_file),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate="7500k",
        preset="medium",
        logger="bar"
    )

    try:
        audio.close()
    except Exception:
        pass

    try:
        clip.close()
    except Exception:
        pass

    print(f"Scene {scene_no} complete:")
    print(output_file)
    return output_file

def srt_time(seconds):

    milliseconds = int(
        round(seconds * 1000)
    )

    hours = (
        milliseconds // 3600000
    )

    milliseconds %= 3600000

    minutes = (
        milliseconds // 60000
    )

    milliseconds %= 60000

    seconds_value = (
        milliseconds // 1000
    )

    milliseconds %= 1000

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{seconds_value:02d},"
        f"{milliseconds:03d}"
    )


def vtt_time(seconds):

    milliseconds = int(
        round(seconds * 1000)
    )

    hours = (
        milliseconds // 3600000
    )

    milliseconds %= 3600000

    minutes = (
        milliseconds // 60000
    )

    milliseconds %= 60000

    seconds_value = (
        milliseconds // 1000
    )

    milliseconds %= 1000

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{seconds_value:02d}."
        f"{milliseconds:03d}"
    )


# ============================================================
# GLOBAL SUBTITLES
# ============================================================

def build_global_subtitles(
    scenes
):

    srt = []

    vtt = [
        "WEBVTT",
        ""
    ]

    global_time = 0.0
    index = 1

    for scene in scenes:

        narration = str(
            scene.get(
                "narration",
                ""
            )
        )

        # Use actual audio duration where possible.
        scene_no = int(
            scene.get(
                "scene_number",
                1
            )
        )

        audio_file = (
            AUDIO_DIR
            / f"scene_{scene_no}.mp3"
        )

        if audio_file.exists():

            try:

                temp_audio = AudioFileClip(
                    str(audio_file)
                )

                duration = max(
                    float(
                        scene.get(
                            "duration",
                            6
                        )
                    ),
                    float(
                        temp_audio.duration
                    )
                )

                temp_audio.close()

            except Exception:

                duration = float(
                    scene.get(
                        "duration",
                        6
                    )
                )

        else:

            duration = float(
                scene.get(
                    "duration",
                    6
                )
            )

        local_subtitles = create_subtitles(
            narration,
            duration
        )

        for (
            start,
            end,
            text
        ) in local_subtitles:

            start += global_time
            end += global_time

            srt.extend(
                [
                    str(index),
                    (
                        f"{srt_time(start)}"
                        f" --> "
                        f"{srt_time(end)}"
                    ),
                    text,
                    ""
                ]
            )

            vtt.extend(
                [
                    (
                        f"{vtt_time(start)}"
                        f" --> "
                        f"{vtt_time(end)}"
                    ),
                    text,
                    ""
                ]
            )

            index += 1

        global_time += duration

    with open(
        FINAL_SRT,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(srt)
        )

    with open(
        FINAL_VTT,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(vtt)
        )


# ============================================================
# COMBINE SCENES
# ============================================================

def combine_scenes(
    scene_files
):

    if not scene_files:

        raise ValueError(
            "No rendered scenes."
        )

    concat_file = (
        SCENES_DIR
        / "concat_list.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as f:

        for file in scene_files:

            absolute = (
                Path(file)
                .resolve()
                .as_posix()
            )

            f.write(
                f"file '{absolute}'\n"
            )

    temp_file = SCENES_DIR / "combined_temp.mp4"

    # --------------------------------------------------------
    # First attempt: stream copy
    # --------------------------------------------------------

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        str(temp_file)
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    # --------------------------------------------------------
    # Fallback re-encode
    # --------------------------------------------------------

    if result.returncode != 0:

        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-pix_fmt",
            "yuv420p",
            str(temp_file)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            print(result.stderr)

            raise RuntimeError(
                "Could not combine scene videos."
            )

    # --------------------------------------------------------
    # Final encode
    # --------------------------------------------------------

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(temp_file),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(FINAL_VIDEO)
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print(result.stderr)

        raise RuntimeError(
            "Final video encoding failed."
        )

    try:
        temp_file.unlink()
    except Exception:
        pass

    try:
        concat_file.unlink()
    except Exception:
        pass


# ============================================================
# DURATION SELECTION
# ============================================================

def get_target_duration():
    """Always ask the user to choose the final video duration."""

    print()
    print("=" * 75)
    print("SELECT VIDEO DURATION")
    print("=" * 75)
    print()
    print("1 = 1 minute")
    print("2 = 2 minutes")
    print("3 = 3 minutes")
    print()

    while True:
        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            return 60.0

        if choice == "2":
            return 120.0

        if choice == "3":
            return 180.0

        print("Please enter only 1, 2 or 3.")

def adjust_scene_durations(
    scenes,
    target_duration
):

    original_durations = []

    for scene in scenes:

        try:

            duration = float(
                scene.get(
                    "duration",
                    6
                )
            )

        except Exception:

            duration = 6.0

        original_durations.append(
            max(
                2.5,
                duration
            )
        )

    original_total = sum(
        original_durations
    )

    if original_total <= 0:

        original_total = (
            len(scenes) * 6
        )

    scale = (
        target_duration
        / original_total
    )

    adjusted = [
        d * scale
        for d in original_durations
    ]

    # Do not allow extremely short scenes.
    adjusted = [
        max(
            2.5,
            d
        )
        for d in adjusted
    ]

    adjusted_total = sum(
        adjusted
    )

    if adjusted_total > 0:

        final_scale = (
            target_duration
            / adjusted_total
        )

        adjusted = [
            d * final_scale
            for d in adjusted
        ]

    for scene, duration in zip(
        scenes,
        adjusted
    ):

        scene["duration"] = float(
            duration
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 75)
    print("       SIH FINAL CORPORATE VIDEO")
    print("=" * 75)
    print()

    # --------------------------------------------------------
    # Check scene data
    # --------------------------------------------------------

    if not SCENE_DATA_FILE.exists():

        raise FileNotFoundError(
            f"\nscene_data.json not found:\n"
            f"{SCENE_DATA_FILE}"
        )

    with open(
        SCENE_DATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    scenes = data.get(
        "scenes",
        []
    )

    if not scenes:

        raise ValueError(
            "No scenes found in scene_data.json."
        )

    topic = (
        data.get("title")
        or data.get("topic")
        or data.get("document_title")
        or scenes[0].get(
            "scene_title",
            "AI Content Transformation"
        )
    )

    topic = str(topic).strip()

    # --------------------------------------------------------
    # Use run-specific output/audio paths saved by main.py
    # --------------------------------------------------------

    global AUDIO_DIR, SCENES_DIR, FINAL_VIDEO, FINAL_SRT, FINAL_VTT

    saved_audio = data.get("audio_dir")
    saved_scenes = data.get("scenes_dir")
    saved_video = data.get("final_video")
    saved_srt = data.get("final_srt")
    saved_vtt = data.get("final_vtt")

    if saved_audio:
        AUDIO_DIR = Path(saved_audio)
    if saved_scenes:
        SCENES_DIR = Path(saved_scenes)
    if saved_video:
        FINAL_VIDEO = Path(saved_video)
    if saved_srt:
        FINAL_SRT = Path(saved_srt)
    if saved_vtt:
        FINAL_VTT = Path(saved_vtt)

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    SCENES_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_VIDEO.parent.mkdir(parents=True, exist_ok=True)

    print("Narrator voice:", data.get("voice", "configured by main.py"))
    print("Output folder:", FINAL_VIDEO.parent)

    # --------------------------------------------------------
    # Duration
    # --------------------------------------------------------

    target_duration = get_target_duration()

    # --------------------------------------------------------
    # Scale requested durations
    # --------------------------------------------------------

    adjust_scene_durations(
        scenes,
        target_duration
    )

    print()
    print("=" * 75)
    print(
        "SELECTED:",
        f"{int(target_duration / 60)} minute(s)"
    )
    print()
    print("Camera movement: OFF")
    print("White transition: OFF")
    print("Background lines: OFF")
    print("Character: INTRO ONLY")
    print("Long text: AUTO FIT")
    print("Narration cutting: OFF")
    print("Graphs: DATA SCENES ONLY")
    print("=" * 75)

    print()

    # --------------------------------------------------------
    # Render
    # --------------------------------------------------------

    rendered_files = []

    for scene in scenes:

        rendered_files.append(
            render_scene(
                scene,
                topic,
                len(scenes),
                scene["duration"]
            )
        )

    # --------------------------------------------------------
    # Subtitles
    # --------------------------------------------------------

    build_global_subtitles(
        scenes
    )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    combine_scenes(
        rendered_files
    )

    # --------------------------------------------------------
    # Done
    # --------------------------------------------------------

    print()
    print("=" * 75)
    print("FINAL VIDEO READY")
    print("=" * 75)
    print()

    print(
        "VIDEO:",
        FINAL_VIDEO
    )

    print(
        "SRT:",
        FINAL_SRT
    )

    print(
        "VTT:",
        FINAL_VTT
    )

    print()
    print("Done.")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
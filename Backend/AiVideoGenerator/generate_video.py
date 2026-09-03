import os
import json
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from moviepy import (
    VideoClip,
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
)

# ============================================================
# SETTINGS
# ============================================================

W = 1280
H = 720
FPS = 24

BASE_DIR = Path(__file__).resolve().parent

CHARACTER_FILE = BASE_DIR / "character" / "main_character.png"
CLEAN_CHARACTER_FILE = BASE_DIR / "character" / "main_character_clean.png"

SCENE_DATA_FILE = BASE_DIR / "scene_data.json"

AUDIO_DIR = BASE_DIR / "audio"
SCENES_DIR = BASE_DIR / "scenes"

FINAL_VIDEO = BASE_DIR / "final_storytelling_video_v2.mp4"

AUDIO_DIR.mkdir(exist_ok=True)
SCENES_DIR.mkdir(exist_ok=True)


# ============================================================
# BASIC HELPERS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def ease_in_out(t):
    """
    Smooth cinematic movement.
    """
    t = clamp(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ============================================================
# LOAD SCENE DATA
# ============================================================

def load_scene_data():

    if not SCENE_DATA_FILE.exists():
        raise FileNotFoundError(
            f"scene_data.json not found:\n{SCENE_DATA_FILE}"
        )

    with open(SCENE_DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenes = data.get("scenes", [])

    if not scenes:
        raise ValueError("No scenes found in scene_data.json")

    print(f"Loaded {len(scenes)} scenes.")

    return scenes


# ============================================================
# CHARACTER CLEANING
# ============================================================

def create_clean_character():
    """
    IMPORTANT:
    The supplied character image is a CHARACTER SHEET.
    It contains several poses.

    We only keep the FIRST / LARGE CHARACTER on the left.

    The previous version accidentally allowed neighbouring
    poses to enter the video.

    This function:
      1. Loads the sheet.
      2. Crops only the left-most character area.
      3. Uses rembg if available.
      4. Saves a transparent PNG.
    """

    if not CHARACTER_FILE.exists():
        raise FileNotFoundError(
            f"Character image not found:\n{CHARACTER_FILE}"
        )

    print("\nPreparing character...")

    source = Image.open(CHARACTER_FILE).convert("RGBA")

    sw, sh = source.size

    print(f"Character sheet size: {sw} x {sh}")

    # --------------------------------------------------------
    # IMPORTANT CROP
    #
    # First large character occupies roughly the left 29%.
    #
    # We intentionally DO NOT use 100% of the sheet.
    # --------------------------------------------------------

    crop_right = int(sw * 0.29)

    # Small safety limit
    crop_right = min(crop_right, 500)

    crop_right = max(crop_right, 350)

    cropped = source.crop(
        (0, 0, crop_right, sh)
    )

    # --------------------------------------------------------
    # Background removal
    # --------------------------------------------------------

    try:

        from rembg import remove

        print("Removing character background...")

        cleaned = remove(
            cropped,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=8,
        )

        cleaned = cleaned.convert("RGBA")

    except Exception as e:

        print("rembg could not be used.")
        print("Using safe crop fallback.")
        print("Reason:", e)

        cleaned = cropped.convert("RGBA")

        # Make pixels near the extreme right side transparent.
        # This prevents neighbouring poses from appearing.
        alpha = cleaned.getchannel("A")

        alpha_np = np.array(alpha)

        cut_x = int(cleaned.width * 0.90)

        alpha_np[:, cut_x:] = 0

        alpha = Image.fromarray(alpha_np.astype(np.uint8), "L")

        cleaned.putalpha(alpha)

    # --------------------------------------------------------
    # Additional safety mask
    #
    # Absolutely remove the far-right edge of the sheet.
    # --------------------------------------------------------

    alpha = cleaned.getchannel("A")
    alpha_np = np.array(alpha)

    safe_edge = int(cleaned.width * 0.92)

    alpha_np[:, safe_edge:] = 0

    # Slightly soften edges
    alpha_img = Image.fromarray(alpha_np.astype(np.uint8), "L")
    alpha_img = alpha_img.filter(
        ImageFilter.GaussianBlur(0.7)
    )

    cleaned.putalpha(alpha_img)

    # --------------------------------------------------------
    # Remove completely transparent borders
    # --------------------------------------------------------

    bbox = cleaned.getbbox()

    if bbox:

        cleaned = cleaned.crop(bbox)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    cleaned.save(
        CLEAN_CHARACTER_FILE,
        "PNG"
    )

    print(
        f"Clean character created: "
        f"{cleaned.width} x {cleaned.height}"
    )

    print(
        f"Saved:\n{CLEAN_CHARACTER_FILE}"
    )

    return cleaned


# ============================================================
# LOAD CLEAN CHARACTER
# ============================================================

def get_character():

    # Always rebuild so the old bad crop cannot be reused.
    return create_clean_character()


# ============================================================
# CHARACTER FRAME
# ============================================================

def character_frame(character, t, duration, scene_number):

    """
    Creates a moving character frame.

    The character:
      - moves slightly
      - zooms slowly
      - has cinematic camera motion
    """

    progress = t / max(duration, 0.001)

    # Smooth motion
    p = ease_in_out(progress)

    # Different movement for different scenes
    if scene_number == 1:

        # Start slightly left, move toward center
        x = 55 + int(55 * p)

        # Slight zoom
        scale = 0.82 + 0.035 * p

    elif scene_number == 2:

        # Move slightly right
        x = 40 + int(80 * p)

        scale = 0.78 + 0.05 * p

    elif scene_number == 3:

        # More subtle movement
        x = 70 + int(30 * math.sin(p * math.pi))

        scale = 0.74 + 0.035 * p

    elif scene_number == 4:

        # Character moves from right toward center
        x = 180 - int(70 * p)

        scale = 0.76 + 0.04 * p

    else:

        # Final scene
        x = 70

        scale = 0.80 + 0.05 * p

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    cw, ch = character.size

    new_w = int(cw * scale)
    new_h = int(ch * scale)

    char = character.resize(
        (new_w, new_h),
        Image.Resampling.LANCZOS
    )

    # --------------------------------------------------------
    # Vertical placement
    # --------------------------------------------------------

    y = H - new_h + 15

    return char, x, y


# ============================================================
# CORPORATE BACKGROUND
# ============================================================

def create_background(t, duration, scene_number):

    img = Image.new(
        "RGB",
        (W, H),
        (12, 24, 42)
    )

    draw = ImageDraw.Draw(img)

    progress = t / max(duration, 0.001)

    # --------------------------------------------------------
    # Soft gradient-like horizontal bands
    # --------------------------------------------------------

    for y in range(H):

        ratio = y / H

        r = int(12 + ratio * 15)
        g = int(24 + ratio * 30)
        b = int(42 + ratio * 45)

        draw.line(
            [(0, y), (W, y)],
            fill=(r, g, b)
        )

    # --------------------------------------------------------
    # Corporate glass panels
    # --------------------------------------------------------

    panel_y = 90

    for i in range(4):

        x1 = 420 + i * 220

        draw.rounded_rectangle(
            (
                x1,
                panel_y,
                x1 + 175,
                410
            ),
            radius=16,
            outline=(70, 105, 135),
            width=2
        )

    # --------------------------------------------------------
    # Building / office shapes
    # --------------------------------------------------------

    base_y = 410

    for i in range(16):

        x = i * 85

        height = 60 + ((i * 37) % 130)

        draw.rectangle(
            (
                x,
                base_y - height,
                x + 55,
                base_y
            ),
            fill=(38, 68, 92)
        )

    # --------------------------------------------------------
    # AI network
    # --------------------------------------------------------

    center_x = 920
    center_y = 300

    radius = 70 + int(
        8 * math.sin(progress * math.pi * 2)
    )

    draw.ellipse(
        (
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius
        ),
        outline=(70, 170, 230),
        width=3
    )

    for angle in range(0, 360, 60):

        rad = math.radians(angle)

        px = center_x + int(
            math.cos(rad) * 120
        )

        py = center_y + int(
            math.sin(rad) * 120
        )

        draw.line(
            (
                center_x,
                center_y,
                px,
                py
            ),
            fill=(55, 120, 165),
            width=2
        )

        draw.ellipse(
            (
                px - 7,
                py - 7,
                px + 7,
                py + 7
            ),
            fill=(75, 165, 220)
        )

    # AI text
    draw.text(
        (center_x - 20, center_y - 15),
        "AI",
        fill=(100, 190, 240)
    )

    # --------------------------------------------------------
    # Floating particles
    # --------------------------------------------------------

    for i in range(35):

        px = (i * 97 + int(t * 18)) % W
        py = (i * 53 + int(t * 10)) % H

        radius = 2 + (i % 3)

        draw.ellipse(
            (
                px - radius,
                py - radius,
                px + radius,
                py + radius
            ),
            fill=(80, 125, 155)
        )

    # --------------------------------------------------------
    # Floor
    # --------------------------------------------------------

    draw.rectangle(
        (0, 525, W, H),
        fill=(20, 32, 48)
    )

    # Floor perspective lines

    for x in range(-500, 1800, 120):

        draw.line(
            (
                W // 2,
                525,
                x,
                H
            ),
            fill=(35, 55, 72),
            width=1
        )

    # Horizontal floor line

    for y in range(560, H, 45):

        draw.line(
            (
                0,
                y,
                W,
                y
            ),
            fill=(30, 48, 65),
            width=1
        )

    return img


# ============================================================
# TEXT RENDERING
# ============================================================

def draw_text_safe(
    draw,
    text,
    xy,
    font_size=32,
    fill=(255, 255, 255),
    anchor=None
):

    try:

        from PIL import ImageFont

        font = ImageFont.truetype(
            "arial.ttf",
            font_size
        )

    except:

        font = ImageFont.load_default()

    draw.text(
        xy,
        text,
        font=font,
        fill=fill,
        anchor=anchor
    )


# ============================================================
# SCENE RENDERING
# ============================================================

def render_scene(scene, character):

    scene_number = int(
        scene.get("scene_number", 1)
    )

    duration = float(
        scene.get("duration", 8)
    )

    narration = scene.get(
        "narration",
        ""
    )

    screen_text = scene.get(
        "on_screen_text",
        ""
    )

    if isinstance(screen_text, list):

        screen_text = "\n".join(
            str(x) for x in screen_text
        )

    output_file = (
        SCENES_DIR /
        f"scene_{scene_number}_v2.mp4"
    )

    print(
        f"\nRendering Scene {scene_number}..."
    )

    def make_frame(t):

        # ----------------------------------------------------
        # Background
        # ----------------------------------------------------

        bg = create_background(
            t,
            duration,
            scene_number
        )

        # ----------------------------------------------------
        # Camera movement
        # ----------------------------------------------------

        progress = t / max(duration, 0.001)

        zoom = 1.0 + 0.025 * progress

        bg_w = int(W * zoom)
        bg_h = int(H * zoom)

        bg_zoom = bg.resize(
            (bg_w, bg_h),
            Image.Resampling.BICUBIC
        )

        crop_x = int(
            (bg_w - W) * 0.5
        )

        crop_y = int(
            (bg_h - H) * 0.5
        )

        bg = bg_zoom.crop(
            (
                crop_x,
                crop_y,
                crop_x + W,
                crop_y + H
            )
        )

        # ----------------------------------------------------
        # Character
        # ----------------------------------------------------

        char, char_x, char_y = character_frame(
            character,
            t,
            duration,
            scene_number
        )

        bg.paste(
            char,
            (char_x, char_y),
            char
        )

        draw = ImageDraw.Draw(bg)

        # ----------------------------------------------------
        # Top scene indicator
        # ----------------------------------------------------

        draw.rounded_rectangle(
            (
                45,
                35,
                105,
                78
            ),
            radius=12,
            fill=(20, 50, 75)
        )

        draw_text_safe(
            draw,
            f"{scene_number:02d}",
            (75, 56),
            font_size=25,
            fill=(150, 215, 245),
            anchor="mm"
        )

        # ----------------------------------------------------
        # Scene title
        # ----------------------------------------------------

        title = scene.get(
            "scene_title",
            ""
        )

        draw_text_safe(
            draw,
            title.upper(),
            (130, 57),
            font_size=27,
            fill=(240, 245, 250)
        )

        # ----------------------------------------------------
        # Highlight text
        # ----------------------------------------------------

        if screen_text:

            lines = str(
                screen_text
            ).split("\n")

            box_x1 = 620
            box_y1 = 500
            box_x2 = 1210
            box_y2 = 650

            draw.rounded_rectangle(
                (
                    box_x1,
                    box_y1,
                    box_x2,
                    box_y2
                ),
                radius=22,
                fill=(10, 25, 42),
                outline=(80, 135, 170),
                width=2
            )

            y = box_y1 + 30

            for line in lines:

                line = line.strip()

                if not line:
                    continue

                draw_text_safe(
                    draw,
                    line,
                    (box_x1 + 28, y),
                    font_size=25,
                    fill=(235, 245, 250)
                )

                y += 42

        # ----------------------------------------------------
        # Cinematic bars
        # ----------------------------------------------------

        bar_h = 18

        draw.rectangle(
            (0, 0, W, bar_h),
            fill=(5, 10, 18)
        )

        draw.rectangle(
            (0, H - bar_h, W, H),
            fill=(5, 10, 18)
        )

        # ----------------------------------------------------
        # Subtle vignette
        # ----------------------------------------------------

        vignette = Image.new(
            "RGBA",
            (W, H),
            (0, 0, 0, 0)
        )

        vd = ImageDraw.Draw(vignette)

        vd.rectangle(
            (0, 0, W, H),
            outline=(0, 0, 0, 90),
            width=35
        )

        bg = Image.alpha_composite(
            bg.convert("RGBA"),
            vignette
        )

        return np.array(
            bg.convert("RGB")
        )

    clip = VideoClip(
        frame_function=make_frame,
        duration=duration
    )

    # --------------------------------------------------------
    # Audio
    # --------------------------------------------------------

    audio_file = (
        AUDIO_DIR /
        f"scene_{scene_number}.mp3"
    )

    if not audio_file.exists():

        print(
            f"Audio missing for Scene {scene_number}"
        )

        print(
            f"Expected:\n{audio_file}"
        )

        raise FileNotFoundError(
            audio_file
        )

    audio = AudioFileClip(
        str(audio_file)
    )

    # Never let audio exceed scene duration
    audio_duration = min(
        audio.duration,
        duration
    )

    audio = audio.subclipped(
        0,
        audio_duration
    )

    clip = clip.with_audio(audio)

    # --------------------------------------------------------
    # Write scene
    # --------------------------------------------------------

    clip.write_videofile(
        str(output_file),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="5000k",
        logger="bar"
    )

    clip.close()
    audio.close()

    print(
        f"Scene {scene_number} completed:"
        f" {output_file.name}"
    )

    return output_file


# ============================================================
# CONCATENATE SCENES
# ============================================================

def concatenate_scenes(scene_files):

    print("\nCombining scenes...")

    # Use ffmpeg concat demuxer.
    concat_file = BASE_DIR / "concat_v2.txt"

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as f:

        for scene_file in scene_files:

            # FFmpeg needs forward slashes
            path = str(
                scene_file.resolve()
            ).replace("\\", "/")

            f.write(
                f"file '{path}'\n"
            )

    command = [
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
        str(FINAL_VIDEO)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print(result.stderr)

        raise RuntimeError(
            "FFmpeg could not combine scenes."
        )

    print(
        "\n======================================"
    )

    print(
        "FINAL VIDEO CREATED SUCCESSFULLY!"
    )

    print(
        f"File:\n{FINAL_VIDEO}"
    )

    print(
        "======================================"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n======================================"
    )

    print(
        "AI STORYTELLING VIDEO GENERATOR V2"
    )

    print(
        "======================================"
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "Old final video will NOT be overwritten."
    )

    print(
        f"New output: {FINAL_VIDEO.name}"
    )

    # --------------------------------------------------------
    # Load scenes
    # --------------------------------------------------------

    scenes = load_scene_data()

    # --------------------------------------------------------
    # Prepare clean character
    # --------------------------------------------------------

    character = get_character()

    # --------------------------------------------------------
    # Render scenes
    # --------------------------------------------------------

    scene_files = []

    for scene in scenes:

        output = render_scene(
            scene,
            character
        )

        scene_files.append(
            output
        )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    concatenate_scenes(
        scene_files
    )


if __name__ == "__main__":
    main()
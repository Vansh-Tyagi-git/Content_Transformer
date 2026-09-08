import json
import os
import re
import sys
import asyncio
from datetime import datetime
from pathlib import Path

import pymupdf
from google import genai
import edge_tts


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
AUDIO_DIR = BASE_DIR / "audio"
IMAGE_DIR = BASE_DIR / "images"

SCENE_DATA_FILE = BASE_DIR / "scene_data.json"
RUNS_DIR = BASE_DIR / "outputs"
VOICE_STATE_FILE = BASE_DIR / "voice_rotation.json"

# Professional Edge-TTS voices used for consecutive video runs.
# The generator rotates to the next voice for every new PDF/video run.
# This keeps consecutive videos from using the same narrator repeatedly.
VOICE_POOL = [
    "en-US-AriaNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-DavisNeural",
    "en-US-AvaNeural",
    "en-US-AndrewNeural",
    "en-US-EmmaNeural",
    "en-US-BrianNeural",
    "en-US-JasonNeural",
    "en-GB-SoniaNeural",
    "en-IN-NeerjaNeural",
    "en-IN-PrabhatNeural",
]

INPUT_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)
IMAGE_DIR.mkdir(exist_ok=True)
RUNS_DIR.mkdir(exist_ok=True)


# ============================================================
# GEMINI
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY environment variable is not set."
    )

client = genai.Client(api_key=API_KEY)


# ============================================================
# PDF
# ============================================================

def find_pdf():

    pdfs = list(INPUT_DIR.glob("*.pdf"))

    if not pdfs:
        raise FileNotFoundError(
            f"No PDF found in:\n{INPUT_DIR}"
        )

    if len(pdfs) > 1:
        print()
        print("Multiple PDFs found:")
        for i, pdf in enumerate(pdfs, 1):
            print(f"{i}. {pdf.name}")

        choice = input(
            "Select PDF number: "
        ).strip()

        try:
            return pdfs[int(choice) - 1]
        except Exception:
            raise ValueError(
                "Invalid PDF selection."
            )

    return pdfs[0]


def read_pdf(pdf_path):

    print()
    print("=" * 70)
    print("READING PDF")
    print("=" * 70)

    doc = pymupdf.open(pdf_path)

    pages = []

    for page in doc:
        text = page.get_text("text")

        if text:
            pages.append(text)

    doc.close()

    source_text = "\n\n".join(pages).strip()

    if not source_text:
        raise ValueError(
            "Could not extract text from PDF."
        )

    print(
        f"Extracted approximately "
        f"{len(source_text.split())} words."
    )

    return source_text


# ============================================================
# DURATION
# ============================================================

def get_target_duration():

    print()
    print("=" * 70)
    print("SELECT VIDEO DURATION")
    print("=" * 70)
    print()
    print("1 = 1 minute")
    print("2 = 2 minutes")
    print("3 = 3 minutes")
    print()

    while True:

        choice = input(
            "Enter choice (1/2/3): "
        ).strip()

        if choice == "1":
            return 60

        if choice == "2":
            return 120

        if choice == "3":
            return 180

        print(
            "Please enter only 1, 2 or 3."
        )


# ============================================================
# STORYBOARD
# ============================================================

def create_storyboard(
    source_text,
    target_seconds
):
    minutes = target_seconds / 60

    if target_seconds == 60:
        scene_instruction = """
Create 8 to 10 scenes.
Keep every scene short and focused.
"""
    elif target_seconds == 120:
        scene_instruction = """
Create 15 to 18 scenes.
Do not compress the PDF into only 10-12 scenes.
Break the source into many small storytelling moments.
Each scene should communicate ONE main idea.
"""
    else:
        scene_instruction = """
Create 21 to 24 scenes.
Break the source into many short storytelling moments.
Each scene should communicate ONE main idea.
Avoid combining several major concepts into one scene.
"""

    prompt = f"""
You are the creative director of a premium animated corporate explainer video system.

Convert the PDF into a professional storytelling video.

TARGET LENGTH:
{target_seconds} seconds ({minutes:.1f} minutes)

{scene_instruction}

============================================================
CORE STYLE
============================================================

This is NOT a static PowerPoint slideshow.

The result should feel like a premium animated corporate explainer/reel.

Use polished 2D/2.5D/3D-inspired corporate motion language:
- animated cards
- diagrams
- timelines
- process flows
- comparison layouts
- dashboards
- maps/network diagrams
- document visuals
- people/stakeholders
- technology/AI visuals
- domain-specific visualizations
- restrained motion
- clean typography
- professional composition

The Python renderer creates the actual visuals from your plan.
Do not ask for photorealistic images.

============================================================
CONTENT-DRIVEN VISUAL DESIGN
============================================================

Do NOT use one fixed visual formula for every PDF.

First understand the actual document domain and content.

For EACH scene, choose the visual that communicates that scene best.
Do not force a chart just because numbers appear.

IMPORTANT:
Numbers alone do NOT justify a chart.

Use show_chart=true ONLY when the source contains meaningful quantitative information that benefits from visual comparison/trend representation.

Examples:
- "28% to 20%" -> comparison/progress visual, optionally chart if useful.
- "12-month implementation" -> timeline, NOT a generic graph.
- "31% increase at 2:15 AM" -> alert/KPI/dashboard visual, NOT automatically a graph.
- multiple yearly values -> chart may be appropriate.

If no meaningful quantitative story exists, show_chart=false.

============================================================
VISUAL TYPES
============================================================

Choose the BEST type for each scene from:

"intro"
"process"
"workflow"
"timeline"
"comparison"
"chart"
"dashboard"
"network"
"security"
"healthcare"
"finance"
"real_estate"
"manufacturing"
"education"
"documents"
"people"
"technology"
"domain"
"concept"
"conclusion"

Avoid repeating the same visual type in consecutive scenes unless the content genuinely requires it.

============================================================
VISUAL STYLE
============================================================

For each scene choose one visual_style:

"minimal"
"infographic"
"editorial"
"technical"
"cinematic_cards"
"diagrammatic"
"data_story"
"map_network"
"executive"

The visual_style must match the scene content.

============================================================
LAYOUT
============================================================

Choose one:
"left_visual_right_text"
"right_visual_left_text"
"full_visual"
"center_diagram"
"split_comparison"
"timeline"
"dashboard"
"grid_cards"

Do not repeat the same layout unnecessarily.

============================================================
BACKGROUND
============================================================

Choose a professional background_theme for each scene based on the PDF domain:

"water"
"environment"
"technology"
"security"
"finance"
"healthcare"
"infrastructure"
"government"
"business"
"neutral"

Backgrounds should vary subtly between scenes while remaining visually coherent.

Allowed professional palette families:
white, light blue, cyan, lavender, mint, soft cream, soft yellow,
subtle coral, navy, deep blue, teal, restrained green.

Do not use childish or flashy colours.

Also choose:
"background_mode": "light" or "dark"

Use dark only for emphasis, not every other scene.

============================================================
VISUAL ELEMENTS
============================================================

Every scene must contain 3-6 concrete visual elements relevant to the scene.

Examples:
document, sensor, water tank, city map, AI node, dashboard,
warning badge, timeline, people, building, server, secure shield,
chart, KPI card, checklist, location marker, network node.

Do NOT use vague phrases such as "modern technology" or "beautiful environment".

============================================================
CHARACTER
============================================================

Scene 1:
character=true

Middle scenes:
character=false

Final scene:
character=false

Do not introduce random characters.

============================================================
ON-SCREEN TEXT
============================================================

Maximum 4 words.
Never put paragraphs on screen.

============================================================
NARRATION
============================================================

Natural professional spoken English.

Narration must be based ONLY on the PDF.
Each scene should normally contain approximately 10-22 spoken words.
Each scene should explain ONE idea.
Avoid repetition.
Do not invent facts.

============================================================
OUTPUT JSON
============================================================

Return ONLY valid JSON.

{{
  "title": "short title",
  "summary": "one sentence summary",
  "scenes": [
    {{
      "scene_number": 1,
      "scene_title": "short title",
      "duration": 6,
      "narration": "spoken narration",
      "visual_concept": "specific visual event grounded in the PDF",
      "visual_type": "intro",
      "visual_style": "cinematic_cards",
      "visual_elements": ["presenter", "topic card", "key concept"],
      "layout": "left_visual_right_text",
      "background_theme": "neutral",
      "background_mode": "light",
      "show_chart": false,
      "chart_type": "",
      "on_screen_text": "short phrase",
      "character": true
    }}
  ]
}}

============================================================
FACTUAL RULE
============================================================

The PDF is the only factual source.

Never invent statistics, percentages, names, dates, claims,
examples, numbers, organisations, or technical facts.

============================================================
SOURCE PDF
============================================================

{source_text}
"""

    print()
    print("=" * 70)
    print("GEMINI STORY DIRECTOR")
    print("=" * 70)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    text = response.text.strip()
    return extract_json(text)


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text):

    text = text.strip()

    text = re.sub(
        r"^```json",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```",
        "",
        text
    )

    text = re.sub(
        r"```$",
        "",
        text
    )

    text = text.strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "Gemini did not return valid JSON."
        )

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)

    except json.JSONDecodeError as e:

        print()
        print("Gemini JSON error:")
        print(e)

        raise ValueError(
            "Could not parse Gemini storyboard JSON."
        )


# ============================================================
# VALIDATION
# ============================================================

def validate_storyboard(
    data,
    target_seconds
):
    if not isinstance(data, dict):
        raise ValueError("Invalid storyboard.")

    scenes = data.get("scenes", [])
    if not scenes:
        raise ValueError("No scenes returned by Gemini.")

    allowed_visual_types = {
        "intro", "process", "workflow", "timeline", "comparison",
        "chart", "dashboard", "network", "security", "healthcare",
        "finance", "real_estate", "manufacturing", "education",
        "documents", "people", "technology", "domain", "concept",
        "conclusion"
    }

    allowed_styles = {
        "minimal", "infographic", "editorial", "technical",
        "cinematic_cards", "diagrammatic", "data_story",
        "map_network", "executive"
    }

    allowed_layouts = {
        "left_visual_right_text", "right_visual_left_text",
        "full_visual", "center_diagram", "split_comparison",
        "timeline", "dashboard", "grid_cards"
    }

    allowed_themes = {
        "water", "environment", "technology", "security", "finance",
        "healthcare", "infrastructure", "government", "business", "neutral"
    }

    required = [
        "scene_number", "scene_title", "duration", "narration",
        "visual_concept", "visual_type", "visual_elements", "layout",
        "on_screen_text", "character"
    ]

    for index, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            scene = {}
            scenes[index - 1] = scene

        for field in required:
            if field not in scene:
                scene[field] = ""

        scene["scene_number"] = index

        try:
            duration = float(scene.get("duration", 6))
        except Exception:
            duration = 6.0
        scene["duration"] = max(3.0, min(12.0, duration))

        scene["scene_title"] = str(scene.get("scene_title", "")).strip()
        scene["narration"] = str(scene.get("narration", "")).strip()
        scene["visual_concept"] = str(scene.get("visual_concept", "")).strip()
        scene["visual_type"] = (
            str(scene.get("visual_type", "concept"))
            .strip().lower().replace("-", "_").replace(" ", "_")
        )
        if scene["visual_type"] not in allowed_visual_types:
            scene["visual_type"] = "concept"

        if not isinstance(scene.get("visual_elements"), list):
            scene["visual_elements"] = []
        scene["visual_elements"] = [
            str(x).strip() for x in scene["visual_elements"][:6] if str(x).strip()
        ]

        scene["layout"] = (
            str(scene.get("layout", "full_visual")).strip()
            .lower().replace("-", "_").replace(" ", "_")
        )
        if scene["layout"] not in allowed_layouts:
            scene["layout"] = "full_visual"

        scene["visual_style"] = (
            str(scene.get("visual_style", "infographic")).strip().lower().replace(" ", "_")
        )
        if scene["visual_style"] not in allowed_styles:
            scene["visual_style"] = "infographic"

        scene["background_theme"] = (
            str(scene.get("background_theme", "neutral")).strip().lower().replace(" ", "_")
        )
        if scene["background_theme"] not in allowed_themes:
            scene["background_theme"] = "neutral"

        scene["background_mode"] = (
            str(scene.get("background_mode", "light")).strip().lower()
        )
        if scene["background_mode"] not in {"light", "dark"}:
            scene["background_mode"] = "light"

        value = scene.get("show_chart", False)
        if isinstance(value, str):
            scene["show_chart"] = value.strip().lower() in {"true", "yes", "1"}
        else:
            scene["show_chart"] = bool(value)

        scene["chart_type"] = str(scene.get("chart_type", "")).strip().lower()
        scene["on_screen_text"] = str(scene.get("on_screen_text", "")).strip()
        scene["character"] = bool(scene.get("character", False))

        # Guardrail: numbers alone do not create a chart.
        if scene["visual_type"] not in {"chart", "dashboard"}:
            scene["show_chart"] = False
            scene["chart_type"] = ""

        if scene["show_chart"] and scene["visual_type"] not in {"chart", "dashboard"}:
            scene["show_chart"] = False
            scene["chart_type"] = ""

    # Character rule
    for scene in scenes:
        scene["character"] = False
    scenes[0]["character"] = True

    # Keep Gemini's semantic choice; only repair exact consecutive duplicates.
    rotation = [
        "process", "workflow", "timeline", "comparison", "dashboard",
        "network", "documents", "people", "technology", "domain", "concept"
    ]

    previous = None
    for idx, scene in enumerate(scenes):
        current = scene["visual_type"]

        if idx == 0:
            previous = current
            continue

        if current == previous and current not in {"chart", "dashboard"}:
            for alternative in rotation:
                if alternative != previous:
                    scene["visual_type"] = alternative
                    if alternative != "dashboard":
                        scene["show_chart"] = False
                        scene["chart_type"] = ""
                    current = alternative
                    break

        previous = current

    # First / last scenes
    scenes[0]["visual_type"] = "intro"
    scenes[0]["visual_style"] = "cinematic_cards"
    scenes[0]["show_chart"] = False
    scenes[0]["character"] = True

    scenes[-1]["visual_type"] = "conclusion"
    scenes[-1]["visual_style"] = "minimal"
    scenes[-1]["show_chart"] = False
    scenes[-1]["character"] = False

    # Renumber
    for i, scene in enumerate(scenes, start=1):
        scene["scene_number"] = i

    # Target duration
    total = sum(float(scene["duration"]) for scene in scenes)
    if total <= 0:
        total = len(scenes) * 6

    scale = target_seconds / total
    for scene in scenes:
        scene["duration"] = max(3.0, float(scene["duration"]) * scale)

    total = sum(scene["duration"] for scene in scenes)
    if total > 0:
        scale = target_seconds / total
        for scene in scenes:
            scene["duration"] *= scale

    data["scenes"] = scenes
    return data


# ============================================================
# SAVE
# ============================================================

def save_scene_data(data):

    with open(
        SCENE_DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print(
        "Scene data saved:"
    )
    print(
        SCENE_DATA_FILE
    )


# ============================================================
# RUN OUTPUT + VOICE ROTATION
# ============================================================

def safe_slug(text):
    text = re.sub(r"[^A-Za-z0-9]+", "_", str(text)).strip("_")
    return text[:70] or "video"


def choose_run_voice():
    """Rotate through professional Edge-TTS voices across video runs.

    The requested voice is tested before it is committed to the run. If a
    particular Edge-TTS voice is unavailable, the next available voice in the
    pool is tried automatically, so one bad voice never breaks the pipeline.
    """
    last_index = -1
    last_voice = ""

    try:
        if VOICE_STATE_FILE.exists():
            with open(VOICE_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                last_index = int(state.get("index", -1))
                last_voice = str(state.get("voice", "")).strip()
    except Exception:
        last_index = -1
        last_voice = ""

    index = (last_index + 1) % len(VOICE_POOL)
    if len(VOICE_POOL) > 1 and VOICE_POOL[index] == last_voice:
        index = (index + 1) % len(VOICE_POOL)

    return VOICE_POOL[index]


async def _save_voice_probe(voice, output_file):
    """Generate a tiny probe clip to confirm the Edge-TTS voice works."""
    probe = edge_tts.Communicate(
        "This is a voice test.",
        voice,
        rate="+0%",
        volume="+0%",
    )
    await probe.save(str(output_file))


def find_working_voice(preferred_voice):
    """Return the first voice that successfully produces a tiny audio file."""
    candidates = []
    try:
        preferred_index = VOICE_POOL.index(preferred_voice)
    except ValueError:
        preferred_index = 0

    for offset in range(len(VOICE_POOL)):
        voice = VOICE_POOL[(preferred_index + offset) % len(VOICE_POOL)]
        if voice not in candidates:
            candidates.append(voice)

    probe_dir = BASE_DIR / ".voice_probe"
    probe_dir.mkdir(exist_ok=True)
    probe_file = probe_dir / "voice_test.mp3"

    for voice in candidates:
        for attempt in range(2):
            try:
                if probe_file.exists():
                    probe_file.unlink()
                asyncio.run(_save_voice_probe(voice, probe_file))
                if probe_file.exists() and probe_file.stat().st_size > 1000:
                    print(f"Working narrator voice: {voice}")
                    return voice
            except Exception as exc:
                print(f"Voice check failed for {voice} (attempt {attempt + 1}/2): {exc}")

    raise RuntimeError(
        "No Edge-TTS voice could generate audio. Check internet connectivity and try again."
    )


def save_voice_state(selected_voice):
    """Persist the successful narrator voice so the next run rotates onward."""
    try:
        index = VOICE_POOL.index(selected_voice)
    except ValueError:
        index = 0

    try:
        with open(VOICE_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"index": index, "voice": selected_voice}, f, indent=2)
    except Exception:
        pass

def prepare_run_output(pdf_path, target_seconds):
    """Create a unique run folder so previous videos are never overwritten."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = safe_slug(pdf_path.stem)
    minute_tag = f"{int(target_seconds / 60)}min"

    run_dir = RUNS_DIR / f"{slug}_{minute_tag}_{stamp}"
    run_audio = run_dir / "audio"
    run_scenes = run_dir / "scenes"

    run_audio.mkdir(parents=True, exist_ok=True)
    run_scenes.mkdir(parents=True, exist_ok=True)

    final_video = run_dir / f"{slug}_{minute_tag}_{stamp}.mp4"
    final_srt = run_dir / f"{slug}_{minute_tag}_{stamp}.srt"
    final_vtt = run_dir / f"{slug}_{minute_tag}_{stamp}.vtt"

    return run_dir, run_audio, run_scenes, final_video, final_srt, final_vtt


# ============================================================
# AUDIO
# ============================================================

async def generate_audio(
    text,
    output_file,
    voice
):

    last_error = None

    for attempt in range(3):
        try:
            if output_file.exists():
                output_file.unlink()

            communicate = edge_tts.Communicate(
                text,
                voice,
                rate="+0%",
                volume="+0%"
            )

            await communicate.save(
                str(output_file)
            )

            if output_file.exists() and output_file.stat().st_size > 1000:
                return

            last_error = RuntimeError("Edge-TTS returned an empty audio file.")
        except Exception as exc:
            last_error = exc

        if attempt < 2:
            await asyncio.sleep(1.5 * (attempt + 1))

    raise RuntimeError(
        f"Edge-TTS failed after 3 attempts for voice {voice}: {last_error}"
    )


def create_audio(scenes, voice):

    print()
    print("=" * 70)
    print("GENERATING NARRATION")
    print("=" * 70)

    for scene in scenes:

        scene_no = scene[
            "scene_number"
        ]

        text = scene[
            "narration"
        ]

        output = (
            AUDIO_DIR
            / f"scene_{scene_no}.mp3"
        )

        if not text:
            continue

        print(
            f"Audio {scene_no}/{len(scenes)}"
        )

        asyncio.run(
            generate_audio(
                text,
                output,
                voice
            )
        )


# ============================================================
# PLACEHOLDER IMAGE DATA
# ============================================================

def create_images(scenes):

    """
    The final video renderer creates the actual visuals.
    We only keep this step for compatibility with the
    existing pipeline.
    """

    print()
    print(
        "Visual generation handled by generate_video.py"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 75)
    print("        SIH FINAL AI VIDEO GENERATOR")
    print("=" * 75)

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    pdf_path = find_pdf()

    print()
    print(
        "PDF:",
        pdf_path.name
    )

    # --------------------------------------------------------
    # Duration
    # --------------------------------------------------------

    target_seconds = get_target_duration()

    # --------------------------------------------------------
    # Unique output folder + rotating narrator
    # --------------------------------------------------------

    global AUDIO_DIR, IMAGE_DIR

    (run_dir, run_audio, run_scenes,
     final_video, final_srt, final_vtt) = prepare_run_output(
        pdf_path,
        target_seconds
    )

    AUDIO_DIR = run_audio
    IMAGE_DIR = run_dir / "images"
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    selected_voice = choose_run_voice()
    selected_voice = find_working_voice(selected_voice)
    save_voice_state(selected_voice)

    # --------------------------------------------------------
    # Read PDF
    # --------------------------------------------------------

    source_text = read_pdf(
        pdf_path
    )

    # --------------------------------------------------------
    # Storyboard
    # --------------------------------------------------------

    storyboard = create_storyboard(
        source_text,
        target_seconds
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    final_data = validate_storyboard(
        storyboard,
        target_seconds
    )

    final_data[
        "video_duration_seconds"
    ] = target_seconds
    final_data["run_dir"] = str(run_dir)
    final_data["audio_dir"] = str(run_audio)
    final_data["scenes_dir"] = str(run_scenes)
    final_data["final_video"] = str(final_video)
    final_data["final_srt"] = str(final_srt)
    final_data["final_vtt"] = str(final_vtt)
    final_data["voice"] = selected_voice
    final_data["source_pdf"] = pdf_path.name

    scenes = final_data[
        "scenes"
    ]

    # --------------------------------------------------------
    # Print plan
    # --------------------------------------------------------

    print()
    print("=" * 75)
    print("FINAL ANIMATED VISUAL PLAN")
    print("=" * 75)

    total_duration = 0

    for scene in scenes:

        total_duration += (
            scene["duration"]
        )

        print()
        print(
            f"SCENE {scene['scene_number']}: "
            f"{scene['scene_title']}"
        )

        print(
            "Duration:",
            round(
                scene["duration"],
                1
            ),
            "sec"
        )

        print(
            "Visual type:",
            scene["visual_type"]
        )

        print(
            "Visual:",
            scene["visual_concept"]
        )

        print(
            "Narration:",
            scene["narration"]
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_scene_data(
        final_data
    )

    # --------------------------------------------------------
    # Audio
    # --------------------------------------------------------

    create_audio(
        scenes,
        selected_voice
    )

    # --------------------------------------------------------
    # Finish
    # --------------------------------------------------------

    print()
    print("=" * 75)
    print("GENERATION COMPLETE")
    print("=" * 75)

    print()
    print(
        "Duration:",
        target_seconds,
        "seconds"
    )

    print(
        "Scenes:",
        len(scenes)
    )

    print("Narrator voice:", selected_voice)
    print("Output folder:", run_dir)

    print(
        "Planned duration:",
        round(
            total_duration,
            1
        ),
        "seconds"
    )

    print()
    print("STARTING AUTOMATIC VIDEO RENDER")
    print("=" * 75)

    renderer = BASE_DIR / "generate_video.py"

    if not renderer.exists():
        raise FileNotFoundError(
            f"generate_video.py not found: {renderer}"
        )

    import subprocess

    result = subprocess.run(
        [sys.executable, str(renderer)],
        cwd=str(BASE_DIR),
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Automatic video rendering failed. See the renderer output above."
        )

    print()
    print("AUTOMATIC VIDEO GENERATION COMPLETE")


if __name__ == "__main__":
    main()
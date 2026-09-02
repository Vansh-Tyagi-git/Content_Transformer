import os
import json
import re

from huggingface_hub import InferenceClient
from dotenv import load_dotenv


# ============================================================
# HUGGING FACE CLIENT INITIALIZATION
# ============================================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in .env file")

client = InferenceClient(token=HF_TOKEN)

MODEL_NAME = "deepseek-ai/DeepSeek-V3-0324"


# ============================================================
# SUPPORTED LAYOUTS
# ============================================================

SUPPORTED_LAYOUTS = {
    "title",
    "key_points",
    "two_column",
    "three_column",
    "comparison",
    "process",
    "timeline",
    "statistics",
    "quote",
    "recommendations",
    "conclusion",
}

SUPPORTED_VISUAL_TYPES = {
    "none",
    "chart",
    "process",
    "timeline",
    "statistics",
    "icon",
}


# ============================================================
# LIMITS
# ============================================================

MAX_SLIDES = 30
MAX_KEY_POINTS = 7
MAX_COLUMN_ITEMS = 6
MAX_PROCESS_STEPS = 6
MAX_TIMELINE_EVENTS = 6
MAX_STATISTICS = 5
MAX_RECOMMENDATIONS = 7


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text):
    """
    Extract JSON from a model response.

    Handles:
        - plain JSON
        - ```json ... ```
        - ``` ... ```
        - extra text surrounding JSON
    """

    if not text:
        raise ValueError("Empty response from model")

    text = text.strip()

    # Remove markdown fences if present.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # First attempt: entire response is JSON.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Second attempt: locate first JSON object.
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise json.JSONDecodeError(
            "No JSON object found",
            text,
            0
        )

    json_text = text[start:end + 1]

    return json.loads(json_text)


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_string(value):
    """
    Convert a value into a safe string.
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    return str(value).strip()


def normalize_string_list(value):
    """
    Normalize a value into a list of strings.
    """

    if value is None:
        return []

    if isinstance(value, str):
        return [value.strip()] if value.strip() else []

    if not isinstance(value, list):
        return [normalize_string(value)]

    result = []

    for item in value:
        text = normalize_string(item)

        if text:
            result.append(text)

    return result


def normalize_visual(visual):
    """
    Normalize visual information.
    """

    if not isinstance(visual, dict):
        return {
            "type": "none",
            "description": ""
        }

    visual_type = normalize_string(
        visual.get("type", "none")
    ).lower()

    if visual_type not in SUPPORTED_VISUAL_TYPES:
        visual_type = "none"

    return {
        "type": visual_type,
        "description": normalize_string(
            visual.get("description", "")
        )
    }


def normalize_three_column_content(content):
    """
    Normalize three-column objects.
    """

    if not isinstance(content, list):
        return []

    result = []

    for item in content[:3]:

        if isinstance(item, dict):

            result.append({
                "title": normalize_string(
                    item.get("title", "")
                ),
                "description": normalize_string(
                    item.get("description", "")
                )
            })

        else:

            result.append({
                "title": "",
                "description": normalize_string(item)
            })

    return result


def normalize_statistics(content):
    """
    Normalize statistics.

    Supports:

        {"value": "50%", "label": "Growth"}

    or:

        "50% growth"
    """

    if not isinstance(content, list):
        return []

    result = []

    for item in content[:MAX_STATISTICS]:

        if isinstance(item, dict):

            result.append({
                "value": normalize_string(
                    item.get("value", "")
                ),
                "label": normalize_string(
                    item.get("label", "")
                )
            })

        else:

            result.append({
                "value": normalize_string(item),
                "label": ""
            })

    return result


# ============================================================
# SLIDE NORMALIZATION
# ============================================================

def normalize_slide(slide, index):
    """
    Normalize a model-generated slide into the expected schema.
    """

    if not isinstance(slide, dict):
        raise ValueError(
            f"Slide {index} must be a JSON object"
        )

    layout = normalize_string(
        slide.get("layout", "key_points")
    ).lower()

    if layout not in SUPPORTED_LAYOUTS:
        raise ValueError(
            f"Slide {index}: unsupported layout '{layout}'"
        )

    normalized = {
        "slide_number": index,
        "layout": layout,
        "title": normalize_string(
            slide.get("title", "")
        ),
        "content": [],
        "left_content": [],
        "right_content": [],
        "visual": normalize_visual(
            slide.get("visual")
        )
    }

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    if layout == "title":

        normalized["title"] = normalize_string(
            slide.get("title", "")
        )

        normalized["subtitle"] = normalize_string(
            slide.get("subtitle", "")
        )

        return normalized

    # --------------------------------------------------------
    # THREE COLUMN
    # --------------------------------------------------------

    if layout == "three_column":

        normalized["content"] = (
            normalize_three_column_content(
                slide.get("content", [])
            )
        )

        if len(normalized["content"]) != 3:
            raise ValueError(
                f"Slide {index}: three_column "
                f"requires exactly 3 content objects"
            )

        return normalized

    # --------------------------------------------------------
    # TWO COLUMN / COMPARISON
    # --------------------------------------------------------

    if layout in {
        "two_column",
        "comparison"
    }:

        normalized["left_content"] = (
            normalize_string_list(
                slide.get("left_content", [])
            )[:MAX_COLUMN_ITEMS]
        )

        normalized["right_content"] = (
            normalize_string_list(
                slide.get("right_content", [])
            )[:MAX_COLUMN_ITEMS]
        )

        return normalized

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    if layout == "statistics":

        normalized["content"] = normalize_statistics(
            slide.get("content", [])
        )

        if not normalized["content"]:
            raise ValueError(
                f"Slide {index}: statistics slide "
                f"requires at least one statistic"
            )

        return normalized

    # --------------------------------------------------------
    # GENERAL LIST CONTENT
    # --------------------------------------------------------

    normalized["content"] = normalize_string_list(
        slide.get("content", [])
    )

    # --------------------------------------------------------
    # LIMIT CONTENT
    # --------------------------------------------------------

    if layout == "key_points":
        normalized["content"] = normalized["content"][
            :MAX_KEY_POINTS
        ]

    elif layout == "process":
        normalized["content"] = normalized["content"][
            :MAX_PROCESS_STEPS
        ]

    elif layout == "timeline":
        normalized["content"] = normalized["content"][
            :MAX_TIMELINE_EVENTS
        ]

    elif layout == "recommendations":
        normalized["content"] = normalized["content"][
            :MAX_RECOMMENDATIONS
        ]

    return normalized


# ============================================================
# PRESENTATION VALIDATION
# ============================================================

def validate_presentation(ppt_plan):
    """
    Validate and normalize the complete presentation.
    """

    if not isinstance(ppt_plan, dict):
        raise ValueError(
            "Presentation must be a JSON object"
        )

    title = normalize_string(
        ppt_plan.get("presentation_title", "")
    )

    if not title:
        raise ValueError(
            "Missing presentation_title"
        )

    subtitle = normalize_string(
        ppt_plan.get("presentation_subtitle", "")
    )

    slides = ppt_plan.get("slides")

    if not isinstance(slides, list):
        raise ValueError(
            "slides must be a list"
        )

    if not slides:
        raise ValueError(
            "Presentation contains no slides"
        )

    if len(slides) > MAX_SLIDES:
        slides = slides[:MAX_SLIDES]

    normalized_slides = []

    for index, slide in enumerate(
        slides,
        start=1
    ):

        normalized_slides.append(
            normalize_slide(
                slide,
                index
            )
        )

    # --------------------------------------------------------
    # FIRST SLIDE SHOULD BE TITLE
    # --------------------------------------------------------

    if normalized_slides[0]["layout"] != "title":

        # Automatically insert a title slide.
        title_slide = {
            "slide_number": 1,
            "layout": "title",
            "title": title,
            "subtitle": subtitle,
            "content": [],
            "left_content": [],
            "right_content": [],
            "visual": {
                "type": "none",
                "description": ""
            }
        }

        normalized_slides.insert(
            0,
            title_slide
        )

    # --------------------------------------------------------
    # FIX SLIDE NUMBERS
    # --------------------------------------------------------

    for number, slide in enumerate(
        normalized_slides,
        start=1
    ):
        slide["slide_number"] = number

    # --------------------------------------------------------
    # Ensure presentation title is used
    # --------------------------------------------------------

    if normalized_slides[0]["layout"] == "title":

        normalized_slides[0]["title"] = title
        normalized_slides[0]["subtitle"] = subtitle

    return {
        "presentation_title": title,
        "presentation_subtitle": subtitle,
        "slides": normalized_slides
    }


# ============================================================
# PPT PLAN GENERATOR
# ============================================================

def generate_ppt_plan(
    source_content,
    target_audience="General Audience",
    tone="Professional",
    language="English",
    detail_level="Medium",
    communication_objective="Inform",
    content_style="Clear and Structured"
):
    """
    Analyze source content and generate a structured
    PowerPoint presentation plan.

    Does NOT create a .pptx file.
    """

    if not source_content:
        return {
            "success": False,
            "error": "source_content cannot be empty"
        }

    prompt = f"""
You are an expert presentation strategist and PowerPoint
designer.

Create the BEST possible PowerPoint presentation based ONLY
on the provided source content.

Do not add information that is not supported by the source.

============================================================
SOURCE CONTENT
============================================================

{source_content}

============================================================
GENERATION PARAMETERS
============================================================

Target Audience:
{target_audience}

Tone:
{tone}

Language:
{language}

Level of Detail:
{detail_level}

Communication Objective:
{communication_objective}

Content Style:
{content_style}

============================================================
CORE RULES
============================================================

1. Analyze the source carefully before creating slides.

2. Determine the appropriate number of slides.

3. Do not force sections that are not supported by the source.

4. Never invent:
   - facts
   - statistics
   - examples
   - quotes
   - names
   - dates
   - recommendations
   - conclusions

5. Do not repeat information.

6. Keep slides concise and readable.

7. Every slide must have a clear purpose.

8. Use only information present in the source.

9. Prefer splitting dense information across slides.

10. The first slide MUST use the "title" layout.

11. Use "statistics" ONLY when the source contains actual
    numerical information.

12. Use "quote" ONLY when the source contains an actual quote.

13. Use "recommendations" ONLY when recommendations are
    explicitly supported by the source.

14. Use "conclusion" ONLY when a meaningful conclusion or
    takeaway is supported by the source.

============================================================
AVAILABLE LAYOUTS
============================================================

title
key_points
two_column
three_column
comparison
process
timeline
statistics
quote
recommendations
conclusion

============================================================
VISUAL TYPES
============================================================

none
chart
process
timeline
statistics
icon

Only request a visual when it is actually supported by the
source.

The renderer may use the visual information for future
enhancements, so never invent visual data.

============================================================
JSON FORMAT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "presentation_title": "Presentation title",
    "presentation_subtitle": "Optional subtitle",
    "slides": [
        {{
            "slide_number": 1,
            "layout": "title",
            "title": "Presentation title",
            "subtitle": "Optional subtitle",
            "content": [],
            "left_content": [],
            "right_content": [],
            "visual": {{
                "type": "none",
                "description": ""
            }}
        }}
    ]
}}

============================================================
LAYOUT RULES
============================================================

TITLE:
- content must be []
- Use title and optional subtitle.

KEY POINTS:
- content is a list of concise strings.
- Prefer 3-7 points.

TWO COLUMN:
- left_content is a list of strings.
- right_content is a list of strings.

THREE COLUMN:
content MUST contain exactly 3 objects:

{{
    "title": "Heading",
    "description": "Description"
}}

COMPARISON:
- left_content represents one side.
- right_content represents the other side.

PROCESS:
- content is a sequential list of steps.

TIMELINE:
- content is a chronological list of events.

STATISTICS:
content MUST contain objects:

{{
    "value": "50%",
    "label": "Meaning of the statistic"
}}

Use only numbers actually present in the source.

QUOTE:
- content contains the actual quote.
- Do not create or paraphrase quotes.

RECOMMENDATIONS:
- content contains recommendations supported by the source.

CONCLUSION:
- content contains the key takeaway supported by the source.

============================================================
FINAL REQUIREMENT
============================================================

Return ONLY the JSON object.
"""


    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert presentation strategist "
                        "and PowerPoint designer. "
                        "Return only valid JSON when requested. "
                        "Never invent facts, statistics, quotes, "
                        "names, dates, recommendations, examples, "
                        "or conclusions."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=5000,
            temperature=0.2
        )

        response_text = (
            response.choices[0]
            .message.content
            .strip()
        )

        raw_plan = extract_json(
            response_text
        )

        ppt_plan = validate_presentation(
            raw_plan
        )

        return {
            "success": True,
            "presentation": ppt_plan
        }

    except json.JSONDecodeError as e:

        return {
            "success": False,
            "error": (
                f"Invalid JSON returned by DeepSeek: {str(e)}"
            ),
            "raw_response": (
                response_text
                if "response_text" in locals()
                else ""
            )
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
            "raw_response": (
                response_text
                if "response_text" in locals()
                else ""
            )
        }
import os
import json
import re

from huggingface_hub import InferenceClient
from dotenv import load_dotenv


# ============================================================
# HUGGING FACE CLIENT
# ============================================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in .env file")

client = InferenceClient(
    token=HF_TOKEN
)

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
    "conclusion"
}


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text):
    """
    Extract JSON from model response.

    Handles:
    - plain JSON
    - ```json ... ```
    - accidental surrounding text
    """

    text = text.strip()

    # Remove markdown fences
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # First attempt
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise json.JSONDecodeError(
            "No JSON object found",
            text,
            0
        )

    json_text = text[start:end + 1]

    return json.loads(json_text)


# ============================================================
# NORMALIZE MODEL OUTPUT
# ============================================================

def normalize_presentation(plan):
    """
    Make the generated presentation safer for the renderer.
    """

    plan.setdefault(
        "presentation_title",
        "Presentation"
    )

    plan.setdefault(
        "presentation_subtitle",
        ""
    )

    plan.setdefault(
        "presentation_summary",
        ""
    )

    plan.setdefault(
        "source_metadata",
        {}
    )

    plan.setdefault(
        "design_metadata",
        {}
    )

    slides = plan.get("slides", [])

    for index, slide in enumerate(slides, start=1):

        slide.setdefault(
            "slide_number",
            index
        )

        slide.setdefault(
            "layout",
            "key_points"
        )

        slide.setdefault(
            "title",
            ""
        )

        slide.setdefault(
            "kicker",
            ""
        )

        slide.setdefault(
            "content",
            []
        )

        slide.setdefault(
            "left_content",
            []
        )

        slide.setdefault(
            "right_content",
            []
        )

        slide.setdefault(
            "takeaway",
            ""
        )

        slide.setdefault(
            "visual",
            {
                "type": "none",
                "description": ""
            }
        )

        slide.setdefault(
            "source_reference",
            ""
        )

    return plan


# ============================================================
# VALIDATION
# ============================================================

def validate_presentation(plan):

    if not isinstance(plan, dict):
        raise ValueError(
            "Presentation must be a JSON object"
        )

    if "presentation_title" not in plan:
        raise ValueError(
            "Missing presentation_title"
        )

    if "slides" not in plan:
        raise ValueError(
            "Missing slides"
        )

    if not isinstance(plan["slides"], list):
        raise ValueError(
            "slides must be a list"
        )

    if not plan["slides"]:
        raise ValueError(
            "Presentation contains no slides"
        )

    for index, slide in enumerate(
        plan["slides"],
        start=1
    ):

        if not isinstance(slide, dict):
            raise ValueError(
                f"Slide {index} must be an object"
            )

        layout = slide.get("layout")

        if layout not in SUPPORTED_LAYOUTS:
            raise ValueError(
                f"Unsupported layout: {layout}"
            )

        if not slide.get("title"):
            raise ValueError(
                f"Slide {index} is missing title"
            )

        slide["slide_number"] = index

        visual = slide.get(
            "visual",
            {}
        )

        if not isinstance(visual, dict):
            slide["visual"] = {
                "type": "none",
                "description": ""
            }

        else:
            visual.setdefault(
                "type",
                "none"
            )

            visual.setdefault(
                "description",
                ""
            )

    return True


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
    Analyze source content and create a presentation plan.

    The model extracts substantially more information than
    just slide bullets.

    Everything must be grounded in the source.
    """

    if not source_content or not str(source_content).strip():
        return {
            "success": False,
            "error": "source_content is empty"
        }

    prompt = f"""
You are a senior presentation strategist, information
designer, business analyst, and PowerPoint art director.

Your job is to transform the SOURCE CONTENT into a
high-quality, evidence-grounded presentation.

Do NOT merely summarize the source.

First understand the source deeply.

Then build a coherent presentation narrative.

============================================================
SOURCE CONTENT
============================================================

{source_content}

============================================================
PRESENTATION PARAMETERS
============================================================

Target Audience:
{target_audience}

Tone:
{tone}

Language:
{language}

Detail Level:
{detail_level}

Communication Objective:
{communication_objective}

Content Style:
{content_style}

============================================================
IMPORTANT SOURCE-GROUNDING RULE
============================================================

EVERY factual statement in the presentation must be
supported by the source.

Never invent:

- facts
- statistics
- percentages
- dates
- names
- organizations
- quotes
- examples
- case studies
- recommendations
- conclusions
- causes
- effects
- benefits
- risks

If something is not explicitly supported by the source,
do not include it.

You MAY reorganize, condense, combine, and rephrase
information from the source.

You MAY infer the presentation structure from the source,
but do not invent factual information.

============================================================
SOURCE METADATA EXTRACTION
============================================================

Extract as much useful metadata as the source genuinely
contains.

Create:

source_metadata:

{{
    "document_type": "",
    "summary": "",
    "key_themes": [],
    "key_topics": [],
    "keywords": [],
    "entities": [],
    "people": [],
    "organizations": [],
    "locations": [],
    "dates": [],
    "time_periods": [],
    "statistics": [],
    "facts": [],
    "quotes": [],
    "opportunities": [],
    "challenges": [],
    "risks": [],
    "benefits": [],
    "recommendations": [],
    "actions": [],
    "processes": [],
    "milestones": [],
    "relationships": [],
    "important_terms": []
}}

Rules:

- Use empty arrays when information does not exist.
- Do not hallucinate metadata.
- statistics must contain only actual numerical information.
- quotes must contain only actual quotes from the source.
- dates must contain only dates or time periods explicitly
  present in the source.
- entities must only contain entities explicitly mentioned.
- relationships should describe relationships explicitly
  supported by the source.
- important_terms can contain concepts that are important
  for understanding the source.

For statistics use:

{{
    "value": "",
    "label": "",
    "context": ""
}}

============================================================
PRESENTATION STRATEGY
============================================================

Before creating slides, identify:

1. The central message.
2. The most important ideas.
3. The logical relationship between those ideas.
4. What should be shown first.
5. What deserves visual emphasis.
6. Which information is suitable for comparison.
7. Which information is sequential.
8. Which information contains actual numbers.
9. Which information deserves a conclusion.

The presentation should feel like a coherent story.

Avoid creating one slide for every paragraph.

Avoid repeating the same idea on multiple slides.

Prefer approximately:

- 5-10 slides for a normal source
- fewer slides for short sources
- more slides only when the source genuinely contains
  enough distinct material

============================================================
SLIDE DESIGN
============================================================

Each slide must have a clear communication purpose.

Use concise titles.

Use a small "kicker" above the title when useful.

A kicker should identify the section/category, for example:

"CONTEXT"
"KEY FINDINGS"
"CHALLENGES"
"OPPORTUNITIES"
"PROCESS"
"IMPLICATIONS"

Do not use kickers unnecessarily.

Each slide may contain:

- title
- kicker
- content
- left_content
- right_content
- takeaway
- visual
- source_reference

"takeaway" should be a short statement emphasizing the
most important message of the slide.

"source_reference" should identify the relevant part of
the source in a concise way, when useful.

============================================================
AVAILABLE LAYOUTS
============================================================

Use only:

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
LAYOUT RULES
============================================================

TITLE

Use:

layout = "title"

Keep content empty.

The title slide should contain:

- strong title
- useful subtitle
- optionally a short presentation summary

------------------------------------------------------------

KEY POINTS

Use for several related insights.

Prefer objects:

"content": [
    {{
        "title": "Short heading",
        "description": "Concise explanation"
    }}
]

You may use strings when appropriate.

Maximum recommended items: 5.

------------------------------------------------------------

TWO COLUMN

Use when two related categories should be viewed together.

Example:

"left_content": [
    {{
        "title": "Heading",
        "description": "Explanation"
    }}
]

"right_content": [
    {{
        "title": "Heading",
        "description": "Explanation"
    }}
]

------------------------------------------------------------

THREE COLUMN

Use exactly three meaningful concepts.

"content": [
    {{
        "title": "...",
        "description": "..."
    }},
    {{
        "title": "...",
        "description": "..."
    }},
    {{
        "title": "...",
        "description": "..."
    }}
]

------------------------------------------------------------

COMPARISON

Use only when the source genuinely compares two things.

Left = first side.

Right = second side.

Do not manufacture a comparison.

------------------------------------------------------------

PROCESS

Use only when the source describes a process or sequence.

Example:

"content": [
    {{
        "step": "01",
        "title": "Step title",
        "description": "Step explanation"
    }}
]

------------------------------------------------------------

TIMELINE

Use only when chronological information exists.

Example:

"content": [
    {{
        "date": "2024",
        "title": "Event",
        "description": "Description"
    }}
]

Do not invent dates.

------------------------------------------------------------

STATISTICS

Use only if actual numerical information exists.

Example:

"content": [
    {{
        "value": "42%",
        "label": "Metric",
        "context": "Source context"
    }}
]

Never invent numbers.

------------------------------------------------------------

QUOTE

Use only for an actual quote.

Example:

"content": [
    {{
        "quote": "Actual quote",
        "attribution": "Person or source if explicitly provided"
    }}
]

Never invent quotations.

------------------------------------------------------------

RECOMMENDATIONS

Use only if the source explicitly provides recommendations
or actions.

------------------------------------------------------------

CONCLUSION

Use only if a meaningful takeaway can be directly supported
by the source.

============================================================
VISUAL PLANNING
============================================================

For every slide choose:

visual.type:

"none"
"chart"
"process"
"timeline"
"statistics"
"icon"

The visual description should explain what the renderer
should emphasize.

Do NOT request photographs or external images because the
renderer does not download external images.

For example:

{{
    "type": "statistics",
    "description": "Emphasize the three numerical metrics
    as large cards."
}}

============================================================
DESIGN METADATA
============================================================

Also provide:

design_metadata:

{{
    "visual_theme": "Modern Professional",
    "primary_color": "navy",
    "accent_color": "blue",
    "secondary_color": "light blue",
    "recommended_visual_density": "medium",
    "recommended_emphasis": [],
    "presentation_style": "executive"
}}

Choose the style based on the content and audience.

============================================================
OUTPUT JSON
============================================================

Return ONLY valid JSON.

Use exactly this top-level structure:

{{
    "presentation_title": "",
    "presentation_subtitle": "",
    "presentation_summary": "",

    "source_metadata": {{
        "document_type": "",
        "summary": "",
        "key_themes": [],
        "key_topics": [],
        "keywords": [],
        "entities": [],
        "people": [],
        "organizations": [],
        "locations": [],
        "dates": [],
        "time_periods": [],
        "statistics": [],
        "facts": [],
        "quotes": [],
        "opportunities": [],
        "challenges": [],
        "risks": [],
        "benefits": [],
        "recommendations": [],
        "actions": [],
        "processes": [],
        "milestones": [],
        "relationships": [],
        "important_terms": []
    }},

    "design_metadata": {{
        "visual_theme": "",
        "primary_color": "",
        "accent_color": "",
        "secondary_color": "",
        "recommended_visual_density": "",
        "recommended_emphasis": [],
        "presentation_style": ""
    }},

    "slides": [
        {{
            "slide_number": 1,
            "layout": "title",
            "kicker": "",
            "title": "",
            "content": [],
            "left_content": [],
            "right_content": [],
            "takeaway": "",
            "visual": {{
                "type": "none",
                "description": ""
            }},
            "source_reference": ""
        }}
    ]
}}

============================================================
FINAL QUALITY CHECK
============================================================

Before returning JSON verify:

- Every claim is source-grounded.
- No invented statistics.
- No invented quotes.
- No invented dates.
- No unnecessary slides.
- No repeated ideas.
- Slides have clear purposes.
- The title slide is meaningful.
- Statistics are used only when numbers exist.
- Timeline is used only when dates exist.
- Quote is used only when an actual quote exists.
- Recommendations are source-supported.
- Conclusion is source-supported.
- JSON is valid.

Return ONLY JSON.
"""

    response_text = ""

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert presentation strategist "
                        "and information designer. "
                        "Return only valid JSON. "
                        "Never invent source facts."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=7000,
            temperature=0.2
        )

        response_text = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        ppt_plan = extract_json(
            response_text
        )

        ppt_plan = normalize_presentation(
            ppt_plan
        )

        validate_presentation(
            ppt_plan
        )

        return {
            "success": True,
            "presentation": ppt_plan
        }

    except json.JSONDecodeError as e:

        return {
            "success": False,
            "error": (
                f"Invalid JSON returned by DeepSeek: {e}"
            ),
            "raw_response": response_text
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
            "raw_response": response_text
        }
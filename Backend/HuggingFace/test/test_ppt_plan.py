from pathlib import Path
import sys
import json


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


# ============================================================
# IMPORTS
# ============================================================

from ppt.ppt_generator import generate_ppt_plan
from ppt.ppt_renderer import render_ppt


# ============================================================
# TEST SOURCE CONTENT
# ============================================================

source_content = """
Artificial intelligence is increasingly being adopted by
organizations to automate repetitive tasks, improve decision-making,
and enhance operational efficiency.

However, AI adoption also introduces challenges related to data
privacy, security, transparency, and responsible implementation.

Organizations need appropriate governance frameworks to ensure
that AI systems are used responsibly while maximizing their
potential benefits.
"""


# ============================================================
# OUTPUT PATHS
# ============================================================

OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_PPTX = OUTPUT_DIR / "ai_adoption_presentation.pptx"
OUTPUT_JSON = OUTPUT_DIR / "ai_adoption_presentation.json"


# ============================================================
# GENERATE PRESENTATION PLAN
# ============================================================

print("\n" + "=" * 70)
print("GENERATING PPT PLAN")
print("=" * 70)

result = generate_ppt_plan(
    source_content=source_content,
    target_audience="Business and Technology Professionals",
    tone="Professional and Informative",
    language="English",
    detail_level="Medium",
    communication_objective="Educate",
    content_style="Clear and Engaging"
)


# ============================================================
# HANDLE GENERATION FAILURE
# ============================================================

if not result.get("success"):

    print("\n" + "=" * 70)
    print("PPT PLAN GENERATION FAILED")
    print("=" * 70)

    print("\nError:")
    print(result.get("error", "Unknown error"))

    if result.get("raw_response"):

        print("\nRaw DeepSeek Response:")
        print(result["raw_response"])

    sys.exit(1)


# ============================================================
# GET PRESENTATION
# ============================================================

presentation = result["presentation"]


# ============================================================
# PRINT FULL JSON
# ============================================================

print("\n" + "=" * 70)
print("GENERATED PRESENTATION JSON")
print("=" * 70)

print(
    json.dumps(
        presentation,
        indent=4,
        ensure_ascii=False
    )
)


# ============================================================
# SAVE JSON
# ============================================================

try:

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            presentation,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nJSON saved to:")
    print(OUTPUT_JSON)

except Exception as e:

    print("\nFailed to save JSON:")
    print(str(e))


# ============================================================
# PRINT SLIDE SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SLIDE SUMMARY")
print("=" * 70)

for slide in presentation["slides"]:

    print("\n" + "-" * 70)

    print(
        f"Slide {slide['slide_number']}: "
        f"{slide['title']}"
    )

    print(
        f"Layout: {slide['layout']}"
    )

    if slide.get("subtitle"):

        print(
            f"Subtitle: {slide['subtitle']}"
        )

    if slide.get("content"):

        print("Content:")

        for item in slide["content"]:

            if isinstance(item, dict):

                print(
                    "  - "
                    + json.dumps(
                        item,
                        ensure_ascii=False
                    )
                )

            else:

                print(
                    f"  - {item}"
                )

    if slide.get("left_content"):

        print("Left Content:")

        for item in slide["left_content"]:

            print(
                f"  - {item}"
            )

    if slide.get("right_content"):

        print("Right Content:")

        for item in slide["right_content"]:

            print(
                f"  - {item}"
            )

    visual = slide.get(
        "visual",
        {}
    )

    print("Visual:")
    print(
        f"  Type: {visual.get('type', 'none')}"
    )
    print(
        f"  Description: "
        f"{visual.get('description', '')}"
    )


# ============================================================
# RENDER POWERPOINT
# ============================================================

print("\n" + "=" * 70)
print("RENDERING POWERPOINT")
print("=" * 70)

try:

    output_path = render_ppt(
        presentation_data=presentation,
        output_path=str(OUTPUT_PPTX)
    )

    print("\nPowerPoint generated successfully.")

    print(
        f"File: {output_path}"
    )

    if Path(output_path).exists():

        file_size = Path(
            output_path
        ).stat().st_size

        print(
            f"Size: {file_size:,} bytes"
        )

except Exception as e:

    print("\n" + "=" * 70)
    print("POWERPOINT RENDERING FAILED")
    print("=" * 70)

    print(
        f"Error: {str(e)}"
    )

    sys.exit(1)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("TEST COMPLETED SUCCESSFULLY")
print("=" * 70)

print(
    f"\nJSON : {OUTPUT_JSON}"
)

print(
    f"PPTX : {OUTPUT_PPTX}"
)

print("\n")
"""
infographic_generator.py

Generate a structured infographic specification from source content
using a Hugging Face Inference Provider.

Setup:
    pip install -U huggingface_hub python-dotenv

Create a .env file:
    HF_TOKEN=hf_your_token_here

Run:
    python infographic_generator.py

Or import:
    from infographic_generator import generate_infographic
    result = generate_infographic("your article/report text here")
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

# Change this if you want to test another model available through
# Hugging Face Inference Providers.
MODEL = os.getenv("HF_MODEL", "Qwen/Qwen3-32B")

SYSTEM_PROMPT = r"""
You are an expert information designer, content strategist, and visual
communication specialist.

The user has selected "Infographic" as the desired output format.

Transform the provided source content into a structured infographic
specification that a frontend application can render.

DO NOT generate an image.
DO NOT use Markdown.
Return ONLY valid JSON.

IMPORTANT RULES:
1. Understand the source content before generating the infographic.
2. Extract only facts supported by the source.
3. Never invent statistics, dates, names, quotations, organizations,
   percentages, or conclusions.
4. If a statistic is not explicitly present in the source, do not create one.
5. Keep text short and suitable for visual display.
6. Preserve important technical terminology where necessary.
7. Explain complex concepts in simple language where appropriate.
8. Create a clear visual hierarchy.
9. Recommend charts only when the source contains suitable numerical data.
10. Recommend timelines only when the source contains meaningful chronological
    information.
11. Recommend maps only when the source contains geographic information.
12. The final JSON must be directly usable by a frontend renderer.

The output must follow this exact structure:

{
  "title": "string",
  "subtitle": "string",
  "key_message": "string",
  "layout": {
    "type": "vertical_story | horizontal_timeline | process_flow | statistics_dashboard | comparison | problem_solution | risk_response | before_after | hierarchical | map_based",
    "reason": "string"
  },
  "key_statistics": [
    {
      "value": "string",
      "unit": "string",
      "label": "string",
      "context": "string"
    }
  ],
  "sections": [
    {
      "section_title": "string",
      "short_description": "string",
      "key_points": ["string"],
      "visual_type": "icon | statistic | bar_chart | pie_chart | timeline | process_flow | comparison | map | hierarchy | checklist | quote | alert | diagram | illustration",
      "visual_description": "string"
    }
  ],
  "visual_hierarchy": {
    "primary_element": "string",
    "secondary_elements": "string",
    "supporting_elements": "string"
  },
  "key_messaging": {
    "headline": "string",
    "supporting_message": "string",
    "call_to_action": "string"
  },
  "design_recommendations": {
    "typography": "string",
    "icon_usage": "string",
    "chart_usage": "string",
    "spacing": "string",
    "information_density": "string"
  },
  "fact_checking": ["string"]
}

Additional constraints:
- title: maximum 12 words.
- subtitle: maximum 20 words.
- sections: 3 to 7 sections.
- Each section should have 2 to 5 key points.
- key_message should be one concise sentence.
- key_statistics should contain only source-supported numerical information.
- fact_checking should contain claims that require verification. If none,
  return [].
"""

def generate_infographic(
    source_content: str,
    target_audience: str = "General Public",
    tone: str = "Professional",
    language: str = "English",
    detail_level: str = "Medium",
    communication_objective: str = "Awareness",
):
    """Generate an infographic JSON object from source text."""

    if not source_content or not source_content.strip():
        raise ValueError("source_content cannot be empty.")

    if not HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN is missing. Add it to your .env file or environment."
        )

    client = InferenceClient(
        provider="auto",
        api_key=HF_TOKEN,
    )

    user_prompt = f"""
TARGET AUDIENCE:
{target_audience}

TONE:
{tone}

LANGUAGE:
{language}

LEVEL OF DETAIL:
{detail_level}

COMMUNICATION OBJECTIVE:
{communication_objective}

SOURCE CONTENT:
----------------
{source_content}
----------------

Generate the infographic specification using the required JSON structure.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=4000,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("The model returned an empty response.")

    # Models sometimes surround JSON with ```json ... ```.
    # Remove that wrapper before parsing.
    content = content.strip()

    if content.startswith("```"):
        lines = content.splitlines()
        lines = lines[1:] if lines and lines[0].startswith("```") else lines
        lines = lines[:-1] if lines and lines[-1].strip() == "```" else lines
        content = "\n".join(lines).strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        # Save the raw response to make debugging easy.
        Path("raw_infographic_response.txt").write_text(
            content, encoding="utf-8"
        )
        raise RuntimeError(
            "Model did not return valid JSON. "
            "Raw response saved to raw_infographic_response.txt"
        ) from exc


def main():
    # Replace this with text extracted from your PDF, DOCX, article, etc.
    source_content = """
    Cybersecurity teams increasingly use network traffic analysis to identify
    suspicious activity. Large volumes of network traffic make manual analysis
    difficult. Machine-learning systems can analyze traffic patterns,
    identify anomalies, and help security teams forecast potential attacks.
    Early identification can help organizations prioritize monitoring and
    response efforts.
    """

    infographic = generate_infographic(
        source_content=source_content,
        target_audience="Cybersecurity professionals and students",
        tone="Professional",
        language="English",
        detail_level="Medium",
        communication_objective="Awareness",
    )

    print(json.dumps(infographic, indent=2, ensure_ascii=False))

    # Also save the result for your frontend.
    Path("infographic.json").write_text(
        json.dumps(infographic, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nSaved to: infographic.json")


if __name__ == "__main__":
    main()

import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv


# ============================================================
# HUGGING FACE CLIENT INITIALIZATION
# ============================================================

# Load variables from .env file
load_dotenv()

# Get Hugging Face API key
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError(
        "HF_TOKEN not found in .env file"
    )

# Initialize Hugging Face client
client = InferenceClient(
    token=HF_TOKEN
)

# DeepSeek model
MODEL_NAME = "deepseek-ai/DeepSeek-V3-0324"


# ============================================================
# TEXT OUTPUT TYPE INSTRUCTIONS
# ============================================================

# This file handles TEXT outputs only.
#
# Video, infographic and PPT generation will be handled
# by separate Python files.


OUTPUT_PROMPTS = {

    "linkedin_post": """
Create a professional and engaging LinkedIn post based on the
provided source content.

Requirements:

- Make it suitable for LinkedIn.
- Start with a strong hook.
- Use clear and natural language.
- Keep paragraphs short and readable.
- Highlight important insights or takeaways.
- End with a meaningful conclusion.
- Add relevant hashtags at the end.
- Do not invent facts not present in the source.
""",

    "twitter_post": """
Create content suitable for Twitter/X based on the provided source.

Decide whether the content should be:

1. A single concise post, or
2. A tweet thread.

Requirements:

- Make it concise and engaging.
- Optimize the wording for Twitter/X.
- Start with a strong opening.
- If a thread is appropriate, number each tweet clearly.
- Preserve important facts from the source.
- Do not invent unsupported information.
""",

    "advisory": """
Create a structured and professional advisory based on the
provided source content.

Use the following structure where applicable:

1. Title
2. Background / Context
3. Key Issue or Development
4. Important Information
5. Potential Impact
6. Recommended Actions
7. Additional Considerations
8. Conclusion

The advisory should be:

- Clear
- Formal
- Actionable
- Suitable for the intended audience

Do not invent facts that are not supported by the source content.
""",

    "executive_summary": """
Create a concise executive summary based on the provided source.

Focus on:

- The most important information
- Key developments or findings
- Potential impact
- Important risks or opportunities
- Recommended actions, if applicable

The summary should allow senior decision-makers to quickly
understand the key message.

Avoid unnecessary technical details unless they are important
for decision-making.
"""
}


# ============================================================
# SUPPORTED TEXT OUTPUT TYPES
# ============================================================

TEXT_OUTPUT_TYPES = {
    "linkedin_post",
    "twitter_post",
    "advisory",
    "executive_summary"
}


# ============================================================
# MAIN CONTENT GENERATION FUNCTION
# ============================================================

def generate_content(
    source_content,
    output_types,
    target_audience="General Audience",
    tone="Professional",
    language="English",
    detail_level="Medium",
    communication_objective="Inform",
    content_style="Clear and Structured"
):
    """
    Generate one or more TEXT content artefacts from the
    same source.

    Supported output types:
        - linkedin_post
        - twitter_post
        - advisory
        - executive_summary

    Video, infographic and PPT are NOT handled here.
    """

    results = {}

    # ========================================================
    # GENERATE EACH SELECTED TEXT OUTPUT
    # ========================================================

    for output_type in output_types:

        # Check if the selected output is supported
        if output_type not in TEXT_OUTPUT_TYPES:
            results[output_type] = {
                "success": False,
                "error": (
                    f"Unsupported text output type: {output_type}"
                )
            }
            continue

        # ====================================================
        # BUILD AI PROMPT
        # ====================================================

        prompt = f"""
You are an AI-powered content transformation engine.

Your task is to analyze the provided source content and transform
it into the requested communication artefact.

SOURCE CONTENT:
----------------
{source_content}
----------------

GENERATION PARAMETERS:

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

REQUESTED OUTPUT TYPE:
{output_type}

SPECIFIC OUTPUT INSTRUCTIONS:
{OUTPUT_PROMPTS[output_type]}

GENERAL RULES:

- Carefully analyze the source content before generating.
- Preserve factual accuracy.
- Do not hallucinate or invent information.
- Adapt the content to the specified target audience.
- Follow the requested tone and communication objective.
- Write the output in {language}.
- Match the requested level of detail.
- Return only the final generated artefact.
"""

        # ====================================================
        # HUGGING FACE / DEEPSEEK API CALL
        # ====================================================

        try:

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI-powered content "
                            "transformation engine. "
                            "Follow the user's instructions carefully "
                            "and do not invent unsupported facts."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )

            generated_content = response.choices[0].message.content

            results[output_type] = {
                "success": True,
                "content": generated_content
            }

        except Exception as e:

            results[output_type] = {
                "success": False,
                "error": str(e)
            }

    # ========================================================
    # RETURN ALL GENERATED TEXT OUTPUTS
    # ========================================================

    return results

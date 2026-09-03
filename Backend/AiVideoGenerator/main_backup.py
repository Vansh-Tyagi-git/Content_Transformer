import pymupdf
from google import genai
import os
import asyncio
import edge_tts
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip

# -----------------------------
# 1. Read PDF
# -----------------------------

pdf_path = "input/sample.pdf"

doc = pymupdf.open(pdf_path)

text = ""

for page in doc:
    text += page.get_text()

print("PDF successfully read!")
print("--------------------------------")

# -----------------------------
# 2. Connect to Gemini
# -----------------------------

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# -----------------------------
# 3. Ask Gemini to create
#    a video plan
# -----------------------------

prompt = f"""
You are an expert AI video content creator and documentary storyteller.

Your task is to transform the SOURCE CONTENT into a professional,
engaging, production-ready video plan.

IMPORTANT RULE:
Use ONLY facts and information present in the SOURCE CONTENT.
Do not invent statistics, examples, names, dates, claims, or information.
If something is not stated in the source, do not add it.

VIDEO STYLE:
- Professional and modern
- Engaging documentary/explainer style
- Clear and natural conversational narration
- Suitable for a corporate audience
- Avoid textbook-like or robotic writing
- Start with a strong but source-grounded hook
- Use visual storytelling instead of only bullet points
- Keep the flow logical from beginning to end

Create the following:

1. VIDEO TITLE
A short, professional and interesting title.

2. VIDEO HOOK / INTRODUCTION
Write an engaging opening that immediately introduces the main topic.
Do not describe the video plan itself.

3. COMPLETE NARRATION SCRIPT
Write natural spoken narration for the entire video.
The narration must be based only on the source.

4. SCENE-BY-SCENE STORYBOARD
Create 7 to 9 scenes.

For every scene provide:
- Scene number
- Scene title
- Approximate duration
- Narration for that scene
- What should appear visually
- Camera/animation direction
- On-screen text
- Important fact or message being highlighted
- Suggested transition to the next scene

5. VISUAL DIRECTION
Suggest relevant visuals for each scene.
Prefer:
- Realistic business visuals
- Relevant illustrations
- Charts or diagrams when supported by the source
- Motion graphics
- Icons only when useful
- Smooth animations and transitions

Do not suggest visuals that communicate facts not present in the source.

6. ON-SCREEN TEXT
Keep text short and readable.
Highlight important concepts, keywords and facts from the source.
Do not overcrowd the screen.

7. CONCLUSION
End with a concise and professional conclusion based only on
the source content.

8. SOURCE / FACT CHECK NOTE
List the important facts used in the video and confirm that they
are supported by the SOURCE CONTENT.

QUALITY REQUIREMENTS:
- No hallucinations
- No unsupported claims
- No unnecessary repetition
- Narration and visuals must match
- Scene durations should realistically match the narration
- The video should feel like a professionally produced explainer,
  not a collection of slides
- Maintain a clear beginning, middle and ending

SOURCE CONTENT:
{text}
"""

response = client.interactions.create(
    model="gemini-3.5-flash",
    input=prompt
)

print(response.output_text)

# -----------------------------
# 4. Critic - Check the draft
# -----------------------------

draft = response.output_text

critic_prompt = f"""
You are a strict quality-control reviewer for an AI video generation system.

You will review a VIDEO PLAN against the ORIGINAL SOURCE CONTENT.

Your job is NOT to create a new video plan.
Your job is to find problems in the existing draft.

ORIGINAL SOURCE CONTENT:
{text}

VIDEO PLAN TO REVIEW:
{draft}

Check the video plan for:

1. FACTUAL ACCURACY
- Is every factual claim supported by the source?
- Identify anything that is added, exaggerated, or unsupported.

2. COMPLETENESS
- Are important points from the source missing?

3. HALLUCINATION
- Identify any information that does not appear in the source.

4. NARRATION QUALITY
- Is the narration natural, clear and engaging?
- Identify robotic, generic or unnecessary wording.

5. STORY FLOW
- Does the video have a strong beginning, logical middle and conclusion?
- Are scenes arranged logically?

6. VISUAL QUALITY
- Do the suggested visuals actually represent the narration?
- Identify visuals that are too generic, repetitive or misleading.

7. ON-SCREEN TEXT
- Is the text short, clear and supported by the source?
- Identify unnecessary or unsupported text.

8. TIMING
- Check whether the scene durations are reasonable for the narration.

IMPORTANT:
Be strict.
Do not assume information is correct just because it sounds reasonable.
Use ONLY the ORIGINAL SOURCE CONTENT as the factual reference.

Return your review in this format:

OVERALL SCORE: X/10

CRITICAL ISSUES:
- ...

FACTUAL ISSUES:
- ...

MISSING INFORMATION:
- ...

NARRATION ISSUES:
- ...

VISUAL ISSUES:
- ...

ON-SCREEN TEXT ISSUES:
- ...

TIMING ISSUES:
- ...

RECOMMENDED FIXES:
- ...
"""

critique_response = client.interactions.create(
    model="gemini-3.5-flash",
    input=critic_prompt
)

print("\n")
print("========== CRITIC REVIEW ==========")
print(critique_response.output_text)

# -----------------------------
# 5. Final Editor
# -----------------------------

critique = critique_response.output_text

final_prompt = f"""
You are the final editor of an AI video generation system.

Create the FINAL production-ready video plan by improving the DRAFT
using the CRITIC REVIEW.

IMPORTANT:
The ORIGINAL SOURCE CONTENT is the ONLY source of truth.

Do NOT add any fact, statistic, example, claim, name, date, or conclusion
that is not supported by the original source.

Do NOT blindly follow the critic.
If a critic recommendation conflicts with the source, follow the source.

ORIGINAL SOURCE CONTENT:
{text}

DRAFT VIDEO PLAN:
{draft}

CRITIC REVIEW:
{critique}

Now create the FINAL corrected video plan.

Requirements:

1. VIDEO TITLE
Use a clear, professional title based on the source.
Do not add unsupported claims or subtitles.

2. VIDEO HOOK
Create an engaging but completely source-supported opening.
Do not use phrases such as "across the globe", "no longer a concept
for the future", or similar claims unless they appear in the source.

3. COMPLETE NARRATION
Write natural, professional spoken narration.
Keep it concise and factual.
Remove unnecessary corporate buzzwords and filler.

4. STORYBOARD
Create 6 to 8 well-paced scenes.

For every scene provide:
- Scene number
- Scene title
- Duration in seconds
- Narration
- Visual description
- Camera/animation direction
- On-screen text
- Key fact/message
- Transition

5. VISUAL STORYTELLING
Avoid making every scene a collection of icons.
Use a mixture of:
- realistic business visuals
- relevant illustrations
- motion graphics
- simple diagrams
- icons only when useful

Every visual must match the narration.

6. TIMING
Make scene durations realistic for the amount of narration.
Avoid dead air.
Target an overall video duration of approximately 45–60 seconds
unless the source genuinely requires more time.

7. ON-SCREEN TEXT
Keep text short and readable.
Use only information supported by the source.

8. CONCLUSION
The conclusion must be supported by the source.
Do not introduce new claims such as "successfully leverage the true
power of AI" unless supported by the source.

9. FACT CHECK
At the end, provide a short list confirming the important facts used
and their relationship to the source.

FINAL QUALITY RULE:
The result should feel like a professional explainer video,
not a PowerPoint converted into a video.

Return ONLY the final video plan.
"""

final_response = client.interactions.create(
    model="gemini-3.5-flash",
    input=final_prompt
)

print("\n")
print("========== FINAL POLISHED VIDEO PLAN ==========")
print(final_response.output_text)

final_plan = final_response.output_text

print("\nFinal video plan saved for video generation.")

# -----------------------------
# 6. Extract Scene Information
# -----------------------------

scene_prompt = f"""
You are a video production assistant.

Read the FINAL VIDEO PLAN below and extract the scenes
for automatic video generation.

FINAL VIDEO PLAN:
{final_plan}

Return ONLY valid JSON.

Use this exact format:

{{
  "title": "video title",
  "scenes": [
    {{
      "scene_number": 1,
      "scene_title": "scene title",
      "duration": 6,
      "narration": "spoken narration",
      "visual": "visual description",
      "on_screen_text": "short text"
    }}
  ]
}}

IMPORTANT:
- Keep the narration exactly based on the final plan.
- Do not invent information.
- Duration must be a number in seconds.
- Include every scene.
- Return JSON only.
"""

scene_response = client.interactions.create(
    model="gemini-3.5-flash",
    input=scene_prompt
)

scene_data = scene_response.output_text

print("\n")
print("========== SCENE DATA ==========")
print(scene_data)
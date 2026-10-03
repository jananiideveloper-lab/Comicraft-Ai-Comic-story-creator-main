import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.5-flash-lite"


def generate_story(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style,
    outline
):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Create a simple and connected 5-panel comic story.

Story prompt:
{story_prompt}

Character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Comic outline:
{json.dumps(outline, indent=2)}

Return ONLY valid JSON.

Return exactly 5 objects in this format:

[
  {{
    "panel_number": 1,
    "scene": "Describe the scene simply",
    "action": "Describe what the character does",
    "dialogue": "Character dialogue",
    "narration": "Short narration",
    "image_prompt": "Simple image generation prompt"
  }}
]

Rules:
- Exactly 5 panels
- Panel 1 should start the story
- Panel 2 should continue Panel 1
- Panel 3 should continue naturally
- Panel 4 should move toward the ending
- Panel 5 should give a simple ending
- Keep it child-friendly
- Use simple English
- Do not use markdown
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    data = json.loads(text)

    if isinstance(data, dict) and "comic" in data:
        data = data["comic"]

    if not isinstance(data, list):
        raise ValueError("Gemini did not return a valid story.")

    return data
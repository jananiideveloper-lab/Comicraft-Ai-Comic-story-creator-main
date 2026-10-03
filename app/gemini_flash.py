import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.5-flash-lite"


def generate_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Create a simple 5-panel comic outline.

Story: {story_prompt}
Character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY JSON.

Format:
[
  {{
    "panel_number": 1,
    "title": "Panel title",
    "scene_description": "Simple scene description",
    "image_prompt": "Simple image prompt"
  }}
]

Create exactly 5 panels.
Keep the story connected and child-friendly.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    text = response.text.strip()

    # Remove ```json if Gemini adds it
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    data = json.loads(text)

    # Sometimes Gemini returns {"comic": [...]}
    if isinstance(data, dict) and "comic" in data:
        data = data["comic"]

    if not isinstance(data, list):
        raise ValueError("Gemini did not return a panel list.")

    return data
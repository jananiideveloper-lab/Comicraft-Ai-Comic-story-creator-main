import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

PANELS_DIR = Path("static/panels")
PANELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "black-forest-labs/FLUX.1-schnell"


def generate_image(prompt, panel_number, art_style="comic book"):

    hf_key = os.getenv("HF_API_KEY")

    if not hf_key:
        raise RuntimeError("HF_API_KEY is missing from .env")

    try:
        client = InferenceClient(
            api_key=hf_key,
            provider="auto"
        )

        full_prompt = f"""
Create a colorful children's comic illustration.

{prompt}

Art style: {art_style}

Requirements:
- colorful cartoon illustration
- child-friendly
- clear characters
- expressive faces
- clean comic style
- no text
"""

        print(f"Generating AI image for Panel {panel_number}...")

        image = client.text_to_image(
            full_prompt,
            model=MODEL
        )

        file_path = PANELS_DIR / f"panel_{panel_number}.png"

        image.save(file_path)

        print(f"Panel {panel_number} image saved.")

        return f"/static/panels/panel_{panel_number}.png"

    except Exception as error:
        print(f"Image generation failed for Panel {panel_number}: {error}")

        return None
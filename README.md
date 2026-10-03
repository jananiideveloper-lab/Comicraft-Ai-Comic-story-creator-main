# ComicCraft - AI Comic Story Creator using Gemini Models

This project follows the supplied ComicCraft document: model selection, architecture, core AI functions, FastAPI routes, frontend, PDF export, testing and local deployment.

## Windows
Open this folder in VS Code Terminal and run:

python -m venv env
env\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload

Then open http://127.0.0.1:8000

Add your GEMINI_API_KEY to `.env`. HF_API_KEY is optional; without it, the project creates clean local panel placeholders so the full story/PDF flow can still be demonstrated.

The supplied document names Gemini 1.5 Flash/Pro. Those are legacy model IDs now, so this runnable project uses the current `gemini-3.8-flash` for text generation. The document's `runwayml/stable-diffusion-v1-5` remains the default image model setting.

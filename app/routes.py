from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates

from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout


router = APIRouter()
templates = Jinja2Templates(directory="templates")

EXPORT_DIR = Path("static/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def create_pdf(panels, filename):
    """
    Create a simple PDF containing all comic panels.
    """

    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in panels:

        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 18)
        pdf.cell(
            0,
            12,
            f"Comic Panel {panel['panel_number']}",
            ln=True,
            align="C"
        )

        pdf.ln(5)

        # Image
        image_path = panel.get("image_path")

        if image_path:
            local_image = image_path.lstrip("/")

            if Path(local_image).exists():
                try:
                    pdf.image(
                        local_image,
                        x=20,
                        y=35,
                        w=170
                    )
                    pdf.ln(95)
                except Exception as image_error:
                    print(
                        f"PDF image error for Panel "
                        f"{panel['panel_number']}: {image_error}"
                    )

        # Scene
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Scene:", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(
            0,
            7,
            str(panel.get("scene", ""))
        )

        pdf.ln(3)

        # Action
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Action:", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(
            0,
            7,
            str(panel.get("action", ""))
        )

        pdf.ln(3)

        # Narration
        if panel.get("narration"):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Narration:", ln=True)

            pdf.set_font("Arial", "", 11)
            pdf.multi_cell(
                0,
                7,
                str(panel.get("narration", ""))
            )

            pdf.ln(3)

        # Dialogue
        if panel.get("dialogue"):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Dialogue:", ln=True)

            pdf.set_font("Arial", "", 11)
            pdf.multi_cell(
                0,
                7,
                str(panel.get("dialogue", ""))
            )

    output_path = EXPORT_DIR / filename
    pdf.output(str(output_path))

    return filename


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@router.post("/generate")
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...)
):
    try:

        # -----------------------------------
        # STEP 1: Generate outline
        # -----------------------------------

        outline = generate_outline(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style
        )

        # -----------------------------------
        # STEP 2: Generate full story
        # -----------------------------------

        story = generate_story(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style,
            outline
        )

        # -----------------------------------
        # STEP 3: Generate AI images
        # -----------------------------------

        panels = []

        for i, panel in enumerate(story, start=1):

            image_prompt = panel.get(
                "image_prompt",
                panel.get("scene", "")
            )

            image_path = generate_image(
                image_prompt,
                panel_number=i,
                art_style=art_style
            )

            panels.append({
                "panel_number": i,
                "scene": panel.get("scene", ""),
                "action": panel.get("action", ""),
                "dialogue": panel.get("dialogue", ""),
                "narration": panel.get("narration", ""),
                "image_path": image_path
            })

        # -----------------------------------
        # STEP 4: Build comic layout
        # -----------------------------------

        comic = build_comic_layout(
            outline,
            story
        )

        # -----------------------------------
        # STEP 5: Create PDF
        # -----------------------------------

        pdf_filename = "comiccraft_comic.pdf"

        create_pdf(
            panels,
            pdf_filename
        )

        # Add PDF filename to comic data
        if isinstance(comic, dict):
            comic["pdf_filename"] = pdf_filename
        else:
            comic = {
                "pdf_filename": pdf_filename
            }

        # -----------------------------------
        # STEP 6: Show comic preview
        # -----------------------------------

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "comic": comic,
                "panels": panels
            }
        )

    except Exception as e:

        print("Comic generation error:", e)

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(e)
            }
        )


@router.post("/generate-comic/json")
async def generate_comic_json(data: dict):

    try:

        story_prompt = data.get(
            "story_prompt",
            ""
        )

        character_name = data.get(
            "character_name",
            ""
        )

        setting = data.get(
            "setting",
            ""
        )

        tone = data.get(
            "tone",
            ""
        )

        art_style = data.get(
            "art_style",
            ""
        )

        # Generate outline
        outline = generate_outline(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style
        )

        # Generate story
        story = generate_story(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style,
            outline
        )

        return JSONResponse({
            "success": True,
            "outline": outline,
            "story": story
        })

    except Exception as e:

        return JSONResponse(
            {
                "success": False,
                "error": str(e)
            },
            status_code=500
        )


@router.get("/test-image")
async def test_image(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="test_image.html",
        context={}
    )


@router.get("/download/{filename}")
async def download(filename: str):

    file_path = EXPORT_DIR / filename

    if file_path.exists():

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf"
        )

    return JSONResponse(
        {
            "success": False,
            "error": "File not found"
        },
        status_code=404
    )


@router.get("/export-success")
async def export_success(
    request: Request,
    filename: str = ""
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "filename": filename
        }
    )
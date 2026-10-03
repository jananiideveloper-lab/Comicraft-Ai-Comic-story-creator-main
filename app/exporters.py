import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image

EXPORT_DIR = "static/exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

def _clean(text):
    return (text or "").encode("latin-1", "replace").decode("latin-1")

def save_pdf(layout):
    filename = f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(EXPORT_DIR, filename)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, _clean(f"Panel {panel['panel_number']}: {panel['title']}"))
        local = panel["image_path"].lstrip("/")
        if os.path.exists(local):
            try:
                img = Image.open(local)
                w, h = img.size
                scale = min(175/w, 105/h)
                pdf.image(local, w=w*scale, h=h*scale)
            except Exception:
                pass
        for heading, value in [
            ("Scene", panel["scene_description"]),
            ("Caption", panel["caption"]),
            ("Narration", panel["narration"]),
            ("Dialogue", panel["dialogue"])]:
            pdf.set_font("Helvetica", "B", 12); pdf.multi_cell(0, 7, heading)
            pdf.set_font("Helvetica", "", 11); pdf.multi_cell(0, 7, _clean(value))
    pdf.output(path)
    return f"/download/{filename}"

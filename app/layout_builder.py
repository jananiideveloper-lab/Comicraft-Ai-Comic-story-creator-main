def build_comic_layout(panels, story):
    story_map = {int(x["panel_number"]): x for x in story}
    result = []
    for panel in panels:
        n = int(panel["panel_number"])
        s = story_map.get(n, {})
        result.append({
            "panel_number": n, "title": panel.get("title", f"Panel {n}"),
            "image_path": panel.get("image_path", ""),
            "scene_description": panel.get("scene_description", ""),
            "caption": s.get("caption", ""), "narration": s.get("narration", ""),
            "dialogue": s.get("dialogue", ""),
            "image_prompt": panel.get("image_prompt", "")
        })
    return result

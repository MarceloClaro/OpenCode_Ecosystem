import os
import re
import json
import shutil
from typing import Any, Dict, List, Optional

PERSONAS_DIR = "personas"
PERSONAS_MEDIA_DIR = "personas_media"

os.makedirs(PERSONAS_DIR, exist_ok=True)
os.makedirs(PERSONAS_MEDIA_DIR, exist_ok=True)

def list_personas() -> List[str]:
    return sorted([f[:-5] for f in os.listdir(PERSONAS_DIR) if f.endswith(".json")])

def slugify(name: str) -> str:
    s = (name or "").lower().strip()
    s = re.sub(r"[^a-z0-9\-_. ]", "", s)
    s = s.replace(" ", "_")
    return s[:80] or "persona"

def unique_slug(base_slug: str) -> str:
    slug = base_slug
    i = 2
    while os.path.exists(os.path.join(PERSONAS_DIR, f"{slug}.json")):
        slug = f"{base_slug}_{i}"
        i += 1
    return slug

def save_persona_atomic(slug: str, data: Dict[str, Any]) -> str:
    path = os.path.join(PERSONAS_DIR, f"{slug}.json")
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
    return path

def load_persona(slug: str) -> Optional[Dict[str, Any]]:
    path = os.path.join(PERSONAS_DIR, f"{slug}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_avatar_file(slug: str, uploaded_path: Optional[str]) -> Optional[str]:
    if not uploaded_path:
        return None
    ext = os.path.splitext(uploaded_path)[1].lower() or ".png"
    dest = os.path.join(PERSONAS_MEDIA_DIR, f"{slug}{ext}")
    try:
        from shutil import copyfile
        copyfile(uploaded_path, dest)
        return dest
    except Exception:
        return None

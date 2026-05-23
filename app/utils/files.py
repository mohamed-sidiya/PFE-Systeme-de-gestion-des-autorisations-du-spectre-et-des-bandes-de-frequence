from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError("Type de fichier non autorisé.")
    original = secure_filename(file_storage.filename)
    ext = original.rsplit(".", 1)[1].lower()
    filename = f"{uuid4().hex}.{ext}"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / filename
    file_storage.save(destination)
    return {
        "nom_original": original,
        "nom_stockage": filename,
        "chemin": f"uploads/{filename}",
        "mime_type": file_storage.mimetype,
        "taille_octets": destination.stat().st_size,
    }

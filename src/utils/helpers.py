import json
import os
from datetime import datetime
from typing import Any


def save_json(data: Any, filepath: str) -> str:
    """Sauvegarder des données en JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def get_file_size(filepath: str) -> str:
    """Obtenir la taille du fichier de manière lisible"""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def get_timestamp(include_time: bool = False) -> str:
    """Obtenir un timestamp formaté pour les fichiers"""
    if include_time:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    return datetime.now().strftime("%Y%m%d")


def ensure_dir(directory: str) -> str:
    """Créer un dossier s'il n'existe pas"""
    os.makedirs(directory, exist_ok=True)
    return directory
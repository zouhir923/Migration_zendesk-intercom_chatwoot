import json
import os
import re
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

def clean_markdown_formatting(text: str) -> str:
    """Nettoyer le formatage Markdown - version améliorée"""
    
    text = re.sub(r'\*{3,}([^*]+?)\*{3,}', r'**\1**', text)
    
    text = re.sub(r'\*\*\s+([^*]+?)\s+\*\*', r'**\1**', text)
    text = re.sub(r'\*\s+([^*]+?)\s+\*', r'*\1*', text)
    
    text = re.sub(r'\*\*([^*]+?)\*\*<br>', r'**\1** <br>', text)
    text = re.sub(r'<br>\*\*([^*]+?)\*\*', r'<br> **\1**', text)
    
    text = re.sub(r'\*([^*]+?)\*<br>', r'*\1* <br>', text)
    text = re.sub(r'<br>\*([^*]+?)\*', r'<br> *\1*', text)
    
    text = re.sub(r'\*\*([^*]+?),\s*\*\*', r'**\1,**', text)
    text = re.sub(r'\*\*([^*]+?)\.\s*\*\*', r'**\1.**', text)
    
    text = re.sub(r'(?<!<br)\s{2,}(?!>)', ' ', text)
    
    text = re.sub(r'\s*<br\s*/?>\s*', '<br>', text)
    
    text = re.sub(r'\*\*([^*]+?)\*\*\s*(\[.*?\]\(.*?\))', r'**\1** \2', text)
    
    lines = text.split('<br>')
    cleaned_lines = [line.strip() for line in lines]
    text = '<br>'.join(cleaned_lines)
    
    return text

def html_to_markdown(html_content: str) -> str:
    """Convertir HTML simple en Markdown en gardant les <br> pour les sauts de ligne"""
    if not html_content:
        return ""
    
    text = html_content
    
    # Convert <img> tags to Markdown format FIRST (before removing other HTML tags)
    # Handle images with alt text
    text = re.sub(r'<img[^>]*\ssrc=["\']([^"\']*)["\'][^>]*\salt=["\']([^"\']*)["\'][^>]*/?>', r'![\2](\1)', text)
    # Handle images without alt text or with alt before src
    text = re.sub(r'<img[^>]*\salt=["\']([^"\']*)["\'][^>]*\ssrc=["\']([^"\']*)["\'][^>]*/?>', r'![\1](\2)', text)
    # Handle images with only src (no alt text)
    text = re.sub(r'<img[^>]*\ssrc=["\']([^"\']*)["\'][^>]*/?>', r'![image](\1)', text)
    
    # Convert links
    text = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r' [\2](\1) ', text)
    
    def format_strong(match):
        content = match.group(1).strip()
        return f'**{content}**' if content else ''
    
    def format_em(match):
        content = match.group(1).strip()
        return f'*{content}*' if content else ''
    
    text = re.sub(r'<strong>(.*?)</strong>', format_strong, text)
    text = re.sub(r'<b>(.*?)</b>', format_strong, text)
    text = re.sub(r'<em>(.*?)</em>', format_em, text)
    text = re.sub(r'<i>(.*?)</i>', format_em, text)
    
    text = re.sub(r'<p[^>]*>', '<br>', text)
    text = re.sub(r'</p>', '<br>', text)
    text = re.sub(r'<div[^>]*>', '<br>', text)
    text = re.sub(r'</div>', '<br>', text)
    
    # Remove all other HTML tags except <br>
    text = re.sub(r'<(?!br\s*/?)[^>]+>', '', text)
    
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    
    text = re.sub(r'[ \t]+', ' ', text)
    
    text = re.sub(r'(<br\s*/?>\s*){3,}', '<br><br>', text)
    
    text = clean_markdown_formatting(text)
    
    text = text.strip()
    return text

def format_date_header(iso_date: str) -> str:
    """Formater une date ISO en en-tête français"""
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return f"Date originale: {dt.strftime('%d/%m/%Y %H:%M')}"
    except:
        return f"Date originale: {iso_date}"
import json
import os
from typing import Dict, List
from src.utils.helpers import save_json, get_file_size, get_timestamp
from configs.config import INTERCOM_OUTPUT_DIR


def intercom_clean_articles() -> str:
    """Nettoyer les articles Intercom pour Chatwoot"""
    date_today = get_timestamp()
    origin_file = f"{INTERCOM_OUTPUT_DIR}/origin_export/intercom_articles_{date_today}.json"
    
    print(f"Nettoyage articles: {os.path.basename(origin_file)}")
    
    with open(origin_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles = data.get('articles', [])
    cleaned_articles = []
    
    for article in articles:
        # Extraire les tags
        tags_data = article.get('tags', {})
        tags = []
        if isinstance(tags_data, dict) and 'tags' in tags_data:
            tags = [tag.get('name', '') for tag in tags_data.get('tags', [])]
        
        cleaned_article = {
            'id': article.get('id'),
            'title': article.get('title'),
            'description': article.get('description'),
            'content': article.get('body'),
            'author_id': article.get('author_id'),
            'state': article.get('state'),
            'parent_id': article.get('parent_id'),
            'parent_type': article.get('parent_type'),
            'created_at': article.get('created_at'),
            'updated_at': article.get('updated_at'),
            'tags': tags,
            'url': article.get('url')
        }
        cleaned_articles.append(cleaned_article)
    
    cleaned_data = {
        'metadata': {
            'cleaned_at': get_timestamp(include_time=True),
            'count': len(cleaned_articles),
            'source': 'intercom_articles'
        },
        'articles': cleaned_articles
    }
    
    output_dir = f"{INTERCOM_OUTPUT_DIR}/clean_export_data"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"intercom_articles_{date_today}.json"
    filepath = os.path.join(output_dir, filename)
    save_json(cleaned_data, filepath)
    
    print(f"Articles nettoyés: {filename} ({get_file_size(filepath)}) - {len(cleaned_articles)} items")
    return filepath


def test_intercom_clean_articles():
    """Test de nettoyage des articles"""
    intercom_clean_articles()


if __name__ == "__main__":
    test_intercom_clean_articles()
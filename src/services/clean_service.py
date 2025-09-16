import json
import os
from typing import Dict, List
from src.utils.helpers import save_json, get_file_size, get_timestamp
from configs.config import ZENDESK_OUTPUT_DIR


def zendesk_clean_articles() -> str:
    """Nettoyer les articles Zendesk pour Chatwoot"""
    # Construire le chemin automatiquement
    date_today = get_timestamp()  
    origin_file = f"{ZENDESK_OUTPUT_DIR}/origin_export/zendesk_articles_{date_today}.json"
    
    print(f"Nettoyage articles: {os.path.basename(origin_file)}")
    
    # Charger les données
    with open(origin_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles = data.get('articles', [])
    cleaned_articles = []
    
    for article in articles:
        cleaned_article = {
            'id': article.get('id'),
            'title': article.get('title'),
            'content': article.get('body'),
            'author_id': article.get('author_id'),
            'created_at': article.get('created_at'),
            'updated_at': article.get('updated_at'),
            'locale': article.get('locale'),
            'category_id': article.get('section_id')
        }
        cleaned_articles.append(cleaned_article)
    
    # Structure finale
    cleaned_data = {
        'metadata': {
            'cleaned_at': get_timestamp(include_time=True),
            'count': len(cleaned_articles),
            'source': 'zendesk_articles'
        },
        'articles': cleaned_articles
    }
    
    # Sauvegarder les données nettoyées
    output_dir = f"{ZENDESK_OUTPUT_DIR}/clean_export_data"
    
    filename = f"zendesk_articles_{date_today}.json"
    filepath = os.path.join(output_dir, filename)
    save_json(cleaned_data, filepath)
    
    print(f"Articles nettoyés: {filename} ({get_file_size(filepath)}) - {len(cleaned_articles)} items")
    return filepath


def test_zendesk_clean_articles():
    """Test de nettoyage des articles"""
    zendesk_clean_articles()


if __name__ == "__main__":
    test_zendesk_clean_articles()
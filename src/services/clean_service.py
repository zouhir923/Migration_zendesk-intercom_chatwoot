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

import json
import os
from typing import Dict, List
from src.utils.helpers import save_json, get_file_size, get_timestamp
from configs.config import ZENDESK_OUTPUT_DIR


def zendesk_clean_articles() -> str:
    """Nettoyer les articles Zendesk pour Chatwoot"""
    # Construire le chemin automatiquement
    date_today = get_timestamp()  # Sans include_time pour avoir seulement la date
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
    
    # Sauvegarde avec nom automatique
    output_dir = f"{ZENDESK_OUTPUT_DIR}/clean_export_data"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"zendesk_articles_{date_today}.json"
    filepath = os.path.join(output_dir, filename)
    save_json(cleaned_data, filepath)
    
    print(f"Articles nettoyés: {filename} ({get_file_size(filepath)}) - {len(cleaned_articles)} items")
    return filepath

def zendesk_clean_macros() -> str:
    """Nettoyer les macros Zendesk pour Chatwoot"""
    date_today = get_timestamp()
    origin_file = f"{ZENDESK_OUTPUT_DIR}/origin_export/zendesk_macros_{date_today}.json"
    
    print(f"Nettoyage macros: {os.path.basename(origin_file)}")
    
    with open(origin_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    macros = data.get('macros', [])
    cleaned_macros = []
    
    for macro in macros:
        # Structurer les actions
        actions = macro.get('actions', [])
        structured_actions = {}
        
        for action in actions:
            field = action.get('field')
            value = action.get('value')
            
            if field == 'comment_value_html':
                structured_actions['comment'] = value
            elif field == 'status':
                structured_actions['status'] = value
            elif field == 'assignee_id':
                structured_actions['assignee_id'] = value
            elif field == 'group_id':
                structured_actions['group_id'] = value
            else:
                # Garder les autres actions telles quelles
                structured_actions[field] = value
        
        cleaned_macro = {
            'id': macro.get('id'),
            'title': macro.get('title'),
            'raw_title': macro.get('raw_title'),
            'description': macro.get('description'),
            'active': macro.get('active'),
            'default': macro.get('default'),
            'position': macro.get('position'),
            'actions': structured_actions,
            'restriction': macro.get('restriction'),
            'created_at': macro.get('created_at'),
            'updated_at': macro.get('updated_at')
        }
        cleaned_macros.append(cleaned_macro)
    
    cleaned_data = {
        'metadata': {
            'cleaned_at': get_timestamp(include_time=True),
            'count': len(cleaned_macros),
            'source': 'zendesk_macros'
        },
        'macros': cleaned_macros
    }
    
    output_dir = f"{ZENDESK_OUTPUT_DIR}/clean_export_data"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"zendesk_macros_{date_today}.json"
    filepath = os.path.join(output_dir, filename)
    save_json(cleaned_data, filepath)
    
    print(f"Macros nettoyées: {filename} ({get_file_size(filepath)}) - {len(cleaned_macros)} items")
    return filepath

def test_zendesk_clean():
    """Test de nettoyage des données Zendesk"""
    # zendesk_clean_articles()
    zendesk_clean_macros()


if __name__ == "__main__":
    test_zendesk_clean()
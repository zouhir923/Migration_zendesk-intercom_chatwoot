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

def intercom_clean_contacts() -> str:
    """Nettoyer les contacts Intercom pour Chatwoot"""
    date_today = get_timestamp()
    origin_file = f"{INTERCOM_OUTPUT_DIR}/origin_export/intercom_contacts_{date_today}.json"
    
    print(f"Nettoyage contacts: {os.path.basename(origin_file)}")
    
    with open(origin_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    contacts = data.get('contacts', [])
    cleaned_contacts = []
    
    for contact in contacts:
        # Extraire location
        location = contact.get('location', {})
        
        # Extraire tags
        tags_data = contact.get('tags', {})
        tags = []
        if isinstance(tags_data, dict) and 'data' in tags_data:
            tags = [tag.get('name', '') for tag in tags_data.get('data', [])]
        
        # Extraire companies IDs
        companies_data = contact.get('companies', {})
        company_ids = []
        if isinstance(companies_data, dict) and 'data' in companies_data:
            company_ids = [comp.get('id', '') for comp in companies_data.get('data', [])]
        
        cleaned_contact = {
            'id': contact.get('id'),
            'external_id': contact.get('external_id'),
            'name': contact.get('name'),
            'email': contact.get('email'),
            'phone': contact.get('phone'),
            'avatar': contact.get('avatar'),
            'role': contact.get('role'),
            'created_at': contact.get('created_at'),
            'updated_at': contact.get('updated_at'),
            'signed_up_at': contact.get('signed_up_at'),
            'last_seen_at': contact.get('last_seen_at'),
            'last_replied_at': contact.get('last_replied_at'),
            'last_contacted_at': contact.get('last_contacted_at'),
            'browser': contact.get('browser'),
            'browser_language': contact.get('browser_language'),
            'os': contact.get('os'),
            'location': {
                'country': location.get('country'),
                'city': location.get('city'),
                'country_code': location.get('country_code')
            },
            'tags': tags,
            'company_ids': company_ids,
            'unsubscribed_from_emails': contact.get('unsubscribed_from_emails'),
            'custom_attributes': contact.get('custom_attributes', {})
        }
        cleaned_contacts.append(cleaned_contact)
    
    cleaned_data = {
        'metadata': {
            'cleaned_at': get_timestamp(include_time=True),
            'count': len(cleaned_contacts),
            'source': 'intercom_contacts'
        },
        'contacts': cleaned_contacts
    }
    
    output_dir = f"{INTERCOM_OUTPUT_DIR}/clean_export_data"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"intercom_contacts_{date_today}.json"
    filepath = os.path.join(output_dir, filename)
    save_json(cleaned_data, filepath)
    
    print(f"Contacts nettoyés: {filename} ({get_file_size(filepath)}) - {len(cleaned_contacts)} items")
    return filepath

def intercom_clean_conversations() -> str:
    """Nettoyer les conversations Intercom pour Chatwoot"""
    date_today = get_timestamp()
    origin_file = f"{INTERCOM_OUTPUT_DIR}/origin_export/intercom_conversations_{date_today}.json"
    
    print(f"Nettoyage conversations: {os.path.basename(origin_file)}")
    
    with open(origin_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    conversations = data.get('conversations', [])
    cleaned_conversations = []
    
    for conversation in conversations:
        # Extraire contact principal
        contacts_data = conversation.get('contacts', {}).get('contacts', [])
        contact_id = contacts_data[0].get('id') if contacts_data else None
        
        # Extraire source info
        source = conversation.get('source', {})
        source_author = source.get('author', {})
        
        # Nettoyer les messages
        messages = conversation.get('messages', [])
        cleaned_messages = []
        
        for message in messages:
            # Garder seulement les vrais messages (comment)
            if message.get('part_type') == 'comment':
                author = message.get('author', {})
                cleaned_message = {
                    'id': message.get('id'),
                    'body': message.get('body'),
                    'author_id': author.get('id'),
                    'author_type': author.get('type'),
                    'author_name': author.get('name'),
                    'author_email': author.get('email'),
                    'created_at': message.get('created_at'),
                    'attachments': message.get('attachments', [])
                }
                cleaned_messages.append(cleaned_message)
        
        # Extraire tags
        tags_data = conversation.get('tags', {})
        tags = []
        if isinstance(tags_data, dict) and 'tags' in tags_data:
            tags = [tag.get('name', '') for tag in tags_data.get('tags', [])]
        
        cleaned_conversation = {
            'id': conversation.get('id'),
            'title': conversation.get('title'),
            'state': conversation.get('state'),
            'open': conversation.get('open'),
            'priority': conversation.get('priority'),
            'contact_id': contact_id,
            'admin_assignee_id': conversation.get('admin_assignee_id'),
            'team_assignee_id': conversation.get('team_assignee_id'),
            'created_at': conversation.get('created_at'),
            'updated_at': conversation.get('updated_at'),
            'waiting_since': conversation.get('waiting_since'),
            'tags': tags,
            'source': {
                'subject': source.get('subject'),
                'body': source.get('body'),
                'author_name': source_author.get('name'),
                'author_email': source_author.get('email')
            },
            'messages': cleaned_messages,
            'message_count': len(cleaned_messages)
        }
        cleaned_conversations.append(cleaned_conversation)
    
    cleaned_data = {
        'metadata': {
            'cleaned_at': get_timestamp(include_time=True),
            'count': len(cleaned_conversations),
            'source': 'intercom_conversations'
        },
        'conversations': cleaned_conversations
    }
    
    output_dir = f"{INTERCOM_OUTPUT_DIR}/clean_export_data"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"intercom_conversations_{date_today}.json"
    filepath = os.path.join(output_dir, filename)
    save_json(cleaned_data, filepath)
    
    print(f"Conversations nettoyées: {filename} ({get_file_size(filepath)}) - {len(cleaned_conversations)} items")
    return filepath

def intercom_clean_all() -> Dict[str, str]:
    """Nettoyer toutes les données Intercom"""
    print("Nettoyage complet Intercom")
    print("=" * 25)
    
    files = {}
    files['conversations'] = intercom_clean_conversations()
    files['contacts'] = intercom_clean_contacts()
    files['articles'] = intercom_clean_articles()
    
    print(f"\nNettoyage terminé - {len(files)} fichiers créés")
    return files


# def test_intercom_clean_articles():
#     """Test de nettoyage des articles"""
#     # intercom_clean_articles()
#     # intercom_clean_contacts()
#     # intercom_clean_conversations()
#     intercom_clean_all()


# if __name__ == "__main__":
#     test_intercom_clean_articles()
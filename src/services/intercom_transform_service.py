import json
import os
from src.utils.helpers import save_json, get_file_size, get_timestamp, html_to_markdown, format_date_header
from configs.config import INTERCOM_OUTPUT_DIR


def intercom_transform_conversations() -> str:
    """Transformer les conversations Intercom pour Chatwoot"""
    date_today = get_timestamp()
    input_file = f"{INTERCOM_OUTPUT_DIR}/clean_export_data/intercom_conversations_clean_{date_today}.json"
    
    print(f"Transformation conversations: {os.path.basename(input_file)}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    conversations = data.get('conversations', [])
    transformed_conversations = []
    
    for conversation in conversations:
        messages = conversation.get('messages', [])
        transformed_messages = []
        
        for message in messages:
            body = message.get('body', '')
            if body:
                markdown_content = html_to_markdown(body)
            else:
                markdown_content = ""
            
            created_at = message.get('created_at', '')
            if created_at:
                try:
                    from datetime import datetime
                    iso_date = datetime.fromtimestamp(created_at).isoformat()
                    date_header = format_date_header(iso_date)
                except:
                    date_header = f"Date originale: {created_at}"
            else:
                date_header = "Date originale: inconnue"
            
            if markdown_content:
                final_content = f"{date_header}<br><br>{markdown_content}"
            else:
                final_content = date_header
            
            transformed_message = {
                'id': message.get('id'),
                'author_id': message.get('author_id'),
                'author_type': message.get('author_type'),
                'message_type': message.get('message_type'),
                'author_name': message.get('author_name'),
                'author_email': message.get('author_email'),
                'content': final_content,
                'created_at': message.get('created_at'),
                'attachments': message.get('attachments', [])
            }
            transformed_messages.append(transformed_message)
        
        source = conversation.get('source', {})
        source_body = source.get('body', '')
        created_at = conversation.get('created_at', '')
        
        if source_body:
            markdown_description = html_to_markdown(source_body)
            
            if created_at:
                try:
                    from datetime import datetime
                    iso_date = datetime.fromtimestamp(created_at).isoformat()
                    description_header = format_date_header(iso_date)
                except:
                    description_header = f"Date originale: {created_at}"
            else:
                description_header = "Date originale: inconnue"
            
            transformed_description = f"{description_header}<br><br>{markdown_description}"
        else:
            transformed_description = ""
        
        source_subject = source.get('subject', '')
        if source_subject:
            clean_subject = html_to_markdown(source_subject).replace('<br>', ' ').strip()
        else:
            clean_subject = conversation.get('title', '')
        
        transformed_conversation = {
            'id': conversation.get('id'),
            'title': clean_subject,
            'state': conversation.get('state'),
            'open': conversation.get('open'),
            'priority': conversation.get('priority'),
            'contact_id': conversation.get('contact_id'),
            'admin_assignee_id': conversation.get('admin_assignee_id'),
            'team_assignee_id': conversation.get('team_assignee_id'),
            'created_at': conversation.get('created_at'),
            'updated_at': conversation.get('updated_at'),
            'waiting_since': conversation.get('waiting_since'),
            'tags': conversation.get('tags', []),
            'source': {
                'author_name': source.get('author_name'),
                'author_email': source.get('author_email'),
                'description': transformed_description,
                
            },
            'messages': transformed_messages,
            'message_count': conversation.get('message_count', len(transformed_messages))
        }
        transformed_conversations.append(transformed_conversation)
    
    # Structure finale
    transformed_data = {
        'metadata': {
            'transformed_at': get_timestamp(include_time=True),
            'count': len(transformed_conversations),
            'source': 'intercom_conversations_cleaned',
            'transformations': ['html_to_markdown', 'date_headers_added', 'unix_timestamps_converted', 'markdown_cleaned']
        },
        'conversations': transformed_conversations
    }
    
    # Sauvegarde
    output_dir = f"{INTERCOM_OUTPUT_DIR}/transformed_data"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"intercom_conversations_transformed_{date_today}.json"
    filepath = os.path.join(output_dir, filename)
    save_json(transformed_data, filepath)
    
    print(f"Conversations transformées: {filename} ({get_file_size(filepath)}) - {len(transformed_conversations)} items")
    return filepath


def test_intercom_transform():
    """Test de transformation"""
    intercom_transform_conversations()


if __name__ == "__main__":
    test_intercom_transform()
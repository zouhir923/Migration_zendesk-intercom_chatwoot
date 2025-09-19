import json
import os
from typing import Dict, List, Tuple
from src.utils.helpers import save_json, get_file_size, get_timestamp
from configs.config import ZENDESK_OUTPUT_DIR, INTERCOM_OUTPUT_DIR, CHATWOOT_OUTPUT_DIR


def load_transformed_data() -> Tuple[List[Dict], List[Dict]]:
    """Charger les conversations/tickets transformés"""
    date = get_timestamp()
    
    zendesk_path = f"{ZENDESK_OUTPUT_DIR}/transformed_data/zendesk_tickets_transformed_{date}.json"
    intercom_path = f"{INTERCOM_OUTPUT_DIR}/transformed_data/intercom_conversations_transformed_{date}.json"
    
    with open(zendesk_path, 'r', encoding='utf-8') as f:
        zendesk_data = json.load(f).get('tickets', [])
    
    with open(intercom_path, 'r', encoding='utf-8') as f:
        intercom_data = json.load(f).get('conversations', [])
    
    print(f"Chargé: {len(zendesk_data)} tickets, {len(intercom_data)} conversations")
    return zendesk_data, intercom_data


def load_contact_index() -> Tuple[Dict, Dict]:
    """Charger index des contacts pour mapping rapide"""
    date = get_timestamp()
    contacts_path = f"{CHATWOOT_OUTPUT_DIR}/chatwoot_contacts_prepared_{date}.json"
    
    with open(contacts_path, 'r', encoding='utf-8') as f:
        contacts = json.load(f).get('contacts', [])
    
    zendesk_index = {}
    intercom_index = {}
    
    for contact in contacts:
        if contact.get('zendesk_id'):
            zendesk_index[contact['zendesk_id']] = contact['email']
        if contact.get('intercom_id'):
            intercom_index[contact['intercom_id']] = contact['email']
    
    print(f"Index contacts: {len(zendesk_index)} Zendesk, {len(intercom_index)} Intercom")
    return zendesk_index, intercom_index

def format_conversation(data: Dict, source: str, contact_email: str) -> Dict:
    """Formater conversation selon source"""
    messages = []
    
    if source == "zendesk":
        for comment in data.get('comments', []):
            # Déterminer si c'est un message client ou agent
            # Si author_id = requester_id, c'est le client
            is_client_message = comment.get('author_id') == data.get('requester_id')
            
            messages.append({
                'content': comment['content'].replace('<br>', '\n'),
                'message_type': 'incoming' if is_client_message else 'outgoing',
                'author_name': 'Client' if is_client_message else 'Agent',
                'created_at': comment.get('created_at'),
                'attachments': comment.get('attachments', [])
            })
        
        return {
            'contact_email': contact_email,
            'title': data.get('subject', 'Sans titre'),
            'status': 'resolved' if data.get('status') in ['solved', 'closed'] else data.get('status'),
            'zendesk_ticket_id': data.get('id'),
            'intercom_conversation_id': None,
            'created_at': data.get('created_at'),
            'tags': data.get('tags', []),
            'additional_attributes': {
                'priority': data.get('priority'),
                'type': data.get('type'),
                'assignee_id': data.get('assignee_id'),
                'group_id': data.get('group_id')
            },
            'messages': messages
        }
    
    else:  # intercom
        # Source description + messages
        source_desc = data.get('source', {}).get('description')
        if source_desc:
            author_name = data.get('source', {}).get('author_name', 'Client')
            messages.append({
                'content': source_desc.replace('<br>', '\n'),
                'message_type': 'incoming',
                'author_name': author_name,
                'created_at': data.get('created_at')
            })
        
        # Traiter les messages
        for msg in data.get('messages', []):
            
            # Déterminer le type de message selon author_type
            if msg.get('author_type') == 'admin':
                message_type = 'outgoing'  # Message de l'agent
            elif msg.get('author_type') == 'user':
                message_type = 'incoming'  # Message du client
            else:
                message_type = 'outgoing'
            
            messages.append({
                'content': msg['content'].replace('<br>', '\n'),
                'content_type_msg': msg.get('message_type'),
                'message_type': message_type,
                'author_name': msg.get('author_name', 'Unknown'),
                'created_at': msg.get('created_at'),
                'attachments': msg.get('attachments', [])
            })
        
        # Retourner la conversation formatée
        return {
            'contact_email': contact_email,
            'title': data.get('title', 'Sans titre'),
            'status': 'resolved' if data.get('state') == 'closed' else 'open',
            'zendesk_ticket_id': None,
            'intercom_conversation_id': data.get('id'),
            'created_at': data.get('created_at'),
            'tags': data.get('tags', []),
            'additional_attributes': {
                'priority': data.get('priority'),
                'admin_assignee_id': data.get('admin_assignee_id'),
                'team_assignee_id': data.get('team_assignee_id')
            },
            'messages': messages
        }

def prepare_conversations_for_chatwoot() -> str:
    """Préparer conversations pour l'import Chatwoot"""
    print("Préparation conversations Chatwoot")
    print("=" * 35)
    
    # Charger données
    zendesk_tickets, intercom_convs = load_transformed_data()
    zendesk_index, intercom_index = load_contact_index()
    
    conversations = []
    stats = {'zendesk': 0, 'intercom': 0, 'orphans': 0}
    
    # Traiter tickets Zendesk
    for ticket in zendesk_tickets:
        requester_id = ticket.get('requester_id')
        email = zendesk_index.get(requester_id)
        
        if email:
            conv = format_conversation(ticket, 'zendesk', email)
            conversations.append(conv)
            stats['zendesk'] += 1
        else:
            stats['orphans'] += 1
    
    # Traiter conversations Intercom
    for conv in intercom_convs:
        contact_id = conv.get('contact_id')
        email = intercom_index.get(contact_id)
        
        if email:
            formatted_conv = format_conversation(conv, 'intercom', email)
            conversations.append(formatted_conv)
            stats['intercom'] += 1
        else:
            stats['orphans'] += 1
    
    # Structure finale
    output_data = {
        'metadata': {
            'prepared_at': get_timestamp(True),
            'total_conversations': len(conversations),
            'stats': stats
        },
        'conversations': conversations
    }
    
    # Sauvegarde
    filepath = os.path.join(CHATWOOT_OUTPUT_DIR, f"chatwoot_conversations_prepared_{get_timestamp()}.json")
    os.makedirs(CHATWOOT_OUTPUT_DIR, exist_ok=True)
    save_json(output_data, filepath)
    
    print(f"Conversations préparées: {len(conversations)} ({get_file_size(filepath)})")
    print(f"Stats: ZD:{stats['zendesk']}, IC:{stats['intercom']}, Orphelins:{stats['orphans']}")
    return filepath


# if __name__ == "__main__":
#     prepare_conversations_for_chatwoot()
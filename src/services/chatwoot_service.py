import json
import os
from typing import Dict, List

import requests
from src.api.chatwoot_client import ChatwootClient
from src.utils.helpers import get_timestamp
from configs.config import CHATWOOT_OUTPUT_DIR


def load_prepared_data():
    """Charger les données préparées"""
    date = get_timestamp()
    
    contacts_path = f"{CHATWOOT_OUTPUT_DIR}/chatwoot_contacts_prepared_{date}.json"
    conversations_path = f"{CHATWOOT_OUTPUT_DIR}/chatwoot_conversations_prepared_{date}.json"
    
    with open(contacts_path, 'r', encoding='utf-8') as f:
        contacts_data = json.load(f).get('contacts', [])
    
    with open(conversations_path, 'r', encoding='utf-8') as f:
        conversations_data = json.load(f).get('conversations', [])
    
    print(f"Chargé: {len(contacts_data)} contacts, {len(conversations_data)} conversations")
    return contacts_data, conversations_data


def find_specific_conversations(conversations: List[Dict]) -> Dict:
    """Trouver conversations spécifiques pour test"""
    zendesk_conv = None
    intercom_conv = None
    
    for conv in conversations:
        # # # Chercher conversation Alberto CAMACHO (Intercom)
        # if conv.get('intercom_conversation_id') and conv.get('contact_email') == 'alexia.victor_masterclass-formation.fr@alphorm.com':
        #     intercom_conv = conv
        
        # # Chercher conversation Alberto CAMACHO (Intercom)
        # if conv.get('intercom_conversation_id') and conv.get('contact_email') == 'florence.courtout_soprasteria.com@alphorm.com':
        #     intercom_conv = conv
            
        # Chercher conversation informatique (Zendesk)  
        if conv.get('zendesk_ticket_id') and 'aizen5713_gmail.com@alphorm.com' in str(conv.get('contact_email', '')):
            zendesk_conv = conv
            
        # # Chercher conversation informatique (Zendesk)  
        # if conv.get('zendesk_ticket_id') and 'r.tchegnon_gmail.com@alphorm.com' in str(conv.get('contact_email', '')):
        #     zendesk_conv = conv
        
        if zendesk_conv and intercom_conv:
            break
    
    return {
        'zendesk': zendesk_conv,
        'intercom': intercom_conv
    }


def find_contacts_for_conversations(contacts: List[Dict], sample_conversations: Dict) -> Dict:
    """Trouver les contacts des conversations échantillons"""
    zendesk_contact = None
    intercom_contact = None
    
    zendesk_email = sample_conversations['zendesk']['contact_email'] if sample_conversations['zendesk'] else None
    intercom_email = sample_conversations['intercom']['contact_email'] if sample_conversations['intercom'] else None
    
    for contact in contacts:
        email = contact.get('email')
        
        if email == zendesk_email:
            zendesk_contact = contact
        elif email == intercom_email:
            intercom_contact = contact
        
        if zendesk_contact and intercom_contact:
            break
    
    return {
        'zendesk': zendesk_contact,
        'intercom': intercom_contact
    }


def import_contact_to_chatwoot(client: ChatwootClient, contact: Dict, inbox_id: int) -> Dict:
    """Importer un contact dans Chatwoot avec toutes ses infos"""
    phone = contact.get("phone_number")
    if phone and not (phone.startswith("+") and len(phone) > 5):
        phone = None

    attrs = contact.get("additional_attributes", {}) or {}
    
    # Générer un identifier plus lisible
    email = contact.get("email", "")
    
    if email:
        email_prefix = email
        identifier = f"{email_prefix}_{get_timestamp()}"
    else:
        # Si pas d'email, utiliser le nom
        name = contact.get("name", "unknown").lower().replace(' ', '_')
        identifier = f"{name}_{get_timestamp()}"

    # Construire les custom_attributes
    custom_attributes = {
        **attrs,
        "imported_from_zd_at": contact.get("imported_from_zd_at"),
        "imported_from_intercom_at": contact.get("imported_from_intercom_at"),
        "migration_source": "zendesk" if contact.get("zendesk_id") else "intercom",
        "original_id": contact.get('zendesk_id', contact.get('intercom_id'))  # Garder l'ID original
    }

    # Construire payload final
    contact_data = {
        "inbox_id": inbox_id,
        "name": contact.get("name"),
        "email": contact.get("email"),
        "identifier": identifier, 
        "custom_attributes": custom_attributes,
    }

    # Ajouter champs natifs
    if attrs.get("location_city"):
        contact_data["city"] = attrs["location_city"]
    if attrs.get("location_country"):
        contact_data["country"] = attrs["location_country"]

    if phone:
        contact_data["phone_number"] = phone

    if contact.get("avatar_url"):
        contact_data["avatar_url"] = contact["avatar_url"]

    print(f"Payload contact pour Chatwoot : {contact_data}")
    return client.create_contact(contact_data)


def import_conversation_to_chatwoot(client: ChatwootClient, conversation: Dict, 
                                   contact_id: int, source_id: str, 
                                   inbox_id: int, status: str) -> Dict:
    """Importer une conversation avec ses pièces jointes"""
    
    # Créer la conversation
    created_conv = client.create_conversation(
        source_id=source_id,
        inbox_id=inbox_id,
        contact_id=contact_id,
        status="open"
    )
    
    conversation_id = created_conv.get('id')
    
    # Importer les messages avec leurs pièces jointes
    messages_added = 0
    for message in conversation.get('messages', []):
        attachment_files = []
        
        # Télécharger les pièces jointes 
        for attachment in message.get('attachments', []):
            try:
                # Gérer les différents formats d'URL
                # Pour Zendesk : content_url ou mapped_content_url
                # Pour Intercom : url directement
                file_url = (attachment.get('content_url') or      # Pour Zendesk - priorité 1
                            attachment.get('mapped_content_url') or  # Pour Zendesk - priorité 2
                            attachment.get('url'))                   # Pour Intercom - dernier
                
                if file_url:
                    # Télécharger le fichier
                    response = requests.get(file_url, timeout=30)
                    if response.status_code == 200:
                        # Utiliser le nom du fichier ou un nom par défaut
                        filename = attachment.get('name') or attachment.get('file_name', 'attachment')
                        attachment_files.append((filename, response.content))
                        print(f"Pièce jointe téléchargée: {filename}")
            except Exception as e:
                print(f"Erreur téléchargement pièce jointe: {e}")
        
        # Créer le message avec ou sans pièces jointes
        try:
            if attachment_files:
                # Utiliser la méthode spéciale pour les pièces jointes
                client.create_message_with_attachments(
                    conversation_id=conversation_id,
                    content=message['content'],
                    message_type=message.get('message_type', 'incoming'),
                    private=True if message.get('content_type_msg') == 'note' else False,
                    attachment_files=attachment_files
                )
            else:
                # Message normal sans pièces jointes
                client.create_message(
                    conversation_id=conversation_id,
                    content=message['content'],
                    message_type=message.get('message_type', 'incoming'),
                    private=True if message.get('content_type_msg') == 'note' else False
                )
            messages_added += 1
        except Exception as e:
            print(f"Erreur message: {e}")
    
    print(f"Conversation {conversation_id}: {messages_added} messages ajoutés")
    
    # Mettre à jour le statut final
    client.update_conversation_status(conversation_id, status)
    
    return created_conv

def test_import_sample_data():
    """Test d'import avec échantillons Zendesk + Intercom"""
    print("Test import échantillons Chatwoot")
    print("=" * 35)
    
    # Configuration
    INBOX_ID = 2  # Remplacez par votre inbox API ID
    
    # Initialiser client
    client = ChatwootClient()
    if not client.test_connection():
        print("Connexion échouée")
        return False
    
    try:
        # Charger données préparées
        contacts, conversations = load_prepared_data()
        
        # Sélectionner échantillons spécifiques
        sample_conversations = find_specific_conversations(conversations)
        sample_contacts = find_contacts_for_conversations(contacts, sample_conversations)
        
        print(f"\nÉchantillons sélectionnés:")
        if sample_conversations['zendesk']:
            print(f"Conversation Zendesk: {sample_conversations['zendesk']['title']}")
            print(f"Contact: {sample_contacts['zendesk']['name'] if sample_contacts['zendesk'] else 'CONTACT NON TROUVÉ'}")
        if sample_conversations['intercom']:
            print(f"Conversation Intercom: {sample_conversations['intercom']['title']}")
            print(f"Contact: {sample_contacts['intercom']['name'] if sample_contacts['intercom'] else 'CONTACT NON TROUVÉ'}")
        
        if not sample_conversations['zendesk'] and not sample_conversations['intercom']:
            print("AUCUNE CONVERSATION TROUVÉE")
            return False
        
        results = []
        
        # Test 1: Import contact + conversation Zendesk
        if sample_contacts['zendesk'] and sample_conversations['zendesk']:
            print(f"\n1. Import Zendesk: {sample_contacts['zendesk']['name']}")
            
            # Importer contact
            created_contact = import_contact_to_chatwoot(
                client, sample_contacts['zendesk'], INBOX_ID
            )
            
            # Extraire infos contact
            contact_payload = created_contact.get('payload', {}).get('contact', {})
            contact_id = contact_payload.get('id')
            contact_inboxes = contact_payload.get('contact_inboxes', [])
            source_id = contact_inboxes[0].get('source_id') if contact_inboxes else None
            
            if contact_id and source_id:
                # Importer conversation
                status = sample_conversations['zendesk'].get('status')
                created_conv = import_conversation_to_chatwoot(
                    client, sample_conversations['zendesk'],
                    contact_id, source_id, INBOX_ID, status=status
                )
                
                results.append({
                    'platform': 'zendesk',
                    'contact_name': sample_contacts['zendesk']['name'],
                    'contact_id': contact_id,
                    'conversation_id': created_conv.get('id'),
                    'messages_count': len(sample_conversations['zendesk'].get('messages', []))
                })
        
        # Test 2: Import contact + conversation Intercom
        if sample_contacts['intercom'] and sample_conversations['intercom']:
            print(f"\n2. Import Intercom: {sample_contacts['intercom']['name']}")
            
            # Importer contact
            created_contact = import_contact_to_chatwoot(
                client, sample_contacts['intercom'], INBOX_ID
            )
            
            # Extraire infos contact
            contact_payload = created_contact.get('payload', {}).get('contact', {})
            contact_id = contact_payload.get('id')
            contact_inboxes = contact_payload.get('contact_inboxes', [])
            source_id = contact_inboxes[0].get('source_id') if contact_inboxes else None
            
            if contact_id and source_id:
                status = sample_conversations['intercom'].get('status')
                created_conv = import_conversation_to_chatwoot(
                    client, sample_conversations['intercom'],
                    contact_id, source_id, INBOX_ID, status=status
                )
                
                results.append({
                    'platform': 'intercom',
                    'contact_name': sample_contacts['intercom']['name'],
                    'contact_id': contact_id,
                    'conversation_id': created_conv.get('id'),
                    'messages_count': len(sample_conversations['intercom'].get('messages', []))
                })
        
        # Résumé
        print(f"\nRésultats du test:")
        print(f"=" * 20)
        for result in results:
            print(f"{result['platform'].upper()}:")
            print(f"  Contact: {result['contact_name']} (ID: {result['contact_id']})")
            print(f"  Conversation: ID {result['conversation_id']}")
            print(f"  Messages: {result['messages_count']}")
            print()
        
        print(f"Import test terminé: {len(results)} imports réussis")
        return True
        
    except Exception as e:
        print(f"Erreur durant le test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_import_sample_data()
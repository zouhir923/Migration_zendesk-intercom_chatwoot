import json
import os
from typing import Dict, List

import requests
from src.api.chatwoot_client import ChatwootClient
from src.utils.helpers import get_timestamp
from configs.config import CHATWOOT_OUTPUT_DIR

def load_prepared_data():
    date = get_timestamp()
    contacts_path = f"{CHATWOOT_OUTPUT_DIR}/chatwoot_contacts_prepared_{date}.json"
    conversations_path = f"{CHATWOOT_OUTPUT_DIR}/chatwoot_conversations_prepared_{date}.json"

    with open(contacts_path, 'r', encoding='utf-8') as f:
        contacts_data = json.load(f).get('contacts', [])
    with open(conversations_path, 'r', encoding='utf-8') as f:
        conversations_data = json.load(f).get('conversations', [])

    print(f"Chargé: {len(contacts_data)} contacts, {len(conversations_data)} conversations")
    return contacts_data, conversations_data

def group_conversations_by_contact(conversations: List[Dict]) -> Dict[str, List[Dict]]:
    grouped = {}
    for conv in conversations:
        email = conv.get('contact_email')
        if not email:
            continue
        grouped.setdefault(email, []).append(conv)
    return grouped

def import_contact_to_chatwoot(client: ChatwootClient, contact: Dict, inbox_id: int) -> Dict:
    phone = contact.get("phone_number")
    if phone and not (phone.startswith("+") and len(phone) > 5):
        phone = None

    attrs = contact.get("additional_attributes", {}) or {}
    email = contact.get("email", "")
    if email:
        identifier = f"{email}_{get_timestamp()}"
    else:
        name = contact.get("name", "unknown").lower().replace(' ', '_')
        identifier = f"{name}_{get_timestamp()}"

    custom_attributes = {
        **attrs,
        "imported_from_zd_at": contact.get("imported_from_zd_at"),
        "imported_from_intercom_at": contact.get("imported_from_intercom_at"),
        "migration_source": "zendesk" if contact.get("zendesk_id") else "intercom",
        "original_id": contact.get('zendesk_id', contact.get('intercom_id'))
    }

    contact_data = {
        "inbox_id": inbox_id,
        "name": contact.get("name"),
        "email": contact.get("email"),
        "identifier": identifier,
        "custom_attributes": custom_attributes,
    }

    if attrs.get("location_city"):
        contact_data["city"] = attrs["location_city"]
    if attrs.get("location_country"):
        contact_data["country"] = attrs["location_country"]
    if phone:
        contact_data["phone_number"] = phone
    if contact.get("avatar_url"):
        contact_data["avatar_url"] = contact["avatar_url"]

    print(f"Création contact Chatwoot: {contact_data.get('email', contact_data.get('name'))}")
    return client.create_contact(contact_data)

def import_conversation_to_chatwoot(client: ChatwootClient, conversation: Dict,
                                   contact_id: int, source_id: str,
                                   inbox_id: int, status: str) -> Dict:
    created_conv = client.create_conversation(
        source_id=source_id,
        inbox_id=inbox_id,
        contact_id=contact_id,
        status="open"
    )
    conversation_id = created_conv.get('id')

    messages_added = 0
    for message in conversation.get('messages', []):
        attachment_files = []
        for attachment in message.get('attachments', []):
            try:
                file_url = (
                    attachment.get('content_url') or
                    attachment.get('mapped_content_url') or
                    attachment.get('url')
                )
                if file_url:
                    response = requests.get(file_url, timeout=30)
                    if response.status_code == 200:
                        filename = attachment.get('name') or attachment.get('file_name', 'attachment')
                        attachment_files.append((filename, response.content))
                        print(f"Pièce jointe téléchargée: {filename}")
            except Exception as e:
                print(f"Erreur téléchargement pièce jointe: {e}")

        try:
            if attachment_files:
                client.create_message_with_attachments(
                    conversation_id=conversation_id,
                    content=message['content'],
                    message_type=message.get('message_type', 'incoming'),
                    private=True if message.get('content_type_msg') == 'note' else False,
                    attachment_files=attachment_files
                )
            else:
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
    client.update_conversation_status(conversation_id, status)
    return created_conv

def migrate_all_data(limit: int = None):
    print("Migration complète des contacts et conversations")
    print("=" * 50)

    INBOX_ID = 2
    client = ChatwootClient()
    if not client.test_connection():
        print("Connexion échouée")
        return False

    contacts, conversations = load_prepared_data()
    conversations_by_email = group_conversations_by_contact(conversations)

    if limit:
        contacts = contacts[:limit]
        print(f"⚠ Limite activée: import de {limit} contacts seulement")

    results = {
        'contacts_imported': 0,
        'contacts_without_conv': 0,
        'conversations_imported': 0,
        'messages_imported': 0
    }

    for contact in contacts:
        try:
            created_contact = import_contact_to_chatwoot(client, contact, INBOX_ID)
            contact_payload = created_contact.get('payload', {}).get('contact', {})
            contact_id = contact_payload.get('id')
            contact_inboxes = contact_payload.get('contact_inboxes', [])
            source_id = contact_inboxes[0].get('source_id') if contact_inboxes else None

            results['contacts_imported'] += 1

            contact_email = contact.get('email')
            contact_conversations = conversations_by_email.get(contact_email, [])

            if contact_conversations:
                for conv in contact_conversations:
                    created_conv = import_conversation_to_chatwoot(
                        client, conv, contact_id, source_id, INBOX_ID, status=conv.get('status')
                    )
                    results['conversations_imported'] += 1
                    results['messages_imported'] += len(conv.get('messages', []))
            else:
                results['contacts_without_conv'] += 1
        except Exception as e:
            print(f"Erreur sur contact {contact.get('email')}: {e}")

    print("\nRésumé de migration:")
    print("=" * 30)
    print(f"Contacts importés: {results['contacts_imported']}")
    print(f"Contacts sans conversation: {results['contacts_without_conv']}")
    print(f"Conversations importées: {results['conversations_imported']}")
    print(f"Messages importés: {results['messages_imported']}")
    return True

if __name__ == "__main__":
    migrate_all_data(30) 
    # migrate_all_data()

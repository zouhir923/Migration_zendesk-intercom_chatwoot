import json
import os
from typing import Dict, List, Tuple
from src.utils.helpers import save_json, get_file_size, get_timestamp
from configs.config import ZENDESK_OUTPUT_DIR, INTERCOM_OUTPUT_DIR, CHATWOOT_OUTPUT_DIR


def load_clean_data() -> Tuple[List[Dict], List[Dict]]:
    """Charger les données nettoyées de Zendesk et Intercom"""
    date = get_timestamp()
    
    # Paths
    zendesk_path = f"{ZENDESK_OUTPUT_DIR}/clean_export_data/zendesk_users_clean_{date}.json"
    intercom_path = f"{INTERCOM_OUTPUT_DIR}/clean_export_data/intercom_contacts_clean_{date}.json"
    
    # Load data
    with open(zendesk_path, 'r', encoding='utf-8') as f:
        zendesk_data = json.load(f).get('users', [])
    
    with open(intercom_path, 'r', encoding='utf-8') as f:
        intercom_data = json.load(f).get('contacts', [])
    
    print(f"Chargé: {len(zendesk_data)} Zendesk, {len(intercom_data)} Intercom")
    return zendesk_data, intercom_data


def format_contact(data: Dict, source: str, email: str = None) -> Dict:
    """Formater un contact selon la source"""
    final_email = email if email is not None else data.get('email')
    
    if final_email and '@' in final_email:
        username, domain = final_email.split('@', 1)
        final_email = f"{username}_{domain}@alphorm.com"
    
    base = {
        "email": final_email,
        "name": data.get('name'),
        "phone_number": data.get('phone'),
        "zendesk_id": data.get('id') if source == "zendesk" else None,
        "intercom_id": data.get('id') if source == "intercom" else None,
        "imported_from_zd_at": get_timestamp(True) if source == "zendesk" else None,
        "imported_from_intercom_at": get_timestamp(True) if source == "intercom" else None
    }
    
    if source == "zendesk":
        base.update({
            "avatar_url": None,
            "additional_attributes": {
                "time_zone": data.get('time_zone'),
                "locale": data.get('locale'),
                "organization_id": data.get('organization_id'),
                "created_at": data.get('created_at'),
                "tags": data.get('tags', [])
            }
        })
    else:  # intercom
        location = data.get('location', {})
        base.update({
            "avatar_url": data.get('avatar'),
            "additional_attributes": {
                "external_id": data.get('external_id'),
                "location_country": location.get('country'),
                "location_city": location.get('city'),
                "browser": data.get('browser'),
                "os": data.get('os'),
                "created_at": data.get('created_at'),
                "custom_attributes": data.get('custom_attributes', {}),
                "tags": data.get('tags', [])
            }
        })
    
    return base


def merge_and_deduplicate(zendesk_data: List[Dict], intercom_data: List[Dict]) -> Tuple[List[Dict], Dict]:
    """Fusionner contacts par email, Intercom prioritaire"""
    contacts = {}
    stats = {'zendesk': 0, 'intercom': 0, 'merged': 0, 'no_email': 0}
    
    # Process Zendesk first
    for user in zendesk_data:
        email = user.get('email')
        if email is None:
            email = f"no-email-zd-{user.get('id')}@alphorm.com"
            stats['no_email'] += 1
        contacts[email] = format_contact(user, "zendesk", email)
        stats['zendesk'] += 1
    
    # Process Intercom (overrides if duplicate)
    for contact in intercom_data:
        email = contact.get('email')
        if email is None:
            email = f"no-email-ic-{contact.get('id')}@alphorm.com"
            stats['no_email'] += 1

        if email in contacts:
            # Merge: keep Intercom data + Zendesk ID
            new_contact = format_contact(contact, "intercom", email)
            new_contact['zendesk_id'] = contacts[email]['zendesk_id']
            new_contact['imported_from_zd_at'] = contacts[email]['imported_from_zd_at']
            contacts[email] = new_contact
            stats['merged'] += 1
        else:
            contacts[email] = format_contact(contact, "intercom", email)
            stats['intercom'] += 1
    
    return list(contacts.values()), stats


def prepare_contacts_for_chatwoot() -> str:
    """Préparer les contacts pour l'import Chatwoot"""
    print("Préparation contacts Chatwoot")
    print("=" * 30)
    
    # Load, merge, save
    zendesk_data, intercom_data = load_clean_data()
    contacts, stats = merge_and_deduplicate(zendesk_data, intercom_data)
    
    output_data = {
        'metadata': {
            'prepared_at': get_timestamp(True),
            'total_contacts': len(contacts),
            'stats': stats
        },
        'contacts': contacts
    }
    
    # Save
    filepath = os.path.join(CHATWOOT_OUTPUT_DIR, f"chatwoot_contacts_prepared_{get_timestamp()}.json")
    os.makedirs(CHATWOOT_OUTPUT_DIR, exist_ok=True)
    save_json(output_data, filepath)
    
    print(f"Contacts préparés: {len(contacts)} ({get_file_size(filepath)})")
    print(f"Stats: ZD:{stats['zendesk']}, IC:{stats['intercom']}, Fusionnés:{stats['merged']}")
    return filepath


if __name__ == "__main__":
    prepare_contacts_for_chatwoot()

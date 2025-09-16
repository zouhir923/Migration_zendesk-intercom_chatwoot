import os
from src.api.intercom_client import IntercomClient
from src.utils.helpers import save_json, get_file_size, get_timestamp
from configs.config import INTERCOM_OUTPUT_DIR


class IntercomService:
    """Service pour exporter les données Intercom"""
    
    def __init__(self):
        self.client = IntercomClient()
        self.output_dir = f"{INTERCOM_OUTPUT_DIR}/origin_export"
    
    def export_articles(self) -> str:
        """Exporter seulement les articles"""
        print("Export articles...")
        articles = self.client.get_all_articles()
        
        data = {
            'metadata': {'exported_at': get_timestamp(include_time=True), 'count': len(articles)},
            'articles': articles
        }
        
        filename = f"intercom_articles_{get_timestamp()}.json"
        filepath = os.path.join(self.output_dir, filename)
        save_json(data, filepath)
        
        print(f"Articles sauvés: {filename} ({get_file_size(filepath)}) - {len(articles)} items")
        return filepath

    def export_conversations(self) -> str:
        """Exporter seulement les conversations avec messages"""
        print("Export conversations...")
        conversations = self.client.get_conversations_with_messages()
        
        data = {
            'metadata': {'exported_at': get_timestamp(include_time=True), 'count': len(conversations)},
            'conversations': conversations
        }
        
        filename = f"intercom_conversations_{get_timestamp()}.json"
        filepath = os.path.join(self.output_dir, filename)
        save_json(data, filepath)
        
        print(f"Conversations sauvées: {filename} ({get_file_size(filepath)}) - {len(conversations)} items")
        return filepath
    
    def export_contacts(self) -> str:
        """Exporter seulement les contacts"""
        print("Export contacts...")
        contacts = self.client.get_all_contacts()
        
        data = {
            'metadata': {'exported_at': get_timestamp(include_time=True), 'count': len(contacts)},
            'contacts': contacts
        }
        
        filename = f"intercom_contacts_{get_timestamp()}.json"
        filepath = os.path.join(self.output_dir, filename)
        save_json(data, filepath)
        
        print(f"Contacts sauvés: {filename} ({get_file_size(filepath)}) - {len(contacts)} items")
        return filepath
    
def test_intercom_service():
    """Test du service"""
    service = IntercomService()
    
    if not service.client.test_connection():
        print("Connexion échouée")
        return
    
    # service.export_articles()
    # service.export_conversations()
    service.export_contacts()

if __name__ == "__main__":
    test_intercom_service()
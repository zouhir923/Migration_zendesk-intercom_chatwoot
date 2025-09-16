import os
from typing import Dict, List
from src.api.zendesk_client import ZendeskClient
from src.utils.helpers import save_json, get_file_size, get_timestamp
from configs.config import ZENDESK_OUTPUT_DIR


class ZendeskService:
    """Service pour exporter les données Zendesk"""
    
    def __init__(self):
        self.client = ZendeskClient()
        self.output_dir = f"{ZENDESK_OUTPUT_DIR}/origin_export"
    
    def export_tickets(self) -> str:
        """Exporter seulement les tickets avec commentaires"""
        print("Export tickets...")
        tickets = self.client.get_tickets_with_comments()
        
        data = {
            'metadata': {'exported_at': get_timestamp(include_time=True), 'count': len(tickets)},
            'tickets': tickets
        }
        
        filename = f"zendesk_tickets_{get_timestamp()}.json"
        filepath = os.path.join(self.output_dir, filename)
        save_json(data, filepath)
        
        print(f"Tickets sauvés: {filename} ({get_file_size(filepath)}) - {len(tickets)} items")
        return filepath
    
    def export_users(self) -> str:
        """Exporter seulement les contacts"""
        print("Export contacts...")
        users = self.client.get_all_users()
        
        data = {
            'metadata': {'exported_at': get_timestamp(include_time=True), 'count': len(users)},
            'users': users
        }
        
        filename = f"zendesk_users_{get_timestamp()}.json"
        filepath = os.path.join(self.output_dir, filename)
        save_json(data, filepath)
        
        print(f"Contacts sauvés: {filename} ({get_file_size(filepath)}) - {len(users)} items")
        return filepath
    
    def export_articles(self) -> str:
        """Exporter seulement les articles"""
        print("Export articles...")
        articles = self.client.get_all_articles()
        
        data = {
            'metadata': {'exported_at': get_timestamp(include_time=True), 'count': len(articles)},
            'articles': articles
        }
        
        filename = f"zendesk_articles_{get_timestamp()}.json"
        filepath = os.path.join(self.output_dir, filename)
        save_json(data, filepath)
        
        print(f"Articles sauvés: {filename} ({get_file_size(filepath)}) - {len(articles)} items")
        return filepath
    
    def export_macros(self) -> str:
        """Exporter seulement les macros"""
        print("Export macros...")
        macros = self.client.get_all_macros()
        
        data = {
            'metadata': {'exported_at': get_timestamp(include_time=True), 'count': len(macros)},
            'macros': macros
        }
        
        filename = f"zendesk_macros_{get_timestamp()}.json"
        filepath = os.path.join(self.output_dir, filename)
        save_json(data, filepath)
        
        print(f"Macros sauvés: {filename} ({get_file_size(filepath)}) - {len(macros)} items")
        return filepath
    
    def export_all(self) -> Dict[str, str]:
        """Exporter toutes les données"""
        print("Export complet Zendesk")
        print("=" * 25)
        
        files = {}
        files['tickets'] = self.export_tickets()
        files['users'] = self.export_users()
        files['articles'] = self.export_articles()
        files['macros'] = self.export_macros()
        
        print(f"\nExport terminé - {len(files)} fichiers créés")
        return files


# def test_zendesk_service():
#     """Test du service"""
#     service = ZendeskService()
    
#     if not service.client.test_connection():
#         print("Connexion échouée")
#         return
    
#     print("Tests disponibles:")
#     print("1. export_users()")
#     print("2. export_tickets()")
#     print("3. export_articles()")
#     print("4. export_macros()")
#     print("5. export_all()")

#     service.export_all()


# if __name__ == "__main__":
#     test_zendesk_service()
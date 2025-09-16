import requests
import json
import time
from typing import Dict, List, Optional, Any
from configs.config import INTERCOM_ACCESS_TOKEN, INTERCOM_RATE_LIMIT


class IntercomClient:
    """Client API pour extraire toutes les données d'Intercom"""
    
    def __init__(self):
        # Configuration de base
        self.access_token = INTERCOM_ACCESS_TOKEN
        self.base_url = "https://api.intercom.io"
        
        # Configuration de la session HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Limitation du taux de requêtes
        self.rate_limit = INTERCOM_RATE_LIMIT / 60  # requêtes par seconde
        self.last_request = 0
        
        print(f"Client Intercom initialisé")
    
    def _rate_limit_wait(self):
        """Attendre pour respecter les limites de taux"""
        current_time = time.time()
        time_since_last = current_time - self.last_request
        min_interval = 1 / self.rate_limit
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Effectuer une requête API avec gestion d'erreurs"""
        self._rate_limit_wait()
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur API Intercom: {e}")
            if hasattr(e.response, 'text'):
                print(f"Détails: {e.response.text}")
            raise
    
    def test_connection(self) -> bool:
        """Tester la connexion à Intercom"""
        try:
            response = self._make_request("contacts", {"per_page": 1})
            print(f"Réponse API reçue: {list(response.keys())}")
            
            # Intercom peut retourner différents formats
            if 'data' in response or 'contacts' in response:
                print("Connexion Intercom réussie")
                return True
            else:
                print(f"Structure inattendue: {response}")
                return False
        except Exception as e:
            print(f"Échec de connexion: {e}")
            return False
    
    def get_all_conversations(self) -> List[Dict]:
        """Récupérer toutes les conversations"""
        print("Récupération des conversations...")
        all_conversations = []
        endpoint = "conversations"
        
        params = {"per_page": 150}
        page_count = 0
        
        while True:
            data = self._make_request(endpoint, params)
            
            # Fix: conversations sont dans 'conversations' pas 'data'
            conversations = data.get('conversations', [])
            all_conversations.extend(conversations)
            
            page_count += 1
            print(f"Page {page_count}: {len(conversations)} conversations récupérées")
            
            # Fix pagination
            pages = data.get('pages', {})
            next_page = pages.get('next')
            if not next_page:
                break
            
            if 'starting_after' in next_page:
                params['starting_after'] = next_page['starting_after']
            else:
                break
        
        print(f"Total: {len(all_conversations)} conversations récupérées")
        return all_conversations
    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """Récupérer tous les messages d'une conversation"""
        endpoint = f"conversations/{conversation_id}"
        
        try:
            data = self._make_request(endpoint)
            # Les messages sont dans conversation_parts
            conversation_parts = data.get('conversation_parts', {}).get('conversation_parts', [])
            return conversation_parts
        except Exception as e:
            print(f"Erreur messages conversation {conversation_id}: {e}")
            return []
    
    def get_conversations_with_messages(self) -> List[Dict]:
        """Récupérer toutes les conversations avec leurs messages"""
        conversations = self.get_all_conversations()
        
        print(f"Récupération des messages pour {len(conversations)} conversations...")
        
        for i, conversation in enumerate(conversations):
            conversation_id = conversation['id']
            messages = self.get_conversation_messages(conversation_id)
            conversation['messages'] = messages
            
            # Afficher le progrès tous les 10 conversations
            if (i + 1) % 10 == 0:
                print(f"Traité {i + 1}/{len(conversations)} conversations")
        
        print("Messages récupérés pour toutes les conversations")
        return conversations
    
    def get_all_contacts(self) -> List[Dict]:
        """Récupérer tous les contacts"""
        print("Récupération des contacts...")
        all_contacts = []
        endpoint = "contacts"
        
        params = {"per_page": 150}  # Maximum autorisé
        page_count = 0
        
        while True:
            data = self._make_request(endpoint, params)
            
            contacts = data.get('data', [])
            all_contacts.extend(contacts)
            
            page_count += 1
            print(f"Page {page_count}: {len(contacts)} contacts récupérés")
            
            # Vérifier la pagination
            pages = data.get('pages', {})
            if not pages.get('next'):
                break
            
            # Préparer la page suivante
            next_url = pages['next']
            if 'starting_after' in next_url:
                starting_after = next_url.split('starting_after=')[1].split('&')[0]
                params['starting_after'] = starting_after
        
        print(f"Total: {len(all_contacts)} contacts récupérés")
        return all_contacts
    
    def get_all_articles(self) -> List[Dict]:
        """Récupérer tous les articles"""
        print("Récupération des articles...")
        all_articles = []
        endpoint = "articles"
        
        params = {"per_page": 150}  # Maximum autorisé
        page_count = 0
        
        while True:
            data = self._make_request(endpoint, params)
            
            articles = data.get('data', [])
            all_articles.extend(articles)
            
            page_count += 1
            print(f"Page {page_count}: {len(articles)} articles récupérés")
            
            # Vérifier la pagination
            pages = data.get('pages', {})
            if not pages.get('next'):
                break
            
            # Préparer la page suivante
            next_url = pages['next']
            if 'starting_after' in next_url:
                starting_after = next_url.split('starting_after=')[1].split('&')[0]
                params['starting_after'] = starting_after
        
        print(f"Total: {len(all_articles)} articles récupérés")
        return all_articles
    
    def export_all_data(self) -> Dict[str, Any]:
        """Exporter toutes les données Intercom"""
        print("Début de l'export complet des données Intercom")
        print("=" * 50)
        
        # Structure de données pour l'export
        data = {
            'metadata': {
                'exported_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_items': {}
            }
        }
        
        # 1. Export des conversations avec messages
        print("1. Export des conversations avec messages...")
        conversations = self.get_conversations_with_messages()
        data['conversations'] = conversations
        data['metadata']['total_items']['conversations'] = len(conversations)
        
        # 2. Export des contacts
        print("\n2. Export des contacts...")
        contacts = self.get_all_contacts()
        data['contacts'] = contacts
        data['metadata']['total_items']['contacts'] = len(contacts)
        
        # 3. Export des articles
        print("\n3. Export des articles...")
        articles = self.get_all_articles()
        data['articles'] = articles
        data['metadata']['total_items']['articles'] = len(articles)
        
        # Résumé final
        print("\n" + "=" * 50)
        print("Export Intercom terminé avec succès")
        print("Résumé des données exportées:")
        for item_type, count in data['metadata']['total_items'].items():
            print(f"- {item_type}: {count}")
        
        return data


# # Test avec comptage pour vérifier l'intégrité des données
# def test_intercom_client():
#     """Test du client avec vérification des totaux"""
#     print("Test du client Intercom")
#     print("=" * 30)
    
#     client = IntercomClient()
    
#     # Test de connexion
#     if not client.test_connection():
#         print("Test échoué - Vérifiez la configuration")
#         return False
    
#     # Test de comptage des données
#     print("\nVérification des totaux:")
    
#     try:
#         # Test conversations
#         conv_response = client._make_request("conversations", {"per_page": 1})
#         conv_total = conv_response.get('pages', {}).get('total_pages', 'Inconnu')
#         print(f"Conversations: {conv_total} pages")
        
#         # Test contacts  
#         contacts_response = client._make_request("contacts", {"per_page": 1})
#         contacts_total = contacts_response.get('pages', {}).get('total_pages', 'Inconnu')
#         print(f"Contacts: {contacts_total} pages")
        
#         # Test articles
#         articles_response = client._make_request("articles", {"per_page": 1})
#         articles_total = articles_response.get('pages', {}).get('total_pages', 'Inconnu')
#         print(f"Articles: {articles_total} pages")
        
#     except Exception as e:
#         print(f"Erreur lors du test: {e}")
#         return False
    
#     print("\nTest réussi - Client opérationnel")
#     return True


# # Utilisation du client
# if __name__ == "__main__":
#     test_intercom_client()
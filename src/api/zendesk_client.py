import requests
import json
import time
from typing import Dict, List, Optional, Any
from configs.config import ZENDESK_DOMAIN, ZENDESK_EMAIL, ZENDESK_API_TOKEN, ZENDESK_RATE_LIMIT


class ZendeskClient:
    """Client API pour extraire toutes les données de Zendesk"""
    
    def __init__(self):
        # Configuration de base
        self.domain = ZENDESK_DOMAIN
        self.email = ZENDESK_EMAIL
        self.token = ZENDESK_API_TOKEN
        self.base_url = f"https://{self.domain}/api/v2"
        
        # Configuration de la session HTTP
        self.session = requests.Session()
        self.session.auth = (f"{self.email}/token", self.token)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Limitation du taux de requêtes
        self.rate_limit = ZENDESK_RATE_LIMIT / 60  # requêtes par seconde
        self.last_request = 0
        
        print(f"Client Zendesk initialisé pour {self.domain}")
    
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
            print(f"Erreur API Zendesk: {e}")
            if hasattr(e.response, 'text'):
                print(f"Détails: {e.response.text}")
            raise
    
    def test_connection(self) -> bool:
        """Tester la connexion à Zendesk"""
        try:
            response = self._make_request("users", {"per_page": 1})
            if response.get('users'):
                print("Connexion Zendesk réussie")
                return True
            else:
                print("Erreur: réponse vide de l'API")
                return False
        except Exception as e:
            print(f"Échec de connexion: {e}")
            return False
    
    def get_all_tickets(self) -> List[Dict]:
        """Récupérer tous les tickets"""
        print("Récupération des tickets...")
        all_tickets = []
        endpoint = "tickets"
        
        # Paramètres pour récupérer par ordre chronologique
        params = {
            'sort_order': 'asc',
            'sort_by': 'created_at'
        }
        
        # Pagination Zendesk
        next_page = None
        page_count = 0
        
        while True:
            if next_page:
                response = requests.get(next_page, auth=self.session.auth)
                response.raise_for_status()
                data = response.json()
            else:
                data = self._make_request(endpoint, params)
            
            tickets = data.get('tickets', [])
            all_tickets.extend(tickets)
            
            page_count += 1
            print(f"Page {page_count}: {len(tickets)} tickets récupérés")
            
            next_page = data.get('next_page')
            if not next_page:
                break
        
        print(f"Total: {len(all_tickets)} tickets récupérés")
        return all_tickets
    
    def get_ticket_comments(self, ticket_id: int) -> List[Dict]:
        """Récupérer tous les commentaires d'un ticket"""
        endpoint = f"tickets/{ticket_id}/comments"
        
        try:
            data = self._make_request(endpoint)
            return data.get('comments', [])
        except Exception as e:
            print(f"Erreur commentaires ticket {ticket_id}: {e}")
            return []
    
    def get_tickets_with_comments(self) -> List[Dict]:
        """Récupérer tous les tickets avec leurs commentaires"""
        tickets = self.get_all_tickets()
        
        print(f"Récupération des commentaires pour {len(tickets)} tickets...")
        
        for i, ticket in enumerate(tickets):
            ticket_id = ticket['id']
            comments = self.get_ticket_comments(ticket_id)
            ticket['comments'] = comments

            # Afficher le progrès tous les 15 tickets
            if (i + 1) % 15 == 0:
                print(f"Traité {i + 1}/{len(tickets)} tickets")
        
        print("Commentaires récupérés pour tous les tickets")
        return tickets
    
    def get_all_users(self) -> List[Dict]:
        """Récupérer tous les contacts (utilisateurs end-user)"""
        print("Récupération des contacts...")
        all_contacts = []
        endpoint = "users"
        
        next_page = None
        page_count = 0
        
        while True:
            if next_page:
                response = requests.get(next_page, auth=self.session.auth)
                response.raise_for_status()
                data = response.json()
            else:
                data = self._make_request(endpoint)
            
            users = data.get('users', [])
            # Filtrer pour garder seulement les contacts (end-users)
            contacts = [user for user in users if user.get('role') == 'end-user']
            all_contacts.extend(contacts)
            
            page_count += 1
            print(f"Page {page_count}: {len(contacts)} contacts trouvés sur {len(users)} utilisateurs")
            
            next_page = data.get('next_page')
            if not next_page:
                break
        
        print(f"Total: {len(all_contacts)} contacts récupérés")
        return all_contacts
    
    def get_all_articles(self) -> List[Dict]:
        """Récupérer tous les articles du Help Center"""
        print("Récupération des articles Help Center...")
        all_articles = []
        endpoint = "help_center/articles"
        
        next_page = None
        page_count = 0
        
        while True:
            if next_page:
                response = requests.get(next_page, auth=self.session.auth)
                response.raise_for_status()
                data = response.json()
            else:
                data = self._make_request(endpoint)
            
            articles = data.get('articles', [])
            all_articles.extend(articles)
            
            page_count += 1
            print(f"Page {page_count}: {len(articles)} articles récupérés")
            
            next_page = data.get('next_page')
            if not next_page:
                break
        
        print(f"Total: {len(all_articles)} articles récupérés")
        return all_articles
    
    def get_all_macros(self) -> List[Dict]:
        """Récupérer toutes les macros"""
        print("Récupération des macros...")
        all_macros = []
        endpoint = "macros"
        
        next_page = None
        page_count = 0
        
        while True:
            if next_page:
                response = requests.get(next_page, auth=self.session.auth)
                response.raise_for_status()
                data = response.json()
            else:
                data = self._make_request(endpoint)
            
            macros = data.get('macros', [])
            all_macros.extend(macros)
            
            page_count += 1
            print(f"Page {page_count}: {len(macros)} macros récupérées")
            
            next_page = data.get('next_page')
            if not next_page:
                break
        
        print(f"Total: {len(all_macros)} macros récupérées")
        return all_macros
    
# # Test avec comptage pour vérifier l'intégrité des données
# def test_zendesk_client():
#     """Test du client avec vérification des totaux"""
#     print("Test du client Zendesk")
#     print("=" * 30)
    
#     client = ZendeskClient()
    
#     # Test de connexion
#     if not client.test_connection():
#         print("Test échoué - Vérifiez la configuration")
#         return False
    
#     # Vérification des totaux
#     print("\nVérification des totaux:")
    
#     try:
#         # Test tickets
#         tickets_response = client._make_request("tickets", {"per_page": 1})
#         tickets_total = tickets_response.get('count', 'Inconnu')
#         print(f"Tickets: {tickets_total}")
        
#         # Test contacts
#         users_response = client._make_request("users", {"per_page": 1})
#         all_users_count = users_response.get('count', 'Inconnu')
#         print(f"Utilisateurs total: {all_users_count}")
        
#         # Test articles
#         articles_response = client._make_request("help_center/articles", {"per_page": 1})
#         articles_total = articles_response.get('count', 'Inconnu')
#         print(f"Articles: {articles_total}")
        
#         # Test macros
#         macros_response = client._make_request("macros", {"per_page": 1})
#         macros_total = macros_response.get('count', 'Inconnu')
#         print(f"Macros: {macros_total}")
        
#     except Exception as e:
#         print(f"Erreur lors du test: {e}")
#         return False
    
#     print("\nTest réussi - Client opérationnel")
#     return True


# # Utilisation du client
# if __name__ == "__main__":
#     test_zendesk_client()
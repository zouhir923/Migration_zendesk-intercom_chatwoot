import requests
import json
import time
from typing import Dict, List, Optional, Any
from configs.config import ZENDESK_DOMAIN, ZENDESK_EMAIL, ZENDESK_API_TOKEN, ZENDESK_RATE_LIMIT


class ZendeskClient:
    """Client API pour extraire toutes les données de Zendesk avec backoff 429"""

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

        # Limitation du taux de requêtes (théorique)
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
        """
        Effectuer une requête API avec gestion d'erreurs et backoff 429.
        Réessaie automatiquement après la durée indiquée par Zendesk.
        """
        url = f"{self.base_url}/{endpoint}"

        while True:
            self._rate_limit_wait()
            try:
                response = self.session.get(url, params=params)

                # Gestion du rate-limit
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    print(f"⏳ Limite atteinte pour {endpoint}. Attente {retry_after} sec...")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Erreur API Zendesk sur {endpoint}: {e}")
                if hasattr(e.response, 'text'):
                    print(f"Détails: {e.response.text}")
                # Attente avant de réessayer en cas d'erreur temporaire
                time.sleep(3)
                continue

    def _make_paginated_request(self, initial_url: str) -> List[Dict]:
        """
        Gestion des appels paginés avec backoff 429
        """
        results = []
        next_page = initial_url

        while next_page:
            self._rate_limit_wait()
            try:
                response = self.session.get(next_page)

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    print(f"⏳ Limite atteinte. Attente {retry_after} sec...")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                data = response.json()

                # Ajoute les résultats en fonction du type
                for key in ["tickets", "users", "articles", "macros"]:
                    if key in data:
                        results.extend(data[key])

                next_page = data.get("next_page")

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Erreur API Zendesk: {e}, reprise après 5s...")
                time.sleep(5)
                continue

        return results

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
        endpoint = f"{self.base_url}/tickets.json?sort_order=asc&sort_by=created_at"
        tickets = self._make_paginated_request(endpoint)
        print(f"✅ Total: {len(tickets)} tickets récupérés")
        return tickets

    def get_ticket_comments(self, ticket_id: int) -> List[Dict]:
        """Récupérer tous les commentaires d'un ticket"""
        endpoint = f"tickets/{ticket_id}/comments"
        try:
            time.sleep(0.5)  # pause courte entre tickets
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

        print("✅ Commentaires récupérés pour tous les tickets")
        return tickets

    def get_all_users(self) -> List[Dict]:
        """Récupérer tous les contacts via l'API Incremental Export avec backoff 429"""
        print("Récupération des contacts (API Incremental Export)...")
        all_contacts = []
        start_time = 0
        next_page_url = f"{self.base_url}/incremental/users?start_time={start_time}&per_page=1000"

        while next_page_url:
            self._rate_limit_wait()
            try:
                response = self.session.get(next_page_url)

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    print(f"⏳ Limite atteinte (users). Attente {retry_after} sec...")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                data = response.json()

                users = data.get("users", [])
                contacts = [u for u in users if u.get("role") == "end-user" and u.get("active")]
                all_contacts.extend(contacts)

                print(f"🔄 {len(contacts)} contacts récupérés (total {len(all_contacts)})")

                next_page_url = data.get("next_page")
                if data.get("end_of_stream"):
                    print("✅ Fin de l'export incrémental atteinte.")
                    break

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Erreur API: {e}, reprise après 5s...")
                time.sleep(5)
                continue

        unique_contacts = {c["id"]: c for c in all_contacts}.values()
        print(f"✅ Total final: {len(unique_contacts)} contacts uniques récupérés")
        return list(unique_contacts)

    def get_all_articles(self) -> List[Dict]:
        """Récupérer tous les articles du Help Center"""
        print("Récupération des articles Help Center...")
        endpoint = f"{self.base_url}/help_center/articles.json"
        articles = self._make_paginated_request(endpoint)
        print(f"✅ Total: {len(articles)} articles récupérés")
        return articles

    def get_all_macros(self) -> List[Dict]:
        """Récupérer toutes les macros"""
        print("Récupération des macros...")
        endpoint = f"{self.base_url}/macros.json"
        macros = self._make_paginated_request(endpoint)
        print(f"✅ Total: {len(macros)} macros récupérées")
        return macros

    
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
#         users_response = client._make_request("users")
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
import requests
import json
import time
from typing import Dict, List, Optional, Any
from configs.config import CHATWOOT_BASE_URL, CHATWOOT_API_ACCESS_TOKEN, CHATWOOT_ACCOUNT_ID, CHATWOOT_RATE_LIMIT


class ChatwootClient:
    """Client API pour importer les données dans Chatwoot"""
    
    def __init__(self):
        # Configuration de base
        self.base_url = CHATWOOT_BASE_URL
        self.api_token = CHATWOOT_API_ACCESS_TOKEN
        self.account_id = CHATWOOT_ACCOUNT_ID
        
        # URLs des APIs
        self.application_api_url = f"{self.base_url}/api/v1"
        
        # Configuration de la session HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api_access_token': self.api_token
        })
        
        # Limitation du taux de requêtes
        self.rate_limit = CHATWOOT_RATE_LIMIT / 60  # requêtes par seconde
        self.last_request = 0
        
        print(f"Client Chatwoot initialisé pour le compte {self.account_id}")
    
    def _rate_limit_wait(self):
        """Attendre pour respecter les limites de taux"""
        current_time = time.time()
        time_since_last = current_time - self.last_request
        min_interval = 1 / self.rate_limit
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request = time.time()
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Effectuer une requête API avec gestion d'erreurs"""
        self._rate_limit_wait()
        url = f"{self.application_api_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PATCH":
                response = self.session.patch(url, json=data)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur API Chatwoot: {e}")
            if hasattr(e.response, 'text') and e.response is not None:
                print(f"Détails: {e.response.text}")
            raise
    
    def test_connection(self) -> bool:
        """Tester la connexion à Chatwoot"""
        try:
            endpoint = f"accounts/{self.account_id}"
            response = self._make_request("GET", endpoint)
            
            if response and 'name' in response:
                print(f"Connexion Chatwoot réussie - Compte: {response.get('name')}")
                return True
            else:
                print("Erreur: réponse inattendue de l'API")
                return False
                
        except Exception as e:
            print(f"Échec de connexion: {e}")
            return False
    
    def get_all_contacts(self) -> List[Dict]:
        """Récupérer tous les contacts existants pour éviter les doublons"""
        endpoint = f"accounts/{self.account_id}/contacts"
        try:
            response = self._make_request("GET", endpoint)
            contacts = response.get('payload', [])
            print(f"Contacts existants: {len(contacts)}")
            return contacts
        except Exception as e:
            print(f"Erreur récupération contacts: {e}")
            return []
    
    def create_contact(self, contact_data: Dict) -> Dict:
        """Créer un nouveau contact"""
        endpoint = f"accounts/{self.account_id}/contacts"
        
        # Validation des données requises
        required_fields = ['inbox_id', 'name']
        for field in required_fields:
            if field not in contact_data:
                raise ValueError(f"Champ requis manquant: {field}")
        
        try:
            response = self._make_request("POST", endpoint, contact_data)
            
            # Récupérer l'ID depuis payload.contact.id
            contact_id = None
            if 'payload' in response and 'contact' in response['payload']:
                contact_id = response['payload']['contact'].get('id')
            
            print(f"Contact créé: {contact_data.get('name')} (ID: {contact_id})")
            return response
            
        except Exception as e:
            print(f"Erreur création contact {contact_data.get('name', 'inconnu')}: {e}")
            raise

    def create_conversation(self, source_id: str, inbox_id: int, contact_id: int, status: str) -> Dict:
        """Créer une nouvelle conversation"""
        endpoint = f"accounts/{self.account_id}/conversations"
        
        conversation_data = {
            "source_id": source_id,
            "inbox_id": inbox_id,
            "contact_id": contact_id,
            "status": status
        }
        
        try:
            response = self._make_request("POST", endpoint, conversation_data)
            print(f"Conversation créée: ID {response.get('id')}")
            return response
        except Exception as e:
            print(f"Erreur création conversation: {e}")
            raise

    def create_message(self, conversation_id: int, content: str, message_type: str = "incoming", private: bool = False) -> Dict:
        """
        Créer un message dans une conversation
        message_type: "incoming" (client) ou "outgoing" (agent)
        """
        endpoint = f"accounts/{self.account_id}/conversations/{conversation_id}/messages"
        
        message_data = {
            "content": content,
            "message_type": message_type,
            "private": private,
            "content_type": "text"
        }
        
        try:
            response = self._make_request("POST", endpoint, message_data)
            print(f"Message ajouté à la conversation {conversation_id}")
            return response
        except Exception as e:
            print(f"Erreur création message: {e}")
            raise
    
    def get_conversation_details(self, conversation_id: int) -> Dict:
        """Obtenir les détails d'une conversation"""
        endpoint = f"accounts/{self.account_id}/conversations/{conversation_id}"
        try:
            response = self._make_request("GET", endpoint)
            return response
        except Exception as e:
            print(f"Erreur récupération conversation {conversation_id}: {e}")
            raise

    def update_conversation_status(self, conversation_id: int, status: str) -> Dict:
        """
        Mettre à jour le statut d'une conversation (open, resolved, pending).
        Exemple de status valides :
        - "open"
        - "resolved"
        - "pending"
        """
        endpoint = f"accounts/{self.account_id}/conversations/{conversation_id}/toggle_status"

        data = {
            "status": status
        }

        try:
            response = self._make_request("POST", endpoint, data)
            print(f"Statut de la conversation {conversation_id} mis à jour -> {status}")
            return response
        except Exception as e:
            print(f"Erreur mise à jour statut conversation {conversation_id}: {e}")
            raise
 
    def create_message_with_attachments(self, conversation_id: int, content: str = "", 
                                    message_type: str = "incoming", private: bool = False, 
                                    attachment_files: List[tuple] = None) -> Dict:
        """
        Créer un message avec pièces jointes directement (sans upload séparé)
        attachment_files: Liste de tuples (filename, file_content_bytes)
        """
        endpoint = f"accounts/{self.account_id}/conversations/{conversation_id}/messages"
        
        # Enlever temporairement le Content-Type JSON pour multipart
        old_headers = self.session.headers.copy()
        self.session.headers.pop('Content-Type', None)
        
        try:
            # Préparer les données du formulaire
            data = {
                'content': content or "",
                'message_type': message_type,
                'private': str(private).lower()
            }
            
            # Préparer les fichiers
            files = []
            if attachment_files:
                for filename, file_content in attachment_files:
                    files.append(('attachments[]', (filename, file_content)))
            
            url = f"{self.application_api_url}/{endpoint}"
            response = self.session.post(url, data=data, files=files)
            response.raise_for_status()
            
            # Restaurer les headers
            self.session.headers = old_headers
            
            print(f"Message avec {len(files)} pièces jointes ajouté")
            return response.json()
            
        except Exception as e:
            self.session.headers = old_headers
            print(f"Erreur création message avec attachments: {e}")
            raise
       
# client = ChatwootClient()
# client.update_conversation_status(64, "resolved")

# def test_chatwoot_client():
#     """Test simple du client Chatwoot"""
#     print("Test du client Chatwoot")
#     print("=" * 30)
    
#     client = ChatwootClient()
    
#     # 1. Test de connexion
#     if not client.test_connection():
#         print("Test échoué - Vérifiez la configuration")
#         return False
    
#     # 2. Test récupération contacts
#     try:
#         contacts = client.get_all_contacts()
#         print(f"API GET contacts: OK ({len(contacts)} contacts)")
#     except Exception as e:
#         print(f"API GET contacts: Erreur - {e}")
    
#     print("\nClient prêt pour l'import")
#     return True


# def test_chatwoot_complete():
#     """Test complet: contact + conversation + messages"""
#     print("Test complet Chatwoot API")
#     print("=" * 40)
    
#     client = ChatwootClient()
    
#     if not client.test_connection():
#         print("Connexion échouée")
#         return False
    
#     try:
#         INBOX_ID = 2  # Votre inbox ID
        
#         print(f"\n1. Création contact (inbox_id: {INBOX_ID})")
#         test_contact = {
#             "inbox_id": INBOX_ID,
#             "name": "Test Migration Contact",
#             "email": "migration.test@example.com", 
#             "phone_number": "+33987654321",
#             "identifier": f"migration_test_{int(time.time())}",
#             "additional_attributes": {
#                 "source": "migration_test",
#                 "original_platform": "zendesk"
#             }
#         }
        
#         created_contact = client.create_contact(test_contact)
        
#         # Extraire les données depuis payload
#         payload = created_contact.get('payload', {})
#         contact_data = payload.get('contact', {})
#         contact_id = contact_data.get('id')
#         contact_inboxes = contact_data.get('contact_inboxes', [])
        
#         if not contact_id or not contact_inboxes:
#             print("Erreur: données contact manquantes")
#             return False
        
#         source_id = contact_inboxes[0].get('source_id')
#         print(f"Contact: ID {contact_id}, Source ID: {source_id}")
        
#         print(f"\n2. Création conversation")
#         created_conversation = client.create_conversation(
#             source_id=source_id,
#             inbox_id=INBOX_ID, 
#             contact_id=contact_id
#         )
        
#         conversation_id = created_conversation.get('id')
#         if not conversation_id:
#             print("Erreur: conversation ID manquant")
#             return False
        
#         print(f"\n3. Ajout messages (simulation migration)")
        
#         # Message client original (incoming)
#         client.create_message(
#             conversation_id, 
#             "Date originale: 12/09/2025 09:15\n\n**Problème urgent:** Ma commande n'est pas arrivée et je dois partir en voyage demain. Pouvez-vous m'aider rapidement ?",
#             "incoming"
#         )
        
#         # Réponse agent (outgoing)  
#         client.create_message(
#             conversation_id,
#             "Date originale: 12/09/2025 09:47\n\nBonjour ! Je comprends votre urgence. Laissez-moi vérifier immédiatement le statut de votre commande. Pouvez-vous me donner votre numéro de commande ?",
#             "outgoing"
#         )
        
#         # Message client avec détails
#         client.create_message(
#             conversation_id,
#             "Date originale: 12/09/2025 09:52\n\nMerci ! Mon numéro de commande est **#CMD-789456**. J'ai commandé il y a 5 jours.",
#             "incoming"
#         )
        
#         print(f"\n4. Vérification conversation finale")
#         conversation_details = client.get_conversation_details(conversation_id)
#         messages_count = len(conversation_details.get('messages', []))
        
#         print(f"\nTEST COMPLET RÉUSSI !")
#         print(f"Contact: {contact_data.get('name')} (ID: {contact_id})")
#         print(f"Conversation: ID {conversation_id}")
#         print(f"Messages: {messages_count} ajoutés")
#         print(f"Status: {conversation_details.get('status')}")
        
#         return True
        
#     except Exception as e:
#         print(f"Erreur durant le test: {e}")
#         import traceback
#         traceback.print_exc()
#         return False


# # Utilisation du client
# if __name__ == "__main__":
#     import sys
    
#     if len(sys.argv) > 1 and sys.argv[1] == "--test-complete":
#         # Test complet avec contact + conversation + messages
#         test_chatwoot_complete()
#     else:
#         # Test simple de connexion
#         test_chatwoot_client()
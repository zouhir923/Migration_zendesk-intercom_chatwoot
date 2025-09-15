# 🚀 Migration Zendesk & Intercom vers Chatwoot

Projet privé pour transférer nos données depuis Zendesk et Intercom vers Chatwoot.

## 📋 Aperçu du Projet

Ce projet permet de migrer automatiquement **toutes les données importantes** depuis Zendesk et Intercom vers Chatwoot en utilisant leurs APIs officielles :

- ✅ **Tickets Zendesk** → Conversations Chatwoot  
  - `GET /api/v2/tickets.json`  
  - `GET /api/v2/tickets/{ticket_id}/comments.json` (pour récupérer tout l'historique des messages)

- ✅ **Articles Zendesk & Intercom** → Articles Chatwoot (Markdown)  
  - `GET /api/v2/help_center/articles.json` (Zendesk)  
  - `GET /articles` (Intercom)

- ✅ **Utilisateurs/Contacts** → Contacts Chatwoot  
  - `GET /api/v2/users.json` (Zendesk)  
  - `GET /contacts` (Intercom)

- ✅ **Macros / Réponses enregistrées** → Macros Chatwoot  
  - `GET /api/v2/macros.json` (Zendesk)

- ✅ **Groupes & Équipes** → Équipes Chatwoot  
  - `GET /api/v2/groups.json` (Zendesk)  
  - `GET /teams` et `GET /admins` (Intercom)

- ✅ **Conversations Intercom** → Conversations Chatwoot  
  - `GET /conversations` + `GET /conversations/{conversation_id}` (messages)

Chaque entité est transformée et adaptée au format attendu par Chatwoot :
- Conversion HTML → **Markdown** (articles, messages)
- Mapping des **tags → labels**
- Ajout des **dates** et de l'historique complet des conversations
- Association des **auteurs** (agents/contacts) pour conserver la fidélité des échanges

## 🏗️ Structure du Projet

```
chatwoot-migration/
├── .vscode/             # Configuration VS Code
├── configs/
│   └── config.py        # Configuration du projet
├── outputs/             # Données exportées/importées
│   ├── chatwoot/
│   ├── intercom/
│   └── zendesk/
├── src/
│   ├── main.py          # Point d'entrée principal
│   ├── api/             # Clients API pour chaque plateforme
│   │   ├── chatwoot_client.py
│   │   ├── intercom_client.py
│   │   └── zendesk_client.py
│   ├── services/        # Logique métier de migration
│   │   ├── chatwoot_service.py
│   │   ├── intercom_service.py
│   │   ├── mapping_service.py
│   │   ├── migration_service.py
│   │   └── zendesk_service.py
│   └── utils/           # Utilitaires (logs, helpers)
│       ├── helpers.py
│       └── rate_limiter.py
├── .env                 # Variables d'environnement
├── .gitignore
├── README.md
└── requirements.txt
```

## 🔧 Installation

1. **Cloner le projet :**
   ```bash
   git clone https://github.com/zouhir923/Migration_zendesk-intercom_chatwoot.git
   cd chatwoot-migration
   ```

2. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer les variables d'environnement :**
   - Créer le fichier `.env` à partir du modèle
   - Remplir avec nos clés API

## ⚙️ Configuration

Modifier le fichier `.env` avec nos informations :

```env
# Zendesk
ZENDESK_DOMAIN=alphorm.zendesk.com
ZENDESK_EMAIL=amine.sa@alphorm.com
ZENDESK_API_TOKEN=votre_token_zendesk

# Intercom
INTERCOM_ACCESS_TOKEN=votre_token_intercom

# Chatwoot
CHATWOOT_BASE_URL=https://chatwoot.alphorm.org
CHATWOOT_API_ACCESS_TOKEN=votre_token_chatwoot
CHATWOOT_ACCOUNT_ID=2

# Migration Settings
BATCH_SIZE=50
ZENDESK_RATE_LIMIT=700
INTERCOM_RATE_LIMIT=1000
CHATWOOT_RATE_LIMIT=600
```

## 🚀 Utilisation

```bash
# Lancer la migration complète
python src/main.py

```

## ⚠️ Important

- Les données sont exportées dans le dossier `outputs/`

---
**Développé avec hooo❤️b par zouhair harabazan pour nos migrations vers Chatwoot**
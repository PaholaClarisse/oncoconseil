# OncoConseil

Agent IA de conseil en oncologie — API backend FastAPI s'appuyant sur un pipeline RAG (Retrieval-Augmented Generation) construit à partir d'un document de référence en oncologie, et sur le LLM Gemini pour formuler les réponses finales.

Projet fil rouge — mentorat **LesCracks**.

## 🎯 Objectif

Un agent conversationnel spécialisé qui ne répond qu'à partir d'un corpus documentaire de référence en oncologie, et qui refuse explicitement de répondre si la question sort de ce périmètre — plutôt que d'improviser une réponse potentiellement dangereuse.

## 🛠️ Stack technique

| Brique | Choix |
|---|---|
| Framework API | FastAPI (Python) |
| Base de données relationnelle | PostgreSQL + SQLAlchemy + Alembic (migrations) |
| Authentification | JWT (access token) avec `python-jose` + hashing des mots de passe avec `passlib`/`bcrypt` |
| Base vectorielle (RAG) | ChromaDB en mode embarqué |
| Embeddings | Gemini (`gemini-embedding-001`) |
| LLM externe | Gemini (`gemini-3.5-flash-lite`) |
| Conteneurisation | Docker + docker-compose *(à venir, Échéance 5)* |

## 📁 Structure du projet

```
oncoconseil/
├── venv/                    # environnement virtuel (non versionné)
├── alembic/                 # migrations de base de données
├── alembic.ini
├── .env                     # variables d'environnement (non versionné)
├── .gitignore
├── requirements.txt
├── chroma_data/             # données ChromaDB (non versionné)
└── app/
    ├── main.py               # point d'entrée FastAPI
    ├── config.py             # lecture des variables d'environnement
    ├── database.py           # connexion SQLAlchemy à PostgreSQL, get_db()
    ├── vector_db.py           # connexion ChromaDB
    ├── models/                # classes SQLAlchemy (User, BlacklistToken, Document)
    ├── schemas/               # classes Pydantic (validation entrée/sortie API)
    ├── routes/                # endpoints (auth.py, admin.py)
    └── services/              # logique métier (auth.py, document_processor.py, chat_service.py)
```

## ⚙️ Installation

### 1. Cloner le projet et créer l'environnement virtuel

```bash
git clone <url-du-repo>
cd oncoconseil
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurer PostgreSQL

Créer un rôle et une base dédiés (principe du moindre privilège) :

```sql
CREATE USER oncoconseil_user WITH PASSWORD 'votre_mot_de_passe';
CREATE DATABASE oncoconseil_db OWNER oncoconseil_user;
GRANT ALL PRIVILEGES ON DATABASE oncoconseil_db TO oncoconseil_user;
```

### 3. Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

```
DB_NAME=oncoconseil_db
DB_USER=oncoconseil_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=votre_cle_secrete_aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
LLM_API_KEY=votre_cle_api_gemini
```

Générer une `SECRET_KEY` sécurisée :
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Obtenir une clé API Gemini gratuite sur [Google AI Studio](https://aistudio.google.com/apikey).

### 4. Appliquer les migrations

```bash
alembic upgrade head
```

### 5. Lancer le serveur

```bash
uvicorn app.main:app --reload
```

L'API est accessible sur `http://localhost:8000`, avec documentation interactive sur `http://localhost:8000/docs`.

## 📡 Endpoints disponibles

### Authentification (`/auth`)

| Méthode | Route | Description | Protégée |
|---|---|---|---|
| POST | `/auth/register` | Création de compte | Non |
| POST | `/auth/login` | Connexion, renvoie un token JWT (format OAuth2 : `username` = email) | Non |
| GET | `/auth/me` | Informations du compte connecté | Oui |
| POST | `/auth/logout` | Révocation du token courant (liste noire) | Oui |

### Base de connaissance (`/admin`)

| Méthode | Route | Description | Protégée |
|---|---|---|---|
| POST | `/admin/documents` | Upload d'un document oncologie → extraction, chunking, embeddings, indexation ChromaDB | Oui |
| GET | `/admin/documents` | Liste des documents indexés | Oui |
| DELETE | `/admin/documents/{id}` | Supprime un document et tous ses chunks associés (PostgreSQL + ChromaDB) | Oui |

### Chat IA — en cours de construction (Échéance 3)

Le pipeline de réponse (recherche vectorielle → scope-guard → prompt → appel LLM) est fonctionnel côté service (`app/services/chat_service.py`), la route `POST /chat/ask` reste à finaliser (Jour 11 : gestion des sessions et persistance des messages).

## 🔐 Sécurité

- Mots de passe hashés avec **bcrypt** (jamais stockés en clair)
- Authentification par **JWT**, avec révocation possible via une liste noire (`blacklist_tokens`) — un logout invalide immédiatement le token, même s'il n'est pas encore expiré
- Toutes les variables sensibles (mots de passe, clés API, clé de signature JWT) sont isolées dans `.env`, jamais commitées
- **Scope-guard** : toute question hors du périmètre oncologie est détectée par similarité vectorielle et rejetée **avant** l'appel au LLM (défense en profondeur, avec un garde-fou supplémentaire dans le prompt lui-même)

## 🧠 Fonctionnement du pipeline RAG

1. Le document de référence est découpé en chunks (fenêtre de mots avec chevauchement)
2. Chaque chunk est transformé en vecteur (embedding) et stocké dans ChromaDB, lié à son document d'origine
3. À chaque question posée, son embedding est comparé aux chunks stockés pour retrouver les plus pertinents
4. Si le meilleur score de similarité est trop faible, la question est rejetée comme hors périmètre — **sans appeler le LLM**
5. Sinon, un prompt est construit avec le contexte trouvé, la question, et des instructions de garde-fou (dont un refus explicite de tout pronostic vital, avec redirection vers un médecin)
6. Le LLM génère une réponse strictement basée sur ce contexte

## 📅 Avancement du projet

| Échéance | Statut |
|---|---|
| 1 — Authentification complète (Jours 1-4) | ✅ Terminée |
| 2 — Indexation du corpus oncologie (Jours 5-7) | ✅ Terminée |
| 3 — Cœur du RAG : `POST /chat/ask` (Jours 8-11) | 🔄 En cours (Jours 8, 9, 10 terminés) |
| 4 — Historique des conversations | 🔲 À venir |
| 5 — Robustesse, sécurité & conteneurisation | 🔲 À venir |

## 🌳 Stratégie Git

Une branche par fonctionnalité (`feature/<nom>`), fusionnée dans `main` via Pull Request une fois testée et validée.

# Hackathon Datacraft - Château de Versailles

## Prérequis

- Docker et Docker Compose installés sur votre machine
- Une clé API Mistral

## Configuration

1. Copiez le fichier `.env.example` vers `.env` :
```bash
cp .env.example .env
```

2. Modifiez le fichier `.env` et ajoutez votre clé API Mistral :
```
MISTRAL_API_KEY=votre-cle-api-mistral
MISTRAL_MODEL=mistral-medium-latest
EMBEDDING_MODEL=mistral-embed
```

## Lancement du projet

À la racine du projet, exécutez :
```bash
docker compose up --build
```

Une fois que les logs affichent les lignes suivantes :
```
backend-1  | INFO:     Started server process [1]
backend-1  | INFO:     Waiting for application startup.
backend-1  | INFO:     Application startup complete.
backend-1  | INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

## Accès aux services

- **Backend API** : [http://localhost:8001](http://localhost:8001) - Swagger UI pour tester l'API
- **Frontend** : [http://localhost:8501](http://localhost:8501) - Interface utilisateur Streamlit

## Test du chatbot

### Via l'API (Swagger UI)
1. Rendez-vous sur [http://localhost:8001](http://localhost:8001)
2. Cliquez sur le premier élément (POST /chat Chat With Agent)
3. Cliquez sur `Try it out`
4. Remplacez `string` par votre prompt dans le champ message
5. Cliquez sur `Exécuter`
6. La réponse s'affiche dans `Response body`

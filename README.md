# Hackathon Datacraft - Palace of Versailles

## Prerequisites

- Docker and Docker Compose installed on your machine
- A Mistral API key

## Configuration

1. Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

2. Edit the `.env` file and add your Mistral API key:
```
MISTRAL_API_KEY=your-mistral-api-key
MISTRAL_MODEL=mistral-medium-latest
EMBEDDING_MODEL=mistral-embed
```

## Launching the project

At the project root, run:
```bash
docker compose up --build
```

Once the logs display the following lines:
```
frontend-1  |
frontend-1  | Collecting usage statistics. To deactivate, set browser.gatherUsageStats to false.
frontend-1  |
frontend-1  |
frontend-1  |   You can now view your Streamlit app in your browser.
frontend-1  |
frontend-1  |   URL: http://0.0.0.0:8501
frontend-1  |
backend-1   | INFO:     Started server process [1]
backend-1   | INFO:     Waiting for application startup.
backend-1   | INFO:     Application startup complete.
backend-1   | INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

You can access the following services:

- **Backend API**: [http://localhost:8001](http://localhost:8001) - Swagger UI to test the API
- **Frontend**: [http://localhost:8501](http://localhost:8501) - Streamlit user interface

## Testing the chatbot

### Via the API (Swagger UI)
1. Go to [http://localhost:8001](http://localhost:8001)
2. Click on the first element (POST /chat Chat With Agent)
3. Click on `Try it out`
4. Replace `string` with your prompt in the message field
5. Click on `Execute`
6. The response is displayed in `Response body`

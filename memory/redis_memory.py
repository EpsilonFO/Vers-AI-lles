from langchain.memory import RedisChatMessageHistory, ConversationBufferMemory
import redis
import os

# Connexion Redis
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Historique des messages LangChain dans Redis
chat_history = RedisChatMessageHistory(
    redis_client=r, session_id="default_session"  # ou injecter session_id dynamique
)

# Mémoire ConversationBuffer pour l’agent
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=chat_history)

"""Multi-step agent for Versailles visit planning with integrated tools and memory."""

import os
import sys
sys.path.append(os.path.abspath('../tools'))
sys.path.append(os.path.abspath('../memory'))
sys.path.append(os.path.abspath('..'))

from langchain.agents import initialize_agent, AgentType
from langchain.llms import HuggingFacePipeline
from langchain.memory import RedisChatMessageHistory, ConversationBufferMemory
from dotenv import load_dotenv
import redis

# Import tools
from tools.check_versailles_availability import check_versailles_availability
from tools.book_versailles_tickets import book_versailles_tickets, check_ticket_availability
from tools.get_next_passage import get_next_passages
from tools.get_schedule_at_times import get_schedules_at_time
from tools.get_weather import get_weather
from tools.google_maps_tool import google_maps_route
from tools.search_train import search_train
from tools.book_train import book_train
from tools.search_airbnb import search_airbnb
from tools.book_airbnb import book_airbnb

# Import memory and prompts
from memory.memory import load_session, save_session
from prompts.reservation_prompt import reservation_template

# Load environment variables (optional, for Redis etc.)
load_dotenv()

# -----------------------------
# REDIS CONFIGURATION
# -----------------------------
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))

try:
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    r.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    print(f"Warning: Redis not available: {e}")
    REDIS_AVAILABLE = False

# -----------------------------
# LOCAL MISTRAL LLM CONFIG
# -----------------------------
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_name = "mistralai/Mistral-7B-Instruct-v0.1"  # remplacer par ton modèle local si téléchargé
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",  # GPU si dispo
    torch_dtype="auto"
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=512,
    temperature=0.2
)

llm = HuggingFacePipeline(pipeline=pipe)

# -----------------------------
# MEMORY
# -----------------------------
def get_memory(session_id: str):
    """
    Get conversation memory for the session.
    """
    if REDIS_AVAILABLE:
        try:
            chat_history = RedisChatMessageHistory(
                redis_client=r,
                session_id=session_id
            )
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                chat_memory=chat_history,
                return_messages=True
            )
            return memory
        except Exception as e:
            print(f"Error creating Redis memory: {e}")

    # Fallback in-memory
    return ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

# -----------------------------
# TOOLS
# -----------------------------
tools = [    
    # Transportation
    get_next_passages,
    get_schedules_at_time,
    search_train,
    book_train,
    
    # Accommodation
    search_airbnb,
    book_airbnb,
    
    # Practical info
    get_weather,
    google_maps_route
]

# -----------------------------
# AGENT CREATION
# -----------------------------
def create_agent(session_id: str):
    """
    Create an agent instance with memory and tools.
    """
    memory = get_memory(session_id)
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        agent_kwargs={"prefix": reservation_template}
    )
    return agent

# -----------------------------
# AGENT EXECUTION
# -----------------------------
def run_agent(session_id: str, user_message: str) -> str:
    """
    Execute the agent with user message and manage conversation state.
    """
    try:
        session_data = load_session(session_id)
        previous_context = session_data.get("chat_history", "")
        agent = create_agent(session_id)

        # Build context-aware message
        if previous_context:
            context_msg = f"Contexte précédent : {previous_context[-500:]}\n\nUtilisateur : {user_message}"
        else:
            context_msg = user_message

        response = agent.run(context_msg)

        # Save to backup memory
        session_data["chat_history"] = previous_context + f"\nUtilisateur : {user_message}\nAgent : {response}"
        save_session(session_id, session_data)

        return response

    except Exception as e:
        error_msg = f"Erreur lors du traitement de votre demande: {str(e)}"
        print(f"Agent error: {e}")
        return error_msg

# -----------------------------
# RESET SESSION
# -----------------------------
def reset_session(session_id: str):
    """
    Reset a session's conversation history.
    """
    try:
        if REDIS_AVAILABLE:
            chat_history = RedisChatMessageHistory(
                redis_client=r,
                session_id=session_id
            )
            chat_history.clear()
        
        save_session(session_id, {"chat_history": ""})
        print(f"Session {session_id} reset successfully")

    except Exception as e:
        print(f"Error resetting session: {e}")

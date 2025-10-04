import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import os

# --- Streamlit page config ---
st.set_page_config(
    page_title="👑 Versailles Assistant (GPU)",
    page_icon="🏰",
    layout="centered"
)

st.title("👑 Versailles Assistant (GPU powered)")
st.caption("Ask about tickets, schedules, travel, or accommodations at Versailles.")

# --- Load model from local path ---
@st.cache_resource
def load_mistral():
    model_path = r"C:\Users\sarah\Desktop\les_4_MousquetAIres\Mistral-7B-Instruct-v0.1"

    if not os.path.exists(model_path):
        st.error(f"❌ Model folder not found: {model_path}")
        st.stop()

    # Load tokenizer and model (GPU optimized)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,     # ✅ use half precision for GPU
        device_map="cuda",             # ✅ load directly to CUDA
        low_cpu_mem_usage=True
    )

    # Build text generation pipeline
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=0,                      # use CUDA:0
        max_new_tokens=512,
        temperature=0.3,
        do_sample=True,
        top_p=0.9
    )
    return pipe

# --- Load model ---
with st.spinner("Loading Mistral model on GPU... ⚡"):
    pipe = load_mistral()

st.success("✅ Mistral loaded on GPU successfully!")

# --- Session management ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Input ---
user_input = st.chat_input("Ask me about Versailles...")

def generate_response(user_message: str) -> str:
    """
    Generate a response from the local Mistral model.
    """
    prompt = f"""You are a polite and expert travel assistant for visitors at Château de Versailles.
Answer clearly and concisely.

User: {user_message}
Answer:"""

    # Run inference on GPU
    outputs = pipe(prompt)
    full_text = outputs[0]["generated_text"]
    response = full_text.split("Answer:")[-1].strip()
    return response

# --- Chat interaction ---
if user_input:
    with st.spinner("Thinking... 🤔"):
        response = generate_response(user_input)

    st.session_state.history.append(("👩‍💬 You", user_input))
    st.session_state.history.append(("🤖 Assistant", response))

# --- Display chat history ---
for speaker, msg in st.session_state.history:
    if "You" in speaker:
        st.markdown(f"**{speaker}:** {msg}")
    else:
        st.markdown(f"> 💬 **{speaker}:** {msg}")

# --- Reset button ---
if st.button("🧹 Reset conversation"):
    st.session_state.history = []
    st.success("Chat cleared ✅")

# --- GPU Info ---
if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    st.sidebar.success(f"🟢 GPU detected: {gpu_name}")
    st.sidebar.write(f"Memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
    st.sidebar.write(f"Memory reserved: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
else:
    st.sidebar.error("⚠️ CUDA GPU not detected.")

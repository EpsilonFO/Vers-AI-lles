import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import os

# --- Configuration de la page ---
st.set_page_config(
    page_title="👑 Versailles Assistant",
    page_icon="🏰",
    layout="centered"
)

st.title("👑 Assistant du Château de Versailles")
st.caption("Posez vos questions sur les billets, horaires, transports, hébergements, ou météo à Versailles.")

# --- Chargement du modèle Mistral local ---
@st.cache_resource
def load_mistral():
    # 🔹 Utilisation du chemin local vers le modèle
    model_path = "Mistral-7B-Instruct-v0.1"

    # Vérifie que le dossier existe
    '''if not os.path.exists(model_path):
        st.error(f"❌ Le dossier du modèle n'existe pas : {model_path}")
        st.stop()'''

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        temperature=0.3,
        do_sample=True,
        top_p=0.9
    )
    return pipe

with st.spinner("Chargement du modèle local Mistral... ⏳"):
    pipe = load_mistral()

st.success("Modèle Mistral chargé avec succès ✅")

# --- Gestion de la session ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Entrée utilisateur ---
user_input = st.chat_input("Écrivez votre question ici...")

def generate_response(user_message: str) -> str:
    """
    Génère la réponse à partir du modèle local.
    """
    prompt = f"""Tu es un assistant de voyage expert du Château de Versailles.
Réponds de manière claire, polie et utile à la question suivante :

Utilisateur : {user_message}
Réponse :"""

    output = pipe(prompt)[0]["generated_text"]
    response = output.split("Réponse :")[-1].strip()
    return response

# --- Interaction utilisateur ---
if user_input:
    with st.spinner("L'assistant réfléchit... 🤔"):
        response = generate_response(user_input)

    # Sauvegarde dans l'historique
    st.session_state.history.append(("👩‍💬 Vous", user_input))
    st.session_state.history.append(("🤖 Assistant", response))

# --- Affichage du chat ---
for speaker, msg in st.session_state.history:
    if "Vous" in speaker:
        st.markdown(f"**{speaker}:** {msg}")
    else:
        st.markdown(f"> 💬 **{speaker}:** {msg}")

# --- Bouton reset ---
if st.button("🧹 Réinitialiser la conversation"):
    st.session_state.history = []
    st.success("Conversation réinitialisée ✅")

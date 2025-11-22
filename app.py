import streamlit as st
import google.generativeai as genai
from datetime import datetime

# 1. CONFIGURATION DE L'IA
# On récupère la clé secrète qu'on a mise dans les réglages
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("La clé API n'est pas configurée dans les Secrets Streamlit.")

# On définit le modèle (le cerveau)
model = genai.GenerativeModel('gemini-pro')

# 2. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Mon Suivi Fitness", page_icon="💪")
st.title("💪 Mon Coach Personnel")

# Initialisation de l'historique de discussion si vide
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es un coach sportif expert et bienveillant. Tu aides l'utilisateur à suivre sa nutrition et son sport. Sois concis et motivant."}
    ]

# 3. LES ONGLETS
tab1, tab2, tab3 = st.tabs(["🏋️‍♂️ Entrainement", "🥗 Nutrition", "🧠 Coach IA"])

# --- ONGLET SPORT ---
with tab1:
    st.header("Ajouter une séance")
    col1, col2 = st.columns(2)
    with col1:
        exo = st.text_input("Exercice", placeholder="Ex: Squat")
    with col2:
        poids = st.number_input("Poids (kg)", step=0.5)
        reps = st.number_input("Répétitions", step=1, value=10)
    
    if st.button("Valider la série"):
        info_seance = f"J'ai fait {reps} répétitions à {poids}kg au {exo}."
        st.success(f"Noté : {exo} - {poids}kg x {reps}")
        # On ajoute l'info à la mémoire de l'IA
        st.session_state.messages.append({"role": "user", "content": info_seance})

# --- ONGLET NUTRITION ---
with tab2:
    st.header("Suivi Repas")
    repas = st.text_area("Qu'as-tu mangé ?", placeholder="Ex: Omelette 3 oeufs, 100g riz...")
    
    if st.button("Analyser ce repas"):
        # On envoie direct à l'IA pour analyse
        prompt_repas = f"Analyse nutritionnelle approximative (cal/prot) pour : {repas}. Sois bref."
        response = model.generate_content(prompt_repas)
        st.info(response.text)
        # On ajoute à la mémoire
        st.session_state.messages.append({"role": "user", "content": f"J'ai mangé : {repas}"})

# --- ONGLET IA (CHAT) ---
with tab3:
    st.header("Discuter avec ton Coach")
    
    # Afficher l'historique
    for msg in st.session_state.messages:
        if msg["role"] != "system": # On cache l'instruction système
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # Zone de saisie
    user_input = st.chat_input("Pose une question ou demande un bilan...")
    
    if user_input:
        # Afficher le message utilisateur
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Réflexion de l'IA
        # On construit le contexte pour Gemini
        history_for_ai = [{"role": "user", "parts": [m["content"]]} for m in st.session_state.messages if m["role"] != "system"]
        # On ajoute l'instruction système au début
        instruction_systeme = "Agis comme un coach sportif. Prends en compte les infos que l'utilisateur t'a données (repas/sport) pour répondre."
        
        try:
            chat = model.start_chat(history=history_for_ai)
            response = chat.send_message(instruction_systeme + " " + user_input)
            
            with st.chat_message("assistant"):
                st.write(response.text)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")

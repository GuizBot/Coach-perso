import streamlit as st
import google.generativeai as genai
from datetime import datetime

# 1. CONFIGURATION DE L'IA
try:
    # Récupération de la clé
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # ATTENTION : C'est ici qu'on a mis le bon nom trouvé grâce au scan
    model = genai.GenerativeModel('models/gemini-2.0-flash')
except Exception as e:
    st.error(f"Erreur de configuration : {e}")

# 2. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Mon Suivi Fitness", page_icon="💪")
st.title("💪 Mon Coach Personnel")

# Initialisation de l'historique de discussion si vide
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "parts": ["Tu es un coach sportif expert. Sois concis, motivant et précis sur la nutrition."]},
        {"role": "model", "parts": ["Compris ! Je suis prêt à t'aider pour tes entraînements et ta nutrition."]}
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
        # On ajoute l'info à la mémoire de l'IA pour qu'elle s'en souvienne
        st.session_state.messages.append({"role": "user", "parts": [info_seance]})
        st.session_state.messages.append({"role": "model", "parts": ["C'est noté !"]})

# --- ONGLET NUTRITION ---
with tab2:
    st.header("Suivi Repas")
    repas = st.text_area("Qu'as-tu mangé ?", placeholder="Ex: Omelette 3 oeufs, 100g riz...")
    
    if st.button("Analyser ce repas"):
        # On envoie direct à l'IA pour analyse
        try:
            prompt_repas = f"Analyse nutritionnelle approximative (cal/prot) pour : {repas}. Sois très bref (format liste)."
            response = model.generate_content(prompt_repas)
            st.info(response.text)
            
            # On ajoute à la mémoire
            st.session_state.messages.append({"role": "user", "parts": [f"J'ai mangé : {repas}"]})
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {e}")

# --- ONGLET IA (CHAT) ---
with tab3:
    st.header("Discuter avec ton Coach")
    
    # Afficher l'historique (on saute les 2 premiers messages de configuration système)
    for msg in st.session_state.messages[2:]:
        role_affiche = "user" if msg["role"] == "user" else "assistant"
        with st.chat_message(role_affiche):
            st.write(msg["parts"][0])

    # Zone de saisie
    user_input = st.chat_input("Pose une question ou demande un bilan...")
    
    if user_input:
        # 1. Afficher le message utilisateur
        with st.chat_message("user"):
            st.write(user_input)
        
        # 2. Ajouter à l'historique
        st.session_state.messages.append({"role": "user", "parts": [user_input]})

        # 3. Réflexion de l'IA
        try:
            # On envoie tout l'historique pour qu'il ait le contexte
            chat = model.start_chat(history=st.session_state.messages)
            response = chat.send_message(user_input) # On renvoie le dernier input pour déclencher la réponse
            
            # 4. Afficher la réponse
            with st.chat_message("assistant"):
                st.write(response.text)
            
            # 5. Sauvegarder la réponse (correction : on n'ajoute pas manuellement car start_chat le gère parfois, 
            # mais ici on veut garder le contrôle de l'état session_state, donc on ne l'ajoute que si nécessaire.
            # Pour simplifier avec Streamlit, on met juste à jour notre liste locale)
            # Note : L'objet 'chat' garde son propre historique, mais nous on veut le garder dans session_state
            # pour qu'il ne disparaisse pas si on change d'onglet.
            
            # On remplace le dernier message ajouté par la réponse correcte du modèle dans notre state
            # (L'objet chat a ajouté l'user et le model automatiquement dans son instance, mais pas dans notre liste)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")

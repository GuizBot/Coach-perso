import streamlit as st
import google.generativeai as genai
import gspread
from datetime import datetime

# --- 1. CONFIGURATION & CONNEXIONS ---
st.set_page_config(page_title="Mon Suivi Fitness", page_icon="💪")
st.title("💪 Mon Coach Personnel")

# A. Connexion à Google Sheets (Le Mémoire)
try:
    gc = gspread.service_account_from_dict(st.secrets["gsheets"])
    sh = gc.open("Suivi Fitness") # Le nom de ton fichier sur Drive
    worksheet = sh.sheet1
except Exception as e:
    st.error("⚠️ Erreur de connexion au Google Sheet.")
    st.warning("As-tu bien partagé le fichier 'Suivi Fitness' avec l'email du robot ?")
    st.stop()

# B. Connexion à l'IA (Le Cerveau)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.0-flash')
except Exception as e:
    st.error(f"Erreur IA : {e}")

# --- 2. FONCTIONS UTILES ---

def ajouter_ligne(type_data, contenu, details):
    """Ajoute une ligne dans le Google Sheet"""
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    heure_str = now.strftime("%H:%M")
    # Ordre des colonnes : Date | Heure | Type | Contenu | Détails
    worksheet.append_row([date_str, heure_str, type_data, contenu, details])

def lire_historique():
    """Récupère les 20 dernières lignes pour l'IA"""
    data = worksheet.get_all_values()
    # On garde les titres + les 20 dernières lignes
    if len(data) > 20:
        return [data[0]] + data[-20:]
    return data

# --- 3. INTERFACE UTILISATEUR ---

tab1, tab2, tab3 = st.tabs(["🏋️‍♂️ Entrainement", "🥗 Nutrition", "🧠 Coach IA"])

# === ONGLET SPORT ===
with tab1:
    st.header("Nouvelle Séance")
    col1, col2 = st.columns(2)
    with col1:
        exo = st.text_input("Exercice", placeholder="Ex: Développé Couché")
    with col2:
        poids = st.number_input("Poids (kg)", step=0.5, min_value=0.0)
        reps = st.number_input("Répétitions", step=1, value=10)
    
    if st.button("Enregistrer la série"):
        if exo:
            details_str = f"{poids}kg x {reps}"
            ajouter_ligne("SPORT", exo, details_str)
            st.success(f"✅ Ajouté : {exo} ({details_str})")
        else:
            st.warning("Indique le nom de l'exercice.")

# === ONGLET NUTRITION ===
with tab2:
    st.header("Mes Macros du jour")
    col_a, col_b = st.columns(2)
    with col_a:
        cal = st.number_input("🔥 Calories", step=10)
        prot = st.number_input("🥩 Protéines (g)", step=1)
    with col_b:
        glu = st.number_input("🍚 Glucides (g)", step=1)
        lip = st.number_input("🥑 Lipides (g)", step=1)
        
    if st.button("Valider la journée"):
        resume = f"{cal} kcal"
        details_str = f"P:{prot}g | G:{glu}g | L:{lip}g"
        ajouter_ligne("NUTRITION", resume, details_str)
        st.success("✅ Nutrition sauvegardée dans le Drive !")

# === ONGLET COACH IA ===
with tab3:
    st.header("Analyse & Conseils")
    
    # Historique de chat (session locale)
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "model", "parts": ["Bonjour ! Je suis connecté à ton fichier Excel. Je vois tes progrès. On fait le point ?"]}]

    # Affichage du chat
    for msg in st.session_state.messages:
        role = "assistant" if msg["role"] == "model" else "user"
        with st.chat_message(role):
            st.write(msg["parts"][0])

    user_input = st.chat_input("Ex: Analyse ma semaine, est-ce que je progresse ?")

    if user_input:
        # 1. Affiche le message user
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "parts": [user_input]})

        # 2. L'IA réfléchit
        with st.spinner("Je lis ton fichier Excel..."):
            # On récupère les données réelles du Sheet
            donnees_sheet = lire_historique()
            donnees_str = str(donnees_sheet)
            
            # On prépare le prompt avec le contexte
            prompt_systeme = f"""
            Tu es un coach sportif expert. Voici l'historique récent de l'utilisateur (format CSV issu d'un Google Sheet) :
            {donnees_str}
            
            Utilise ces données pour répondre à la question : "{user_input}"
            Sois motivant, précis, et base-toi sur les chiffres fournis.
            """
            
            try:
                response = model.generate_content(prompt_systeme)
                text_rep = response.text
                
                with st.chat_message("assistant"):
                    st.write(text_rep)
                st.session_state.messages.append({"role": "model", "parts": [text_rep]})
            except Exception as e:
                st.error(f"Erreur : {e}")

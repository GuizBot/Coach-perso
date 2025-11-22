import streamlit as st
from datetime import datetime

# 1. Configuration de la page
st.set_page_config(page_title="Mon Suivi Fitness", page_icon="💪")

# 2. Titre et Introduction
st.title("💪 Mon Coach Personnel")
st.write("Bienvenue dans ton espace de suivi.")

# 3. Création des onglets
tab1, tab2, tab3 = st.tabs(["🏋️‍♂️ Entrainement", "🥗 Nutrition", "🧠 Analyse IA"])

# --- ONGLET SPORT ---
with tab1:
    st.header("Ajouter une séance")
    col1, col2 = st.columns(2)
    with col1:
        date_sport = st.date_input("Date", datetime.now())
        exo = st.text_input("Exercice (ex: Développé Couché)")
    with col2:
        poids = st.number_input("Poids (kg)", min_value=0.0, step=0.5)
        reps = st.number_input("Répétitions", min_value=0, step=1)
    
    if st.button("Enregistrer la série"):
        st.success(f"Série notée : {exo} - {poids}kg x {reps}")

# --- ONGLET NUTRITION ---
with tab2:
    st.header("Suivi Repas")
    repas = st.text_area("Description du repas (ex: 100g de riz, 1 steak, brocolis)")
    calories = st.number_input("Estimation Calories", step=10)
    
    if st.button("Enregistrer le repas"):
        st.success("Repas ajouté !")

# --- ONGLET IA (VIDE POUR L'INSTANT) ---
with tab3:
    st.info("Ici, on connectera bientôt ton Gem Gemini pour analyser tes progrès !")

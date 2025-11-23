import streamlit as st
import google.generativeai as genai
import gspread
from datetime import datetime

# --- 1. CONFIGURATION & CONNEXIONS ---
st.set_page_config(page_title="Mon Suivi Fitness", page_icon="💪")
st.title("💪 Mon Coach Personnel")

# A. Connexion à Google Sheets (Silencieuse)
try:
    gc = gspread.service_account_from_dict(st.secrets["gsheets"])
    sh = gc.open("Suivi Fitness")
    worksheet = sh.sheet1
except Exception as e:
    st.error("⚠️ Erreur de connexion au Google Sheet.")
    st.info("Vérifie les secrets et le partage du fichier.")
    st.stop()

# B. Connexion à l'IA
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.0-flash')
except Exception as e:
    st.error(f"Erreur IA : {e}")

# --- 2. FONCTIONS UTILES ---

def ajouter_ligne(type_data, contenu, details):
    """Ajoute une ligne dans le Google Sheet"""
    now = datetime.now()
    date_str = now

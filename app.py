import streamlit as st
import google.generativeai as genai

st.title("🛠️ Diagnostic de Connexion")

# 1. Vérification de la clé
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.success("✅ Clé API trouvée dans les Secrets.")
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"❌ Erreur de lecture de la clé : {e}")
    st.stop()

# 2. Scan des modèles disponibles
st.write("Tentative de connexion à Google... Recherche des modèles...")

try:
    liste_modeles = genai.list_models()
    trouve = False
    
    st.write("### Modèles détectés :")
    for m in liste_modeles:
        if 'generateContent' in m.supported_generation_methods:
            st.code(f"Nom système : {m.name}")
            trouve = True
            
    if not trouve:
        st.error("⚠️ La connexion fonctionne, mais aucun modèle de texte n'est disponible pour cette clé.")
    else:
        st.success("✅ Connexion réussie ! Copie un des noms ci-dessus (ex: models/gemini-pro).")

except Exception as e:
    st.error("❌ CRASH TOTAL : Impossible de contacter Google.")
    st.error(f"Détail de l'erreur : {e}")

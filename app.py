import streamlit as st
import google.generativeai as genai
import time

st.set_page_config(page_title="Agente de Alta Performance", layout="wide")
st.title("🤖 Assistente de Equipe")

# 1. Configuração da API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

@st.cache_resource
def carregar_modelo():
    # Buscando o modelo disponível na sua conta
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            return genai.GenerativeModel(m.name)
    return None

model = carregar_modelo()

# 2. Ler a base
with open("base.txt", "r", encoding="utf-8") as f:
    conhecimento = f.read()

# 3. Chat simples (sem histórico longo para economizar tokens)
if "messages" not in st.session_state:
    st.session_state.messages = []

if prompt := st.chat_input("Perqunte algo..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Enviamos apenas a base + a pergunta atual (para não estourar a cota)
        prompt_final = f"Base: {conhecimento}\n\nPergunta: {prompt}"
        
        try:
            response = model.generate_content(prompt_final)
            st.markdown(response.text)
        except Exception as e:
            if "429" in str(e):
                st.error("Limite de velocidade atingido. Por favor, aguarde 60 segundos e tente novamente.")
            else:
                st.error(f"Erro: {e}")

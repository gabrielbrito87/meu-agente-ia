import streamlit as st
import google.generativeai as genai

# Título do site
st.title("🤖 Assistente da Equipe (Google Gemini)")

# Conectando com a chave do Google
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Lendo sua base de conhecimento
with open("base.txt", "r", encoding="utf-8") as f:
    conhecimento = f.read()

# Chat
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Como posso ajudar?"):
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        # Criando o contexto para o Gemini
        prompt_completo = f"Base de conhecimento: {conhecimento}\n\nPergunta do usuário: {pergunta}"
        
        response = model.generate_content(prompt_completo)
        texto_ai = response.text
        
        st.markdown(texto_ai)
        st.session_state.mensagens.append({"role": "assistant", "content": texto_ai})

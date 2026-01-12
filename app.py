import streamlit as st
import google.generativeai as genai

st.title("🤖 Assistente da Equipe")

# 1. Configurando a Chave
try:
    minha_chave = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=minha_chave)
    # Mudamos o nome para 'gemini-1.5-flash' (garantindo que não haja erros de digitação)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro na chave ou configuração: {e}")

# 2. Lendo a base
with open("base.txt", "r", encoding="utf-8") as f:
    conhecimento = f.read()

# --- Interface do Chat ---
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
        try:
            # Instrução reforçada para a IA
            prompt_sistema = f"Você é um assistente da equipe. Use esta base para responder: {conhecimento}"
            
            # Chamada da resposta
            response = model.generate_content([prompt_sistema, pergunta])
            
            st.markdown(response.text)
            st.session_state.mensagens.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Ocorreu um erro ao gerar a resposta: {e}")
            st.info("Dica: Verifique se sua chave do Google no Streamlit Secrets está correta.")

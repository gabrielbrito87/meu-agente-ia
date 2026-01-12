import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Assistente da Equipe", page_icon="🤖")
st.title("🤖 Assistente Colaborativo")

# 1. Configurando a Chave
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Truque para evitar o erro 404: vamos tentar o nome mais comum
    # Se falhar, ele avisará
    model_name = 'gemini-1.5-flash' 
    model = genai.GenerativeModel(model_name)
except Exception as e:
    st.error(f"Erro de configuração: {e}")

# 2. Lendo a base de conhecimento
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
except FileNotFoundError:
    st.error("Arquivo base.txt não encontrado no GitHub!")
    conhecimento = ""

# --- Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Pergunte algo sobre a base ou envie um link..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Enviamos a base de conhecimento como 'instrução de sistema'
            instrucao = f"Você é um assistente da equipe. Baseie-se exclusivamente nisto: {conhecimento}"
            
            # Gerando a resposta
            response = model.generate_content([instrucao, prompt])
            
            resposta_texto = response.text
            st.markdown(resposta_texto)
            st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
            
        except Exception as e:
            st.error(f"Erro ao conversar com a IA: {e}")
            st.info("Dica: Verifique se sua chave no Streamlit Secrets está correta e sem aspas extras.")

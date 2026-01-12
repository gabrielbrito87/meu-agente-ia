import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Diagnóstico de Agente", layout="wide")
st.title("🤖 Agente: Modo de Diagnóstico")

# 1. Configuração da API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configure a GOOGLE_API_KEY nos Secrets do Streamlit!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. MÁGICA: Listar o que está disponível para VOCÊ
modelos_disponiveis = []
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            modelos_disponiveis.append(m.name)
    
    if modelos_disponiveis:
        st.success(f"Modelos encontrados: {', '.join(modelos_disponiveis)}")
        # Vamos tentar o primeiro da lista, seja ele qual for!
        nome_escolhido = modelos_disponiveis[0]
        model = genai.GenerativeModel(nome_escolhido)
    else:
        st.error("Sua chave não tem nenhum modelo disponível para gerar conteúdo.")
        st.stop()
except Exception as e:
    st.error(f"Erro ao listar modelos: {e}")
    st.stop()

# 3. Ler a base
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
except:
    conhecimento = "Base não encontrada."

# 4. Chat Simples
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pergunte algo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Prompt focado em usar a base
            prompt_final = f"Base de conhecimento: {conhecimento}\n\nPergunta: {prompt}"
            response = model.generate_content(prompt_final)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro na resposta: {e}")

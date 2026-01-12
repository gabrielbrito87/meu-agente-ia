import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Agente da Equipe", layout="wide")
st.title("🤖 Assistente Especialista")

# 1. Configuração da API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Chave não configurada nos Secrets do Streamlit!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. MÁGICA: Procurar qual modelo o seu Google liberou
@st.cache_resource
def buscar_modelo_funcional():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Prioriza o 'flash', se não tiver, pega o primeiro da lista
        for m in modelos:
            if 'flash' in m:
                return m
        return modelos[0] if modelos else None
    except Exception as e:
        return str(e)

modelo_nome = buscar_modelo_funcional()

# 3. Ler a base de conhecimento
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
    st.sidebar.success(f"✅ Base carregada: {len(conhecimento)} caracteres")
    with st.sidebar.expander("Ver conteúdo lido"):
        st.write(conhecimento)
except:
    conhecimento = ""
    st.sidebar.error("❌ Arquivo base.txt não encontrado")

# 4. Chat e Lógica
if isinstance(modelo_nome, str) and modelo_nome.startswith('models/'):
    st.caption(f"Conectado via: {modelo_nome}")
    model = genai.GenerativeModel(modelo_nome)
else:
    st.error(f"Erro ao localizar modelo: {modelo_nome}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pergunte algo sobre a base..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Super Prompt para forçar o uso da base
        prompt_completo = f"""
        Você é um assistente que SÓ responde usando a base abaixo.
        Se não souber, diga que não está na base.
        
        BASE DE CONHECIMENTO:
        {conhecimento}
        
        PERGUNTA: {prompt}
        """
        try:
            response = model.generate_content(prompt_completo)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro na resposta: {e}")

import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Assistente da Equipe", page_icon="🤖")
st.title("🤖 Assistente Colaborativo")

# 1. Configurando a Chave
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Chave GOOGLE_API_KEY não encontrada nos Secrets do Streamlit!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Lendo a base de conhecimento
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
except Exception:
    st.error("Erro ao ler o arquivo base.txt. Verifique se ele existe no GitHub.")
    conhecimento = ""

# 3. MÁGICA: Descobrindo qual modelo usar automaticamente
@st.cache_resource # Isso evita que ele fique procurando toda hora
def buscar_modelo_disponivel():
    try:
        for m in genai.list_models():
            # Procuramos um modelo que aceite gerar conteúdo (Flash ou Pro)
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except Exception as e:
        st.error(f"Erro ao listar modelos: {e}")
    return None

nome_do_modelo = buscar_modelo_disponivel()

if not nome_do_modelo:
    st.error("Nenhum modelo disponível foi encontrado para esta chave API.")
    st.stop()
else:
    # Mostra apenas para você saber qual ele escolheu (pode apagar essa linha depois)
    st.caption(f"Conectado via: {nome_do_modelo}")
    model = genai.GenerativeModel(nome_do_modelo)

# --- Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Enviamos a base de conhecimento + a pergunta
            prompt_final = f"Base de Conhecimento:\n{conhecimento}\n\nPergunta: {prompt}"
            
            response = model.generate_content(prompt_final)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro na resposta: {e}")

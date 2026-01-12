import streamlit as st
import google.generativeai as genai
from google.generativeai import caching
import datetime
import PyPDF2

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Agente de Elite ⚡", page_icon="🤖", layout="wide")

# --- LOGIN (Mantido) ---
def check_password():
    if st.session_state.get("authenticated"): return True
    st.title("🔐 Acesso Restrito")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u == st.secrets["LOGIN_USER"] and p == st.secrets["LOGIN_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Dados incorretos.")
    return False

if check_password():
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

    # --- GERENCIADOR DE CACHE DINÂMICO ---
    @st.cache_resource(ttl=3600)
    def configurar_ai_dinamico(texto_base):
        CACHE_DISPLAY_NAME = "cache_equipe_final"
        
        try:
            # 1. Busca automática pelo modelo que suporta cache em 2026
            modelo_valido = None
            for m in genai.list_models():
                # Procuramos versões estáveis (com números no final) que sejam Flash
                if 'gemini-1.5-flash' in m.name and any(char.isdigit() for char in m.name):
                    modelo_valido = m.name
                    break
            
            if not modelo_valido:
                modelo_valido = "models/gemini-1.5-flash" # Último recurso

            # 2. Verifica se já existe um cache para não gastar
            for c in caching.CachedContent.list():
                if c.display_name == CACHE_DISPLAY_NAME:
                    return genai.GenerativeModel.from_cached_content(cached_content=c)
            
            # 3. Cria o cache com o modelo que encontramos
            with st.spinner(f"⚡ Otimizando memória com {modelo_valido}..."):
                novo_cache = caching.CachedContent.create(
                    model=modelo_valido,
                    display_name=CACHE_DISPLAY_NAME,
                    contents=[texto_base],
                    ttl=datetime.timedelta(hours=24),
                )
                return genai.GenerativeModel.from_cached_content(cached_content=novo_cache)
        
        except Exception as e:
            st.sidebar.warning(f"Modo normal (sem cache): {e}")
            return genai.GenerativeModel("models/gemini-1.5-flash")

    # --- CARREGAMENTO ---
    try:
        with open("base.txt", "r", encoding="utf-8") as f:
            base_conteudo = f.read()
    except:
        st.error("Arquivo base.txt não encontrado.")
        st.stop()

    model = configurar_ai_dinamico(base_conteudo)

    # --- INTERFACE ---
    st.markdown("<h1 style='text-align: center;'>🤖 Assistente Inteligente</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Painel de Controle")
        st.info(f"Base: {len(base_conteudo):,} caracteres")
        pdf_file = st.file_uploader("Auditar PDF", type=["pdf"])
        if st.button("Sair"):
            st.session_state.authenticated = False
            st.rerun()

    # Processamento PDF
    extra_text = ""
    if pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        extra_text = "\n".join([p.extract_text() for p in reader.pages])
        st.toast("PDF carregado!")

    # --- CHAT ---
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Sua dúvida..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                input_final = f"Contexto Extra: {extra_text}\n\nPergunta: {prompt}"
                response = model.generate_content(input_final)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                if "429" in str(e):
                    st.error("Limite atingido. Aguarde 1 minuto.")
                else:
                    st.error(f"Erro: {e}")

import streamlit as st
import google.generativeai as genai
from google.generativeai import caching
import datetime
import PyPDF2

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Agente de Elite ⚡", page_icon="🤖", layout="wide")

# --- LOGIN ---
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

    # --- GERENCIADOR DE CACHE (VERSÃO ESTÁVEL) ---
    @st.cache_resource(ttl=3600)
    def configurar_ai(texto_base):
        # NOME TÉCNICO EXATO (Essencial para evitar o erro 404 no cache)
        MODELO_ESTAVEL = "models/gemini-1.5-flash-001"
        CACHE_DISPLAY_NAME = "cache_equipe_v3"
        
        try:
            # 1. Verifica se já existe um cache ativo para economizar
            for c in caching.CachedContent.list():
                if c.display_name == CACHE_DISPLAY_NAME:
                    st.sidebar.success("⚡ Memória de Cache Ativa")
                    return genai.GenerativeModel.from_cached_content(cached_content=c)
            
            # 2. Se não existir, cria usando a versão estável 001
            with st.spinner("🧠 Carregando base na memória prioritária..."):
                novo_cache = caching.CachedContent.create(
                    model=MODELO_ESTAVEL,
                    display_name=CACHE_DISPLAY_NAME,
                    contents=[texto_base],
                    ttl=datetime.timedelta(hours=24),
                )
                return genai.GenerativeModel.from_cached_content(cached_content=novo_cache)
        
        except Exception as e:
            # Fallback caso o cache falhe (garante que o app não pare)
            st.sidebar.warning(f"Usando modo normal (sem cache): {e}")
            return genai.GenerativeModel("models/gemini-1.5-flash")

    # --- CARREGAMENTO ---
    with open("base.txt", "r", encoding="utf-8") as f:
        base_conteudo = f.read()

    model = configurar_ai(base_conteudo)

    # --- INTERFACE ---
    st.markdown("<h1 style='text-align: center;'>🤖 Assistente Inteligente</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Ferramentas")
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
        st.toast(f"PDF {pdf_file.name} carregado!")

    # --- CHAT ---
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Sua dúvida..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # O comando agora é leve, a base já está "decorada" no modelo
                input_final = f"Contexto Adicional: {extra_text}\n\nPergunta: {prompt}"
                response = model.generate_content(input_final)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Erro na resposta: {e}")

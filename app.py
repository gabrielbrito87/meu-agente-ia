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

    # --- GERENCIADOR DE CACHE DINÂMICO ---
    @st.cache_resource(ttl=3600)
    def configurar_ai_dinamico(texto_base):
        CACHE_DISPLAY_NAME = "cache_equipe_final"
        
        # Em 2026, tentamos primeiro o nome estável simples
        MODELO_NOME = "gemini-1.5-flash" 
        
        try:
            # 1. Tenta listar caches existentes para reaproveitar
            for c in caching.CachedContent.list():
                if c.display_name == CACHE_DISPLAY_NAME:
                    return genai.GenerativeModel.from_cached_content(cached_content=c)
            
            # 2. Tenta criar o cache (Isso requer Billing/Faturamento ativo no Google Cloud)
            with st.spinner("⚡ Otimizando memória (Context Caching)..."):
                novo_cache = caching.CachedContent.create(
                    model=f"models/{MODELO_NOME}",
                    display_name=CACHE_DISPLAY_NAME,
                    contents=[texto_base],
                    ttl=datetime.timedelta(hours=24),
                )
                return genai.GenerativeModel.from_cached_content(cached_content=novo_cache)
        
        except Exception as e:
            # SE DER ERRO 404 OU QUALQUER OUTRO NO CACHE:
            # Ele cai aqui e usa o modelo normal, sem frescuras.
            st.sidebar.warning("Aviso: Usando modo direto (sem otimização de cache).")
            # Tentamos o modelo sem o prefixo 'models/' caso o erro persista
            return genai.GenerativeModel(model_name=MODELO_NOME)

    # --- CARREGAMENTO ---
    try:
        with open("base.txt", "r", encoding="utf-8") as f:
            base_conteudo = f.read()
    except:
        st.error("Arquivo base.txt não encontrado no GitHub.")
        st.stop()

    # Inicializa o modelo (com ou sem cache, dependendo do sucesso acima)
    model = configurar_ai_dinamico(base_conteudo)

    # --- INTERFACE ---
    st.markdown("<h1 style='text-align: center;'>🤖 Assistente Inteligente</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Painel de Controle")
        st.info(f"Base carregada: {len(base_conteudo):,} caracteres")
        pdf_file = st.file_uploader("Auditar PDF Extra", type=["pdf"])
        if st.button("Sair"):
            st.session_state.authenticated = False
            st.rerun()

    # Processamento de PDF (se houver)
    extra_text = ""
    if pdf_file:
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            extra_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            st.toast("PDF lido com sucesso!")
        except Exception as e:
            st.error(f"Erro ao ler PDF: {e}")

    # --- SISTEMA DE CHAT ---
    if "messages" not in st.session_state: 
        st.session_state.messages = []

    # Mostra o histórico
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): 
            st.markdown(m["content"])

    # Entrada do usuário
    if prompt := st.chat_input("Como posso ajudar?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.

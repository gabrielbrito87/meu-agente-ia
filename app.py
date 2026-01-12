import streamlit as st
import google.generativeai as genai
from google.generativeai import caching
import datetime
import PyPDF2

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Agente de Elite (Cache ON)", page_icon="⚡", layout="wide")

st.markdown("""<style>
    .stButton>button { border-radius: 10px; background-color: #007bff; color: white; font-weight: bold; }
    .titulo { color: #1E3A8A; text-align: center; font-weight: bold; }
    .stAlert { border-radius: 10px; }
</style>""", unsafe_allow_html=True)

# --- 2. SISTEMA DE LOGIN ---
def check_password():
    if st.session_state.get("authenticated"): return True
    st.markdown("<h1 class='titulo'>🛡️ Acesso Restrito</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container(border=True):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("Entrar no Sistema"):
                if u == st.secrets["LOGIN_USER"] and p == st.secrets["LOGIN_PASSWORD"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else: st.error("Credenciais inválidas.")
    return False

if check_password():
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

    # --- 3. GERENCIADOR DE CACHE (ECONOMIA DE CUSTOS) ---
    @st.cache_resource(ttl=3600) # Atualiza a referência interna a cada hora
    def obter_modelo_com_cache(texto_base):
        # Nome único para identificar seu cache no servidor do Google
        CACHE_ID = "cache_v2026_equipe"
        MODELO_ESTAVEL = "models/gemini-1.5-flash-002"
        
        try:
            # Tenta localizar se o cache já existe no Google para não gastar criando outro
            for c in caching.CachedContent.list():
                if c.display_name == CACHE_ID:
                    return genai.GenerativeModel.from_cached_content(cached_content=c)
            
            # Se não existir, cria um novo (Isso acontece 1x por dia ou quando expirar)
            with st.spinner("🚀 Criando cache de memória (Otimizando custos)..."):
                novo_cache = caching.CachedContent.create(
                    model=MODELO_ESTAVEL,
                    display_name=CACHE_ID,
                    system_instruction="Você é um consultor que responde EXCLUSIVAMENTE com base na base de conhecimento fornecida.",
                    contents=[texto_base],
                    ttl=datetime.timedelta(hours=24), # Cache dura 24h
                )
                return genai.GenerativeModel.from_cached_content(cached_content=novo_cache)
        except Exception as e:
            st.sidebar.warning(f"Modo normal ativo (Cache offline): {e}")
            return genai.GenerativeModel("models/gemini-1.5-flash")

    # --- 4. CARREGAR BASE ---
    try:
        with open("base.txt", "r", encoding="utf-8") as f:
            base_txt = f.read()
    except:
        st.error("Erro: base.txt não encontrado.")
        st.stop()

    model = obter_modelo_com_cache(base_txt)

    # --- 5. INTERFACE LATERAL ---
    with st.sidebar:
        st.markdown("### 📊 Painel do Agente")
        st.info(f"Base: {len(base_txt):,} caracteres")
        st.divider()
        arquivo_pdf = st.file_uploader("Auditar Documento (PDF)", type=["pdf"])
        st.divider()
        if st.button("Sair do Sistema"):
            st.session_state.authenticated = False
            st.rerun()

    # --- 6. PROCESSAMENTO DE PDF ---
    texto_extra = ""
    if arquivo_pdf:
        try:
            reader = PyPDF2.PdfReader(arquivo_pdf)
            texto_extra = "\n".join([p.extract_text() for p in reader.pages])
            st.success(f"PDF '{arquivo_pdf.name}' pronto para análise.")
        except: st.error("Erro ao ler PDF.")

    # --- 7. CHAT ---
    st.markdown("<h2 style='text-align: center;'>🤖 Consultor Inteligente</h2>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Como posso ajudar com a base de dados?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Agora o envio é leve e rápido porque a base já está no Cache
                instrucao_curta = f"Documento extra para análise: {texto_extra}\n\nPergunta do usuário: {prompt}"
                
                with st.spinner("Consultando memória..."):
                    response = model.generate_content(instrucao_curta)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Erro: {e}")

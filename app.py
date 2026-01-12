import streamlit as st
import google.generativeai as genai
from google.generativeai import caching
import datetime
import PyPDF2

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Agente de Elite ⚡", page_icon="🤖", layout="wide")

# --- SISTEMA DE LOGIN ---
def check_password():
    if st.session_state.get("authenticated"):
        return True
    st.title("🔐 Acesso Restrito")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u == st.secrets["LOGIN_USER"] and p == st.secrets["LOGIN_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Dados incorretos.")
    return False

# Só executa o resto se estiver logado
if check_password():
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

    # --- CONFIGURAÇÃO DA IA ---
    @st.cache_resource(ttl=3600)
    def configurar_ai(texto_base):
        # Nome do modelo corrigido para evitar erro 404 em 2026
        MODELO_NOME = "gemini-1.5-flash"
        
        try:
            # Tentativa de usar Cache para economizar recursos
            CACHE_NAME = "cache_agente_elite"
            for c in caching.CachedContent.list():
                if c.display_name == CACHE_NAME:
                    return genai.GenerativeModel.from_cached_content(cached_content=c)
            
            with st.spinner("⚡ Preparando cérebro da IA..."):
                novo_cache = caching.CachedContent.create(
                    model=f"models/{MODELO_NOME}",
                    display_name=CACHE_NAME,
                    contents=[texto_base],
                    ttl=datetime.timedelta(hours=24),
                )
                return genai.GenerativeModel.from_cached_content(cached_content=novo_cache)
        except Exception:
            # Plano B: Se o cache falhar, usa o modelo normal
            return genai.GenerativeModel(model_name=MODELO_NOME)

    # --- CARREGAR BASE DE CONHECIMENTO ---
    try:
        with open("base.txt", "r", encoding="utf-8") as f:
            base_conteudo = f.read()
    except FileNotFoundError:
        st.error("Erro: Arquivo base.txt não encontrado.")
        st.stop()

    model = configurar_ai(base_conteudo)

    # --- INTERFACE DO USUÁRIO ---
    st.markdown("<h1 style='text-align: center;'>🤖 Assistente Inteligente</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Painel de Controle")
        st.info(f"Base: {len(base_conteudo):,} caracteres")
        pdf_file = st.file_uploader("Upload de PDF Extra", type=["pdf"])
        if st.button("Sair"):
            st.session_state.authenticated = False
            st.rerun()

    # Processar PDF se enviado
    extra_text = ""
    if pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        extra_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        st.toast("PDF lido com sucesso!")

    # --- CHAT ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar histórico
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Nova pergunta
    if prompt := st.chat_input("Como posso ajudar?"):
        # Adiciona pergunta do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Mostra o balão do usuário
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gera e mostra a resposta da IA
        with st.chat_message("assistant"):
            try:
                # Combinar contexto do PDF com a pergunta
                contexto_final = f"PDF: {extra_text}\n\nPergunta: {prompt}" if extra_text else prompt
                
                response = model.generate_content(contexto_final)
                texto_resposta = response.text
                
                st.markdown(texto_resposta)
                st.session_state.messages.append({"role": "assistant", "content": texto_resposta})
            except Exception as e:
                st.error(f"Erro ao gerar resposta: {e}")
    # Entrada do usuário
    if prompt := st.chat_input("Como posso ajudar?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):

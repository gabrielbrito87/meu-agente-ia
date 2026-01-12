import streamlit as st
import google.generativeai as genai
from google.generativeai import caching
import datetime
import PyPDF2

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Agente de Elite ⚡", page_icon="🤖", layout="wide")

# --- 2. SISTEMA DE LOGIN ---
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

# Só executa o código abaixo se o login estiver correto
if check_password():
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

    # --- 3. CONFIGURAÇÃO DA IA ---
    @st.cache_resource(ttl=3600)
    def configurar_ai(texto_base):
        MODELO_NOME = "gemini-1.5-flash"
        try:
            CACHE_NAME = "cache_agente_elite"
            # Tenta reutilizar um cache existente
            for c in caching.CachedContent.list():
                if c.display_name == CACHE_NAME:
                    return genai.GenerativeModel.from_cached_content(cached_content=c)
            
            # Se não existir, tenta criar
            with st.spinner("⚡ Otimizando base de conhecimento..."):
                novo_cache = caching.CachedContent.create(
                    model=f"models/{MODELO_NOME}",
                    display_name=CACHE_NAME,
                    contents=[texto_base],
                    ttl=datetime.timedelta(hours=24),
                )
                return genai.GenerativeModel.from_cached_content(cached_content=novo_cache)
        except Exception:
            # Se der erro no cache, usa o modelo normal (Plano B)
            return genai.GenerativeModel(model_name=MODELO_NOME)

    # --- 4. CARREGAR ARQUIVO BASE ---
    try:
        with open("base.txt", "r", encoding="utf-8") as f:
            base_conteudo = f.read()
    except Exception:
        st.error("Arquivo base.txt não encontrado.")
        st.stop()

    model = configurar_ai(base_conteudo)

    # --- 5. INTERFACE ---
    st.markdown("<h1 style='text-align: center;'>🤖 Assistente Inteligente</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Painel")
        st.info(f"Base: {len(base_conteudo):,} caracteres")
        pdf_file = st.file_uploader("Upload PDF Extra", type=["pdf"])
        if st.button("Sair"):
            st.session_state.authenticated = False
            st.rerun()

    # Processar PDF
    extra_text = ""
    if pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        extra_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        st.toast("PDF lido!")

    # --- 6. CHAT ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensagens anteriores
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Campo de nova pergunta
    if prompt := st.chat_input("Sua dúvida..."):
        # Adiciona ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Mostra a pergunta do usuário (Aqui estava o erro!)
        with st.chat_message("user"):
            st.markdown(prompt)

        # Resposta da IA
        with st.chat_message("assistant"):
            try:
                # Combina tudo (PDF + Pergunta)
                ctx = f"Contexto PDF: {extra_text}\n\nPergunta: {prompt}" if extra_text else prompt
                response = model.generate_content(ctx)
                
                # Exibe a resposta
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Erro ao responder: {e}")

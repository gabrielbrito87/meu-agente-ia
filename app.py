import streamlit as st
import google.generativeai as genai
import PyPDF2

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Agente de Elite", page_icon="🤖", layout="wide")

# CSS para visual moderno - CORRIGIDO AQUI
st.markdown("""
    <style>
    .titulo-principal { color: #1E3A8A; text-align: center; font-weight: bold; }
    .stButton>button { border-radius: 10px; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN SEGURO ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True

    if "LOGIN_USER" not in st.secrets or "LOGIN_PASSWORD" not in st.secrets:
        st.error("Erro: Configure LOGIN_USER e LOGIN_PASSWORD nos Secrets do Streamlit.")
        return False

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 class='titulo-principal'>🛡️ Acesso Interno</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.button("Entrar no Sistema"):
                if usuario == st.secrets["LOGIN_USER"] and senha == st.secrets["LOGIN_PASSWORD"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    return False

# Execução do App
if check_password():
    # 1. Configuração IA
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    @st.cache_resource
    def carregar_modelo():
        try:
            modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            for m in modelos:
                if 'gemini-1.5-flash' in m: return genai.GenerativeModel(m)
            return genai.GenerativeModel(modelos[0]) if modelos else None
        except:
            return None

    model = carregar_modelo()

    # 2. Interface Principal
    st.markdown("<h1 style='text-align: center;'>🤖 Assistente de Inteligência</h1>", unsafe_allow_html=True)
    st.divider()

    # Barra Lateral
    with st.sidebar:
        st.header("Painel de Controle")
        try:
            with open("base.txt", "r", encoding="utf-8") as f:
                conhecimento = f.read()
            st.success(f"📚 Base: {len(conhecimento)} carac.")
        except:
            conhecimento = "Base não encontrada."
            st.error("Arquivo base.txt não encontrado.")
        
        st.divider()
        arquivo_equipe = st.file_uploader("Upload (PDF/TXT)", type=["txt", "pdf"])
        
        if st.button("Sair"):
            st.session_state.authenticated = False
            st.rerun()

    # 3. Processamento de Arquivos
    def extrair_texto_pdf(arquivo):
        try:
            pdf_reader = PyPDF2.PdfReader(arquivo)
            return "".join([p.extract_text() for p in pdf_reader.pages])
        except: return "Erro ao ler PDF."

    texto_do_arquivo = ""
    if arquivo_equipe:
        if arquivo_equipe.type == "application/pdf":
            texto_do_arquivo = extrair_texto_pdf(arquivo_equipe)
        else:
            texto_do_arquivo = arquivo_equipe.read().decode("utf-8", errors="ignore")
        st.info(f"🔎 Analisando: {arquivo_equipe.name}")

    # 4. Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Sua dúvida..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if model is None:
                st.error("IA não disponível.")
            else:
                instrucao = f"Base: {conhecimento}\nArquivo: {texto_do_arquivo}\nPergunta: {prompt}"
                try:
                    with st.spinner('Consultando base...'):
                        response = model.generate_content(instrucao)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Erro: {e}")

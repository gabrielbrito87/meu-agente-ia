import streamlit as st
import google.generativeai as genai
import PyPDF2

# --- CONFIGURAÇÃO DA PÁGINA E DESIGN ---
st.set_page_config(page_title="Agente de Elite", page_icon="🤖", layout="wide")

# CSS para deixar o visual mais moderno
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .titulo-principal {
        color: #1E3A8A;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: bold;
        text-align: center;
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_input=True)

# --- SISTEMA DE LOGIN (Mantido) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True

    # Tela de Login com Visual Centralizado
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
                    st.error("Credenciais inválidas.")
    return False

if check_password():
    # --- CABEÇALHO DO APP ---
    col_logo, col_titulo = st.columns([1, 8])
    with col_logo:
        st.markdown("# 🤖")
    with col_titulo:
        st.markdown("<h1 style='margin-bottom: 0;'>Assistente de Inteligência Colaborativa</h1>", unsafe_allow_html=True)
        st.caption("Especialista em base de conhecimento e auditoria de documentos")
    
    st.divider()

    # --- CONFIGURAÇÃO IA ---
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    @st.cache_resource
    def carregar_modelo():
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
        return None

    model = carregar_modelo()

    # --- BARRA LATERAL ESTILIZADA ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        st.header("Painel de Controle")
        
        try:
            with open("base.txt", "r", encoding="utf-8") as f:
                conhecimento = f.read()
            st.success(f"📚 Base Ativa: {len(conhecimento)} carac.")
        except:
            conhecimento = ""
            st.error("Base não encontrada.")

        st.divider()
        st.subheader("📁 Auditoria de Arquivos")
        arquivo_equipe = st.sidebar.file_uploader("Upload (PDF/TXT)", type=["txt", "pdf"])
        
        st.divider()
        if st.button("Encerrar Sessão"):
            st.session_state.authenticated = False
            st.rerun()

    # --- PROCESSAMENTO DE ARQUIVO ---
    def extrair_texto_pdf(arquivo):
        pdf_reader = PyPDF2.PdfReader(arquivo)
        texto = ""
        for pagina in pdf_reader.pages:
            texto += pagina.extract_text()
        return texto

    texto_do_arquivo = ""
    if arquivo_equipe:
        if arquivo_equipe.type == "application/pdf":
            texto_do_arquivo = extrair_texto_pdf(arquivo_equipe)
        else:
            texto_do_arquivo = arquivo_equipe.read().decode("utf-8", errors="ignore")
        st.info(f"🔎 Analisando o documento: **{arquivo_equipe.name}**")

    # --- CHAT ESTILIZADO ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá! Sou seu assistente de elite. No que posso ajudar hoje?"}
        ]

    # Container para o chat ficar organizado
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Digite sua dúvida aqui..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            instrucao = f"Você é um consultor. Use a base: {conhecimento}. Arquivo atual: {texto_do_arquivo}. Pergunta: {prompt}"
            try:
                # Efeito de carregamento para ficar mais bonito
                with st.spinner('Consultando base de conhecimento...'):
                    response = model.generate_content(instrucao)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")

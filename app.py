import streamlit as st
import google.generativeai as genai
import PyPDF2

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Agente Protegido", layout="wide")

# --- SISTEMA DE LOGIN ---
def check_password():
    """Retorna True se o usuário introduziu as credenciais corretas."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔐 Acesso Restrito")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if usuario == st.secrets["LOGIN_USER"] and senha == st.secrets["LOGIN_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    return False

# Só executa o resto do app se o login for bem-sucedido
if check_password():
    
    # --- TÍTULO E CONFIGURAÇÃO IA ---
    st.title("🤖 Assistente e Analisador de Documentos")
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

    @st.cache_resource
    def carregar_modelo():
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
        return None

    model = carregar_modelo()

    # --- CARREGAR BASE ---
    try:
        with open("base.txt", "r", encoding="utf-8") as f:
            conhecimento = f.read()
        st.sidebar.success(f"✅ Base: {len(conhecimento)} caracteres")
    except:
        conhecimento = ""
        st.sidebar.error("Arquivo base.txt não encontrado.")

    # --- FUNÇÃO PDF ---
    def extrair_texto_pdf(arquivo):
        pdf_reader = PyPDF2.PdfReader(arquivo)
        texto = ""
        for pagina in pdf_reader.pages:
            texto += pagina.extract_text()
        return texto

    # --- BARRA LATERAL (UPLOAD E SAIR) ---
    st.sidebar.divider()
    if st.sidebar.button("Sair / Logout"):
        st.session_state.authenticated = False
        st.rerun()

    st.sidebar.header("📁 Avaliar Novo Documento")
    arquivo_equipe = st.sidebar.file_uploader("Envie um arquivo (PDF ou TXT)", type=["txt", "pdf"])

    texto_do_arquivo = ""
    if arquivo_equipe:
        if arquivo_equipe.type == "application/pdf":
            texto_do_arquivo = extrair_texto_pdf(arquivo_equipe)
        else:
            texto_do_arquivo = arquivo_equipe.read().decode("utf-8", errors="ignore")
        st.sidebar.info(f"📄 Arquivo '{arquivo_equipe.name}' carregado!")

    # --- CHAT ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Pergunte algo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            instrucao = f"""
            Você é um consultor da equipe.
            BASE DE CONHECIMENTO: {conhecimento}
            ARQUIVO PARA AVALIAÇÃO: {texto_do_arquivo if texto_do_arquivo else "Nenhum."}
            PERGUNTA: {prompt}
            """
            try:
                response = model.generate_content(instrucao)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Erro: {e}")

import streamlit as st
import google.generativeai as genai
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

if check_password():
    # Configura a chave da API
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

    # --- 3. CONFIGURAÇÃO DA IA (Simplificada para evitar Erro 404) ---
    # Removido o sistema de 'caching' que estava causando o erro 404
    @st.cache_resource
    def carregar_modelo():
        # Usamos o nome mais estável possível
        return genai.GenerativeModel("gemini-1.5-flash")

    # --- 4. CARREGAR ARQUIVO BASE ---
    try:
        with open("base.txt", "r", encoding="utf-8") as f:
            base_conteudo = f.read()
    except Exception:
        base_conteudo = "Instruções base não encontradas."
        st.sidebar.warning("Aviso: base.txt não encontrado.")

    model = carregar_modelo()

    # --- 5. INTERFACE ---
    st.markdown("<h1 style='text-align: center;'>🤖 Assistente Inteligente</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Painel")
        pdf_file = st.file_uploader("Upload PDF Extra", type=["pdf"])
        if st.button("Sair"):
            st.session_state.authenticated = False
            st.rerun()

    # Processar PDF
    extra_text = ""
    if pdf_file:
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            extra_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            st.toast("PDF lido com sucesso!")
        except:
            st.error("Erro ao ler o PDF.")

    # --- 6. CHAT ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar histórico
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Nova pergunta
    if prompt := st.chat_input("Sua dúvida..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Criamos um "Prompt de Sistema" enviando a base.txt junto
                # Isso substitui o cache de forma simples e funcional
                prompt_completo = (
                    f"Instruções/Base de Conhecimento:\n{base_conteudo}\n\n"
                    f"Contexto do PDF adicional:\n{extra_text}\n\n"
                    f"Pergunta do usuário: {prompt}"
                )
                
                response = model.generate_content(prompt_completo)
                
                if response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Erro na conexão com o Google Gemini: {e}")
                st.info("Dica: Verifique se sua API Key é válida no Google AI Studio.")

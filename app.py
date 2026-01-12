import streamlit as st
import google.generativeai as genai
import PyPDF2

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Agente de Elite ⚡", page_icon="🤖")

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

    # --- AUTO-DETECÇÃO DE MODELO ---
    @st.cache_resource
    def inicializar_modelo():
        try:
            # Lista todos os modelos disponíveis para a sua chave
            modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # Tenta encontrar qualquer variação do Flash disponível em 2026
            flash_disponivel = next((m for m in modelos if "flash" in m.lower()), None)
            
            if flash_disponivel:
                return genai.GenerativeModel(flash_disponivel)
            else:
                # Se não achar Flash, pega o primeiro disponível (pode ser Pro)
                return genai.GenerativeModel(modelos[0])
        except Exception as e:
            st.error(f"Erro ao listar modelos: {e}")
            return None

    model = inicializar_modelo()

    # --- CARREGAR BASE ---
    try:
        with open("base.txt", "r", encoding="utf-8") as f:
            base_conteudo = f.read()
    except:
        base_conteudo = "Sem base de conhecimento."

    # --- INTERFACE ---
    st.title("🤖 Assistente de Elite")
    
    with st.sidebar:
        pdf_file = st.file_uploader("PDF Extra", type=["pdf"])
        if st.button("Sair"):
            st.session_state.authenticated = False
            st.rerun()

    extra_text = ""
    if pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        extra_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        st.toast("PDF lido!")

    # --- CHAT ---
    if "messages" not in st.session_state: st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Sua dúvida..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            if model:
                try:
                    full_prompt = f"Base: {base_conteudo}\n\nPDF: {extra_text}\n\nPergunta: {prompt}"
                    response = model.generate_content(full_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Erro na resposta: {e}")
            else:
                st.error("Nenhum modelo compatível encontrado na sua conta Google.")

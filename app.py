import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Agente de Equipe", layout="wide")
st.title("🤖 Assistente Colaborativo")

# 1. Configuração da API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta a chave nos Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Tentar carregar o modelo com o nome completo
# O prefixo 'models/' ajuda a evitar o erro 404
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro ao carregar modelo: {e}")

# 3. Ler a base de conhecimento
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
    st.sidebar.success(f"✅ Base carregada ({len(conhecimento)} caracteres)")
except:
    conhecimento = "Base não encontrada."
    st.sidebar.error("❌ Arquivo base.txt não encontrado.")

# 4. Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Upload de arquivo
arquivo = st.sidebar.file_uploader("Enviar arquivo", type=["txt", "pdf"])
conteudo_arquivo = ""
if arquivo:
    try:
        conteudo_arquivo = arquivo.read().decode("utf-8")
        st.sidebar.info("Arquivo lido com sucesso.")
    except:
        st.sidebar.error("Não consegui ler este arquivo.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pergunte algo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Criamos um "Super Prompt" que junta tudo
        prompt_completo = f"""
        Você é um assistente que responde APENAS com base na base de conhecimento abaixo.
        
        BASE DE CONHECIMENTO:
        {conhecimento}
        
        ARQUIVO ENVIADO PELO USUÁRIO AGORA:
        {conteudo_arquivo}
        
        PERGUNTA DO USUÁRIO:
        {prompt}
        
        Responda de forma clara e profissional.
        """
        
        try:
            # Gerar resposta de forma simples
            response = model.generate_content(prompt_completo)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro na API: {e}")

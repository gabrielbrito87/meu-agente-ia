import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Agente de Equipe", layout="wide")
st.title("🤖 Assistente de Consultas e Arquivos")

# 1. Configuração da API com busca automática de modelo
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configure a GOOGLE_API_KEY nos Secrets do Streamlit!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

@st.cache_resource
def carregar_modelo():
    # Lista de nomes que o Google costuma usar para o modelo Flash
    tentativas = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-1.5-flash-latest']
    
    for nome in tentativas:
        try:
            m = genai.GenerativeModel(nome)
            # Testa se o modelo responde
            m.generate_content("oi", generation_config={"max_output_tokens": 1})
            return m
        except:
            continue
    
    # Se falhar nos nomes fixos, tenta pegar o primeiro disponível na sua conta
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except:
        pass
    return None

model = carregar_modelo()

if model is None:
    st.error("Não foi possível conectar a nenhum modelo Gemini. Verifique sua chave API.")
    st.stop()

# 2. Ler a Base de Conhecimento
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
    st.sidebar.success("✅ Base de conhecimento ativa")
except:
    st.sidebar.error("❌ Arquivo base.txt não encontrado")
    conhecimento = "Sem base de conhecimento carregada."

# 3. Upload de arquivo para avaliação
st.sidebar.divider()
arquivo_equipe = st.sidebar.file_uploader("Enviar arquivo para conferência", type=["txt", "pdf"])
conteudo_extra = ""
if arquivo_equipe:
    conteudo_extra = arquivo_equipe.read().decode("utf-8", errors="ignore")
    st.sidebar.info(f"Analisando: {arquivo_equipe.name}")

# 4. Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Como posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrução personalizada (O "Cérebro" do Agente)
        prompt_sistema = f"""
        Você é um assistente especializado. 
        Sua base de conhecimento é: {conhecimento}
        
        Se houver um arquivo enviado abaixo, compare-o com a base e diga se está correto:
        {conteudo_extra}
        
        Pergunta do usuário: {prompt}
        """
        
        try:
            response = model.generate_content(prompt_sistema)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro na resposta: {e}")

import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Agente da Equipe", layout="wide")
st.title("🤖 Assistente de Consultas e Qualidade")

# 1. Configuração Segura da API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configure a chave GOOGLE_API_KEY nos Secrets do Streamlit!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. FUNÇÃO MÁGICA: Localizar um modelo que funcione na sua conta
@st.cache_resource
def carregar_modelo_seguro():
    try:
        # Pede ao Google uma lista de todos os modelos que sua chave pode usar
        modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not modelos_disponiveis:
            return None, "Nenhum modelo de chat encontrado para esta chave."
        
        # Tenta priorizar o Flash 1.5, mas se não achar, pega o primeiro que aparecer
        selecionado = None
        for m in modelos_disponiveis:
            if "gemini-1.5-flash" in m:
                selecionado = m
                break
        
        if not selecionado:
            selecionado = modelos_disponiveis[0]
            
        return genai.GenerativeModel(selecionado), selecionado
    except Exception as e:
        return None, str(e)

model, nome_do_modelo = carregar_modelo_seguro()

if model is None:
    st.error(f"Erro crítico de conexão: {nome_do_modelo}")
    st.info("Dica: Verifique se sua chave API no Google AI Studio está ativa e em um projeto 'Free' ou 'Pay-as-you-go'.")
    st.stop()
else:
    st.caption(f"✅ Conectado com sucesso via: {nome_do_modelo}")

# 3. Carregar a Base de Conhecimento (Seus 734k caracteres)
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
    st.sidebar.success(f"📚 Base: {len(conhecimento)} caracteres carregados.")
except:
    conhecimento = ""
    st.sidebar.error("Arquivo base.txt não encontrado.")

# 4. Área de Upload para Avaliação
st.sidebar.divider()
arquivo_subido = st.sidebar.file_uploader("Avaliar novo documento", type=["txt", "pdf"])
texto_arquivo = ""
if arquivo_subido:
    texto_arquivo = arquivo_subido.read().decode("utf-8", errors="ignore")
    st.sidebar.info("Documento pronto para análise.")

# 5. Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Como posso ajudar hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Super instrução para a IA
        instrucao = f"""
        Você é um consultor da equipe. Use a base abaixo como sua única fonte.
        
        BASE DE CONHECIMENTO:
        {conhecimento}
        
        ARQUIVO PARA AVALIAR:
        {texto_arquivo if texto_arquivo else "Nenhum arquivo enviado."}
        
        PERGUNTA: {prompt}
        """
        
        try:
            response = model.generate_content(instrucao)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro ao gerar resposta: {e}")

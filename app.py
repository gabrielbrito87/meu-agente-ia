import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Agente Colaborativo", layout="wide")

# 1. Configuração da API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Carregar a Base de Conhecimento Gigante
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
    st.sidebar.success(f"✅ Base de Dados: {len(conhecimento)} caracteres")
except:
    conhecimento = ""
    st.sidebar.error("Arquivo base.txt não encontrado.")

# 3. ÁREA DE AVALIAÇÃO DE ARQUIVOS (O que você pediu)
st.sidebar.divider()
st.sidebar.header("📁 Avaliar Novo Documento")
arquivo_equipe = st.sidebar.file_uploader("Suba o arquivo para conferência", type=["txt", "pdf"])

texto_do_arquivo = ""
if arquivo_equipe:
    # Se for PDF, este código simples lê como texto (funciona para PDFs de texto)
    try:
        texto_do_arquivo = arquivo_equipe.read().decode("utf-8", errors="ignore")
        st.sidebar.info(f"Arquivo '{arquivo_equipe.name}' carregado.")
    except:
        st.sidebar.error("Erro ao ler o conteúdo do arquivo.")

# 4. Interface do Chat
st.title("🤖 Assistente de Consultas e Qualidade")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Como posso ajudar com a base de dados hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Preparamos o comando para a IA
        contexto_instrucao = f"""
        Você é um consultor especialista da equipe.
        
        INFORMAÇÃO DE APOIO (Sua Base de Conhecimento):
        {conhecimento}
        
        DOCUMENTO PARA AVALIAR (Enviado pelo usuário agora):
        {texto_do_arquivo if texto_do_arquivo else "Nenhum arquivo enviado."}
        
        PERGUNTA/SOLICITAÇÃO DO USUÁRIO:
        {prompt}
        
        INSTRUÇÕES:
        1. Se o usuário pedir para avaliar o documento enviado, compare-o com a Base de Conhecimento e aponte erros ou melhorias.
        2. Se o usuário fizer uma pergunta, responda APENAS com base na Base de Conhecimento.
        3. Seja profissional, claro e objetivo.
        """
        
        try:
            # Enviamos tudo para o Gemini
            response = model.generate_content(contexto_instrucao)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro ao processar: {e}")

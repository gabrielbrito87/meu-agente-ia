import streamlit as st
import google.generativeai as genai
import PyPDF2
import io

st.set_page_config(page_title="Agente de Qualidade PDF", layout="wide")
st.title("🤖 Assistente e Analisador de Documentos")

# 1. Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

@st.cache_resource
def carregar_modelo():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            return genai.GenerativeModel(m.name)
    return None

model = carregar_modelo()

# 2. Carregar a Base de Dados (base.txt)
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
    st.sidebar.success(f"✅ Base: {len(conhecimento)} caracteres")
except:
    conhecimento = ""
    st.sidebar.error("Arquivo base.txt não encontrado.")

# 3. FUNÇÃO PARA LER PDF
def extrair_texto_pdf(arquivo_enviado):
    try:
        pdf_reader = PyPDF2.PdfReader(arquivo_enviado)
        texto_extraido = ""
        for pagina in pdf_reader.pages:
            texto_extraido += pagina.extract_text()
        return texto_extraido
    except Exception as e:
        return f"Erro ao ler PDF: {e}"

# 4. ABA DE ARQUIVOS (Suporta TXT e PDF)
st.sidebar.divider()
st.sidebar.header("📁 Avaliar Novo Documento")
arquivo_equipe = st.sidebar.file_uploader("Envie um arquivo (PDF ou TXT)", type=["txt", "pdf"])

texto_do_arquivo = ""
if arquivo_equipe:
    if arquivo_equipe.type == "application/pdf":
        texto_do_arquivo = extrair_texto_pdf(arquivo_equipe)
    else:
        texto_do_arquivo = arquivo_equipe.read().decode("utf-8", errors="ignore")
    
    if texto_do_arquivo:
        st.sidebar.info(f"📄 Arquivo '{arquivo_equipe.name}' carregado!")

# 5. Interface do Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pergunte algo ou peça para avaliar o arquivo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Contexto reforçado
        instrucao = f"""
        Você é um auditor de documentos. Compare o ARQUIVO ENVIADO com a BASE DE CONHECIMENTO.
        
        BASE DE CONHECIMENTO (Regras Oficiais):
        {conhecimento}
        
        ARQUIVO ENVIADO PARA AVALIAÇÃO:
        {texto_do_arquivo if texto_do_arquivo else "Nenhum arquivo enviado pelo usuário."}
        
        PERGUNTA DO USUÁRIO: {prompt}
        """
        
        try:
            response = model.generate_content(instrucao)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            if "429" in str(e):
                st.error("Aguarde 60 segundos. O arquivo enviado é muito grande para o plano gratuito.")
            else:
                st.error(f"Erro: {e}")

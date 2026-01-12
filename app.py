import streamlit as st
import google.generativeai as genai

# Configuração visual
st.set_page_config(page_title="Agente de Qualidade", layout="wide")
st.title("🤖 Assistente e Avaliador da Equipe")

# 1. Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Carregar Base de Conhecimento
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
    st.sidebar.success(f"✅ Base carregada: {len(conhecimento)} caracteres")
except:
    st.sidebar.error("❌ Arquivo base.txt não encontrado!")
    conhecimento = ""

# 3. Upload de arquivos para avaliação (A função que você queria!)
st.sidebar.divider()
st.sidebar.header("Avaliar Documento")
arquivo_subido = st.sidebar.file_uploader("Suba um arquivo para conferência", type=["txt", "pdf", "docx"])

conteudo_do_arquivo = ""
if arquivo_subido:
    conteudo_do_arquivo = arquivo_subido.read().decode("utf-8", errors="ignore")
    st.sidebar.info("Arquivo pronto para análise.")

# 4. Interface do Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ex: Este arquivo está correto? / Como faço para..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # O SEGREDO: Instrução detalhada (System Prompt)
        contexto_sistema = f"""
        Você é um Assistente Colaborativo de elite. Sua missão é ajudar a equipe com base nestas regras:
        ---
        {conhecimento}
        ---
        REGRAS DE OURO:
        1. Se o usuário enviar um arquivo para análise (abaixo), compare-o com a base de conhecimento e diga o que está errado.
        2. Se a resposta não estiver na base, diga educadamente que não possui essa informação.
        3. Seja direto e profissional.

        ARQUIVO PARA ANALISAR AGORA (se houver): {conteudo_do_arquivo}
        """
        
        try:
            # Enviamos a instrução pesada e a pergunta do usuário
            response = model.generate_content([contexto_sistema, prompt])
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro ao processar: {e}")

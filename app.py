import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Agente da Equipe", layout="wide")

# 1. Configuração da API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Tentar ler a base e medir o tamanho dela
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
    tamanho_base = len(conhecimento)
except:
    conhecimento = "ERRO: Arquivo base.txt não encontrado no GitHub."
    tamanho_base = 0

# 3. Criar o modelo com INSTRUÇÕES RÍGIDAS
# Aqui dizemos que ela DEVE usar a base
instrucao_obrigatoria = f"""
Você é um assistente exclusivo da equipe. 
SUA ÚNICA FONTE DE VERDADE É ESTA BASE DE CONHECIMENTO:
---
{conhecimento}
---
REGRAS:
1. Responda APENAS com base no texto acima.
2. Se a informação não estiver na base, diga: "Essa informação não consta na nossa base de conhecimento".
3. Se um arquivo for enviado, compare-o rigorosamente com a base acima.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instrucao_obrigatoria
)

# --- Interface ---
st.title("🤖 Agente Especialista")
st.sidebar.info(f"Tamanho da Base: {tamanho_base} caracteres")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Upload de arquivo (opcional)
arquivo = st.sidebar.file_uploader("Enviar arquivo para conferência", type=["txt", "pdf"])
conteudo_arquivo = ""
if arquivo:
    conteudo_arquivo = arquivo.read().decode("utf-8", errors="ignore")
    st.sidebar.success("Arquivo pronto para análise")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Perqunte algo sobre a base..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Se tiver um arquivo, a gente avisa a IA no momento da pergunta
        pergunta_completa = prompt
        if conteudo_arquivo:
            pergunta_completa = f"Considere este arquivo enviado: {conteudo_arquivo}\n\nPergunta: {prompt}"
        
        response = model.generate_content(pergunta_completa)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

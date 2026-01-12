import streamlit as st
from openai import OpenAI

# Título do site
st.title("🤖 Assistente da Equipe")
st.write("Consulte nossa base ou envie um arquivo para avaliação.")

# Conectando com a inteligência (chave secreta)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Lendo o arquivo que você subiu (base.txt)
with open("base.txt", "r", encoding="utf-8") as f:
    conhecimento = f.read()

# Menu lateral para enviar arquivos
st.sidebar.header("Avaliação de Arquivos")
arquivo_equipe = st.sidebar.file_uploader("Suba um arquivo para conferir", type=["txt", "pdf"])

# Chat propriamente dito
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Como posso ajudar?"):
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        contexto = f"Base de conhecimento: {conhecimento}"
        if arquivo_equipe:
            contexto += f"\nArquivo enviado pelo usuário: {arquivo_equipe.name}"
        
        resposta = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Você é um assistente prestativo. Baseie-se nisto: {contexto}"},
                *st.session_state.mensagens
            ]
        )
        texto_ai = resposta.choices[0].message.content
        st.markdown(texto_ai)
        st.session_state.mensagens.append({"role": "assistant", "content": texto_ai})

import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Agente Fiel à Base", layout="wide")
st.title("🤖 Assistente Especialista da Equipe")

# 1. Configuração da API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Carregando a Base (com verificação)
try:
    with open("base.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
    
    # Mostra na lateral se o arquivo foi lido
    if len(conhecimento) > 10:
        st.sidebar.success(f"✅ Base de dados carregada! ({len(conhecimento)} letras)")
        with st.sidebar.expander("Clique para ver o que a IA está lendo:"):
            st.write(conhecimento)
    else:
        st.sidebar.warning("⚠️ O arquivo base.txt parece estar vazio!")
except Exception as e:
    st.sidebar.error(f"❌ Erro ao ler base.txt: {e}")
    conhecimento = ""

# 3. Configuração do Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir mensagens antigas
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. A Pergunta do Usuário
if prompt := st.chat_input("Pergunte algo sobre a nossa base..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # O PROMPT RÍGIDO (Aqui é onde forçamos a IA a usar a base)
        # Usamos delimitadores claros (---) para ela não se perder
        instrucao_rigida = f"""
        VOCÊ É UM ASSISTENTE QUE TRABALHA APENAS COM OS DADOS FORNECIDOS.
        
        REGRAS ABSOLUTAS:
        1. Use EXCLUSIVAMENTE o texto abaixo (BASE DE CONHECIMENTO) para responder.
        2. Se a resposta não estiver no texto, diga: "Sinto muito, mas essa informação não consta na nossa base de dados oficial."
        3. Não use seus conhecimentos externos ou opiniões.
        4. Seja direto e cite trechos se necessário.

        BASE DE CONHECIMENTO:
        ---
        {conhecimento}
        ---
        
        PERGUNTA DO USUÁRIO: {prompt}
        """
        
        try:
            # Usando o modelo que funcionou no passo anterior
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(instrucao_rigida)
            
            resposta_final = response.text
            st.markdown(resposta_final)
            st.session_state.messages.append({"role": "assistant", "content": resposta_final})
            
        except Exception as e:
            st.error(f"Erro ao gerar resposta: {e}")

import streamlit as st
import google.generativeai as genai
from google.generativeai import caching
import datetime
import PyPDF2

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Agente com Cache", layout="wide")
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- LÓGICA DE CACHE (A Mágica) ---
@st.cache_resource
def gerenciar_contexto_cache(texto_base):
    """Cria ou recupera um cache de contexto para a base gigante"""
    try:
        # Nome identificador para o seu cache (ajuste se mudar a base)
        cache_name = "cache_equipe_v1"
        
        # Tentamos listar caches existentes para ver se o nosso já está lá
        for c in caching.CachedContent.list():
            if c.display_name == cache_name:
                return c

        # Se não existir, criamos um novo
        # O cache expira em 1 hora por padrão (pode aumentar até 48h)
        meu_cache = caching.CachedContent.create(
            model='models/gemini-1.5-flash-001',
            display_name=cache_name,
            system_instruction=(
                "Você é um consultor especialista. Use estritamente esta base "
                "de conhecimento para responder e analisar documentos."
            ),
            contents=[texto_base],
            ttl=datetime.timedelta(hours=1),
        )
        return meu_cache
    except Exception as e:
        st.error(f"Erro ao gerenciar cache: {e}")
        return None

# --- CARREGAR BASE ---
with open("base.txt", "r", encoding="utf-8") as f:
    base_conhecimento = f.read()

# Ativa o cache (Sua base de 734k caracteres entra aqui)
cache_ativo = gerenciar_contexto_cache(base_conhecimento)

# --- INICIALIZAR MODELO COM CACHE ---
if cache_ativo:
    model = genai.GenerativeModel.from_cached_content(cached_content=cache_ativo)
else:
    # Caso o cache falhe, usa o modo normal (mais caro)
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- RESTO DO APP (LOGIN E INTERFACE) ---
# [O código de Login e Upload permanece o mesmo que usamos antes]

# --- MODIFICAÇÃO NO MOMENTO DA RESPOSTA ---
# No campo onde a IA gera a resposta (generate_content):
if prompt := st.chat_input("Sua dúvida..."):
    # ... código de histórico ...
    
    # Agora a instrução é MUITO curta, pois a base já está "decorada" na IA
    contexto_pergunta = f"Pergunta: {prompt}. \nArquivo enviado para analisar: {texto_do_arquivo}"
    
    with st.spinner('Consultando cache de memória...'):
        response = model.generate_content(contexto_pergunta)
        st.markdown(response.text)

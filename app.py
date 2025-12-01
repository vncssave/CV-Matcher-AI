import streamlit as st
import requests
import PyPDF2
from io import BytesIO

# --- CONFIGURAÇÃO DA PÁGINA (WIDE LAYOUT) ---
st.set_page_config(
    page_title="CV Matcher AI",
    page_icon="🚀",
    layout="wide"
)

# --- CONFIGURAÇÃO DO WEBHOOK (COLE SUA URL AQUI) ---
# ⚠️ NÃO ESQUEÇA DE COLOCAR SUA URL DO N8N AQUI NOVAMENTE!
N8N_WEBHOOK_URL = "https://vsave.app.n8n.cloud/webhook/CVAnalyzer"


# --- CSS HACKS (PARA MELHORAR O LAYOUT) ---
# 1. Esconde menu/rodapé padrão.
# 2. REDUZ O ESPAÇO EM BRANCO NO TOPO (block-container).
# 3. Estiliza o botão para ficar mais chamativo.
custom_css = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Reduz o padding superior da área principal */
            .block-container {
                padding-top: 2rem !important;
                padding-bottom: 1rem !important;
            }
            
            /* Estilo do botão principal */
            .stButton button[kind="primary"] {
                width: 100%;
                font-weight: bold;
                border-radius: 10px;
                height: 3em;
            }
            </style>
            """
st.markdown(custom_css, unsafe_allow_html=True)

# --- FUNÇÕES ---
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")
        return None

# --- SIDEBAR (BARRA LATERAL) ---
with st.sidebar:
    # Adicionei um emoji gigante para dar um visual mais moderno
    st.markdown("# 🤖") 
    st.title("CV Matcher AI")
    st.info("**Como funciona?**\n\n1. Cole a vaga na esquerda.\n2. Suba seu PDF na direita.\n3. Clique no botão para gerar a análise.")
    st.divider()
    st.write("Criado por **Vinicius Salvalaio**")
    st.caption("Powered by n8n & Gemini")

# --- ÁREA PRINCIPAL ---
# Títulos mais compactos
st.markdown("## 🚀 CV Matcher AI")
st.markdown("##### Descubra o que o Recrutador, o Gestor e o RH realmente pensam.")

# --- ZONA DE INPUTS (DENTRO DE UM CONTAINER COM BORDA) ---
# Isso ajuda a organizar visualmente e economizar espaço
with st.container(border=True):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📌 A Vaga")
        # REDUZI A ALTURA DE 300 PARA 180px
        vaga_text = st.text_area("Cole a descrição completa aqui", height=180, placeholder="Ex: Requisitos: Python Senior, AWS, Django...")

    with col2:
        st.subheader("📄 Seu Currículo")
        # O uploader já tem um tamanho fixo, mas dentro do container fica mais organizado
        uploaded_file = st.file_uploader("Arraste seu PDF aqui", type="pdf")
        
        if uploaded_file:
            st.success(f"✅ CV carregado: {uploaded_file.name}")

# --- BOTÃO DE AÇÃO ---
# Um pequeno espaço antes do botão
st.write("") 
botao_analisar = st.button("🔍 GERAR ESTRATÉGIA DE ENTREVISTA", type="primary")

# --- LÓGICA PRINCIPAL ---
if botao_analisar:
    if not vaga_text or not uploaded_file:
        st.warning("⚠️ Atenção: Preencha a Vaga E suba o Currículo para continuar.")
    else:
        # Barra de progresso visual
        progress_text = "Iniciando os agentes de IA..."
        my_bar = st.progress(0, text=progress_text)

        try:
            # 1. Extração
            my_bar.progress(20, text="Lendo o PDF...")
            cv_text = extract_text_from_pdf(uploaded_file)
            
            if cv_text:
                # 2. Envio
                my_bar.progress(50, text="Consultando o Gestor Técnico e o RH (Isso leva uns 15s)...")
                payload = {"vaga": vaga_text, "curriculo": cv_text}
                
                # Timeout aumentado para 60s para evitar erros se a IA demorar
                response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=60)
                
                # 3. Resultado
                my_bar.progress(90, text="Formatando relatório...")
                
                if response.status_code == 200:
                    my_bar.empty() # Remove a barra
                    resultado = response.json()
                    
                    texto_final = resultado.get("texto", "Erro: Campo 'texto' não encontrado no JSON.")
                    
                    # Exibição do Resultado em um Expander (para não ocupar muito espaço se não quiser ver)
                    with st.expander("📋 VISUALIZAR RELATÓRIO COMPLETO", expanded=True):
                        st.markdown(texto_final)
                        
                        st.divider()
                        # Botão de Download
                        st.download_button(
                            label="📥 Baixar Relatório em Texto",
                            data=texto_final,
                            file_name="estrategia_entrevista.md",
                            mime="text/markdown"
                        )
                else:
                    my_bar.empty()
                    st.error(f"Erro na conexão com n8n. Status: {response.status_code}")
                    st.write("Verifique se o workflow do n8n está ativo.")
            
        except requests.exceptions.Timeout:
             my_bar.empty()
             st.error("O tempo limite esgotou. O Gemini está demorando para responder. Tente novamente.")
        except Exception as e:
            my_bar.empty()
            st.error(f"Ocorreu um erro: {e}")
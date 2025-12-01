import streamlit as st
import requests
import PyPDF2
from io import BytesIO

# --- CONFIGURAÇÃO DA PÁGINA (WIDE LAYOUT) ---
st.set_page_config(
    page_title="Decodificador de Vagas IA",
    page_icon="🕵️‍♂️",
    layout="wide"
)

# --- CONFIGURAÇÃO DO WEBHOOK ---
# ⚠️ COLE SUA URL DO N8N AQUI EMBAIXO ⚠️
N8N_WEBHOOK_URL = "https://vsave.app.n8n.cloud/webhook/CVAnalyzer"

# --- CSS HACKS (PARA MELHORAR O LAYOUT) ---
custom_css = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Reduz o padding superior */
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
    st.markdown("# 🕵️‍♂️") 
    st.title("Menu")
    st.info("**Como usar:**\n\n1. Cole a vaga.\n2. Suba seu CV.\n3. Receba o feedback.")
    st.divider()
    st.caption("Powered by n8n & Gemini")

# --- ÁREA PRINCIPAL (TÍTULOS) ---
st.markdown("# 🕵️‍♂️ Decodificador de Vagas com IA")

# Subtítulo (Com margem maior para empurrar os quadros para baixo)
st.markdown("""
<div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 40px; border-left: 5px solid #ff4b4b;'>
    <span style='font-size: 1.15rem; color: #31333F;'>
    <b>Descubra o que o Recrutador, o Gestor e o RH realmente pensam.</b><br>
    <span style='font-size: 0.95rem; color: #555; display: block; margin-top: 10px;'>
    Receba um feedback brutalmente honesto sobre seus pontos cegos e ajuste sua estratégia <b>antes</b> de aplicar.
    </span>
    </span>
</div>
""", unsafe_allow_html=True)

st.write("") 
st.write("") 

# --- ZONA DE INPUTS (AQUI ESTAVA O ERRO) ---
# Precisamos criar as colunas DENTRO do container
with st.container(border=True):
    col1, col2 = st.columns(2)  # <--- ESTA LINHA É QUE FALTAVA OU ESTAVA FORA

    with col1:
        st.subheader("📌 A Vaga")
        vaga_text = st.text_area("Cole a descrição completa aqui", height=180, placeholder="Ex: Requisitos: Python Senior, AWS, Django...")

    with col2:
        st.subheader("📄 Seu Currículo")
        uploaded_file = st.file_uploader("Arraste seu PDF aqui", type="pdf")
        if uploaded_file:
            st.success(f"✅ CV carregado: {uploaded_file.name}")

# --- BOTÃO DE AÇÃO ---
st.write("") 
botao_analisar = st.button("🔍 GERAR ESTRATÉGIA DE ENTREVISTA", type="primary")

# --- LÓGICA PRINCIPAL ---
if botao_analisar:
    if not vaga_text or not uploaded_file:
        st.warning("⚠️ Atenção: Preencha a Vaga E suba o Currículo para continuar.")
    else:
        progress_text = "Iniciando os agentes de IA..."
        my_bar = st.progress(0, text=progress_text)

        try:
            # 1. Extração
            my_bar.progress(20, text="Lendo o PDF...")
            cv_text = extract_text_from_pdf(uploaded_file)
            
            if cv_text:
                # 2. Envio
                my_bar.progress(50, text="Consultando o Gestor Técnico e o RH...")
                payload = {"vaga": vaga_text, "curriculo": cv_text}
                
                response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=60)
                
                # 3. Resultado
                my_bar.progress(90, text="Formatando relatório...")
                
                if response.status_code == 200:
                    my_bar.empty()
                    resultado = response.json()
                    texto_final = resultado.get("texto", "Erro: Campo 'texto' não encontrado no JSON.")
                    
                    with st.expander("📋 VISUALIZAR RELATÓRIO COMPLETO", expanded=True):
                        st.markdown(texto_final)
                        st.divider()
                        st.download_button(
                            label="📥 Baixar Relatório",
                            data=texto_final,
                            file_name="estrategia_entrevista.md",
                            mime="text/markdown"
                        )
                else:
                    my_bar.empty()
                    st.error(f"Erro no n8n: {response.status_code}")
            
        except requests.exceptions.Timeout:
             my_bar.empty()
             st.error("O tempo limite esgotou. Tente novamente.")
        except Exception as e:
            my_bar.empty()
            st.error(f"Ocorreu um erro: {e}")
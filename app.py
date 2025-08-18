import yt_dlp
import librosa
import numpy as np
import os
import streamlit as st
import webbrowser
from repertorio import REPERTORIO

# ----------------- FUNÇÕES -----------------
def baixar_audio(link):
    saida_final = None
    def hook_progresso(d):
        nonlocal saida_final
        if d['status'] == 'finished':
            saida_final = d['filename']

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'outtmpl': 'musica.%(ext)s',
        'progress_hooks': [hook_progresso],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
    if saida_final:
        saida_final = saida_final.rsplit('.', 1)[0] + '.mp3'
        return saida_final
    else:
        raise Exception("❌ Não foi possível capturar o nome do arquivo final.")

def estimar_bpm_multiplos(caminho_audio):
    y, sr = librosa.load(caminho_audio, duration=60)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    bpm_principal = float(np.squeeze(tempo))
    bpm_1_2 = bpm_principal / 2
    bpm_2 = bpm_principal * 2
    candidatos = [bpm_principal, bpm_1_2, bpm_2]
    candidatos_filtrados = []
    for b in candidatos:
        val = float(np.squeeze(b))
        if 40 <= val <= 240:
            candidatos_filtrados.append(val)
    candidatos_filtrados = sorted(set([round(b) for b in candidatos_filtrados]))
    return candidatos_filtrados

def estimar_tom(caminho_audio):
    y, sr = librosa.load(caminho_audio, duration=60)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_sum = np.sum(chroma, axis=1)
    nota_idx = chroma_sum.argmax()
    notas = ['C', 'C#', 'D', 'D#', 'E', 'F',
             'F#', 'G', 'G#', 'A', 'A#', 'B']
    tom_estimado = notas[nota_idx]
    return tom_estimado

def pesquisar_youtube(musica):
    """Retorna link para pesquisa no YouTube"""
    query = musica.replace(" ", "+").replace("(", "").replace(")", "")
    return f"https://www.youtube.com/results?search_query={query}"

def pesquisar_cifraclub(musica):
    """Retorna link para pesquisa no Cifra Club"""
    query = musica.split("(")[0].strip().replace(" ", "-").lower()
    return f"https://www.cifraclub.com.br/?q={query}"

# ----------------- INTERFACE STREAMLIT -----------------
st.set_page_config(page_title="🎶 Analisador de Música", page_icon="🎵")

st.title("🎶 Analisador de Música")

# Menu inicial
opcao = st.radio(
    "Selecione uma opção:",
    ["🔗 Analisar música via link do YouTube", "📂 Pesquisar no repertório pré-definido"]
)

if opcao == "🔗 Analisar música via link do YouTube":
    link = st.text_input("Cole o link do YouTube aqui:")
    if st.button("Analisar Link"):
        if not link.strip():
            st.warning("⚠ Cole um link válido primeiro!")
        else:
            with st.spinner("⬇ Baixando e analisando..."):
                arquivo_mp3 = None
                try:
                    arquivo_mp3 = baixar_audio(link)
                    bpm_lista = estimar_bpm_multiplos(arquivo_mp3)
                    tom = estimar_tom(arquivo_mp3)

                    st.success("✅ Análise concluída!")
                    st.write(f"**BPMs estimados:** {bpm_lista}")
                    st.write(f"**Tom estimado:** {tom}")

                except Exception as e:
                    st.error(f"❌ Erro: {e}")
                finally:
                    if arquivo_mp3 and os.path.exists(arquivo_mp3):
                        os.remove(arquivo_mp3)

elif opcao == "📂 Pesquisar no repertório pré-definido":

    # Campo de busca com filtro
    termo_busca = st.text_input("🔍 Digite o nome da música ou artista:")
    
    # Função de filtro aprimorada
    def filtrar_musicas(termo):
        termo = termo.lower().strip()
        if not termo:
            return REPERTORIO
        return [
            musica for musica in REPERTORIO
            if (termo in musica.lower()) or 
               (any(palavra in musica.lower() for palavra in termo.split()))
        ]
    
    # Aplica o filtro
    musicas_filtradas = filtrar_musicas(termo_busca)
    
    if not musicas_filtradas:
        st.warning("Nenhuma música encontrada. Tente outro termo.")
    else:
        escolha = st.selectbox("🎵 Selecione uma música:", musicas_filtradas)
        
        if escolha:
            st.success(f"✅ Você selecionou: **{escolha}**")
        
        # ----------------- Botões de pesquisa -----------------
        col1, col2 = st.columns(2)

        with col1:
            url_youtube = pesquisar_youtube(escolha)
            st.markdown(
                f'<a href="{url_youtube}" target="_blank"><button style="padding:10px; font-size:16px;">🔍 Pesquisar no YouTube</button></a>',
                unsafe_allow_html=True
            )

        with col2:
            url_cifra = pesquisar_cifraclub(escolha)
            st.markdown(
                f'<a href="{url_cifra}" target="_blank"><button style="padding:10px; font-size:16px;">🎼 Ver cifra no Cifra Club</button></a>',
                unsafe_allow_html=True
            )

# ----------------- RODAPÉ FIXO -----------------
st.markdown("""
    <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #0E1117;
            color: white;
            text-align: center;
            padding: 8px 0;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
        }
        .footer a {
            color: white;
            text-decoration: none;
            font-weight: bold;
        }
        .footer a:hover {
            color: #000;
            text-decoration: underline;
        }
    </style>
    <div class="footer">
        © 2025 <a href="https://github.com/alisson9386" target="_blank">Alisson Deives</a>
    </div>
""", unsafe_allow_html=True)

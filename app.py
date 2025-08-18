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
        'format': 'bestaudio',  # pega qualquer áudio disponível
        'noplaylist': True,
        'outtmpl': 'musica.%(ext)s',
        'progress_hooks': [hook_progresso],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,  # não quebra se o vídeo não estiver disponível
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
    query = musica.replace(" ", "+").replace("(", "").replace(")", "")
    return f"https://www.youtube.com/results?search_query={query}"

def pesquisar_cifraclub(musica):
    query = musica.split("(")[0].strip().replace(" ", "-").lower()
    return f"https://www.cifraclub.com.br/?q={query}"

# ----------------- INTERFACE STREAMLIT -----------------
st.set_page_config(page_title="🎶 Analisador de Música", page_icon="🎵")

st.title("🎶 Analisador de Música")

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
    termo_busca = st.text_input("🔍 Digite o nome da música ou artista:")

    def filtrar_musicas(termo):
        termo = termo.lower().strip()
        if not termo:
            return REPERTORIO
        return [
            musica for musica in REPERTORIO
            if (termo in musica.lower()) or 
               (any(palavra in musica.lower() for palavra in termo.split()))
        ]

    musicas_filtradas = filtrar_musicas(termo_busca)

    if not musicas_filtradas:
        st.warning("Nenhuma música encontrada. Tente outro termo.")
    else:
        escolha = st.selectbox("🎵 Selecione uma música:", musicas_filtradas)
        if escolha:
            st.success(f"✅ Você selecionou: **{escolha}**")

        col1, col2 = st.columns(2)

        # Botão do YouTube
        with col1:
            url_youtube = pesquisar_youtube(escolha)
            st.markdown(f'''
                <a href="{url_youtube}" target="_blank" style="text-decoration: none;">
                    <div style="
                        display:inline-block;
                        width:100%;
                        max-width:180px;
                        background-color:#FF0000; 
                        color:white; 
                        padding:8px 12px; 
                        border-radius:6px; 
                        text-align:center; 
                        font-weight:bold; 
                        font-size:14px;
                        box-shadow: 1px 1px 3px rgba(0,0,0,0.3);
                        transition: all 0.2s;
                        margin-bottom:4px;
                    "
                    onmouseover="this.style.backgroundColor='#CC0000'" 
                    onmouseout="this.style.backgroundColor='#FF0000'">
                        🔍 YouTube
                    </div>
                </a>
            ''', unsafe_allow_html=True)

        # Botão do Cifra Club
        with col2:
            url_cifra = pesquisar_cifraclub(escolha)
            st.markdown(f'''
                <a href="{url_cifra}" target="_blank" style="text-decoration: none;">
                    <div style="
                        display:inline-block;
                        width:100%;
                        max-width:180px;
                        background-color:#4CAF50; 
                        color:white; 
                        padding:8px 12px; 
                        border-radius:6px; 
                        text-align:center; 
                        font-weight:bold; 
                        font-size:14px;
                        box-shadow: 1px 1px 3px rgba(0,0,0,0.3);
                        transition: all 0.2s;
                        margin-bottom:4px;
                    "
                    onmouseover="this.style.backgroundColor='#45A049'" 
                    onmouseout="this.style.backgroundColor='#4CAF50'">
                        🎼 Cifra Club
                    </div>
                </a>
            ''', unsafe_allow_html=True)

# ----------------- Rodapé -----------------
st.markdown("""
    <div style="text-align:center; margin-top:30px; font-size:12px; color:gray;">
        © 2025 <a href="https://github.com/SEU_GITHUB" target="_blank" style="color:gray;">Seu Nome</a>
    </div>
""", unsafe_allow_html=True)

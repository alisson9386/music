import librosa
import numpy as np
import os
import requests
import streamlit as st
import webbrowser
from repertorio import REPERTORIO

# ----------------- FUNÇÕES -----------------

def baixar_audio_api(video_url):
    url = "http://127.0.0.1:8000/baixar"
    r = requests.get(url, params={"video_url": video_url})
    if r.status_code == 200:
        with open("musica.mp3", "wb") as f:
            f.write(r.content)
        return "musica.mp3"
    raise Exception(f"Erro no download via API: {r.status_code}")

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
st.title("🎶 Acervo de músicas - alisson9386")

opcao = st.radio(
    "Selecione uma opção:",
    [
        "⬆️ Upload de arquivo", 
        #"🔗 YouTube (via API)", 
        "📂 Repertório pré-definido"]
)

# ---- Upload direto ----
if opcao == "⬆️ Upload de arquivo":
    arquivo = st.file_uploader("Envie a música (MP3 ou M4A)", type=["mp3", "m4a"])
    if arquivo:
        caminho = f"temp_{arquivo.name}"
        with open(caminho, "wb") as f:
            f.write(arquivo.getbuffer())
        with st.spinner("🎧 Analisando música..."):
            try:
                bpm_lista = estimar_bpm_multiplos(caminho)
                tom = estimar_tom(caminho)
                st.success("✅ Análise concluída!")
                st.write(f"**BPMs estimados:** {bpm_lista}")
                st.write(f"**Tom estimado:** {tom}")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
            finally:
                if os.path.exists(caminho):
                    os.remove(caminho)

# ---- YouTube via API ----
elif opcao == "🔗 YouTube (via API)":
    link = st.text_input("Cole o link do YouTube aqui:")
    if st.button("Analisar do YouTube"):
        if not link.strip():
            st.warning("⚠ Informe um link válido primeiro.")
        else:
            with st.spinner("⬇ Baixando e analisando..."):
                try:
                    arquivo_mp3 = baixar_audio_api(link)
                    bpm_lista = estimar_bpm_multiplos(arquivo_mp3)
                    tom = estimar_tom(arquivo_mp3)
                    st.success("✅ Análise concluída!")
                    st.write(f"**BPMs estimados:** {bpm_lista}")
                    st.write(f"**Tom estimado:** {tom}")
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
                finally:
                    if os.path.exists("musica.mp3"):
                        os.remove("musica.mp3")

# ---- Repertório ----
elif opcao == "📂 Repertório pré-definido":
    termo_busca = st.text_input("🔍 Digite o nome da música ou artista:")

    def filtrar_musicas(termo):
        termo = termo.lower().strip()
        if not termo:
            return REPERTORIO
        return [m for m in REPERTORIO if termo in m.lower() or any(p in m.lower() for p in termo.split())]

    musicas_filtradas = filtrar_musicas(termo_busca)

    if not musicas_filtradas:
        st.warning("Nenhuma música encontrada.")
    else:
        escolha = st.selectbox("🎵 Selecione uma música:", musicas_filtradas)
        if escolha:
            st.success(f"✅ Você selecionou: **{escolha}**")

        col1, col2 = st.columns(2)

        with col1:
            url_youtube = pesquisar_youtube(escolha)
            st.markdown(f'''
                <a href="{url_youtube}" target="_blank">
                    <div style="background:#FF0000;color:#fff;padding:8px 12px;border-radius:6px;text-align:center;font-weight:bold;">
                        🔍 YouTube
                    </div>
                </a>
            ''', unsafe_allow_html=True)

        with col2:
            url_cifra = pesquisar_cifraclub(escolha)
            st.markdown(f'''
                <a href="{url_cifra}" target="_blank">
                    <div style="background:#4CAF50;color:#fff;padding:8px 12px;border-radius:6px;text-align:center;font-weight:bold;">
                        🎼 Cifra Club
                    </div>
                </a>
            ''', unsafe_allow_html=True)

# ----------------- Rodapé -----------------
st.markdown("""
    <div style="text-align:center; margin-top:30px; font-size:12px; color:gray;">
        © 2025 <a href="https://github.com/alisson9386" target="_blank" style="color:gray;">Alisson Deives</a>
    </div>
""", unsafe_allow_html=True)
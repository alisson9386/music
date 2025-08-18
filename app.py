import yt_dlp
import librosa
import numpy as np
import os
import streamlit as st
import pandas as pd

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
                    st.write(f"**BPMs estimados (possíveis):** {bpm_lista}")
                    st.write(f"**Tom estimado:** {tom}")

                except Exception as e:
                    st.error(f"❌ Erro: {e}")
                finally:
                    if arquivo_mp3 and os.path.exists(arquivo_mp3):
                        os.remove(arquivo_mp3)

elif opcao == "📂 Pesquisar no repertório pré-definido":
    # Carregar lista do PDF previamente convertida para CSV ou DataFrame
    # Aqui vou simular com uma lista de músicas extraída do seu PDF
    musicas = [
    "A alegria está no coração",
    "A benção (Elevation Worship)",
    "A boa parte (FHOP)",
    "A começar em mim",
    "A Deus demos glória - O grande amor de Deus (hino 042)",
    "A história de Deus (Livres para adorar)",
    "A minh'alma está cheia de paz",
    "A paz do Senhor é o que nós queremos (Rebanhão)",
    "A Ti e só a Ti (Mosaic / Oitava Music)",
    "A Ti me entrego (Vineyard)",
    "A vitória é daquele que contemplar (Adhemar de Campos)",
    "Abra os olhos do meu coração (David Quinlan)",
    "Acendo o fogo em mim (Vineyard / Beto Tavares)",
    "Aclame ao Senhor (Diante do Trono)",
    "Acredito (Newsboys / Leonardo Gonçalves)",
    "Adorai em majestade",
    "Agrada-te do Senhor",
    "Águas purificadoras (Diante do Trono)",
    "Ainda que a figueira (Fernandinho)",
    "Ajuntamento (Jorge Camargo)",
    "Aleluia, salvação e glória",
    "Alfa e Ômega (Marine Friesen)",
    "Algo novo sempre acontece (Silvério Peres)",
    "Alto preço (Asaph Borba)",
    "Andam procurando a razão de viver",
    "Andou onde ando eu",
    "Ano do jubileu (Asaph Borba)",
    "Ao Deus de Abraão - Deus de Abraão (hino 021)",
    "Ao Deus de amor - Maravilhas divinas (hino 033)",
    "Ao nosso Deus que se assenta no trono",
    "Ao orarmos, Senhor",
    "Ao que é digno (Paulo Rogério)",
    "Ao que está assentado",
    "Ao único",
    "Aos pés da cruz (Kleber Lucas)",
    "Aquele que está com Cristo (Comunidade Evangélica Goiânia)",
    "Aquele que foi manifestado em carne",
    "Aquele que tem os meus mandamentos (Grupo Semente)",
    "Aquele que tem sede e busca",
    "Aqui viemos Te adorar, ó Cristo",
    "Arraial do povo de Deus (Daniel Souza)",
    "As trevas estremecem (Mosaic / Mariana Valadão)",
    "Atos 2 (Gabriela Rocha)",
    "Aumenta o fogo (Nívea Soares)",
    "Autor da minha fé (PC Baruk / Paulo Cézar)",
    "Avance e Vença (Oitava Music)",
    "Bem aventurado (Aline Barros)",
    "Bendito é o Rei (FHOP)",
    "Bendize, ó minhalma ao Senhor",
    "Bom estarmos aqui (Renascer Praise)",
    "Bom perfume (Gabi Sampaio)",
    "Bondade de Deus (Bethel / Pedras vivas)",
    "Buscai primeiro o Reino de Deus",
    "Cada estrada em que eu andei",
    "Cada instante contigo, Senhor",
    "Caiam por terra agora",
    "Caminho de milagres (Aline Barros)",
    "Caminho no deserto (Viva Adoração)",
    "Canção ao Cordeiro (Gabriel Guedes e Israel Salazar)",
    "Canção da alvorada (João Alexandre)",
    "Canção do Apocalipse (Diante do Trono)",
    "Canção eterna (FHOP)",
    "Cantai, pois a vitória é ganha",
    "Cantarei Teu amor",
    "Carvalhos de justiça (Josué Rodrigues)",
    "Casa de benção (Eyshila)",
    "Castelo Forte (hino 155)",
    "Cego de Jericó",
    "Ceifeiros da seara santa - Ceifeiros do Senhor (hino 318)",
    "Celebrai a Cristo, celebrai",
    "Celebrai com júbilo ao Senhor",
    "Celebremos com danças ao nosso Deus",
    "Cheguemo-nos pois com ousadia",
    "Chuvas de bençãos (hino 172)",
    "Clamo a Ti",
    "Clamo Jesus (PC Baruk e Marsena)",
    "Colossenses e Suas linhas de amor (FHOP e Marco Telles)",
    "Com Cristo unido - Unido com Cristo (hino 115)",
    "Com muito louvor (Cassiane)",
    "Como é precioso (Asaph Borba)",
    "Como suspira a corça",
    "Comunhão (Gabi Sampaio)",
    "Comunhão (Kleber Lucas)",
    "Conheci um grande amigo (Rebanhão)",
    "Consagração / Louvor ao Rei (Aline Barros)",
    "Coração igual ao Teu (Diante do Trono)",
    "Corpo e família (Daniel Souza)",
    "Correrei (Samuel Mizhahy)",
    "Custe o que custar (Samuel Aleixo, Isa Izaú / Oitava Music)",
    "De todas as tribos (Guilherme Kerr)",
    "Declaramos (Daniel Souza)",
    "Descansarei (Comunidade Evangélica Maringá)",
    "Descerá sobre Ti (Comunidade Evangélica Nilópolis)",
    "Desde o princípio de todas as coisas",
    "Desde os confins da Terra (Igreja Bíblica da Paz)",
    "Desejo do meu coração (Trazendo a Arca)",
    "Deus cuida de mim (Kleber Lucas)",
    "Deus de maravilhas (Christine D´Clario)",
    "Deus de promessas (Trazendo a Arca)",
    "Deus do impossivel (Ministério Apascentar)",
    "Deus dos Antigos (hino 018)",
    "Deus é Deus (Delino Marçal)",
    "Deus está aqui",
    "Deus está no templo - Culto à Trindade (hino 004)",
    "Diante da cruz (Aline Barros)",
    "Diante de Ti",
    "Digno de tudo (Gabi Sampaio)",
    "Digno é o Senhor (Aline Barros)",
    "Dignos És de glória",
    "Disseste (Clamor pelas nações)",
    "Do norte vem o áureo esplendor (Expresso Luz)",
    "Doce nome (Vencedores por Cristo)",
    "Dominio e poder",
    "Dono das estrelas (Trazendo a Arca)",
    "Dou graças de coração",
    "Doxologia (hino 006)",
    "E dizemos amém (Lakewood Music)",
    "Egito (Bethel / Isaias Saas)",
    "Eis dos anjos a harmonia - Louvor Angelical (hino 240)",
    "Ele é exaltado (Comunidade Evangélica RJ)",
    "Ele é o leão da tribo de Judá",
    "Em espírito (Arieta Magrini)",
    "Em memória de Ti (Aristeu Pires Júnior)",
    "Em nome de Jesus (Israel & New Bread)",
    "Em nome do Senhor Jesus",
    "Enche este lugar (David Quinlan)",
    "Enche Tua casa",
    "Enche-me, Espírito (Benedito Carlos e Alda Célia)",
    "Enquanto eu calei",
    "Enquanto eu respirar (Adoração & Adoradores)",
    "Então se verá o Filho do homem",
    "Entre a fé e a razão (Trazendo a Arca)",
    "Entrega (Vineyard e Heloisa Rosa)",
    "Ergo as minhas mãos",
    "És a nossa estrela da manhã",
    "És a razão do meu viver",
    "Esperei confiantemente no Senhor",
    "Espírito Santo de Deus",
    "Espírito, enche a minha vida",
    "Essência da adoração (David Quinlan)",
    "Estamos de pé (Marcus Salles)",
    "Estamos reunidos aqui, Senhor",
    "Este é o dia",
    "Este é o meu respirar",
    "Este reino (Hillsong / Ana Paula Valadão)",
    "Eterna Graça (Samuel Aleixo, Davi Frossard / Oitava Music)",
    "Eterno Pai, Teu povo congregado - A Igreja em adoração (hino 003)",
    "Eu celebrarei cantando ao Senhor",
    "Eu creio (Gabriela Rocha)",
    "Eu creio que tudo é possível",
    "Eu creio, Senhor, na divina promessa - Necessidade (hino 068)",
    "Eu e minha casa (André Valadão)",
    "Eu me alegro em Ti (Hillsong Worship / Ministério Shalom)",
    "Eu me rendo (Renascer Praise)",
    "Eu navegarei",
    "Eu posso escutar o exército de Deus",
    "Eu quero é Deus (Comunidade Evangélica Nilópolis)",
    "Eu quero ser, Senhor amado (Vaso novo)",
    "Eu só quero estar onde estás",
    "Eu sou Teu (Jesus Culture / Gabriela Rocha)",
    "Eu te amo, ó Deus",
    "Eu te louvarei meu bom Jesus (Ronaldo Bezerra)",
    "Eu te louvarei Senhor de todo o meu coração",
    "Eu vejo a glória",
    "Eu vou construir (Pat Barrett / Nívea Soares)",
    "Eu vou passar pela cruz (PG)",
    "Eu vou viver uma virada (Ministério Apascentar)",
    "Exaltai (Igreja Bíblica da Paz)",
    "Exaltar-Te-ei (Vencedores por Cristo)"
]

    escolha = st.selectbox("🎵 Escolha uma música do repertório:", musicas)

    if escolha:
        st.success(f"✅ Você selecionou: **{escolha}**")
        st.info("👉 Aqui você pode, por exemplo, exibir a cifra, link do YouTube, ou até usar o mesmo analisador se tiver um link associado.")

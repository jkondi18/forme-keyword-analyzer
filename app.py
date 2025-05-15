import streamlit as st
from bs4 import BeautifulSoup
import requests
from collections import Counter
import pandas as pd
import string
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')

SCRAPINGBEE_API_KEY = "NET733AO4YPT1IX4ZLWXXS662HCSJX8FFHPZ3ZHVGPGL29WP4P6OXTS1R7LMX7BDGRF236ELQJOENFB3"

st.set_page_config(page_title="Analisador de Palavras-Chave", page_icon="🔍")

st.title("🔍 Analisador de Palavras-Chave de Blogs")
st.write("Cole os links de blogs concorrentes separados por vírgula abaixo. O sistema extrai os títulos das páginas (h2/h3 e similares) e gera uma análise de palavras mais comuns para orientar o conteúdo da FORME.")

urls_input = st.text_area("Links dos sites", placeholder="https://blog1.com, https://blog2.com")

if st.button("Analisar"):
    urls = [url.strip() for url in urls_input.split(",") if url.strip()]
    todos_titulos = []

    for pagina in urls:
        try:
            st.info(f"⏳ Coletando: {pagina}")
            api_url = f"https://app.scrapingbee.com/api/v1/?api_key={SCRAPINGBEE_API_KEY}&url={pagina}&render_js=True"
            response = requests.get(api_url, timeout=30)
            if response.status_code != 200:
                raise Exception(f"Erro HTTP {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')
            titulos = soup.select("h2, h3, .post-title, .entry-title, article h1, article h2")
            textos = [t.get_text(strip=True) for t in titulos if t.get_text(strip=True)]
            todos_titulos.extend(textos)
            st.success(f"✅ Coletado: {pagina} ({len(textos)} títulos)")
        except Exception as e:
            st.error(f"❌ Erro ao coletar {pagina}: {e}")

    if todos_titulos:
        texto = " ".join(todos_titulos).lower()
        texto = texto.translate(str.maketrans("", "", string.punctuation))
        palavras = texto.split()
        palavras_filtradas = [p for p in palavras if p not in stopwords.words("portuguese")]

        frequencia = Counter(palavras_filtradas)
        df = pd.DataFrame(frequencia.items(), columns=["Palavra", "Frequência"]).sort_values("Frequência", ascending=False)

        st.subheader("📊 Palavras mais comuns entre os blogs")
        st.dataframe(df.head(20), use_container_width=True)

        st.download_button("📥 Baixar resultado em Excel", data=df.to_csv(index=False), file_name="palavras_chave.csv", mime="text/csv")
    else:
        st.warning("Nenhum título encontrado nos links fornecidos.")

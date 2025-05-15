import streamlit as st
from bs4 import BeautifulSoup
import requests
from collections import Counter
import pandas as pd
import string
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
import nltk

nltk.download('stopwords')

SCRAPERAPI_KEY = "9dde42e63d33c31226c22ed62e7f601c"

st.set_page_config(page_title="Analisador de Palavras-Chave", page_icon="🔍")

st.image("https://raw.githubusercontent.com/jkondi18/forme-keyword-analyzer/main/logo-forme.png", width=300)

st.title("Analisador de Palavras-Chave de Blogs")
st.write("Cole os links de blogs concorrentes separados por vírgula abaixo. O sistema extrai os títulos das páginas e gera uma análise das expressões mais comuns para orientar o conteúdo da FORME.")

urls_input = st.text_area("Links dos sites", placeholder="https://blog1.com, https://blog2.com")

if st.button("Analisar"):
    urls = [url.strip() for url in urls_input.split(",") if url.strip()]
    todos_titulos = []

    for pagina in urls:
        try:
            st.info(f"⏳ Coletando: {pagina}")
            api_url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={pagina}&render=true"
            response = requests.get(api_url, timeout=40)
            if response.status_code != 200:
                raise Exception(f"Erro HTTP {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')
            titulos = soup.select("h1, h2, h3, .post-title, .entry-title, article h1, article h2")
            textos = [t.get_text(strip=True) for t in titulos if t.get_text(strip=True)]
            todos_titulos.extend(textos)
            st.success(f"✅ Coletado: {pagina} ({len(textos)} títulos)")
        except Exception as e:
            st.error(f"❌ Erro ao coletar {pagina}: {e}")

    if todos_titulos:
        texto = [t.lower() for t in todos_titulos]
        stopwords_pt = stopwords.words("portuguese")

        vectorizer = CountVectorizer(ngram_range=(2, 3), stop_words=stopwords_pt).fit(texto)
        bag_of_words = vectorizer.transform(texto)
        sum_words = bag_of_words.sum(axis=0)
        palavras_freq = [(word, sum_words[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
        palavras_freq = sorted(palavras_freq, key=lambda x: x[1], reverse=True)

        df = pd.DataFrame(palavras_freq, columns=['Expressão', 'Frequência'])

        st.subheader("📊 Expressões mais comuns entre os blogs")
        st.dataframe(df.head(20).reset_index(drop=True), use_container_width=True)

        st.download_button("📥 Baixar resultado em Excel", data=df.to_csv(index=False), file_name="expressoes_chave.csv", mime="text/csv")
    else:
        st.warning("Nenhum título encontrado nos links fornecidos.")

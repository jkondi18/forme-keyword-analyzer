
import streamlit as st
from bs4 import BeautifulSoup
import requests
from collections import Counter
import pandas as pd
import string
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')

st.set_page_config(page_title="Analisador de Palavras-Chave", page_icon="🔍")

st.title("🔍 Analisador de Palavras-Chave de Blogs")
st.write("Cole os links de blogs concorrentes separados por vírgula abaixo. O sistema extrai os títulos das páginas (h2/h3) e gera uma análise de palavras mais comuns para orientar o conteúdo da FORME.")

urls_input = st.text_area("Links dos sites", placeholder="https://blog1.com, https://blog2.com")

if st.button("Analisar"):
    urls = [url.strip() for url in urls_input.split(",") if url.strip()]
    todos_titulos = []

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            titulos = soup.find_all(['h2', 'h3'])
            textos = [t.get_text(strip=True) for t in titulos]
            todos_titulos.extend(textos)
            st.success(f"Coletado: {url} ({len(textos)} títulos)")
        except Exception as e:
            st.error(f"Erro com {url}: {e}")

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

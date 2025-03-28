import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="Racenet Scraper", layout="wide")
st.title("🏇 Racenet Horse Racing Scraper")
st.markdown("Paste a **Racenet race overview URL** (e.g. Rosehill R8) to extract full race data.")

url = st.text_input("Paste Racenet Overview URL:")
run_button = st.button("Scrape Race Data")

if run_button and url:
    # Move the call INTO here
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"
    }
    res = requests.get(url, headers=headers)

    st.text(f"Status Code: {res.status_code}")
    st.text(res.text[:1000])  # Show HTML preview

    # You can still call your full scraper here later:
    # df = scrape_racenet_data(url)
    # st.dataframe(df)


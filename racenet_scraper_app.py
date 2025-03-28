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


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"
}
res = requests.get(url, headers=headers)

st.text(f"Status Code: {res.status_code}")
st.text(res.text[:1000])  # Preview the top part of the HTML response

    soup = BeautifulSoup(res.text, "html.parser")

    runners = soup.select(".selection-row-desktop")
    data = []

    for block in runners:
        try:
            name_tag = block.select_one(".horseracing-selection-details-name.desktop")
            horse_name = name_tag.get_text(strip=True).split("(")[0].split(".", 1)[-1].strip() if name_tag else ""

            barrier = ""
            for span in block.select(".competior-meta-info span"):
                if span and span.text.strip().isdigit():
                    barrier = int(span.text.strip())
                    break
            if barrier == "":
                fallback = block.select_one(".competior-meta-info")
                if fallback:
                    match = re.search(r"\((\d{1,2})\)", fallback.get_text())
                    if match:
                        barrier = int(match.group(1))

            lines = block.get_text(separator="\n", strip=True).split("\n")
            age = next((int(l.replace("yo", "")) for l in lines if "yo" in l), "")
            gender = next((l for l in lines if re.fullmatch(r"[A-Z]", l)), "")

            rating_tag = block.select_one(".event-selection-row-right__column--rating")
            rating = int(rating_tag.text.strip()) if rating_tag and rating_tag.text.strip().isdigit() else ""

            career_tag = block.select_one(".event-selection-row-right__column--career")
            starts = wins = places = ""
            if career_tag:
                ctext = career_tag.text.strip()
                match = re.match(r"(\d+):\s*(\d+)-(\d+)-(\d+)", ctext)
                if match:
                    starts = int(match.group(1))
                    wins = int(match.group(2))
                    places = int(match.group(3)) + int(match.group(4))

            prize_tag = block.select_one(".event-selection-row-right__column--statsDropdown")
            prize_money = prize_tag.text.strip() if prize_tag else ""

            win_tag = block.select_one(".event-selection-row-right__column--wins")
            plc_tag = block.select_one(".event-selection-row-right__column--places")
            win_pct = int(win_tag.text.strip().replace("%", "")) if win_tag else ""
            plc_pct = int(plc_tag.text.strip().replace("%", "")) if plc_tag else ""

            form_tag = block.select_one(".event-selection-row-right__column--last10")
            form = form_tag.text.strip() if form_tag else ""
            last_pos = int(re.search(r"(\d)", form[::-1]).group(1)) if form and re.search(r"(\d)", form[::-1]) else ""

            last_race_tag = block.select_one(".event-selection-row-right__column--lastRace")
            last_race_info = last_race_tag.text.strip() if last_race_tag else ""

            odds_tag = block.select_one(".odds-link__odds")
            odds = odds_tag.text.strip().replace("$", "") if odds_tag else ""

            trainer_tag = block.select_one("a[href*='/profiles/trainer']")
            trainer = trainer_tag.text.strip() if trainer_tag else ""

            jockey_tag = block.select_one("a[href*='/profiles/jockey']")
            jockey_raw = jockey_tag.text.strip() if jockey_tag else ""
            jockey_match = re.match(r"(.*?)\s\((\d+(\.\d+)?)kg\)", jockey_raw)
            jockey = jockey_match.group(1) if jockey_match else jockey_raw
            jockey_weight = float(jockey_match.group(2)) if jockey_match else ""

            # Placeholder extras for your formulas
            avg_prize_per_start = ""
            last_race_date = ""
            days_since_last = ""
            form_score = recency_bonus = probability_score = win_score = class_score = experience_score = 0
            jockey_score = trainer_score = freshness_score = 0
            total_score = 0.0

            data.append({
                "Horse Name": horse_name,
                "Age": age,
                "Gender": gender,
                "Trainer": trainer,
                "Trainer Win Rate (%)": "",  # to be added
                "Jockey": jockey,
                "Jockey Weight": jockey_weight,
                "Jockey Win Rate (%)": "",  # to be added
                "Rating": rating,
                "Career Starts": starts,
                "Career Wins": wins,
                "Career Places": places,
                "Win %": win_pct,
                "Place %": plc_pct,
                "Prize Money ($)": prize_money,
                "Avg Prize Money per Start ($)": avg_prize_per_start,
                "Last Race Position": last_pos,
                "last race date (MM/DD/YYYY)": last_race_date,
                "Days since last race": days_since_last,
                "Form (Last 10 races)": form,
                "Form Score (FS)": form_score,
                "Recency Bonus (RB)": recency_bonus,
                "Probability Score (PS)": probability_score,
                "Win % Score (WS)": win_score,
                "Class Score (CS)": class_score,
                "Experience Score (ES)": experience_score,
                "Jockey Score (JS)": jockey_score,
                "Trainer Score (TS)": trainer_score,
                "Freshness Score (FRS)": freshness_score,
                "Total Form Analysis Score (FAS)": total_score
            })

        except Exception as e:
            print("Error parsing runner:", e)

    df = pd.DataFrame(data)
    return df

# Run scraper when button is clicked
if run_button and url:
    try:
        df = scrape_racenet_data(url)
        st.success("Race data scraped successfully!")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", data=csv, file_name="race_data.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

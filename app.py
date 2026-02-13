import streamlit as st
import requests
import csv
import re
import time

st.title("📱 App Store Reviews Parser")

# ==============================
# Функция извлечения app_id
# ==============================
def extract_app_id(url):
    match = re.search(r'id(\d+)', url)
    if match:
        return match.group(1)
    else:
        return None

# ==============================
# Получение отзывов для одной страны
# ==============================
def fetch_reviews(app_id, country):
    reviews = []
    page = 1

    while page <= 10:
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                break

            data = response.json()

            if "feed" not in data or "entry" not in data["feed"]:
                break

            entries = data["feed"]["entry"][1:]

            for entry in entries:
                reviews.append({
                    "country": country,
                    "user": entry["author"]["name"]["label"],
                    "rating": entry["im:rating"]["label"],
                    "title": entry["title"]["label"],
                    "text": entry["content"]["label"],
                    "version": entry["im:version"]["label"]
                })

            page += 1
            time.sleep(0.5)

        except:
            break

    return reviews

# ==============================
# Интерфейс
# ==============================
app_url = st.text_input("Введите ссылку на App Store")

if st.button("Собрать отзывы"):
    app_id = extract_app_id(app_url)

    if not app_id:
        st.error("Неверная ссылка")
    else:
        st.write("Сбор отзывов...")

        all_reviews = fetch_reviews(app_id, "us")

        if not all_reviews:
            st.warning("Отзывы не найдены")
        else:
            csv_file = "reviews.csv"
            with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=all_reviews[0].keys())
                writer.writeheader()
                writer.writerows(all_reviews)

            with open(csv_file, "rb") as f:
                st.download_button(
                    label="📥 Скачать CSV",
                    data=f,
                    file_name="appstore_reviews.csv",
                    mime="text/csv"
                )

            st.success(f"Собрано отзывов: {len(all_reviews)}")

import streamlit as st
import requests
import re
import time
from openpyxl import Workbook
from io import BytesIO

# ==============================
# Настройка страницы
# ==============================
st.set_page_config(
    page_title="App Store Reviews Parser",
    page_icon="📱",
    layout="wide"
)

# ==============================
# Кастомный CSS (красивый UI)
# ==============================
st.markdown("""
<style>
.big-title {
    font-size:40px !important;
    font-weight:700;
}
.card {
    padding:20px;
    border-radius:15px;
    background-color:#f5f7fa;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">📱 App Store Reviews Parser</p>', unsafe_allow_html=True)
st.write("Собирает отзывы из App Store и сохраняет в Excel.")

# ==============================
# Функция извлечения ID
# ==============================
def extract_app_id(url):
    match = re.search(r'id(\d+)', url)
    if match:
        return match.group(1)
    return None

# ==============================
# Список стран (можно расширять)
# ==============================
COUNTRIES = ["us", "gb", "de", "fr", "it", "es", "ca", "au"]

# ==============================
# Сбор отзывов
# ==============================
def fetch_reviews(app_id, country):
    reviews = []
    page = 1

    while page <= 10:
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
        
        try:
            r = requests.get(url)
            if r.status_code != 200:
                break

            data = r.json()

            if "feed" not in data or "entry" not in data["feed"]:
                break

            entries = data["feed"]["entry"][1:]

            for entry in entries:
                reviews.append([
                    country,
                    entry["author"]["name"]["label"],
                    entry["updated"]["label"],
                    entry["im:rating"]["label"],
                    entry["title"]["label"],
                    entry["content"]["label"],
                    entry["im:version"]["label"]
                ])

            page += 1
            time.sleep(0.3)

        except:
            break

    return reviews

# ==============================
# Интерфейс
# ==============================
col1, col2 = st.columns([3,1])

with col1:
    app_url = st.text_input("🔗 Вставьте ссылку на App Store")

with col2:
    selected_country = st.selectbox("🌍 Страна", COUNTRIES)

if st.button("🚀 Запустить сбор отзывов"):

    app_id = extract_app_id(app_url)

    if not app_id:
        st.error("❌ Неверная ссылка")
    else:
        progress = st.progress(0)
        status = st.empty()

        status.text("Сбор отзывов...")
        reviews = fetch_reviews(app_id, selected_country)
        progress.progress(100)

        if not reviews:
            st.warning("Отзывы не найдены")
        else:
            # ==============================
            # Создание Excel в памяти
            # ==============================
            wb = Workbook()
            ws = wb.active
            ws.title = "Reviews"

            headers = [
                "Country",
                "User Name",
                "Review Date",
                "Rating",
                "Title",
                "Review Text",
                "App Version"
            ]

            ws.append(headers)

            for row in reviews:
                ws.append(row)

            file_buffer = BytesIO()
            wb.save(file_buffer)
            file_buffer.seek(0)

            st.success(f"✅ Собрано отзывов: {len(reviews)}")

            st.download_button(
                label="📥 Скачать Excel",
                data=file_buffer,
                file_name="appstore_reviews.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# app.py
import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

# -----------------------------
# PAGE CONFIG + STYLING
# -----------------------------
st.set_page_config(page_title="Australia Student Dashboard", layout="wide")
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:#1a73e8;">Australia Student Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center; color:#555;">Explore cities, universities, budgets, and maps interactively</h3>', unsafe_allow_html=True)
st.markdown("---")

# -----------------------------
# CITIES & ENVIRONMENT SELECTOR
# -----------------------------
cities = [
    "Melbourne","Sydney","Adelaide","Hobart","Perth",
    "Canberra","Brisbane","Gold Coast","Darwin","Launceston",
    "Newcastle","Wollongong","Geelong","Cairns","Townsville",
    "Sunshine Coast","Toowoomba","Ballarat","Bendigo","Launceston"
]

city = st.selectbox("Select a City", cities)
env_type = st.radio("Environment Preference", ["Urban","Nature"])

# -----------------------------
# UNSPLASH DYNAMIC BACKGROUND IMAGE
# -----------------------------
def fetch_unsplash_image(city, env_type):
    access_key = "YOUR_UNSPLASH_API_KEY"  # Replace with your Unsplash API key
    query = f"{city} {env_type} skyline"
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={access_key}"
    res = requests.get(url).json()
    return res['urls']['regular']

try:
    img_url = fetch_unsplash_image(city, env_type)
    st.markdown(f"<div class='bg-container' style='background-image: url({img_url});'></div>", unsafe_allow_html=True)
except:
    st.warning("Could not fetch image. Using fallback if available.")

# -----------------------------
# UNIVERSITIES DATA (TOP 100)
# -----------------------------
uni_url = "https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json"
data = requests.get(uni_url).json()
aus_unis = [uni for uni in data if uni["country"] == "Australia"]
df_unis = pd.DataFrame(aus_unis).head(100)
selected_uni = st.selectbox("Select University", df_unis["name"])
uni_city = df_unis[df_unis["name"] == selected_uni]["state-province"].values[0]
st.markdown(f"**{selected_uni}** is located in **{uni_city or 'Unknown'}**")

# -----------------------------
# WIKIPEDIA INFO
# -----------------------------
def wiki_summary(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ','_')}"
    res = requests.get(url).json()
    return res.get("extract","Info not available")

st.subheader(f"About {city}")
st.write(wiki_summary(city))

st.subheader(f"About {selected_uni}")
st.write(wiki_summary(selected_uni))

# -----------------------------
# BUDGET / EXPENSE SIMULATOR
# -----------------------------
st.subheader("Budget Simulator")
city_data = {
    "Melbourne":{"rent":1200,"cost":2000},
    "Sydney":{"rent":1500,"cost":2300},
    "Adelaide":{"rent":900,"cost":1700},
    "Hobart":{"rent":950,"cost":1600},
    "Perth":{"rent":1000,"cost":1800},
    "Canberra":{"rent":1400,"cost":2100},
    "Brisbane":{"rent":1100,"cost":1800},
    "Gold Coast":{"rent":1000,"cost":1750},
    "Darwin":{"rent":1200,"cost":1900},
    "Launceston":{"rent":850,"cost":1500},
    "Newcastle":{"rent":950,"cost":1650},
    "Wollongong":{"rent":900,"cost":1600},
    "Geelong":{"rent":880,"cost":1550},
    "Cairns":{"rent":850,"cost":1500},
    "Townsville":{"rent":870,"cost":1520},
    "Sunshine Coast":{"rent":890,"cost":1550},
    "Toowoomba":{"rent":800,"cost":1450},
    "Ballarat":{"rent":780,"cost":1400},
    "Bendigo":{"rent":760,"cost":1380}
}

new_rent = st.number_input(f"Update Rent for {city}", value=city_data[city]["rent"])
new_cost = st.number_input(f"Update Cost of Living for {city}", value=city_data[city]["cost"])
budget = st.number_input("Enter your monthly budget ($)", min_value=500, max_value=10000, step=50)
total_expense = new_rent + new_cost
if budget >= total_expense:
    st.success(f"You can live comfortably in {city} with your budget of ${budget}")
else:
    st.warning(f"Your budget of ${budget} is not enough for {city} (Expenses: ${total_expense})")

# -----------------------------
# INTERACTIVE MAP
# -----------------------------
st.subheader("Map of City / University")
coords = {
    "Melbourne":[-37.8136, 144.9631],
    "Sydney":[-33.8688, 151.2093],
    "Adelaide":[-34.9285,138.6007],
    "Hobart":[-42.8821,147.3272],
    "Perth":[-31.9505,115.8605],
    "Canberra":[-35.2809,149.1300],
    "Brisbane":[-27.4698,153.0251],
    "Gold Coast":[-28.0167,153.4000],
    "Darwin":[-12.4634,130.8456],
    "Launceston":[-41.4332,147.1441],
    "Newcastle":[-32.9283,151.7817],
    "Wollongong":[-34.4278,150.8931],
    "Geelong":[-38.1499,144.3617],
    "Cairns":[-16.9186,145.7781],
    "Townsville":[-19.2589,146.8169],
    "Sunshine Coast":[-26.6500,153.0667],
    "Toowoomba":[-27.5606,151.9539],
    "Ballarat":[-37.5622,143.8503],
    "Bendigo":[-36.7570,144.2794]
}

m = folium.Map(location=coords[city], zoom_start=12)
folium.Marker(location=coords[city], popup=f"{city}").add_to(m)
st_folium(m, width=700, height=500)

# -----------------------------
# SUGGESTIONS / FEEDBACK BOX
# -----------------------------
st.subheader("Suggestions / Feedback")
feedback = st.text_area("Enter your suggestion or idea")
if st.button("Submit"):
    st.success("Thanks! Your suggestion has been recorded (demo).")
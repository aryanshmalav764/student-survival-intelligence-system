import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="SSIS", layout="wide")

# ---------------- CSS ----------------
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------- IMAGE ----------------
def get_image(query):
    try:
        return f"https://source.unsplash.com/1600x900/?{query}"
    except:
        return "https://via.placeholder.com/800x500"

# ---------------- WIKI ----------------
def wiki(topic):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
        return requests.get(url).json().get("extract", "No info available.")
    except:
        return "No info available."

# ---------------- DATA ----------------
df = pd.read_csv("data.csv")

# ---------------- HEADER ----------------
st.title("Student Survival Intelligence System")
st.write("Choose the best university, city and lifestyle in Australia")

# ---------------- FILTER LOGIC ----------------
state = st.selectbox("Select State", ["All"] + sorted(df["State"].unique()))

if state != "All":
    city_options = sorted(df[df["State"] == state]["City"].unique())
else:
    city_options = sorted(df["City"].unique())

city = st.selectbox("Select City", ["All"] + city_options)

field = st.selectbox("Field", ["All"] + sorted(df["Field"].unique()))
level = st.selectbox("Study Level", ["All"] + sorted(df["Level"].unique()))

budget = st.slider("Monthly Budget", 800, 5000, 2000)
tuition = st.slider("Max Tuition", 20000, 60000, 40000)

# ---------------- BACKGROUND ----------------
bg = city if city != "All" else state if state != "All" else "Australia skyline"

st.markdown(
    f"<div class='bg-image' style='background-image:url({get_image(bg)})'></div>",
    unsafe_allow_html=True
)

# ---------------- FILTER ----------------
filtered = df.copy()

if state != "All":
    filtered = filtered[filtered["State"] == state]

if city != "All":
    filtered = filtered[filtered["City"] == city]

if field != "All":
    filtered = filtered[filtered["Field"] == field]

if level != "All":
    filtered = filtered[filtered["Level"] == level]

filtered = filtered[filtered["Avg_Tuition_AUD"] <= tuition]

# ---------------- SCORE ----------------
def score(r):
    s = 0
    if r["Avg_Tuition_AUD"] <= tuition: s += 2
    if budget >= r["Living_Cost"]: s += 2
    if r["Ranking"] < 100: s += 2
    elif r["Ranking"] < 200: s += 1
    return s

filtered["Score"] = filtered.apply(score, axis=1)
filtered = filtered.sort_values(by="Score", ascending=False)

# ---------------- RESULTS ----------------
st.header("Top Recommendations")

if filtered.empty:
    st.warning("No results found. Try adjusting filters.")
else:
    for _, r in filtered.head(6).iterrows():
        st.subheader(r["University"])
        st.image(get_image(r["University"]))

        st.write(f"{r['City']}, {r['State']}")
        st.write(f"{r['Field']} | {r['Level']}")
        st.write(f"Tuition: {r['Avg_Tuition_AUD']}")
        st.write(f"Living Cost: {r['Living_Cost']}")

        st.write("Why this?")
        if r["Avg_Tuition_AUD"] <= tuition:
            st.write("- Fits your budget")
        if budget >= r["Living_Cost"]:
            st.write("- Affordable living")
        if r["Ranking"] < 100:
            st.write("- Strong ranking")

        st.write("About City:")
        st.write(wiki(r["City"]))

        st.markdown("---")

# ---------------- MAP ----------------
st.header("Map")

coords = {
    "Melbourne":[-37.81,144.96],
    "Sydney":[-33.86,151.20],
    "Brisbane":[-27.46,153.02],
    "Perth":[-31.95,115.86],
    "Adelaide":[-34.92,138.60],
    "Hobart":[-42.88,147.32],
    "Geelong":[-38.15,144.36],
    "Newcastle":[-32.93,151.78]
}

m = folium.Map(location=[-25,135], zoom_start=4)

for _, r in filtered.head(5).iterrows():
    if r["City"] in coords:
        folium.Marker(location=coords[r["City"]], popup=r["City"]).add_to(m)

st_folium(m)

# ---------------- COMPARE ----------------
st.header("Compare Universities")

u_list = sorted(df["University"].unique())

u1 = st.selectbox("First University", ["Select"] + u_list)
u2 = st.selectbox("Second University", ["Select"] + u_list)

if u1 != "Select" and u2 != "Select" and u1 != u2:
    d1 = df[df["University"] == u1].iloc[0]
    d2 = df[df["University"] == u2].iloc[0]

    score1 = 0
    score2 = 0

    if d1["Ranking"] < d2["Ranking"]: score1 += 2
    else: score2 += 2

    if d1["Avg_Tuition_AUD"] < d2["Avg_Tuition_AUD"]: score1 += 1
    else: score2 += 1

    if d1["Living_Cost"] < d2["Living_Cost"]: score1 += 1
    else: score2 += 1

    if score1 > score2:
        st.success(f"{u1} is better")
    else:
        st.success(f"{u2} is better")

# ---------------- FOOTER ----------------
st.markdown("---")
st.write("Built by Aryansh Malav")
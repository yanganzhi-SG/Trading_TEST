import streamlit as st
import pandas as pd
import itertools
import random
import requests

# =====================================================
# 🔑 GEMINI API KEYS (PASTE YOUR KEYS HERE LOCALLY)
# =====================================================

GEMINI_KEYS = [ "AIzaSyBgXQuKQsahIUbfJ2bJ0hewjxhCBThxgZo", "AIzaSyBluOzXVSItFulOip-APayR18w1jm1b8QE", "AIzaSyC5rnO3ASEVzGd8W-DSAFjgzTrfEA4XzFg", "AIzaSyARNFj-KwfpOvyrbqarm9_juitYg_ilb1w", "AIzaSyCRj9zqBpQXA3OO-7qrb5xD1GaSulk5bQ4" ]

# =====================================================
# PAGE SETUP
# =====================================================

st.set_page_config(
    page_title="AI PvPoke Engine",
    layout="wide"
)

st.title("⚔️ AI PvPoke Engine")
st.caption("Meta-aware Great League Team Builder")

# =====================================================
# LOAD CSV
# =====================================================

@st.cache_data
def load_data():
    df = pd.read_csv("cp1500_all_overall_rankings.csv")
    df.columns = df.columns.str.strip()
    df["Pokemon"] = df["Pokemon"].astype(str).str.strip()
    return df


df = load_data()
pokemon_list = df["Pokemon"].dropna().tolist()

# =====================================================
# DYNAMIC META
# =====================================================

def get_dynamic_meta(df, top_n=30):
    return df.sort_values("Score", ascending=False).head(top_n)["Pokemon"].tolist()

DYNAMIC_META = get_dynamic_meta(df)

# =====================================================
# GEMINI CALL WITH FALLBACK KEYS
# =====================================================

def call_gemini(prompt):

    for key in GEMINI_KEYS:

        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"

            payload = {
                "contents": [
                    {"parts": [{"text": prompt}]}
                ]
            }

            r = requests.post(url, json=payload, timeout=10)

            if r.status_code == 200:
                data = r.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]

        except:
            continue

    return None

# =====================================================
# AI TEAM BUILDER
# =====================================================

def ai_build_team(pokemon_list):

    prompt = f"""
You are a Pokémon GO Great League expert.

Build the BEST possible team of 6 Pokémon.

Rules:
- Use only strong PvP meta logic
- Ensure type coverage
- Avoid duplicate weaknesses
- Include balance (lead, safe swap, closer roles)

Available Pokémon:
{pokemon_list[:80]}

Return ONLY 6 Pokémon names separated by commas.
"""

    response = call_gemini(prompt)

    if not response:
        return random.sample(pokemon_list, 6)

    names = [p.strip() for p in response.split(",")]

    valid = [p for p in names if p in pokemon_list]

    if len(valid) >= 3:
        return valid[:6]

    return random.sample(pokemon_list, 6)

# =====================================================
# TEAM SCORING
# =====================================================

def score_team(team):

    score = 0
    types = []

    for p in team:

        row = df[df["Pokemon"] == p].iloc[0]

        score += float(row["Attack"]) + float(row["Defense"]) + float(row["Stamina"])

        types.append(row["Type 1"])

        if p in DYNAMIC_META:
            score += 50

    score += len(set(types)) * 40

    return score

# =====================================================
# REFINE TEAM
# =====================================================

def refine_team(team):

    weakest = min(
        team,
        key=lambda p: float(df[df["Pokemon"] == p].iloc[0]["Attack"])
    )

    team.remove(weakest)

    candidates = [p for p in pokemon_list if p not in team]

    team.append(random.choice(candidates))

    return team

# =====================================================
# SESSION STATE
# =====================================================

if "team" not in st.session_state:
    st.session_state.team = []

# =====================================================
# UI
# =====================================================

st.subheader("🧠 AI Team Builder")

if st.button("Generate AI Team"):

    st.session_state.team = ai_build_team(pokemon_list)
    st.rerun()

if st.button("🔁 Improve Team"):

    if st.session_state.team:
        st.session_state.team = refine_team(st.session_state.team)
        st.rerun()

# =====================================================
# DISPLAY TEAM
# =====================================================

st.divider()
st.subheader("🛡️ Current Team")

if not st.session_state.team:
    st.info("Click Generate AI Team")

for p in st.session_state.team:

    row = df[df["Pokemon"] == p].iloc[0]

    col1, col2 = st.columns([5, 1])

    with col1:

        st.markdown(f"### {p}")

        st.write(f"{row['Type 1']} / {row.get('Type 2','')}")

        if p in DYNAMIC_META:
            st.success("🔥 META")

    with col2:

        if st.button(f"❌ Remove {p}", key=p):

            st.session_state.team.remove(p)
            st.rerun()

# =====================================================
# STATS
# =====================================================

def team_power(team):
    return sum(
        float(df[df["Pokemon"] == p].iloc[0]["Attack"]) +
        float(df[df["Pokemon"] == p].iloc[0]["Defense"]) +
        float(df[df["Pokemon"] == p].iloc[0]["Stamina"])
        for p in team
    )

if len(st.session_state.team) == 6:

    st.divider()
    st.subheader("🔥 Team Analysis")

    st.success(f"Power Score: {team_power(st.session_state.team)}")

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📊 System")

    st.write(f"Pokémon loaded: {len(df)}")
    st.write(f"Dynamic meta size: {len(DYNAMIC_META)}")

    if st.button("Clear Team"):
        st.session_state.team = []
        st.rerun()

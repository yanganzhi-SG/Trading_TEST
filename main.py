import streamlit as st
import pandas as pd
import itertools

# =====================================================
# PAGE SETUP
# =====================================================

st.set_page_config(
    page_title="GL Team Forge",
    layout="wide"
)

st.title("⚔️ GL Team Forge")
st.caption("Great League Pokémon Team Builder")

# =====================================================
# LOAD CSV FROM GITHUB
# =====================================================

@st.cache_data
def load_data():

    url = "cp1500_all_overall_rankings.csv"  # file in same repo

    df = pd.read_csv(url)

    df.columns = df.columns.str.strip()

    df["Pokemon"] = df["Pokemon"].astype(str).str.strip()

    # make sure numbers are numeric
    numeric_cols = ["Score", "Attack", "Defense", "Stamina"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_data()

pokemon_list = sorted(df["Pokemon"].dropna().unique())

# =====================================================
# SESSION STATE
# =====================================================

if "team" not in st.session_state:
    st.session_state.team = []

# =====================================================
# SEARCH SYSTEM (FIXED)
# =====================================================

st.subheader("🔍 Search Pokémon")

search = st.text_input(
    "Type Pokémon name",
    placeholder="Try: Quagsire, Lanturn, Skarmory..."
)

def get_row(name):
    return df[df["Pokemon"] == name].iloc[0]

if search:

    search_lower = search.lower().strip()

    matches = [
        p for p in pokemon_list
        if search_lower in p.lower()
    ]

    matches = matches[:10]  # limit dropdown

    if not matches:
        st.warning("No Pokémon found.")
    else:
        for name in matches:

            row = get_row(name)

            col1, col2, col3 = st.columns([4, 3, 1])

            with col1:
                st.markdown(f"### {name}")
                st.caption(f"{row['Type 1']} / {row.get('Type 2','')}")

            with col2:
                st.write(f"⭐ Score: {row['Score']}")
                st.write(f"⚔️ Fast: {row['Fast Move']}")

            with col3:
                if st.button("Add", key=f"add_{name}"):

                    if name not in st.session_state.team and len(st.session_state.team) < 6:
                        st.session_state.team.append(name)
                        st.rerun()

# =====================================================
# TEAM DISPLAY
# =====================================================

st.divider()
st.subheader("🛡️ Your Team")

if not st.session_state.team:
    st.info("No Pokémon added yet.")

for p in st.session_state.team:

    row = get_row(p)

    col1, col2 = st.columns([5, 1])

    with col1:
        st.write(f"### {p}")
        st.caption(f"Score: {row['Score']} | {row['Type 1']} / {row.get('Type 2','')}")

    with col2:
        if st.button("❌", key=f"remove_{p}"):
            st.session_state.team.remove(p)
            st.rerun()

# =====================================================
# TEAM SCORING
# =====================================================

def team_score(team):

    return sum(
        float(get_row(p)["Score"])
        for p in team
    )

# =====================================================
# BEST TEAM OF 3
# =====================================================

if len(st.session_state.team) >= 3:

    st.divider()
    st.subheader("🏆 Best Team of 3")

    combos = itertools.combinations(st.session_state.team, 3)

    best_combo = None
    best_score = 0

    for combo in combos:

        score = team_score(combo)

        if score > best_score:
            best_score = score
            best_combo = combo

    if best_combo:

        st.success(
            f"""
🔥 Best Trio:

1. {best_combo[0]}
2. {best_combo[1]}
3. {best_combo[2]}

⭐ Score: {best_score}
"""
        )

# =====================================================
# FULL TEAM ANALYSIS
# =====================================================

if len(st.session_state.team) == 6:

    st.divider()
    st.subheader("🔥 Full Team Analysis")

    total = team_score(st.session_state.team)

    st.success(f"""
Total Team Score: {total}
Average: {round(total/6, 2)}
""")

# =====================================================
# SIDEBAR INFO
# =====================================================

with st.sidebar:

    st.header("📊 Stats")

    st.write(f"Pokémon loaded: {len(df)}")
    st.write(f"Team size: {len(st.session_state.team)}")

    if st.button("Clear Team"):
        st.session_state.team = []
        st.rerun()

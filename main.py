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
st.caption("Great League PvP Team Builder")

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
pokemon_list = sorted(df["Pokemon"].unique())

# =====================================================
# TYPE EFFECTIVENESS (simplified PvP logic)
# =====================================================

TYPE_EFFECTS = {
    "Normal": [],
    "Fire": ["Grass", "Ice", "Bug", "Steel"],
    "Water": ["Fire", "Ground", "Rock"],
    "Electric": ["Water", "Flying"],
    "Grass": ["Water", "Ground", "Rock"],
    "Ice": ["Grass", "Ground", "Flying", "Dragon"],
    "Fighting": ["Normal", "Ice", "Rock", "Dark", "Steel"],
    "Poison": ["Grass", "Fairy"],
    "Ground": ["Fire", "Electric", "Poison", "Rock", "Steel"],
    "Flying": ["Grass", "Fighting", "Bug"],
    "Psychic": ["Fighting", "Poison"],
    "Bug": ["Grass", "Psychic", "Dark"],
    "Rock": ["Fire", "Ice", "Flying", "Bug"],
    "Ghost": ["Psychic", "Ghost"],
    "Dragon": ["Dragon"],
    "Dark": ["Psychic", "Ghost"],
    "Steel": ["Ice", "Rock", "Fairy"],
    "Fairy": ["Fighting", "Dragon", "Dark"],
}

def type_effect(attacker_type, defender_type):

    if defender_type in TYPE_EFFECTS.get(attacker_type, []):
        return "🟢 Super Effective"

    if attacker_type in TYPE_EFFECTS.get(defender_type, []):
        return "🔴 Weak"

    return ""

# =====================================================
# MOVE EFFECTS (color coded)
# =====================================================

MOVE_EFFECTS = {
    "Power-Up Punch": ("🟢 +1 ATK", "#2ecc71"),
    "Psychic Fangs": ("🔴 -1 DEF", "#e74c3c"),
    "Breaking Swipe": ("🔴 -1 ATK", "#e74c3c"),
    "Icy Wind": ("🔴 -1 ATK", "#3498db"),
    "Bubble Beam": ("🔴 -1 ATK", "#3498db"),
    "Draco Meteor": ("🔴 -2 ATK", "#9b59b6"),
    "Overheat": ("🔴 -2 ATK", "#e67e22"),
    "Psychic": ("🔴 -1 DEF (chance)", "#f1c40f"),
    "Flamethrower": ("🔴 -1 ATK (chance)", "#f39c12"),
}

def move_effect(move):

    if move in MOVE_EFFECTS:
        return MOVE_EFFECTS[move]

    return ("", "")  # no text if no effect

# =====================================================
# SESSION STATE
# =====================================================

if "team" not in st.session_state:
    st.session_state.team = []

# =====================================================
# SEARCH
# =====================================================

st.subheader("🔍 Search Pokémon")

search = st.text_input(
    "Type Pokémon name",
    placeholder="Example: Quagsire"
)

def get_row(name):
    return df[df["Pokemon"] == name].iloc[0]

if search:

    matches = [
        p for p in pokemon_list
        if search.lower() in p.lower()
    ][:10]

    if not matches:
        st.warning("No Pokémon found.")
    else:

        for name in matches:

            row = get_row(name)

            col1, col2, col3 = st.columns([4, 4, 1])

            with col1:
                st.markdown(f"### {name}")
                st.caption(f"{row['Type 1']} / {row.get('Type 2','')}")

            with col2:

                # FAST MOVE
                st.write(f"⚡ Fast: {row['Fast Move']}")

                # CHARGE 1
                effect1, color1 = move_effect(row["Charged Move 1"])
                if effect1:
                    st.markdown(
                        f"🔥 {row['Charged Move 1']}  <span style='color:{color1}'>{effect1}</span>",
                        unsafe_allow_html=True
                    )
                else:
                    st.write(f"🔥 {row['Charged Move 1']}")

                # CHARGE 2
                effect2, color2 = move_effect(row["Charged Move 2"])
                if effect2:
                    st.markdown(
                        f"💥 {row['Charged Move 2']}  <span style='color:{color2}'>{effect2}</span>",
                        unsafe_allow_html=True
                    )
                else:
                    st.write(f"💥 {row['Charged Move 2']}")

            with col3:
                if st.button("Add", key=f"add_{name}"):

                    if len(st.session_state.team) < 6:
                        if name not in st.session_state.team:
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

        st.markdown(f"### {p}")

        effect1, color1 = move_effect(row["Charged Move 1"])
        effect2, color2 = move_effect(row["Charged Move 2"])

        st.write(f"⚡ Fast: {row['Fast Move']}")

        if effect1:
            st.markdown(
                f"🔥 {row['Charged Move 1']} <span style='color:{color1}'>{effect1}</span>",
                unsafe_allow_html=True
            )
        else:
            st.write(f"🔥 {row['Charged Move 1']}")

        if effect2:
            st.markdown(
                f"💥 {row['Charged Move 2']} <span style='color:{color2}'>{effect2}</span>",
                unsafe_allow_html=True
            )
        else:
            st.write(f"💥 {row['Charged Move 2']}")

        # TYPE EFFECTIVENESS PREVIEW
        t1 = row["Type 1"]
        t2 = row.get("Type 2", "")

        st.caption(
            f"Type: {t1} / {t2}"
        )

    with col2:
        if st.button("❌", key=f"remove_{p}"):
            st.session_state.team.remove(p)
            st.rerun()

# =====================================================
# SIMPLE TEAM SCORE (STATS BASED)
# =====================================================

def team_power(team):

    total = 0

    for p in team:

        row = get_row(p)

        total += (
            float(row["Attack"]) +
            float(row["Defense"]) +
            float(row["Stamina"])
        )

    return total

# =====================================================
# BEST TEAM OF 3
# =====================================================

if len(st.session_state.team) >= 3:

    st.divider()
    st.subheader("🏆 Best Team of 3")

    combos = itertools.combinations(st.session_state.team, 3)

    best = None
    best_score = 0

    for c in combos:

        score = team_power(c)

        if score > best_score:
            best_score = score
            best = c

    if best:

        st.success(
            f"""
🔥 Best Trio:

{best[0]}
{best[1]}
{best[2]}

💪 Power: {best_score}
"""
        )

# =====================================================
# FULL TEAM
# =====================================================

if len(st.session_state.team) == 6:

    st.divider()
    st.subheader("🔥 Full Team Analysis")

    power = team_power(st.session_state.team)

    st.success(
        f"""
Total Power: {power}
Average: {round(power/6, 2)}
"""
    )

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📊 Stats")

    st.write(f"Pokémon loaded: {len(df)}")
    st.write(f"Team size: {len(st.session_state.team)}")

    if st.button("Clear Team"):
        st.session_state.team = []
        st.rerun()

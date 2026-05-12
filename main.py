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
st.caption("Pokémon GO Great League Team Builder")

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
# SESSION STATE
# =====================================================

if "team" not in st.session_state:
    st.session_state.team = []

if "swap_index" not in st.session_state:
    st.session_state.swap_index = 0

# =====================================================
# HELPERS
# =====================================================

def get_row(name):
    return df[df["Pokemon"] == name].iloc[0]


def type_score(a, b):

    # simple synergy score: stats + diversity
    ra = get_row(a)
    rb = get_row(b)

    score = 0

    # stat balance
    score += abs(float(ra["Defense"]) - float(rb["Attack"])) * 0.5

    # type diversity bonus
    if ra["Type 1"] != rb["Type 1"]:
        score += 20

    if ra.get("Type 2", "") != rb.get("Type 2", ""):
        score += 10

    return score


def suggest_teammates(pokemon):

    candidates = [
        p for p in pokemon_list
        if p != pokemon
    ]

    scored = []

    for c in candidates:
        scored.append((c, type_score(pokemon, c)))

    scored.sort(key=lambda x: x[1], reverse=True)

    return [s[0] for s in scored[:10]]


# =====================================================
# SEARCH
# =====================================================

st.subheader("🔍 Search Pokémon")

search = st.text_input("Type Pokémon name")

def move_card(name):

    row = get_row(name)

    st.markdown(f"### {name}")
    st.caption(f"{row['Type 1']} / {row.get('Type 2','')}")

    st.write(f"⚡ Fast: {row['Fast Move']}")
    st.write(f"🔥 {row['Charged Move 1']}")
    st.write(f"💥 {row['Charged Move 2']}")


if search:

    matches = [
        p for p in pokemon_list
        if search.lower() in p.lower()
    ][:8]

    for name in matches:

        col1, col2 = st.columns([5, 1])

        with col1:
            move_card(name)

        with col2:

            if st.button("Add", key=f"add_{name}"):

                if len(st.session_state.team) < 6:
                    if name not in st.session_state.team:
                        st.session_state.team.append(name)
                        st.rerun()

# =====================================================
# TEAM DISPLAY + SUGGESTIONS
# =====================================================

st.divider()
st.subheader("🛡️ Your Team")

if not st.session_state.team:
    st.info("No Pokémon added yet.")

for i, p in enumerate(st.session_state.team):

    row = get_row(p)

    col1, col2 = st.columns([4, 2])

    with col1:

        move_card(p)

    with col2:

        st.markdown("### 🤝 Suggested Teammates")

        suggestions = suggest_teammates(p)

        # show 2 suggestions only
        shown = suggestions[:2]

        for j, s in enumerate(shown):

            if s in st.session_state.team:

                st.success(f"✔ {s} (Already in team)")
            else:

                st.warning(f"{s}")

                if st.button(
                    f"Change → {s}",
                    key=f"swap_{i}_{j}"
                ):

                    # replace current pokemon with suggestion
                    st.session_state.team[i] = s
                    st.rerun()

        # CHANGE RANDOM BUTTON
        if st.button(f"🔁 Suggest New", key=f"new_{i}"):

            st.session_state.swap_index += 1

            new_suggestion = suggestions[
                st.session_state.swap_index % len(suggestions)
            ]

            if new_suggestion not in st.session_state.team:

                st.session_state.team[i] = new_suggestion
                st.rerun()

# =====================================================
# REMOVE POKEMON
# =====================================================

for p in st.session_state.team:

    if st.button(f"❌ Remove {p}", key=f"rm_{p}"):

        st.session_state.team.remove(p)
        st.rerun()

# =====================================================
# TEAM POWER
# =====================================================

def team_power(team):

    return sum(
        float(get_row(p)["Attack"]) +
        float(get_row(p)["Defense"]) +
        float(get_row(p)["Stamina"])
        for p in team
    )

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

1. {best[0]}
2. {best[1]}
3. {best[2]}

💪 Score: {best_score}
"""
        )

# =====================================================
# FULL TEAM
# =====================================================

if len(st.session_state.team) == 6:

    st.divider()
    st.subheader("🔥 Full Team Analysis")

    total = team_power(st.session_state.team)

    st.success(
        f"""
Total Power: {total}
Average: {round(total/6, 2)}
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

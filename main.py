import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Pokémon GO Search",
    layout="wide"
)

st.title("⚔️ Pokémon GO Search Engine")

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():
    df = pd.read_csv("cp1500_all_overall_rankings.csv")

    df.columns = df.columns.str.strip()

    df["Pokemon"] = (
        df["Pokemon"]
        .astype(str)
        .str.strip()
    )

    return df


df = load_data()

pokemon_names = sorted(
    df["Pokemon"]
    .dropna()
    .unique()
    .tolist()
)

# =========================================================
# TYPE EFFECTIVENESS
# =========================================================

TYPE_EFFECTIVENESS = {
    "water": {
        "strong": ["fire", "ground", "rock"],
        "weak": ["water", "grass", "dragon"]
    },
    "ground": {
        "strong": ["fire", "electric", "poison", "rock", "steel"],
        "weak": ["grass", "bug"],
        "immune": ["flying"]
    },
    "rock": {
        "strong": ["fire", "ice", "flying", "bug"],
        "weak": ["fighting", "ground", "steel"]
    },
    "electric": {
        "strong": ["water", "flying"],
        "weak": ["electric", "grass", "dragon"],
        "immune": ["ground"]
    },
    "grass": {
        "strong": ["water", "ground", "rock"],
        "weak": ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"]
    },
    "ice": {
        "strong": ["grass", "ground", "flying", "dragon"],
        "weak": ["fire", "water", "ice", "steel"]
    },
    "ghost": {
        "strong": ["psychic", "ghost"],
        "weak": ["dark"]
    },
    "dragon": {
        "strong": ["dragon"],
        "weak": ["steel"],
        "immune": ["fairy"]
    },
    "normal": {
        "strong": [],
        "weak": ["rock", "steel"],
        "immune": ["ghost"]
    },
    "fighting": {
        "strong": ["normal", "rock", "steel", "ice", "dark"],
        "weak": ["poison", "flying", "psychic", "bug", "fairy"],
        "immune": ["ghost"]
    },
    "flying": {
        "strong": ["grass", "fighting", "bug"],
        "weak": ["electric", "rock", "steel"]
    }
}

# =========================================================
# MOVE TYPES
# =========================================================

MOVE_TYPES = {
    "Mud Shot": "ground",
    "Mud Bomb": "ground",
    "Earthquake": "ground",
    "Stone Edge": "rock",
    "Body Slam": "normal",
    "Rollout": "rock",
    "Hydro Cannon": "water",
    "Surf": "water",
    "Ice Beam": "ice",
    "Thunderbolt": "electric",
    "Frenzy Plant": "grass",
    "Shadow Ball": "ghost",
    "Dragon Claw": "dragon",
    "Sky Attack": "flying",
    "Counter": "fighting",
    "Lick": "ghost",
    "Spark": "electric",
    "Wing Attack": "flying",
    "Volt Switch": "electric",
    "Water Gun": "water"
}

# =========================================================
# SESSION STATE
# =========================================================

if "selected_pokemon" not in st.session_state:
    st.session_state.selected_pokemon = None

# =========================================================
# SEARCH BOX
# =========================================================

st.subheader("🔍 Search Pokémon")

search = st.text_input(
    "",
    placeholder="Start typing... like 'qu'"
)

# =========================================================
# LIVE SEARCH RESULTS
# =========================================================

matches = []

if search:

    search_lower = search.lower().strip()

    matches = [
        p for p in pokemon_names
        if p.lower().startswith(search_lower)
    ]

# =========================================================
# SHOW RESULTS ONLY IF NO POKEMON SELECTED
# =========================================================

if matches and st.session_state.selected_pokemon is None:

    st.markdown("### Results")

    for pokemon in matches[:15]:

        if st.button(
            pokemon,
            key=f"search_{pokemon}",
            use_container_width=True
        ):
            st.session_state.selected_pokemon = pokemon
            st.rerun()

# =========================================================
# CLEAR BUTTON
# =========================================================

if st.session_state.selected_pokemon is not None:

    if st.button("⬅️ Back To Search"):
        st.session_state.selected_pokemon = None
        st.rerun()

# =========================================================
# DISPLAY POKEMON
# =========================================================

selected_pokemon = st.session_state.selected_pokemon

if selected_pokemon:

    pokemon_data = df[df["Pokemon"] == selected_pokemon]

    if not pokemon_data.empty:

        row = pokemon_data.iloc[0]

        st.divider()

        st.header(f"⚔️ {selected_pokemon}")

        # =========================================================
        # TYPES
        # =========================================================

        type1 = str(row["Type 1"]).lower()

        type2 = ""

        if "Type 2" in row and pd.notna(row["Type 2"]):
            type2 = str(row["Type 2"]).lower()

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("🧬 Types")

            st.success(type1.capitalize())

            if type2 and type2 != "nan":
                st.success(type2.capitalize())

        # =========================================================
        # STATS
        # =========================================================

        with col2:

            st.subheader("📊 Stats")

            st.write(f"⚔️ Attack: {row['Attack']}")
            st.write(f"🛡️ Defense: {row['Defense']}")
            st.write(f"❤️ HP: {row['Stamina']}")
            st.write(f"🔥 CP: {row['CP']}")

        st.divider()

        # =========================================================
        # MOVES
        # =========================================================

        st.subheader("⚡ Moves")

        move_list = [
            str(row["Fast Move"]).strip(),
            str(row["Charged Move 1"]).strip(),
            str(row["Charged Move 2"]).strip()
        ]

        for move in move_list:

            move_type = MOVE_TYPES.get(move, "unknown")

            with st.container(border=True):

                st.markdown(f"### {move}")

                st.write(f"Type: **{move_type.capitalize()}**")

                if move_type in TYPE_EFFECTIVENESS:

                    data = TYPE_EFFECTIVENESS[move_type]

                    strong = data.get("strong", [])
                    weak = data.get("weak", [])
                    immune = data.get("immune", [])

                    if strong:
                        st.success(
                            "✅ Super Effective Against: "
                            + ", ".join(
                                [x.capitalize() for x in strong]
                            )
                        )

                    if weak:
                        st.error(
                            "❌ Not Very Effective Against: "
                            + ", ".join(
                                [x.capitalize() for x in weak]
                            )
                        )

                    if immune:
                        st.warning(
                            "🚫 No Effect Against: "
                            + ", ".join(
                                [x.capitalize() for x in immune]
                            )
                        )

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📘 Search Features")

    st.write("✅ Live search while typing")
    st.write("✅ No need to press enter")
    st.write("✅ Instant clickable results")
    st.write("✅ Results disappear after clicking")
    st.write("✅ Back button to search again")

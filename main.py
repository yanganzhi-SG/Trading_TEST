import streamlit as st
import pandas as pd

# =====================================================
# PAGE SETUP
# =====================================================

st.set_page_config(
    page_title="Pokémon GO Move Checker",
    layout="wide"
)

st.title("⚔️ Pokémon GO Move & Type Checker")
st.caption("Search Pokémon with live autocomplete")

# =====================================================
# LOAD CSV
# =====================================================

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

# =====================================================
# REMOVE DUPLICATES
# =====================================================

pokemon_names = sorted(df["Pokemon"].dropna().unique().tolist())

# =====================================================
# TYPE EFFECTIVENESS
# =====================================================

TYPE_EFFECTIVENESS = {
    "fire": {
        "strong": ["grass", "ice", "bug", "steel"],
        "weak": ["fire", "water", "rock", "dragon"]
    },
    "water": {
        "strong": ["fire", "ground", "rock"],
        "weak": ["water", "grass", "dragon"]
    },
    "grass": {
        "strong": ["water", "ground", "rock"],
        "weak": ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"]
    },
    "electric": {
        "strong": ["water", "flying"],
        "weak": ["electric", "grass", "dragon"],
        "immune": ["ground"]
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
    "ghost": {
        "strong": ["psychic", "ghost"],
        "weak": ["dark"],
        "immune": ["normal"]
    },
    "dragon": {
        "strong": ["dragon"],
        "weak": ["steel"],
        "immune": ["fairy"]
    },
    "fighting": {
        "strong": ["normal", "rock", "steel", "ice", "dark"],
        "weak": ["poison", "flying", "psychic", "bug", "fairy"],
        "immune": ["ghost"]
    },
    "flying": {
        "strong": ["grass", "fighting", "bug"],
        "weak": ["electric", "rock", "steel"]
    },
    "ice": {
        "strong": ["grass", "ground", "flying", "dragon"],
        "weak": ["fire", "water", "ice", "steel"]
    },
    "dark": {
        "strong": ["psychic", "ghost"],
        "weak": ["fighting", "dark", "fairy"]
    },
    "steel": {
        "strong": ["ice", "rock", "fairy"],
        "weak": ["fire", "water", "electric", "steel"]
    },
    "fairy": {
        "strong": ["fighting", "dragon", "dark"],
        "weak": ["fire", "poison", "steel"]
    },
    "normal": {
        "strong": [],
        "weak": ["rock", "steel"],
        "immune": ["ghost"]
    }
}

# =====================================================
# MOVE TYPES
# =====================================================

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

# =====================================================
# SEARCH
# =====================================================

st.subheader("🔍 Search Pokémon")

search = st.text_input(
    "Type Pokémon name",
    placeholder="Example: quaq"
)

selected_pokemon = None

# LIVE FILTERING
if search:

    matches = [
        p for p in pokemon_names
        if search.lower() in p.lower()
    ]

    if len(matches) > 0:

        selected_pokemon = st.selectbox(
            "Select Pokémon",
            matches,
            index=0
        )

    else:
        st.error("No Pokémon found.")

# =====================================================
# DISPLAY
# =====================================================

if selected_pokemon:

    poke_rows = df[df["Pokemon"] == selected_pokemon]

    if len(poke_rows) > 0:

        row = poke_rows.iloc[0]

        type1 = str(row["Type 1"]).lower()

        type2 = ""

        if "Type 2" in row and pd.notna(row["Type 2"]):
            type2 = str(row["Type 2"]).lower()

        st.divider()

        st.header(selected_pokemon)

        col1, col2 = st.columns(2)

        # =====================================================
        # TYPES
        # =====================================================

        with col1:

            st.subheader("🛡️ Types")

            st.success(type1.capitalize())

            if type2 and type2 != "nan":
                st.success(type2.capitalize())

        # =====================================================
        # STATS
        # =====================================================

        with col2:

            st.subheader("📊 Stats")

            st.write(f"⚔️ Attack: {row['Attack']}")
            st.write(f"🛡️ Defense: {row['Defense']}")
            st.write(f"❤️ Stamina: {row['Stamina']}")
            st.write(f"🔥 CP: {row['CP']}")

        st.divider()

        # =====================================================
        # MOVES
        # =====================================================

        st.subheader("⚔️ Moves")

        move_list = [
            ("Fast Move", str(row["Fast Move"]).strip()),
            ("Charged Move 1", str(row["Charged Move 1"]).strip()),
            ("Charged Move 2", str(row["Charged Move 2"]).strip())
        ]

        for move_label, move_name in move_list:

            move_type = MOVE_TYPES.get(move_name, "unknown")

            with st.container(border=True):

                st.markdown(f"### {move_name}")

                st.write(f"Move Type: **{move_type.capitalize()}**")

                if move_type in TYPE_EFFECTIVENESS:

                    data = TYPE_EFFECTIVENESS[move_type]

                    strong = data.get("strong", [])
                    weak = data.get("weak", [])
                    immune = data.get("immune", [])

                    if strong:
                        st.success(
                            "✅ Super Effective: " +
                            ", ".join([x.capitalize() for x in strong])
                        )

                    if weak:
                        st.error(
                            "❌ Not Effective: " +
                            ", ".join([x.capitalize() for x in weak])
                        )

                    if immune:
                        st.warning(
                            "🚫 No Effect: " +
                            ", ".join([x.capitalize() for x in immune])
                        )

        # =====================================================
        # WEAKNESSES
        # =====================================================

        st.divider()

        st.subheader("⚠️ Type Matchups")

        weak_to = []
        resist_to = []

        for atk_type, data in TYPE_EFFECTIVENESS.items():

            strong = data.get("strong", [])
            weak = data.get("weak", [])

            if type1 in strong or type2 in strong:
                weak_to.append(atk_type.capitalize())

            if type1 in weak or type2 in weak:
                resist_to.append(atk_type.capitalize())

        c1, c2 = st.columns(2)

        with c1:
            st.error("Weak To")
            st.write(", ".join(weak_to) if weak_to else "None")

        with c2:
            st.success("Resists")
            st.write(", ".join(resist_to) if resist_to else "None")

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📊 Database")

    st.write(f"Pokémon Loaded: {len(pokemon_names)}")

    st.write("✅ Working live search")
    st.write("✅ Dropdown autocomplete")
    st.write("✅ Move effectiveness")
    st.write("✅ Type weaknesses")

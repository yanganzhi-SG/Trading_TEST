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
st.caption("Search a Pokémon to see its types, moves, and effectiveness")

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

# =====================================================
# TYPE EFFECTIVENESS CHART
# =====================================================

TYPE_EFFECTIVENESS = {
    "normal": {
        "strong": [],
        "weak": ["rock", "steel"],
        "immune": ["ghost"]
    },
    "fire": {
        "strong": ["grass", "ice", "bug", "steel"],
        "weak": ["fire", "water", "rock", "dragon"]
    },
    "water": {
        "strong": ["fire", "ground", "rock"],
        "weak": ["water", "grass", "dragon"]
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
    "fighting": {
        "strong": ["normal", "ice", "rock", "dark", "steel"],
        "weak": ["poison", "flying", "psychic", "bug", "fairy"],
        "immune": ["ghost"]
    },
    "poison": {
        "strong": ["grass", "fairy"],
        "weak": ["poison", "ground", "rock", "ghost"],
        "immune": ["steel"]
    },
    "ground": {
        "strong": ["fire", "electric", "poison", "rock", "steel"],
        "weak": ["grass", "bug"],
        "immune": ["flying"]
    },
    "flying": {
        "strong": ["grass", "fighting", "bug"],
        "weak": ["electric", "rock", "steel"]
    },
    "psychic": {
        "strong": ["fighting", "poison"],
        "weak": ["psychic", "steel"],
        "immune": ["dark"]
    },
    "bug": {
        "strong": ["grass", "psychic", "dark"],
        "weak": ["fire", "fighting", "poison", "flying", "ghost", "steel", "fairy"]
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
# SEARCH BOX WITH AUTOCOMPLETE
# =====================================================

pokemon_names = sorted(df["Pokemon"].unique())

search_text = st.text_input(
    "🔍 Search Pokémon",
    placeholder="Type like: quaq"
)

filtered_names = []

if search_text:

    filtered_names = [
        p for p in pokemon_names
        if search_text.lower() in p.lower()
    ][:20]

selected_pokemon = None

if filtered_names:

    selected_pokemon = st.selectbox(
        "Choose Pokémon",
        filtered_names
    )

# =====================================================
# DISPLAY POKEMON
# =====================================================

if selected_pokemon:

    rows = df[df["Pokemon"] == selected_pokemon]

    if not rows.empty:

        row = rows.iloc[0]

        st.divider()

        st.header(f"🛡️ {selected_pokemon}")

        type1 = str(row["Type 1"]).lower()

        type2 = ""
        if "Type 2" in row and pd.notna(row["Type 2"]):
            type2 = str(row["Type 2"]).lower()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Types")

            st.success(type1.capitalize())

            if type2 and type2 != "nan":
                st.success(type2.capitalize())

        with col2:
            st.subheader("Stats")

            st.write(f"⚔️ Attack: {row['Attack']}")
            st.write(f"🛡️ Defense: {row['Defense']}")
            st.write(f"❤️ Stamina: {row['Stamina']}")
            st.write(f"🔥 CP: {row['CP']}")

        st.divider()

        # =====================================================
        # MOVES
        # =====================================================

        moves = []

        fast_move = str(row["Fast Move"]).strip()
        charge1 = str(row["Charged Move 1"]).strip()
        charge2 = str(row["Charged Move 2"]).strip()

        moves.append(("Fast Move", fast_move))
        moves.append(("Charged Move 1", charge1))
        moves.append(("Charged Move 2", charge2))

        st.subheader("⚔️ Moves")

        for label, move in moves:

            move_type = MOVE_TYPES.get(move, "unknown")

            with st.container(border=True):

                st.markdown(f"### {move}")
                st.write(f"Move Type: **{move_type.capitalize()}**")

                if move_type in TYPE_EFFECTIVENESS:

                    strong = TYPE_EFFECTIVENESS[move_type].get("strong", [])
                    weak = TYPE_EFFECTIVENESS[move_type].get("weak", [])
                    immune = TYPE_EFFECTIVENESS[move_type].get("immune", [])

                    if strong:
                        st.success(
                            "✅ Super Effective Against: "
                            + ", ".join([x.capitalize() for x in strong])
                        )

                    if weak:
                        st.error(
                            "❌ Not Very Effective Against: "
                            + ", ".join([x.capitalize() for x in weak])
                        )

                    if immune:
                        st.warning(
                            "🚫 No Effect Against: "
                            + ", ".join([x.capitalize() for x in immune])
                        )

        # =====================================================
        # TYPE WEAKNESSES
        # =====================================================

        st.divider()

        st.subheader("⚠️ Pokémon Type Matchups")

        weaknesses = []
        resistances = []

        for attack_type, data in TYPE_EFFECTIVENESS.items():

            strong_against = data.get("strong", [])

            if type1 in strong_against or type2 in strong_against:
                weaknesses.append(attack_type)

            weak_against = data.get("weak", [])

            if type1 in weak_against or type2 in weak_against:
                resistances.append(attack_type)

        col1, col2 = st.columns(2)

        with col1:
            st.error(
                "Weak To:\n\n" +
                ", ".join([x.capitalize() for x in weaknesses])
            )

        with col2:
            st.success(
                "Resists:\n\n" +
                ", ".join([x.capitalize() for x in resistances])
            )

else:
    st.info("Start typing a Pokémon name above.")

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📊 Database")

    st.write(f"Pokémon Loaded: {len(df)}")

    st.write("Autocomplete enabled")
    st.write("Move effectiveness enabled")
    st.write("Type weakness checker enabled")

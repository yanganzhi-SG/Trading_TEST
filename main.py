import streamlit as st
import pandas as pd

# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="Pokemon Search",
    layout="wide"
)

st.title("⚔️ Pokémon GO Search")

# =========================================================
# LOAD CSV
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
# MOVE TYPES
# =========================================================

MOVE_TYPES = {
    "Mud Shot": "Ground",
    "Mud Bomb": "Ground",
    "Earthquake": "Ground",
    "Stone Edge": "Rock",
    "Body Slam": "Normal",
    "Rollout": "Rock",
    "Hydro Cannon": "Water",
    "Surf": "Water",
    "Ice Beam": "Ice",
    "Thunderbolt": "Electric",
    "Frenzy Plant": "Grass",
    "Shadow Ball": "Ghost",
    "Dragon Claw": "Dragon",
    "Sky Attack": "Flying",
    "Counter": "Fighting",
    "Lick": "Ghost",
    "Spark": "Electric",
    "Wing Attack": "Flying",
    "Volt Switch": "Electric",
    "Water Gun": "Water"
}

# =========================================================
# TYPE EFFECTIVENESS
# =========================================================

TYPE_EFFECTIVENESS = {
    "Water": {
        "good": ["Fire", "Ground", "Rock"],
        "bad": ["Water", "Grass", "Dragon"]
    },
    "Ground": {
        "good": ["Fire", "Electric", "Poison", "Rock", "Steel"],
        "bad": ["Grass", "Bug"],
        "immune": ["Flying"]
    },
    "Rock": {
        "good": ["Fire", "Ice", "Flying", "Bug"],
        "bad": ["Fighting", "Ground", "Steel"]
    },
    "Electric": {
        "good": ["Water", "Flying"],
        "bad": ["Electric", "Grass", "Dragon"],
        "immune": ["Ground"]
    },
    "Grass": {
        "good": ["Water", "Ground", "Rock"],
        "bad": ["Fire", "Grass", "Poison", "Flying"]
    },
    "Ice": {
        "good": ["Grass", "Ground", "Flying", "Dragon"],
        "bad": ["Fire", "Water", "Ice", "Steel"]
    },
    "Ghost": {
        "good": ["Psychic", "Ghost"],
        "bad": ["Dark"]
    },
    "Dragon": {
        "good": ["Dragon"],
        "bad": ["Steel"],
        "immune": ["Fairy"]
    },
    "Flying": {
        "good": ["Grass", "Fighting", "Bug"],
        "bad": ["Electric", "Rock", "Steel"]
    },
    "Fighting": {
        "good": ["Normal", "Rock", "Steel", "Ice", "Dark"],
        "bad": ["Poison", "Flying", "Psychic", "Bug", "Fairy"]
    }
}

# =========================================================
# SESSION STATE
# =========================================================

if "selected_pokemon" not in st.session_state:
    st.session_state.selected_pokemon = ""

# =========================================================
# SEARCH INPUT
# =========================================================

search = st.text_input(
    "🔍 Search Pokémon",
    value="",
    placeholder="Type qu..."
)

# =========================================================
# LIVE SEARCH RESULTS
# =========================================================

if search != "" and st.session_state.selected_pokemon == "":

    matches = []

    for pokemon in pokemon_names:

        if pokemon.lower().startswith(search.lower()):
            matches.append(pokemon)

    if len(matches) > 0:

        st.markdown("### Pokémon Results")

        for pokemon in matches[:15]:

            # THIS MAKES CLICKABLE LIVE RESULTS
            if st.button(
                pokemon,
                key=pokemon,
                use_container_width=True
            ):

                # SAVE SELECTED POKEMON
                st.session_state.selected_pokemon = pokemon

                # INSTANTLY REFRESH PAGE
                st.rerun()

# =========================================================
# SHOW SELECTED POKEMON
# =========================================================

selected = st.session_state.selected_pokemon

if selected != "":

    pokemon_data = df[df["Pokemon"] == selected]

    if not pokemon_data.empty:

        row = pokemon_data.iloc[0]

        st.divider()

        st.header(f"⚔️ {selected}")

        # =====================================================
        # BACK BUTTON
        # =====================================================

        if st.button("⬅️ Back To Search"):

            st.session_state.selected_pokemon = ""

            st.rerun()

        # =====================================================
        # TYPES
        # =====================================================

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("🧬 Types")

            st.success(str(row["Type 1"]))

            if "Type 2" in row:

                type2 = str(row["Type 2"])

                if type2 != "nan":
                    st.success(type2)

        # =====================================================
        # STATS
        # =====================================================

        with col2:

            st.subheader("📊 Stats")

            if "Attack" in row:
                st.write(f"⚔️ Attack: {row['Attack']}")

            if "Defense" in row:
                st.write(f"🛡️ Defense: {row['Defense']}")

            if "Stamina" in row:
                st.write(f"❤️ HP: {row['Stamina']}")

            if "CP" in row:
                st.write(f"🔥 CP: {row['CP']}")

        st.divider()

        # =====================================================
        # MOVES
        # =====================================================

        st.subheader("⚡ Moves")

        moves = []

        if "Fast Move" in row:
            moves.append(str(row["Fast Move"]))

        if "Charged Move 1" in row:
            moves.append(str(row["Charged Move 1"]))

        if "Charged Move 2" in row:
            moves.append(str(row["Charged Move 2"]))

        for move in moves:

            move_type = MOVE_TYPES.get(move, "Unknown")

            with st.container(border=True):

                st.markdown(f"### {move}")

                st.write(f"Type: **{move_type}**")

                if move_type in TYPE_EFFECTIVENESS:

                    data = TYPE_EFFECTIVENESS[move_type]

                    if "good" in data:

                        st.success(
                            "✅ Super Effective Against: "
                            + ", ".join(data["good"])
                        )

                    if "bad" in data:

                        st.error(
                            "❌ Not Very Effective Against: "
                            + ", ".join(data["bad"])
                        )

                    if "immune" in data:

                        st.warning(
                            "🚫 No Effect Against: "
                            + ", ".join(data["immune"])
                        )

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📘 Features")

    st.write("✅ Live search")
    st.write("✅ No enter needed")
    st.write("✅ Click Pokémon instantly")
    st.write("✅ Results disappear after click")
    st.write("✅ Back button")

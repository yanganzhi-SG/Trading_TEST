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
# TYPE COLORS
# =========================================================

TYPE_COLORS = {
    "Normal": "#A8A77A",
    "Fire": "#EE8130",
    "Water": "#6390F0",
    "Electric": "#F7D02C",
    "Grass": "#7AC74C",
    "Ice": "#96D9D6",
    "Fighting": "#C22E28",
    "Poison": "#A33EA1",
    "Ground": "#E2BF65",
    "Flying": "#A98FF3",
    "Psychic": "#F95587",
    "Bug": "#A6B91A",
    "Rock": "#B6A136",
    "Ghost": "#735797",
    "Dragon": "#6F35FC",
    "Dark": "#705746",
    "Steel": "#B7B7CE",
    "Fairy": "#D685AD"
}

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    rankings = pd.read_csv("cp1500_all_overall_rankings.csv")
    fast_moves = pd.read_csv("fast_moves.csv")
    charged_moves = pd.read_csv("charged_moves.csv")

    rankings.columns = rankings.columns.str.strip()
    fast_moves.columns = fast_moves.columns.str.strip()
    charged_moves.columns = charged_moves.columns.str.strip()

    rankings["Pokemon"] = rankings["Pokemon"].astype(str).str.strip()

    fast_moves["Move"] = fast_moves["Move"].astype(str).str.strip()
    charged_moves["Move"] = charged_moves["Move"].astype(str).str.strip()

    return rankings, fast_moves, charged_moves


df, fast_moves_df, charged_moves_df = load_data()

pokemon_names = sorted(
    df["Pokemon"]
    .dropna()
    .unique()
    .tolist()
)

# =========================================================
# SEARCH BAR
# =========================================================

selected_pokemon = st.selectbox(
    "🔍 Search Pokémon",
    options=pokemon_names,
    index=None,
    placeholder="Type like: qu..."
)

# =========================================================
# TYPE BADGE
# =========================================================

def type_badge(type_name):

    color = TYPE_COLORS.get(type_name, "#777777")

    st.markdown(
        f"""
        <div style="
            background-color:{color};
            color:white;
            padding:8px;
            border-radius:10px;
            text-align:center;
            font-weight:bold;
            margin-bottom:8px;
        ">
            {type_name}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# MOVE DISPLAY
# =========================================================

def show_move(move_name):

    move_name = str(move_name).strip()

    move_data = fast_moves_df[
        fast_moves_df["Move"] == move_name
    ]

    if move_data.empty:

        move_data = charged_moves_df[
            charged_moves_df["Move"] == move_name
        ]

    if move_data.empty:

        st.warning(f"No move data found for {move_name}")
        return

    row = move_data.iloc[0]

    move_type = str(row.get("Type", "Unknown"))
    category = str(row.get("Category", "Unknown"))

    color = TYPE_COLORS.get(move_type, "#777777")

    with st.container(border=True):

        st.markdown(
            f"""
            <div style="
                background-color:{color};
                padding:12px;
                border-radius:12px;
                color:white;
            ">
                <h3>{move_name}</h3>
                <p><b>Type:</b> {move_type}</p>
                <p><b>Category:</b> {category}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            if pd.notna(row.get("Damage")):
                st.metric("Damage", row["Damage"])

            if pd.notna(row.get("Energy")):
                st.metric("Energy", row["Energy"])

        with col2:

            if pd.notna(row.get("Turns")):
                st.metric("Turns", row["Turns"])

            if pd.notna(row.get("DPT")):
                st.metric("DPT", row["DPT"])

        with col3:

            if pd.notna(row.get("EPT")):
                st.metric("EPT", row["EPT"])

            if pd.notna(row.get("DPE")):
                st.metric("DPE", row["DPE"])

# =========================================================
# SHOW POKEMON
# =========================================================

if selected_pokemon:

    pokemon_data = df[
        df["Pokemon"] == selected_pokemon
    ]

    if not pokemon_data.empty:

        row = pokemon_data.iloc[0]

        st.divider()

        st.header(f"⚔️ {selected_pokemon}")

        # =====================================================
        # TYPES + STATS
        # =====================================================

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("🧬 Types")

            type1 = str(row.get("Type 1", ""))

            if type1 != "nan" and type1 != "":
                type_badge(type1)

            type2 = str(row.get("Type 2", ""))

            if type2 != "nan" and type2 != "":
                type_badge(type2)

        with col2:

            st.subheader("📊 Stats")

            if "Attack" in row:
                st.metric("Attack", row["Attack"])

            if "Defense" in row:
                st.metric("Defense", row["Defense"])

            if "Stamina" in row:
                st.metric("HP", row["Stamina"])

            if "CP" in row:
                st.metric("CP", row["CP"])

        st.divider()

        # =====================================================
        # MOVES
        # =====================================================

        st.subheader("⚡ Fast Move")

        if "Fast Move" in row:
            show_move(row["Fast Move"])

        st.subheader("🔥 Charged Move 1")

        if "Charged Move 1" in row:
            show_move(row["Charged Move 1"])

        st.subheader("💥 Charged Move 2")

        if "Charged Move 2" in row:
            show_move(row["Charged Move 2"])

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📘 Features")

    st.write("✅ Real autocomplete search")
    st.write("✅ Type colored moves")
    st.write("✅ Move stats")
    st.write("✅ Fast + Charged attacks")
    st.write("✅ DPT / EPT / DPE")
    st.write("✅ Pokémon stats")

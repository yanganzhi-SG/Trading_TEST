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

    # CLEAN COLUMNS
    rankings.columns = rankings.columns.str.strip()
    fast_moves.columns = fast_moves.columns.str.strip()
    charged_moves.columns = charged_moves.columns.str.strip()

    # CLEAN STRINGS
    rankings["Pokemon"] = rankings["Pokemon"].astype(str).str.strip()

    fast_moves["Move"] = (
        fast_moves["Move"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    charged_moves["Move"] = (
        charged_moves["Move"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # CLEAN TYPES
    fast_moves["Type"] = (
        fast_moves["Type"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    charged_moves["Type"] = (
        charged_moves["Type"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    return rankings, fast_moves, charged_moves


df, fast_moves_df, charged_moves_df = load_data()

pokemon_names = sorted(
    df["Pokemon"]
    .dropna()
    .unique()
    .tolist()
)

# =========================================================
# SEARCH
# =========================================================

selected_pokemon = st.selectbox(
    "🔍 Search Pokémon",
    options=pokemon_names,
    index=None,
    placeholder="Type qu..."
)

# =========================================================
# TYPE BADGE
# =========================================================

def type_badge(type_name):

    type_name = str(type_name).title().strip()

    color = TYPE_COLORS.get(type_name, "#666666")

    st.markdown(
        f"""
        <div style="
            background-color:{color};
            color:white;
            padding:10px;
            border-radius:12px;
            font-weight:bold;
            text-align:center;
            margin-bottom:10px;
        ">
            {type_name}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# MOVE CARD
# =========================================================

def show_move(move_name):

    clean_move = str(move_name).strip().lower()

    # =====================================================
    # SEARCH BOTH FILES
    # =====================================================

    move_data = fast_moves_df[
        fast_moves_df["Move"] == clean_move
    ]

    if move_data.empty:

        move_data = charged_moves_df[
            charged_moves_df["Move"] == clean_move
        ]

    # =====================================================
    # NOT FOUND
    # =====================================================

    if move_data.empty:

        st.error(f"Move not found: {move_name}")
        return

    # =====================================================
    # GET FIRST MATCH
    # =====================================================

    row = move_data.iloc[0]

    move_type = str(row.get("Type", "Unknown")).title().strip()

    category = str(row.get("Category", "Unknown")).strip()

    color = TYPE_COLORS.get(move_type, "#666666")

    # =====================================================
    # CARD
    # =====================================================

    with st.container(border=True):

        st.markdown(
            f"""
            <div style="
                background-color:{color};
                padding:15px;
                border-radius:15px;
                color:white;
            ">
                <h2>{move_name}</h2>
                <h4>{move_type} • {category}</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

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

        # =====================================================
        # TYPES
        # =====================================================

        with col1:

            st.subheader("🧬 Types")

            type1 = str(row.get("Type 1", "")).title().strip()

            if type1 and type1 != "Nan":
                type_badge(type1)

            type2 = str(row.get("Type 2", "")).title().strip()

            if type2 and type2 != "Nan":
                type_badge(type2)

        # =====================================================
        # STATS
        # =====================================================

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
        # FAST MOVE
        # =====================================================

        st.subheader("⚡ Fast Move")

        if "Fast Move" in row:

            fast_move = str(row["Fast Move"]).strip()

            show_move(fast_move)

        # =====================================================
        # CHARGED MOVE 1
        # =====================================================

        st.subheader("🔥 Charged Move 1")

        if "Charged Move 1" in row:

            charged1 = str(row["Charged Move 1"]).strip()

            show_move(charged1)

        # =====================================================
        # CHARGED MOVE 2
        # =====================================================

        st.subheader("💥 Charged Move 2")

        if "Charged Move 2" in row:

            charged2 = str(row["Charged Move 2"]).strip()

            show_move(charged2)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📘 Features")

    st.write("✅ Fixed move searching")
    st.write("✅ Searches BOTH csv files")
    st.write("✅ Aqua Tail now works")
    st.write("✅ Correct type colors")
    st.write("✅ Styled move cards")
    st.write("✅ Live Pokémon search")

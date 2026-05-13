# =========================================================
# TYPE EFFECTIVENESS
# =========================================================

TYPE_EFFECTIVENESS = {
    "Normal": {
        "strong": [],
        "weak": ["Rock", "Steel"],
        "immune": ["Ghost"]
    },

    "Fire": {
        "strong": ["Grass", "Ice", "Bug", "Steel"],
        "weak": ["Fire", "Water", "Rock", "Dragon"],
        "immune": []
    },

    "Water": {
        "strong": ["Fire", "Ground", "Rock"],
        "weak": ["Water", "Grass", "Dragon"],
        "immune": []
    },

    "Electric": {
        "strong": ["Water", "Flying"],
        "weak": ["Electric", "Grass", "Dragon"],
        "immune": ["Ground"]
    },

    "Grass": {
        "strong": ["Water", "Ground", "Rock"],
        "weak": ["Fire", "Grass", "Poison", "Flying", "Bug", "Dragon", "Steel"],
        "immune": []
    },

    "Ice": {
        "strong": ["Grass", "Ground", "Flying", "Dragon"],
        "weak": ["Fire", "Water", "Ice", "Steel"],
        "immune": []
    },

    "Fighting": {
        "strong": ["Normal", "Ice", "Rock", "Dark", "Steel"],
        "weak": ["Poison", "Flying", "Psychic", "Bug", "Fairy"],
        "immune": ["Ghost"]
    },

    "Poison": {
        "strong": ["Grass", "Fairy"],
        "weak": ["Poison", "Ground", "Rock", "Ghost"],
        "immune": ["Steel"]
    },

    "Ground": {
        "strong": ["Fire", "Electric", "Poison", "Rock", "Steel"],
        "weak": ["Grass", "Bug"],
        "immune": ["Flying"]
    },

    "Flying": {
        "strong": ["Grass", "Fighting", "Bug"],
        "weak": ["Electric", "Rock", "Steel"],
        "immune": []
    },

    "Psychic": {
        "strong": ["Fighting", "Poison"],
        "weak": ["Psychic", "Steel"],
        "immune": ["Dark"]
    },

    "Bug": {
        "strong": ["Grass", "Psychic", "Dark"],
        "weak": ["Fire", "Fighting", "Poison", "Flying", "Ghost", "Steel", "Fairy"],
        "immune": []
    },

    "Rock": {
        "strong": ["Fire", "Ice", "Flying", "Bug"],
        "weak": ["Fighting", "Ground", "Steel"],
        "immune": []
    },

    "Ghost": {
        "strong": ["Psychic", "Ghost"],
        "weak": ["Dark"],
        "immune": ["Normal"]
    },

    "Dragon": {
        "strong": ["Dragon"],
        "weak": ["Steel"],
        "immune": ["Fairy"]
    },

    "Dark": {
        "strong": ["Psychic", "Ghost"],
        "weak": ["Fighting", "Dark", "Fairy"],
        "immune": []
    },

    "Steel": {
        "strong": ["Ice", "Rock", "Fairy"],
        "weak": ["Fire", "Water", "Electric", "Steel"],
        "immune": []
    },

    "Fairy": {
        "strong": ["Fighting", "Dragon", "Dark"],
        "weak": ["Fire", "Poison", "Steel"],
        "immune": []
    }
}

# =========================================================
# SHOW MOVE
# =========================================================

def show_move(move_name):

    original_move_name = str(move_name).strip()

    clean_move_name = clean_text(move_name)

    move_data = fast_moves_df[
        fast_moves_df["CleanMove"] == clean_move_name
    ]

    if move_data.empty:

        move_data = charged_moves_df[
            charged_moves_df["CleanMove"] == clean_move_name
        ]

    if move_data.empty:

        st.error(f"Move not found: {original_move_name}")
        return

    row = move_data.iloc[0]

    move_type = str(row.get("Type", "Unknown")).title().strip()

    category = str(row.get("Category", "Unknown")).strip()

    color = TYPE_COLORS.get(move_type, "#666666")

    effectiveness = TYPE_EFFECTIVENESS.get(move_type, {})

    strong_against = effectiveness.get("strong", [])
    weak_against = effectiveness.get("weak", [])
    immune_against = effectiveness.get("immune", [])

    # =====================================================
    # MOVE CARD
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
                <h2>{original_move_name}</h2>
                <h4>{move_type} • {category}</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        # =================================================
        # SUPER EFFECTIVE
        # =================================================

        st.subheader("✅ Super Effective Against")

        if strong_against:

            cols = st.columns(len(strong_against))

            for i, t in enumerate(strong_against):

                with cols[i]:

                    c = TYPE_COLORS.get(t, "#666666")

                    st.markdown(
                        f"""
                        <div style="
                            background-color:{c};
                            color:white;
                            padding:10px;
                            border-radius:10px;
                            text-align:center;
                            font-weight:bold;
                        ">
                            {t}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # =================================================
        # NOT VERY EFFECTIVE
        # =================================================

        st.subheader("❌ Not Very Effective Against")

        if weak_against:

            cols = st.columns(len(weak_against))

            for i, t in enumerate(weak_against):

                with cols[i]:

                    c = TYPE_COLORS.get(t, "#666666")

                    st.markdown(
                        f"""
                        <div style="
                            background-color:{c};
                            color:white;
                            padding:10px;
                            border-radius:10px;
                            text-align:center;
                            font-weight:bold;
                        ">
                            {t}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # =================================================
        # IMMUNE
        # =================================================

        if immune_against:

            st.subheader("🚫 No Effect Against")

            cols = st.columns(len(immune_against))

            for i, t in enumerate(immune_against):

                with cols[i]:

                    c = TYPE_COLORS.get(t, "#666666")

                    st.markdown(
                        f"""
                        <div style="
                            background-color:{c};
                            color:white;
                            padding:10px;
                            border-radius:10px;
                            text-align:center;
                            font-weight:bold;
                        ">
                            {t}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

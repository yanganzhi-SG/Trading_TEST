# main.py

import streamlit as st
import pandas as pd
import itertools

# =========================================================
# OPTIONAL GEMINI API KEYS
# =========================================================

api1 = "PUT_KEY_HERE"
api2 = "PUT_KEY_HERE"
api3 = "PUT_KEY_HERE"
api4 = "PUT_KEY_HERE"
api5 = "PUT_KEY_HERE"

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="GL Team Forge",
    layout="wide"
)

# =========================================================
# TYPE DATA
# =========================================================

TYPE_WEAKNESSES = {
    "Normal": ["Fighting"],
    "Fire": ["Water", "Ground", "Rock"],
    "Water": ["Electric", "Grass"],
    "Electric": ["Ground"],
    "Grass": ["Fire", "Ice", "Poison", "Flying", "Bug"],
    "Ice": ["Fire", "Fighting", "Rock", "Steel"],
    "Fighting": ["Flying", "Psychic", "Fairy"],
    "Poison": ["Ground", "Psychic"],
    "Ground": ["Water", "Grass", "Ice"],
    "Flying": ["Electric", "Ice", "Rock"],
    "Psychic": ["Bug", "Ghost", "Dark"],
    "Bug": ["Fire", "Flying", "Rock"],
    "Rock": ["Water", "Grass", "Fighting", "Ground", "Steel"],
    "Ghost": ["Ghost", "Dark"],
    "Dragon": ["Ice", "Dragon", "Fairy"],
    "Dark": ["Fighting", "Bug", "Fairy"],
    "Steel": ["Fire", "Fighting", "Ground"],
    "Fairy": ["Poison", "Steel"],
}

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
    "Fairy": "#D685AD",
}

# =========================================================
# SESSION STATE
# =========================================================

if "squad" not in st.session_state:
    st.session_state.squad = []

if "pokemon_df" not in st.session_state:
    st.session_state.pokemon_df = None

# =========================================================
# HELPERS
# =========================================================

def normalize_name(name):
    return str(name).strip().lower()


def get_weaknesses(pokemon):

    weaknesses = []

    t1 = str(pokemon.get("type1", "")).strip()
    t2 = str(pokemon.get("type2", "")).strip()

    if t1 in TYPE_WEAKNESSES:
        weaknesses.extend(TYPE_WEAKNESSES[t1])

    if t2 in TYPE_WEAKNESSES:
        weaknesses.extend(TYPE_WEAKNESSES[t2])

    return list(set(weaknesses))


def role_fit_lead(row):

    return (
        float(row["leadScore"]) * 0.6
        + float(row["consistencyScore"]) * 0.4
    )


def role_fit_switch(row):

    bulk = (
        float(row["consistencyScore"])
        + float(row["score"])
    ) / 2

    return (
        float(row["switchScore"]) * 0.7
        + bulk * 0.3
    )


def role_fit_closer(row):

    return (
        float(row["closerScore"]) * 0.8
        + float(row["attackerScore"]) * 0.2
    )


def best_role(row):

    lead = role_fit_lead(row)
    switch = role_fit_switch(row)
    closer = role_fit_closer(row)

    highest = max(lead, switch, closer)

    if highest == lead:
        return "🟡 Lead"

    if highest == switch:
        return "🟢 Safe Switch"

    return "🔴 Closer"


def duo_core_score(a, b):

    score = 60

    weak_a = set(get_weaknesses(a))
    weak_b = set(get_weaknesses(b))

    shared = weak_a.intersection(weak_b)

    score -= len(shared) * 10

    cover_bonus = len(
        weak_a.symmetric_difference(weak_b)
    ) * 3

    score += cover_bonus

    return round(max(0, min(100, score)), 1)


def trio_score(team):

    lead = role_fit_lead(team[0])
    switch = role_fit_switch(team[1])
    closer = role_fit_closer(team[2])

    role_score = (
        lead + switch + closer
    ) / 3

    unique_types = len(set([
        team[0]["type1"],
        team[1]["type1"],
        team[2]["type1"]
    ]))

    diversity_bonus = unique_types * 10

    consistency = (
        float(team[0]["consistencyScore"])
        + float(team[1]["consistencyScore"])
        + float(team[2]["consistencyScore"])
    ) / 3

    total = (
        role_score * 0.5
        + diversity_bonus * 0.2
        + consistency * 0.3
    )

    return round(min(total, 100), 1)


def line_structure(score):

    if score >= 82:
        return "⚡ Trio Core"

    if score >= 70:
        return "🔄 Duo Core + Pivot"

    return "💥 Carry Line"


def archetype(team):

    types = [
        team[0]["type1"],
        team[1]["type1"],
        team[2]["type1"]
    ]

    if len(set(types)) == 3:
        return "🔵 ABC"

    if types[1] == types[2]:
        return "🟠 ABB"

    if types[0] == types[2]:
        return "🟣 ABA"

    return "🔵 ABC"


def pokemon_card(pokemon):

    role = best_role(pokemon)

    weak = ", ".join(get_weaknesses(pokemon))

    t1 = pokemon.get("type1", "")
    t2 = pokemon.get("type2", "")

    c1 = TYPE_COLORS.get(t1, "#444")
    c2 = TYPE_COLORS.get(t2, "#444")

    st.markdown(
        f"""
        <div style="
            background:#111;
            padding:18px;
            border-radius:16px;
            border:1px solid #333;
            margin-bottom:12px;
        ">
            <h3>{pokemon['speciesName']}</h3>

            <span style="
                background:{c1};
                color:white;
                padding:6px 12px;
                border-radius:10px;
                font-size:14px;
            ">
                {t1}
            </span>

            <span style="
                background:{c2};
                color:white;
                padding:6px 12px;
                border-radius:10px;
                font-size:14px;
            ">
                {t2}
            </span>

            <br><br>

            <b>Overall Score:</b> {pokemon['score']}<br>
            <b>Role:</b> {role}<br>
            <b>Fast Move:</b> {pokemon['fastMove']}<br>
            <b>Charged Move 1:</b> {pokemon['chargedMove1']}<br>
            <b>Charged Move 2:</b> {pokemon['chargedMove2']}<br>
            <b>Weak To:</b> {weak}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# TITLE
# =========================================================

st.title("⚔️ GL Team Forge")
st.caption("Pokémon GO Great League Team Builder")

# =========================================================
# CSV UPLOAD
# =========================================================

uploaded = st.file_uploader(
    "Upload PvPoke CSV",
    type=["csv"]
)

if uploaded is not None:

    try:

        df = pd.read_csv(uploaded)

        # CLEAN COLUMN NAMES
        df.columns = df.columns.str.strip()

        # CLEAN TEXT FIELDS
        text_columns = [
            "speciesName",
            "type1",
            "type2",
            "fastMove",
            "chargedMove1",
            "chargedMove2"
        ]

        for col in text_columns:

            if col in df.columns:
                df[col] = df[col].astype(str).fillna("")

        # CLEAN NUMERIC FIELDS
        numeric_cols = [
            "score",
            "leadScore",
            "switchScore",
            "closerScore",
            "attackerScore",
            "consistencyScore"
        ]

        for col in numeric_cols:

            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                ).fillna(0)

        st.session_state.pokemon_df = df

        st.success(
            f"Loaded {len(df)} Pokémon from CSV"
        )

    except Exception as e:

        st.error(
            f"CSV Error: {e}"
        )

# =========================================================
# SEARCH SYSTEM
# =========================================================

if st.session_state.pokemon_df is not None:

    df = st.session_state.pokemon_df

    st.divider()

    st.subheader("🔍 Search Pokémon")

    search = st.text_input(
        "Search",
        placeholder="Type Pokémon name..."
    )

    existing_names = [
        normalize_name(p["speciesName"])
        for p in st.session_state.squad
    ]

    if search:

        search_lower = normalize_name(search)

        filtered = df[
            df["speciesName"]
            .str.lower()
            .str.contains(search_lower, na=False)
        ]

        filtered = filtered[
            ~filtered["speciesName"]
            .str.lower()
            .isin(existing_names)
        ]

        filtered = filtered.sort_values(
            by="score",
            ascending=False
        ).head(8)

        if len(filtered) == 0:

            st.warning(
                "No Pokémon found"
            )

        else:

            for idx, row in filtered.iterrows():

                col1, col2 = st.columns([6, 1])

                with col1:

                    st.markdown(
                        f"""
                        **{row['speciesName']}**
                        | {row['type1']} / {row['type2']}
                        | Score: {row['score']}
                        """
                    )

                with col2:

                    if st.button(
                        "Add",
                        key=f"add_{idx}"
                    ):

                        if len(st.session_state.squad) < 6:

                            st.session_state.squad.append(
                                row.to_dict()
                            )

                            st.rerun()

# =========================================================
# SQUAD DISPLAY
# =========================================================

if len(st.session_state.squad) > 0:

    st.divider()

    st.header(
        f"👥 Your Squad ({len(st.session_state.squad)}/6)"
    )

    if len(st.session_state.squad) >= 6:
        st.warning("Maximum squad size reached")

    for i, pokemon in enumerate(st.session_state.squad):

        col1, col2 = st.columns([12, 1])

        with col1:
            pokemon_card(pokemon)

        with col2:

            if st.button(
                "❌",
                key=f"remove_{i}"
            ):

                st.session_state.squad.pop(i)

                st.rerun()

# =========================================================
# ANALYSIS
# =========================================================

if len(st.session_state.squad) >= 3:

    st.divider()

    st.header("📊 Squad Analysis")

    squad = st.session_state.squad

    squad_df = pd.DataFrame(squad)

    avg_score = squad_df["score"].mean()

    unique_types = len(
        set(squad_df["type1"])
    )

    # =====================================================
    # DUO CORES
    # =====================================================

    duo_cores = []

    for a, b in itertools.combinations(squad, 2):

        score = duo_core_score(a, b)

        if score >= 65:

            duo_cores.append(
                (
                    a["speciesName"],
                    b["speciesName"],
                    score
                )
            )

    # =====================================================
    # SHARED WEAKNESSES
    # =====================================================

    weakness_count = {}

    for p in squad:

        weaknesses = get_weaknesses(p)

        for weak in weaknesses:

            weakness_count[weak] = (
                weakness_count.get(weak, 0) + 1
            )

    # =====================================================
    # SQUAD SCORE
    # =====================================================

    squad_score = (
        avg_score * 0.5
        + unique_types * 5
        + len(duo_cores) * 4
    )

    squad_score = round(
        min(squad_score, 100),
        1
    )

    # =====================================================
    # METRICS
    # =====================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Squad Score",
            squad_score
        )

    with col2:
        st.metric(
            "Strong Duo Cores",
            len(duo_cores)
        )

    with col3:
        st.metric(
            "Type Diversity",
            unique_types
        )

    # =====================================================
    # WARNINGS
    # =====================================================

    st.subheader("⚠️ Warnings")

    found_warning = False

    for weak, amount in weakness_count.items():

        if amount >= 3:

            found_warning = True

            st.error(
                f"🔴 {amount} Pokémon weak to {weak}"
            )

    if len(duo_cores) == 0:

        found_warning = True

        st.warning(
            "🟡 NO DUO CORES FOUND"
        )

    if not found_warning:

        st.success(
            "No major squad problems detected"
        )

    # =====================================================
    # DUO CORES
    # =====================================================

    st.subheader("🤝 Duo Cores")

    if len(duo_cores) > 0:

        for a, b, score in duo_cores:

            st.success(
                f"{a} + {b} — Core Score {score}"
            )

    else:

        st.info(
            "No strong duo cores found"
        )

    # =====================================================
    # BEST TEAMS
    # =====================================================

    st.divider()

    st.header("🏆 Best Teams")

    all_teams = list(
        itertools.combinations(
            squad,
            3
        )
    )

    scored_teams = []

    for trio in all_teams:

        trio = list(trio)

        # AUTO ROLE SORTING
        trio_sorted = sorted(
            trio,
            key=lambda x: role_fit_lead(x),
            reverse=True
        )

        score = trio_score(trio_sorted)

        scored_teams.append(
            (
                trio_sorted,
                score
            )
        )

    scored_teams = sorted(
        scored_teams,
        key=lambda x: x[1],
        reverse=True
    )

    best_team, best_score = scored_teams[0]

    st.metric(
        "Best Trio Score",
        best_score
    )

    st.markdown(
        f"### {line_structure(best_score)}"
    )

    st.markdown(
        f"### {archetype(best_team)}"
    )

    lead = best_team[0]
    switch = best_team[1]
    closer = best_team[2]

    col1, col2, col3 = st.columns(3)

    with col1:

        st.subheader("🟡 LEAD")
        pokemon_card(lead)

    with col2:

        st.subheader("🟢 SAFE SWITCH")
        pokemon_card(switch)

    with col3:

        st.subheader("🔴 CLOSER")
        pokemon_card(closer)

    # =====================================================
    # ALL POSSIBLE TEAMS
    # =====================================================

    st.divider()

    st.header("📋 All Possible Teams")

    for trio, score in scored_teams:

        names = (
            f"{trio[0]['speciesName']} / "
            f"{trio[1]['speciesName']} / "
            f"{trio[2]['speciesName']}"
        )

        st.markdown(
            f"""
            **{names}**
            — Team Score: {score}
            """
        )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "GL Team Forge • Streamlit Edition"
)

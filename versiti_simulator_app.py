import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Versiti Leadership Simulator", layout="wide")

st.title("Versiti Leadership Simulation - Team Scoring")

# Session state to store teams and phase
if "teams" not in st.session_state:
    st.session_state.teams = {}
if "phase" not in st.session_state:
    st.session_state.phase = 1
if "custom_scoring" not in st.session_state:
    st.session_state.custom_scoring = {}

# --- Scoring model ---
def get_score(key, option):
    custom = st.session_state.custom_scoring
    if key in custom and option in custom[key]:
        return custom[key][option]
    return scoring_summary.get(key, {}).get(option, (0, 0, 0))

scoring_summary = {
    "Y1 D1": {
        "A": (-1, 0, 1), "B1": (-2, 1, 1), "B2": (-3, 2, 1), "B3": (-1, 2, 1),
        "C": (-1, 0, -2), "D": (0, 0, -1)
    },
    "Y1 D1 Delay Y2": {
        "A": (-2, 1, 1), "B3": (1, 1, 1)
    },
    "Y1 D1 Delay Y3": {
        "A": (5, 3, 1), "B3": (3, 3, 1)
    },
    "Y1 D2": {"A": (-2, -1, -3), "B": (-1, 0, -1), "C": (0, 0, 0)},
    "Y1 D3": {"A": (0, -2, 0), "B": (0, 1, 1), "C": (2, -1, -2)},
    "Y1 D4": {"Yes": (-4, 0, 0), "No": (0, 0, 0)},

    "Y2 D1": {"A": (-3, 4, 2), "B": (1, 1, 2)},
    "Y2 D2": {"A": (-2, 1, 0), "B": (1, 0, 1)},
    "Y2 D3": {"A": (-5, -1, -2), "B": (-2, -3, -3), "C": (-2, -3, -3)},
    "Y2 D4": {
        "A": (-5, -1, -2), "B": (-2, -3, -3), "C": (0, -1, -1),
        "D": (-4, 4, 0), "E": (-2, 3, -1)
    },
    "Y2 D5": {"A": (3, 1, 1), "B": (0, 0, 0)},

    "Y3 D1": {"A": (-3, -1, -3), "B": (0, -2, -1)},
    "Y3 D2": {
        "A Big Win": (15, 7, 3),
        "A Small Win": (2, 2, 0),
        "B": (1, 0, -2)
    },
    "Y3 D3": {
        "A": (10, 7, 3),
        "B": (1, 0, -2),
        "C": (-4, 3, 2),
        "D": (1, 3, -1)
    }
}

# --- Admin Controls ---
st.sidebar.title("Simulation Phase")
phase = st.sidebar.radio("Select Simulation Phase", [1, 2, 3])
st.session_state.phase = phase
show_admin = st.sidebar.checkbox("Enable Admin Scoring Editor")

if show_admin:
    st.sidebar.title("Scoring Editor")
    confirm_reset = st.sidebar.checkbox("I am sure I want to reset to default scoring")
    if st.sidebar.button("Reset to Default Scoring") and confirm_reset:
        st.session_state.custom_scoring = {}
        st.experimental_rerun()

    for decision, options in scoring_summary.items():
        st.sidebar.markdown(f"### {decision}")
        if decision not in st.session_state.custom_scoring:
            st.session_state.custom_scoring[decision] = {}
        for opt, (f, r, c) in options.items():
            col1, col2, col3 = st.sidebar.columns(3)
            new_f = col1.number_input(f"{opt} - Fin", value=f, key=f"{decision}_{opt}_f")
            new_r = col2.number_input(f"{opt} - Rep", value=r, key=f"{decision}_{opt}_r")
            new_c = col3.number_input(f"{opt} - Cul", value=c, key=f"{decision}_{opt}_c")
            st.session_state.custom_scoring[decision][opt] = (new_f, new_r, new_c)

# --- Input and Scoring Interface ---
st.subheader(f"Enter Team Decisions - Year {phase}")
with st.form("team_form"):
    team_name = st.text_input("Team Name")
    if team_name:
        if team_name not in st.session_state.teams:
            st.session_state.teams[team_name] = {
                "Team": team_name,
                "Y1 Fin": 0, "Y1 Rep": 0, "Y1 Cul": 0,
                "Y2 Fin": 0, "Y2 Rep": 0, "Y2 Cul": 0,
                "Y3 Fin": 0, "Y3 Rep": 0, "Y3 Cul": 0
            }

    team = st.session_state.teams.get(team_name, {})
    decisions = {}

    if phase == 1:
        y1_d1 = st.selectbox("Y1 D1", list(scoring_summary["Y1 D1"].keys()))
        y1_d2 = st.selectbox("Y1 D2", list(scoring_summary["Y1 D2"].keys()))
        y1_d3 = st.selectbox("Y1 D3", list(scoring_summary["Y1 D3"].keys()))
        y1_d4 = st.selectbox("Y1 D4", list(scoring_summary["Y1 D4"].keys()))
        y1_bonus = ""
        if y1_d4 == "Yes":
            remaining = [opt for opt in scoring_summary["Y1 D1"].keys() if opt != y1_d1]
            y1_bonus = st.selectbox("Y1 D1 Bonus (Debt)", remaining)

        decisions = {
            "Y1 D1": y1_d1,
            "Y1 D2": y1_d2,
            "Y1 D3": y1_d3,
            "Y1 D4": y1_d4
        }
        if y1_bonus:
            decisions["Y1 D1 Bonus"] = y1_bonus

    elif phase == 2:
        decisions = {
            "Y2 D1": st.selectbox("Y2 D1", ["None"] + list(scoring_summary["Y2 D1"].keys())),
            "Y2 D2": st.selectbox("Y2 D2", ["None"] + list(scoring_summary["Y2 D2"].keys())),
            "Y2 D3": st.selectbox("Y2 D3", ["None"] + list(scoring_summary["Y2 D3"].keys())),
            "Y2 D4": st.selectbox("Y2 D4", list(scoring_summary["Y2 D4"].keys())),
            "Y2 D5": st.selectbox("Y2 D5", list(scoring_summary["Y2 D5"].keys()))
        }

    elif phase == 3:
        decisions = {
            "Y3 D1": st.selectbox("Y3 D1", ["None"] + list(scoring_summary["Y3 D1"].keys())),
            "Y3 D2": st.selectbox("Y3 D2", ["None"] + list(scoring_summary["Y3 D2"].keys())),
            "Y3 D3": st.selectbox("Y3 D3", list(scoring_summary["Y3 D3"].keys()))
        }

    submitted = st.form_submit_button("Submit")

if submitted and team_name:
    ykey = f"Y{phase}"
    team = st.session_state.teams[team_name]
    for cat in ["Fin", "Rep", "Cul"]:
        team[f"{ykey} {cat}"] = 0

    for d, opt in decisions.items():
        if opt and opt != "None":
            f, r, c = get_score(d, opt)
            team[f"{ykey} Fin"] += f
            team[f"{ykey} Rep"] += r
            team[f"{ykey} Cul"] += c

    if phase == 2:
        for delayed_key in ["Y1 D1", "Y1 D1 Bonus"]:
            opt = st.session_state.teams[team_name].get(delayed_key)
            if opt in scoring_summary.get("Y1 D1 Delay Y2", {}):
                f, r, c = get_score("Y1 D1 Delay Y2", opt)
                team[f"{ykey} Fin"] += f
                team[f"{ykey} Rep"] += r
                team[f"{ykey} Cul"] += c

    if phase == 3:
        for delayed_key in ["Y1 D1", "Y1 D1 Bonus"]:
            opt = st.session_state.teams[team_name].get(delayed_key)
            if opt in scoring_summary.get("Y1 D1 Delay Y3", {}):
                f, r, c = get_score("Y1 D1 Delay Y3", opt)
                team[f"{ykey} Fin"] += f
                team[f"{ykey} Rep"] += r
                team[f"{ykey} Cul"] += c

    st.session_state.teams[team_name] = team

# --- Leaderboard ---
if st.session_state.teams:
    st.subheader(f"Leaderboard After Year {phase}")
    df = pd.DataFrame(st.session_state.teams.values())
    df["Total Fin"] = df[["Y1 Fin", "Y2 Fin", "Y3 Fin"]].sum(axis=1)
    df["Total Rep"] = df[["Y1 Rep", "Y2 Rep", "Y3 Rep"]].sum(axis=1)
    df["Total Cul"] = df[["Y1 Cul", "Y2 Cul", "Y3 Cul"]].sum(axis=1)
    df["Total Score"] = df[["Total Fin", "Total Rep", "Total Cul"]].sum(axis=1)
    st.dataframe(df.sort_values("Total Score", ascending=False), use_container_width=True)

    if st.button("Reset All Teams"):
        st.session_state.teams = {}

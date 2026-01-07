import streamlit as st
from src.tarka_core import get_compute_options, score_options

st.set_page_config(page_title="Tarka — Cloud Compute Referee", layout="centered")

st.title("Tarka — Cloud Compute Referee")
st.caption("Compare AWS compute options by understanding trade-offs")

traffic = st.selectbox(
    "Traffic pattern",
    ["bursty", "steady"],
    format_func=lambda x: "Bursty / unpredictable" if x == "bursty" else "Steady / predictable"
)

control = st.selectbox(
    "Infrastructure control required",
    ["low", "medium", "high"],
    format_func=lambda x: x.capitalize()
)

cost = st.selectbox(
    "Cost sensitivity",
    ["sensitive", "flexible"],
    format_func=lambda x: "Very sensitive" if x == "sensitive" else "Flexible"
)

if st.button("Compare options"):
    options = get_compute_options()
    ranked = score_options(options, traffic, control, cost)

    for opt in ranked:
        st.subheader(opt.name)
        st.write(f"**Best for:** {opt.best_for}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Pros**")
            for p in opt.pros:
                st.markdown(f"- {p}")
        with col2:
            st.markdown("**Cons**")
            for c in opt.cons:
                st.markdown(f"- {c}")

        st.divider()
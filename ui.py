"""
Tarka — Cloud Compute Referee
Streamlit UI with polished UX, mobile support, and submission-safe features.
"""

import streamlit as st
import json
from datetime import datetime
from src.tarka_core import (
    get_compute_options, score_options, get_score_rationale,
    evaluate, get_confidence, get_what_would_change, get_assumptions
)

# Page configuration
st.set_page_config(
    page_title="Tarka — Cloud Compute Referee",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'traffic': "bursty",
        'control': "low",
        'cost': "sensitive",
        'results': None,
        'view_mode': "card",
        'compare_mode': False,
        'advanced_mode': False,
        'simple_mode': True,
        'theme': "light",
        'weights': {"traffic": 1.0, "control": 1.0, "cost": 1.0},
        'scenario_b': {"traffic": "steady", "control": "medium", "cost": "flexible"},
        'max_exec_time': "not sure",
        'compliance': "low",
        'cold_start_tolerance': True,
        'bias_override': None,
        'deterministic_mode': True,
        'arch_review_mode': False,
        'sensitivity_weights': {"cost": 1.0, "ops": 1.0, "control": 1.0},
        'reflection_mode': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================================================
# CSS AND THEMING
# ============================================================================

def apply_base_css(theme):
    """
    Apply base CSS with theme support.
    Ensures strong contrast for mobile readability.
    """
    if theme == "dark":
        bg_color = "#0e1117"
        card_bg = "#1e2130"
        text_color = "#ffffff"  # Full opacity for mobile
        border_color = "#3d4451"
        highlight_bg = "#2a2d3a"
        primary_color = "#ff4b4b"
        secondary_color = "#00d4aa"
        accent_color = "#6366f1"
    else:  # light
        bg_color = "#ffffff"
        card_bg = "#f8f9fa"
        text_color = "#1a1a1a"  # Strong contrast, no opacity
        border_color = "#d0d0d0"
        highlight_bg = "#e8f4f8"
        primary_color = "#ff4b4b"
        secondary_color = "#00d4aa"
        accent_color = "#6366f1"
    
    css = f"""
    <style>
    /* Hide Streamlit chrome */
    #MainMenu {{ visibility: hidden; }}
    header {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    [data-testid="stToolbar"] {{ display: none; }}
    [data-testid="stHeader"] {{ display: none; }}
    [data-testid="stDecoration"] {{ display: none; }}
    [data-testid="stStatusWidget"] {{ display: none; }}
    .stDeployButton {{ display: none; }}
    
    /* Base theme variables */
    :root {{
        --bg-color: {bg_color};
        --card-bg: {card_bg};
        --text-color: {text_color};
        --border-color: {border_color};
        --primary-color: {primary_color};
        --secondary-color: {secondary_color};
        --accent-color: {accent_color};
        --highlight-bg: {highlight_bg};
    }}
    
    /* Ensure strong text contrast - no opacity tricks */
    .stApp {{
        background-color: var(--bg-color);
    }}
    
    /* Explicit text colors for all elements */
    p, li, label, span, div, h1, h2, h3, h4, h5, h6 {{
        color: var(--text-color) !important;
    }}
    
    /* Hero header */
    .hero-header {{
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: var(--text-color) !important;
    }}
    
    .hero-subtitle {{
        text-align: center;
        color: var(--text-color);
        font-size: 1.1rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }}
    
    .offline-badge {{
        display: inline-block;
        background: var(--secondary-color);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }}
    
    /* Cards */
    .summary-card {{
        background-color: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    
    .option-card {{
        background-color: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    .best-fit-card {{
        background-color: var(--highlight-bg);
        border: 3px solid var(--secondary-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 6px 12px rgba(0, 212, 170, 0.3);
    }}
    
    /* Badges */
    .rank-badge {{
        display: inline-block;
        background: var(--primary-color);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }}
    
    .score-badge {{
        display: inline-block;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 0.5rem 1.2rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1rem;
    }}
    
    .confidence-badge {{
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        margin: 0.5rem 0;
        color: white;
    }}
    
    .confidence-high {{ background-color: #00d4aa; }}
    .confidence-medium {{ background-color: #ffa500; }}
    .confidence-low {{ background-color: #ff6b6b; }}
    
    .preference-badge {{
        display: inline-block;
        background: var(--accent-color);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }}
    
    /* Mobile responsiveness */
    @media (max-width: 600px) {{
        .hero-header {{
            font-size: 1.8rem;
            padding: 1rem 0.5rem;
        }}
        
        .summary-card, .option-card, .best-fit-card {{
            padding: 1rem;
            margin: 0.5rem 0;
        }}
        
        [class*="stButton"] {{
            width: 100% !important;
        }}
    }}
    
    /* Mobile sidebar hint */
    .mobile-hint {{
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.75rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: var(--text-color);
        text-align: center;
    }}
    
    /* Footer */
    .footer-text {{
        text-align: center;
        padding: 1rem;
        color: var(--text-color);
        font-size: 0.85rem;
        border-top: 1px solid var(--border-color);
        margin-top: 2rem;
    }}
    
    /* Ensure all Streamlit elements have proper colors */
    .stSelectbox label, .stSlider label, .stRadio label {{
        color: var(--text-color) !important;
    }}
    
    /* Progress bars */
    .score-meter {{
        height: 8px;
        background: var(--border-color);
        border-radius: 4px;
        overflow: hidden;
        margin-top: 0.5rem;
    }}
    
    .score-fill {{
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        border-radius: 4px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Apply CSS based on current theme
apply_base_css(st.session_state.theme)

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

def render_sidebar_controls():
    """Render all sidebar controls."""
    st.sidebar.title("⚙️ Controls")
    
    # Theme toggle
    theme_options = ["Light", "Dark"]
    theme_idx = 0 if st.session_state.theme == "light" else 1
    theme_choice = st.sidebar.radio("Theme", theme_options, index=theme_idx)
    st.session_state.theme = "light" if theme_choice == "Light" else "dark"
    if theme_choice != theme_options[theme_idx]:
        apply_base_css(st.session_state.theme)
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # App mode
    app_mode = st.sidebar.radio(
        "App Mode",
        ["Simple", "Advanced"],
        index=0 if st.session_state.simple_mode else 1
    )
    st.session_state.simple_mode = (app_mode == "Simple")
    st.session_state.advanced_mode = (app_mode == "Advanced")
    
    st.sidebar.markdown("---")
    
    # Scenario Presets (quick buttons)
    st.sidebar.markdown("### 🎯 Quick Presets")
    presets = {
        "Startup MVP": {"traffic": "bursty", "control": "low", "cost": "sensitive"},
        "High-traffic API": {"traffic": "steady", "control": "medium", "cost": "flexible"},
        "Batch processing": {"traffic": "steady", "control": "medium", "cost": "sensitive"},
        "Legacy migration": {"traffic": "steady", "control": "high", "cost": "flexible"}
    }
    
    for name, values in presets.items():
        if st.sidebar.button(name, use_container_width=True, key=f"preset_{name}"):
            st.session_state.traffic = values["traffic"]
            st.session_state.control = values["control"]
            st.session_state.cost = values["cost"]
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Main inputs (always in sidebar for mobile)
    st.sidebar.markdown("### 📊 Requirements")
    
    traffic = st.sidebar.selectbox(
        "🚦 Traffic pattern",
        ["bursty", "steady"],
        index=0 if st.session_state.traffic == "bursty" else 1,
        format_func=lambda x: "Bursty / unpredictable" if x == "bursty" else "Steady / predictable"
    )
    
    control = st.sidebar.selectbox(
        "⚙️ Infrastructure control",
        ["low", "medium", "high"],
        index=["low", "medium", "high"].index(st.session_state.control),
        format_func=lambda x: x.capitalize()
    )
    
    cost = st.sidebar.selectbox(
        "💰 Cost sensitivity",
        ["sensitive", "flexible"],
        index=0 if st.session_state.cost == "sensitive" else 1,
        format_func=lambda x: "Very sensitive" if x == "sensitive" else "Flexible"
    )
    
    st.session_state.traffic = traffic
    st.session_state.control = control
    st.session_state.cost = cost
    
    # Hard Constraints (Feature 1)
    with st.sidebar.expander("🔒 Hard Constraints"):
        max_exec_time = st.selectbox(
            "Max execution time",
            ["seconds", "minutes", "hours", "not sure"],
            index=["seconds", "minutes", "hours", "not sure"].index(st.session_state.max_exec_time)
        )
        compliance = st.selectbox(
            "Compliance sensitivity",
            ["low", "medium", "high"],
            index=["low", "medium", "high"].index(st.session_state.compliance)
        )
        cold_start = st.checkbox(
            "Cold start tolerance",
            value=st.session_state.cold_start_tolerance
        )
        st.session_state.max_exec_time = max_exec_time
        st.session_state.compliance = compliance
        st.session_state.cold_start_tolerance = cold_start
    
    # Bias Override (Feature 3)
    with st.sidebar.expander("🎯 Preference Override"):
        bias_options = ["None", "Serverless", "Containers", "Full Control"]
        bias_idx = 0
        if st.session_state.bias_override == "serverless":
            bias_idx = 1
        elif st.session_state.bias_override == "containers":
            bias_idx = 2
        elif st.session_state.bias_override == "control":
            bias_idx = 3
        
        bias_choice = st.radio("I prefer", bias_options, index=bias_idx)
        if bias_choice == "None":
            st.session_state.bias_override = None
        elif bias_choice == "Serverless":
            st.session_state.bias_override = "serverless"
        elif bias_choice == "Containers":
            st.session_state.bias_override = "containers"
        else:
            st.session_state.bias_override = "control"
    
    # Advanced mode features
    if st.session_state.advanced_mode:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚖️ Advanced")
        
        # Weighted inputs (if supported)
        st.sidebar.markdown("**Input Weights**")
        weight_traffic = st.sidebar.slider("Traffic", 0.0, 3.0, st.session_state.weights["traffic"], 0.1)
        weight_control = st.sidebar.slider("Control", 0.0, 3.0, st.session_state.weights["control"], 0.1)
        weight_cost = st.sidebar.slider("Cost", 0.0, 3.0, st.session_state.weights["cost"], 0.1)
        st.session_state.weights = {
            "traffic": weight_traffic,
            "control": weight_control,
            "cost": weight_cost
        }
        
        # Sensitivity Visualization (Feature 7)
        with st.sidebar.expander("📊 Sensitivity (Visualization)"):
            st.caption("What-if visualization; does not change ranking")
            sens_cost = st.slider("Cost emphasis", 0.0, 3.0, st.session_state.sensitivity_weights["cost"], 0.1)
            sens_ops = st.slider("Ops emphasis", 0.0, 3.0, st.session_state.sensitivity_weights["ops"], 0.1)
            sens_control = st.slider("Control emphasis", 0.0, 3.0, st.session_state.sensitivity_weights["control"], 0.1)
            st.session_state.sensitivity_weights = {
                "cost": sens_cost,
                "ops": sens_ops,
                "control": sens_control
            }
        
        # Reflection Mode (Feature 15)
        reflection = st.sidebar.checkbox("Reflection Mode", value=st.session_state.reflection_mode)
        st.session_state.reflection_mode = reflection
    
    # Deterministic Mode (Feature 9)
    st.sidebar.markdown("---")
    deterministic = st.sidebar.checkbox("Deterministic output", value=st.session_state.deterministic_mode)
    st.session_state.deterministic_mode = deterministic
    
    # Architecture Review Mode (Feature 10)
    arch_review = st.sidebar.checkbox("Architecture review language", value=st.session_state.arch_review_mode)
    st.session_state.arch_review_mode = arch_review
    
    # Reset button
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Reset Inputs", use_container_width=True):
        st.session_state.traffic = "bursty"
        st.session_state.control = "low"
        st.session_state.cost = "sensitive"
        st.session_state.results = None
        st.session_state.weights = {"traffic": 1.0, "control": 1.0, "cost": 1.0}
        st.rerun()
    
    # About (Feature 13)
    with st.sidebar.expander("ℹ️ About"):
        st.markdown("""
        **Decision-support tool** — not a recommendation engine.
        
        Highlights trade-offs between AWS compute options to support informed decision-making.
        
        **No single 'best' answer** — use trade-offs to decide.
        """)
    
    # Help (Feature 16)
    with st.sidebar.expander("❓ Help"):
        st.markdown("""
        **Run locally:**
        ```bash
        streamlit run ui.py
        ```
        
        **On phone (Network URL):**
        1. Find your computer's IP: `ifconfig` (Mac/Linux) or `ipconfig` (Windows)
        2. Run: `streamlit run ui.py --server.address 0.0.0.0`
        3. Open: `http://YOUR_IP:8501` on your phone
        
        **Offline & Deterministic:**
        - No external APIs
        - No cloud calls
        - All logic runs locally
        """)
    
    # Glossary (Feature 5)
    with st.sidebar.expander("📖 Glossary"):
        st.markdown("""
        **Cold start:** Initial delay when a function/container starts from idle state.
        
        **Ops overhead:** Operational tasks like patching, monitoring, scaling.
        
        **Infrastructure control:** Level of control over underlying infrastructure (networking, storage, OS).
        
        **Burst traffic:** Unpredictable spikes in usage.
        
        **Steady traffic:** Predictable, consistent usage patterns.
        """)
    
    return traffic, control, cost

# ============================================================================
# MAIN PAGE RENDERING
# ============================================================================

def render_hero():
    """Render hero header section."""
    st.markdown('<div class="hero-header">Tarka — Cloud Compute Referee</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Compare AWS compute options by understanding trade-offs</div>', unsafe_allow_html=True)
    
    # Offline badge (Feature 14)
    st.markdown('<div class="offline-badge">Offline • Deterministic • No external APIs</div>', unsafe_allow_html=True)
    
    # Mobile hint (Feature 16)
    st.markdown("""
    <div class="mobile-hint">
        ☰ Use the sidebar to adjust inputs. Tap the arrow to collapse.
    </div>
    """, unsafe_allow_html=True)

def render_results(ranked, details, traffic, control, cost):
    """Render results section with all features."""
    if not ranked:
        return
    
    # Input summary
    st.markdown("### 📋 Input Summary")
    st.markdown(f"""
    <div class="summary-card">
        <strong>Traffic:</strong> {traffic.capitalize()}<br>
        <strong>Control:</strong> {control.capitalize()}<br>
        <strong>Cost:</strong> {cost.capitalize()}
    </div>
    """, unsafe_allow_html=True)
    
    # Confidence indicator
    conf_level, conf_msg = get_confidence(ranked)
    conf_class = f"confidence-{conf_level.lower()}"
    st.markdown(f'<div class="confidence-badge {conf_class}">Confidence: {conf_level.upper()}</div>', unsafe_allow_html=True)
    st.caption(conf_msg)
    
    # Deterministic mode display (Feature 9)
    if st.session_state.deterministic_mode:
        with st.expander("🔍 Deterministic Output Details"):
            st.markdown("**Inputs used:**")
            st.code(f"Traffic: {traffic}, Control: {control}, Cost: {cost}")
            st.markdown("**Raw scores:**")
            for opt in ranked:
                st.code(f"{opt.name}: {opt.score}")
            st.markdown("**Note:** No randomness; no external calls.")
    
    # Ranked options
    st.markdown("### 🎯 Ranked Options")
    
    max_score = max(opt.score for opt in ranked) if ranked else 1
    
    for idx, opt in enumerate(ranked):
        is_best_fit = idx == 0
        card_class = "best-fit-card" if is_best_fit else "option-card"
        
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        # Rank badge
        st.markdown(f'<span class="rank-badge">#{idx + 1}</span>', unsafe_allow_html=True)
        
        # Preference badge (Feature 3)
        if st.session_state.bias_override:
            if (st.session_state.bias_override == "serverless" and opt.name == "AWS Lambda") or \
               (st.session_state.bias_override == "containers" and "ECS" in opt.name) or \
               (st.session_state.bias_override == "control" and opt.name == "AWS EC2"):
                st.markdown('<span class="preference-badge">Preference Match</span>', unsafe_allow_html=True)
        
        col_title, col_score = st.columns([3, 1])
        with col_title:
            st.markdown(f"#### {opt.name}")
        with col_score:
            st.markdown(f'<div class="score-badge">Score: {opt.score}</div>', unsafe_allow_html=True)
            score_pct = (opt.score / max_score * 100) if max_score > 0 else 0
            st.markdown(f"""
            <div class="score-meter">
                <div class="score-fill" style="width: {score_pct}%"></div>
            </div>
            """, unsafe_allow_html=True)
        
        # Use when / Recommended for (Feature 10)
        if st.session_state.arch_review_mode:
            st.markdown(f"**Recommended for:** {opt.best_for}")
        else:
            st.markdown(f"**Use when:** {opt.best_for}")
        
        # Explainability timeline (Feature 8)
        with st.expander("📊 Explainability Timeline"):
            factors = ["traffic", "control", "cost"]
            for factor in factors:
                contrib = details["contributions"][opt.name][factor]
                reason = details["reasons"][opt.name][factor]
                if contrib > 0:
                    st.markdown(f"**{factor.capitalize()}**: {reason}")
                    st.markdown(f"  → Contribution: +{contrib:.1f}")
                else:
                    st.markdown(f"**{factor.capitalize()}**: No contribution")
        
        # Pros / Cons
        col_pros, col_cons = st.columns(2)
        with col_pros:
            st.markdown("**✅ Pros**")
            for p in opt.pros:
                st.markdown(f"• {p}")
        with col_cons:
            if st.session_state.arch_review_mode:
                st.markdown("**⚠️ Key Risks**")
            else:
                st.markdown("**❌ Cons**")
            for c in opt.cons:
                st.markdown(f"• {c}")
        
        # Watch outs
        if st.session_state.arch_review_mode:
            st.markdown("**⚠️ Open Questions**")
        else:
            st.markdown("**⚠️ Watch out for**")
        for c in opt.cons:
            st.markdown(f"  • {c}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Eliminated Options (Feature 2)
    if len(ranked) > 0:
        eliminated = []
        top_score = ranked[0].score
        for opt in ranked[1:]:
            if top_score - opt.score >= 2:  # Threshold-based
                eliminated.append(opt)
        
        if eliminated:
            st.markdown("### ⚠️ Eliminated / Risky Options")
            for opt in eliminated:
                st.markdown(f"**{opt.name}** — Score gap indicates less alignment with current constraints.")
    
    # What You're Trading Away (Feature 4)
    if ranked:
        top_opt = ranked[0]
        st.markdown("### 🔄 What You're Trading Away")
        gains = ", ".join(top_opt.pros[:2])
        trades = ", ".join(top_opt.cons[:2])
        st.markdown(f"**You gain:** {gains}")
        st.markdown(f"**You trade away:** {trades}")
    
    # Hard Constraints Warnings (Feature 1)
    warnings = []
    if st.session_state.max_exec_time in ["seconds", "minutes"]:
        warnings.append("Lambda has execution time limits; review max duration requirements.")
    if st.session_state.compliance == "high":
        warnings.append("High compliance needs may require additional AWS services beyond compute.")
    if not st.session_state.cold_start_tolerance:
        warnings.append("Cold start sensitivity may favor ECS/Fargate or EC2 over Lambda.")
    
    if warnings:
        st.markdown("### ⚠️ Open Questions")
        for warning in warnings:
            st.markdown(f"• {warning}")
    
    # What Would Change (existing feature)
    suggestions = get_what_would_change(ranked[0].name, traffic, control, cost)
    st.markdown("### 🔄 What Would Change This Decision?")
    for suggestion in suggestions:
        st.markdown(f"• {suggestion}")
    
    # Reflection Mode (Feature 15)
    if st.session_state.reflection_mode and ranked:
        st.markdown("### 💭 Reflection")
        top_opt = ranked[0]
        st.markdown(f"If I were building this system, I'd start with **{top_opt.name}** when constraints look like {traffic} traffic, {control} control needs, and {cost} cost sensitivity. This aligns with '{top_opt.best_for}'.")
    
    # Sensitivity Visualization (Feature 7)
    if st.session_state.advanced_mode:
        st.markdown("### 📊 Sensitivity Visualization")
        st.caption("What-if emphasis values (does not change ranking)")
        sens = st.session_state.sensitivity_weights
        st.progress(sens["cost"] / 3.0, text=f"Cost: {sens['cost']:.1f}")
        st.progress(sens["ops"] / 3.0, text=f"Ops: {sens['ops']:.1f}")
        st.progress(sens["control"] / 3.0, text=f"Control: {sens['control']:.1f}")
    
    # Shareable Summary (Feature 11)
    st.markdown("---")
    st.markdown("### 📋 Shareable Decision Summary")
    summary_text = f"""Inputs: Traffic={traffic}, Control={control}, Cost={cost}

Ranked Options:
"""
    for idx, opt in enumerate(ranked):
        summary_text += f"{idx+1}. {opt.name} (Score: {opt.score}) - {opt.best_for}\n"
    
    summary_text += f"""
Trade-off Summary:
Top choice: {ranked[0].name}
Gains: {', '.join(ranked[0].pros[:2])}
Trade-offs: {', '.join(ranked[0].cons[:2])}

Disclaimer: This is not a single best answer; use trade-offs to decide.
"""
    
    st.text_area("Copy this summary", value=summary_text, height=200, key="summary_text")
    
    # Downloads
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "inputs": {"traffic": traffic, "control": control, "cost": cost},
            "confidence": {"level": conf_level, "message": conf_msg},
            "results": [
                {
                    "rank": idx + 1,
                    "name": opt.name,
                    "score": opt.score,
                    "use_when": opt.best_for,
                    "pros": opt.pros,
                    "cons": opt.cons
                }
                for idx, opt in enumerate(ranked)
            ],
            "disclaimer": "This is not a single best answer; use trade-offs to decide."
        }
        json_str = json.dumps(snapshot, indent=2)
        st.download_button(
            "💾 Download JSON",
            data=json_str,
            file_name=f"tarka_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col_dl2:
        md_content = f"""# Tarka Decision Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Input Summary
- Traffic: {traffic}
- Control: {control}
- Cost: {cost}

## Results
"""
        for idx, opt in enumerate(ranked):
            md_content += f"""
### {idx+1}. {opt.name}
Score: {opt.score}
Use when: {opt.best_for}
Pros: {', '.join(opt.pros)}
Cons: {', '.join(opt.cons)}
"""
        md_content += "\n## Disclaimer\nThis is not a single best answer; use trade-offs to decide.\n"
        
        st.download_button(
            "📄 Download Markdown",
            data=md_content,
            file_name=f"tarka_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    # Footer (Feature 12)
    st.markdown('<div class="footer-text">Decision logic: v1 (deterministic, local)</div>', unsafe_allow_html=True)
    
    # Why no single best answer (Feature 13)
    with st.expander("🤔 Why no single 'best' answer?"):
        st.markdown("""
        This tool supports **reasoning** rather than automation.
        
        Different teams have different constraints, risk tolerance, and operational capabilities.
        What works for one project may not work for another.
        
        By showing trade-offs explicitly, you can make an informed decision that fits your specific context.
        """)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main application flow."""
    # Render sidebar and get inputs
    traffic, control, cost = render_sidebar_controls()
    
    # Render hero
    render_hero()
    
    # Compare button
    if st.button("🔍 Compare Options", type="primary", use_container_width=True):
        weights = st.session_state.weights if st.session_state.advanced_mode else None
        ranked, details = evaluate(traffic, control, cost, weights)
        st.session_state.results = {
            'ranked': ranked,
            'details': details,
            'traffic': traffic,
            'control': control,
            'cost': cost
        }
        st.rerun()
    
    # Render results if available
    if st.session_state.results:
        render_results(
            st.session_state.results['ranked'],
            st.session_state.results['details'],
            st.session_state.results['traffic'],
            st.session_state.results['control'],
            st.session_state.results['cost']
        )

if __name__ == "__main__":
    main()

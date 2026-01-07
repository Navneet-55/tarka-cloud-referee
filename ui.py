"""
Tarka — Cloud Compute Referee
Streamlit UI with optimized control placement and improved readability.
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
    Ensures strong contrast and readable header text.
    """
    if theme == "dark":
        bg_color = "#0e1117"
        card_bg = "#1e2130"
        text_color = "#ffffff"
        muted_color = "#b0b0b0"
        border_color = "#3d4451"
        highlight_bg = "#2a2d3a"
        primary_color = "#ff4b4b"
        secondary_color = "#00d4aa"
        accent_color = "#6366f1"
        header_bg = "#1e2130"
        header_text = "#ffffff"
    else:  # light
        bg_color = "#ffffff"
        card_bg = "#f8f9fa"
        text_color = "#1a1a1a"
        muted_color = "#666666"
        border_color = "#d0d0d0"
        highlight_bg = "#e8f4f8"
        primary_color = "#ff4b4b"
        secondary_color = "#00d4aa"
        accent_color = "#6366f1"
        header_bg = "#ffffff"
        header_text = "#1a1a1a"
    
    css = f"""
    <style>
    /* Ensure Streamlit header is visible and readable */
    header[data-testid="stHeader"] {{
        background-color: {header_bg} !important;
        border-bottom: 1px solid {border_color};
    }}
    
    header[data-testid="stHeader"] h1,
    header[data-testid="stHeader"] h2,
    header[data-testid="stHeader"] h3,
    header[data-testid="stHeader"] span,
    header[data-testid="stHeader"] div {{
        color: {header_text} !important;
    }}
    
    /* Base theme variables */
    :root {{
        --bg: {bg_color};
        --card: {card_bg};
        --text: {text_color};
        --muted: {muted_color};
        --border: {border_color};
        --accent: {primary_color};
        --accent2: {secondary_color};
        --highlight-bg: {highlight_bg};
    }}
    
    /* Ensure strong text contrast - no opacity */
    .stApp {{
        background-color: var(--bg);
    }}
    
    /* Explicit text colors for all elements - no opacity tricks */
    body {{
        color: var(--text) !important;
    }}
    
    p, li, label, span, div, h1, h2, h3, h4, h5, h6 {{
        color: var(--text) !important;
    }}
    
    /* Streamlit markdown elements */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: var(--text) !important;
    }}
    
    /* Streamlit labels and inputs */
    .stSelectbox label, .stSlider label, .stRadio label, .stCheckbox label {{
        color: var(--text) !important;
    }}
    
    /* Hero section */
    .hero-header {{
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }}
    
    .hero-subtitle {{
        text-align: center;
        color: var(--text);
        font-size: 1.1rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }}
    
    .offline-badge {{
        display: inline-block;
        background: var(--accent2);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }}
    
    /* Control bar */
    .control-bar {{
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    
    /* Cards */
    .summary-card {{
        background-color: var(--card);
        border: 2px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    
    .option-card {{
        background-color: var(--card);
        border: 2px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    .best-fit-card {{
        background-color: var(--highlight-bg);
        border: 3px solid var(--accent2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 6px 12px rgba(0, 212, 170, 0.3);
    }}
    
    .exports-card {{
        background-color: var(--card);
        border: 2px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}
    
    /* Badges */
    .rank-badge {{
        display: inline-block;
        background: var(--accent);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }}
    
    .score-badge {{
        display: inline-block;
        background: linear-gradient(135deg, var(--accent), var(--accent2));
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
    
    /* Progress bars */
    .score-meter {{
        height: 8px;
        background: var(--border);
        border-radius: 4px;
        overflow: hidden;
        margin-top: 0.5rem;
    }}
    
    .score-fill {{
        height: 100%;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
        border-radius: 4px;
    }}
    
    /* Footer */
    .footer-text {{
        text-align: center;
        padding: 1rem;
        color: var(--text);
        font-size: 0.85rem;
        border-top: 1px solid var(--border);
        margin-top: 2rem;
    }}
    
    /* Mobile responsiveness */
    @media (max-width: 600px) {{
        .hero-header {{
            font-size: 1.8rem;
            padding: 1rem 0.5rem;
        }}
        
        .summary-card, .option-card, .best-fit-card, .exports-card {{
            padding: 1rem;
            margin: 0.5rem 0;
        }}
        
        .control-bar {{
            padding: 0.75rem;
        }}
        
        [class*="stButton"] {{
            width: 100% !important;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Apply CSS based on current theme
apply_base_css(st.session_state.theme)

# ============================================================================
# SIDEBAR (SECONDARY CONTROLS ONLY)
# ============================================================================

def render_sidebar_secondary():
    """Render only secondary sidebar controls."""
    st.sidebar.title("⚙️ Settings")
    
    # Theme toggle
    theme_options = ["Light", "Dark"]
    theme_idx = 0 if st.session_state.theme == "light" else 1
    theme_choice = st.sidebar.radio("Theme", theme_options, index=theme_idx)
    st.session_state.theme = "light" if theme_choice == "Light" else "dark"
    if theme_choice != theme_options[theme_idx]:
        apply_base_css(st.session_state.theme)
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # About
    with st.sidebar.expander("ℹ️ About"):
        st.markdown("""
        **Decision-support tool** — not a recommendation engine.
        
        Highlights trade-offs between AWS compute options to support informed decision-making.
        
        **No single 'best' answer** — use trade-offs to decide.
        """)
    
    # Help
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
    
    # Glossary
    with st.sidebar.expander("📖 Glossary"):
        st.markdown("""
        **Cold start:** Initial delay when a function/container starts from idle state.
        
        **Ops overhead:** Operational tasks like patching, monitoring, scaling.
        
        **Infrastructure control:** Level of control over underlying infrastructure (networking, storage, OS).
        
        **Burst traffic:** Unpredictable spikes in usage.
        
        **Steady traffic:** Predictable, consistent usage patterns.
        """)

# ============================================================================
# CONTROL BAR (PRIMARY CONTROLS)
# ============================================================================

def render_control_bar():
    """Render primary control bar at top of main page."""
    st.markdown("### 🎛️ Control Bar")
    
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
        
        with col1:
            # Mode toggle
            app_mode = st.radio(
                "Mode",
                ["Simple", "Advanced"],
                index=0 if st.session_state.simple_mode else 1,
                horizontal=True
            )
            st.session_state.simple_mode = (app_mode == "Simple")
            st.session_state.advanced_mode = (app_mode == "Advanced")
        
        with col2:
            # Presets
            st.markdown("**Presets:**")
            preset_cols = st.columns(4)
            presets = {
                "Startup MVP": {"traffic": "bursty", "control": "low", "cost": "sensitive"},
                "High-traffic API": {"traffic": "steady", "control": "medium", "cost": "flexible"},
                "Batch": {"traffic": "steady", "control": "medium", "cost": "sensitive"},
                "Legacy": {"traffic": "steady", "control": "high", "cost": "flexible"}
            }
            
            for idx, (name, values) in enumerate(presets.items()):
                with preset_cols[idx]:
                    if st.button(name, use_container_width=True, key=f"preset_{name}"):
                        st.session_state.traffic = values["traffic"]
                        st.session_state.control = values["control"]
                        st.session_state.cost = values["cost"]
                        st.rerun()
        
        with col3:
            # Compare mode toggle
            compare_mode = st.checkbox("Compare Two Scenarios", value=st.session_state.compare_mode)
            st.session_state.compare_mode = compare_mode
            
            # Reset button
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.traffic = "bursty"
                st.session_state.control = "low"
                st.session_state.cost = "sensitive"
                st.session_state.results = None
                st.session_state.weights = {"traffic": 1.0, "control": 1.0, "cost": 1.0}
                st.rerun()
        
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
    
    st.markdown("---")
    
    # Requirements inputs
    st.markdown("### 📊 Requirements")
    req_col1, req_col2, req_col3 = st.columns(3)
    
    with req_col1:
        traffic = st.selectbox(
            "🚦 Traffic pattern",
            ["bursty", "steady"],
            index=0 if st.session_state.traffic == "bursty" else 1,
            format_func=lambda x: "Bursty / unpredictable" if x == "bursty" else "Steady / predictable"
        )
    
    with req_col2:
        control = st.selectbox(
            "⚙️ Infrastructure control",
            ["low", "medium", "high"],
            index=["low", "medium", "high"].index(st.session_state.control),
            format_func=lambda x: x.capitalize()
        )
    
    with req_col3:
        cost = st.selectbox(
            "💰 Cost sensitivity",
            ["sensitive", "flexible"],
            index=0 if st.session_state.cost == "sensitive" else 1,
            format_func=lambda x: "Very sensitive" if x == "sensitive" else "Flexible"
        )
    
    st.session_state.traffic = traffic
    st.session_state.control = control
    st.session_state.cost = cost
    
    # Advanced mode features
    if st.session_state.advanced_mode:
        st.markdown("---")
        st.markdown("### ⚖️ Advanced Options")
        
        adv_col1, adv_col2, adv_col3 = st.columns(3)
        
        with adv_col1:
            st.markdown("**Input Weights**")
            weight_traffic = st.slider("Traffic", 0.0, 3.0, st.session_state.weights["traffic"], 0.1)
            weight_control = st.slider("Control", 0.0, 3.0, st.session_state.weights["control"], 0.1)
            weight_cost = st.slider("Cost", 0.0, 3.0, st.session_state.weights["cost"], 0.1)
            st.session_state.weights = {
                "traffic": weight_traffic,
                "control": weight_control,
                "cost": weight_cost
            }
        
        with adv_col2:
            st.markdown("**Hard Constraints**")
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
            cold_start = st.checkbox("Cold start tolerance", value=st.session_state.cold_start_tolerance)
            st.session_state.max_exec_time = max_exec_time
            st.session_state.compliance = compliance
            st.session_state.cold_start_tolerance = cold_start
        
        with adv_col3:
            st.markdown("**Preferences**")
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
            
            deterministic = st.checkbox("Deterministic output", value=st.session_state.deterministic_mode)
            st.session_state.deterministic_mode = deterministic
            
            arch_review = st.checkbox("Architecture review language", value=st.session_state.arch_review_mode)
            st.session_state.arch_review_mode = arch_review
    
    # Compare button
    st.markdown("---")
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
    
    return traffic, control, cost

# ============================================================================
# RESULTS RENDERING
# ============================================================================

def render_results(ranked, details, traffic, control, cost):
    """Render results section with all features."""
    if not ranked:
        return
    
    # Input Summary
    st.markdown("### 📋 Input Summary")
    st.markdown(f"""
    <div class="summary-card">
        <strong>Traffic pattern:</strong> {traffic.capitalize()}<br>
        <strong>Infrastructure control:</strong> {control.capitalize()}<br>
        <strong>Cost sensitivity:</strong> {cost.capitalize()}
    </div>
    """, unsafe_allow_html=True)
    
    # Confidence indicator
    conf_level, conf_msg = get_confidence(ranked)
    conf_class = f"confidence-{conf_level.lower()}"
    st.markdown(f'<div class="confidence-badge {conf_class}">Confidence: {conf_level.upper()}</div>', unsafe_allow_html=True)
    st.caption(conf_msg)
    
    # Deterministic mode display
    if st.session_state.deterministic_mode:
        with st.expander("🔍 Deterministic Output Details"):
            st.markdown("**Inputs used:**")
            st.code(f"Traffic: {traffic}, Control: {control}, Cost: {cost}")
            st.markdown("**Raw scores:**")
            for opt in ranked:
                st.code(f"{opt.name}: {opt.score}")
            st.markdown("**Note:** No randomness; no external calls.")
    
    # Ranked Options
    st.markdown("### 🎯 Ranked Options")
    
    max_score = max(opt.score for opt in ranked) if ranked else 1
    
    for idx, opt in enumerate(ranked):
        is_best_fit = idx == 0
        card_class = "best-fit-card" if is_best_fit else "option-card"
        
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        # Rank badge
        st.markdown(f'<span class="rank-badge">#{idx + 1}</span>', unsafe_allow_html=True)
        
        # Preference badge
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
        
        # Use when / Recommended for
        if st.session_state.arch_review_mode:
            st.markdown(f"**Recommended for:** {opt.best_for}")
        else:
            st.markdown(f"**Use when:** {opt.best_for}")
        
        # Explainability timeline
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
    
    # Eliminated Options
    if len(ranked) > 0:
        eliminated = []
        top_score = ranked[0].score
        for opt in ranked[1:]:
            if top_score - opt.score >= 2:
                eliminated.append(opt)
        
        if eliminated:
            st.markdown("### ⚠️ Eliminated / Risky Options")
            for opt in eliminated:
                st.markdown(f"**{opt.name}** — Score gap indicates less alignment with current constraints.")
    
    # What You're Trading Away
    if ranked:
        top_opt = ranked[0]
        st.markdown("### 🔄 What You're Trading Away")
        gains = ", ".join(top_opt.pros[:2])
        trades = ", ".join(top_opt.cons[:2])
        st.markdown(f"**You gain:** {gains}")
        st.markdown(f"**You trade away:** {trades}")
    
    # Hard Constraints Warnings
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
    
    # What Would Change
    suggestions = get_what_would_change(ranked[0].name, traffic, control, cost)
    st.markdown("### 🔄 What Would Change This Decision?")
    for suggestion in suggestions:
        st.markdown(f"• {suggestion}")
    
    # Reflection Mode
    if st.session_state.reflection_mode and ranked:
        st.markdown("### 💭 Reflection")
        top_opt = ranked[0]
        st.markdown(f"If I were building this system, I'd start with **{top_opt.name}** when constraints look like {traffic} traffic, {control} control needs, and {cost} cost sensitivity. This aligns with '{top_opt.best_for}'.")
    
    # Exports Card
    st.markdown("### 📤 Exports")
    st.markdown('<div class="exports-card">', unsafe_allow_html=True)
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        # Markdown download
        md_content = f"""# Tarka Decision Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Input Summary
- Traffic: {traffic}
- Control: {control}
- Cost: {cost}

## Confidence / Sensitivity
**Level:** {conf_level.upper()}
**Message:** {conf_msg}

## Recommended Options (Ranked)
"""
        for idx, opt in enumerate(ranked):
            md_content += f"""
### {idx + 1}. {opt.name}
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
    
    with col_exp2:
        # Copy summary text area
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
        
        st.text_area("Copy Decision Summary", value=summary_text, height=150, key="summary_text")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # JSON download
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
    
    # Footer
    st.markdown('<div class="footer-text">Decision logic: v1 (deterministic, local)</div>', unsafe_allow_html=True)
    
    # Why no single best answer
    with st.expander("🤔 Why no single \'best\' answer?"):
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
    # Render sidebar (secondary only)
    render_sidebar_secondary()
    
    # Hero section
    st.markdown("""
    <div style="text-align: center; font-size: 0.85rem; color: var(--muted); margin-bottom: 0.5rem; padding: 0.5rem; background-color: var(--card); border-radius: 8px;">
        💡 Tip: App controls are in the main page. The ⋮ menu is Streamlit system options.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="hero-header">Tarka — Cloud Compute Referee</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Compare AWS compute options by understanding trade-offs</div>', unsafe_allow_html=True)
    st.markdown('<div class="offline-badge">Offline • Deterministic • No external APIs</div>', unsafe_allow_html=True)
    
    # Render control bar and get inputs
    traffic, control, cost = render_control_bar()
    
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

"""
Tarka — Cloud Compute Referee
Streamlit UI with clean architecture and smooth interactions.
"""

import streamlit as st
import json
from datetime import datetime
from src.models import EvaluationInputs, EvaluationResult
from src.tarka_core import evaluate, get_compute_options
from src.rendering import format_confidence


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

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
    """Initialize session state with defaults."""
    defaults = {
        'traffic': "bursty",
        'control': "low",
        'cost': "sensitive",
        'theme': "light",
        'mode': "simple",
        'results': None,
        'weights': {"traffic": 1.0, "control": 1.0, "cost": 1.0}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


# ============================================================================
# CSS AND THEMING
# ============================================================================

def apply_base_css(theme: str):
    """Apply base CSS with theme support and smooth animations."""
    if theme == "dark":
        bg_color = "#0e1117"
        card_bg = "#1a1f2e"
        surface = "#252b3a"
        text_color = "#ffffff"
        muted_color = "#b0b0b0"
        border_color = "#3d4451"
        sidebar_bg = "#151a28"
        primary_color = "#ff4b4b"
        secondary_color = "#00d4aa"
        accent_color = "#6366f1"
    else:  # light
        bg_color = "#f5f7fa"  # Tinted background
        card_bg = "#ffffff"
        surface = "#ffffff"
        text_color = "#2d3748"  # Dark slate
        muted_color = "#718096"
        border_color = "#e2e8f0"
        sidebar_bg = "#ffffff"
        primary_color = "#ff4b4b"
        secondary_color = "#00d4aa"
        accent_color = "#6366f1"
    
    css = f"""
    <style>
    /* Motion system */
    :root {{
        --ease: cubic-bezier(0.22, 1, 0.36, 1);
        --ease-soft: cubic-bezier(0.16, 1, 0.3, 1);
        --dur-1: 120ms;
        --dur-2: 220ms;
        --dur-3: 360ms;
        --shadow-1: 0 1px 3px rgba(0, 0, 0, 0.08);
        --shadow-2: 0 4px 12px rgba(0, 0, 0, 0.12);
        --radius: 16px;
    }}
    
    /* Accessibility: Respect reduced motion */
    @media (prefers-reduced-motion: reduce) {{
        *,
        *::before,
        *::after {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }}
    }}
    
    /* Streamlit header - keep visible and readable */
    header[data-testid="stHeader"] {{
        background-color: {sidebar_bg} !important;
        border-bottom: 1px solid {border_color};
    }}
    
    header[data-testid="stHeader"] * {{
        color: {text_color} !important;
    }}
    
    /* Base theme variables */
    :root {{
        --bg: {bg_color};
        --card: {card_bg};
        --surface: {surface};
        --text: {text_color};
        --muted: {muted_color};
        --border: {border_color};
        --accent: {primary_color};
        --accent2: {secondary_color};
        --sidebar-bg: {sidebar_bg};
    }}
    
    /* App background */
    .stApp {{
        background-color: var(--bg);
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border);
    }}
    
    [data-testid="stSidebar"] * {{
        color: var(--text) !important;
    }}
    
    /* Text colors - no opacity */
    body, p, li, label, span, div, h1, h2, h3, h4, h5, h6 {{
        color: var(--text) !important;
    }}
    
    .stMarkdown, .stMarkdown * {{
        color: var(--text) !important;
    }}
    
    /* Hero section */
    .hero-header {{
        text-align: center;
        padding: 2rem 1rem;
        color: var(--text) !important;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        animation: fadeInUp var(--dur-3) var(--ease);
    }}
    
    .hero-header::after {{
        content: '';
        display: block;
        width: 120px;
        height: 3px;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
        margin: 0.75rem auto 0;
        border-radius: 2px;
        animation: fadeInUp var(--dur-3) var(--ease) 0.1s both;
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
        background: linear-gradient(135deg, var(--accent2), var(--accent));
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.5rem 0;
        box-shadow: var(--shadow-1);
    }}
    
    /* Cards */
    .tarka-card {{
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: var(--shadow-1);
        transition: transform var(--dur-2) var(--ease),
                    box-shadow var(--dur-2) var(--ease);
        animation: fadeInUp var(--dur-2) var(--ease-soft);
    }}
    
    .tarka-card:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-2);
    }}
    
    .option-card {{
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: var(--shadow-1);
        transition: transform var(--dur-2) var(--ease),
                    box-shadow var(--dur-2) var(--ease);
        animation: fadeInUp var(--dur-2) var(--ease-soft);
    }}
    
    .option-card:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-2);
    }}
    
    .best-fit-card {{
        background-color: var(--surface);
        border: 2px solid var(--accent2);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.2);
        animation: fadeInUp var(--dur-2) var(--ease-soft);
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
    
    /* Buttons */
    .stButton > button {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: background-color var(--dur-1) var(--ease),
                    border-color var(--dur-1) var(--ease),
                    transform var(--dur-1) var(--ease),
                    box-shadow var(--dur-1) var(--ease);
    }}
    
    .stButton > button:hover {{
        background-color: var(--card) !important;
        border-color: var(--accent) !important;
        transform: translateY(-1px);
        box-shadow: var(--shadow-2);
    }}
    
    .stButton > button:active {{
        transform: translateY(0);
    }}
    
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
        color: white !important;
        border: none !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.25);
    }}
    
    /* Inputs */
    .stSelectbox > div > div {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        transition: border-color var(--dur-1) var(--ease);
    }}
    
    .stSelectbox > div > div:hover {{
        border-color: var(--accent) !important;
    }}
    
    .stRadio > div > label,
    .stCheckbox > label {{
        color: var(--text) !important;
    }}
    
    /* Animations */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(8px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    /* Mobile responsiveness */
    @media (max-width: 600px) {{
        .hero-header {{
            font-size: 1.8rem;
            padding: 1rem 0.5rem;
        }}
        
        body, p, li, label {{
            font-size: 16px !important;
        }}
        
        .tarka-card, .option-card, .best-fit-card {{
            padding: 1rem;
            margin: 1rem 0;
        }}
        
        [class*="stButton"] {{
            width: 100% !important;
        }}
        
        .tarka-card:hover,
        .option-card:hover {{
            transform: none;
        }}
    }}
    
    /* Mobile hint */
    .mobile-hint {{
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.75rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: var(--text);
        text-align: center;
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
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Apply CSS
apply_base_css(st.session_state.theme)


# ============================================================================
# SIDEBAR (SECONDARY CONTROLS ONLY)
# ============================================================================

def render_sidebar():
    """Render sidebar with minimal controls."""
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
    
    # About Tarka
    with st.sidebar.expander("ℹ️ About Tarka — Cloud Compute Referee"):
        st.markdown("""
        Tarka is a constraint-aware decision-support tool designed to help developers reason through AWS compute choices.
        Instead of recommending a single 'best' service, it explains trade-offs across Lambda, ECS, and EC2 based on real-world constraints such as traffic patterns, infrastructure control, and cost sensitivity.
        The goal is to support thoughtful architectural decisions, especially in early-stage system design.
        """)
        
        st.markdown("---")
        st.markdown("**How Tarka Works**")
        st.markdown("""
        • User inputs are collected via a lightweight Streamlit interface  
        • Inputs are mapped to deterministic rules (no probabilistic scoring or ML inference)
        • Each compute option accumulates alignment signals based on constraints
        • Final output presents ranked options with clear pros, cons, and watch-outs
        • The system intentionally avoids a single definitive recommendation
        """)
        
        st.markdown("---")
        st.markdown("**Technical Architecture & Stack**")
        st.markdown("""
        • **Language:** Python 3.9+
        • **UI Framework:** Streamlit
        • **Core Logic:** Pure Python (rule-based, deterministic)
        • **State Management:** Streamlit session state
        • **Styling:** Custom CSS injected at runtime (theme-aware)
        • **Runtime:** Local execution; no backend services required
        """)
        
        st.markdown("**Explicit Guarantees:**")
        st.markdown("""
        • No external APIs
        • No cloud calls
        • No data collection
        • Fully offline-capable
        • Reproducible results for the same inputs
        """)
        
        st.markdown("---")
        st.markdown("**Design Philosophy**")
        st.markdown("""
        Tarka is intentionally opinionated in structure but transparent in reasoning.
        The interface is designed to feel calm, readable, and focused — prioritizing clarity over complexity.
        Visual polish supports comprehension rather than distraction, especially on mobile devices.
        """)
        
        st.markdown("---")
        st.markdown("**Creator**")
        st.markdown("""
        Created by **Navneet Patnaik**
        
        Built as part of the AI for Bharat — Kiro Week 6 challenge.
        All architectural decisions, scoring logic, and UI structure were implemented manually.
        
        **GitHub:** [https://github.com/Navneet-55](https://github.com/Navneet-55)
        """)
        
        st.markdown("---")
        st.markdown("""
        <div style="color: var(--muted); font-size: 0.9rem; font-style: italic; margin-top: 0.5rem; padding-top: 1rem; border-top: 1px solid var(--border);">
        This tool is intended to support architectural reasoning and does not replace professional judgment.
        </div>
        """, unsafe_allow_html=True)
    
    # Help
    with st.sidebar.expander("❓ Help"):
        st.markdown("""
        **Run locally:**
        ```bash
        streamlit run ui.py
        ```
        
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
    """Render control bar with inputs and presets."""
    st.markdown("### 🎛️ Control Bar")
    st.markdown('<div class="tarka-card">', unsafe_allow_html=True)
    
    # Mode toggle
    mode = st.radio(
        "Mode",
        ["Simple", "Advanced"],
        index=0 if st.session_state.mode == "simple" else 1,
        horizontal=True
    )
    st.session_state.mode = "simple" if mode == "Simple" else "advanced"
    
    st.markdown("---")
    
    # Presets
    st.markdown("**Quick Presets:**")
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
                st.session_state.results = None
                st.rerun()
    
    st.markdown("---")
    
    # Requirements inputs
    st.markdown("**Requirements:**")
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
    
    # Advanced mode weights
    if st.session_state.mode == "advanced":
        st.markdown("---")
        st.markdown("**Input Weights:**")
        w_col1, w_col2, w_col3 = st.columns(3)
        with w_col1:
            weight_traffic = st.slider("Traffic", 0.0, 3.0, st.session_state.weights["traffic"], 0.1)
        with w_col2:
            weight_control = st.slider("Control", 0.0, 3.0, st.session_state.weights["control"], 0.1)
        with w_col3:
            weight_cost = st.slider("Cost", 0.0, 3.0, st.session_state.weights["cost"], 0.1)
        st.session_state.weights = {
            "traffic": weight_traffic,
            "control": weight_control,
            "cost": weight_cost
        }
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Compare button
    st.markdown("---")
    if st.button("🔍 Compare Options", type="primary", use_container_width=True):
        inputs = EvaluationInputs(
            traffic=traffic,
            control=control,
            cost=cost,
            weights=st.session_state.weights if st.session_state.mode == "advanced" else None
        )
        result = evaluate(inputs)
        st.session_state.results = result
        st.rerun()
    
    return traffic, control, cost


# ============================================================================
# RESULTS RENDERING
# ============================================================================

def render_results(result: EvaluationResult):
    """Render evaluation results."""
    if not result or not result.ranked_options:
        return
    
    st.markdown("### 📋 Input Summary")
    st.markdown(f"""
    <div class="tarka-card">
        <strong>Traffic pattern:</strong> {result.inputs.traffic.capitalize()}<br>
        <strong>Infrastructure control:</strong> {result.inputs.control.capitalize()}<br>
        <strong>Cost sensitivity:</strong> {result.inputs.cost.capitalize()}
    </div>
    """, unsafe_allow_html=True)
    
    # Confidence
    conf_class = f"confidence-{result.confidence_level.lower()}"
    st.markdown(f'<div class="confidence-badge {conf_class}">Confidence: {result.confidence_level.upper()}</div>', unsafe_allow_html=True)
    st.caption(result.confidence_message)
    
    # Ranked options
    st.markdown("### 🎯 Ranked Options")
    
    max_score = max(opt.score for opt in result.ranked_options) if result.ranked_options else 1
    
    for opt in result.ranked_options:
        evaluation = result.option_details[opt.name]
        is_best_fit = evaluation.rank == 1
        card_class = "best-fit-card" if is_best_fit else "option-card"
        
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        # Rank and score
        st.markdown(f'<span class="rank-badge">#{evaluation.rank}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="score-badge">Score: {opt.score:.1f}</div>', unsafe_allow_html=True)
        
        st.markdown(f"#### {opt.name}")
        st.markdown(f"**Recommended for:** {opt.best_for}")
        
        # Why this scored
        with st.expander("📊 Why this scored"):
            for reason in evaluation.rationale:
                st.markdown(f"• {reason}")
        
        # Pros / Cons
        col_pros, col_cons = st.columns(2)
        with col_pros:
            st.markdown("**✅ Pros**")
            for pro in opt.pros:
                st.markdown(f"• {pro}")
        with col_cons:
            st.markdown("**❌ Cons**")
            for con in opt.cons:
                st.markdown(f"• {con}")
        
        # Watch outs
        st.markdown("**⚠️ Watch out for:**")
        for watch_out in opt.watch_outs:
            st.markdown(f"  • {watch_out}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # What would change
    if result.what_would_change:
        st.markdown("### 🔄 What Would Change This Decision?")
        for suggestion in result.what_would_change:
            st.markdown(f"• {suggestion}")
    
    # Exports
    st.markdown("### 📤 Exports")
    st.markdown('<div class="tarka-card">', unsafe_allow_html=True)
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        # Markdown export
        md_content = f"""# Tarka Decision Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Input Summary
- Traffic: {result.inputs.traffic}
- Control: {result.inputs.control}
- Cost: {result.inputs.cost}

## Confidence
**Level:** {result.confidence_level.upper()}
**Message:** {result.confidence_message}

## Ranked Options
"""
        for opt in result.ranked_options:
            eval_detail = result.option_details[opt.name]
            md_content += f"""
### {eval_detail.rank}. {opt.name}
**Score:** {opt.score:.1f}
**Recommended for:** {opt.best_for}

**Why this scored:**
"""
            for reason in eval_detail.rationale:
                md_content += f"- {reason}\n"
            
            md_content += f"""
**Pros:**
"""
            for pro in opt.pros:
                md_content += f"- {pro}\n"
            
            md_content += f"""
**Cons:**
"""
            for con in opt.cons:
                md_content += f"- {con}\n"
            
            md_content += f"""
**Watch out for:**
"""
            for watch_out in opt.watch_outs:
                md_content += f"- {watch_out}\n"
            
            md_content += "\n---\n\n"
        
        md_content += "## Disclaimer\n\n"
        md_content += "This is not a single best answer; use the trade-offs above to decide.\n"
        
        st.download_button(
            "📄 Download Markdown",
            data=md_content,
            file_name=f"tarka_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col_exp2:
        # Copy summary
        summary_text = f"""Inputs: Traffic={result.inputs.traffic}, Control={result.inputs.control}, Cost={result.inputs.cost}

Ranked Options:
"""
        for opt in result.ranked_options:
            eval_detail = result.option_details[opt.name]
            summary_text += f"{eval_detail.rank}. {opt.name} (Score: {opt.score:.1f}) - {opt.best_for}\n"
        
        summary_text += f"""
Trade-off Summary:
Top choice: {result.top_option.name}
Gains: {', '.join(result.top_option.pros[:2])}
Trade-offs: {', '.join(result.top_option.cons[:2])}

Disclaimer: This is not a single best answer; use the trade-offs above to decide.
"""
        
        st.text_area("Copy Decision Summary", value=summary_text, height=150, key="summary_text")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="footer-text">
        <strong>Note:</strong> This is not a single best answer; use the trade-offs above to decide.<br>
        Decision logic: v1 (deterministic, local)
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main application flow."""
    # Render sidebar
    render_sidebar()
    
    # Hero section
    st.markdown("""
    <div style="text-align: center; font-size: 0.85rem; color: var(--muted); margin-bottom: 0.5rem; padding: 0.5rem; background-color: var(--surface); border-radius: 8px;">
        💡 Tip: App controls are in the main page. The ⋮ menu is Streamlit system options.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="hero-header">Tarka — Cloud Compute Referee</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Compare AWS compute options by understanding trade-offs</div>', unsafe_allow_html=True)
    st.markdown('<div class="offline-badge">Offline • Deterministic • No external APIs</div>', unsafe_allow_html=True)
    
    # Mobile hint
    st.markdown("""
    <div class="mobile-hint">
        ☰ Use the sidebar for theme/info. Main controls are below.
    </div>
    """, unsafe_allow_html=True)
    
    # Control bar
    render_control_bar()
    
    # Results
    if st.session_state.results:
        render_results(st.session_state.results)


if __name__ == "__main__":
    main()

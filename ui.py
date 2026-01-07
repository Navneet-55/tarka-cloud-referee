import streamlit as st
import json
from datetime import datetime
from src.tarka_core import get_compute_options, score_options, get_score_rationale

st.set_page_config(
    page_title="Tarka — Cloud Compute Referee",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'traffic' not in st.session_state:
    st.session_state.traffic = "bursty"
if 'control' not in st.session_state:
    st.session_state.control = "low"
if 'cost' not in st.session_state:
    st.session_state.cost = "sensitive"
if 'results' not in st.session_state:
    st.session_state.results = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "card"

# Dark mode toggle in sidebar
st.sidebar.title("⚙️ Settings")
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

# View mode toggle
st.sidebar.markdown("---")
st.sidebar.markdown("### View Options")
view_mode = st.sidebar.radio(
    "Display mode",
    ["Card view", "Table view"],
    index=0 if st.session_state.view_mode == "card" else 1
)
st.session_state.view_mode = "card" if view_mode == "Card view" else "table"

# Custom CSS for theming
css_vars = """
    :root {{
        --bg-color: {bg};
        --card-bg: {card_bg};
        --text-color: {text};
        --border-color: {border};
        --primary-color: #ff4b4b;
        --secondary-color: #00d4aa;
        --accent-color: #6366f1;
        --highlight-bg: {highlight};
    }}
    .stApp {{
        background-color: var(--bg-color);
    }}
"""

if dark_mode:
    css = css_vars.format(
        bg="#0e1117", card_bg="#1e2130", text="#fafafa",
        border="#3d4451", highlight="#2a2d3a"
    )
else:
    css = css_vars.format(
        bg="#ffffff", card_bg="#f8f9fa", text="#262730",
        border="#e0e0e0", highlight="#e8f4f8"
    )

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Main CSS styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .tagline {
        text-align: center;
        color: var(--text-color);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        opacity: 0.8;
    }
    .input-summary-card {
        background-color: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .option-card {
        background-color: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .option-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .best-fit-card {
        background-color: var(--highlight-bg);
        border: 3px solid var(--secondary-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 6px 12px rgba(0, 212, 170, 0.3);
    }
    .score-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 0.5rem 1.2rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    .score-meter {
        height: 8px;
        background: var(--border-color);
        border-radius: 4px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    .score-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        border-radius: 4px;
        transition: width 0.3s;
    }
    .note-box {
        background-color: var(--card-bg);
        border-left: 4px solid var(--primary-color);
        padding: 1.2rem;
        margin-top: 2rem;
        border-radius: 4px;
    }
    .context-hint {
        font-size: 0.85rem;
        color: var(--text-color);
        opacity: 0.7;
        font-style: italic;
        margin-top: 0.25rem;
    }
    h3, h4 {
        color: var(--text-color) !important;
    }
    .best-fit-label {
        display: inline-block;
        background: var(--secondary-color);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">Tarka — Cloud Compute Referee</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Compare AWS compute options by understanding trade-offs</div>', unsafe_allow_html=True)

# About expander
with st.expander("ℹ️ About"):
    st.markdown("""
    **Challenge**: Choosing the right AWS compute service early in a project can be confusing.
    
    **What this tool does**: Tarka helps you compare AWS Lambda, ECS/Fargate, and EC2 by showing ranked options with scores, use cases, pros, and cons. It supports informed decision-making rather than providing a single "best" answer.
    
    **Architecture context**:
    - **Lambda**: Serverless functions - event-driven, auto-scaling, pay-per-use
    - **ECS (Fargate)**: Managed containers - good balance of control and abstraction
    - **EC2**: Virtual machines - maximum infrastructure control and customization
    """)

# Reset button
if st.session_state.results is not None:
    if st.button("🔄 Reset / Try Another Scenario", use_container_width=True):
        st.session_state.results = None
        st.session_state.traffic = "bursty"
        st.session_state.control = "low"
        st.session_state.cost = "sensitive"
        st.rerun()

# Input section
st.markdown("### 📊 Your Requirements")
col1, col2, col3 = st.columns(3)

with col1:
    traffic = st.selectbox(
        "🚦 Traffic pattern",
        ["bursty", "steady"],
        index=0 if st.session_state.traffic == "bursty" else 1,
        format_func=lambda x: "Bursty / unpredictable" if x == "bursty" else "Steady / predictable"
    )

with col2:
    control = st.selectbox(
        "⚙️ Infrastructure control required",
        ["low", "medium", "high"],
        index=["low", "medium", "high"].index(st.session_state.control),
        format_func=lambda x: x.capitalize()
    )

with col3:
    cost = st.selectbox(
        "💰 Cost sensitivity",
        ["sensitive", "flexible"],
        index=0 if st.session_state.cost == "sensitive" else 1,
        format_func=lambda x: "Very sensitive" if x == "sensitive" else "Flexible"
    )

st.session_state.traffic = traffic
st.session_state.control = control
st.session_state.cost = cost

if st.button("🔍 Compare Options", type="primary", use_container_width=True):
    options = get_compute_options()
    ranked = score_options(options, traffic, control, cost)
    st.session_state.results = {
        'ranked': ranked,
        'traffic': traffic,
        'control': control,
        'cost': cost
    }
    st.rerun()

# Display results
if st.session_state.results:
    ranked = st.session_state.results['ranked']
    traffic = st.session_state.results['traffic']
    control = st.session_state.results['control']
    cost = st.session_state.results['cost']
    
    # Input summary card
    st.markdown("### 📋 Input Summary")
    st.markdown(f"""
    <div class="input-summary-card">
        <strong>Traffic pattern:</strong> {traffic.capitalize()}<br>
        <strong>Infrastructure control:</strong> {control.capitalize()}<br>
        <strong>Cost sensitivity:</strong> {cost.capitalize()}
    </div>
    """, unsafe_allow_html=True)
    
    # Get max score for progress bars
    max_score = max(opt.score for opt in ranked) if ranked else 1
    
    if st.session_state.view_mode == "card":
        st.markdown("### 🎯 Recommended Options (Ranked)")
        
        for idx, opt in enumerate(ranked):
            is_best_fit = idx == 0
            card_class = "best-fit-card" if is_best_fit else "option-card"
            
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            
            if is_best_fit:
                st.markdown('<div class="best-fit-label">🏆 Best fit based on your inputs (not a recommendation)</div>', unsafe_allow_html=True)
            
            col_title, col_score = st.columns([3, 1])
            with col_title:
                st.markdown(f"#### {opt.name}")
                # Architecture context hint
                if opt.name == "AWS Lambda":
                    st.markdown('<div class="context-hint">Serverless functions - event-driven, auto-scaling</div>', unsafe_allow_html=True)
                elif opt.name == "AWS ECS (Fargate)":
                    st.markdown('<div class="context-hint">Managed containers - balanced control and abstraction</div>', unsafe_allow_html=True)
                elif opt.name == "AWS EC2":
                    st.markdown('<div class="context-hint">Virtual machines - maximum infrastructure control</div>', unsafe_allow_html=True)
            
            with col_score:
                st.markdown(f'<div class="score-badge">Score: {opt.score}</div>', unsafe_allow_html=True)
                # Score meter
                score_pct = (opt.score / max_score * 100) if max_score > 0 else 0
                st.markdown(f"""
                <div class="score-meter">
                    <div class="score-fill" style="width: {score_pct}%"></div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"**Use when:** {opt.best_for}")
            
            # Score rationale
            rationale = get_score_rationale(opt.name, traffic, control, cost)
            with st.expander("📊 Why this scored"):
                for reason in rationale:
                    st.markdown(f"• {reason}")
            
            col_pros, col_cons = st.columns(2)
            with col_pros:
                st.markdown("**✅ Pros**")
                for p in opt.pros:
                    st.markdown(f"• {p}")
            with col_cons:
                st.markdown("**❌ Cons**")
                for c in opt.cons:
                    st.markdown(f"• {c}")
            
            st.markdown("**⚠️ Watch out for:**")
            for c in opt.cons:
                st.markdown(f"  • {c}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
    else:  # Table view
        st.markdown("### 🎯 Comparison Table")
        
        # Create table data
        table_data = []
        for idx, opt in enumerate(ranked):
            rationale = get_score_rationale(opt.name, traffic, control, cost)
            table_data.append({
                "Rank": idx + 1,
                "Option": opt.name,
                "Score": opt.score,
                "Use When": opt.best_for,
                "Pros": " • ".join(opt.pros),
                "Cons": " • ".join(opt.cons),
                "Watch Outs": " • ".join(opt.cons),
                "Score Rationale": " • ".join(rationale)
            })
        
        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )
    
    # Note at the end
    st.markdown("""
    <div class="note-box">
        <strong>📝 Note:</strong> This is not a single best answer; use the trade-offs above to decide.
    </div>
    """, unsafe_allow_html=True)
    
    # Download snapshot
    st.markdown("---")
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "inputs": {
            "traffic": traffic,
            "control": control,
            "cost": cost
        },
        "results": [
            {
                "rank": idx + 1,
                "name": opt.name,
                "score": opt.score,
                "use_when": opt.best_for,
                "pros": opt.pros,
                "cons": opt.cons,
                "watch_outs": opt.cons,
                "score_rationale": get_score_rationale(opt.name, traffic, control, cost)
            }
            for idx, opt in enumerate(ranked)
        ],
        "disclaimer": "This is not a single best answer; use the trade-offs above to decide."
    }
    
    json_str = json.dumps(snapshot, indent=2)
    st.download_button(
        label="💾 Download Decision Snapshot (JSON)",
        data=json_str,
        file_name=f"tarka_decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )

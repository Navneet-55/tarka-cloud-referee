import streamlit as st
import json
from datetime import datetime
from src.tarka_core import (
    get_compute_options, score_options, get_score_rationale,
    evaluate, get_confidence, get_what_would_change, get_assumptions
)

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
if 'compare_mode' not in st.session_state:
    st.session_state.compare_mode = False
if 'advanced_mode' not in st.session_state:
    st.session_state.advanced_mode = False
if 'weights' not in st.session_state:
    st.session_state.weights = {"traffic": 1.0, "control": 1.0, "cost": 1.0}
if 'scenario_b' not in st.session_state:
    st.session_state.scenario_b = {"traffic": "steady", "control": "medium", "cost": "flexible"}

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

# Compare mode toggle
compare_mode = st.sidebar.toggle("Compare Two Scenarios", value=st.session_state.compare_mode)
st.session_state.compare_mode = compare_mode

# Advanced mode toggle
advanced_mode = st.sidebar.toggle("Advanced Mode (Weighted Inputs)", value=st.session_state.advanced_mode)
st.session_state.advanced_mode = advanced_mode

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
    .confidence-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    .confidence-high {
        background-color: #00d4aa;
        color: white;
    }
    .confidence-medium {
        background-color: #ffa500;
        color: white;
    }
    .confidence-low {
        background-color: #ff6b6b;
        color: white;
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

# Assumptions expander
with st.expander("📋 Assumptions"):
    assumptions = get_assumptions()
    for assumption in assumptions:
        st.markdown(f"• {assumption}")

# Reset button
if st.session_state.results is not None:
    if st.button("🔄 Reset / Try Another Scenario", use_container_width=True):
        st.session_state.results = None
        st.session_state.traffic = "bursty"
        st.session_state.control = "low"
        st.session_state.cost = "sensitive"
        st.session_state.scenario_b = {"traffic": "steady", "control": "medium", "cost": "flexible"}
        st.rerun()

# Scenario Presets
st.markdown("### 🎯 Scenario Presets")
preset_cols = st.columns(4)
presets = {
    "Startup MVP": {"traffic": "bursty", "control": "low", "cost": "sensitive"},
    "High-traffic API": {"traffic": "steady", "control": "medium", "cost": "flexible"},
    "Batch processing": {"traffic": "steady", "control": "medium", "cost": "sensitive"},
    "Legacy migration": {"traffic": "steady", "control": "high", "cost": "flexible"}
}

for idx, (name, values) in enumerate(presets.items()):
    with preset_cols[idx]:
        if st.button(name, use_container_width=True, key=f"preset_{idx}"):
            st.session_state.traffic = values["traffic"]
            st.session_state.control = values["control"]
            st.session_state.cost = values["cost"]
            st.rerun()

# Input section
if compare_mode:
    st.markdown("### 📊 Scenario A (Primary)")
    col1a, col2a, col3a = st.columns(3)
    with col1a:
        traffic_a = st.selectbox(
            "🚦 Traffic pattern",
            ["bursty", "steady"],
            index=0 if st.session_state.traffic == "bursty" else 1,
            format_func=lambda x: "Bursty / unpredictable" if x == "bursty" else "Steady / predictable",
            key="traffic_a"
        )
    with col2a:
        control_a = st.selectbox(
            "⚙️ Infrastructure control required",
            ["low", "medium", "high"],
            index=["low", "medium", "high"].index(st.session_state.control),
            format_func=lambda x: x.capitalize(),
            key="control_a"
        )
    with col3a:
        cost_a = st.selectbox(
            "💰 Cost sensitivity",
            ["sensitive", "flexible"],
            index=0 if st.session_state.cost == "sensitive" else 1,
            format_func=lambda x: "Very sensitive" if x == "sensitive" else "Flexible",
            key="cost_a"
        )
    
    st.markdown("### 📊 Scenario B (Comparison)")
    col1b, col2b, col3b = st.columns(3)
    with col1b:
        traffic_b = st.selectbox(
            "🚦 Traffic pattern",
            ["bursty", "steady"],
            index=0 if st.session_state.scenario_b["traffic"] == "bursty" else 1,
            format_func=lambda x: "Bursty / unpredictable" if x == "bursty" else "Steady / predictable",
            key="traffic_b"
        )
    with col2b:
        control_b = st.selectbox(
            "⚙️ Infrastructure control required",
            ["low", "medium", "high"],
            index=["low", "medium", "high"].index(st.session_state.scenario_b["control"]),
            format_func=lambda x: x.capitalize(),
            key="control_b"
        )
    with col3b:
        cost_b = st.selectbox(
            "💰 Cost sensitivity",
            ["sensitive", "flexible"],
            index=0 if st.session_state.scenario_b["cost"] == "sensitive" else 1,
            format_func=lambda x: "Very sensitive" if x == "sensitive" else "Flexible",
            key="cost_b"
        )
    
    st.session_state.traffic = traffic_a
    st.session_state.control = control_a
    st.session_state.cost = cost_a
    st.session_state.scenario_b = {"traffic": traffic_b, "control": control_b, "cost": cost_b}
    
    if st.button("🔍 Compare Both Scenarios", type="primary", use_container_width=True):
        weights_a = st.session_state.weights if advanced_mode else None
        weights_b = st.session_state.weights if advanced_mode else None
        
        ranked_a, details_a = evaluate(traffic_a, control_a, cost_a, weights_a)
        ranked_b, details_b = evaluate(traffic_b, control_b, cost_b, weights_b)
        
        st.session_state.results = {
            'scenario_a': {
                'ranked': ranked_a,
                'details': details_a,
                'traffic': traffic_a,
                'control': control_a,
                'cost': cost_a
            },
            'scenario_b': {
                'ranked': ranked_b,
                'details': details_b,
                'traffic': traffic_b,
                'control': control_b,
                'cost': cost_b
            },
            'compare_mode': True
        }
        st.rerun()
else:
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
    
    # Advanced mode weights
    if advanced_mode:
        st.markdown("### ⚖️ Advanced: Input Weights")
        st.caption("Adjust weights to emphasize different factors. Default is 1.0 for all.")
        w_col1, w_col2, w_col3 = st.columns(3)
        with w_col1:
            weight_traffic = st.slider("Weight: Traffic", 0.0, 3.0, st.session_state.weights["traffic"], 0.1)
        with w_col2:
            weight_control = st.slider("Weight: Control", 0.0, 3.0, st.session_state.weights["control"], 0.1)
        with w_col3:
            weight_cost = st.slider("Weight: Cost", 0.0, 3.0, st.session_state.weights["cost"], 0.1)
        st.session_state.weights = {
            "traffic": weight_traffic,
            "control": weight_control,
            "cost": weight_cost
        }
    
    if st.button("🔍 Compare Options", type="primary", use_container_width=True):
        weights = st.session_state.weights if advanced_mode else None
        ranked, details = evaluate(traffic, control, cost, weights)
        st.session_state.results = {
            'ranked': ranked,
            'details': details,
            'traffic': traffic,
            'control': control,
            'cost': cost,
            'weights': weights,
            'compare_mode': False
        }
        st.rerun()

# Display results
if st.session_state.results:
    if st.session_state.results.get('compare_mode', False):
        # Compare mode display
        scenario_a = st.session_state.results['scenario_a']
        scenario_b = st.session_state.results['scenario_b']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("### 📊 Scenario A Results")
            ranked_a = scenario_a['ranked']
            traffic_a = scenario_a['traffic']
            control_a = scenario_a['control']
            cost_a = scenario_a['cost']
            details_a = scenario_a['details']
            
            st.markdown(f"""
            <div class="input-summary-card">
                <strong>Traffic:</strong> {traffic_a.capitalize()}<br>
                <strong>Control:</strong> {control_a.capitalize()}<br>
                <strong>Cost:</strong> {cost_a.capitalize()}
            </div>
            """, unsafe_allow_html=True)
            
            conf_level_a, conf_msg_a = get_confidence(ranked_a)
            conf_class = f"confidence-{conf_level_a.lower()}"
            st.markdown(f'<div class="confidence-badge {conf_class}">Confidence: {conf_level_a.upper()}</div>', unsafe_allow_html=True)
            st.caption(conf_msg_a)
            
            for idx, opt in enumerate(ranked_a[:3]):
                st.markdown(f"**{idx+1}. {opt.name}** (Score: {opt.score})")
        
        with col_b:
            st.markdown("### 📊 Scenario B Results")
            ranked_b = scenario_b['ranked']
            traffic_b = scenario_b['traffic']
            control_b = scenario_b['control']
            cost_b = scenario_b['cost']
            details_b = scenario_b['details']
            
            st.markdown(f"""
            <div class="input-summary-card">
                <strong>Traffic:</strong> {traffic_b.capitalize()}<br>
                <strong>Control:</strong> {control_b.capitalize()}<br>
                <strong>Cost:</strong> {cost_b.capitalize()}
            </div>
            """, unsafe_allow_html=True)
            
            conf_level_b, conf_msg_b = get_confidence(ranked_b)
            conf_class = f"confidence-{conf_level_b.lower()}"
            st.markdown(f'<div class="confidence-badge {conf_class}">Confidence: {conf_level_b.upper()}</div>', unsafe_allow_html=True)
            st.caption(conf_msg_b)
            
            for idx, opt in enumerate(ranked_b[:3]):
                st.markdown(f"**{idx+1}. {opt.name}** (Score: {opt.score})")
        
        # Delta analysis
        if ranked_a[0].name != ranked_b[0].name:
            st.markdown("### 🔄 Delta Analysis")
            changes = []
            if traffic_a != traffic_b:
                changes.append(f"Traffic: {traffic_a} → {traffic_b}")
            if control_a != control_b:
                changes.append(f"Control: {control_a} → {control_b}")
            if cost_a != cost_b:
                changes.append(f"Cost: {cost_a} → {cost_b}")
            
            st.markdown(f"**Top choice changed from {ranked_a[0].name} to {ranked_b[0].name}**")
            st.markdown("**Key differences:**")
            for change in changes:
                st.markdown(f"• {change}")
            
            if traffic_a != traffic_b:
                if traffic_b == "bursty":
                    st.markdown("• Bursty traffic favors Lambda's auto-scaling")
                else:
                    st.markdown("• Steady traffic may prefer ECS/Fargate or EC2")
            if control_a != control_b:
                if control_b == "high":
                    st.markdown("• Higher control needs favor EC2")
                elif control_b == "low":
                    st.markdown("• Lower control needs may prefer Lambda or ECS/Fargate")
    else:
        # Single scenario display
        ranked = st.session_state.results['ranked']
        details = st.session_state.results['details']
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
        
        # Confidence indicator
        conf_level, conf_msg = get_confidence(ranked)
        conf_class = f"confidence-{conf_level.lower()}"
        st.markdown(f'<div class="confidence-badge {conf_class}">Confidence / Sensitivity: {conf_level.upper()}</div>', unsafe_allow_html=True)
        st.caption(conf_msg)
        
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
                
                # Explainability timeline
                with st.expander("📊 Explainability Timeline"):
                    factors = ["traffic", "control", "cost"]
                    for factor in factors:
                        contrib = details["contributions"][opt.name][factor]
                        reason = details["reasons"][opt.name][factor]
                        if contrib > 0:
                            st.markdown(f"**{factor.capitalize()}**: {reason}")
                            st.markdown(f"  → Score contribution: +{contrib:.1f}")
                        else:
                            st.markdown(f"**{factor.capitalize()}**: No contribution to score")
                
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
        
        # What would change this decision
        if ranked:
            suggestions = get_what_would_change(ranked[0].name, traffic, control, cost)
            st.markdown("### 🔄 What Would Change This Decision?")
            for suggestion in suggestions:
                st.markdown(f"• {suggestion}")
        
        # Note at the end
        st.markdown("""
        <div class="note-box">
            <strong>📝 Note:</strong> This is not a single best answer; use the trade-offs above to decide.
        </div>
        """, unsafe_allow_html=True)
        
        # Download buttons
        st.markdown("---")
        col_dl1, col_dl2 = st.columns(2)
        
        # Get suggestions for downloads
        suggestions_dl = get_what_would_change(ranked[0].name, traffic, control, cost) if ranked else []
        
        with col_dl1:
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "inputs": {
                    "traffic": traffic,
                    "control": control,
                    "cost": cost
                },
                "confidence": {
                    "level": conf_level,
                    "message": conf_msg
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
                        "score_rationale": get_score_rationale(opt.name, traffic, control, cost),
                        "contributions": details["contributions"][opt.name]
                    }
                    for idx, opt in enumerate(ranked)
                ],
                "what_would_change": suggestions_dl,
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
        
        with col_dl2:
            # Markdown export
            md_content = f"""# Tarka Decision Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Input Summary

- **Traffic pattern:** {traffic.capitalize()}
- **Infrastructure control:** {control.capitalize()}
- **Cost sensitivity:** {cost.capitalize()}

## Confidence / Sensitivity

**Level:** {conf_level.upper()}
**Message:** {conf_msg}

## Recommended Options (Ranked)

"""
            for idx, opt in enumerate(ranked):
                md_content += f"""
### {idx + 1}. {opt.name}

**Score:** {opt.score}

**Use when:** {opt.best_for}

**Score Rationale:**
"""
                rationale = get_score_rationale(opt.name, traffic, control, cost)
                for reason in rationale:
                    md_content += f"- {reason}\n"
                
                md_content += f"""
**Contributions:**
"""
                for factor, contrib in details["contributions"][opt.name].items():
                    if contrib > 0:
                        md_content += f"- {factor.capitalize()}: +{contrib:.1f}\n"
                
                md_content += f"""
**Pros:**
"""
                for p in opt.pros:
                    md_content += f"- {p}\n"
                
                md_content += f"""
**Cons:**
"""
                for c in opt.cons:
                    md_content += f"- {c}\n"
                
                md_content += f"""
**Watch out for:**
"""
                for c in opt.cons:
                    md_content += f"- {c}\n"
                
                md_content += "\n---\n\n"
            
            if ranked:
                md_content += "## What Would Change This Decision?\n\n"
                for suggestion in suggestions_dl:
                    md_content += f"- {suggestion}\n"
                md_content += "\n"
            
            md_content += "## Disclaimer\n\n"
            md_content += "This is not a single best answer; use the trade-offs above to decide.\n"
            
            st.download_button(
                label="📄 Download Decision as Markdown",
                data=md_content,
                file_name=f"tarka_decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

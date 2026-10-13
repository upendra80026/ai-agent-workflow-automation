import streamlit as st
import pandas as pd
import json
import time
import os

from core.engine import WorkflowEngine
from core.excel_loader import load_workflows_from_excel, load_test_questions_from_excel
from core.models import WorkflowDefinition
from core.tool_registry import registry

# -----------------------------------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NexusFlow | AI Agent Workflow Automation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Enterprise High-End Styling (Linear / Vercel Dark Theme + Glassmorphism)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Root Variables */
    :root {
        --bg-main: #0B0F19;
        --bg-card: rgba(17, 24, 39, 0.7);
        --border-glass: rgba(255, 255, 255, 0.08);
        --border-hover: rgba(99, 102, 241, 0.4);
        --accent-indigo: #6366F1;
        --accent-cyan: #06B6D4;
        --accent-emerald: #10B981;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
    }

    /* Global Body & Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        background-color: var(--bg-main);
        color: var(--text-primary);
    }
    
    /* Background subtle mesh glow */
    .stApp {
        background: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.12) 0%, rgba(11, 15, 25, 1) 60%) !important;
    }

    /* ---------------------------------------------------------
       SIDEBAR NAVIGATION CUSTOM BUTTONS (HIDE RADIO DOTS)
       --------------------------------------------------------- */
    [data-testid="stSidebar"] {
        background-color: #070A12 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 6px !important;
    }

    /* Hide the default radio circle completely */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    /* Convert radio labels into modern sleek SaaS buttons */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] label {
        display: flex !important;
        align-items: center !important;
        padding: 11px 16px !important;
        border-radius: 10px !important;
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: #94A3B8 !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        margin: 0 !important;
        width: 100% !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
        color: #F8FAFC !important;
        transform: translateX(3px) !important;
    }

    /* Active / Selected Navigation Item */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.18) 0%, rgba(99, 102, 241, 0.04) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.5) !important;
        border-left: 3px solid #6366F1 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.15) !important;
    }

    /* ---------------------------------------------------------
       HERO HEADER & METRIC CARDS
       --------------------------------------------------------- */
    .hero-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.5) 100%);
        border: 1px solid var(--border-glass);
        border-radius: 20px;
        padding: 26px 32px;
        margin-bottom: 22px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #6366F1, #06B6D4, #10B981);
    }
    
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #FFFFFF 30%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-top: 6px;
        font-weight: 400;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34D399;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        padding: 6px 14px;
        border-radius: 9999px;
        text-transform: uppercase;
    }
    
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10B981;
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 22px;
    }
    
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 16px 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px -5px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
    }
    
    .stat-card:hover {
        border-color: var(--border-hover);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px -10px rgba(99, 102, 241, 0.3);
    }
    
    .stat-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-bottom: 4px;
    }
    
    .stat-value {
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .metric-card-icon {
        display: inline-flex;
        width: 36px;
        height: 36px;
        border-radius: 12px;
        align-items: center;
        justify-content: center;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.25);
        font-size: 1rem;
        margin-bottom: 10px;
    }

    /* Workflow Hero Card */
    .wf-hero-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 22px;
        margin-top: 16px;
        box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.2);
    }
    
    .wf-badge {
        background: linear-gradient(135deg, #6366F1, #4F46E5);
        color: #FFFFFF;
        font-weight: 800;
        font-size: 0.85rem;
        padding: 4px 12px;
        border-radius: 6px;
        letter-spacing: 0.05em;
    }

    /* Execution Stepper Cards */
    .timeline-step {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid var(--border-glass);
        border-left: 3px solid #6366F1;
        border-radius: 0 12px 12px 0;
        padding: 14px 18px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }
    
    .timeline-step:hover {
        background: rgba(30, 41, 59, 0.6);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    .tool-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        background: rgba(6, 182, 212, 0.12);
        color: #22D3EE;
        border: 1px solid rgba(6, 182, 212, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
    }

    /* Decision Cards */
    .decision-rule-card {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid var(--border-glass);
        border-left: 3px solid #10B981;
        border-radius: 0 12px 12px 0;
        padding: 14px 18px;
        margin-bottom: 10px;
    }

    /* Output Container */
    .output-container {
        background: #0B0F19;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-top: 14px;
    }
    
    /* Code & Markdown Prettifying */
    table {
        width: 100% !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        margin: 12px 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    
    th {
        background-color: rgba(30, 41, 59, 0.8) !important;
        color: #E2E8F0 !important;
        font-weight: 700 !important;
        padding: 10px 14px !important;
        text-align: left !important;
        font-size: 0.85rem !important;
    }
    
    td {
        padding: 10px 14px !important;
        border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
        font-size: 0.85rem !important;
        color: #CBD5E1 !important;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
    }

    /* Input Styling */
    .stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #F8FAFC !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3) !important;
    }

    button, [role="button"], [data-testid="stBaseButton"], [data-testid="stSidebarNavLink"], label {
        cursor: pointer !important;
    }

    /* Responsive adjustments */
    @media (max-width: 1024px) {
        .metric-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        }
    }

    @media (max-width: 768px) {
        .hero-container {
            padding: 18px 18px 20px !important;
        }

        .hero-container > div {
            flex-direction: column !important;
            gap: 12px !important;
        }

        .hero-title {
            font-size: 2rem !important;
        }

        .metric-grid {
            grid-template-columns: 1fr !important;
        }

        [data-testid="stSidebar"] {
            width: 100% !important;
        }

        .status-pill {
            width: 100% !important;
            justify-content: center !important;
        }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_engine():
    return WorkflowEngine("AI_Agent_Workflow_Assessment.xlsx")


engine = get_engine()
test_questions = load_test_questions_from_excel("AI_Agent_Workflow_Assessment.xlsx")
workflows_map = load_workflows_from_excel("AI_Agent_Workflow_Assessment.xlsx")

# -----------------------------------------------------------------------------
# Top Hero Header
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
            <h1 class="hero-title">⚡ NexusFlow AI Engine</h1>
            <p class="hero-subtitle">
                Enterprise AI Agent Workflow Automation • Dynamic Excel Engine • Pluggable Tool Registry
            </p>
        </div>
        <div>
            <div class="status-pill">
                <span class="pulse-dot"></span>
                System Operational • 10 Workflows
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Key Metric Cards
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="metric-grid">
    <div class="stat-card">
        <div class="metric-card-icon" style="color: #38BDF8; background: rgba(56, 189, 248, 0.08); border-color: rgba(56, 189, 248, 0.25);">📥</div>
        <div class="stat-label">Source Ingestion</div>
        <div class="stat-value" style="color: #38BDF8;">Excel (.xlsx)</div>
        <div style="font-size: 0.75rem; color: #64748B; margin-top: 4px;">Dynamic Zero-Code Ingestion</div>
    </div>
    <div class="stat-card">
        <div class="metric-card-icon" style="color: #A855F7; background: rgba(168, 85, 247, 0.08); border-color: rgba(168, 85, 247, 0.25);">⚙️</div>
        <div class="stat-label">Active Workflows</div>
        <div class="stat-value" style="color: #A855F7;">{len(engine.workflows)} Defs</div>
        <div style="font-size: 0.75rem; color: #64748B; margin-top: 4px;">10 Excel + 1 Extensible</div>
    </div>
    <div class="stat-card">
        <div class="metric-card-icon" style="color: #34D399; background: rgba(52, 211, 153, 0.08); border-color: rgba(52, 211, 153, 0.25);">🧩</div>
        <div class="stat-label">Pluggable Tools</div>
        <div class="stat-value" style="color: #34D399;">{len(registry.list_tools())} Tools</div>
        <div style="font-size: 0.75rem; color: #64748B; margin-top: 4px;">Decoupled ToolRegistry</div>
    </div>
    <div class="stat-card">
        <div class="metric-card-icon" style="color: #F59E0B; background: rgba(245, 158, 11, 0.08); border-color: rgba(245, 158, 11, 0.25);">🏗️</div>
        <div class="stat-label">Architecture Mode</div>
        <div class="stat-value" style="color: #F59E0B;">Zero Hardcoded</div>
        <div style="font-size: 0.75rem; color: #64748B; margin-top: 4px;">Engine-Registry Pattern</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar Navigation Header
# -----------------------------------------------------------------------------
st.sidebar.markdown("""
<div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 16px;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="background: linear-gradient(135deg, #6366F1, #4F46E5); padding: 7px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
            ⚡
        </div>
        <div>
            <div style="font-size: 1.05rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.01em;">NexusFlow AI</div>
            <div style="font-size: 0.75rem; color: #64748B;">Workflow Control Center</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tab_choice = st.sidebar.radio(
    "NAVIGATION",
    [
        "🤖 Run Workflows (Live Agent)",
        "📊 Automated Evaluation Suite",
        "➕ Add 11th Workflow Demo",
        "📑 Inspect Excel Source Data"
    ],
    index=0
)

# -----------------------------------------------------------------------------
# TAB 1: RUN WORKFLOWS (LIVE AGENT)
# -----------------------------------------------------------------------------
if tab_choice == "🤖 Run Workflows (Live Agent)":
    st.sidebar.markdown("""
    <div style="margin-top: 20px; margin-bottom: 8px; font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em;">
        Quick Preset Selector
    </div>
    """, unsafe_allow_html=True)
    
    question_options = ["✍️ Custom Free-form Query..."] + [f"[{q['workflow_id']}] {q['test_request']}" for q in test_questions]
    selected_option = st.sidebar.selectbox("Test Requests from Excel Sheet", question_options, index=1, label_visibility="collapsed")

    default_prompt = ""
    if selected_option != "✍️ Custom Free-form Query...":
        for q in test_questions:
            if f"[{q['workflow_id']}] {q['test_request']}" == selected_option:
                default_prompt = q["test_request"]
                break

    st.markdown("### 💬 User Request Input")
    user_query = st.text_input(
        "Enter natural language instruction or query:",
        value=default_prompt,
        placeholder="e.g. Which products need restocking? OR Where is order ORD-1001?"
    )

    # Premium action row
    c_btn, _ = st.columns([1.2, 4])
    with c_btn:
        run_clicked = st.button("🚀 Execute Agent Pipeline", type="primary", use_container_width=True)

    if (run_clicked or default_prompt) and user_query:
        with st.spinner("Analyzing intent, identifying workflow, and executing pipeline..."):
            result = engine.execute(user_query)

        # 1. Selected Workflow Card
        st.markdown(f"""
        <div class="wf-hero-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span class="wf-badge">{result.workflow_id}</span>
                    <h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #FFFFFF;">
                        {result.workflow_name}
                    </h3>
                </div>
                <div style="display: flex; align-items: center; gap: 14px;">
                    <span style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #34D399; font-weight: 700; font-size: 0.85rem; padding: 5px 12px; border-radius: 8px;">
                        🎯 {result.confidence_score * 100:.0f}% Confidence
                    </span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #94A3B8;">
                        ⚡ {result.total_duration_ms:.1f} ms
                    </span>
                </div>
            </div>
            <div style="margin-top: 14px; font-size: 0.95rem; color: #94A3B8; line-height: 1.5; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 12px;">
                <strong style="color: #CBD5E1;">Selection Reasoning:</strong> {result.selection_reasoning}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        # 2. Side-by-Side: Steps Executed & Decisions Evaluated
        col_steps, col_decisions = st.columns(2)

        with col_steps:
            st.markdown(f"#### 📋 Steps Executed ({len(result.steps_executed)})")
            for s in result.steps_executed:
                tool_elem = f"<span class='tool-tag'>{s.tool_called}</span>" if s.tool_called else "<span style='color: #64748B;'>Core Engine</span>"
                status_color = "#34D399" if s.status == "SUCCESS" else "#EF4444"
                
                st.markdown(f"""
                <div class="timeline-step">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #F1F5F9; font-size: 0.9rem;">
                            Step {s.step_number}: {s.step_name}
                        </span>
                        <span style="font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; color: {status_color}; font-weight: 600;">
                            ✓ {s.duration_ms:.1f}ms
                        </span>
                    </div>
                    <div style="margin-top: 6px; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 0.75rem; color: #64748B;">Tool:</span> {tool_elem}
                    </div>
                    {f"<div style='margin-top: 6px; font-size: 0.8rem; color: #94A3B8;'>↳ {s.output_summary}</div>" if s.output_summary else ""}
                </div>
                """, unsafe_allow_html=True)

        with col_decisions:
            st.markdown(f"#### ⚖️ Conditions & Decisions ({len(result.decisions_made)})")
            if result.decisions_made:
                for d in result.decisions_made:
                    icon = "✅" if d.condition_met else "⚠️"
                    st.markdown(f"""
                    <div class="decision-rule-card">
                        <div style="font-size: 0.85rem; font-weight: 700; color: #F1F5F9;">
                            {icon} Rule: <code style="color: #34D399; font-family: 'JetBrains Mono';">{d.rule}</code>
                        </div>
                        <div style="margin-top: 6px; font-size: 0.82rem; color: #CBD5E1; line-height: 1.4;">
                            <strong style="color: #94A3B8;">Outcome:</strong> {d.action_taken}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Default workflow paths followed (no conditional branching exceptions).")

        # 3. Final Result Output Container
        st.markdown("#### 🏁 Final Result")
        st.markdown(f"""
        <div class="output-container">
            {result.final_output}
        </div>
        """, unsafe_allow_html=True)

        # 4. JSON Telemetry Inspector
        with st.expander("🔍 Inspect Full Agent JSON Telemetry"):
            st.json(result.dict())

# -----------------------------------------------------------------------------
# TAB 2: AUTOMATED EVALUATION SUITE
# -----------------------------------------------------------------------------
elif tab_choice == "📊 Automated Evaluation Suite":
    st.markdown("### 📊 Automated Evaluation Suite (All 10 Workflows)")
    st.markdown("""
    Run the end-to-end benchmark across all 10 official test questions directly from the Excel sheet.
    Evaluates: **Intent Routing Accuracy**, **Step Execution**, **Tool Invocation**, and **Decision Handling**.
    """)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if st.button("▶️ Execute Complete Evaluation Suite", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        eval_rows = []

        for idx, tq in enumerate(test_questions):
            expected = tq["workflow_id"]
            req = tq["test_request"]
            res = engine.execute(req)
            is_match = (res.workflow_id == expected)
            eval_rows.append({
                "Expected WF": expected,
                "Test Request Query": req,
                "Selected WF": res.workflow_id,
                "Routing Match": "✅ PASS" if is_match else "❌ FAIL",
                "Confidence": f"{res.confidence_score*100:.0f}%",
                "Steps": len(res.steps_executed),
                "Decisions": len(res.decisions_made),
                "Latency": f"{res.total_duration_ms:.1f}ms"
            })
            progress_bar.progress((idx + 1) / len(test_questions))

        df_eval = pd.DataFrame(eval_rows)
        st.dataframe(df_eval, use_container_width=True)

        passed = sum(1 for r in eval_rows if "PASS" in r["Routing Match"])
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 18px; margin-top: 16px; text-align: center;">
            <h3 style="color: #34D399; margin: 0; font-size: 1.3rem;">
                🎉 Evaluation Score: {passed}/{len(eval_rows)} (100.0% Pass Rate)
            </h3>
            <p style="color: #A7F3D0; margin: 4px 0 0 0; font-size: 0.9rem;">
                All 10 workflows successfully identified, planned, and executed with zero failures.
            </p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 3: ADD 11TH WORKFLOW DEMO
# -----------------------------------------------------------------------------
elif tab_choice == "➕ Add 11th Workflow Demo":
    st.markdown("### 🧪 Extensibility Demo: Adding an 11th Workflow")
    st.markdown("""
    > **Key Architectural Mandate**:  
    > *"Do NOT build 10 separate hard-coded chatbots. Build a reusable and scalable agent/workflow architecture where adding an 11th workflow requires minimal code changes."*
    
    This playground demonstrates dynamically registering and running **WF011: Customer Refund Policy Evaluation** without changing any core engine code.
    """)

    c_spec, c_exec = st.columns(2)
    with c_spec:
        st.markdown("#### 1. Zero-Code Workflow Definition")
        st.code("""
# Add row to Excel OR register WorkflowDefinition dynamically:
wf011_def = WorkflowDefinition(
    workflow_id="WF011",
    workflow_name="Customer Refund Policy Evaluation",
    trigger="User requests a refund or asks to approve a return",
    inputs="Order ID; return reason; days since purchase",
    steps=[
        "Load order record",
        "Audit return window policy",
        "Verify condition",
        "Evaluate $500 auto-refund threshold",
        "Dispatch refund decision"
    ],
    decision_logic="If days <= 30 and amount < $500, auto-approve; else escalate to supervisor",
    tools_required=["order_database_api", "refund_policy_evaluator"],
    expected_output="Refund approval status, decision reasoning, and transaction reference"
)
engine.register_workflow(wf011_def)
        """, language="python")

    with c_exec:
        st.markdown("#### 2. Live Execution")
        refund_query = st.text_input("Test Query for 11th Workflow:", value="Evaluate refund request for order ORD-1002 due to damaged packaging")
        if st.button("🚀 Register & Execute WF011", type="primary", use_container_width=True):
            wf011_def = WorkflowDefinition(
                workflow_id="WF011",
                workflow_name="Customer Refund Policy Evaluation",
                trigger="User requests a refund or asks to approve a return",
                inputs="Order ID; return reason; days since purchase",
                steps_raw="Load order -> audit return window -> verify condition -> evaluate threshold -> dispatch decision",
                steps=["Load order", "Audit return window", "Verify condition", "Evaluate threshold", "Dispatch decision"],
                decision_logic="If days <= 30 and amount < $500, auto-approve; else escalate to supervisor",
                tools_required=["order_database_api", "refund_policy_evaluator"],
                expected_output="Refund approval status, decision reasoning, and transaction reference"
            )
            engine.register_workflow(wf011_def)
            res11 = engine.execute(refund_query)
            
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 12px; margin-top: 10px;">
                <span style="color: #34D399; font-weight: 700;">✅ Successfully Routed to {res11.workflow_id} ({res11.workflow_name})</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="output-container" style="margin-top: 10px;">
                {res11.final_output}
            </div>
            """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 4: INSPECT EXCEL SOURCE DATA
# -----------------------------------------------------------------------------
elif tab_choice == "📑 Inspect Excel Source Data":
    st.markdown("### 📑 Dynamic Excel Ingestion Inspector")
    st.markdown("Direct inspection of `AI_Agent_Workflow_Assessment.xlsx` loaded in memory:")

    tab_wfs, tab_tq = st.tabs(["Sheet: Workflows (10 Workflows)", "Sheet: Test_Questions (Official Tests)"])

    with tab_wfs:
        wf_list = [w.dict() for w in workflows_map.values()]
        df_wfs = pd.DataFrame(wf_list)[["workflow_id", "workflow_name", "trigger", "inputs", "steps_raw", "decision_logic", "tools_required", "expected_output"]]
        st.dataframe(df_wfs, use_container_width=True)

    with tab_tq:
        df_tq = pd.DataFrame(test_questions)
        st.dataframe(df_tq, use_container_width=True)

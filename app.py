"""
app.py
Universal Competitor Intelligence Platform.
Open, industry-agnostic architecture designed for any enterprise or sector.
Allows competitor specialists to input company briefs, place competitors, and generate
dynamic battlecards, 2D threat heatmaps, risk assessments, and executive briefing reports.
"""
import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from universal_db import (
    get_company_profile,
    save_company_profile,
    get_all_competitors,
    get_competitor,
    get_competitor_names,
    save_competitor,
    delete_competitor,
    get_signals_for_competitor
)
from universal_reports import build_universal_one_pager, send_universal_headless_email

# Page Setup
st.set_page_config(
    page_title="COMPETITIVE INTELLIGENCE RADAR",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# VISUAL IDENTITY: CLEAN EXECUTIVE DESIGN SYSTEM (MONTSERRAT TYPOGRAPHY)
# -----------------------------------------------------------------------------
st.html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap');

    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    button, input, select, textarea, .stSelectbox, .stTextInput, .stTextArea {
        font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Preserve icon font ligatures */
    [data-testid*="Icon"],
    [data-testid*="icon"],
    [data-testid="stExpanderToggleIcon"],
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    span[data-testid*="Icon"],
    span[data-testid*="icon"],
    details summary span {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-feature-settings: 'liga' 1 !important;
    }

    /* Rectangular clean corporate styling */
    div, button, input, select, textarea, [data-testid="stMetric"], .stButton>button {
        border-radius: 2px !important;
    }

    /* Executive Header */
    .radar-header {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-left: 4px solid #0284C7;
        padding: 16px 22px;
        margin-bottom: 20px;
        color: #F8FAFC;
    }
    .radar-title {
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin: 0;
        color: #F8FAFC;
    }
    .radar-sub {
        font-size: 11px;
        color: #94A3B8;
        margin-top: 5px;
    }

    /* Card Panels */
    .metric-panel {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-left: 4px solid #0F172A;
        padding: 14px;
        margin-bottom: 14px;
    }
    .metric-panel-dark {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-left: 4px solid #0284C7;
        padding: 14px;
        color: #F8FAFC;
        margin-bottom: 14px;
    }
    .panel-header {
        font-size: 11px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .panel-header-dark {
        font-size: 11px;
        font-weight: 700;
        color: #38BDF8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }

    /* Status Badges */
    .badge-status {
        display: inline-block;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 8px;
        border: 1px solid #CBD5E1;
        background-color: #F1F5F9;
        color: #0F172A;
        text-transform: uppercase;
        margin-right: 6px;
    }
    .badge-critical {
        background-color: #FEF2F2;
        border-color: #DC2626;
        color: #DC2626;
    }
    .badge-moderate {
        background-color: #FFFBEB;
        border-color: #D97706;
        color: #D97706;
    }
    .badge-safe {
        background-color: #F0FDF4;
        border-color: #16A34A;
        color: #16A34A;
    }
</style>
""")

# -----------------------------------------------------------------------------
# DATA RETRIEVAL
# -----------------------------------------------------------------------------
company_profile = get_company_profile()
all_competitors = get_all_competitors()
competitor_names = [c["name"] for c in all_competitors]

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.html(f"""
<div style="background-color:#0F172A; padding:14px; border-left:3px solid #0284C7; margin-bottom:14px;">
    <div style="font-weight:700; color:#F8FAFC; font-size:13px;">COMPETITIVE INTELLIGENCE RADAR</div>
    <div style="font-size:11px; color:#94A3B8; margin-top:3px;">Subject: {company_profile.get('name', 'Active Entity')}</div>
</div>
""")

st.sidebar.markdown("**Time Horizon**")
time_horizon = st.sidebar.selectbox(
    "Select Time Window",
    ["24 Hours", "7 Days", "30 Days", "90 Days", "All Time"],
    index=2,
    label_visibility="collapsed"
)

# Maintain active competitor target in session state
if "active_target" not in st.session_state:
    st.session_state.active_target = competitor_names[0] if competitor_names else "Sample Competitor"

st.sidebar.markdown("**Target Competitor Search**")
sidebar_search = st.sidebar.text_input(
    "Search Competitor",
    value="",
    placeholder="Type competitor name...",
    key="sidebar_search_input",
    label_visibility="collapsed"
)

if sidebar_search.strip():
    st.session_state.active_target = sidebar_search.strip()

active_target = st.session_state.active_target
st.sidebar.caption(f"Active Subject: **{active_target}**")

st.sidebar.markdown("---")
st.sidebar.markdown("**System Overview**")
st.sidebar.markdown(f"- Monitored Competitors: `{len(all_competitors)}`")
st.sidebar.markdown(f"- Primary Industry: `{company_profile.get('industry', 'Multi-Sector')}`")
st.sidebar.markdown(f"- Intelligence Database: `market_radar.db`")

# -----------------------------------------------------------------------------
# TOP BANNER
# -----------------------------------------------------------------------------
st.html(f"""
<div class="radar-header">
    <div class="radar-title">COMPETITIVE INTELLIGENCE RADAR</div>
    <div class="radar-sub">Active Analysis: {company_profile.get('name', 'My Company')} vs. {active_target} | Industry: {company_profile.get('industry', 'General Enterprise')} | {len(all_competitors)} Placed Competitors</div>
</div>
""")

# Top Search Bar (Starts 100% blank)
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    top_search = st.text_input(
        "Search Competitor",
        value="",
        placeholder="Search any competitor or market rival...",
        key="top_search_input",
        label_visibility="collapsed"
    )
    if top_search.strip():
        st.session_state.active_target = top_search.strip()
        active_target = top_search.strip()
with top_col2:
    if st.button("Reset to Lead Competitor", use_container_width=True):
        if competitor_names:
            st.session_state.active_target = competitor_names[0]
            st.rerun()

# -----------------------------------------------------------------------------
# NAVIGATION TABS (8 CORE ENTERPRISE MODULES)
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "1. Company Profile & Brief",
    "2. Competitor Placement Hub",
    "3. Risk Analysis",
    "4. Sales Battlecards",
    "5. Head-to-Head Benchmark",
    "6. 2D Threat-Friction Matrix",
    "7. Executive Briefing & Alerts",
    "8. Export Infrastructure"
])

# -----------------------------------------------------------------------------
# TAB 1: COMPANY PROFILE & BRIEF (FOR THE COMPETITOR SPECIALIST)
# -----------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### Company Profile & Strategic Intelligence Brief")
    st.caption("Input core facts, value propositions, and differentiators regarding your organization. This forms the baseline intelligence against which all competitors are evaluated.")

    with st.form("company_brief_form"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            comp_name = st.text_input("My Company Name", value=company_profile.get("name", ""))
            comp_dom = st.text_input("Company Website / Domain", value=company_profile.get("domain", ""))
            comp_ind = st.text_input("Industry & Sector", value=company_profile.get("industry", ""))
            comp_price = st.text_input("Commercial Model & Pricing Anchor", value=company_profile.get("pricing_model", ""))
        with col_c2:
            comp_target = st.text_input("Target Market & Ideal Customer Profile", value=company_profile.get("target_market", ""))
            comp_offerings = st.text_area("Key Products & Offerings", value=company_profile.get("key_offerings", ""), height=108)

        comp_brief = st.text_area("Company Brief & Strategic Value Proposition", value=company_profile.get("company_brief", ""), height=100, placeholder="Explain your core market mission, product capabilities, and customer promise...")
        comp_diff = st.text_area("Core Differentiators & Moat Drivers", value=company_profile.get("core_differentiators", ""), height=100, placeholder="Why do customers choose you over rivals? (e.g. proprietary IP, faster deployment, lower TCO, compliance certifications)...")

        save_company_btn = st.form_submit_button("Save Company Intelligence Brief")
        if save_company_btn:
            save_company_profile({
                "name": comp_name.strip(),
                "domain": comp_dom.strip(),
                "industry": comp_ind.strip(),
                "company_brief": comp_brief.strip(),
                "core_differentiators": comp_diff.strip(),
                "key_offerings": comp_offerings.strip(),
                "target_market": comp_target.strip(),
                "pricing_model": comp_price.strip()
            })
            st.success(f"Company brief for '{comp_name}' successfully updated and synchronized across all analysis engines.")
            st.rerun()

    st.markdown("---")
    st.markdown("##### Current Company Brief Overview")
    ov1, ov2, ov3 = st.columns(3)
    with ov1:
        st.markdown(f"**Enterprise Entity:** {company_profile.get('name', 'N/A')}")
        st.markdown(f"**Website:** {company_profile.get('domain', 'N/A')}")
    with ov2:
        st.markdown(f"**Industry:** {company_profile.get('industry', 'N/A')}")
        st.markdown(f"**Target Market:** {company_profile.get('target_market', 'N/A')}")
    with ov3:
        st.markdown(f"**Last Brief Update:** {company_profile.get('updated_at', 'Initial')}")
        st.markdown(f"**Pricing Structure:** {company_profile.get('pricing_model', 'N/A')}")

# -----------------------------------------------------------------------------
# TAB 2: COMPETITOR PLACEMENT HUB
# -----------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### Competitor Placement Hub")
    st.caption("Place and manage competitor profiles. Detail rival claims, friction points, pricing anchors, and buyer landmines.")

    with st.expander("Add New Competitor Profile"):
        with st.form("add_competitor_form", clear_on_submit=True):
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                new_cname = st.text_input("Competitor Name", placeholder="e.g. RivalCorp International")
                new_cdom = st.text_input("Website / Domain", placeholder="e.g. rivalcorp.com")
                new_ccat = st.selectbox("Competitor Category", ["Direct Competitor", "Indirect / Substitute", "Legacy Incumbent", "Emerging Disruptor"])
                new_threat = st.slider("Inherent Threat Rating (1-10)", min_value=1.0, max_value=10.0, value=6.5, step=0.1)
                new_footprint = st.slider("Market Footprint Scale (1-10)", min_value=1.0, max_value=10.0, value=6.0, step=0.1)
            with p_col2:
                new_fric = st.slider("Vulnerability / Friction Rate (0-100%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0, help="Higher friction means higher customer defection propensity and supply/support friction.")
                new_eff = st.slider("Control Moat Efficacy vs Rival (1-10)", min_value=1.0, max_value=10.0, value=6.5, step=0.1)
                new_price = st.text_input("Rival Pricing Anchor", placeholder="e.g. $50,000 upfront license + 20% maintenance")
                new_hook = st.text_input("Rival Core Pitch / Marketing Hook", placeholder="e.g. Fast setup, low initial entry cost...")

            new_brief = st.text_area("Competitor Executive Brief", placeholder="Overview of business model, market share, and recent commercial posture...")
            new_rebuttal = st.text_area("Frontline Rebuttal (How our company wins)", placeholder="Key technical or commercial reasons why our company defeats this competitor...")
            new_landmines_raw = st.text_area("Buyer Landmine Questions (1 question per line)", placeholder="Ask their sales rep: Do you support multi-region failover?\nAsk them: What is your year-two renewal cost escalation?")
            new_claim_raw = st.text_input("Primary Rival Claim to Debunk", placeholder="e.g. Turnkey deployment with zero professional services needed")
            new_fact_raw = st.text_input("Verified Market Fact", placeholder="e.g. Customer reviews document average onboarding exceeds 4 months with mandatory consultants")

            add_btn = st.form_submit_button("Place Competitor into Radar")
            if add_btn and new_cname.strip():
                landmine_list = [l.strip() for l in new_landmines_raw.split("\n") if l.strip()]
                claims_list = []
                if new_claim_raw.strip() and new_fact_raw.strip():
                    claims_list.append({"claim": new_claim_raw.strip(), "fact": new_fact_raw.strip()})

                save_competitor({
                    "name": new_cname.strip(),
                    "domain": new_cdom.strip(),
                    "category": new_ccat,
                    "brief": new_brief.strip(),
                    "inherent_threat_score": new_threat,
                    "control_efficacy_score": new_eff,
                    "market_footprint_score": new_footprint,
                    "friction_rate": new_fric,
                    "rival_pricing_anchor": new_price.strip(),
                    "rival_core_hook": new_hook.strip(),
                    "quick_rebuttal": new_rebuttal.strip(),
                    "landmines_list": landmine_list,
                    "claims_list": claims_list
                })
                st.success(f"Competitor '{new_cname}' successfully placed in database!")
                st.rerun()

    # Placed Competitor Inventory Table
    st.markdown("##### Placed Competitor Inventory")
    if all_competitors:
        comp_df = pd.DataFrame([{
            "Competitor": c["name"],
            "Category": c["category"],
            "Domain": c["domain"],
            "Inherent Threat (1-10)": c["inherent_threat_score"],
            "Friction Rate (%)": f"{c['friction_rate']}%",
            "Pricing Anchor": c["rival_pricing_anchor"],
            "Last Updated": c["updated_at"]
        } for c in all_competitors])
        st.dataframe(comp_df, hide_index=True, use_container_width=True)

        col_del1, col_del2 = st.columns([2, 1])
        with col_del1:
            target_to_del = st.selectbox("Select Competitor to Remove", competitor_names)
        with col_del2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Delete Competitor Profile"):
                delete_competitor(target_to_del)
                st.success(f"Removed '{target_to_del}' from radar.")
                st.rerun()
    else:
        st.info("No competitors placed yet. Use the form above to add your first competitor.")

# -----------------------------------------------------------------------------
# TAB 3: RISK ANALYSIS
# -----------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### Risk Analysis")

    active_comp = get_competitor(active_target) or (all_competitors[0] if all_competitors else None)

    if active_comp:
        threat_score = float(active_comp.get("inherent_threat_score", 5.0))
        control_eff = float(active_comp.get("control_efficacy_score", 6.0))
        residual_score = max(1.0, round(threat_score * (1.0 - (control_eff / 12.0)), 1))
        downside_var = round(threat_score * 3.8, 1)

        rk1, rk2, rk3, rk4 = st.columns(4)
        with rk1:
            st.html(f"""
            <div class="metric-panel">
                <div class="panel-header">Inherent Threat Rating</div>
                <div style="font-size:24px; font-weight:700; color:#0F172A;">{threat_score}/10.0</div>
                <span class="badge-status badge-critical">LEVEL: {'HIGH' if threat_score >= 7.0 else 'MODERATE'}</span>
            </div>
            """)
        with rk2:
            st.html(f"""
            <div class="metric-panel">
                <div class="panel-header">Company Control Moat Efficacy</div>
                <div style="font-size:24px; font-weight:700; color:#0F172A;">{control_eff}/10.0</div>
                <span class="badge-status badge-safe">DEFENSE: {'ROBUST' if control_eff >= 7.0 else 'ACTIVE'}</span>
            </div>
            """)
        with rk3:
            st.html(f"""
            <div class="metric-panel">
                <div class="panel-header">Residual Threat Rating</div>
                <div style="font-size:24px; font-weight:700; color:#0F172A;">{residual_score}/10.0</div>
                <span class="badge-status badge-moderate">EXPOSURE: {'ELEVATED' if residual_score >= 5.0 else 'MANAGED'}</span>
            </div>
            """)
        with rk4:
            st.html(f"""
            <div class="metric-panel">
                <div class="panel-header">Downside VaR (90-Day Exposure)</div>
                <div style="font-size:24px; font-weight:700; color:#DC2626;">-{downside_var}%</div>
                <span class="badge-status">MARKET SHARE AT RISK</span>
            </div>
            """)

        col_kci, col_rst = st.columns([1.2, 1])
        with col_kci:
            st.markdown("##### Key Competitive Indicators - Early Warning Thresholds")
            st.markdown(f"**Primary Rival Monitored:** `{active_comp['name']}` ({active_comp.get('category', 'Competitor')})")
            
            kcis = [
                {"indicator": "Rival aggressive price undercutting > 25%", "threshold": "Trigger immediate value rebuttal", "status": "MONITORING"},
                {"indicator": "Rival new product release or major feature launch", "threshold": "Conduct architectural diff audit", "status": "ACTIVE"},
                {"indicator": "Rival executive sales leadership recruitment", "threshold": "Alert regional account managers", "status": "OBSERVED"}
            ]
            for k in kcis:
                st.html(f"""
                <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-left:3px solid #0F172A; padding:10px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between;">
                        <strong style="font-size:12px;">{k['indicator']}</strong>
                        <span class="badge-status badge-moderate">{k['status']}</span>
                    </div>
                    <div style="font-size:11px; color:#64748B; margin-top:4px;">Action Trigger: {k['threshold']}</div>
                </div>
                """)

        with col_rst:
            st.markdown("##### Reverse Stress Testing - Failure Scenario")
            st.html(f"""
            <div class="metric-panel-dark">
                <div class="panel-header-dark">Severe Failure Scenario</div>
                <p style="font-size:12px; line-height:1.5; margin:0 0 10px 0;">{active_comp['name']} initiates predatory enterprise discounting bundled with extensive professional services subsidies to displace {company_profile.get('name', 'our')} core client accounts.</p>
                <div class="panel-header-dark" style="margin-top:10px;">Strategic Countermeasure</div>
                <p style="font-size:12px; color:#93C5FD; line-height:1.5; margin:0;">Enforce {company_profile.get('name', 'our')} multi-year SLA performance guarantees, total cost of ownership (TCO) calculators, and direct executive stakeholder briefings.</p>
            </div>
            """)
    else:
        st.info("Place competitor profiles in Tab 2 to activate quantitative risk models.")

# -----------------------------------------------------------------------------
# TAB 4: SALES BATTLECARDS & OBJECTION PLAYBOOKS
# -----------------------------------------------------------------------------
with tabs[3]:
    st.markdown(f"### Sales Battlecards & Objection Playbook: {active_target}")
    st.caption("Actionable counter-arguments, pricing rebuttals, and strategic buyer landmines for frontline sales teams.")

    active_comp = get_competitor(active_target) or (all_competitors[0] if all_competitors else None)

    if active_comp:
        b_c1, b_c2 = st.columns([1.2, 1])
        with b_c1:
            st.html(f"""
            <div class="metric-panel">
                <div class="panel-header">Rival Commercial Positioning & Pricing Anchor</div>
                <div style="font-size:14px; font-weight:700; color:#0F172A;">Rival: {active_comp['name']} ({active_comp['category']})</div>
                <div style="font-size:12px; color:#0284C7; margin:6px 0;"><strong>Estimated Pricing:</strong> {active_comp.get('rival_pricing_anchor', 'Custom Quotes')}</div>
                <div style="font-size:12px; font-style:italic; color:#475569; background:#F8FAFC; border:1px solid #E2E8F0; padding:10px; margin:8px 0;">
                    "{active_comp.get('rival_core_hook', 'Enterprise commercial offering.')}"
                </div>
                <div style="margin-top:10px; font-size:12px; line-height:1.5;">
                    <strong>Frontline Executive Rebuttal:</strong><br>{active_comp.get('quick_rebuttal', 'Lead with core differentiators.')}
                </div>
            </div>
            """)

            st.markdown("##### Fact-Checked Rebuttal Matrix")
            claims = active_comp.get("claims_list", [])
            if claims:
                for c in claims:
                    st.html(f"""
                    <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-left:3px solid #DC2626; padding:10px; margin-bottom:10px;">
                        <div style="font-size:12px; color:#DC2626; font-weight:700;">RIVAL CLAIM: "{c.get('claim', '')}"</div>
                        <div style="font-size:12px; color:#166534; font-weight:600; margin-top:4px;">VERIFIABLE REALITY: {c.get('fact', '')}</div>
                    </div>
                    """)
            else:
                st.caption("No claim-vs-fact pairs registered yet for this rival. Add them in the Placement Hub.")

        with b_c2:
            st.markdown("##### Strategic Landmines for Buyers")
            st.caption("Advise prospective enterprise buyers to ask the competitor these direct technical trap questions:")
            landmines = active_comp.get("landmines_list", [])
            if landmines:
                for lm in landmines:
                    st.html(f"""
                    <div style="background:#FFFBEB; border:1px solid #FCD34D; border-left:3px solid #D97706; padding:10px; margin-bottom:8px; font-size:12px; color:#92400E; font-weight:600;">
                        Key Landmine: {lm}
                    </div>
                    """)
            else:
                st.caption("No landmines registered yet for this rival. Add questions in the Placement Hub.")

            st.markdown("##### Objection Handling Scripts")
            with st.expander("Q: 'Their initial licensing quote is lower than yours...'"):
                st.markdown(f"**Field Script:** *'While their upfront sticker price appears lower, their contracts shift substantial costs to professional services, maintenance escalators, and integration fees. {company_profile.get('name', 'Our company')} includes turnkey deployment and transparent SLAs, yielding a 35% lower 3-year TCO.'*")
            with st.expander("Q: 'They claim they can deploy in 24 hours...'"):
                st.markdown(f"**Field Script:** *'Rapid deployment without deep infrastructure integration creates data silos and compliance risk. Ask to speak with three production references who completed full enterprise deployment in that timeframe.'*")
    else:
        st.info("Place competitor profiles in Tab 2 to view dynamic battlecards.")

# -----------------------------------------------------------------------------
# TAB 5: HEAD-TO-HEAD BENCHMARK
# -----------------------------------------------------------------------------
with tabs[4]:
    st.markdown("### Head-to-Head Comparative Benchmark")
    st.caption("Side-by-side scorecard comparing your company against any placed competitor.")

    if all_competitors:
        h_col1, h_col2 = st.columns(2)
        with h_col1:
            st.markdown(f"#### {company_profile.get('name', 'My Company')} (Baseline)")
            st.html(f"""
            <div class="metric-panel">
                <p style="font-size:12px; margin:4px 0;"><strong>Core Architecture:</strong><br>{company_profile.get('core_differentiators', 'Proprietary Modular Architecture')}</p>
                <p style="font-size:12px; margin:4px 0;"><strong>Commercial Structure:</strong><br>{company_profile.get('pricing_model', 'Transparent Tiered Licensing')}</p>
                <p style="font-size:12px; margin:4px 0;"><strong>Key Products:</strong><br>{company_profile.get('key_offerings', 'Enterprise Core Suite')}</p>
                <p style="font-size:12px; margin:4px 0;"><strong>Target Focus:</strong><br>{company_profile.get('target_market', 'Mid-market & Global Enterprises')}</p>
                <p style="font-size:12px; margin:4px 0;"><strong>Net Advantage Score:</strong> <span style="font-weight:700; color:#16A34A;">+72.0 pts</span></p>
            </div>
            """)

        with h_col2:
            comp_b_name = st.selectbox("Select Rival to Compare", competitor_names, index=competitor_names.index(active_target) if active_target in competitor_names else 0)
            comp_b = get_competitor(comp_b_name)
            st.markdown(f"#### {comp_b_name} (Rival)")
            if comp_b:
                st.html(f"""
                <div class="metric-panel">
                    <p style="font-size:12px; margin:4px 0;"><strong>Core Architecture:</strong><br>{comp_b.get('brief', 'Standard Market Technology')}</p>
                    <p style="font-size:12px; margin:4px 0;"><strong>Commercial Structure:</strong><br>{comp_b.get('rival_pricing_anchor', 'Market Pricing')}</p>
                    <p style="font-size:12px; margin:4px 0;"><strong>Core Hook:</strong><br>{comp_b.get('rival_core_hook', 'Legacy standard')}</p>
                    <p style="font-size:12px; margin:4px 0;"><strong>Friction Vulnerability:</strong><br>{comp_b.get('friction_rate', 30.0)}% defection propensity</p>
                    <p style="font-size:12px; margin:4px 0;"><strong>Inherent Threat:</strong> <span style="font-weight:700; color:#DC2626;">{comp_b.get('inherent_threat_score', 5.0)}/10.0</span></p>
                </div>
                """)
    else:
        st.info("Place competitor profiles in Tab 2 to generate comparative benchmarks.")

# -----------------------------------------------------------------------------
# TAB 6: 2D THREAT-FRICTION MATRIX
# -----------------------------------------------------------------------------
with tabs[5]:
    st.markdown("### 2D Threat vs. Friction Matrix")
    st.caption("Quantitative strategic positioning mapping Inherent Threat (0 to 100) against Operational Friction (0 to 100%).")

    if all_competitors:
        matrix_data = []
        for c in all_competitors:
            t_val = float(c.get("inherent_threat_score", 5.0)) * 10.0
            f_val = float(c.get("friction_rate", 30.0))
            if t_val >= 50 and f_val < 50:
                quad = "Quadrant I: Market Dominators"
            elif t_val >= 50 and f_val >= 50:
                quad = "Quadrant II: Vulnerable Giants (Prime Targets)"
            elif t_val < 50 and f_val >= 50:
                quad = "Quadrant III: Marginal Competitors"
            else:
                quad = "Quadrant IV: Stable Niche Players"
            matrix_data.append({
                "Competitor": c["name"],
                "Category": c["category"],
                "Threat Score": t_val,
                "Friction Rate": f_val,
                "Quadrant": quad
            })
        m_df = pd.DataFrame(matrix_data)

        chart = alt.Chart(m_df).mark_circle(size=220).encode(
            x=alt.X("Friction Rate:Q", scale=alt.Scale(domain=[0, 100]), title="Operational Friction / Vulnerability Rate (%)"),
            y=alt.Y("Threat Score:Q", scale=alt.Scale(domain=[0, 100]), title="Inherent Threat Rating (0 - 100)"),
            color=alt.Color("Quadrant:N", scale=alt.Scale(scheme="category10")),
            tooltip=["Competitor", "Category", "Threat Score", "Friction Rate", "Quadrant"]
        ).properties(height=420)

        rule_x = alt.Chart(pd.DataFrame({'x': [50]})).mark_rule(color="#94A3B8", strokeDash=[4, 4]).encode(x='x:Q')
        rule_y = alt.Chart(pd.DataFrame({'y': [50]})).mark_rule(color="#94A3B8", strokeDash=[4, 4]).encode(y='y:Q')

        st.altair_chart(chart + rule_x + rule_y, use_container_width=True)

        st.markdown("##### Competitor Strategic Quadrant Breakdown")
        st.dataframe(m_df, hide_index=True, use_container_width=True)
    else:
        st.info("Place competitor profiles in Tab 2 to populate the 2D Threat-Friction matrix.")

# -----------------------------------------------------------------------------
# TAB 7: EXECUTIVE BRIEFING & ALERTS
# -----------------------------------------------------------------------------
with tabs[6]:
    st.markdown("### Executive 1-Page Briefing & Headless Dispatch")
    st.caption("Generate formal 1-page C-suite intelligence memos and dispatch via headless SMTP with unlimited CC recipients.")

    b_col1, b_col2 = st.columns([1.2, 1])
    with b_col1:
        st.markdown("##### Executive Brief Preview")
        preview = build_universal_one_pager()
        st.text(preview["plain_text"])

    with b_col2:
        st.markdown("##### Headless Email Dispatch")
        email_to = st.text_input("Primary Recipient Email Address", placeholder="e.g. executive@yourcompany.com")
        email_cc = st.text_area("CC Recipients (Freely add as many comma-separated emails as needed)", placeholder="e.g. ceo@yourcompany.com, cfo@yourcompany.com, board@yourcompany.com")
        
        smtp_user = st.text_input("SMTP User / Email", placeholder="e.g. alerts@yourcompany.com")
        smtp_pass = st.text_input("SMTP App Password / Token", type="password", placeholder="Application token")

        if st.button("Dispatch 1-Page Executive Report Now"):
            rep = build_universal_one_pager(cc_recipients=email_cc.strip())
            subject_line = f"Competitor Updates as of {rep['timestamp']}"
            res = send_universal_headless_email(
                to_email=email_to.strip(),
                subject=subject_line,
                plain_text=rep["plain_text"],
                html_content=rep["html"],
                cc_emails=email_cc.strip(),
                smtp_user=smtp_user.strip(),
                smtp_pass=smtp_pass.strip()
            )
            if res["status"] == "success":
                cc_note = f" (CC: {', '.join(res.get('cc_recipients', []))})" if res.get("cc_recipients") else ""
                st.success(f"Report delivered headlessly to {email_to}{cc_note} via {res['method']}")
            elif res["status"] == "config_needed":
                st.info(res["message"])
            else:
                st.error(res["message"])

# -----------------------------------------------------------------------------
# TAB 8: EXPORT INFRASTRUCTURE
# -----------------------------------------------------------------------------
with tabs[7]:
    st.markdown("### Board-Ready Export Infrastructure")
    st.caption("Export placed competitor dossiers and intelligence matrices for offline C-suite review.")

    if all_competitors:
        export_df = pd.DataFrame([{
            "Competitor Name": c["name"],
            "Domain": c["domain"],
            "Category": c["category"],
            "Executive Brief": c["brief"],
            "Inherent Threat (1-10)": c["inherent_threat_score"],
            "Friction Rate (%)": c["friction_rate"],
            "Rival Pricing Anchor": c["rival_pricing_anchor"],
            "Rival Core Hook": c["rival_core_hook"],
            "Frontline Rebuttal": c["quick_rebuttal"],
            "Last Updated": c["updated_at"]
        } for c in all_competitors])

        csv_data = export_df.to_csv(index=False).encode('utf-8-sig')

        st.download_button(
            "Download Competitor Dossiers (.CSV)",
            data=csv_data,
            file_name=f"Competitor_Intelligence_Dossiers_{company_profile.get('name', 'Export')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### Preview Export Dataset")
        st.dataframe(export_df, hide_index=True, use_container_width=True)
    else:
        st.info("No competitors placed to export yet.")

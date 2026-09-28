"""
app.py
Competitor Snapshot Platform by Lunsad Pilipinas.
4-Step SME Competitive Strategy Engine: Your Business -> Competitors -> Map -> Snapshot.
Official Lunsad Design Palette: Ignition Terracotta (#C85A44) & Oxide Teal (#4B6B6B).
"""
import streamlit as st
import pandas as pd
import altair as alt
import html
import os
from datetime import datetime


import universal_db as db
import universal_reports as reports


# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Competitor Snapshot by Lunsad Pilipinas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# -----------------------------------------------------------------------------
# STYLING (LUNSAD BRAND PALETTE & TYPOGRAPHY)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,600;0,700;1,400;1,700&display=swap');


    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #222831;
    }


    /* Primary Accent Styling */
    .stButton>button {
        border-radius: 4px !important;
        font-weight: 600 !important;
    }
    .stButton>button[kind="primary"] {
        background-color: #C85A44 !important;
        border-color: #C85A44 !important;
        color: #FFFFFF !important;
    }


    /* Top Brand Header */
    .lunsad-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #FFFFFF;
        border-bottom: 2px solid #C85A44;
        padding: 12px 18px;
        margin-bottom: 20px;
    }
    .lunsad-title {
        font-size: 19px;
        font-weight: 700;
        color: #222831;
        margin: 0;
    }
    .lunsad-subtitle {
        font-size: 11px;
        color: #6B7280;
        margin-top: 2px;
    }


    /* Step Navigation Tabs */
    .step-badge {
        display: inline-block;
        border-radius: 50%;
        width: 22px;
        height: 22px;
        text-align: center;
        line-height: 22px;
        font-size: 11px;
        font-weight: 700;
        margin-right: 6px;
    }


    /* Cards & Panels */
    .panel-box {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 4px solid #1E5E5E;
        padding: 14px 18px;
        margin-bottom: 14px;
        border-radius: 2px;
    }
    .panel-box-alert {
        background: #FEF2F2;
        border: 1px solid #FCA5A5;
        border-left: 4px solid #C85A44;
        padding: 14px 18px;
        margin-bottom: 14px;
        border-radius: 2px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SESSION STATE & CLIENT WORKSPACE MANAGEMENT
# -----------------------------------------------------------------------------
all_clients = db.get_all_clients()


if not all_clients:
    # First time initialization: seed sample bakery data
    sample_id = db.load_sample_bakery_data()
    all_clients = db.get_all_clients()
    st.session_state.active_client_id = sample_id


if "active_client_id" not in st.session_state or not st.session_state.active_client_id:
    st.session_state.active_client_id = all_clients[0]["id"] if all_clients else None


client_id_map = {c["name"]: c["id"] for c in all_clients}
client_names = list(client_id_map.keys())


# Current Active Client
active_client = db.get_client(st.session_state.active_client_id) if st.session_state.active_client_id else (all_clients[0] if all_clients else None)
active_client_name = active_client["name"] if active_client else "New Client"


# -----------------------------------------------------------------------------
# TOP BRAND BAR
# -----------------------------------------------------------------------------
head_col1, head_col2, head_col3 = st.columns([3, 1.8, 1.2])


with head_col1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:26px;">📊</span>
        <div>
            <div style="font-size:18px; font-weight:700; color:#222831; line-height:1.2;">Competitor Snapshot</div>
            <div style="font-size:11px; color:#4B6B6B; font-weight:600;">by Lunsad Pilipinas &bull; Practical SME Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


with head_col2:
    selected_client_name = st.selectbox(
        "Active Client Workspace",
        client_names,
        index=client_names.index(active_client_name) if active_client_name in client_names else 0,
        label_visibility="collapsed"
    )
    if selected_client_name and client_id_map.get(selected_client_name) != st.session_state.active_client_id:
        st.session_state.active_client_id = client_id_map[selected_client_name]
        st.rerun()


with head_col3:
    if st.button("➕ New Business", use_container_width=True):
        new_id = db.save_client({
            "name": f"New Business {len(all_clients) + 1}",
            "location": "Metro Manila",
            "industry": "Retail & Services",
            "price_range": "₱100 - ₱1,000",
            "offerings": "Main product or service",
            "target_customers": "Local neighborhood customers",
            "sales_channels": "Walk-in store, Facebook",
            "why_choose_us": "Quality service and dependable local delivery"
        })
        st.session_state.active_client_id = new_id
        st.rerun()


st.markdown("<hr style='margin:10px 0 16px 0; border:none; border-top:1px solid #E5E7EB;'>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4-STEP WORKFLOW TABS
# -----------------------------------------------------------------------------
step_tabs = st.tabs([
    "1. Your Business",
    "2. Competitors",
    "3. Map",
    "4. Snapshot"
])


current_client = db.get_client(st.session_state.active_client_id) if st.session_state.active_client_id else None
competitors = db.get_competitors_for_client(current_client["id"]) if current_client else []
snapshot_plan = db.get_snapshot_plan(current_client["id"]) if current_client else None


# =============================================================================
# STEP 1: YOUR BUSINESS
# =============================================================================
with step_tabs[0]:
    st.markdown("### Step 1: Your Business Profile")
    st.caption("Tell us about this business. This serves as the benchmark against which all rivals are compared.")


    if current_client:
        with st.form("client_profile_form"):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                b_name = st.text_input("Business Name *", value=current_client.get("name", ""), help="Pangalan ng negosyo")
                b_loc = st.text_input("Location / Barangay *", value=current_client.get("location", ""), help="Halimbawa: Concepcion Uno, Marikina")
                b_ind = st.text_input("Industry & Sector", value=current_client.get("industry", ""), help="Halimbawa: Bakery & Pastries, Salon, Coffee Shop")
                b_price = st.text_input("Price Range (PHP) *", value=current_client.get("price_range", ""), help="Halimbawa: ₱5 to ₱850")


            with c_col2:
                b_target = st.text_input("Target Customers *", value=current_client.get("target_customers", ""), help="Sino ang mga bumibili sa inyo?")
                b_channels = st.text_input("Where do you sell? (Channels)", value=current_client.get("sales_channels", ""), help="Halimbawa: Walk-in store, Facebook page, GrabFood")
                b_offerings = st.text_area("Key Products / Offerings *", value=current_client.get("offerings", ""), height=80, help="Ano ang mga mabentang produkto niyo?")


            b_why = st.text_area("Why do customers choose you over rivals?", value=current_client.get("why_choose_us", ""), height=70, help="Bakit ka pinipili ng mga suki? (Halimbawa: mainit na pandesal dalawang beses sa umaga, maingat na delivery)")


            save_b_btn = st.form_submit_button("Save Business Profile", type="primary")
            if save_b_btn:
                if not b_name.strip():
                    st.error("Please provide a valid business name.")
                else:
                    db.save_client({
                        "id": current_client["id"],
                        "name": b_name.strip(),
                        "location": b_loc.strip(),
                        "industry": b_ind.strip(),
                        "price_range": b_price.strip(),
                        "offerings": b_offerings.strip(),
                        "target_customers": b_target.strip(),
                        "sales_channels": b_channels.strip(),
                        "why_choose_us": b_why.strip()
                    })
                    st.toast("Business profile successfully saved!", icon="✅")
                    st.rerun()


        st.markdown("---")
        with st.expander("Workspace Actions (Delete / Reset)"):
            del_col1, del_col2 = st.columns([3, 1])
            with del_col1:
                st.caption(f"Delete '{current_client['name']}' and all attached competitors?")
            with del_col2:
                if st.button("Delete Business", type="secondary"):
                    db.delete_client(current_client["id"])
                    st.toast("Business workspace deleted.", icon="🗑️")
                    st.session_state.active_client_id = None
                    st.rerun()
    else:
        st.info("No business selected. Click '➕ New Business' to start.")


# =============================================================================
# STEP 2: COMPETITORS
# =============================================================================
with step_tabs[1]:
    st.markdown("### Step 2: Competitor Roster")
    st.caption("Place and rate up to 3 primary competitors. Focus on their real price, promises, and weak spots reported by customers.")


    if current_client:
        # Toggle Add / Edit Mode
        if "editing_comp_id" not in st.session_state:
            st.session_state.editing_comp_id = None


        editing_comp = db.get_competitor(st.session_state.editing_comp_id) if st.session_state.editing_comp_id else None


        with st.expander("➕ Add or Edit Competitor", expanded=True if not competitors or editing_comp else False):
            with st.form("competitor_entry_form", clear_on_submit=False):
                st.markdown(f"##### {'Edit Competitor Profile: ' + editing_comp['name'] if editing_comp else 'Add New Competitor'}")
                
                cp_c1, cp_c2 = st.columns(2)
                with cp_c1:
                    c_name_val = st.text_input("Competitor Name *", value=editing_comp.get("name", "") if editing_comp else "")
                    cat_options = [
                        "Same product, same area",
                        "Online seller (Shopee/Lazada/FB)",
                        "Big chain / franchise",
                        "Different product, same need",
                        "Other"
                    ]
                    cat_idx = cat_options.index(editing_comp.get("category", cat_options[0])) if (editing_comp and editing_comp.get("category") in cat_options) else 0
                    c_cat_val = st.selectbox("Competitor Category", cat_options, index=cat_idx)
                    c_price_val = st.text_input("Their Price Range (PHP) *", value=editing_comp.get("price_range", "") if editing_comp else "", help="Halimbawa: ₱4 to ₱6 pandesal, cakes from ₱650")
                    c_promise_val = st.text_input("Their Main Promise / Hook *", value=editing_comp.get("main_promise", "") if editing_comp else "", help="Halimbawa: 'Pinakamurang pandesal sa barangay'")
                    c_sell_val = st.text_input("Where do they sell?", value=editing_comp.get("where_they_sell", "") if editing_comp else "", help="Halimbawa: Walk-in store, Facebook page")


                with cp_c2:
                    c_weak_val = st.text_area("Weak Spot (What customers complain about) *", value=editing_comp.get("weak_spot", "") if editing_comp else "", height=80, help="Anong reklamo ng mga customer sa reviews o FB comments?")
                    c_source_val = st.text_input("Source of Weak Spot *", value=editing_comp.get("weak_spot_source", "") if editing_comp else "", help="Halimbawa: FB reviews, checked 24 Sep 2026")
                    
                    st.markdown("**Consultant Ratings (1 to 5)**")
                    r_col1, r_col2 = st.columns(2)
                    with r_col1:
                        c_strength = st.select_slider(
                            "How strong are they? *",
                            options=[1, 2, 3, 4, 5],
                            value=int(editing_comp.get("strength_rating", 3)) if editing_comp else 3,
                            help="1 = Maliit / Niche, 5 = Dominante at sikat"
                        )
                    with r_col2:
                        c_unhappy = st.select_slider(
                            "How unhappy are customers? *",
                            options=[1, 2, 3, 4, 5],
                            value=int(editing_comp.get("unhappy_rating", 3)) if editing_comp else 3,
                            help="1 = Masaya ang customer, 5 = Maraming reklamo (Malaking opening!)"
                        )


                c_save_btn = st.form_submit_button("Save Competitor Profile", type="primary")
                if c_save_btn:
                    if not c_name_val.strip():
                        st.error("Please enter a competitor name.")
                    else:
                        try:
                            comp_payload = {
                                "client_id": current_client["id"],
                                "name": c_name_val.strip(),
                                "category": c_cat_val,
                                "price_range": c_price_val.strip(),
                                "main_promise": c_promise_val.strip(),
                                "where_they_sell": c_sell_val.strip(),
                                "weak_spot": c_weak_val.strip(),
                                "weak_spot_source": c_source_val.strip(),
                                "strength_rating": c_strength,
                                "unhappy_rating": c_unhappy
                            }
                            if editing_comp:
                                comp_payload["id"] = editing_comp["id"]
                                
                            db.save_competitor(comp_payload)
                            st.session_state.editing_comp_id = None
                            st.toast(f"Competitor '{c_name_val.strip()}' saved successfully!", icon="✅")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))


        # Competitor Inventory Table
        st.markdown("##### Monitored Competitors")
        if competitors:
            comp_table_data = []
            for c in competitors:
                comp_table_data.append({
                    "Name": c["name"],
                    "Category": c["category"],
                    "Price (PHP)": c["price_range"],
                    "Main Promise": c["main_promise"],
                    "Weak Spot": c["weak_spot"],
                    "Strength (1-5)": c["strength_rating"],
                    "Unhappy (1-5)": c["unhappy_rating"]
                })
            st.dataframe(pd.DataFrame(comp_table_data), hide_index=True, use_container_width=True)


            # Edit and Delete Controls
            st.markdown("###### Manage Selected Competitor")
            m_c1, m_c2, m_c3 = st.columns([2, 1, 1])
            with m_c1:
                target_comp_name = st.selectbox("Select Competitor", [c["name"] for c in competitors], key="manage_comp_select")
                target_comp_obj = next((c for c in competitors if c["name"] == target_comp_name), None)


            with m_c2:
                if st.button("✏️ Edit Profile", use_container_width=True):
                    if target_comp_obj:
                        st.session_state.editing_comp_id = target_comp_obj["id"]
                        st.rerun()


            with m_c3:
                if st.button("🗑️ Delete Profile", use_container_width=True):
                    if target_comp_obj:
                        db.delete_competitor(target_comp_obj["id"])
                        st.toast(f"Removed '{target_comp_name}'", icon="🗑️")
                        st.session_state.editing_comp_id = None
                        st.rerun()
        else:
            st.info("No competitors added yet. Use the form above to record your top competitors.")


# =============================================================================
# STEP 3: MAP
# =============================================================================
with step_tabs[2]:
    st.markdown("### Step 3: Competitor Map")
    st.caption("Visual positioning mapping your competitors by Strength (Size/Footprint) vs. Customer Dissatisfaction (Complaints).")


    if current_client and competitors:
        m_col1, m_col2 = st.columns([1.3, 1])


        with m_col1:
            st.markdown("##### Visual Quadrant Matrix")
            m_records = []
            for idx, c in enumerate(competitors[:3], start=1):
                unhappy = float(c.get("unhappy_rating", 3))
                strength = float(c.get("strength_rating", 3))
                
                if strength >= 3 and unhappy < 3:
                    box = "Malakas at gusto ng customers"
                elif strength >= 3 and unhappy >= 3:
                    box = "Malaki pero maraming reklamo (Best Opening)"
                elif strength < 3 and unhappy < 3:
                    box = "Maliit pero loyal ang customers"
                else:
                    box = "Maliit at maraming reklamo"


                m_records.append({
                    "Index": str(idx),
                    "Name": c["name"],
                    "Label": f"{idx}. {c['name']}",
                    "Unhappy": unhappy,
                    "Strength": strength,
                    "Quadrant": box,
                    "Price": c.get("price_range", "N/A"),
                    "Weakness": c.get("weak_spot", "N/A")
                })
            m_df = pd.DataFrame(m_records)


            chart_points = alt.Chart(m_df).mark_circle(size=300).encode(
                x=alt.X("Unhappy:Q", scale=alt.Scale(domain=[0.8, 5.2]), axis=alt.Axis(values=[1, 3, 5], title="How unhappy are their customers? →")),
                y=alt.Y("Strength:Q", scale=alt.Scale(domain=[0.8, 5.2]), axis=alt.Axis(values=[1, 3, 5], title="How strong are they? →")),
                color=alt.Color("Quadrant:N", scale=alt.Scale(
                    domain=[
                        "Malakas at gusto ng customers",
                        "Malaki pero maraming reklamo (Best Opening)",
                        "Maliit pero loyal ang customers",
                        "Maliit at maraming reklamo"
                    ],
                    range=["#1E5E5E", "#C85A44", "#4B6B6B", "#9CA3AF"]
                ), legend=alt.Legend(orient="bottom", columns=2)),
                tooltip=["Label", "Price", "Weakness"]
            )


            chart_text = alt.Chart(m_df).mark_text(align="left", dx=12, fontSize=11, fontWeight="bold").encode(
                x="Unhappy:Q",
                y="Strength:Q",
                text="Label:N"
            )


            mid_rule_x = alt.Chart(pd.DataFrame({'x': [3.0]})).mark_rule(color="#D1D5DB", strokeDash=[4, 4]).encode(x='x:Q')
            mid_rule_y = alt.Chart(pd.DataFrame({'y': [3.0]})).mark_rule(color="#D1D5DB", strokeDash=[4, 4]).encode(y='y:Q')


            final_map = (chart_points + chart_text + mid_rule_x + mid_rule_y).properties(height=420)
            st.altair_chart(final_map, use_container_width=True)


        with m_col2:
            st.markdown("##### What the map says")
            opening_c = None
            for idx, c in enumerate(competitors[:3], start=1):
                unhappy = float(c.get("unhappy_rating", 3))
                strength = float(c.get("strength_rating", 3))


                if strength >= 3 and unhappy < 3:
                    quad_t = "Malakas at gusto ng customers"
                    adv = "Watch closely. Don't copy their price; copy what customers praise."
                elif strength >= 3 and unhappy >= 3:
                    quad_t = "Malaki pero maraming reklamo"
                    adv = "Your best opening. Win their unhappy customers."
                    opening_c = c
                elif strength < 3 and unhappy < 3:
                    quad_t = "Maliit pero loyal ang customers"
                    adv = "Learn from them. Find out why customers stay."
                else:
                    quad_t = "Maliit at maraming reklamo"
                    adv = "Low priority. Focus on stronger threats."


                is_op = (opening_c and opening_c["name"] == c["name"])
                st.markdown(f"""
                <div style="background:{'#FEF2F2' if is_op else '#FFFFFF'}; border:1px solid {'#FCA5A5' if is_op else '#E5E7EB'}; border-left:4px solid {'#C85A44' if is_op else '#1E5E5E'}; padding:10px 14px; margin-bottom:8px; border-radius:2px;">
                    <div style="font-weight:700; font-size:12px; color:#111827;">{idx}. {c['name']}</div>
                    <div style="font-size:11px; font-weight:600; color:{'#C85A44' if is_op else '#1E5E5E'}; margin-top:2px;">{quad_t}</div>
                    <div style="font-size:11px; color:#4B5563; margin-top:4px;">{adv}</div>
                </div>
                """, unsafe_allow_html=True)


            if opening_c:
                st.markdown(f"""
                <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:10px 14px; margin-top:10px; border-radius:2px;">
                    <strong style="color:#92400E; font-size:12px;">Biggest opening: {opening_c['name']}.</strong><br>
                    <span style="color:#78350F; font-size:11px;">Many customers already complain about their service/stock. Communicate your reliability on their exact weak points.</span>
                </div>
                """, unsafe_allow_html=True)


            st.markdown("---")
            st.markdown("""
            **How to read the 4 boxes:**
            - **Malakas at gusto:** bantayan nang mabuti; tapatan ang kalidad.
            - **Malaki pero maraming reklamo:** pinakamagandang opening para humatak ng suki.
            - **Maliit pero loyal:** aralin kung bakit bumabalik ang customers nila.
            - **Maliit at maraming reklamo:** hindi kailangang pag-aksayahan ng oras.
            """)
    else:
        st.info("Add competitors in Step 2 to generate the competitor map.")


# =============================================================================
# STEP 4: SNAPSHOT
# =============================================================================
with step_tabs[3]:
    st.markdown("### Step 4: Build the Snapshot")
    st.caption("Write 3 practical, low-cost actions the owner can try in the next 30 days, then download the 1-page A4 deliverable.")


    if current_client and competitors:
        snap_col1, snap_col2 = st.columns([1.1, 1.3])


        with snap_col1:
            st.markdown("##### 3 Things to Try in the Next 30 Days")
            st.caption("Actionable initiatives doable without extra staff or big budgets.")


            p_data = snapshot_plan or {}
            with st.form("action_plan_form"):
                a1_t = st.text_input("Action 1 Title *", value=p_data.get("action_1_title", "Promise pandesal until 9 AM"))
                a1_d = st.text_area("Action 1 Details *", value=p_data.get("action_1_desc", "Bake a second batch at 6:30 AM and post 'May pandesal pa!' on FB page by 7:30 AM daily."), height=70)
                a1_l = st.text_input("Linked Competitor Weakness 1", value=p_data.get("action_1_link", "Panaderya Uno runs out early"))


                st.markdown("---")
                a2_t = st.text_input("Action 2 Title *", value=p_data.get("action_2_title", "Safe-arrival cake delivery"))
                a2_d = st.text_area("Action 2 Details *", value=p_data.get("action_2_desc", "Free delivery within barangay for orders over ₱800, with photo of boxed cake sent before transit."), height=70)
                a2_l = st.text_input("Linked Competitor Weakness 2", value=p_data.get("action_2_link", "Crumbs & Co. cakes arrive damaged"))


                st.markdown("---")
                a3_t = st.text_input("Action 3 Title *", value=p_data.get("action_3_title", "Start a suki loyalty card"))
                a3_d = st.text_area("Action 3 Details *", value=p_data.get("action_3_desc", "10th ensaymada free. Target 40 sign-ups by end of the month; count every Saturday."), height=70)
                a3_l = st.text_input("Linked Competitor Weakness 3", value=p_data.get("action_3_link", "Keep regulars from trying the new kiosk"))


                save_plan_btn = st.form_submit_button("Save 30-Day Action Plan", type="primary")
                if save_plan_btn:
                    db.save_snapshot_plan(current_client["id"], {
                        "action_1_title": a1_t.strip(),
                        "action_1_desc": a1_d.strip(),
                        "action_1_link": a1_l.strip(),
                        "action_2_title": a2_t.strip(),
                        "action_2_desc": a2_d.strip(),
                        "action_2_link": a2_l.strip(),
                        "action_3_title": a3_t.strip(),
                        "action_3_desc": a3_d.strip(),
                        "action_3_link": a3_l.strip()
                    })
                    st.toast("Action plan saved!", icon="✅")
                    st.rerun()


            st.markdown("##### Quality Check Before Sending")
            q1 = len(competitors) >= 3
            q2 = all(c.get("weak_spot") and c.get("weak_spot_source") for c in competitors[:3])
            q3 = bool(p_data.get("action_1_title") and p_data.get("action_2_title") and p_data.get("action_3_title"))


            st.markdown(f"{'✅' if q1 else '⚠️'} At least 3 competitors with price and weak spot")
            st.markdown(f"{'✅' if q2 else '⚠️'} Every weak spot has a verifiable source")
            st.markdown(f"{'✅' if q3 else '⚠️'} 3 doable actions written")


        with snap_col2:
            st.markdown("##### Preview — A4 Single Page Deliverable")
            snapshot_html = reports.build_a4_snapshot_html(current_client, competitors, snapshot_plan)
            
            st.components.v1.html(snapshot_html, height=620, scrolling=True)


            exp_c1, exp_c2 = st.columns(2)
            with exp_c1:
                clean_name = current_client['name'].replace(' ', '_')
                file_name = f"Snapshot_{clean_name}_{datetime.now().strftime('%Y-%m-%d')}.html"
                st.download_button(
                    label="⬇️ Download Snapshot (HTML/Print)",
                    data=snapshot_html,
                    file_name=file_name,
                    mime="text/html",
                    use_container_width=True
                )
            with exp_c2:
                messenger_msg = reports.generate_messenger_message(current_client, competitors, snapshot_plan)
                with st.popover("💬 Copy Messenger Script", use_container_width=True):
                    st.markdown("**Ready-to-send Taglish Messenger Message:**")
                    st.code(messenger_msg, language="markdown")
                    st.caption("Copy this text and send it alongside the PDF in Facebook Messenger.")
    else:
        st.info("Please set up your business in Step 1 and competitors in Step 2 to generate the Snapshot.")
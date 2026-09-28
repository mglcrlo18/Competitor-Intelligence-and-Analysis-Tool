"""
universal_reports.py
Deliverable generator for Lunsad Competitor Snapshot Platform.
Generates printable A4 HTML with embedded SVG quadrant maps and Messenger scripts.
"""
import html
from datetime import datetime


def generate_map_svg(competitors):
    svg_width = 380
    svg_height = 270
    pad_left = 30
    pad_right = 20
    pad_top = 25
    pad_bottom = 35
    
    plot_w = svg_width - pad_left - pad_right
    plot_h = svg_height - pad_top - pad_bottom
    mid_x = pad_left + plot_w / 2
    mid_y = pad_top + plot_h / 2


    svg = f"""<svg width="100%" height="auto" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg" style="background:#FFFFFF; font-family:'Montserrat', sans-serif;">
        <rect x="{pad_left}" y="{pad_top}" width="{plot_w/2}" height="{plot_h/2}" fill="#F0F7F7" />
        <rect x="{mid_x}" y="{pad_top}" width="{plot_w/2}" height="{plot_h/2}" fill="#FDF3F0" />
        <rect x="{pad_left}" y="{mid_y}" width="{plot_w/2}" height="{plot_h/2}" fill="#F7FAF9" />
        <rect x="{mid_x}" y="{mid_y}" width="{plot_w/2}" height="{plot_h/2}" fill="#FAF9F7" />


        <rect x="{pad_left}" y="{pad_top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#D1D5DB" stroke-width="1" />
        <line x1="{mid_x}" y1="{pad_top}" x2="{mid_x}" y2="{pad_top + plot_h}" stroke="#9CA3AF" stroke-width="1" stroke-dasharray="3,3" />
        <line x1="{pad_left}" y1="{mid_y}" x2="{pad_left + plot_w}" y2="{mid_y}" stroke="#9CA3AF" stroke-width="1" stroke-dasharray="3,3" />


        <!-- Quadrant Names in Taglish -->
        <text x="{pad_left + 8}" y="{pad_top + 14}" font-size="9" font-weight="700" fill="#1E5E5E">Malakas at gusto ng customers</text>
        <text x="{pad_left + 8}" y="{pad_top + 24}" font-size="7.5" fill="#4B6B6B">Strong and well liked</text>


        <text x="{mid_x + 8}" y="{pad_top + 14}" font-size="9" font-weight="700" fill="#C85A44">Malaki pero maraming reklamo</text>
        <text x="{mid_x + 8}" y="{pad_top + 24}" font-size="7.5" fill="#9C4432">Big but many complaints</text>


        <text x="{pad_left + 8}" y="{mid_y + 14}" font-size="9" font-weight="700" fill="#1E5E5E">Maliit pero loyal ang customers</text>
        <text x="{pad_left + 8}" y="{mid_y + 24}" font-size="7.5" fill="#4B6B6B">Small but loyal customers</text>


        <text x="{mid_x + 8}" y="{mid_y + 14}" font-size="9" font-weight="700" fill="#6B7280">Maliit at maraming reklamo</text>
        <text x="{mid_x + 8}" y="{mid_y + 24}" font-size="7.5" fill="#9CA3AF">Small, many complaints</text>


        <text x="{pad_left}" y="{pad_top + plot_h + 16}" font-size="8" fill="#6B7280">Happy customers</text>
        <text x="{mid_x}" y="{pad_top + plot_h + 16}" font-size="8.5" font-weight="600" fill="#374151" text-anchor="middle">How unhappy are their customers? &rarr;</text>
        <text x="{pad_left + plot_w}" y="{pad_top + plot_h + 16}" font-size="8" fill="#6B7280" text-anchor="end">Many complaints</text>


        <text transform="rotate(-90)" x="-{mid_y}" y="12" font-size="8.5" font-weight="600" fill="#374151" text-anchor="middle">How strong are they? &rarr;</text>
    """


    for idx, c in enumerate(competitors[:3], start=1):
        unhappy = float(c.get("unhappy_rating", 3))
        strength = float(c.get("strength_rating", 3))
        norm_x = (unhappy - 1.0) / 4.0
        norm_y = (strength - 1.0) / 4.0


        cx = pad_left + 25 + norm_x * (plot_w - 50)
        cy = pad_top + plot_h - 25 - norm_y * (plot_h - 50)


        is_opening = (unhappy >= 3.0 and strength >= 3.0)
        pin_color = "#C85A44" if is_opening else "#1E5E5E"
        comp_name = html.escape(c.get("name", f"Competitor {idx}"))


        svg += f"""
        <g>
            <circle cx="{cx}" cy="{cy}" r="10" fill="{pin_color}" />
            <text x="{cx}" y="{cy + 3.5}" font-size="9" font-weight="700" fill="#FFFFFF" text-anchor="middle">{idx}</text>
            <text x="{cx + 14}" y="{cy + 3.5}" font-size="8.5" font-weight="700" fill="#1F2937">{comp_name}</text>
        </g>
        """


    svg += "</svg>"
    return svg


def build_a4_snapshot_html(client_data, competitors, plan_data=None, consultant_name="Miguel Gonzales"):
    plan_data = plan_data or {}
    client_name = html.escape(client_data.get("name", "Client Business"))
    client_offerings = html.escape(client_data.get("offerings", ""))
    client_target = html.escape(client_data.get("target_customers", ""))
    client_price = html.escape(client_data.get("price_range", ""))
    client_channels = html.escape(client_data.get("sales_channels", ""))
    now_str = datetime.now().strftime("%d %b %Y")


    comp_rows_html = ""
    for idx, c in enumerate(competitors[:3], start=1):
        c_name = html.escape(c.get("name", ""))
        c_cat = html.escape(c.get("category", "Same product, same area"))
        c_price = html.escape(c.get("price_range", "N/A"))
        c_promise = html.escape(c.get("main_promise", "N/A"))
        c_sell = html.escape(c.get("where_they_sell", "N/A"))
        c_weak = html.escape(c.get("weak_spot", "No recorded weakness"))
        c_source = html.escape(c.get("weak_spot_source", ""))


        is_opening = (float(c.get("unhappy_rating", 3)) >= 3 and float(c.get("strength_rating", 3)) >= 3)
        pin_bg = "#C85A44" if is_opening else "#1E5E5E"


        comp_rows_html += f"""
        <tr style="border-bottom: 1px solid #E5E7EB; font-size: 11px;">
            <td style="padding: 9px 8px; vertical-align: top;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="background:{pin_bg}; color:#fff; border-radius:50%; width:18px; height:18px; display:inline-flex; align-items:center; justify-content:center; font-size:10px; font-weight:700;">{idx}</span>
                    <strong style="color: #111827;">{c_name}</strong>
                </div>
                <div style="font-size: 9.5px; color: #6B7280; margin-top: 2px;">{c_cat}</div>
            </td>
            <td style="padding: 9px 8px; vertical-align: top; color:#1F2937;">{c_price}</td>
            <td style="padding: 9px 8px; vertical-align: top; color:#374151; font-style: italic;">&ldquo;{c_promise}&rdquo;</td>
            <td style="padding: 9px 8px; vertical-align: top; color:#4B5563;">{c_sell}</td>
            <td style="padding: 9px 8px; vertical-align: top;">
                <div style="color: #991B1B; font-weight: 500;">{c_weak}</div>
                {f'<div style="font-size: 9px; color: #9CA3AF; margin-top: 3px;">{c_source}</div>' if c_source else ''}
            </td>
        </tr>
        """


    interpretations_html = ""
    opening_rival = None
    for idx, c in enumerate(competitors[:3], start=1):
        unhappy = float(c.get("unhappy_rating", 3))
        strength = float(c.get("strength_rating", 3))
        c_name = html.escape(c.get("name", ""))


        if strength >= 3 and unhappy < 3:
            box_title = "Malakas at gusto ng customers"
            advice = "Watch closely. Don't copy their price; copy what customers praise."
        elif strength >= 3 and unhappy >= 3:
            box_title = "Malaki pero maraming reklamo"
            advice = "Your best opening. Win their unhappy customers."
            opening_rival = c
        elif strength < 3 and unhappy < 3:
            box_title = "Maliit pero loyal ang customers"
            advice = "Learn from them. Find out why customers stay."
        else:
            box_title = "Maliit at maraming reklamo"
            advice = "Low priority. They do not pose immediate competitive friction."


        is_opening = (opening_rival and opening_rival.get("name") == c.get("name"))
        badge_color = "#C85A44" if is_opening else "#1E5E5E"


        interpretations_html += f"""
        <div style="margin-bottom: 9px;">
            <div style="display: flex; align-items: baseline; gap: 6px;">
                <span style="background:{badge_color}; color:#fff; border-radius:50%; width:15px; height:15px; display:inline-flex; align-items:center; justify-content:center; font-size:8.5px; font-weight:700;">{idx}</span>
                <span style="font-weight: 700; font-size: 11px; color:#111827;">{c_name}:</span>
                <span style="font-size: 10.5px; font-weight: 600; color:{badge_color};">{box_title}</span>
            </div>
            <div style="font-size: 10px; color: #4B5563; margin-left: 21px; margin-top: 2px;">{advice}</div>
        </div>
        """


    opening_box_html = ""
    if opening_rival:
        op_name = html.escape(opening_rival.get("name", ""))
        opening_box_html = f"""
        <div style="background: #FEF2F2; border-left: 3px solid #DC2626; padding: 7px 10px; margin-top: 10px;">
            <strong style="color: #991B1B; font-size: 10.5px;">Biggest opening: {op_name}.</strong>
            <span style="color: #7F1D1D; font-size: 10px;"> Customers are actively complaining about their weak spots. Highlight your reliability on this exact point.</span>
        </div>
        """


    act1_t = html.escape(plan_data.get("action_1_title", "Action 1"))
    act1_d = html.escape(plan_data.get("action_1_desc", "Details for action 1."))
    act2_t = html.escape(plan_data.get("action_2_title", "Action 2"))
    act2_d = html.escape(plan_data.get("action_2_desc", "Details for action 2."))
    act3_t = html.escape(plan_data.get("action_3_title", "Action 3"))
    act3_d = html.escape(plan_data.get("action_3_desc", "Details for action 3."))


    map_svg = generate_map_svg(competitors)


    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Competitor Snapshot - {client_name}</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
    @page {{
        size: A4;
        margin: 12mm 15mm;
    }}
    body {{
        font-family: 'Montserrat', sans-serif;
        color: #222831;
        background-color: #FFFFFF;
        margin: 0;
        padding: 0;
        line-height: 1.4;
    }}
    .header-bar {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 2px solid #C85A44;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }}
    .brand-sub {{
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 700;
        color: #C85A44;
        margin-bottom: 2px;
    }}
    .client-title {{
        font-size: 20px;
        font-weight: 700;
        color: #222831;
        margin: 0;
    }}
    .meta-box {{
        text-align: right;
        font-size: 9.5px;
        color: #6B7280;
    }}
    .section-title {{
        font-size: 11.5px;
        font-weight: 700;
        color: #1E5E5E;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 10px 0 6px 0;
    }}
    .business-card {{
        background: #F7F5F0;
        border-left: 3px solid #1E5E5E;
        padding: 8px 12px;
        font-size: 11px;
        color: #374151;
        line-height: 1.45;
        margin-bottom: 12px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 12px;
    }}
    th {{
        background: #F3F4F6;
        text-align: left;
        padding: 6px 8px;
        font-size: 10px;
        font-weight: 700;
        color: #4B5563;
        border-bottom: 2px solid #D1D5DB;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }}
    .action-box {{
        background: #FDF3F0;
        border-left: 3px solid #C85A44;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 2px;
    }}
    .action-title {{
        font-size: 11px;
        font-weight: 700;
        color: #C85A44;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .action-desc {{
        font-size: 10.5px;
        color: #374151;
        margin-top: 3px;
        line-height: 1.4;
    }}
    .cta-banner {{
        background: #1E5E5E;
        color: #FFFFFF;
        padding: 9px 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 10px;
        border-radius: 2px;
    }}
    .footer-text {{
        font-size: 8px;
        color: #9CA3AF;
        margin-top: 8px;
        line-height: 1.35;
    }}
</style>
</head>
<body>


    <div class="header-bar">
        <div>
            <div class="brand-sub">COMPETITOR SNAPSHOT &bull; Lunsad Pilipinas</div>
            <h1 class="client-title">{client_name}</h1>
        </div>
        <div class="meta-box">
            <div>Prepared {now_str}</div>
            <div>by {consultant_name}, Lunsad Pilipinas</div>
            <div>Based on public info & client brief</div>
        </div>
    </div>


    <!-- 1. Your Business -->
    <div class="section-title">Your business</div>
    <div class="business-card">
        <strong>Offerings:</strong> {client_offerings} | <strong>Target Customers:</strong> {client_target}<br>
        <strong>Price range:</strong> {client_price} | <strong>Sells via:</strong> {client_channels}
    </div>


    <!-- 2. Top 3 Competitors -->
    <div class="section-title">Your top 3 competitors</div>
    <table>
        <thead>
            <tr>
                <th style="width: 23%;">Competitor</th>
                <th style="width: 17%;">Price</th>
                <th style="width: 22%;">Main promise</th>
                <th style="width: 18%;">Where they sell</th>
                <th style="width: 20%;">Weak spot (from reviews)</th>
            </tr>
        </thead>
        <tbody>
            {comp_rows_html}
        </tbody>
    </table>


    <!-- 3. Where they sit / What it means -->
    <div style="display: flex; gap: 18px; margin-bottom: 10px;">
        <div style="flex: 1.1;">
            <div class="section-title">Where they sit</div>
            {map_svg}
        </div>
        <div style="flex: 1;">
            <div class="section-title">What it means for you</div>
            {interpretations_html}
            {opening_box_html}
        </div>
    </div>


    <!-- 4. 3 Things to Try -->
    <div class="section-title">3 things to try in the next 30 days</div>
    
    <div class="action-box">
        <div class="action-title"><span>1.</span> {act1_t}</div>
        <div class="action-desc">{act1_d}</div>
    </div>


    <div class="action-box">
        <div class="action-title"><span>2.</span> {act2_t}</div>
        <div class="action-desc">{act2_d}</div>
    </div>


    <div class="action-box">
        <div class="action-title"><span>3.</span> {act3_t}</div>
        <div class="action-desc">{act3_d}</div>
    </div>


    <!-- 5. CTA Walkthrough Banner -->
    <div class="cta-banner">
        <div style="background:#FFFFFF; color:#1E5E5E; border-radius:4px; padding:4px 8px; font-weight:800; font-size:11px;">CHAT</div>
        <div style="font-size: 10px; line-height: 1.35;">
            <strong>Free 20-minute walkthrough:</strong> Reply <strong>"CALL"</strong> in our Messenger conversation and we will walk through this Snapshot together and answer any questions.
        </div>
    </div>


    <div class="footer-text">
        Ratings are the consultant's judgement based on public customer reviews, social media pages, store visits, and client inputs. They are not formal survey results. Competitor notes are for your private strategic use. Lunsad Pilipinas &bull; Ignition &bull; Traction &bull; Ascent.
    </div>


</body>
</html>
"""
    return full_html


def generate_messenger_message(client_data, competitors, plan_data=None):
    plan_data = plan_data or {}
    client_name = client_data.get("name", "Ma'am/Sir")
    top_comp = competitors[0].get("name", "mga katapat") if competitors else "mga kakumpitensya"
    
    act1_t = plan_data.get("action_1_title", "I-promote ang best seller mo")
    act2_t = plan_data.get("action_2_title", "I-highlight ang serbisyo")
    act3_t = plan_data.get("action_3_title", "Suki rewards initiative")


    msg = f"""Kumusta {client_name}! Eto na po ang official 1-Page Competitor Snapshot para sa inyong negosyo. 📊


Inaral namin ang market niyo kasama ang mga katulad ng {top_comp}. Heto ang 3 quick highlights para sa inyo:


1. {act1_t}
2. {act2_t}
3. {act3_t}


Kasama sa PDF attachment ang complete matrix kung saan nakapuwesto ang bawat competitor at kung ano ang pwede nating gawing panalo laban sa kanila.


Kung gusto niyo po pag-usapan nang libre (20-minute walkthrough sa phone or video call), mag-reply lang po kayo ng "CALL" dito sa chat! Salamat! 🚀"""
    return msg
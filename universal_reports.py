"""
universal_reports.py
Universal Executive 1-Page Intelligence Briefing & Headless Dispatcher.
Completely neutral, industry-agnostic architecture.
Produces clean executive memos and supports headless SMTP delivery with CC recipients.
"""
import os
import re
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from universal_db import get_company_profile, get_all_competitors, get_signals_for_competitor

def build_universal_one_pager(cc_recipients: str = "") -> Dict[str, str]:
    """
    Generates a 1-page executive briefing memo tailored to the specialist's company brief.
    Zero emojis, clean C-suite typography.
    """
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    company = get_company_profile()
    comps = get_all_competitors()
    signals = get_signals_for_competitor()

    company_name = company.get("name", "Enterprise Subject")
    industry = company.get("industry", "Global Enterprise")
    active_cc = cc_recipients or "None specified"

    critical_threats = sum(1 for c in comps if float(c.get("inherent_threat_score", 0)) >= 7.0)

    # 1. Plain Text Representation
    pt_lines = [
        "=" * 72,
        f"{company_name.upper()} // COMPETITIVE INTELLIGENCE EXECUTIVE BRIEFING",
        "=" * 72,
        f"SUBJECT: Competitor Updates as of {timestamp_str}",
        f"DATE & TIME: {timestamp_str}",
        f"COMPANY: {company_name} ({industry})",
        "TO: Executive Leadership Team / C-Suite",
        "FROM: Strategic Market Intelligence Unit",
        f"CC: {active_cc}",
        f"MONITORED ROSTER: {len(comps)} Active Competitors Under Surveillance",
        f"THREAT POSTURE: {critical_threats} High/Critical Inherent Threats Identified",
        "-" * 72,
        "",
        "SECTION 1: UPDATES ON SIGNIFICANT NEWS & SIGNALS",
        "-" * 72
    ]

    if signals:
        for idx, s in enumerate(signals[:5], 1):
            pt_lines.append(f"[{idx}] {s.get('competitor', '').upper()} - {s.get('platform', 'Market Update')}")
            pt_lines.append(f"    Headline: {s.get('title', '')}")
            if s.get("snippet"):
                pt_lines.append(f"    Intelligence: {s.get('snippet', '')[:200]}")
            pt_lines.append("")
    else:
        pt_lines.append("No critical external market signals detected in the trailing monitoring window.")
        pt_lines.append("")

    pt_lines.extend([
        "-" * 72,
        "SECTION 2: STRATEGIC FINDINGS & TACTICAL PLAYBOOK",
        "-" * 72
    ])

    # Dynamic generation based on placed competitors
    if comps:
        top_rival = comps[0]
        pt_lines.append(f"1. Primary Rival Assessment ({top_rival['name']}):")
        pt_lines.append(f"   Positioning: {top_rival.get('rival_core_hook', 'Aggressive commercial expansion.')}")
        pt_lines.append(f"   Vulnerability Factor: Friction rate estimated at {top_rival.get('friction_rate', 30)}%.")
        pt_lines.append(f"   Sales Countermeasure: {top_rival.get('quick_rebuttal', 'Lead with core technical moats.')}")
        pt_lines.append("")
        pt_lines.append("2. Market Share Defense & Buyer Guidance:")
        pt_lines.append(f"   Reinforce {company_name}'s key differentiators: {company.get('core_differentiators', 'Superior reliability and compliance')[:150]}.")
        pt_lines.append("   Arm frontline sales executives with targeted buyer landmines during RFP evaluations.")
        pt_lines.append("")
    else:
        pt_lines.append("Add competitor profiles to the Placement Hub to generate automated strategic findings.")
        pt_lines.append("")

    pt_lines.extend([
        "=" * 72,
        f"CONFIDENTIAL: FOR INTERNAL {company_name.upper()} STRATEGY COMMITTEE ONLY",
        "=" * 72
    ])

    plain_text = "\n".join(pt_lines)

    # 2. Executive HTML Representation
    signals_html = ""
    for idx, s in enumerate(signals[:5], 1):
        signals_html += f"""
        <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-left:4px solid #1E293B; padding:12px; margin-bottom:10px;">
            <div style="font-family:'Montserrat', sans-serif; font-size:11px; font-weight:700; color:#1E293B; text-transform:uppercase;">
                [{idx}] {s.get('competitor', '').upper()} - {s.get('platform', 'MARKET SIGNAL')}
            </div>
            <div style="font-size:13px; font-weight:700; color:#0284C7; margin:4px 0;">
                <a href="{s.get('url', '#')}" target="_blank" style="color:#0284C7; text-decoration:none;">{s.get('title', '')}</a>
            </div>
            <div style="font-size:11px; color:#334155; line-height:1.4;">
                {s.get('snippet', '')}
            </div>
        </div>
        """

    top_findings = ""
    if comps:
        top_rival = comps[0]
        top_findings = f"""
        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-left:4px solid #0284C7; padding:12px; margin-bottom:10px; font-size:12px; line-height:1.5;">
            <strong>Primary Exposure ({top_rival['name']}):</strong><br>
            Rival Pitch: <em>"{top_rival.get('rival_core_hook', 'Enterprise market coverage.')}"</em><br>
            <strong>Frontline Rebuttal:</strong> {top_rival.get('quick_rebuttal', 'Lead with unique product architecture and SLA commitments.')}
        </div>
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; padding:12px; font-size:12px; line-height:1.5;">
            <strong>Defensive Value Realization ({company_name}):</strong><br>
            Emphasize {company_name}'s proven moat: {company.get('core_differentiators', 'Superior execution, security compliance, and dedicated client success.')[:200]}
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #F8FAFC;
                color: #0F172A;
                margin: 0;
                padding: 20px;
            }}
            .card {{
                max-width: 820px;
                margin: 0 auto;
                background-color: #FFFFFF;
                border: 1px solid #0F172A;
                border-top: 5px solid #0F172A;
                padding: 24px;
            }}
            .header-bar {{
                background-color: #0F172A;
                border-left: 4px solid #0284C7;
                padding: 14px 18px;
                color: #F8FAFC;
                margin-bottom: 20px;
            }}
            .header-title {{
                font-size: 16px;
                font-weight: 700;
                margin: 0;
            }}
            .header-meta {{
                font-size: 11px;
                color: #94A3B8;
                margin-top: 4px;
            }}
            .metric-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                margin-bottom: 16px;
            }}
            .metric-box {{
                background: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-left: 3px solid #0F172A;
                padding: 10px;
            }}
            .metric-num {{
                font-size: 20px;
                font-weight: 700;
                color: #0F172A;
            }}
            .metric-lbl {{
                font-size: 10px;
                color: #64748B;
                text-transform: uppercase;
            }}
            .section-label {{
                font-size: 12px;
                font-weight: 700;
                color: #0F172A;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                border-bottom: 2px solid #0F172A;
                padding-bottom: 4px;
                margin-top: 20px;
                margin-bottom: 12px;
            }}
            .footer {{
                margin-top: 24px;
                padding-top: 12px;
                border-top: 1px solid #E2E8F0;
                font-size: 10px;
                color: #64748B;
                display: flex;
                justify-content: space-between;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header-bar">
                <div class="header-title">Competitor Updates as of {timestamp_str}</div>
                <div class="header-meta">
                    <strong>Company:</strong> {company_name} &nbsp;|&nbsp; <strong>Industry:</strong> {industry}<br>
                    <strong>To:</strong> Executive Leadership Team &nbsp;|&nbsp; <strong>CC:</strong> {active_cc}
                </div>
            </div>

            <div class="metric-grid">
                <div class="metric-box">
                    <div class="metric-lbl">Monitored Competitor Roster</div>
                    <div class="metric-num">{len(comps)}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-lbl">High Threat Rivals Under Surveillance</div>
                    <div class="metric-num">{critical_threats}</div>
                </div>
            </div>

            <div class="section-label">1. Updates on Significant News & Market Signals</div>
            {signals_html}

            <div class="section-label">2. Strategic Findings & Tactical Playbook</div>
            {top_findings}

            <div class="footer">
                <span>CONFIDENTIAL: STRICTLY FOR INTERNAL LEADERSHIP</span>
                <span>SYSTEM: MARKET RADAR PLATFORM</span>
            </div>
        </div>
    </body>
    </html>
    """

    return {
        "plain_text": plain_text,
        "html": html,
        "timestamp": timestamp_str
    }

def send_universal_headless_email(
    to_email: str,
    subject: str,
    plain_text: str,
    html_content: Optional[str] = None,
    cc_emails: Optional[str] = None,
    smtp_user: str = "",
    smtp_pass: str = "",
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587
) -> Dict[str, Any]:
    """Headless SMTP delivery supporting unlimited CC recipients."""
    if not to_email or not smtp_user or not smtp_pass:
        return {
            "status": "config_needed",
            "message": "SMTP credentials or recipient missing."
        }

    # Clean CC list
    cc_list = []
    if cc_emails:
        for c in re.split(r"[,;\n]", str(cc_emails)):
            clean = c.strip()
            if clean and "@" in clean:
                cc_list.append(clean)

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Competitive Intelligence Radar <{smtp_user}>"
        msg["To"] = to_email
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        msg["Subject"] = subject
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")

        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        if html_content:
            msg.attach(MIMEText(html_content, "html", "utf-8"))

        server = smtplib.SMTP(smtp_host, smtp_port, timeout=15.0)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)

        all_dests = [to_email] + [c for c in cc_list if c.lower() != to_email.lower()]
        server.sendmail(smtp_user, all_dests, msg.as_string())
        server.quit()

        return {
            "status": "success",
            "method": f"Headless SMTP ({smtp_host}:{smtp_port})",
            "recipient": to_email,
            "cc_recipients": cc_list,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"SMTP delivery failed: {str(e)}"
        }

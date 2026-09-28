"""
universal_db.py
Database and Persistence Layer for the Universal Competitor Intelligence Platform.
Industry-agnostic architecture: completely free of any specific brand or vertical hardcoding.
Maintains company profile briefs and placed competitors in SQLite.
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "market_radar.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # 1. Company Profile & Strategic Brief (Inputted by Competitor Specialist)
    c.execute("""
    CREATE TABLE IF NOT EXISTS company_profile (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        domain TEXT,
        industry TEXT,
        company_brief TEXT,
        core_differentiators TEXT,
        key_offerings TEXT,
        target_market TEXT,
        pricing_model TEXT,
        updated_at TEXT
    )
    """)

    # 2. Placed Competitor Profiles
    c.execute("""
    CREATE TABLE IF NOT EXISTS competitors (
        name TEXT PRIMARY KEY,
        domain TEXT,
        category TEXT,
        brief TEXT,
        inherent_threat_score REAL DEFAULT 5.0,
        control_efficacy_score REAL DEFAULT 6.0,
        market_footprint_score REAL DEFAULT 5.0,
        friction_rate REAL DEFAULT 30.0,
        rival_pricing_anchor TEXT,
        rival_core_hook TEXT,
        quick_rebuttal TEXT,
        landmines TEXT,
        claims_vs_facts TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    # 3. Market Signals & News Stream
    c.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        competitor TEXT,
        platform TEXT,
        title TEXT,
        snippet TEXT,
        url TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()

    # Seed initial industry-agnostic sample data if empty
    c.execute("SELECT COUNT(*) as count FROM company_profile")
    if c.fetchone()["count"] == 0:
        seed_sample_data(conn)

    conn.close()

def seed_sample_data(conn):
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sample Company: Nexus Systems (Enterprise Cloud & Analytics)
    c.execute("""
    INSERT INTO company_profile (
        id, name, domain, industry, company_brief, core_differentiators, key_offerings, target_market, pricing_model, updated_at
    ) VALUES (
        1,
        'Nexus Systems',
        'nexussystems.io',
        'Enterprise Software & Intelligence Platforms',
        'Nexus Systems provides enterprise organizations with unified autonomous decision intelligence, automated compliance auditing, and real-time operational radar systems.',
        'Zero-trust modular data pipelines; sub-second query retrieval across heterogeneous data silos; 100% data sovereign on-prem or private cloud deployment.',
        'Nexus Core Platform, Enterprise Risk Auditor, Autonomous Market Radar, Executive Decision Room',
        'Mid-market and Global 2000 enterprises, regulated financial institutions, industrial operators',
        'Annual subscription per active intelligence node with tier-based compute allocation',
        ?
    )
    """, (now_str,))

    # Sample Placed Competitors
    sample_comps = [
        {
            "name": "CloudScale Global",
            "domain": "cloudscaleglobal.com",
            "category": "Direct Competitor",
            "brief": "Large legacy competitor with broad market reach and aggressive commercial marketing, but plagued by rigid long-term contracts and high customer support latency.",
            "inherent_threat_score": 8.4,
            "control_efficacy_score": 6.8,
            "market_footprint_score": 8.5,
            "friction_rate": 62.0,
            "rival_pricing_anchor": "$120,000 / Year + High Professional Services Fees",
            "rival_core_hook": "The legacy standard in enterprise data aggregation with global 24/7 account representatives.",
            "quick_rebuttal": "CloudScale relies on fragmented multi-tenant architectures that require 6-9 months of costly systems integration. Nexus deploys within 48 hours with guaranteed data sovereignty.",
            "landmines": json.dumps([
                "Ask for their mean-time-to-resolution (MTTR) SLA on custom data pipeline failures.",
                "Inquire whether customer data is co-located across shared multi-tenant clusters.",
                "Request exact line-item costs for mandatory professional services in Year 2 renewal."
            ]),
            "claims_vs_facts": json.dumps([
                {"claim": "Turnkey deployment across any enterprise infrastructure.", "fact": "Independent customer reviews report average onboarding duration exceeds 180 days with required billable consultants."},
                {"claim": "99.99% automated ingestion uptime.", "fact": "Field reports document regular pipeline timeouts during high-throughput schema transformations."}
            ])
        },
        {
            "name": "LegacyCorp ERP",
            "domain": "legacycorperp.com",
            "category": "Legacy Incumbent",
            "brief": "Dominant institutional incumbent with deep multi-year vendor lock-in, slow feature iteration velocity, and steep maintenance surcharges.",
            "inherent_threat_score": 7.5,
            "control_efficacy_score": 7.5,
            "market_footprint_score": 9.0,
            "friction_rate": 78.0,
            "rival_pricing_anchor": "$250,000+ Enterprise Master Services Agreement",
            "rival_core_hook": "Nobody gets fired for choosing LegacyCorp.",
            "quick_rebuttal": "LegacyCorp locks buyers into 5-year monolithic upgrade cycles. Nexus offers a modular API-first architecture with modern UX and zero lock-in.",
            "landmines": json.dumps([
                "Ask how many business days are required to export all raw operational data upon contract termination.",
                "Check their mobile responsiveness and browser UI compatibility."
            ]),
            "claims_vs_facts": json.dumps([
                {"claim": "All-in-one comprehensive operating suite.", "fact": "Components are stitched together through past acquisitions with disjointed logins and inconsistent database models."}
            ])
        },
        {
            "name": "Vanguard Platform",
            "domain": "vanguardplatform.tech",
            "category": "Direct Competitor",
            "brief": "Venture-backed high-velocity challenger with aggressive pricing discounts, high sales turnover, and incomplete enterprise security certifications.",
            "inherent_threat_score": 6.8,
            "control_efficacy_score": 6.2,
            "market_footprint_score": 5.5,
            "friction_rate": 45.0,
            "rival_pricing_anchor": "Discounts up to 60% for upfront annual commitments",
            "rival_core_hook": "Next-generation lightweight analytics with instant self-service sign-up.",
            "quick_rebuttal": "Vanguard lacks SOC 2 Type II and HIPAA compliance certifications. Nexus meets strict global regulatory compliance out of the box.",
            "landmines": json.dumps([
                "Request audited third-party penetration testing and SOC 2 Type II compliance reports.",
                "Inquire about dedicated customer success engineer availability during non-US business hours."
            ]),
            "claims_vs_facts": json.dumps([
                {"claim": "Enterprise-grade bank security encryption.", "fact": "Lacks dedicated hardware security module (HSM) key isolation and role-based row-level permissions."}
            ])
        },
        {
            "name": "AeroSync Dynamics",
            "domain": "aerosyncdynamics.com",
            "category": "Emerging Disruptor",
            "brief": "Boutique AI startup focusing on automated signal detection, growing rapidly in regional startup ecosystems.",
            "inherent_threat_score": 4.5,
            "control_efficacy_score": 7.0,
            "market_footprint_score": 3.0,
            "friction_rate": 25.0,
            "rival_pricing_anchor": "$2,500 / Month flat rate",
            "rival_core_hook": "AI-first autonomous agents doing the work of 5 market researchers.",
            "quick_rebuttal": "AeroSync lacks custom data connectors and historical longitudinal databases. Nexus provides verifiable audit trails with deep relational integrity.",
            "landmines": json.dumps([
                "Ask how AI hallucinations and ungrounded market claims are filtered before executive delivery."
            ]),
            "claims_vs_facts": json.dumps([
                {"claim": "100% automated market research with zero human intervention.", "fact": "Relies on generic public LLM web search without verifiable source cross-referencing."}
            ])
        }
    ]

    for comp in sample_comps:
        c.execute("""
        INSERT INTO competitors (
            name, domain, category, brief, inherent_threat_score, control_efficacy_score,
            market_footprint_score, friction_rate, rival_pricing_anchor, rival_core_hook,
            quick_rebuttal, landmines, claims_vs_facts, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            comp["name"], comp["domain"], comp["category"], comp["brief"],
            comp["inherent_threat_score"], comp["control_efficacy_score"], comp["market_footprint_score"],
            comp["friction_rate"], comp["rival_pricing_anchor"], comp["rival_core_hook"],
            comp["quick_rebuttal"], comp["landmines"], comp["claims_vs_facts"],
            now_str, now_str
        ))

    # Sample signals
    sample_signals = [
        ("CloudScale Global", "Industry Wire", "CloudScale Announces Restructuring of Regional Customer Success Units", "Enterprise customers report extended ticket backlog following quarterly cost-reduction measures.", "https://example.com/news1"),
        ("LegacyCorp ERP", "Tech Regulatory Bulletin", "LegacyCorp Faces Class Inquiries Regarding Data Portability Fees", "Enterprise clients contest retroactive fee hikes applied during cloud migration transitions.", "https://example.com/news2"),
        ("Vanguard Platform", "Venture Digest", "Vanguard Platform Closes Series B Growth Round", "Capital to be deployed toward aggressive direct-to-consumer enterprise sales funnels.", "https://example.com/news3")
    ]
    for s_comp, s_plat, s_title, s_snip, s_url in sample_signals:
        c.execute("""
        INSERT INTO signals (competitor, platform, title, snippet, url, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (s_comp, s_plat, s_title, s_snip, s_url, now_str))

    conn.commit()

def get_company_profile() -> Dict[str, Any]:
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM company_profile WHERE id = 1")
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "name": "My Company",
        "domain": "",
        "industry": "General Enterprise",
        "company_brief": "",
        "core_differentiators": "",
        "key_offerings": "",
        "target_market": "",
        "pricing_model": "",
        "updated_at": ""
    }

def save_company_profile(data: Dict[str, Any]):
    init_db()
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
    INSERT INTO company_profile (id, name, domain, industry, company_brief, core_differentiators, key_offerings, target_market, pricing_model, updated_at)
    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        name = excluded.name,
        domain = excluded.domain,
        industry = excluded.industry,
        company_brief = excluded.company_brief,
        core_differentiators = excluded.core_differentiators,
        key_offerings = excluded.key_offerings,
        target_market = excluded.target_market,
        pricing_model = excluded.pricing_model,
        updated_at = excluded.updated_at
    """, (
        data.get("name", "My Company"),
        data.get("domain", ""),
        data.get("industry", ""),
        data.get("company_brief", ""),
        data.get("core_differentiators", ""),
        data.get("key_offerings", ""),
        data.get("target_market", ""),
        data.get("pricing_model", ""),
        now_str
    ))
    conn.commit()
    conn.close()

def get_all_competitors() -> List[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM competitors ORDER BY inherent_threat_score DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_competitor_names() -> List[str]:
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM competitors ORDER BY name ASC")
    names = [r["name"] for r in c.fetchall()]
    conn.close()
    return names

def get_competitor(name: str) -> Optional[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM competitors WHERE name = ?", (name,))
    row = c.fetchone()
    conn.close()
    if row:
        d = dict(row)
        try:
            d["landmines_list"] = json.loads(d.get("landmines") or "[]")
        except Exception:
            d["landmines_list"] = []
        try:
            d["claims_list"] = json.loads(d.get("claims_vs_facts") or "[]")
        except Exception:
            d["claims_list"] = []
        return d
    return None

def save_competitor(comp: Dict[str, Any]):
    init_db()
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    landmines_json = json.dumps(comp.get("landmines_list", []))
    claims_json = json.dumps(comp.get("claims_list", []))

    c.execute("""
    INSERT INTO competitors (
        name, domain, category, brief, inherent_threat_score, control_efficacy_score,
        market_footprint_score, friction_rate, rival_pricing_anchor, rival_core_hook,
        quick_rebuttal, landmines, claims_vs_facts, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(name) DO UPDATE SET
        domain = excluded.domain,
        category = excluded.category,
        brief = excluded.brief,
        inherent_threat_score = excluded.inherent_threat_score,
        control_efficacy_score = excluded.control_efficacy_score,
        market_footprint_score = excluded.market_footprint_score,
        friction_rate = excluded.friction_rate,
        rival_pricing_anchor = excluded.rival_pricing_anchor,
        rival_core_hook = excluded.rival_core_hook,
        quick_rebuttal = excluded.quick_rebuttal,
        landmines = excluded.landmines,
        claims_vs_facts = excluded.claims_vs_facts,
        updated_at = excluded.updated_at
    """, (
        comp["name"], comp.get("domain", ""), comp.get("category", "Direct Competitor"),
        comp.get("brief", ""), float(comp.get("inherent_threat_score", 5.0)),
        float(comp.get("control_efficacy_score", 6.0)), float(comp.get("market_footprint_score", 5.0)),
        float(comp.get("friction_rate", 30.0)), comp.get("rival_pricing_anchor", ""),
        comp.get("rival_core_hook", ""), comp.get("quick_rebuttal", ""),
        landmines_json, claims_json, now_str, now_str
    ))
    conn.commit()
    conn.close()

def delete_competitor(name: str):
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM competitors WHERE name = ?", (name,))
    c.execute("DELETE FROM signals WHERE competitor = ?", (name,))
    conn.commit()
    conn.close()

def get_signals_for_competitor(comp_name: str = "") -> List[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    c = conn.cursor()
    if comp_name and comp_name != "All Competitors":
        c.execute("SELECT * FROM signals WHERE competitor = ? ORDER BY id DESC LIMIT 10", (comp_name,))
    else:
        c.execute("SELECT * FROM signals ORDER BY id DESC LIMIT 15")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

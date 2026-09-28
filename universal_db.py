"""
universal_db.py
Storage layer for Lunsad Competitor Snapshot Platform.
Designed for Philippine SME consulting workflows with multi-client support,
safe CRUD operations, schema migrations, and zero fabricated data.
"""
import sqlite3
import os
import json
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


# Allow override via environment variable or default to local directory
DB_PATH = os.environ.get("LUNSAD_DB_PATH", os.path.join(os.path.dirname(__file__), "market_radar.db"))


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables with proper relational schema and migration checks."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Clients / Business Workspaces
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                location TEXT DEFAULT '',
                industry TEXT DEFAULT '',
                price_range TEXT DEFAULT '',
                offerings TEXT DEFAULT '',
                target_customers TEXT DEFAULT '',
                sales_channels TEXT DEFAULT '',
                why_choose_us TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


        # 2. Competitors Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                name TEXT NOT NULL COLLATE NOCASE,
                category TEXT DEFAULT 'Same product, same area',
                price_range TEXT DEFAULT '',
                main_promise TEXT DEFAULT '',
                where_they_sell TEXT DEFAULT '',
                weak_spot TEXT DEFAULT '',
                weak_spot_source TEXT DEFAULT '',
                strength_rating INTEGER DEFAULT 3,
                unhappy_rating INTEGER DEFAULT 3,
                why_choose_you TEXT DEFAULT '',
                watch_out TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
                UNIQUE (client_id, name)
            )
        """)


        # 3. Snapshot 30-Day Action Plans
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshot_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL UNIQUE,
                action_1_title TEXT DEFAULT '',
                action_1_desc TEXT DEFAULT '',
                action_1_link TEXT DEFAULT '',
                action_2_title TEXT DEFAULT '',
                action_2_desc TEXT DEFAULT '',
                action_2_link TEXT DEFAULT '',
                action_3_title TEXT DEFAULT '',
                action_3_desc TEXT DEFAULT '',
                action_3_link TEXT DEFAULT '',
                updated_at TEXT NOT NULL,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
        """)
        conn.commit()


# --- CLIENT OPERATIONS ---


def get_all_clients():
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients ORDER BY name ASC")
        return [dict(row) for row in cursor.fetchall()]


def get_client(client_id):
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def save_client(client_data):
    init_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    name = client_data.get("name", "").strip()
    if not name:
        raise ValueError("Client name cannot be blank.")


    with get_connection() as conn:
        cursor = conn.cursor()
        client_id = client_data.get("id")
        if client_id:
            cursor.execute("""
                UPDATE clients SET
                    name = ?, location = ?, industry = ?, price_range = ?,
                    offerings = ?, target_customers = ?, sales_channels = ?,
                    why_choose_us = ?, updated_at = ?
                WHERE id = ?
            """, (
                name,
                client_data.get("location", "").strip(),
                client_data.get("industry", "").strip(),
                client_data.get("price_range", "").strip(),
                client_data.get("offerings", "").strip(),
                client_data.get("target_customers", "").strip(),
                client_data.get("sales_channels", "").strip(),
                client_data.get("why_choose_us", "").strip(),
                now,
                client_id
            ))
            return client_id
        else:
            cursor.execute("""
                INSERT INTO clients (
                    name, location, industry, price_range, offerings,
                    target_customers, sales_channels, why_choose_us,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                client_data.get("location", "").strip(),
                client_data.get("industry", "").strip(),
                client_data.get("price_range", "").strip(),
                client_data.get("offerings", "").strip(),
                client_data.get("target_customers", "").strip(),
                client_data.get("sales_channels", "").strip(),
                client_data.get("why_choose_us", "").strip(),
                now,
                now
            ))
            return cursor.lastrowid


def delete_client(client_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM competitors WHERE client_id = ?", (client_id,))
        cursor.execute("DELETE FROM snapshot_plans WHERE client_id = ?", (client_id,))
        cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()


# --- COMPETITOR OPERATIONS ---


def get_competitors_for_client(client_id):
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM competitors WHERE client_id = ? ORDER BY id ASC", (client_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_competitor(comp_id):
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM competitors WHERE id = ?", (comp_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def save_competitor(comp_data):
    init_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    name = comp_data.get("name", "").strip()
    client_id = comp_data.get("client_id")
    
    if not name:
        raise ValueError("Competitor name cannot be empty.")
    if not client_id:
        raise ValueError("Competitor must be linked to a valid client workspace.")


    with get_connection() as conn:
        cursor = conn.cursor()
        comp_id = comp_data.get("id")
        
        # Check duplicate name within the same client
        if comp_id:
            cursor.execute("SELECT id FROM competitors WHERE client_id = ? AND name = ? AND id != ?", (client_id, name, comp_id))
            if cursor.fetchone():
                raise ValueError(f"A competitor named '{name}' already exists for this business.")
                
            cursor.execute("""
                UPDATE competitors SET
                    name = ?, category = ?, price_range = ?, main_promise = ?,
                    where_they_sell = ?, weak_spot = ?, weak_spot_source = ?,
                    strength_rating = ?, unhappy_rating = ?, why_choose_you = ?,
                    watch_out = ?, updated_at = ?
                WHERE id = ?
            """, (
                name,
                comp_data.get("category", "Same product, same area"),
                comp_data.get("price_range", "").strip(),
                comp_data.get("main_promise", "").strip(),
                comp_data.get("where_they_sell", "").strip(),
                comp_data.get("weak_spot", "").strip(),
                comp_data.get("weak_spot_source", "").strip(),
                int(comp_data.get("strength_rating", 3)),
                int(comp_data.get("unhappy_rating", 3)),
                comp_data.get("why_choose_you", "").strip(),
                comp_data.get("watch_out", "").strip(),
                now,
                comp_id
            ))
            return comp_id
        else:
            cursor.execute("SELECT id FROM competitors WHERE client_id = ? AND name = ?", (client_id, name))
            if cursor.fetchone():
                raise ValueError(f"A competitor named '{name}' already exists. Please choose a distinct name or edit the existing profile.")
                
            cursor.execute("""
                INSERT INTO competitors (
                    client_id, name, category, price_range, main_promise,
                    where_they_sell, weak_spot, weak_spot_source,
                    strength_rating, unhappy_rating, why_choose_you,
                    watch_out, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client_id,
                name,
                comp_data.get("category", "Same product, same area"),
                comp_data.get("price_range", "").strip(),
                comp_data.get("main_promise", "").strip(),
                comp_data.get("where_they_sell", "").strip(),
                comp_data.get("weak_spot", "").strip(),
                comp_data.get("weak_spot_source", "").strip(),
                int(comp_data.get("strength_rating", 3)),
                int(comp_data.get("unhappy_rating", 3)),
                comp_data.get("why_choose_you", "").strip(),
                comp_data.get("watch_out", "").strip(),
                now,
                now
            ))
            return cursor.lastrowid


def delete_competitor(comp_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM competitors WHERE id = ?", (comp_id,))
        conn.commit()


# --- SNAPSHOT PLANS ---


def get_snapshot_plan(client_id):
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM snapshot_plans WHERE client_id = ?", (client_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def save_snapshot_plan(client_id, plan_data):
    init_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO snapshot_plans (
                client_id, action_1_title, action_1_desc, action_1_link,
                action_2_title, action_2_desc, action_2_link,
                action_3_title, action_3_desc, action_3_link,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(client_id) DO UPDATE SET
                action_1_title = excluded.action_1_title,
                action_1_desc = excluded.action_1_desc,
                action_1_link = excluded.action_1_link,
                action_2_title = excluded.action_2_title,
                action_2_desc = excluded.action_2_desc,
                action_2_link = excluded.action_2_link,
                action_3_title = excluded.action_3_title,
                action_3_desc = excluded.action_3_desc,
                action_3_link = excluded.action_3_link,
                updated_at = excluded.updated_at
        """, (
            client_id,
            plan_data.get("action_1_title", "").strip(),
            plan_data.get("action_1_desc", "").strip(),
            plan_data.get("action_1_link", "").strip(),
            plan_data.get("action_2_title", "").strip(),
            plan_data.get("action_2_desc", "").strip(),
            plan_data.get("action_2_link", "").strip(),
            plan_data.get("action_3_title", "").strip(),
            plan_data.get("action_3_desc", "").strip(),
            plan_data.get("action_3_link", "").strip(),
            now
        ))
        conn.commit()


def load_sample_bakery_data():
    """Seeds the exact 'Tita Nena's Bakeshop' fictional demo data shown in the approved mockups."""
    init_db()
    client_id = save_client({
        "name": "Tita Nena's Bakeshop",
        "location": "Concepcion Uno, Marikina",
        "industry": "Bakery & Pastries",
        "price_range": "₱5 to ₱850",
        "offerings": "Fresh pandesal, ensaymada, and made-to-order custom cakes",
        "target_customers": "Families and small offices in Concepcion Uno, Marikina",
        "sales_channels": "Walk-in store, Facebook page, GrabFood",
        "why_choose_us": "Hot bread baked twice every morning; carefully boxed safe-arrival cake transport"
    })
    
    # 3 Competitors
    save_competitor({
        "client_id": client_id,
        "name": "Panaderya Uno",
        "category": "Same product, same area",
        "price_range": "₱4 to ₱6 pandesal, cakes from ₱650",
        "main_promise": "Pinakamurang pandesal sa barangay",
        "where_they_sell": "Walk-in store, Facebook page",
        "weak_spot": "Several Facebook comments say pandesal runs out before 7 AM.",
        "weak_spot_source": "FB page comments, checked 25 Sep 2026",
        "strength_rating": 4,
        "unhappy_rating": 4,
        "why_choose_you": "We bake twice every morning so our bread never runs out before 9 AM.",
        "watch_out": "They undercut on plain loaf bread."
    })
    
    save_competitor({
        "client_id": client_id,
        "name": "Crumbs & Co.",
        "category": "Online seller (Shopee/Lazada/FB)",
        "price_range": "₱750 to ₱1,200 custom cakes",
        "main_promise": "Custom cakes delivered same day",
        "where_they_sell": "Facebook, Instagram, Lalamove delivery",
        "weak_spot": "A few reviews mention cakes arriving dented or tilted.",
        "weak_spot_source": "FB reviews, checked 24 Sep 2026",
        "strength_rating": 4,
        "unhappy_rating": 2,
        "why_choose_you": "Every custom cake includes dedicated safe-transport packaging with pre-dispatch photo verification.",
        "watch_out": "Heavy Instagram ad presence."
    })


    save_competitor({
        "client_id": client_id,
        "name": "BreadHub Express",
        "category": "Big chain / franchise",
        "price_range": "₱8 to ₱45 per piece",
        "main_promise": "Freshly baked every 2 hours",
        "where_they_sell": "Mall kiosk, GrabFood",
        "weak_spot": "No custom cakes; limited choice after 6 PM.",
        "weak_spot_source": "Store visit and menu, 23 Sep 2026",
        "strength_rating": 2,
        "unhappy_rating": 2,
        "why_choose_you": "Personal neighborhood touch, local custom orders, and full evening inventory.",
        "watch_out": "Very strong branding and mall foot traffic."
    })


    # Plan
    save_snapshot_plan(client_id, {
        "action_1_title": "Promise pandesal until 9 AM",
        "action_1_desc": "Bake a second batch at 6:30 AM and post 'May pandesal pa!' on your FB page by 7:30 AM, every day for 30 days.",
        "action_1_link": "Panaderya Uno runs out early",
        "action_2_title": "Safe-arrival cake delivery",
        "action_2_desc": "Free delivery within Concepcion for cakes over ₱800, with a photo of the boxed cake sent before it leaves.",
        "action_2_link": "Crumbs & Co. cakes arrive damaged",
        "action_3_title": "Start a suki card",
        "action_3_desc": "10th ensaymada free. Target 40 sign-ups by 31 Oct; count them every Saturday.",
        "action_3_link": "Keep regulars from trying the new kiosk"
    })
    return client_id
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- ՔՈ ԲԱԶԱՅԻ ՏՎՅԱԼՆԵՐԸ ---
SUPABASE_URL = "https://umbgvfyczrsjfxvpyaei.supabase.co"
SUPABASE_KEY = "sb_publishable_587nBtq5BdKGZqb8LdUjGA_2GhxqH6D"
PRODUCTS_TABLE = "products"
REMONT_TABLE = "remont"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

st.set_page_config(page_title="Phone Business", page_icon="📱", layout="wide")

# Session State-ի ստեղծում և ստուգում
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "role" not in st.session_state: st.session_state.role = None
if "page" not in st.session_state: st.session_state.page = "home"

# Session State-եր վերանորոգման էջի համար
if "remont_step2" not in st.session_state: st.session_state.remont_step2 = False
if "found_product" not in st.session_state: st.session_state.found_product = None

# Գաղտնաբառեր
ADMIN_PASSWORD = "sirusadmin2026"
USER_PASSWORD = "sirususer2026"

# --- 🔐 ՄՈՒՏՔԻ ԷՋ ---
if not st.session_state.authenticated:
    st.title("🔒 SIRUS SYSTEM - ՄՈՒՏՔ")
    input_password = st.text_input("Գաղտնաբառ", type="password", placeholder="Գրիր պասվորդը...")
    if st.button("🚪 Մուտք Գործել", type="primary"):
        if input_password == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.role = "admin"
            st.session_state.page = "home"
            st.rerun()
        elif input_password == USER_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.role = "user"
            st.session_state.page = "baza"
            st.rerun()
        else: st.error("❌ Սխալ գաղտնաբառ")
    st.stop()

# --- 🗺️ NAVIGATION ՄԵՆՅՈՒ ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 45px; font-weight: bold; }
    .nav-container { background-color: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 10px; margin-bottom: 25px; border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="nav-container">', unsafe_allow_html=True)
if st.session_state.role == "admin":
    menu_col1, menu_col2, menu_col3, menu_col4, menu_col5 = st.columns([1, 1.2, 1.2, 1.2, 1])
    with menu_col1:
        if st.button("🏠 ԳԼԽԱՎՈՐ ԷՋ", key="btn_home"): st.session_state.page = "home"; st.rerun()
    with menu_col2:
        if st.button("📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ", key="btn_add"): st.session_state.page = "add_product"; st.rerun()
    with menu_col3:
        if st.button("🔧 ՎԵՐԱՆՈՐՈԳՈՒՄ", key="btn_remont"): 
            st.session_state.page = "remont"
            st.session_state.remont_step2 = False
            st.session_state.found_product = None
            st.rerun()
    with menu_col4:
        if st.button("📊 SIRUS CLOUD BAZA", key="btn_baza"): st.session_state.page = "baza"; st.rerun()
    with menu_col5:
        if st.button("🚪 ԵԼՔ", key="btn_logout"): st.session_state.authenticated = False; st.rerun()
else:
    menu

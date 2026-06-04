import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- 🔒 ԱՊԱՀՈՎ ՏՎՅԱԼՆԵՐԻ ՍՏԱՑՈՒՄ (SECRET-ՆԵՐԻՑ) ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    PRODUCTS_TABLE = st.secrets["PRODUCTS_TABLE"]
    REMONT_TABLE = st.secrets["REMONT_TABLE"]
    HISTORY_TABLE = st.secrets["HISTORY_TABLE"]
    SETTINGS_TABLE = st.secrets["SETTINGS_TABLE"]
except KeyError:
    st.error("❌ Կարգավորումների secret-ները գտնված չեն։ Ստուգեք .streamlit/secrets.toml ֆայլը կամ Cloud-ի settings-ը։")
    st.stop()

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

st.set_page_config(page_title="Phone Business", page_icon="📱", layout="wide")

# ՎԵՐՍԻԱ 3.6 (Գույների թարմացումով)
st.write("")

# Session State-ի սկզբնավորում
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "role" not in st.session_state: st.session_state.role = None
if "page" not in st.session_state: st.session_state.page = "home"
if "remont_step2" not in st.session_state: st.session_state.remont_step2 = False
if "found_product" not in st.session_state: st.session_state.found_product = None

# Ֆունկցիա՝ Բազայից գաղտնաբառերը կարդալու համար
def load_passwords():
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/{SETTINGS_TABLE}", headers=HEADERS)
        if res.status_code == 200 and len(res.json()) > 0:
            data = res.json()[0]
            return data.get("admin_password", "sirusadmin2026"), data.get("user_password", "sirususer2026")
    except:
        pass
    return "sirusadmin2026", "sirususer2026"

# Ֆունկցիա՝ Բազայում գաղտնաբառերը թարմացնելու համար
def update_passwords_in_db(new_admin, new_user):
    res = requests.get(f"{SUPABASE_URL}/rest/v1/{SETTINGS_TABLE}", headers=HEADERS)
    payload = {"admin_password": new_admin, "user_password": new_user}
    
    if res.status_code == 200 and len(res.json()) > 0:
        row_id = res.json()[0]['id']
        requests.patch(f"{SUPABASE_URL}/rest/v1/{SETTINGS_TABLE}?id=eq.{row_id}", headers=HEADERS, json=payload)
    else:
        requests.post(f"{SUPABASE_URL}/rest/v1/{SETTINGS_TABLE}", headers=HEADERS, json=payload)

# Կարդում ենք գաղտնաբառերը
ADMIN_PASSWORD, USER_PASSWORD = load_passwords()

def check_imei_exists(imei):
    res = requests.get(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?imei=eq.{imei}", headers=HEADERS)
    if res.status_code == 200 and len(res.json()) > 0:
        return True
    return False

# --- 🔒 ՄՈՒՏՔԻ ԷՋ ---
if not st.session_state.authenticated:
    st.title("🔒 SIRUS SYSTEM - ՄՈՒՏՔ")
    input_password = st.text_input("Գաղտնաբառ", type="password", placeholder="Գրիր պասվորդը...")
    
    if st.button("🚪 Մուտք Գործել", type="primary"):
        if input_password == ADMIN_PASSWORD:
            st.session_state.authenticated = True; st.session_state.role = "admin"; st.session_state.page = "home"; st.rerun()
        elif input_password == USER_PASSWORD:
            st.session_state.authenticated = True; st.session_state.role = "user"; st.session_state.page = "baza"; st.rerun()
        else: st.error("❌ Սխալ գաղտնաբառ")
    st.stop()

# --- 🗺️ NAVIGATION ՄԵՆՅՈՒ ԵՎ ԱՎՏՈՄԱՏ ԱԴԱՊՏԻՎ ՍՏԱՅԼԵՐ ---
st.markdown("""
    <style>
    .sticky-nav {
        position: fixed; top: 0; left: 0; right: 0; 
        background: linear-gradient(135deg, #1b4332 0%, #aacc00 100%); 
        z-index: 999999; padding: 10px 45px 10px 45px; 
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
    }
    .main-content { margin-top: 110px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 40px; font-weight: bold; }
    .nav-container { background-color: rgba(0, 0, 0, 0.2); padding: 12px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1); }
    
    .table-header { 
        background-color: #b0f2a5; 
        padding: 10px; 
        border-radius: 5px; 
        font-weight: bold; 
        text-align: center; 
        border-bottom: 2px solid #464855; 
        font-size: 12px; 
    }
    
    .table-row-odd { background-color: #769472; padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); align-items: center; text-align: center; font-size: 14px; border-radius: 4px; min-height: 45px; display: flex; justify-content: center; }
    .table-row-even { background-color:#779e7d; padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); align-items: center; text-align: center; font-size: 14px; border-radius: 4px; min-height: 45px; display: flex; justify-content: center; }
    
    /* Ֆիլտրների դաշտերի հատուկ փոքրացված ստայլ */
    div[data-testid="stHeaderBlock"] input {
        padding: 2px 5px !important;
    }
    
    @media (max-width: 768px) {
        .sticky-nav { padding: 5px 10px; position: static !important; }
        .main-content { margin-top: 15px; }
        .nav-container { padding: 6px; }
        .stButton>button { height: 32px !important; font-size: 11px !important; padding: 2px 5px !important; margin-bottom: 4px; }
        .table-header { font-size: 11px !important; padding: 6px 2px !important; }
        .table-row-odd, .table-row-even { font-size: 11px !important; padding: 5px 2px !important; min-height: 35px !important; }
        .stWidgetFormLabel div, label p, .stMarkdown p, span { font-size: 11px !important; }
        .stSelectbox div[data-baseweb="select"], .stTextInput input, .stNumberInput input { font-size: 11px !important; min-height: 28px !important; }
        div[data-testid="stHorizontalBlock"] { gap: 4px !important; }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="sticky-nav">', unsafe_allow_html=True)
st.markdown('<div class="nav-container">', unsafe_allow_html=True)

if st.session_state.role == "admin":
    menu_col1, menu_col2, menu_col3, menu_col4, menu_col5, menu_col6, menu_col7 = st.columns([1, 1.2, 1.2, 1.2, 1.4, 0.6, 0.8])
    with menu_col1:
        if st.button("🏠 ԳԼԽԱՎՈՐ"): st.session_state.page = "home"; st.rerun()
    with menu_col2:
        if st.button("📦 ՁԵՌՔԲԵՐՈՒՄ"): st.session_state.page = "add_product"; st.rerun()
    with menu_col3:
        if st.button("🔧 ՎԵՐԱՆՈՐՈԳՈՒՄ"): st.session_state.page = "remont"; st.session_state.remont_step2 = False; st.session_state.found_product = None; st.rerun()
    with menu_col4:
        if st.button("📊 CLOUD BAZA"): st.session_state.page = "baza"; st.rerun()
    with menu_col5:
        if st.button("📜 ՊԱՏՄՈՒԹՅՈՒՆ"): st.session_state.page = "history"; st.rerun()
    with menu_col6:
        if st.button("⚙️"): st.session_state.page = "settings"; st.rerun()
    with menu_col7:
        if st.button("🚪 ԵԼՔ"): st.session_state.authenticated = False; st.rerun()
else:
    menu_col1, menu_col2 = st.columns([5, 1])
    with menu_col1:
        st.markdown("<h4 style='margin:0; padding-top:5px; color:#4E9F3D;'>📱 SIRUS SYSTEM (User Mode)</h4>", unsafe_allow_html=True)
    with menu_col2:
        if st.button("🚪 ԵԼՔ"): st.session_state.authenticated = False; st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- Pop-up պատուհանների ֆունկցիաները ---
@st.dialog("📝 Ապրանքի Տվյալների Փոփոխում", width="large")
def edit_product_dialog(item):
    st.markdown(f"### ⚙️ Խմբագրել ապրանքը՝ {item['model']} (Համար՝ {item['display_id']})")
    col1, col2 = st.columns(2)
    with col1:
        u_category = st.text_input("📁 Խումբ", value=item.get("category", "Հեռախոս"))
        u_model = st.text_input("📝 Մոդել", value=item.get("model", ""))
        u_storage = st.text_input("💾 Հիշողություն", value=item.get("storage", "") if item.get("storage") else "")
        u_color = st.text_input("🎨 Գույն", value=item.get("color", "") if item.get("color") else "")
    with col2:
        u_imei = st.text_input("🔢 IMEI / Սերիական", value=item.get("imei", ""))
        u_matakarar = st.text_input("📦 Մատակարար", value=item.get("matakarar", "") if item.get("matakarar") else "")
        u_buy_date = st.date_input("📅 Գնելու Ամսաթիվ", datetime.strptime(item["buy_date"], "%Y-%m-%d").date() if item.get("buy_date") else datetime.now())
        u_nshumner = st.text_input("📌 Լրացուցիչ Նշումներ", value=item.get("nshumner", "") if item.get("nshumner") else "")

    if st.button("💾 ՊԱՀՊԱՆԵԼ ՓՈՓՈԽՈՒԹՅՈՒՆՆԵՐԸ", type="primary"):
        update_payload = {
            "category": u_category, "model": u_model, "storage": u_storage if u_storage else None,
            "color": u_color if u_color else None, "imei": u_imei, "matakarar": u_matakarar if u_matakarar else None,
            "buy_date": str(u_buy_date), "nshumner": u_nshumner if u_nshumner else None
        }
        res = requests.patch(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?id=eq.{item['id']}", headers=HEADERS, json=update_payload)
        if res.status_code in [200, 201, 204]: st.success("🎉 Թարմացվեց։"); st.rerun()

@st.dialog("📝 Դեպքի Տվյալների Փոփոխում", width="large")
def edit_remont_dialog(item):
    st.markdown(f"### ⚙️ Խմբագրել՝ {item['model']} (Համար՝ {item['display_id']})")
    col1, col2 = st.columns(2)
    with col1:
        u_model = st.text_input("📝 Մոդել", value=item.get("model", ""))
        u_imei = st.text_input("🔢 IMEI", value=item.get("imei", ""))
        u_rec_date = st.date_input("📅 Ստացման Ամսաթիվ", datetime.strptime(item["received_date"], "%Y-%m-%d").date() if item.get("received_date") else datetime.now())
        u_kampania = st.text_input("🏢 Կամպանիա", value=item.get("kampania", ""))
        u_xndir = st.text_area("❌ Խնդիր", value=item.get("xndir", ""))
    with col2:
        u_komplekt = st.selectbox("💳 Դրամարկղ / Վճարում",

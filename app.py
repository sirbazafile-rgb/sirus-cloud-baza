import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- ՔՈ ԲԱԶԱՅԻ ՏՎՅԱԼՆԵՐԸ ---
SUPABASE_URL = "https://umbgvfyczrsjfxvpyaei.supabase.co"
SUPABASE_KEY = "sb_publishable_587nBtq5BdKGZqb8LdUjGA_2GhxqH6D"
TABLE_NAME = "products"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

st.set_page_config(page_title="Phone Business", page_icon="📱", layout="wide")

# Session State-ի ստեղծում
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "role" not in st.session_state: st.session_state.role = None
if "page" not in st.session_state: st.session_state.page = "home"

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
        else:
            st.error("❌ Սխալ գաղտնաբառ։")
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
        if st.button("🏠 ԳԼԽԱՎՈՐ ԷՋ", key="btn_home"):
            st.session_state.page = "home"; st.rerun()
    with menu_col2:
        if st.button("📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ", key="btn_add"):
            st.session_state.page = "add_product"; st.rerun()
    with menu_col3:
        if st.button("🔧 ՎԵՐԱՆՈՐՈԳՈՒՄ", key="btn_remont"):
            st.session_state.page = "remont"; st.rerun()
    with menu_col4:
        if st.button("📊 SIRUS CLOUD BAZA", key="btn_baza"):
            st.session_state.page = "baza"; st.rerun()
    with menu_col5:
        if st.button("🚪 ԵԼՔ", key="btn_logout"):
            st.session_state.authenticated = False; st.rerun()
else:
    menu_col1, menu_col2 = st.columns([3, 1])
    with menu_col1: st.markdown("### 📊 SIRUS CLOUD BAZA (Դիտման Ռեժիմ)")
    with menu_col2:
        if st.button("🚪 ԵԼՔ", key="btn_logout_user"):
            st.session_state.authenticated = False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 1. 🏠 ԳԼԽԱՎՈՐ ԷՋ ---
if st.session_state.page == "home" and st.session_state.role == "admin":
    st.title("🚀 SIRUS SYSTEM (Admin Mode)")
    st.markdown("### Հեռախոսների և Բիզնեսի Կառավարման Ամպային Համակարգ")
    st.info("💡 Ապրանք մուտքագրելու համար վերևից ընտրիր 📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ կամ 🔧 ՎԵՐԱՆՈՐՈԳՈՒՄ:")

# --- 2. 📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ ---
elif st.session_state.page == "add_product" and st.session_state.role == "admin":
    st.title("📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ")
    
    col1, col2 = st.columns(2)
    with col1:
        model = st.text_input("📝 Մոդել", placeholder="օր. iPhone 15")
        storage = st.text_input("💾 Հիշողություն", placeholder="օր. 128GB")
        color = st.text_input("🎨 Գույն", placeholder="օր. Black")
    with col2:
        matakarar = st.text_input("📦 Մատակարար", placeholder="օր. Dubai")
        buy_date = st.date_input("📅 Գնելու Ամսաթիվ", datetime.now())
        nshumner = st.text_input("📌 Լրացուցիչ Նշումներ", placeholder="Նշումներ...")

    st.markdown("---")
    st.subheader("🔢 IMEI Կոդերի Մուտքագրում")
    
    current_imeis = st.text_area("🔢 IMEI-ների Ցուցակ (Ամեն տողում մեկ IMEI)", placeholder="111111111\n222222222", height=150)
    
    if st.button("💾 ՊԱՀՊԱՆԵԼ ԲՈԼՈՐԸ ԲԱԶԱՅՈՒՄ", type="primary"):
        if model and current_imeis:
            imei_list = [i.strip() for i in current_imeis.split('\n') if i.strip()]
            success_count = 0
            for imei in imei_list:
                payload = {
                    "model": model, "storage": storage, "color": color, 
                    "imei": imei, "matakarar": matakarar if matakarar else None,
                    "buy_date": str(buy_date), "nshumner": nshumner if nshumner else None
                }
                res = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}", headers=HEADERS, json=payload)
                if res.status_code in [200, 201]:
                    success_count += 1
            if success_count > 0:
                st.success(f"🎉 Հաջողությամբ ավելացավ {success_count} հեռախոս։")
                st.balloons()
        else:
            st.warning("⚠️ Խնդրում ենք լրացնել Մոդելը և IMEI կոդերը։")

# --- 3. 🔧 ՎԵՐԱՆՈՐՈԳՄԱՆ ԲԱԺԻՆ ---
elif st.session_state.page == "remont" and st.session_state.role == "admin":
    st.title("🔧 ՎԵՐԱՆՈՐՈԳՄԱՆ ԲԱԺԻՆ")
    st.info("👋 Բռատ ջան, էս էջը պատրաստ է։ Ասա՝ ինչ դաշտեր (պատուհաններ) ավելացնենք այստեղ։")
    
    # Այստեղ կգրենք քո ուզած դաշտերը...

# --- 4. 📊 SIRUS CLOUD BAZA ---
elif st.session_state.page == "baza":
    st.title("📊 SIRUS CLOUD BAZA")
    read_response = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*&order=id.asc", headers=HEADERS)

    if read_response.status_code == 200:
        data = read_response.json()
        if data:
            df = pd.DataFrame(data)
            search_query = st.text_input("🔍 Արագ փնտրում...", placeholder="Գրիր այստեղ...")
            if search_query:
                search_query = search_query.lower()
                mask = df['model'].astype(str).str.lower().str.contains(search_query) | df['imei'].astype(str).str.lower().str.contains(search_query)
                df_filtered = df[mask]
            else:
                df_filtered = df

            st.dataframe(df_filtered, use_container_width=True, hide_index=True)

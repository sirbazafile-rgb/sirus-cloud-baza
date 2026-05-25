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

# --- ԷՋԻ ՍԵԹԻՆԳՆԵՐ ---
st.set_page_config(page_title="Phone Business", page_icon="📱", layout="wide")

# Session State-ի խելացի ստեղծում (որ էլ սխալ չտա)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# Custom CSS
st.markdown("""
    <style>
    .main { padding-top: 1rem; }
    .stButton>button { width: 100%; border-radius: 8px; height: 45px; font-weight: bold; }
    .nav-container {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Գաղտնաբառեր
ADMIN_PASSWORD = "sirusadmin2026"
USER_PASSWORD = "sirususer2026"

# --- 🔐 ՄՈՒՏՔԻ ԷՋ ---
if not st.session_state.authenticated:
    st.title("🔒 SIRUS SYSTEM - ՄՈՒՏՔ")
    st.write("Խնդրում ենք մուտքագրել գաղտնաբառը՝ համակարգից օգտվելու համար։")
    
    input_password = st.text_input("Գաղտնաբառ", type="password", placeholder="Գրիր պասվորդը այստեղ...")
    
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
            st.error("❌ Սխալ գաղտնաբառ։ Խնդրում ենք փորձել կրկին։")
    st.stop()

# --- 🗺️ NAVIGATION ՄԵՆՅՈՒ ---
st.markdown('<div class="nav-container">', unsafe_allow_html=True)

if st.session_state.role == "admin":
    menu_col1, menu_col2, menu_col3, menu_col4 = st.columns([1, 1.2, 1.2, 1])
    with menu_col1:
        if st.button("🏠 ԳԼԽԱՎՈՐ ԷՋ", key="btn_home"):
            st.session_state.page = "home"
            st.rerun()
    with menu_col2:
        if st.button("📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ", key="btn_add"):
            st.session_state.page = "add_product"
            st.rerun()
    with menu_col3:
        if st.button("📊 SIRUS CLOUD BAZA", key="btn_baza"):
            st.session_state.page = "baza"
            st.rerun()
   with menu_col4: # Կամ որ սյունակում որ ուզես
    if st.button("🔧 ՎԵՐԱՆՈՐՈԳՈՒՄ", key="btn_remont"):
        st.session_state.page = "remont"
        st.rerun()
    with menu_col5:
        if st.button("🚪 ԵԼՔ", key="btn_logout"):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.session_state.page = "home"
            st.rerun()
else:
    menu_col1, menu_col2 = st.columns([3, 1])
    with menu_col1:
        st.markdown("### 📊 SIRUS CLOUD BAZA (Դիտման Ռեժիմ)")
    with menu_col2:
        if st.button("🚪 ԵԼՔ", key="btn_logout_user"):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.session_state.page = "home"
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- 1. 🏠 🏠 🏠 ԳԼԽԱՎՈՐ ԷՋ ---
if st.session_state.page == "home" and st.session_state.role == "admin":
    st.title("🚀 SIRUS SYSTEM (Admin Mode)")
    st.markdown("### Հեռախոսների և Բիզնեսի Կառավարման Ամպային Համակարգ")
    st.write("Բարի գալուստ։ Այստեղից կառավարում ես քո ամբողջ բիզնեսը։")
    st.markdown("---")
    st.info("💡 Ապրանք մուտքագրելու համար վերևից ընտրիր 📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ, իսկ բազան տեսնելու համար՝ 📊 SIRUS CLOUD BAZA։")

# --- 2. 📦 📦 📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ ---
elif st.session_state.page == "add_product" and st.session_state.role == "admin":
    st.title("📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ")
    st.caption("✨ Մուտքագրիր նոր ստացված հեռախոսները բազմակի IMEI կոդերով")
    
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
    imei_input = st.text_area("🔢 IMEI Կոդեր (Ամեն տողում գրիր մեկ IMEI)", placeholder="111111111\n222222222", height=150)
    
    if st.button("💾 ՊԱՀՊԱՆԵԼ ԲՈԼՈՐԸ ԲԱԶԱՅՈՒՄ", type="primary"):
        if model and imei_input:
            imei_list = [i.strip() for i in imei_input.split('\n') if i.strip()]
            if not imei_list:
                st.warning("⚠️ Խնդրում ենք գրել գոնե մեկ IMEI կոդ։")
            else:
                success_count = 0
                skipped_imeis = []
                for imei in imei_list:
                    check_url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?imei=eq.{imei}"
                    check_response = requests.get(check_url, headers=HEADERS)
                    if check_response.status_code == 200 and len(check_response.json()) > 0:
                        skipped_imeis.append(imei)
                    else:
                        payload = {
                            "model": model,
                            "storage": storage,
                            "color": color,
                            "imei": imei,
                            "matakarar": matakarar if matakarar else None,
                            "buy_date": str(buy_date),
                            "nshumner": nshumner if nshumner else None
                        }
                        res = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}", headers=HEADERS, json=payload)
                        if res.status_code in [200, 201]:
                            success_count += 1
                if success_count > 0:
                    st.success(f"🎉 Հաջողությամբ ավելացավ {success_count} հեռախոս։")
                    st.balloons()
                if skipped_imeis:
                    st.warning(f"⚠️ Հետևյալ IMEI-ները բաց թողնվեցին. {', '.join(skipped_imeis)}")
        else:
            st.warning("⚠️ Խնդրում ենք լրացնել Մոդելը և IMEI կոդերը։")

# --- 3. 📊 📊 📊 SIRUS CLOUD BAZA ---
elif st.session_state.page == "baza":
    st.title("📊 SIRUS CLOUD BAZA")
    st.caption("✨ Առկա ապրանքների դիտում, որոնում և ֆիլտրում")
    
    read_response = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*&order=id.asc", headers=HEADERS)

    if read_response.status_code == 200:
        data = read_response.json()
        if data:
            df = pd.DataFrame(data)
            search_query = st.text_input("🔍 Արագ փնտրում (Մոդել, IMEI, Գույն, Մատակարար)...", placeholder="Գրիր այստեղ...")
            
            if search_query:
                search_query = search_query.lower()
                mask = (
                    df['model'].astype(str).str.lower().str.contains(search_query) |
                    df['imei'].astype(str).str.lower().str.contains(search_query) |
                    df['color'].astype(str).str.lower().str.contains(search_query) |
                    df['matakarar'].astype(str).str.lower().str.contains(search_query)
                )
                df_filtered = df[mask]
            else:
                df_filtered = df

            if not df_filtered.empty:
                ordered_cols = ['id', 'model', 'storage', 'color', 'imei', 'matakarar', 'buy_date', 'nshumner']
                cols_to_show = [c for c in ordered_cols if c in df_filtered.columns]
                df_clean = df_filtered[cols_to_show]
                
                rename_dict = {
                    'id': 'ID', 'model': 'Մոդել', 'storage': 'Հիշողություն', 
                    'color': 'Գույն', 'imei': 'IMEI', 'matakarar': 'Մատակարար', 
                    'buy_date': 'Գնելու Օր', 'nshumner': 'Նշումներ'
                }
                df_clean = df_clean.rename(columns={k: v for k, v in rename_dict.items() if k in df_clean.columns})
                st.dataframe(df_clean, use_container_width=True, hide_index=True)
                st.caption(f"💡 Ընդհանուր բազայում կա {len(df_clean)} հեռախոս:")
            else:
                st.info("🔍 Համապատասխան հեռախոս չգտնվեց։")
        else:
            st.info("📦 Բազան դեռ դատարկ է։")
    else:
        st.error("Չհաջողվեց կապվել բազայի հետ։")

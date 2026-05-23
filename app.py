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

# Custom CSS՝ Վերևի մենյուն և կոճակները սիրունացնելու համար
st.markdown("""
    <style>
    .main { padding-top: 1rem; }
    .stButton>button { width: 100%; border-radius: 8px; height: 45px; font-weight: bold; }
    div[data-testid="stExpander"] { border-radius: 10px; background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); }
    
    /* Մենյուի ստիլը */
    .nav-container {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)


# --- 🗺️ ՎԵՐԵՎԻ ԳԼԽԱՎՈՐ ՄԵՆՅՈՒ (NAVIGATION BAR) ---
# Օգտագործում ենք սիրուն հորիզոնական կոճակներ էջերի արագ փոխման համար
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
menu_col1, menu_col2, menu_col3 = st.columns([1, 1, 3])

with menu_col1:
    if st.button("🏠 ԳԼԽԱՎՈՐ ԷՋ", key="btn_home"):
        st.session_state.page = "home"
        st.rerun()

with menu_col2:
    if st.button("📊 SIRUS CLOUD BAZA", key="btn_baza"):
        st.session_state.page = "baza"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)


# Պահում ենք ընթացիկ էջի վիճակը (default էջը՝ home)
if "page" not in st.session_state:
    st.session_state.page = "home"


# ==========================================
# 1. 🏠 🏠 🏠 ԳԼԽԱՎՈՐ ԷՋԻ ԿՈՆՏԵՆՏԸ 🏠 🏠 🏠
# ==========================================
if st.session_state.page == "home":
    st.title("🚀 Բարի Գալուստ SIRUS SYSTEM")
    st.markdown("### Հեռախոսների և Բիզնեսի Կառավարման Ամպային Համակարգ")
    st.write("Այս հարթակը նախատեսված է քո ապրանքների, մատակարարների և IMEI կոդերի հաշվառումը ավտոմատացնելու համար։")
    
    st.markdown("---")
    st.info("💡 **Ինչպես անցնել բազային.** Վերևի տողում սեղմիր **`📊 SIRUS CLOUD BAZA`** կոճակը, որպեսզի տեսնես աղյուսակը կամ ավելացնես նոր հեռախոս։")
    st.write("Ցանկացած այլ էջից միշտ կարող ես սեղմել **`🏠 ԳԼԽԱՎՈՐ ԷՋ`**-ին՝ այստեղ վերադառնալու համար։")


# ==========================================
# 2. 📊 📊 📊 ԲԱԶԱՅԻ ԷՋԻ ԿՈՆՏԵՆՏԸ 📊 📊 📊
# ==========================================
elif st.session_state.page == "baza":
    st.title("📊 SIRUS CLOUD BAZA")
    st.caption("✨ Ավելացրու նոր ապրանք կամ փնտրիր եղածները")
    
    # --- ԱՎԵԼԱՑՆԵԼ ՆՈՐ ՀԵՌԱԽՈՍ (ԾԱԼՎՈՂ) ---
    with st.expander("➕ ԱՎԵԼԱՑՆԵԼ ՆՈՐ ՀԵՌԱԽՈՍ", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            model = st.text_input("📝 Մոդել", placeholder="օր. Samsung A17")
            color = st.text_input("🎨 Գույն", placeholder="օր. Black")
        with col2:
            storage = st.text_input("💾 Հիշողություն", placeholder="օր. 6/128GB")
            imei = st.text_input("🔢 IMEI Կոդ", placeholder="օր. 123456789")
        with col3:
            matakarar = st.text_input("📦 Մատակարար", placeholder="օր. Dubai")
            buy_date = st.date_input("📅 Գնելու Ամսաթիվ", datetime.now())

        nshumner = st.text_area("📌 Նշումներ (Պարտադիր չէ)", placeholder="Լրացուցիչ տեղեկություն...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 ՊԱՀՊԱՆԵԼ ԲԱԶԱՅՈՒՄ", type="primary"):
            if model and imei:
                # IMEI ստուգում
                check_url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?imei=eq.{imei}"
                check_response = requests.get(check_url, headers=HEADERS)
                
                if check_response.status_code == 200 and len(check_response.json()) > 0:
                    existing_phone = check_response.json()[0]
                    st.error(f"⚠️ Սխա՛լ. {imei} IMEI-ով հեռախոս արդեն կա բազայում ({existing_phone['model']}):")
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
                    
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}", headers=HEADERS, json=payload)
                    
                    if response.status_code in [200, 201]:
                        st.success(f"🎉 {model}-ը հաջողությամբ ավելացավ:")
                        st.rerun()
                    else:
                        st.error(f"Բազայի սխալ: {response.text}")
            else:
                st.warning("⚠️ Խնդրում ենք լրացնել Մոդել և IMEI դաշտերը։")

    st.markdown("---")

    # --- ՈՐՈՆՈՒՄ ՈՒ ԱՂՅՈՒՍԱԿ ---
    st.subheader("📋 Առկա Ապրանքների Ցուցակ")
    
    read_response = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*&order=id.desc", headers=HEADERS)

    if read_response.status_code == 200:
        data = read_response.json()
        if data:
            df = pd.DataFrame(data)
            
            # Search Bar
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
                st.caption(f"💡 Ցուցադրված է {len(df_clean)} հեռախոս:")
            else:
                st.info("🔍 Համապատասխան հեռախոս չգտնվեց։")
        else:
            st.info("📦 Բազան դեռ դատարկ է։")
    else:
        st.error("Չհաջողվեց կապվել բազայի հետ։")

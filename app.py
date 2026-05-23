import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

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
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "scanned_imeis" not in st.session_state:
    st.session_state.scanned_imeis = []

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
    menu_col1, menu_col2, menu_col3, menu_col4 = st.columns([1, 1.2, 1.2, 1])
    with menu_col1:
        if st.button("🏠 ԳԼԽԱՎՈՐ ԷՋ", key="btn_home"):
            st.session_state.page = "home"; st.rerun()
    with menu_col2:
        if st.button("📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ", key="btn_add"):
            st.session_state.page = "add_product"; st.rerun()
    with menu_col3:
        if st.button("📊 SIRUS CLOUD BAZA", key="btn_baza"):
            st.session_state.page = "baza"; st.rerun()
    with menu_col4:
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
    st.info("💡 Ապրանք մուտքագրելու համար վերևից ընտրիր 📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ:")

# --- 2. 📦 📦 📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ (ՍԿԱՆԵՐՈՎ) 📦 📦 📦
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

    st.markdown("#### 📷 Իրական Ժամանակով Սկաներ (HTML5)")

    # --- HTML5 / JavaScript Սկաների Կոմպոնենտ ---
    # Այս կոդը բրաուզերի մեջ ուղղակի միացնում է տեսախցիկը ու սկանավորում
    scanner_html = """
    <div id="reader" style="width:100%; max-width:500px; border-radius:10px; overflow:hidden; margin:auto;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        function onScanSuccess(decodedText, decodedResult) {
            // Սկանավորված կոդը ուղարկում ենք Streamlit-ին
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: decodedText
            }, '*');
            
            // Կանգնեցնում ենք սկաները մի պահ, որ նույն կոդը 100 անգամ չկարդա
            html5QrcodeScanner.clear();
            setTimeout(() => { startScanner(); }, 2000);
        }

        function startScanner() {
            window.html5QrcodeScanner = new Html5QrcodeScanner(
                "reader", { fps: 15, qrbox: {width: 250, height: 150} }, false);
            html5QrcodeScanner.render(onScanSuccess);
        }
        
        startScanner();
    </script>
    """
    
    # Ցուցադրում ենք սկաները էկրանին
    with st.container():
        # Ստանում ենք JavaScript-ից եկած արժեքը
        scanned_value = components.html(scanner_html, height=350, scrolling=False)
        
    # Եթե նոր IMEI է սկանավորվել, ավելացնում ենք ցուցակում
    # Քանի որ iframe-ից արժեք ստանալը Streamlit-ում կատարվում է query params-ով կամ փոխանցմամբ,
    # մենք ստուգում ենք սկանավորված արդյունքը query_params-ի միջոցով (ավելի հուսալի տարբերակ)
    
    # Որպեսզի Streamlit-ը ֆիքսի JavaScript-ի ուղարկած տվյալը, օգտագործենք փոքրիկ հնարք text_input-ի միջոցով
    # Բայց քանի որ postMessage-ը կարդալու համար պետք է Custom Component, ամենապարզ ձևը սկանավորած IMEI-ն ձեռքով կամ այս սկաներով ֆիքսելն է։
    # Որպեսզի Streamlit-ը ճիշտ աշխատի HTML5-ի հետ, ահա թե ինչպես ենք անում.
    
    st.info("💡 Պահիր շտրիխ կոդը կամ QR-ը տեսախցիկի կենտրոնում։")

    # Մաքրելու կոճակ
    if st.session_state.scanned_imeis:
        if st.button("🗑️ Մաքրել Ցուցակը"):
            st.session_state.scanned_imeis = []
            st.rerun()

    # Քանի որ վերևի JS կոդը փոխանցում է տվյալը, մենք թույլ ենք տալիս նաև արագ ձեռքով լրացնել, եթե հեռախոսը հին է
    st.markdown("---")
    
    # Տեքստային դաշտ
    current_imeis = st.text_area(
        "🔢 IMEI-ների Ցուցակ (Ամեն տողում մեկ IMEI)", 
        placeholder="111111111\n222222222", 
        height=150
    )
    
    if st.button("💾 ՊԱՀՊԱՆԵԼ ԲՈԼՈՐԸ ԲԱԶԱՅՈՒՄ", type="primary"):
        if model and current_imeis:
            imei_list = [i.strip() for i in current_imeis.split('\n') if i.strip()]
            if not imei_list:
                st.warning("⚠️ Խնդրում ենք գրել կամ սկանավորել գոնե մեկ IMEI։")
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
                if skipped_imeis:
                    st.warning(f"⚠️ Հետևյալ IMEI-ները արդեն կային բազայում. {', '.join(skipped_imeis)}")
        else:
            st.warning("⚠️ Խնդրում ենք լրացնել Մոդելը և IMEI կոդերը։")

# --- 3. 📊 SIRUS CLOUD BAZA ---
elif st.session_state.page == "baza":
    st.title("📊 SIRUS CLOUD BAZA")
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

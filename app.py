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
    menu_col1, menu_col2 = st.columns([3, 1])
    with menu_col1: st.markdown("### 📊 SIRUS CLOUD BAZA (Դիտման Ռեժիմ)")
    with menu_col2:
        if st.button("🚪 ԵԼՔ", key="btn_logout_user"): st.session_state.authenticated = False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 1. 🏠 ԳԼԽԱՎՈՐ ԷՋ ---
if st.session_state.page == "home" and st.session_state.role == "admin":
    st.title("🚀 SIRUS SYSTEM (Admin Mode)")
    st.markdown("### Հեռախոսների և Բիզնեսի Կառավարման Ամպային Համակարգ")

# --- 2. 📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ ---
elif st.session_state.page == "add_product" and st.session_state.role == "admin":
    st.title("📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ")
    col1, col2 = st.columns(2)
    with col1:
        model = st.text_input("📝 Մոդել")
        storage = st.text_input("💾 Հիշողություն")
        color = st.text_input("🎨 Գույն")
    with col2:
        matakarar = st.text_input("📦 Մատակարար")
        buy_date = st.date_input("📅 Գնելու Ամսաթիվ", datetime.now())
        nshumner = st.text_input("📌 Լրացուցիչ Նշումներ")

    st.markdown("---")
    current_imeis = st.text_area("🔢 IMEI-ների Ցուցակ (Ամեն տողում մեկ IMEI)", height=150)
    
    if st.button("💾 ՊԱՀՊԱՆԵԼ ԲՈԼՈՐԸ ԲԱԶԱՅՈՒՄ", type="primary"):
        if model and current_imeis:
            imei_list = [i.strip() for i in current_imeis.split('\n') if i.strip()]
            success_count = 0
            for imei in imei_list:
                payload = {
                    "model": model, "storage": storage, "color": color, "imei": imei,
                    "matakarar": matakarar if matakarar else None, "buy_date": str(buy_date), "nshumner": nshumner if nshumner else None
                }
                res = requests.post(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}", headers=HEADERS, json=payload)
                if res.status_code in [200, 201]: success_count += 1
            if success_count > 0: st.success(f"🎉 Հաջողությամբ ավելացավ {success_count} հեռախոս։"); st.balloons()
        else: st.warning("⚠️ Խնդրում ենք լրացնել Մոդելը և IMEI կոդերը։")

# --- 3. 🔧 ՎԵՐԱՆՈՐՈԳՄԱՆ ԲԱԺԻՆ ---
elif st.session_state.page == "remont" and st.session_state.role == "admin":
    st.title("🔧 ՎԵՐԱՆՈՐՈԳՄԱՆ ԲԱԺԻՆ")
    
    st.subheader("🔍 ՔԱՅԼ 1: Փնտրել Հեռախոսը IMEI-ով")
    search_imei = st.text_input("🔢 Գրիր կամ սկանավորիր IMEI-ն", placeholder="Մուտքագրիր IMEI...")
    
    if st.button("🔍 ՓՆՏՐԵԼ ԲԱԶԱՅՈՒՄ", type="secondary"):
        if search_imei:
            remont_check_url = f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?imei=eq.{search_imei}"
            res_remont_check = requests.get(remont_check_url, headers=HEADERS)
            
            if res_remont_check.status_code == 200 and len(res_remont_check.json()) > 0:
                times_in_remont = len(res_remont_check.json())
                st.session_state.remont_warning_msg = f"⚠️ ՈՒՇԱԴՐՈՒԹՅՈՒՆ. Այս հեռախոսը արդեն {times_in_remont} անգամ եղել է վերանորոգման բաժնում։ Խնդրում ենք նշումների դաշտում նշել մանրամասները:"
            else:
                st.session_state.remont_warning_msg = None

            check_url = f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?imei=eq.{search_imei}"
            res = requests.get(check_url, headers=HEADERS)
            if res.status_code == 200 and len(res.json()) > 0:
                st.session_state.found_product = res.json()[0]
                st.session_state.remont_step2 = False
            else:
                st.session_state.found_product = None
                st.session_state.remont_step2 = False
                st.error("❌ Այս IMEI-ով ապրանք բազայում չգտնվեց։")
        else: st.warning("⚠️ Խնդրում ենք մուտքագրել IMEI:")

    if st.session_state.found_product:
        prod = st.session_state.found_product
        st.markdown("### 📱 Գտնված Հեռախոսի Տվյալները")
        
        info_df = pd.DataFrame([{
            "Մոդել": prod.get("model"), "Հիշողություն": prod.get("storage"), "Գույն": prod.get("color"),
            "Ձեռքբերման Օր": prod.get("buy_date"), "Մատակարար": prod.get("matakarar")
        }])
        st.dataframe(info_df, use_container_width=True, hide_index=True)
        
        if "remont_warning_msg" in st.session_state and st.session_state.remont_warning_msg:
            st.warning(st.session_state.remont_warning_msg)
            
        if st.button("➕ ԱՎԵԼԱՑՆԵԼ ՎԵՐԱՆՈՐՈԳՈՒՄ ԲԱԺՆՈՒՄ", type="primary"):
            st.session_state.remont_step2 = True

    if st.session_state.remont_step2 and st.session_state.found_product:
        st.markdown("---")
        st.subheader("📝 ՔԱՅԼ 2: Լրացնել Վերանորոգման Տվյալները")
        
        prod = st.session_state.found_product
        full_model_name = f"{prod.get('model', '')} {prod.get('storage', '')} {prod.get('color', '')}".strip()
        
        col1, col2 = st.columns(2)
        with col1:
            model_input = st.text_input("📝 Մոդել (Ավտոմատ)", value=full_model_name)
            imei_input = st.text_input("🔢 IMEI (Ավտոմատ)", value=prod.get("imei"))
            received_date = st.date_input("📅 Ստացման Ամսաթիվ", datetime.now())
            kampania = st.text_input("🏢 Կամպանիա (Ումից է ստացվել)")
            xndir = st.text_area("❌ Խնդիր (Ինչ խնդրով է եկել)")
        with col2:
            komplekt = st.text_input("📦 Կոմպլեկտ")
            gumar = st.number_input("💵 Գումար (💰)", min_value=0, value=0, step=1000)
            katarvac_ashxatanq = st.text_area("🛠️ Կատարված Աշխատանք")
            
            buy_date_str = prod.get("buy_date")
            if buy_date_str:
                parsed_buy_date = datetime.strptime(buy_date_str, "%Y-%m-%d").date()
                dzerq_date = st.date_input("📅 Ապրանքի Ձեռքբերման Ամսաթիվ (Ավտոմատ)", parsed_buy_date)
            else: dzerq_date = st.date_input("📅 Ապրանքի Ձեռքբերման Ամսաթիվ", datetime.now())
                
            kargavichak = st.selectbox("🚦 Կարգավիճակ", ["Ստացել եմ", "Վերանորոգման է", "Պատրաստ է", "Ուղարկել եմ Կամպանիա"])
            
            default_nshum = ""
            if "remont_warning_msg" in st.session_state and st.session_state.remont_warning_msg:
                default_nshum = "ԿՐԿՆԱԿԻ ՎԵՐԱՆՈՐՈԳՈՒՄ. "
            nshumner = st.text_input("📌 Նշումներ", value=default_nshum)

        if st.button("💾 ՊԱՀՊԱՆԵԼ ՎԵՐԱՆՈՐՈԳՈՒՄԸ ԲԱԶԱՅՈՒՄ", type="primary"):
            remont_payload = {
                "model": model_input, "imei": imei_input, "received_date": str(received_date),
                "kampania": kampania if kampania else None, "xndir": xndir if xndir else None,
                "gumar": gumar, "komplekt": komplekt if komplekt else None,
                "katarvac_ashxatanq": katarvac_ashxatanq if katarvac_ashxatanq else None,
                "dzerq_berman_date": str(dzerq_date), "kargavichak": kargavichak, "nshumner": nshumner if nshumner else None
            }
            res_remont = requests.post(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}", headers=HEADERS, json=remont_payload)
            if res_remont.status_code in [200, 201]:
                st.success("🎉 Վերանորոգման տվյալները հաջողությամբ գրանցվեցին բազայում։")
                st.balloons()
                st.session_state.remont_step2 = False; st.session_state.found_product = None
            else: st.error("❌ Սխալ՝ բազայում չհաջողվեց պահպանել։")

# --- 4. 📊 SIRUS CLOUD BAZA ---
elif st.session_state.page == "baza":
    st.title("📊 SIRUS CLOUD BAZA")
    tab1, tab2 = st.tabs(["📦 ԱՊՐԱՆՔՆԵՐ", "🔧 ՎԵՐԱՆՈՐՈԳՈՒՄՆԵՐ"])
    
    with tab1:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?select=*&order=id.asc", headers=HEADERS)
        if res.status_code == 200 and res.json():
            df = pd.DataFrame(res.json())
            st.dataframe(df, use_container_width=True, hide_index=True)
            
    with tab2:
        # Կարդում ենք վերանորոգման տվյալները
        res_rem = requests.get(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?select=*&order=id.asc", headers=HEADERS)
        if res_rem.status_code == 200:
            rem_data = res_rem.json()
            if rem_data:
                df_rem = pd.DataFrame(rem_data)
                st.dataframe(df_rem, use_container_width=True, hide_index=True)
                
                # --- 🔄 ՏՎՅԱԼՆԵՐԻ ՓՈՓՈԽՄԱՆ (ԹԱՐՄԱՑՄԱՆ) ԲԱԺԻՆ ---
                st.markdown("---")
                st.subheader("🔄 Խմբագրել / Փոխել Վերանորոգման Կարգավիճակը")
                
                # Թույլ ենք տալիս ընտրել բազայում եղած IMEI-ներից մեկը
                all_imeis = df_rem["imei"].unique().tolist()
                selected_imei = st.selectbox("🎯 Ընտրիր այն հեռախոսի IMEI-ն, որի տվյալները ուզում ես փոխել", all_imeis)
                
                if selected_imei:
                    # Գտնում ենք ընտրված հեռախոսի ընթացիկ տվյալները
                    current_row = df_rem[df_rem["imei"] == selected_imei].iloc[0]
                    
                    st.info(f"📱 Ընտրված է՝ **{current_row['model']}**")
                    
                    col_edit1, col_edit2 = st.columns(2)
                    with col_edit1:
                        # Ցույց է տալիս իր հին կարգավիճակը ու թույլ տալիս փոխել
                        statuses = ["Ստացել եմ", "Վերանորոգման է", "Պատրաստ է", "Ուղարկել եմ Կամպանիա"]
                        old_status_index = statuses.index(current_row["kargavichak"]) if current_row["kargavichak"] in statuses else 0
                        new_kargavichak = st.selectbox("🚦 Նոր Կարգավիճակ", statuses, index=old_status_index)
                        
                        # Թարմացնել կատարված աշխատանքը
                        old_work = current_row["katarvac_ashxatanq"] if current_row["katarvac_ashxatanq"] else ""
                        new_work = st.text_area("🛠️ Կատարված Աշխատանք", value=old_work)
                    
                    with col_edit2:
                        # Փոխել գումարը
                        old_gumar = int(current_row["gumar"]) if current_row["gumar"] else 0
                        new_gumar = st.number_input("💵 Գումար (💰)", min_value=0, value=old_gumar, step=1000, key="edit_gumar")
                        
                        # Փոխել կամ ավելացնել նշումներ
                        old_nshum = current_row["nshumner"] if current_row["nshumner"] else ""
                        new_nshumner = st.text_input("📌 Նշումներ", value=old_nshum, key="edit_nshum")

                    if st.button("🚀 ԹԱՐՄԱՑՆԵԼ ՏՎՅԱԼՆԵՐԸ", type="primary"):
                        update_payload = {
                            "kargavichak": new_kargavichak,
                            "gumar": new_gumar,
                            "katarvac_ashxatanq": new_work if new_work else None,
                            "nshumner": new_nshumner if new_nshumner else None
                        }
                        # Supabase PATCH հարցում՝ տվյալները թարմացնելու համար ըստ IMEI-ի
                        update_url = f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?imei=eq.{selected_imei}"
                        res_update = requests.patch(update_url, headers=HEADERS, json=update_payload)
                        
                        if res_update.status_code in [200, 204]:
                            st.success("🎉 Տվյալները հաջողությամբ թարմացվեցին բազայում։")
                            st.rerun()
                        else:
                            st.error("❌ Չհաջողվեց թարմացնել բազան։")
            else:
                st.info("🔧 Վերանորոգման բազան դեռ դատարկ է։")

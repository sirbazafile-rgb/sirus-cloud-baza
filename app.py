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

# Խմբագրման և ջնջման համար նոր վիճակներ
if "edit_imei" not in st.session_state: st.session_state.edit_imei = None
if "delete_imei" not in st.session_state: st.session_state.delete_imei = None
if "remont_step2" not in st.session_state: st.session_state.remont_step2 = False
if "found_product" not in st.session_state: st.session_state.found_product = None

ADMIN_PASSWORD = "sirusadmin2026"
USER_PASSWORD = "sirususer2026"

# --- 🔐 ՄՈՒՏՔԻ ԷՋ ---
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

# --- 🗺️ NAVIGATION ՄԵՆՅՈՒ ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 40px; font-weight: bold; }
    .nav-container { background-color: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 10px; margin-bottom: 25px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .table-header { background-color: #05ebdb; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; border-bottom: 2px solid #464855; font-size: 14px; }
    .table-row { background-color: #1E1E24; padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); align-items: center; text-align: center; font-size: 14px; border-radius: 4px; min-height: 45px; display: flex; justify-content: center; }
    .link-btn button { background-color: transparent !important; color: #ff4b4b !important; border: none !important; text-decoration: underline !important; font-size: 15px !important; text-align: center !important; }
    /* Հաշվիչ տուփերի սիրունացում */
    div[data-testid="stMetric"] { background-color: #e0a96e; padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="nav-container">', unsafe_allow_html=True)
if st.session_state.role == "admin":
    menu_col1, menu_col2, menu_col3, menu_col4, menu_col5 = st.columns([1, 1.2, 1.2, 1.2, 1])
    with menu_col1:
        if st.button("🏠 ԳԼԽԱՎՈՐ ԷՋ"): st.session_state.page = "home"; st.rerun()
    with menu_col2:
        if st.button("📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ"): st.session_state.page = "add_product"; st.rerun()
    with menu_col3:
        if st.button("🔧 ՎԵՐԱՆՈՐՈԳՈՒՄ"): 
            st.session_state.page = "remont"; st.session_state.remont_step2 = False; st.session_state.found_product = None; st.rerun()
    with menu_col4:
        if st.button("📊 SIRUS CLOUD BAZA"): st.session_state.page = "baza"; st.rerun()
    with menu_col5:
        if st.button("🚪 ԵԼՔ"): st.session_state.authenticated = False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- ԱՌԱՆՁԻՆ ՊԱՏՈՒՀԱՆԻ ՖՈՒՆԿՑԻԱՆ (POP-UP) ---
@st.dialog("📱 Հեռախոսի Ամբողջական Ինֆորմացիան", width="large")
def show_details_dialog(row):
    st.markdown(f"### 🔗 {row['model']}")
    st.markdown(f"**🔢 IMEI:** `{row['imei']}`")
    st.markdown("---")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown(f"🏢 **Կամպանիա:** {row['kampania'] if row['kampania'] else '֊'}")
        st.markdown(f"📅 **Ստացման Ամսաթիվ:** {row['received_date']}")
        st.markdown(f"📅 **Ձեռքբերման Ամսաթիվ:** {row['dzerq_berman_date'] if row['dzerq_berman_date'] else '֊'}")
        st.markdown(f"💳 **Վճարման Տեսակ:** `{row['komplekt'] if row['komplekt'] else 'Կանխիկ'}`")
    with col_d2:
        st.markdown(f"💵 **Գումար:** {row['gumar']} 💰")
        status_color = "#FFA500" if row['kargavichak'] == "Վերանորոգման է" else "#00FF00" if row['kargavichak'] == "Պատրաստ է" else "#999999"
        st.markdown(f"🚦 **Կարգավիճակ:** <span style='color:{status_color}; font-weight:bold;'>{row['kargavichak']}</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"❌ **Ի հայտ եկած Խնդիրը:**")
    st.info(row['xndir'] if row['xndir'] else "Նշված չէ")
    
    st.markdown(f"🛠️ **Կատարված Աշխատանք:**")
    st.success(row['katarvac_ashxatanq'] if row['katarvac_ashxatanq'] else "Դեռ ոչինչ չի արվել")
    
    st.markdown(f"📌 **Լրացուցիչ Նշումներ:**")
    st.warning(row['nshumner'] if row['nshumner'] else "Չկան")

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
                st.session_state.remont_warning_msg = f"⚠️ ՈՒՇԱԴՐՈՒԹՅՈՒՆ. Այս հեռախոսը արդեն {times_in_remont} անգամ եղել է վերանորոգման բաժնում։"
            else: st.session_state.remont_warning_msg = None

            check_url = f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?imei=eq.{search_imei}"
            res = requests.get(check_url, headers=HEADERS)
            if res.status_code == 200 and len(res.json()) > 0:
                st.session_state.found_product = res.json()[0]; st.session_state.remont_step2 = False
            else:
                st.session_state.found_product = None; st.session_state.remont_step2 = False
                st.error("❌ Այս IMEI-ով ապրանք բազայում չգտնվեց։")

    if st.session_state.found_product:
        prod = st.session_state.found_product
        st.markdown("### 📱 Գտնված Հեռախոսի Տվյալները")
        info_df = pd.DataFrame([{"Մոդել": prod.get("model"), "Հիշողություն": prod.get("storage"), "Գույն": prod.get("color"), "Ձեռքբերման Օր": prod.get("buy_date")}])
        st.dataframe(info_df, use_container_width=True, hide_index=True)
        if "remont_warning_msg" in st.session_state and st.session_state.remont_warning_msg:
            st.warning(st.session_state.remont_warning_msg)
        if st.button("➕ ԱՎԵԼԱՑՆԵԼ ՎԵՐԱՆՈՐՈԳՈՒՄ ԲԱԺՆՈՒՄ", type="primary"): st.session_state.remont_step2 = True

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
            vcharman_tesak = st.selectbox("💳 ՎՃԱՐՄԱՆ ՏԵՍԱԿ", ["Կանխիկ", "Անկանխիկ"])
            gumar = st.number_input("💵 Գումար (💰)", min_value=0, value=0, step=1000)
            katarvac_ashxatanq = st.text_area("🛠️ Կատարված Աշխատանք")
            buy_date_str = prod.get("buy_date")
            dzerq_date = st.date_input("📅 Ապրանքի Ձեռքբերման Ամսաթիվ", datetime.strptime(buy_date_str, "%Y-%m-%d").date() if buy_date_str else datetime.now())
            kargavichak = st.selectbox("🚦 Կարգավիճակ", ["Ստացել եմ", "Վերանորոգման է", "Պատրաստ է", "Ուղարկել եմ Կամպանիա"])
            nshumner = st.text_input("📌 Նշումներ", value="ԿՐԿՆԱԿԻ ՎԵՐԱՆՈՐՈԳՈՒՄ. " if "remont_warning_msg" in st.session_state and st.session_state.remont_warning_msg else "")

        if st.button("💾 ՊԱՀՊԱՆԵԼ ԲՈԼՈՐԸ ԲԱԶԱՅՈՒՄ", type="primary"):
            remont_payload = {
                "model": model_input, "imei": imei_input, "received_date": str(received_date), "kampania": kampania if kampania else None,
                "xndir": xndir if xndir else None, "gumar": gumar, "komplekt": vcharman_tesak,
                "katarvac_ashxatanq": katarvac_ashxatanq if katarvac_ashxatanq else None, "dzerq_berman_date": str(dzerq_date), "kargavichak": kargavichak, "nshumner": nshumner if nshumner else None
            }
            if requests.post(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}", headers=HEADERS, json=remont_payload).status_code in [200, 201]:
                st.success("🎉 Տվյալները գրանցվեցին։"); st.balloons()
                st.session_state.remont_step2 = False; st.session_state.found_product = None

# --- 4. 📊 SIRUS CLOUD BAZA ---
elif st.session_state.page == "baza":
    st.title("📊 SIRUS CLOUD BAZA")
    tab1, tab2 = st.tabs(["📦 ԱՊՐԱՆՔՆԵՐ", "🔧 ՎԵՐԱՆՈՐՈԳՈՒՄՆԵՐ"])
    
    with tab1:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?select=*&order=id.asc", headers=HEADERS)
        if res.status_code == 200 and res.json():
            st.dataframe(pd.DataFrame(res.json()), use_container_width=True, hide_index=True)

    # --- TAB 2: 🔧 ՎԵՐԱՆՈՐՈԳՈՒՄՆԵՐ ---
    with tab2:
        res_rem = requests.get(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?select=*&order=id.asc", headers=HEADERS)
        if res_rem.status_code == 200 and res_rem.json():
            rem_list = res_rem.json()
            
            # --- 🧮 ՀԱՇՎԻՉՆԵՐԻ ԲԱԺԻՆ ---
            total_gumar = sum(int(item['gumar']) for item in rem_list)
            total_cash = sum(int(item['gumar']) for item in rem_list if item.get('komplekt') == "Կանխիկ" or item.get('komplekt') is None)
            total_card = sum(int(item['gumar']) for item in rem_list if item.get('komplekt') == "Անկանխիկ")
            
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("💰 Ընդհանուր Շրջանառություն", f"{total_gumar:,} Դրամ")
            m_col2.metric("💵 Ընդհանուր Կանխիկ", f"{total_cash:,} Դրամ")
            m_col3.metric("💳 Ընդհանուր Անկանխիկ", f"{total_card:,} Դրամ")
            
            st.markdown(" ")
            
            # --- 📥 EXCEL / CSV ՏՊԵԼՈՒ ԿՈՃԱԿ ---
            df_remont = pd.DataFrame(rem_list)
            df_excel = df_remont.rename(columns={
                'model': 'Մոդել', 'imei': 'IMEI', 'kampania': 'Կամպանիա', 'gumar': 'Գումար (Դրամ)',
                'komplekt': 'Վճարման Տեսակ', 'received_date': 'Ստացման Ամսաթիվ', 'xndir': 'Խնդիր',
                'katarvac_ashxatanq': 'Կատարված Աշխատանք', 'dzerq_berman_date': 'Ձեռքբերման Ամսաթիվ',
                'kargavichak': 'Կարգավիճակ', 'nshumner': 'Նշումներ'
            })
            if 'id' in df_excel.columns: df_excel = df_excel.drop(columns=['id'])
            csv_data = df_excel.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📥 ՏՊԵԼ / ՆԵՐԲԵՌՆԵԼ EXCEL ՖԱՅԼԸ",
                data=csv_data,
                file_name=f"remont_baza_{datetime.now().strftime('%Y-%m-%d')}.csv",
                mime="text/csv",
                type="secondary"
            )
            
            st.markdown("---")
            
            # Աղյուսակի 7 Գլխավոր Սյուները
            h_cols = st.columns([2.2, 1.6, 1.4, 1.4, 1.4, 1.4, 0.8])
            h_cols[0].markdown("<div class='table-header'>📱 Մոդել (Սեղմիր՝ տեսնելու)</div>", unsafe_allow_html=True)
            h_cols[1].markdown("<div class='table-header'>🔢 IMEI</div>", unsafe_allow_html=True)
            h_cols[2].markdown("<div class='table-header'>🏢 Կամպանիա</div>", unsafe_allow_html=True)
            h_cols[3].markdown("<div class='table-header'>💵 Գումար (Տեսակ)</div>", unsafe_allow_html=True)
            h_cols[4].markdown("<div class='table-header'>📅 Ամսաթիվ</div>", unsafe_allow_html=True)
            h_cols[5].markdown("<div class='table-header'>🚦 Կարգավիճակ</div>", unsafe_allow_html=True)
            h_cols[6].markdown("<div class='table-header'>⚙️</div>", unsafe_allow_html=True)
            
            for row in rem_list:
                r_cols = st.columns([2.2, 1.6, 1.4, 1.4, 1.4, 1.4, 0.8])
                
                # 📱 Մոդել կոճակ
                with r_cols[0]:
                    st.markdown("<div class='link-btn'>", unsafe_allow_html=True)
                    if st.button(f"🔎 {row['model']}", key=f"view_{row['imei']}", help="Տեսնել ամբողջական տվյալները"):
                        show_details_dialog(row)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                r_cols[1].markdown(f"<div class='table-row'><code>{row['imei']}</code></div>", unsafe_allow_html=True)
                r_cols[2].markdown(f"<div class='table-row'>{row['kampania'] if row['kampania'] else '֊'}</div>", unsafe_allow_html=True)
                
                # 💵 Գումար + Տեսակ (Կանխիկ/Անկանխիկ)
                v_type = row.get('komplekt') if row.get('komplekt') else "Կանխիկ"
                type_emoji = "💵" if v_type == "Կանխիկ" else "💳"
                r_cols[3].markdown(f"<div class='table-row'><b>{row['gumar']} 💰</b><br><small style='color:#aaa;'>{type_emoji} {v_type}</small></div>", unsafe_allow_html=True)
                
                r_cols[4].markdown(f"<div class='table-row'>{row['received_date']}</div>", unsafe_allow_html=True)
                
                status_color = "#FFA500" if row['kargavichak'] == "Վերանորոգման է" else "#00FF00" if row['kargavichak'] == "Պատրաստ է" else "#999999"
                r_cols[5].markdown(f"<div class='table-row' style='color:{status_color}; font-weight:bold;'>{row['kargavichak']}</div>", unsafe_allow_html=True)
                
                # ⚙️ Խմբագրել և Ջնջել
                with r_cols[6]:
                    btn_col1, btn_col2 = st.columns(2)
                    if btn_col1.button("📝", key=f"edit_{row['imei']}"):
                        st.session_state.edit_imei = row['imei']; st.session_state.delete_imei = None; st.rerun()
                    if st.session_state.role == "admin" and btn_col2.button("🗑️", key=f"del_{row['imei']}"):
                        st.session_state.delete_imei = row['imei']; st.session_state.edit_imei = None; st.rerun()

            # --- 📝 ԽՄԲԱԳՐՄԱՆ ՊԱՏՈՒՀԱՆ ---
            if st.session_state.edit_imei:
                st.markdown("---")
                edit_row = next(item for item in rem_list if item["imei"] == st.session_state.edit_imei)
                st.subheader(f"📝 Խմբագրել՝ {edit_row['model']}")
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    statuses = ["Ստացել եմ", "Վերանորոգման է", "Պատրաստ է", "Ուղարկել եմ Կամպանիա"]
                    up_kargavichak = st.selectbox("🚦 Կարգավիճակ", statuses, index=statuses.index(edit_row["kargavichak"]) if edit_row["kargavichak"] in statuses else 0)
                    up_work = st.text_area("🛠️ Կատարված Աշխատանք", value=edit_row["katarvac_ashxatanq"] if edit_row["katarvac_ashxatanq"] else "")
                with col_e2:
                    current_pay_type = edit_row.get("komplekt") if edit_row.get("komplekt") else "Կանխիկ"
                    up_pay_type = st.selectbox("💳 Վճարման Տեսակ", ["Կանխիկ", "Անկանխիկ"], index=0 if current_pay_type == "Կանխիկ" else 1)
                    up_gumar = st.number_input("💵 Գումար", min_value=0, value=int(edit_row["gumar"]), step=1000)
                    up_nshum = st.text_input("📌 Նշումներ", value=edit_row["nshumner"] if edit_row["nshumner"] else "")
                
                if st.button("🚀 ԹԱՐՄԱՑՆԵԼ", type="primary"):
                    payload = {"kargavichak": up_kargavichak, "gumar": up_gumar, "komplekt": up_pay_type, "katarvac_ashxatanq": up_work, "nshumner": up_nshum}
                    if requests.patch(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?imei=eq.{st.session_state.edit_imei}", headers=HEADERS, json=payload).status_code in [200, 204]:
                        st.session_state.edit_imei = None; st.rerun()
                if st.button("❌ Չեղարկել"): st.session_state.edit_imei = None; st.rerun()

            # --- 🗑️ ՋՆՋՄԱՆ ՊԱՏՈՒՀԱՆ ---
            if st.session_state.delete_imei:
                st.markdown("---")
                del_pass = st.text_input("🔒 Մուտքագրիր գաղտնաբառը (89)", type="password")
                if st.button("💥 ՀԱՍՏԱՏԵԼ ՋՆՋՈՒՄԸ", type="primary") and del_pass == "89":
                    if requests.delete(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?imei=eq.{st.session_state.delete_imei}", headers=HEADERS).status_code in [200, 204]:
                        st.session_state.delete_imei = None; st.rerun()
                if st.button("❌ Չեղարկել", key="cancel_del"): st.session_state.delete_imei = None; st.rerun()
        else: st.info("🔧 Վերանորոգման բազան դեռ դատարկ է։")

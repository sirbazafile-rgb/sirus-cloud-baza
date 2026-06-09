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

# Session State-ի սկզբնավորում
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "role" not in st.session_state: st.session_state.role = None
if "page" not in st.session_state: st.session_state.page = "home"
if "remont_step2" not in st.session_state: st.session_state.remont_step2 = False
if "found_product" not in st.session_state: st.session_state.found_product = None

# Ֆունկցիա՝ Բազայից գաղտնաբառերը կարդալու համար
def load_passwords():
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/{SETTINGS_TABLE}?select=*", headers=HEADERS)
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
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/{SETTINGS_TABLE}?id=eq.{row_id}", headers=HEADERS, json=payload)
        return r.status_code in [200, 201, 204]
    else:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/{SETTINGS_TABLE}", headers=HEADERS, json=payload)
        return r.status_code in [200, 201]

ADMIN_PASSWORD, USER_PASSWORD = load_passwords()

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

# --- 🗺️ STYLES ---
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
        background-color: #b0f2a5; padding: 10px; border-radius: 5px; 
        font-weight: bold; text-align: center; border-bottom: 2px solid #464855; font-size: 12px; 
    }
    .table-row-odd { background-color: #769472; padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); align-items: center; text-align: center; font-size: 14px; border-radius: 4px; min-height: 45px; display: flex; justify-content: center; }
    .table-row-even { background-color:#779e7d; padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); align-items: center; text-align: center; font-size: 14px; border-radius: 4px; min-height: 45px; display: flex; justify-content: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="sticky-nav"><div class="nav-container">', unsafe_allow_html=True)
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
    with menu_col1: st.markdown("<h4 style='margin:0; padding-top:5px; color:#4E9F3D;'>📱 SIRUS SYSTEM (User Mode)</h4>", unsafe_allow_html=True)
    with menu_col2:
        if st.button("🚪 ԵԼՔ"): st.session_state.authenticated = False; st.rerun()
st.markdown('</div></div>', unsafe_allow_html=True)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- Dialogs (Խմբագրման և Ջնջման Պատուհաններ) ---
@st.dialog("📝 Ապրանքի Տվյալների Փոփոխում", width="large")
def edit_product_dialog(item):
    st.markdown(f"### ⚙️ Խմբագրել ապրանքը՝ {item['model']}")
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

    if st.button("💾 ՊԱՀՊԱՆԵԼ", type="primary"):
        update_payload = {
            "category": u_category, "model": u_model, "storage": u_storage if u_storage else None,
            "color": u_color if u_color else None, "imei": u_imei, "matakarar": u_matakarar if u_matakarar else None,
            "buy_date": str(u_buy_date), "nshumner": u_nshumner if u_nshumner else None
        }
        res = requests.patch(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?id=eq.{item['id']}", headers=HEADERS, json=update_payload)
        if res.status_code in [200, 201, 204]: st.success("🎉 Թարմացվեց։"); st.rerun()

@st.dialog("📝 Դեպքի Տվյալների Փոփոխում", width="large")
def edit_remont_dialog(item):
    st.markdown(f"### ⚙️ Խմբագրել Ռեմոնտը")
    col1, col2 = st.columns(2)
    with col1:
        u_model = st.text_input("📝 Մոդել", value=item.get("model", ""))
        u_imei = st.text_input("🔢 IMEI", value=item.get("imei", ""))
        u_rec_date = st.date_input("📅 Ստացման Ամսաթիվ", datetime.strptime(item["received_date"], "%Y-%m-%d").date() if item.get("received_date") else datetime.now())
        u_kampania = st.text_input("🏢 Կամպանիա", value=item.get("kampania", ""))
        u_xndir = st.text_area("❌ Խնդիր", value=item.get("xndir", ""))
    with col2:
        u_komplekt = st.selectbox("💳 Դրամարկղ", ["Կանխիկ", "Անկանխիկ"], index=0 if item.get("komplekt") == "Կանխիկ" else 1)
        u_gumar = st.number_input("💵 Գումար", min_value=0, value=int(item.get("gumar", 0)), step=1000)
        u_work = st.text_area("🛠️ Աշխատանք", value=item.get("katarvac_ashxatanq", ""))
        u_buy_date = st.date_input("📅 Ձեռքբերման Օր", datetime.strptime(item["dzerq_berman_date"], "%Y-%m-%d").date() if item.get("dzerq_berman_date") else datetime.now())
        status_list = ["Ստացել եմ", "Վերանորոգման է", "Պատրաստ է", "Ուղարկել եմ Կամպանիա"]
        u_status = st.selectbox("🚦 Կարգավիճակ", status_list, index=status_list.index(item["kargavichak"]) if item.get("kargavichak") in status_list else 0)
        u_nshum = st.text_input("📌 Նշումներ", value=item.get("nshumner", ""))

    if st.button("💾 ԹԱՐՄԱՑՆԵԼ", type="primary"):
        update_payload = {
            "model": u_model, "imei": u_imei, "received_date": str(u_rec_date), "kampania": u_kampania,
            "xndir": u_xndir, "komplekt": u_komplekt, "gumar": u_gumar, "katarvac_ashxatanq": u_work,
            "dzerq_berman_date": str(u_buy_date), "kargavichak": u_status, "nshumner": u_nshum
        }
        res = requests.patch(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?id=eq.{item['id']}", headers=HEADERS, json=update_payload)
        if res.status_code in [200, 201, 204]: st.success("🎉 Թարմացվեց։"); st.rerun()

@st.dialog("🗑️ Հաստատել Ջնջումը")
def delete_remont_dialog(item_id):
    pass_input = st.text_input("Գաղտնաբառ (12)", type="password")
    if st.button("🗑️ ՋՆՋԵԼ", type="primary"):
        if pass_input == "12":
            if requests.delete(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?id=eq.{item_id}", headers=HEADERS).status_code in [200, 204]:
                st.success("Ջնջվեց։"); st.rerun()

@st.dialog("📱 Հեռախոսի Ամբողջական Ինֆորմացիան", width="large")
def show_details_dialog(row):
    st.markdown(f"### 🔗 {row['model']}")
    st.markdown(f"**🔢 IMEI:** `{row['imei']}`")
    st.info(f"❌ **Խնդիրը:** {row.get('xndir', 'Նշված չէ')}")
    st.success(f"🛠️ **Աշխատանք:** {row.get('katarvac_ashxatanq', 'Արված չէ')}")

# --- 1. 🏠 ԳԼԽԱՎՈՐ ---
if st.session_state.page == "home" and st.session_state.role == "admin":
    st.title("🚀 SIRUS SYSTEM (Admin Mode)")
    st.markdown("### Հեռախոսների Ամպային Համակարգ")

# --- 2. 📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ (Bulk Insert) ---
elif st.session_state.page == "add_product" and st.session_state.role == "admin":
    st.title("📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ")
    category = st.selectbox("📁 Խումբ", ["Հեռախոս", "Աքսեսուար", "Պլանշետ"])
    model = st.text_input("📝 Մոդել")
    storage = st.text_input("💾 Հիշողություն")
    color = st.text_input("🎨 Գույն")
    current_imeis = st.text_area("🔢 IMEI-ներ (ամեն տողում մեկ հատ)")
    
    if st.button("💾 ՊԱՀՊԱՆԵԼ ԱՄԲՈՂՋԸ ՄԻԱՆԳԱՄԻՑ", type="primary"):
        if model and current_imeis:
            imei_list = [i.strip() for i in current_imeis.split('\n') if i.strip()]
            total_count = len(imei_list)
            
            bulk_payload = [
                {
                    "category": category, "model": model, "storage": storage if storage else None, 
                    "color": color if color else None, "imei": imei, "buy_date": str(datetime.now().date())
                } for imei in imei_list
            ]
            
            with st.spinner(f"⏳ Ավելացվում է {total_count} ապրանք..."):
                res = requests.post(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}", headers=HEADERS, json=bulk_payload)
                if res.status_code in [200, 201, 204]:
                    st.success(f"🎉 Հաջողությամբ բազա ավելացվեց {total_count} հատ հեռախոս։")
                else: st.error(f"❌ Բազայի սխալ։ Status: {res.status_code}")

# --- 3. 🔧 ՎԵՐԱՆՈՐՈԳՈՒՄ ---
elif st.session_state.page == "remont" and st.session_state.role == "admin":
    st.title("🔧 ՎԵՐԱՆՈՐՈԳՄԱՆ ԲԱԺԻՆ")
    col_s1, col_s2 = st.columns([4, 1])
    with col_s1: search_imei = st.text_input("🔢 Մուտքագրեք կամ սկանավորեք IMEI / Սերիական համարը", placeholder="Օրինակ՝ 3529...")
    with col_s2:
        st.write(""); search_btn = st.button("🔍 ՓՆՏՐԵԼ", type="primary")

    if search_btn:
        if search_imei.strip():
            with st.spinner("⏳ Որոնվում է..."):
                res_prod = requests.get(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?imei=eq.{search_imei.strip()}", headers=HEADERS)
                if res_prod.status_code == 200 and len(res_prod.json()) > 0:
                    st.session_state.found_product = res_prod.json()[0]; st.session_state.remont_step2 = True
                    st.success("📱 Ապրանքը գտնվեց պահեստում։")
                else:
                    st.session_state.found_product = {"model": "", "imei": search_imei.strip()}; st.session_state.remont_step2 = True
                    st.warning("⚠️ Պահեստում չգտնվեց, բայց կարող եք գրանցել ձեռքով։")

    if st.session_state.remont_step2:
        st.markdown("---")
        prod = st.session_state.found_product
        col1, col2 = st.columns(2)
        with col1:
            model_input = st.text_input("📝 Մոդել", value=prod.get('model', ''))
            imei_input = st.text_input("🔢 IMEI / Սերիական", value=prod.get('imei', ''))
            kampania = st.text_input("🏢 Կամպանիա")
            xndir = st.text_area("❌ Խնդիր")
        with col2:
            komplekt = st.selectbox("💳 Դրամարկղ", ["Կանխիկ", "Անկանխիկ"])
            gumar = st.number_input("💵 Վերանորոգման Արժեք", min_value=0, value=0)
            kargavichak = st.selectbox("🚦 Կարգավիճակ", ["Ստացել եմ", "Վերանորոգման է", "Պատրաստ է"])
            nshumner = st.text_input("📌 Նշումներ")
        
        if st.button("💾 ԳՐԱՆՑԵԼ ՎԵՐԱՆՈՐՈԳՈՒՄԸ", type="secondary"):
            if model_input and imei_input:
                remont_payload = {
                    "model": model_input, "imei": imei_input, "kampania": kampania if kampania else None,
                    "xndir": xndir, "komplekt": komplekt, "gumar": gumar, "kargavichak": kargavichak, 
                    "received_date": str(datetime.now().date()), "nshumner": nshumner if nshumner else None
                }
                res_save = requests.post(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}", headers=HEADERS, json=remont_payload)
                if res_save.status_code in [200, 201, 204]:
                    st.success("🎉 Վերանորոգումը գրանցվեց։"); st.session_state.remont_step2 = False; st.session_state.found_product = None; st.rerun()

# --- 4. 📊 SIRUS CLOUD BAZA (⚡ ԽԵԼԱՑԻ ՈՐՈՆՄԱՆ ՏԱՐԲԵՐԱԿ) ---
elif st.session_state.page == "baza":
    st.title("📊 SIRUS CLOUD BAZA")
    tab1, tab2 = st.tabs(["📦 ԱՊՐԱՆՔՆԵՐ", "🔧 ՎԵՐԱՆՈՐՈԳՈՒՄՆԵՐ"])
    
    with tab1:
        st.markdown("#### ⚡ Որոնել Ապրանքներ պահեստից")
        col_f1, col_f2 = st.columns(2)
        with col_f1: search_model = st.text_input("📝 Խելացի Որոնում (Մոդել/Հիշող./Գույն)", placeholder="Օրինակ՝ Samsung 8/128 Black...", key="p_mod")
        with col_f2: search_imei = st.text_input("🔢 Փնտրել ըստ IMEI-ի", placeholder="Սկանավորեք կամ գրեք IMEI...", key="p_imei")
        
        if not search_model.strip() and not search_imei.strip():
            st.info("🔍 Մուտքագրեք Մոդելը, Հիշողությունը, Գույնը կամ IMEI-ն վերևի դաշտերում՝ տվյալները տեսնելու համար։")
        else:
            query_params = "select=*&order=id.desc&limit=200"
            
            # --- 🚀 ԽԵԼԱՑԻ ՖԻԼՏՐԻ ՏՐԱՄԱԲԱՆՈՒԹՅՈՒՆԸ ---
            if search_model.strip():
                words = [w.strip() for w in search_model.strip().split() if w.strip()]
                # Յուրաքանչյուր բառի համար ստեղծում ենք (model, storage, color) ֆիլտր
                for word in words:
                    query_params += f"&or=(model.ilike.*{word}*,storage.ilike.*{word}*,color.ilike.*{word}*)"
            
            if search_imei.strip(): 
                query_params += f"&imei=eq.{search_imei.strip()}"

            with st.spinner("⏳ Բեռնվում է..."):
                res = requests.get(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?{query_params}", headers=HEADERS)
                
            if res.status_code == 200:
                products_data = res.json()
                if len(products_data) > 0:
                    st.success(f"📊 Գտնվել է {len(products_data)} ապրանք։")
                    p_cols = st.columns([0.8, 2.2, 1.2, 1.2, 2.3, 1.5, 1.3, 1.1])
                    headers_text = ["🆔 ID", "📝 Մոդել", "💾 Հիշող.", "🎨 Գույն", "🔢 IMEI", "📁 Խումբ", "📅 Գնելու Օր", "📝 Ուղղել"]
                    for idx, h in enumerate(headers_text): p_cols[idx].markdown(f"<div class='table-header'>{h}</div>", unsafe_allow_html=True)
                    
                    for idx, row in enumerate(products_data):
                        row_style = "table-row-even" if idx % 2 == 1 else "table-row-odd"
                        r_cols = st.columns([0.8, 2.2, 1.2, 1.2, 2.3, 1.5, 1.3, 1.1])
                        r_cols[0].markdown(f"<div class='{row_style}'><code>{idx+1}</code></div>", unsafe_allow_html=True)
                        r_cols[1].markdown(f"<div class='{row_style}'><b>{row['model']}</b></div>", unsafe_allow_html=True)
                        r_cols[2].markdown(f"<div class='{row_style}'>{row['storage'] if row['storage'] else '֊'}</div>", unsafe_allow_html=True)
                        r_cols[3].markdown(f"<div class='{row_style}'>{row['color'] if row['color'] else '֊'}</div>", unsafe_allow_html=True)
                        r_cols[4].markdown(f"<div class='{row_style}'><code>{row['imei']}</code></div>", unsafe_allow_html=True)
                        r_cols[5].markdown(f"<div class='{row_style}'>{row.get('category', 'Հեռախոս')}</div>", unsafe_allow_html=True)
                        r_cols[6].markdown(f"<div class='{row_style}'>{row['buy_date'] if row['buy_date'] else '֊'}</div>", unsafe_allow_html=True)
                        with r_cols[7]:
                            if st.session_state.role == "admin":
                                if st.button("📝", key=f"edit_p_{row['id']}"): edit_product_dialog(row)
                            else: st.write("🔒")
                else:
                    st.warning("❌ Ոչ մի ապրանք չգտնվեց այդ տվյալներով։")

    with tab2:
        st.markdown("#### ⚡ Որոնել Վերանորոգումներ")
        col_r1, col_r2 = st.columns(2)
        with col_r1: search_rem_model = st.text_input("📝 Խելացի Որոնում (Ռեմոնտ)", placeholder="Գրեք Մոդել/Հիշող./Կամպանիա...", key="r_mod")
        with col_r2: search_rem_imei = st.text_input("🔢 IMEI (Ռեմոնտ)", placeholder="Գրեք IMEI-ն...", key="r_imei")

        if not search_rem_model.strip() and not search_rem_imei.strip():
            st.info("🔍 Մուտքագրեք տվյալները վերևի դաշտերում՝ ռեմոնտները տեսնելու համար։")
        else:
            rem_params = "select=*&order=id.desc&limit=200"
            
            if search_rem_model.strip():
                rem_words = [w.strip() for w in search_rem_model.strip().split() if w.strip()]
                for r_word in rem_words:
                    rem_params += f"&or=(model.ilike.*{r_word}*,kampania.ilike.*{r_word}*)"
                    
            if search_rem_imei.strip(): 
                rem_params += f"&imei=eq.{search_rem_imei.strip()}"

            with st.spinner("⏳ Որոնվում է..."):
                res_rem = requests.get(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?{rem_params}", headers=HEADERS)
                
            if res_rem.status_code == 200:
                remont_data = res_rem.json()
                if len(remont_data) > 0:
                    rem_cols = st.columns([0.8, 1.5, 2, 1.5, 1.2, 1.2, 1, 1, 1])
                    headers_rem = ["🆔 ID", "📝 Մոդել", "🔢 IMEI", "🏢 Կամպանիա", "💵 Գումար", "🚦 Կարգավիճակ", "📱 Ինֆո", "📝 Ուղղել", "🗑️ Ջնջել"]
                    for idx, h in enumerate(headers_rem): rem_cols[idx].markdown(f"<div class='table-header'>{h}</div>", unsafe_allow_html=True)
                    
                    for idx, rem_item in enumerate(remont_data):
                        row_style = "table-row-even" if idx % 2 == 1 else "table-row-odd"
                        r_cols = st.columns([0.8, 1.5, 2, 1.5, 1.2, 1.2, 1, 1, 1])
                        r_cols[0].markdown(f"<div class='{row_style}'><code>{idx+1}</code></div>", unsafe_allow_html=True)
                        r_cols[1].markdown(f"<div class='{row_style}'><b>{rem_item['model']}</b></div>", unsafe_allow_html=True)
                        r_cols[2].markdown(f"<div class='{row_style}'><code>{rem_item['imei']}</code></div>", unsafe_allow_html=True)
                        r_cols[3].markdown(f"<div class='{row_style}'>{rem_item['kampania'] if rem_item['kampania'] else '֊'}</div>", unsafe_allow_html=True)
                        r_cols[4].markdown(f"<div class='{row_style}'>{rem_item['gumar']} 💰</div>", unsafe_allow_html=True)
                        
                        status_color = "#FFA500" if rem_item['kargavichak'] == "Վերանորոգման է" else ("#00FF00" if rem_item['kargavichak'] == "Պատրաստ է" else "#3498db")
                        r_cols[5].markdown(f"<div class='{row_style}' style='color:{status_color}; font-weight:bold;'>{rem_item['kargavichak']}</div>", unsafe_allow_html=True)
                        
                        with r_cols[6]:
                            if st.button("👁️", key=f"v_{rem_item['id']}"): show_details_dialog(rem_item)
                        with r_cols[7]:
                            if st.session_state.role == "admin":
                                if st.button("📝", key=f"e_{rem_item['id']}"): edit_remont_dialog(rem_item)
                        with r_cols[8]:
                            if st.session_state.role == "admin":
                                if st.button("🗑️", key=f"d_{rem_item['id']}"): delete_remont_dialog(rem_item['id'])
                else:
                    st.warning("❌ Վերանորոգման գրառումներ չգտնվեցին։")

# --- 5. 📜 ՊԱՏՄՈՒԹՅՈՒՆ ---
elif st.session_state.page == "history" and st.session_state.role == "admin":
    st.title("📜 ԳՆՈՒՄՆԵՐԻ ՊԱՏՄՈՒԹՅՈՒՆ")
    res_hist = requests.get(f"{SUPABASE_URL}/rest/v1/{HISTORY_TABLE}?select=*&order=id.desc&limit=100", headers=HEADERS)
    if res_hist.status_code == 200 and res_hist.json():
        st.dataframe(res_hist.json(), use_container_width=True)

# --- 6. ⚙️ ԿԱՐԳԱՎՈՐՈՒՄՆԵՐԻ ԷՋ ---
elif st.session_state.page == "settings" and st.session_state.role == "admin":
    st.title("⚙️ ՀԱՄԱԿԱՐԳԻ ԿԱՐԳԱՎՈՐՈՒՄՆԵՐ")
    st.markdown("### 🔒 Գաղտնաբառերի Փոփոխում")
    
    st.markdown("---")
    col_p1, col_p2 = st.columns(2)
    with col_p1: new_admin_pass = st.text_input("🔑 Նոր ԱԴՄԻՆ Գաղտնաբառ", value=ADMIN_PASSWORD, type="password")
    with col_p2: new_user_pass = st.text_input("👤 Նոր ՅՈՒԶԵՐ Գաղտնաբառ", value=USER_PASSWORD, type="password")
        
    if st.button("💾 ՊԱՀՊԱՆԵԼ ՆՈՐ ԳԱՂՏՆԱԲԱՌԵՐԸ", type="primary"):
        if new_admin_pass.strip() and new_user_pass.strip():
            with st.spinner("⏳ Թարմացվում է..."):
                if update_passwords_in_db(new_admin_pass.strip(), new_user_pass.strip()):
                    st.success("🎉 Գաղտնաբառերը փոխվեցին։")
                    ADMIN_PASSWORD = new_admin_pass.strip()
                    USER_PASSWORD = new_user_pass.strip()
                else: st.error("❌ Բազայի սխալ։")

st.markdown('</div>', unsafe_allow_html=True)

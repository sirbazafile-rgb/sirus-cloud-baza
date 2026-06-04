import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- ՔՈ ԲԱԶԱՅԻ ՏՎՅԱԼՆԵՐԸ ---
SUPABASE_URL = "https://umbgvfyczrsjfxvpyaei.supabase.co"
SUPABASE_KEY = "sb_publishable_587nBtq5BdKGZqb8LdUjGA_2GhxqH6D"
PRODUCTS_TABLE = "products"
REMONT_TABLE = "remont"
HISTORY_TABLE = "purchase"  # ՈՒՂՂՎԱԾ Է․ Քո բազայի աղյուսակի ճիշտ անունը
SETTINGS_TABLE = "system_settings"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

st.set_page_config(page_title="Phone Business", page_icon="📱", layout="wide")

# ՎԵՐՍԻԱ 3.1 (Բազայի սյուների ճշգրտում)
st.write("<!-- v3.1 -->")

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

# --- 🗺️ NAVIGATION ՄԵՆՅՈՒ ԵՎ ՍՏԱՅԼԵՐ ---
st.markdown("""
    <style>
    .sticky-nav {
        position: fixed; top: 0; left: 0; right: 0; background-color: #0e1117; 
        z-index: 999999; padding: 10px 45px 10px 45px; border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }
    .main-content { margin-top: 90px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 40px; font-weight: bold; }
    .nav-container { background-color: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .table-header { background-color: #262730; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; border-bottom: 2px solid #464855; font-size: 14px; }
    .table-row-odd { background-color: #1E1E24; padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); align-items: center; text-align: center; font-size: 14px; border-radius: 4px; min-height: 45px; display: flex; justify-content: center; }
    .table-row-even { background-color: #292A34; padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); align-items: center; text-align: center; font-size: 14px; border-radius: 4px; min-height: 45px; display: flex; justify-content: center; }
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

# --- Pop-up պատուհանների ֆունկցիաները (Անփոփոխ) ---
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

@st.dialog("📝 Վերանորոգման Տվյալների Փոփոխում", width="large")
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
        u_komplekt = st.selectbox("💳 Վճարման Տեսակ", ["Կանխիկ", "Անկանխիկ"], index=0 if item.get("komplekt") == "Կանխիկ" else 1)
        u_gumar = st.number_input("💵 Գումար (💰)", min_value=0, value=int(item.get("gumar", 0)), step=1000)
        u_work = st.text_area("🛠️ Կատարված Աշխատանք", value=item.get("katarvac_ashxatanq", ""))
        u_buy_date = st.date_input("📅 Ձեռքբերման Օր", datetime.strptime(item["dzerq_berman_date"], "%Y-%m-%d").date() if item.get("dzerq_berman_date") else datetime.now())
        status_list = ["Ստացել եմ", "Վերանորոգման է", "Պատրաստ է", "Ուղարկել եմ Կամպանիա"]
        u_status = st.selectbox("🚦 Կարգավիճակ", status_list, index=status_list.index(item["kargavichak"]) if item.get("kargavichak") in status_list else 0)
        u_nshum = st.text_input("📌 Նշումներ", value=item.get("nshumner", ""))

    if st.button("💾 ԹԱՐՄԱՑՆԵԼ ՏՎՅԱԼՆԵՐԸ", type="primary"):
        update_payload = {
            "model": u_model, "imei": u_imei, "received_date": str(u_rec_date), "kampania": u_kampania,
            "xndir": u_xndir, "komplekt": u_komplekt, "gumar": u_gumar, "katarvac_ashxatanq": u_work,
            "dzerq_berman_date": str(u_buy_date), "kargavichak": u_status, "nshumner": u_nshum
        }
        res = requests.patch(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?id=eq.{item['id']}", headers=HEADERS, json=update_payload)
        if res.status_code in [200, 201, 204]: st.success("🎉 Թարմացվեց։"); st.rerun()

@st.dialog("🗑️ Հաստատել Վերանորոգման Ջնջումը")
def delete_remont_dialog(item_id, display_id, model_name):
    st.warning(f"⚠️ Վստա՞հ ես, որ ուզում ես ջնջել № {display_id} «{model_name}» վերանորոգման տվյալը։")
    pass_input = st.text_input("Մուտքագրեք գաղտնաբառը (12)", type="password")
    if st.button("🗑️ HԱՍՏԱՏԵԼ ՋՆՋՈՒՄԸ", type="primary"):
        if pass_input == "12":
            del_res = requests.delete(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?id=eq.{item_id}", headers=HEADERS)
            if del_res.status_code in [200, 204]: st.success("Հաջողությամբ ջնջվեց։"); st.rerun()

@st.dialog("🚨 Ջնջել Ամբողջ Ապրանքների Բազան")
def delete_all_products_dialog():
    st.error("❗❗❗ Այս գործողությունը կջնջի ԱՊՐԱՆՔՆԵՐԻ ամբողջ բազան։")
    pass_input = st.text_input("Մուտքագրեք գաղտնաբառը (89)", type="password")
    if st.button("💥 ՋՆՋԵԼ ԱՄԲՈՂՋՈՒԹՅԱՄԲ", type="primary"):
        if pass_input == "89":
            del_res = requests.delete(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?id=gt.0", headers=HEADERS)
            if del_res.status_code in [200, 204]: st.success("🎉 Մաքրվեց։"); st.rerun()

@st.dialog("📱 Հեռախոսի Ամբողջական Ինֆորմացիան", width="large")
def show_details_dialog(row):
    st.markdown(f"### 🔗 {row['model']} (Համար՝ {row['display_id']})")
    st.markdown(f"**🔢 IMEI:** `{row['imei']}`")
    st.markdown("---")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown(f"🏢 **Կամպանիա:** {row['kampania'] if row.get('kampania') else '֊'}")
        st.markdown(f"📅 **Ստացման Ամսաթիվ:** {row['received_date']}")
        st.markdown(f"📅 **Ձեռքբերման Ամսաթիվ:** {row['dzerq_berman_date'] if row['dzerq_berman_date'] else '֊'}")
        st.markdown(f"💳 **Վճարման Տեսակ:** `{row['komplekt'] if row['komplekt'] else 'Կանխիկ'}`")
    with col_d2:
        st.markdown(f"💵 **Գումար:** {row['gumar']} 💰")
        st.markdown(f"🚦 **Կարգավիճակ:** {row['kargavichak']}")
    st.markdown("---")
    st.info(f"❌ **Խնդիրը:**\n{row['xndir'] if row['xndir'] else 'Նշված չէ'}")
    st.success(f"🛠️ **Կատարված Աշխատանք:**\n{row['katarvac_ashxatanq'] if row['katarvac_ashxatanq'] else 'Դեռ արված չէ'}")

# --- 1. 🏠 ԳԼԽԱՎՈՐ ԷՋ ---
if st.session_state.page == "home" and st.session_state.role == "admin":
    st.title("🚀 SIRUS SYSTEM (Admin Mode)")
    st.markdown("### Հեռախոսների և Բիզնեսի Կառավարման Ամպային Համակարգ")

# --- 2. 📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ (ՈՒՂՂՎԱԾ Է ՍՅՈՒՆԵՐԸ ՔՈ ԲԱԶԱՅԻՆ) ---
elif st.session_state.page == "add_product" and st.session_state.role == "admin":
    st.title("📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ")
    tab_manual, tab_excel = st.tabs(["✍️ ՁԵՌՔՈՎ ՄՈՒՏՔԱԳՐՈՒՄ", "📥 EXCEL / CSV ՖԱՅԼԻՑ ՄՈՒՏՔ"])
    
    with tab_manual:
        col1, col2 = st.columns(2)
        with col1:
            category_selection = st.selectbox("📁 Խումբ", ["Հեռախոս", "Աքսեսուար", "Պլանշետ", "Խելացի Ժամացույց", "Այլ..."])
            category = st.text_input("✍️ Մուտքագրիր նոր խումբը") if category_selection == "Այլ..." else category_selection
            model = st.text_input("📝 Մոդել")
            storage = st.text_input("💾 Հիշողություն")
            color = st.text_input("🎨 Գույն")
        with col2:
            matakarar = st.text_input("📦 Մատակարար")
            buy_date = st.date_input("📅 Գնելու Ամսաթիվ", datetime.now(), key="manual_buy_date")
            nshumner = st.text_input("📌 Լրացուցիչ Նշումներ")
        st.markdown("---")
        current_imeis = st.text_area("🔢 IMEI-ների / Սերիականների Ցուցակ", height=150)
        
        if st.button("💾 ՊԱՀՊԱՆԵԼ ԲՈԼՈՐԸ ԲԱԶԱՅՈՒՄ", type="primary"):
            if model and current_imeis and category:
                imei_list = [i.strip() for i in current_imeis.split('\n') if i.strip()]
                has_duplicate = False
                for imei in imei_list:
                    if check_imei_exists(imei): st.error(f"⚠️ IMEI `{imei}` արդեն կա products-ում։"); has_duplicate = True; break
                
                if not has_duplicate:
                    success_count = 0
                    full_model_title = f"{model} {storage} {color}".strip()
                    for imei in imei_list:
                        # 1. Գրում ենք PRODUCTS աղյուսակում
                        prod_payload = {
                            "category": category, "model": model, "storage": storage if storage else None, 
                            "color": color if color else None, "imei": imei,
                            "matakarar": matakarar if matakarar else None, "buy_date": str(buy_date), "nshumner": nshumner if nshumner else None
                        }
                        res = requests.post(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}", headers=HEADERS, json=prod_payload)
                        if res.status_code in [200, 201]: 
                            success_count += 1
                            # 2. Գրում ենք PURCHASE (Պատմության) աղյուսակում՝ ՃԻՇՏ ՍՅՈՒՆԵՐՈՎ
                            hist_payload = {
                                "date": str(buy_date), 
                                "category": category, 
                                "model": full_model_title, 
                                "imei": imei, 
                                "quantity": 1
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/{HISTORY_TABLE}", headers=HEADERS, json=hist_payload)
                    if success_count > 0: st.success(f"🎉 Հաջողությամբ ավելացավ {success_count} ապրանք և գրանցվեց պատմության մեջ։"); st.balloons()
            else: st.warning("⚠️ Լրացրեք պարտադիր դաշտերը։")

    with tab_excel:
        uploaded_file = st.file_uploader("Ընտրիր Excel կամ CSV ֆայլը", type=["xlsx", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'): df_upload = pd.read_csv(uploaded_file, dtype={'imei': str, 'storage': str})
                else: df_upload = pd.read_excel(uploaded_file, dtype={'imei': str, 'storage': str})
                df_upload = df_upload.dropna(subset=['model', 'imei'])
                st.dataframe(df_upload, use_container_width=True)
                
                if st.button("🚀 ՊԱՀՊԱՆԵԼ EXCEL-Ի ՏՎՅԱԼՆԵՐԸ ԲԱԶԱՅՈՒՄ", type="primary"):
                    success_excel_count = 0
                    for index, row_data in df_upload.iterrows():
                        clean_imei = str(row_data['imei']).split('.')[0].strip()
                        if check_imei_exists(clean_imei): continue
                        
                        cat_val = str(row_data['xumb']) if 'xumb' in row_data and pd.notna(row_data['xumb']) else "Հեռախոս"
                        excel_payload = {
                            "category": cat_val, "model": str(row_data['model']),
                            "storage": str(row_data['storage']) if 'storage' in row_data and pd.notna(row_data['storage']) else None,
                            "color": str(row_data['color']) if 'color' in row_data and pd.notna(row_data['color']) else None, "imei": clean_imei,
                            "matakarar": str(row_data['matakarar']) if 'matakarar' in row_data and pd.notna(row_data['matakarar']) else None,
                            "buy_date": str(row_data['buy_date']) if 'buy_date' in row_data and pd.notna(row_data['buy_date']) else str(datetime.now().date()),
                            "nshumner": str(row_data['nshumner']) if 'nshumner' in row_data and pd.notna(row_data['nshumner']) else None
                        }
                        res_excel = requests.post(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}", headers=HEADERS, json=excel_payload)
                        if res_excel.status_code in [200, 201]:
                            success_excel_count += 1
                            ex_date = str(row_data['buy_date']) if 'buy_date' in row_data and pd.notna(row_data['buy_date']) else str(datetime.now().date())
                            ex_model = f"{row_data['model']} {row_data['storage'] if 'storage' in row_data and pd.notna(row_data['storage']) else ''}".strip()
                            # Գրում ենք PURCHASE աղյուսակում Excel-ի համար
                            excel_hist_payload = {
                                "date": ex_date, "category": cat_val, "model": ex_model, "imei": clean_imei, "quantity": 1
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/{HISTORY_TABLE}", headers=HEADERS, json=excel_hist_payload)
                    if success_excel_count > 0: st.success(f"🎉 {success_excel_count} ապրանք գրանցվեց Excel-ից պատմության մեջ։"); st.balloons()
            except Exception as e: st.error(f"❌ Սխալ. {e}")

# --- 3. 🔧 ՎԵՐԱՆՈՐՈԳՄԱՆ ԲԱԺԻՆ ---
elif st.session_state.page == "remont" and st.session_state.role == "admin":
    st.title("🔧 ՎԵՐԱՆՈՐՈԳՄԱՆ ԲԱԺԻՆ")
    search_imei = st.text_input("🔢 Գրիր կամ սկանավորիր IMEI-ն")
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("🔍 ՓՆՏՐԵԼ ԲԱԶԱՅՈՒՄ"):
            if search_imei:
                res_remont_check = requests.get(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?imei=eq.{search_imei}&order=id.desc", headers=HEADERS)
                res_prod = requests.get(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?imei=eq.{search_imei}", headers=HEADERS)
                if res_remont_check.status_code == 200 and len(res_remont_check.json()) > 0:
                    past_remont = res_remont_check.json()[0]
                    st.warning(f"⚠️ Այս հեռախոսը ԱՐԴԵՆ ԵՂԵԼ Է վերանորոգման մեջ։")
                    st.session_state.found_product = {"model": past_remont.get("model", ""), "imei": search_imei}; st.session_state.remont_step2 = True
                elif res_prod.status_code == 200 and len(res_prod.json()) > 0:
                    st.session_state.found_product = res_prod.json()[0]; st.session_state.remont_step2 = True
                    st.success(f"📱 Գտնվեց ապրանքների բազայում՝ {st.session_state.found_product.get('model')}")
                else: st.session_state.found_product = None; st.warning("⚠️ Այս IMEI-ով ապրանք չգտնվեց բազաներում։")
    with col_btn2:
        if st.button("➕ ԱՎԵԼԱՑՆԵԼ ՁԵՌՔՈՎ (ԱՌԱՆՑ ՓՆՏՐԵԼՈՒ)"):
            st.session_state.found_product = {"model": "", "storage": "", "imei": search_imei}; st.session_state.remont_step2 = True

    if st.session_state.remont_step2 and st.session_state.found_product is not None:
        prod = st.session_state.found_product
        col1, col2 = st.columns(2)
        with col1:
            initial_model = prod.get('model', '')
            if prod.get('storage'): initial_model = f"{initial_model} {prod.get('storage')}".strip()
            model_input = st.text_input("📝 Մոդել", value=initial_model)
            imei_input = st.text_input("🔢 IMEI", value=prod.get("imei", search_imei))
            received_date = st.date_input("📅 Ստացման Ամսաթիվ", datetime.now())
            kampania = st.text_input("🏢 Կամպանիա")
            xndir = st.text_area("❌ Խնդիր")
        with col2:
            vcharman_tesak = st.selectbox("💳 ՎՃԱՐՄԱՆ ՏԵՍԱԿ", ["Կանխիկ", "Անկանխիկ"])
            gumar = st.number_input("💵 Գումար", min_value=0, value=0, step=1000)
            katarvac_ashxatanq = st.text_area("🛠️ Աշխատանք")
            dzerq_date = st.date_input("📅 Ձեռքբերման Ամսաթիվ", datetime.now())
            kargavichak = st.selectbox("🚦 Կարգավիճակ", ["Ստացել եմ", "Վերանորոգման է", "Պատրաստ է"])

        if st.button("💾 ՊԱՀՊԱՆԵԼ ՌԵՄՈՆՏԸ", type="primary"):
            remont_payload = {
                "model": model_input, "imei": imei_input, "received_date": str(received_date), "kampania": kampania,
                "xndir": xndir, "gumar": gumar, "komplekt": vcharman_tesak, "katarvac_ashxatanq": katarvac_ashxatanq, 
                "dzerq_berman_date": str(dzerq_date), "kargavichak": kargavichak
            }
            if requests.post(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}", headers=HEADERS, json=remont_payload).status_code in [200, 201]:
                st.success("🎉 Ռեմոնտը գրանցվեց։"); st.session_state.remont_step2 = False; st.session_state.found_product = None; st.rerun()

# --- 4. 📊 SIRUS CLOUD BAZA ---
elif st.session_state.page == "baza":
    st.title("📊 SIRUS CLOUD BAZA")
    tab1, tab2 = st.tabs(["📦 ԱՊՐԱՆՔՆԵՐ", "🔧 ՎԵՐԱՆՈՐՈԳՈՒՄՆԵՐ"])
    
    with tab1:
        if st.session_state.role == "admin" and st.button("🚨 ՋՆՋԵԼ ԱՄԲՈՂՋ ԲԱԶԱՆ", type="primary"): delete_all_products_dialog()
        search_prod_query = st.text_input("🔍 Փնտրել Ապրանք (Գրեք IMEI կամ Մոդել)", placeholder="Մուտքագրեք տվյալը...")
        
        res = requests.get(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?select=*&order=id.asc", headers=HEADERS)
        if res.status_code == 200 and res.json():
            products_data = res.json()
            if search_prod_query.strip():
                q = search_prod_query.strip().lower()
                products_data = [r for r in products_data if q in str(r.get('imei','')).lower() or q in str(r.get('model','')).lower()]
            
            p_cols = st.columns([0.8, 2.2, 1.2, 1.2, 2.3, 1.5, 1.3, 1.1])
            headers_text = ["🆔 ID", "📝 Մոդել", "💾 Հիշող.", "🎨 Գույն", "🔢 IMEI", "📁 Խումբ", "📅 Գնելու Օր", "📝 Ուղղել"]
            for idx, h in enumerate(headers_text): p_cols[idx].markdown(f"<div class='table-header'>{h}</div>", unsafe_allow_html=True)
            
            for idx, row in enumerate(products_data):
                row_style = "table-row-even" if idx % 2 == 1 else "table-row-odd"
                display_id = idx + 1; row['display_id'] = display_id
                r_cols = st.columns([0.8, 2.2, 1.2, 1.2, 2.3, 1.5, 1.3, 1.1])
                r_cols[0].markdown(f"<div class='{row_style}'><code>{display_id}</code></div>", unsafe_allow_html=True)
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

    with tab2:
        search_rem_query = st.text_input("🔍 Փնտրել Դեպք (Գրեք IMEI, Մոդել կամ Կամպանիա)", placeholder="Մուտքագրեք տվյալը...")
        res_rem = requests.get(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?select=*&order=id.asc", headers=HEADERS)
        if res_rem.status_code == 200 and res_rem.json():
            remont_data = res_rem.json()
            if search_rem_query.strip():
                q = search_rem_query.strip().lower()
                remont_data = [r for r in remont_data if q in str(r.get('imei','')).lower() or q in str(r.get('model','')).lower() or q in str(r.get('kampania','')).lower()]
            
            rem_cols = st.columns([0.8, 1.5, 2, 1.5, 1.2, 1.2, 1, 1, 1])
            headers_rem = ["🆔 ID", "📝 Մոդել", "🔢 IMEI", "🏢 Կամպանիա", "💵 Գումար", "🚦 Կարգավիճակ", "📱 Ինֆո", "📝 Ուղղել", "🗑️ Ջնջել"]
            for idx, h in enumerate(headers_rem): rem_cols[idx].markdown(f"<div class='table-header'>{h}</div>", unsafe_allow_html=True)
            
            for idx, rem_item in enumerate(remont_data):
                row_style = "table-row-even" if idx % 2 == 1 else "table-row-odd"
                display_id = idx + 1; rem_item['display_id'] = display_id
                r_cols = st.columns([0.8, 1.5, 2, 1.5, 1.2, 1.2, 1, 1, 1])
                r_cols[0].markdown(f"<div class='{row_style}'><code>{display_id}</code></div>", unsafe_allow_html=True)
                r_cols[1].markdown(f"<div class='{row_style}'><b>{rem_item['model']}</b></div>", unsafe_allow_html=True)
                r_cols[2].markdown(f"<div class='{row_style}'><code>{rem_item['imei']}</code></div>", unsafe_allow_html=True)
                r_cols[3].markdown(f"<div class='{row_style}'>{rem_item['kampania'] if rem_item['kampania'] else '֊'}</div>", unsafe_allow_html=True)
                r_cols[4].markdown(f"<div class='{row_style}'>{rem_item['gumar']} 💰</div>", unsafe_allow_html=True)
                status_color = "#FFA500" if rem_item['kargavichak'] == "Վերանորոգման է" else "#00FF00" if rem_item['kargavichak'] == "Պատրաստ է" else "#999999"
                r_cols[5].markdown(f"<div class='{row_style}' style='color:{status_color}; font-weight:bold;'>{rem_item['kargavichak']}</div>", unsafe_allow_html=True)
                with r_cols[6]:
                    if st.button("👁️", key=f"v_{rem_item['id']}"): show_details_dialog(rem_item)
                with r_cols[7]:
                    if st.session_state.role == "admin":
                        if st.button("📝", key=f"e_{rem_item['id']}"): edit_remont_dialog(rem_item)
                    else: st.write("🔒")
                with r_cols[8]:
                    if st.session_state.role == "admin":
                        if st.button("🗑️", key=f"d_{rem_item['id']}"): delete_remont_dialog(rem_item['id'], display_id, rem_item['model'])
                    else: st.write("🔒")

# --- 5. 📜 ՊԱՏՄՈՒԹՅՈՒՆ (ՈՒՂՂՎԱԾ Է ՔՈ ԻՐԱԿԱՆ ԲԱԶԱՅԻ ՍՅՈՒՆԵՐԻՆ) ---
elif st.session_state.page == "history" and st.session_state.role == "admin":
    st.title("📜 ԳՆՈՒՄՆԵՐԻ ՊԱՏՄՈՒԹՅՈՒՆ")
    res_hist = requests.get(f"{SUPABASE_URL}/rest/v1/{HISTORY_TABLE}?select=*&order=id.desc", headers=HEADERS)
    
    if res_hist.status_code == 200 and res_hist.json():
        h_data = res_hist.json()
        h_cols = st.columns([1, 2, 3, 3, 1, 2])
        headers_hist = ["🆔 ID", "📅 Ամսաթիվ", "📝 Ապրանք / Մոդել", "🔢 IMEI", "📦 Քանակ", "📁 Խումբ"]
        for idx, h in enumerate(headers_hist): h_cols[idx].markdown(f"<div class='table-header'>{h}</div>", unsafe_allow_html=True)
        
        for idx, h_item in enumerate(h_data):
            row_style = "table-row-even" if idx % 2 == 1 else "table-row-odd"
            r_cols = st.columns([1, 2, 3, 3, 1, 2])
            r_cols[0].markdown(f"<div class='{row_style}'><code>{idx+1}</code></div>", unsafe_allow_html=True)
            r_cols[1].markdown(f"<div class='{row_style}'>{h_item.get('date', '֊')}</div>", unsafe_allow_html=True)
            r_cols[2].markdown(f"<div class='{row_style}'><b>{h_item.get('model', '֊')}</b></div>", unsafe_allow_html=True)
            r_cols[3].markdown(f"<div class='{row_style}'><code>{h_item.get('imei', '֊')}</code></div>", unsafe_allow_html=True)
            r_cols[4].markdown(f"<div class='{row_style}'>{h_item.get('quantity', 1)} հատ</div>", unsafe_allow_html=True)
            r_cols[5].markdown(f"<div class='{row_style}'>{h_item.get('category', 'Հեռախոս')}</div>", unsafe_allow_html=True)
    else:
        st.info("ℹ️ Գնումների պատմությունը դատարկ է։ Նոր ապրանք ավելացնելիս այն կգրանցվի այստեղ։")

# --- 6. ⚙️ ՍԱԶԱՆԴՈՒՄՆԵՐ ---
elif st.session_state.page == "settings" and st.session_state.role == "admin":
    st.title("⚙️ ՀԱՄԱԿԱՐԳԻ ԿԱՐԳԱՎՈՐՈՒՄՆԵՐ")
    st.subheader("🔑 Գաղտնաբառերի Փոփոխում")
    new_admin_pass = st.text_input("Նոր Ադմինի Գաղտնաբառ", value=ADMIN_PASSWORD, type="password")
    new_user_pass = st.text_input("Նոր Յուզերի Գաղտնաբառ", value=USER_PASSWORD, type="password")
    
    if st.button("💾 ՊԱՀՊԱՆԵԼ ԳԱՂՏՆԱԲԱՌԵՐԸ ԲԱԶԱՅՈՒՄ", type="primary"):
        if new_admin_pass.strip() and new_user_pass.strip():
            update_passwords_in_db(new_admin_pass.strip(), new_user_pass.strip())
            st.success("🎉 Գաղտնաբառերը հաջողությամբ պահպանվեցին Ամպային Բազայում (Supabase)։")
        else: st.error("❌ Գաղտնաբառերը չեն կարող դատարկ լինել։")

st.markdown('</div>', unsafe_allow_html=True)

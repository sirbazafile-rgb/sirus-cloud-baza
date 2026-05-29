import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- ՔՈ ԲԱԶԱՅԻ ՏՎՅԱԼՆԵՐԸ ---
SUPABASE_URL = "https://umbgvfyczrsjfxvpyaei.supabase.co"
SUPABASE_KEY = "sb_publishable_587nBtq5BdKGZqb8LdUjGA_2GhxqH6D"
PRODUCTS_TABLE = "products"
REMONT_TABLE = "remont"
HISTORY_TABLE = "purchase_history"

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

ADMIN_PASSWORD = "sirusadmin2026"
USER_PASSWORD = "sirususer2026"

# Ֆունկցիա՝ IMEI-ի գոյությունը բազայում ստուգելու համար
def check_imei_exists(imei):
    res = requests.get(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?imei=eq.{imei}", headers=HEADERS)
    if res.status_code == 200 and len(res.json()) > 0:
        return True
    return False

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

# --- 🗺️ NAVIGATION ՄԵՆՅՈՒ ԵՎ ՍՏԱՅԼԵՐ ---
# Այստեղ ավելացրեցի fixed դիրքը, որ մենյուն վերևում սառած մնա
st.markdown("""
    <style>
    /* Սարքում ենք վերևի մենյուն ֆիքսված (Sticky) */
    .sticky-nav {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background-color: #0e1117; /* Ֆոնի գույնը, որ տեքստերը տակով անցնելիս չերևան */
        z-index: 999999;
        padding: 10px 45px 10px 45px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Բովանդակության համար բացատ, որ չմտնի ֆիքսված մենյուի տակ */
    .main-content {
        margin-top: 130px;
    }
    
    .stButton>button { width: 100%; border-radius: 8px; height: 40px; font-weight: bold; }
    .nav-container { background-color: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .table-header { background-color: #262730; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; border-bottom: 2px solid #464855; font-size: 14px; }
    
    /* Տողերի հիմնական ստայլը (Կենտ տողերի համար - 1, 3, 5...) */
    .table-row-odd { background-color: #1E1E24; padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); align-items: center; text-align: center; font-size: 14px; border-radius: 4px; min-height: 45px; display: flex; justify-content: center; }
    
    /* Զույգ տողերի ստայլը (2, 4, 6...) - թեթևակի ավելի բաց գույն */
    .table-row-even { background-color: #292A34; padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); align-items: center; text-align: center; font-size: 14px; border-radius: 4px; min-height: 45px; display: flex; justify-content: center; }
    
    div[data-testid="stMetric"] { background-color: #262730; padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Բացում ենք ֆիքսված HTML div-ը մենյուի համար
st.markdown('<div class="sticky-nav">', unsafe_allow_html=True)
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
if st.session_state.role == "admin":
    menu_col1, menu_col2, menu_col3, menu_col4, menu_col5, menu_col6 = st.columns([1, 1.2, 1.2, 1.2, 1.4, 1])
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
        if st.button("📜 ՁԵՌՔԲԵՐՄԱՆ ՊԱՏՄՈՒԹՅՈՒՆ"): st.session_state.page = "history"; st.rerun()
    with menu_col6:
        if st.button("🚪 ԵԼՔ"): st.session_state.authenticated = False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True) # Փակում ենք sticky-nav div-ը

# Այստեղից սկսվում է հիմնական էջի բովանդակությունը (որը կանցնի մենյուի տակով)
st.markdown('<div class="main-content">', unsafe_allow_html=True)


# --- 📦 ԱՊՐԱՆՔԻ ԽՄԲԱԳՐՄԱՆ POP-UP (DIALOG) ---
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
        if res.status_code in [200, 201, 204]:
            st.success("🎉 Ապրանքի տվյալները հաջողությամբ թարմացվեցին։")
            st.rerun()


# --- 📝 🔧 ՎԵՐԱՆՈՐՈԳՄԱՆ ԽՄԲԱԳՐՄԱՆ POP-UP (DIALOG) ---
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
        current_status_idx = status_list.index(item["kargavichak"]) if item.get("kargavichak") in status_list else 0
        u_status = st.selectbox("🚦 Կարգավիճակ", status_list, index=current_status_idx)
        u_nshum = st.text_input("📌 Նշումներ", value=item.get("nshumner", ""))

    if st.button("💾 ԹԱՐՄԱՑՆԵԼ ՏՎՅԱԼՆԵՐԸ", type="primary"):
        update_payload = {
            "model": u_model, "imei": u_imei, "received_date": str(u_rec_date), "kampania": u_kampania,
            "xndir": u_xndir, "komplekt": u_komplekt, "gumar": u_gumar, "katarvac_ashxatanq": u_work,
            "dzerq_berman_date": str(u_buy_date), "kargavichak": u_status, "nshumner": u_nshum
        }
        res = requests.patch(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?id=eq.{item['id']}", headers=HEADERS, json=update_payload)
        if res.status_code in [200, 201, 204]:
            st.success("🎉 Տվյալները հաջողությամբ թարմացվեցին։")
            st.rerun()

# --- 🗑️ ՎԵՐԱՆՈՐՈԳՈՒՄ ՋՆՋԵԼՈՒ ՊԱՍՎՈՐԴՈՎ ՊԱՏՈՒՀԱՆ (DIALOG 12) ---
@st.dialog("🗑️ Հաստատել Վերանորոգման Ջնջումը")
def delete_remont_dialog(item_id, display_id, model_name):
    st.warning(f"⚠️ Վստա՞հ ես, որ ուզում ես ջնջել № {display_id} «{model_name}» վերանորոգման տվյալը։")
    pass_input = st.text_input("Մուտքագրեք գաղտնաբառը (12)", type="password")
    if st.button("🗑️ HԱՍՏԱՏԵԼ ՋՆՋՈՒՄԸ", type="primary"):
        if pass_input == "12":
            del_res = requests.delete(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?id=eq.{item_id}", headers=HEADERS)
            if del_res.status_code in [200, 204]:
                st.success("Հաջողությամբ ջնջվեց։")
                st.rerun()
        else:
            st.error("❌ Սխալ գաղտնաբառ։ Ջնջումը մերժվեց։")

# --- 🚨 ԱՄԲՈՂՋ ԱՊՐԱՆՔՆԵՐԸ ՋՆՋԵԼՈՒ ՊԱՍՎՈՐԴՈՎ ՊԱՏՈՒՀԱՆ (DIALOG 89) ---
@st.dialog("🚨 Ջնջել Ամբողջ Ապրանքների Բազան")
def delete_all_products_dialog():
    st.error("❗❗❗ ԶԳՈՒՇԱՑՈՒՄ. Այս գործողությունը կջնջի ԱՊՐԱՆՔՆԵՐԻ ամբողջ բազան և այն հնարավոր չի լինի վերականգնել։")
    pass_input = st.text_input("Մուտքագրեք գաղտնաբառը (89)", type="password")
    if st.button("💥 ՋՆՋԵԼ ԱՄԲՈՂՋՈՒԹՅԱՄԲ", type="primary"):
        if pass_input == "89":
            del_res = requests.delete(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?id=gt.0", headers=HEADERS)
            if del_res.status_code in [200, 204]:
                st.success("🎉 Ապրանքների ամբողջ բազան հաջողությամբ մաքրվեց։")
                st.rerun()
            else:
                st.error("❌ Սերվերի սխալ կամ սահմանափակում Supabase-ում։")
        else:
            st.error("❌ Սխալ գաղտնաբառ։")

# --- POP-UP ՏԵՍՆԵԼՈՒ ՖՈՒՆԿՑԻԱ ---
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
        current_imeis = st.text_area("🔢 IMEI-ների / Սերիականների Ցուցակ (Ամեն տողում մեկ հատ)", height=150)
        
        if st.button("💾 ՊԱՀՊԱՆԵԼ ԲՈԼՈՐԸ ԲԱԶԱՅՈՒՄ", type="primary"):
            if model and current_imeis and category:
                imei_list = [i.strip() for i in current_imeis.split('\n') if i.strip()]
                
                has_duplicate = False
                for imei in imei_list:
                    if check_imei_exists(imei):
                        st.error(f"⚠️ IMEI `{imei}` արդեն գոյություն ունի բազայում։ Մուտքագրումը չեղարկվեց։")
                        has_duplicate = True
                        break
                
                if not has_duplicate:
                    success_count = 0
                    for imei in imei_list:
                        payload = {
                            "category": category, "model": model, "storage": storage, "color": color, "imei": imei,
                            "matakarar": matakarar if matakarar else None, "buy_date": str(buy_date), "nshumner": nshumner if nshumner else None
                        }
                        res = requests.post(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}", headers=HEADERS, json=payload)
                        if res.status_code in [200, 201]: 
                            success_count += 1
                            full_model_title = f"{model} {storage} {color}".strip()
                            hist_payload = {
                                "date": str(buy_date), "category": category, "model": full_model_title, "imei": imei, 
                                "quantity": 1, "matakarar": matakarar if matakarar else "Նշված չէ"
                            }
                           requests.post(f"{SUPABASE_URL}/rest/v1/{HISTORY_TABLE}", headers=HEADERS, json=hist_payload)
                    if success_count > 0: 
                        st.success(f"🎉 Հաջողությամբ ավելացավ {success_count} ապրանք բազայում և պատմության մեջ։"); st.balloons()
            else: st.warning("⚠️ Խնդրում ենք լրացնել Խումբը, Մոդելը և IMEI/Սերիական կոդերը։")

    with tab_excel:
        st.subheader("📥 Բեռնել Ապրանքները Excel/CSV ֆայլից")
        st.markdown("**💡 Սյուների անունները.** `model` | `storage` | `color` | `imei` | `xumb` | `matakarar` | `buy_date` | `nshumner`")
        uploaded_file = st.file_uploader("Ընտրիր Excel կամ CSV ֆայլը", type=["xlsx", "csv"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'): df_upload = pd.read_csv(uploaded_file, dtype={'imei': str, 'storage': str})
                else: df_upload = pd.read_excel(uploaded_file, dtype={'imei': str, 'storage': str})
                
                df_upload = df_upload.dropna(subset=['model', 'imei'])
                st.dataframe(df_upload, use_container_width=True)
                total_rows = len(df_upload)
                
                if st.button("🚀 ՊԱՀՊԱՆԵԼ EXCEL-Ի ՏՎՅԱԼՆԵՐԸ ԲԱԶԱՅՈՒՄ", type="primary"):
                    success_excel_count = 0
                    duplicate_excel_count = 0
                    progress_bar = st.progress(0)
                    
                    for index, row_data in df_upload.iterrows():
                        clean_imei = str(row_data['imei']).split('.')[0].strip()
                        
                        if check_imei_exists(clean_imei):
                            duplicate_excel_count += 1
                            progress_bar.progress((index + 1) / total_rows)
                            continue
                        
                        cat_val = str(row_data['xumb']) if 'xumb' in row_data and pd.notna(row_data['xumb']) else "Հեռախոս"
                        
                        excel_payload = {
                            "category": cat_val, "model": str(row_data['model']),
                            "storage": str(row_data['storage']) if 'storage' in row_data and pd.notna(row_data['storage']) else None,
                            "color": str(row_data['color']) if 'color' in row_data and pd.notna(row_data['color']) else None,
                            "imei": clean_imei,
                            "matakarar": str(row_data['matakarar']) if 'matakarar' in row_data and pd.notna(row_data['matakarar']) else None,
                            "buy_date": str(row_data['buy_date']) if 'buy_date' in row_data and pd.notna(row_data['buy_date']) else str(datetime.now().date()),
                            "nshumner": str(row_data['nshumner']) if 'nshumner' in row_data and pd.notna(row_data['nshumner']) else None
                        }
                        
                        res_excel = requests.post(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}", headers=HEADERS, json=excel_payload)
                        if res_excel.status_code in [200, 201]:
                            success_excel_count += 1
                            ex_date = str(row_data['buy_date']) if 'buy_date' in row_data and pd.notna(row_data['buy_date']) else str(datetime.now().date())
                            ex_model = f"{row_data['model']} {row_data['storage'] if 'storage' in row_data and pd.notna(row_data['storage']) else ''}".strip()
                            ex_matakarar = str(row_data['matakarar']) if 'matakarar' in row_data and pd.notna(row_data['matakarar']) else "Նշված չէ"
                            
                            excel_hist_payload = {
                                "date": ex_date, "category": cat_val, "model": ex_model, "imei": clean_imei, 
                                "quantity": 1, "matakarar": ex_matakarar
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/{HISTORY_TABLE}", headers=HEADERS, json=excel_hist_payload)
                        
                        progress_bar.progress((index + 1) / total_rows)
                    
                    if duplicate_excel_count > 0:
                        st.warning(f"⚠️ Ֆայլի միջից {duplicate_excel_count} ապրանք բաց թողնվեց, քանի որ դրանց IMEI-ները արդեն կային բազայում։")
                    if success_excel_count > 0: 
                        st.success(f"🎉 {success_excel_count} նոր ապրանք հաջողությամբ գրանցվեց բազայում։"); st.balloons()
            except Exception as e: st.error(f"❌ Ֆայլի ընթերցման սխալ. {e}")

# --- 3. 🔧 ՎԵՐԱՆՈՐՈԳՄԱՆ ԲԱԺԻՆ ---
elif st.session_state.page == "remont" and st.session_state.role == "admin":
    st.title("🔧 ՎԵՐԱՆՈՐՈԳՄԱՆ ԲԱԺԻՆ")
    search_imei = st.text_input("🔢 Գրիր կամ սկանավորիր IMEI-ն")
    
    if st.button("🔍 ՓՆՏՐԵԼ ԲԱԶԱՅՈՒՄ", type="secondary"):
        if search_imei:
            res = requests.get(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?imei=eq.{search_imei}", headers=HEADERS)
            if res.status_code == 200 and len(res.json()) > 0:
                st.session_state.found_product = res.json()[0]; st.session_state.remont_step2 = False
            else:
                st.session_state.found_product = None; st.session_state.remont_step2 = False
                st.error("❌ Այս IMEI-ով ապրանք բազայում չգտնվեց։")

    if st.session_state.found_product:
        prod = st.session_state.found_product
        st.markdown("### 📱 Գտնված Ապրանքի Տվյալները")
        info_df = pd.DataFrame([{"ID": prod.get("id"), "Մոդել": prod.get("model"), "Հիշողություն": prod.get("storage"), "Գույն": prod.get("color"), "Խումբ": prod.get("category")}])
        st.dataframe(info_df, use_container_width=True, hide_index=True)
        if st.button("➕ ԱՎԵԼԱՑՆԵԼ ՎԵՐԱՆՈՐՈԳՈՒՄ ԲԱԺՆՈՒՄ", type="primary"): st.session_state.remont_step2 = True

    if st.session_state.remont_step2 and st.session_state.found_product:
        st.markdown("---")
        prod = st.session_state.found_product
        full_model_name = f"{prod.get('model', '')} {prod.get('storage', '')}".strip()
        
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
            nshumner = st.text_input("📌 Նշումներ")

        if st.button("💾 ՊԱՀՊԱՆԵԼ", type="primary"):
            remont_payload = {
                "model": model_input, "imei": imei_input, "received_date": str(received_date), "kampania": kampania,
                "xndir": xndir, "gumar": gumar, "komplekt": vcharman_tesak, "katarvac_ashxatanq": katarvac_ashxatanq, 
                "dzerq_berman_date": str(dzerq_date), "kargavichak": kargavichak, "nshumner": nshumner
            }
            if requests.post(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}", headers=HEADERS, json=remont_payload).status_code in [200, 201]:
                st.success("🎉 Տվյալները գրանցվեցին։"); st.session_state.remont_step2 = False; st.session_state.found_product = None

# --- 4. 📊 SIRUS CLOUD BAZA ---
elif st.session_state.page == "baza":
    st.title("📊 SIRUS CLOUD BAZA")
    tab1, tab2 = st.tabs(["📦 ԱՊՐԱՆՔՆԵՐ", "🔧 ՎԵՐԱՆՈՐՈԳՈՒՄՆԵՐ"])
    
    # --- 📦 ԱՊՐԱՆՔՆԵՐԻ ԲԱԺԻՆ ---
    with tab1:
        if st.session_state.role == "admin":
            if st.button("🚨 ՋՆՋԵԼ ԱՄԲՈՂՋ ԱՊՐԱՆՔՆԵՐԻ ԲԱԶԱՆ", type="primary"):
                delete_all_products_dialog()
            st.markdown("---")

        res = requests.get(f"{SUPABASE_URL}/rest/v1/{PRODUCTS_TABLE}?select=*&order=id.asc", headers=HEADERS)
        if res.status_code == 200 and res.json():
            prod_list = res.json()
            
            p_cols = st.columns([0.8, 2.2, 1.2, 1.2, 2.3, 1.5, 1.3, 1.1])
            p_cols[0].markdown("<div class='table-header'>🆔 ID</div>", unsafe_allow_html=True)
            p_cols[1].markdown("<div class='table-header'>📝 Մոդել</div>", unsafe_allow_html=True)
            p_cols[2].markdown("<div class='table-header'>💾 Հիշող.</div>", unsafe_allow_html=True)
            p_cols[3].markdown("<div class='table-header'>🎨 Գույն</div>", unsafe_allow_html=True)
            p_cols[4].markdown("<div class='table-header'>🔢 IMEI / Սերիական</div>", unsafe_allow_html=True)
            p_cols[5].markdown("<div class='table-header'>📁 Խումբ</div>", unsafe_allow_html=True)
            p_cols[6].markdown("<div class='table-header'>📅 Գնելու Օր</div>", unsafe_allow_html=True)
            p_cols[7].markdown("<div class='table-header'>📝 Ուղղել</div>", unsafe_allow_html=True)
            
            for idx, row in enumerate(prod_list):
                row_style = "table-row-even" if idx % 2 == 1 else "table-row-odd"
                display_id = idx + 1
                row['display_id'] = display_id
                
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
                        if st.button("📝", key=f"edit_prod_{row['id']}"):
                            edit_product_dialog(row)
                    else: st.markdown(f"<div class='{row_style}'>🔒</div>", unsafe_allow_html=True)
        else: st.info("📦 Ապրանքների բազան դեռ դատարկ է։")

    # --- 🔧 ՎԵՐԱՆՈՐՈԳՈՒՄՆԵՐԻ ԲԱԺԻՆ ---
    with tab2:
        res_rem = requests.get(f"{SUPABASE_URL}/rest/v1/{REMONT_TABLE}?select=*&order=id.asc", headers=HEADERS)
        if res_rem.status_code == 200 and res_rem.json():
            rem_list = res_rem.json()
            
            rem_cols = st.columns([0.8, 1.5, 2, 1.5, 1.2, 1.2, 1, 1, 1])
            rem_cols[0].markdown("<div class='table-header'>🆔 ID</div>", unsafe_allow_html=True)
            rem_cols[1].markdown("<div class='table-header'>📝 Մոդել</div>", unsafe_allow_html=True)
            rem_cols[2].markdown("<div class='table-header'>🔢 IMEI</div>", unsafe_allow_html=True)
            rem_cols[3].markdown("<div class='table-header'>🏢 Կամպանիա</div>", unsafe_allow_html=True)
            rem_cols[4].markdown("<div class='table-header'>💵 Գումար</div>", unsafe_allow_html=True)
            rem_cols[5].markdown("<div class='table-header'>🚦 Կարգավիճակ</div>", unsafe_allow_html=True)
            rem_cols[6].markdown("<div class='table-header'>📱 Ինֆո</div>", unsafe_allow_html=True)
            rem_cols[7].markdown("<div class='table-header'>📝 Ուղղել</div>", unsafe_allow_html=True)
            rem_cols[8].markdown("<div class='table-header'>🗑️ Ջնջել</div>", unsafe_allow_html=True)
            
            for idx, rem_item in enumerate(rem_list):
                row_style = "table-row-even" if idx % 2 == 1 else "table-row-odd"
                display_id = idx + 1
                rem_item['display_id'] = display_id
                
                r_cols = st.columns([0.8, 1.5, 2, 1.5, 1.2, 1.2, 1, 1, 1])
                r_cols[0].markdown(f"<div class='{row_style}'><code>{display_id}</code></div>", unsafe_allow_html=True)
                r_cols[1].markdown(f"<div class='{row_style}'><b>{rem_item['model']}</b></div>", unsafe_allow_html=True)
                r_cols[2].markdown(f"<div class='{row_style}'><code>{rem_item['imei']}</code></div>", unsafe_allow_html=True)
                r_cols[3].markdown(f"<div class='{row_style}'>{rem_item['kampania'] if rem_item['kampania'] else '֊'}</div>", unsafe_allow_html=True)
                r_cols[4].markdown(f"<div class='{row_style}'>{rem_item['gumar']} 💰</div>", unsafe_allow_html=True)
                
                status_color = "#FFA500" if rem_item['kargavichak'] == "Վերանորոգման է" else "#00FF00" if rem_item['kargavichak'] == "Պատրաստ է" else "#999999"
                r_cols[5].markdown(f"<div class='{row_style}' style='color:{status_color}; font-weight:bold;'>{rem_item['kargavichak']}</div>", unsafe_allow_html=True)
                
                with r_cols[6]:
                    if st.button("👁️", key=f"view_rem_{rem_item['id']}"):
                        show_details_dialog(rem_item)
                        
                with r_cols[7]:
                    if st.session_state.role == "admin":
                        if st.button("📝", key=f"edit_rem_{rem_item['id']}"):
                            edit_remont_dialog(rem_item)
                    else: st.markdown(f"<div class='{row_style}'>🔒</div>", unsafe_allow_html=True)
                
                with r_cols[8]:
                    if st.session_state.role == "admin":
                        if st.button("🗑️", key=f"del_rem_{rem_item['id']}"):
                            delete_remont_dialog(rem_item['id'], display_id, rem_item['model'])
                    else: st.markdown(f"<div class='{row_style}'>🔒</div>", unsafe_allow_html=True)
        else: st.info("🔧 Վերանորոգման բազան դեռ դատարկ է։")

# --- 5. 📜 ՁԵՌՔԲԵՐՄԱՆ ՊԱՏՄՈՒԹՅՈՒՆ ---
elif st.session_state.page == "history" and st.session_state.role == "admin":
    st.title("📜 ՁԵՌՔԲԵՐՄԱՆ ՊԱՏՄՈՒԹՅՈՒՆ")
    res_hist = requests.get(f"{SUPABASE_URL}/rest/v1/{HISTORY_TABLE}?select=*&order=id.desc", headers=HEADERS)
    if res_hist.status_code == 200 and res_hist.json():
        df_hist = pd.DataFrame(res_hist.json())
        df_hist_clean = df_hist.rename(columns={
            'date': '📅 Ամսաթիվ', 'category': '📁 Խումբ', 'model': '📝 Մոդել',
            'imei': '🔢 IMEI', 'quantity': '📦 Քանակ', 'matakarar': '🏢 Մատակարար'
        })
        if 'id' in df_hist_clean.columns: df_hist_clean = df_hist_clean.drop(columns=['id'])
        st.dataframe(df_hist_clean, use_container_width=True, hide_index=True)
    else: st.info("📜 Պատմությունը դեռ դատարկ է։")

st.markdown('</div>', unsafe_allow_html=True) # Փակում ենք main-content div-ը

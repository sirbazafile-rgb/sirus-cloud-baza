import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIG & CONSTANTS ---
# --- CONFIG & CONSTANTS ---
# Հետ ենք դնում քո ուղիղ հղումները
SUPABASE_URL = "https://umbgvfyczrsjfxvpyaei.supabase.co"
SUPABASE_KEY = "sb_publishable_587nBtq5BdKGZqb8LdUjGA_2GhxqH6D"

# Աղյուսակների անունները
BAZA_TABLE = "sirus_baza"
HISTORY_TABLE = "sirus_history"
REPAIR_TABLE = "sirus_repair"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

st.set_page_config(page_title="SIRUS SYSTEM", layout="wide")

# --- SESSION STATE FOR NAVIGATION ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- CUSTOM CSS FOR MENU ---
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_html=True)

# --- TOP NAVIGATION BAR ---
# Հեռացվել է վերևի առանձին լոգո-կոճակը՝ կրկնողությունից խուսափելու համար
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("🏠 ԳԼԽԱՎՈՐ ԷՋ", key="nav_home"):
        st.session_state.page = "home"
        st.rerun()
with col2:
    if st.button("📦 ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ", key="nav_purchase"):
        st.session_state.page = "purchase"
        st.rerun()
with col3:
    if st.button("🔧 ՎԵՐԱՆՈՐՈԳՈՒՄ", key="nav_repair"):
        st.session_state.page = "repair"
        st.rerun()
with col4:
    if st.button("📊 SIRUS CLOUD BAZA", key="nav_baza"):
        st.session_state.page = "baza"
        st.rerun()
with col5:
    if st.button("📜 ՁԵՌՔԲԵՐՄԱՆ ՊԱՏՄՈՒԹՅՈՒՆ", key="nav_history"):
        st.session_state.page = "history"
        st.rerun()
with col6:
    if st.button("🚪 ԵԼՔ", key="nav_logout"):
        st.session_state.page = "logout"
        st.rerun()

st.markdown("---")

# --- HELPER FUNCTIONS ---
def check_duplicate_imei(table, imei_code):
    """Ստուգում է IMEI-ի դուբլիկատ լինելը բազայում"""
    if not imei_code:
        return False
    res = requests.get(f"{SUPABASE_URL}/rest/v1/{table}?imei=eq.{imei_code}", headers=HEADERS)
    if res.status_code == 200 and len(res.json()) > 0:
        return True
    return False

def reset_table_sequence(table_name):
    """Մաքրելուց հետո ID-ների հերթականությունը զրոյացնում է դեպի 1"""
    # Այս ֆունկցիան աշխատում է RPC-ի միջոցով Supabase-ում
    rpc_url = f"{SUPABASE_URL}/rest/v1/rpc/reset_sequence"
    payload = {"table_to_reset": table_name}
    requests.post(rpc_url, headers=HEADERS, json=payload)

# --- PAGE LOGIC ---

# 1. HOME PAGE
if st.session_state.page == "home":
    st.title("🚀 SIRUS SYSTEM (Admin Mode)")
    st.subheader("Հեռախոսների և Բիզնեսի Կառավարման Ամպային Համակարգ")
    st.write("Բարի գալուստ համակարգ։ Օգտագործեք վերևի մենյուն էջերի միջև անցնելու համար։")

# 2. PURCHASE PAGE (ԱՊՐԱՆՔԻ ՁԵՌՔԲԵՐՈՒՄ)
elif st.session_state.page == "purchase":
    st.title("📦 Ապրանքի Ձեռքբերում / Մուտքագրում")
    
    tab_manual, tab_excel = st.tabs(["✍️ Ձեռքով Մուտքագրում", "📊 Excel-ով Ներբեռնում"])
    
    with tab_manual:
        with st.form("manual_entry_form", clear_on_submit=True):
            m_date = st.date_input("Ամսաթիվ", datetime.now())
            m_cat = st.selectbox("Կատեգորիա", ["Phone", "Tablet", "Accessory", "Other"])
            m_model = st.text_input("Մոդել")
            m_group = st.text_input("Խումբ (Group)")
            m_imei = st.text_input("IMEI / Սերիալ համար")
            m_matakarar = st.text_input("Մատակարար")
            
            submit_btn = st.form_submit_form_button = st.form_submit_button("Գրանցել Բազայում")
            
            if submit_btn:
                clean_imei = m_imei.strip()
                # Դուբլիկատ IMEI-ի ստուգում և զգուշացում
                if check_duplicate_imei(BAZA_TABLE, clean_imei):
                    st.warning(f"⚠️ Ուշադրություն. '{clean_imei}' IMEI-ով ապրանք արդեն գոյություն ունի բազայում:")
                
                # Մուտքագրման պրոցես
                baza_payload = {
                    "category": m_cat, "model": m_model, "group": m_group, 
                    "imei": clean_imei, "matakarar": m_matakarar
                }
                
                hist_payload = {
                    "date": str(m_date), "category": m_cat, "model": m_model, 
                    "imei": clean_imei, "quantity": 1, "matakarar": m_matakarar
                }
                
                # Բազա ուղարկելը
                res1 = requests.post(f"{SUPABASE_URL}/rest/v1/{BAZA_TABLE}", headers=HEADERS, json=baza_payload)
                # Պատմության մեջ գրանցելը (Ուղղված է hist_payload-ի սխալը)
                res2 = requests.post(f"{SUPABASE_URL}/rest/v1/{HISTORY_TABLE}", headers=HEADERS, json=hist_payload)
                
                if res1.status_code in [200, 201]:
                    st.success("🎯 Ապրանքը հաջողությամբ գրանցվեց հիմնական բազայում և պատմության մեջ:")
                else:
                    st.error("Սխալ տեղի ունեցավ գրանցելիս:")

    with tab_excel:
        st.subheader("Ներբեռնել Excel Ֆայլ")
        uploaded_file = st.file_uploader("Ընտրեք .xlsx ֆայլը", type=["xlsx"])
        
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            st.write("Ֆայլի նախադիտում.")
            st.dataframe(df.head())
            
            if st.button("Հաստատել և Մուտքագրել Բոլորը"):
                success_count = 0
                for index, row in df.iterrows():
                    ex_date = str(row.get("Ամսաթիվ", datetime.now().date()))
                    cat_val = row.get("Կատեգորիա", "Other")
                    ex_model = row.get("Մոդել", "")
                    ex_group = row.get("Խումբ", "")
                    clean_imei = str(row.get("IMEI", "")).strip()
                    ex_matakarar = row.get("Մատակարար", "")
                    
                    if check_duplicate_imei(BAZA_TABLE, clean_imei):
                        st.warning(f"⚠️ Դուբլիկատ IMEI տող {index+2}-ում. {clean_imei}")
                    
                    baza_payload = {
                        "category": cat_val, "model": ex_model, "group": ex_group, 
                        "imei": clean_imei, "matakarar": ex_matakarar
                    }
                    excel_hist_payload = {
                        "date": ex_date, "category": cat_val, "model": ex_model, 
                        "imei": clean_imei, "quantity": 1, "matakarar": ex_matakarar
                    }
                    
                    r1 = requests.post(f"{SUPABASE_URL}/rest/v1/{BAZA_TABLE}", headers=HEADERS, json=baza_payload)
                    r2 = requests.post(f"{SUPABASE_URL}/rest/v1/{HISTORY_TABLE}", headers=HEADERS, json=excel_hist_payload)
                    
                    if r1.status_code in [200, 201]:
                        success_count += 1
                        
                st.success(f"📈 Հաջողությամբ բազա ներմուծվեց {success_count} ապրանք:")

# 3. REPAIR PAGE (ՎԵՐԱՆՈՐՈԳՈՒՄ)
elif st.session_state.page == "repair":
    st.title("🔧 Վերանորոգման Բաժին")
    
    # Այստեղ գրվում է վերանորոգման մոդուլի տրամաբանությունը
    st.info("Վերանորոգման տվյալների կառավարման վահանակ։")
    
    # Ջնջելու գաղտնաբառի ստուգում Ռեմոնտի համար (Password: 12)
    with st.expander("🗑️ Մաքրել Վերանորոգման Աղյուսակը"):
        repair_pass = st.text_input("Մուտքագրեք գաղտնաբառը", type="password", key="rep_pass")
        if st.button("Հաստատել Մաքրումը", key="rep_clear_btn"):
            if repair_pass == "12":
                res = requests.delete(f"{SUPABASE_URL}/rest/v1/{REPAIR_TABLE}?id=gt.0", headers=HEADERS)
                if res.status_code in [200, 204]:
                    reset_table_sequence(REPAIR_TABLE)
                    st.success("Վերանորոգման աղյուսակը մաքրվեց, ID-ները զրոյացվեցին:")
                else:
                    st.error("Չհաջողվեց մաքրել աղյուսակը:")
            else:
                st.error("Սխալ գաղտնաբառ:")

# 4. SIRUS CLOUD BAZA PAGE (📊 ԲՈՒՆ ԲԱԶԱՆ)
elif st.session_state.page == "baza":
    st.title("📊 SIRUS CLOUD BAZA (Ապրանքների Աղյուսակ)")
    
    # Տվյալների բեռնում Supabase-ից
    res = requests.get(f"{SUPABASE_URL}/rest/v1/{BAZA_TABLE}?select=*", headers=HEADERS)
    
    if res.status_code == 200 and len(res.json()) > 0:
        data = res.json()
        df = pd.DataFrame(data)
        
        # Սյուների հերթականության կարգավորում (Group-ը Մոդելից հետո)
        desired_columns = ['id', 'category', 'model', 'group', 'imei', 'matakarar']
        # Ստուգում ենք, որ սյուները կան ֆրեյմում, նոր դասավորում
        existing_cols = [col for col in desired_columns if col in df.columns]
        df = df[existing_cols]
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Ապրանքների բազան դատարկ է:")
        
    # Ջնջելու գաղտնաբառի ստուգում Ընդհանուր Բազայի համար (Password: 89)
    with st.expander("🗑️ Մաքրել Հիմնական Ապրանքների Բազան"):
        baza_pass = st.text_input("Մուտքագրեք գաղտնաբառը", type="password", key="baz_pass")
        if st.button("Հաստատել Մաքրումը", key="baz_clear_btn"):
            if baza_pass == "89":
                res = requests.delete(f"{SUPABASE_URL}/rest/v1/{BAZA_TABLE}?id=gt.0", headers=HEADERS)
                if res.status_code in [200, 204]:
                    reset_table_sequence(BAZA_TABLE)
                    st.success("Հիմնական բազան լիովին մաքրվեց, ID-ները զրոյացվեցին:")
                    st.rerun()
                else:
                    st.error("Չհաջողվեց մաքրել բազան:")
            else:
                st.error("Սխալ գաղտնաբառ:")

# 5. HISTORY PAGE (ՊԱՏՄՈՒԹՅՈՒՆ)
elif st.session_state.page == "history":
    st.title("📜 Ձեռքբերումների Պատմություն")
    res = requests.get(f"{SUPABASE_URL}/rest/v1/{HISTORY_TABLE}?select=*", headers=HEADERS)
    if res.status_code == 200 and len(res.json()) > 0:
        st.dataframe(pd.DataFrame(res.json()), use_container_width=True)
    else:
        st.info("Պատմության բազան դատարկ է:")

# 6. LOGOUT PAGE
elif st.session_state.page == "logout":
    st.title("🚪 Դուրս գալ համակարգից")
    st.write("Դուք դուրս եկաք ադմինիստրատիվ համակարգից։")

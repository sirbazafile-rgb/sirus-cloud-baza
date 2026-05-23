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

st.set_page_config(page_title="Phone Business Baza", layout="wide")
st.title("📱 Հեռախոսների Ամպային Բազա")
st.write("Ավելացրու նոր ապրանք և տես բազայի վիճակը իրական ժամանակում։")

# --- ՄՈՒՏՔԱԳՐՄԱՆ ԻՆՏԵՐՖԵՅՍ ---
st.subheader("➕ Ավելացնել նոր հեռախոս")

col1, col2, col3 = st.columns(3)
with col1:
    model = st.text_input("Մոդել (օր. Samsung A17)", placeholder="Samsung A17")
    color = st.text_input("Գույն (օր. Black)", placeholder="Black")
with col2:
    storage = st.text_input("Հիշողություն (օր. 6/128GB կամ 256)", placeholder="6/128GB")
    imei = st.text_input("IMEI կոդ", placeholder="123456789")
with col3:
    matakarar = st.text_input("Մատակարար (օր. Dubai)", placeholder="Dubai")
    buy_date = st.date_input("Գնելու Ամսաթիվ", datetime.now())

nshumner = st.text_area("Նշումներ (Պարտադիր չէ)", placeholder="Լրացուցիչ տեղեկություն...")

if st.button("💾 Ավելացնել Բազայում", type="primary"):
    if model and imei:
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
            st.success(f"🎉 {model}-ը հաջողությամբ ավելացավ բազայում:")
            st.rerun()
        else:
            st.error(f"Խնդիր առաջացավ բազայի հետ կապվելիս: {response.text}")
    else:
        st.warning("⚠️ Խնդրում ենք լրացնել Մոդել և IMEI դաշտերը։")

st.markdown("---")

# --- ՏՎՅԱԼՆԵՐԻ ՑՈՒՑԱԴՐՈՒՄ ---
st.subheader("📊 Բազայում եղած ապրանքները")

read_response = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*", headers=HEADERS)

if read_response.status_code == 200:
    data = read_response.json()
    if data:
        df = pd.DataFrame(data)
        
        # Դասավորում ենք սյունակները ճիշտ հերթականությամբ
        ordered_cols = ['id', 'model', 'storage', 'color', 'imei', 'matakarar', 'buy_date', 'nshumner', 'created_at']
        cols_to_show = [c for c in ordered_cols if c in df.columns]
        df_clean = df[cols_to_show]
        
        # Փոխում ենք աղյուսակի գլխագրերի անունները հայերենի
        rename_dict = {
            'id': 'ID', 
            'model': 'Մոդել', 
            'storage': 'Հիշողություն', 
            'color': 'Գույն', 
            'imei': 'IMEI', 
            'matakarar': 'Մատակարար', 
            'buy_date': 'Գնելու Օր', 
            'nshumner': 'Նշումներ', 
            'created_at': 'Ավելացման Ժամ'
        }
        df_clean = df_clean.rename(columns={k: v for k, v in rename_dict.items() if k in df_clean.columns})
        
        st.dataframe(df_clean, use_container_width=True)
    else:
        st.info("Բազան դեռ դատարկ է։ Ավելացրու առաջին հեռախոսը։")
else:
    st.error("Չհաջողվեց կարդալ տվյալները բազայից։")

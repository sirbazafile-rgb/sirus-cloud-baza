import streamlit as st
import requests
import pandas as pd

# --- ՔՈ ԲԱԶԱՅԻ ՏՎՅԱԼՆԵՐԸ ---
SUPABASE_URL = "https://umbgvfyczrsjfxvpyaei.supabase.co"
SUPABASE_KEY = "sb_publishable_587nBtq5BdKGZqb8LdUjGA_2GhxqH6D"
TABLE_NAME = "products"  # Եթե աղյուսակիդ անունը ուրիշ է, փոխիր սա

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

st.set_page_config(page_title="Phone Business Baza", layout="centered")
st.title("📱 Հեռախոսների Ամպային Բազա")
st.write("Ավելացրու նոր ապրանք և տես բազայի վիճակը իրական ժամանակում։")

# --- ՄՈՒՏՔԱԳՐՄԱՆ ԻՆՏԵՐՖԵՅՍ ---
st.subheader("➕ Ավելացնել նոր հեռախոս")

col1, col2 = st.columns(2)
with col1:
    model = st.text_input("Մոդել (օր. iPhone 15)", placeholder="iPhone 15")
    color = st.text_input("Գույն (օր. Black)", placeholder="Black")
with col2:
    storage = st.number_input("Հիշողություն (միայն թիվ)", min_value=1, value=128, step=1)
    imei = st.text_input("IMEI կոդ", placeholder="123456789012345")

nshumner = st.text_area("Նշումներ (Պարտադիր չէ)")

if st.button("💾 Ավելացնել Բազայում", type="primary"):
    if model and imei:  # Ստուգում ենք, որ հիմնական դաշտերը դատարկ չեն
        payload = {
            "model": model,
            "storage": int(storage),
            "color": color,
            "imei": imei,
            "nshumner": nshumner if nshumner else None
        }
        
        # Ուղարկում ենք տվյալները Supabase
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

# Կարդում ենք տվյալները Supabase-ից
read_response = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*", headers=HEADERS)

if read_response.status_code == 200:
    data = read_response.json()
    if data:
        # Սարքում ենք աղյուսակ (DataFrame)
        df = pd.DataFrame(data)
        
        # Ռեդակցիա ենք անում սյունակները սիրուն տեսքի համար
        if 'storage' in df.columns:
            # Ավտոմատ կպցնում ենք "GB" տեքստը թվի կողքը ցուցադրելիս
            df['storage'] = df['storage'].astype(str) + " GB"
            
        # Մաքրում ենք ավելորդ համակարգային սյունակները ցույց չտալու համար
        cols_to_show = [c for c in ['id', 'model', 'storage', 'color', 'imei', 'nshumner', 'created_at'] if c in df.columns]
        df_clean = df[cols_to_show]
        
        # Ցույց ենք տալիս էկրանին
        st.dataframe(df_clean, use_container_width=True)
    else:
        st.info("Բազան դեռ դատարկ է։ Ավելացրու առաջին հեռախոսը։")
else:
    st.error("Չհաջողվեց կարդալ տվյալները բազայից։")

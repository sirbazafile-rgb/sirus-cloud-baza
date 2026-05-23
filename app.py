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

# Custom CSS՝ տեսքը էլ ավելի սիրունացնելու համար
st.markdown("""
    <style>
    .main { padding-top: 2rem; }
    .stButton>button { width: 100%; border-radius: 8px; height: 45px; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 8px; }
    div[data-testid="stExpander"] { border-radius: 10px; background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); }
    </style>
""", unsafe_allow_html=True)

st.title("📱 SIRUS CLOUD BAZA")
st.caption("✨ Հեռախոսների կառավարման քո անձնական պրոֆեսիոնալ համակարգը")

st.markdown("---")

# --- ՖՈՒՆԿՑԻՈՆԱԼ: ԱՎԵԼԱՑՆԵԼ ՆՈՐ ՀԵՌԱԽՈՍ (ԾԱԼՎՈՂ ԲԼՈԿ) ---
with st.expander("➕ ԱՎԵԼԱՑՆԵԼ ՆՈՐ ՀԵՌԱԽՈՍ", expanded=False):
    st.write("Լրացրու ապրանքի տվյալները ներքևում.")
    
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
            # IMEI-ի ստուգում
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

st.markdown("<br>", unsafe_allow_html=True)

# --- ՖՈՒՆԿՑԻՈՆԱԼ: ՈՐՈՆՈՒՄ ՈՒ ԱՂՅՈՒՍԱԿ ---
st.subheader("📊 ԲԱԶԱՅՈՒՄ ԱՌԿԱ ԱՊՐԱՆՔՆԵՐԸ")

# Բերում ենք տվյալները բազայից
read_response = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*&order=id.desc", headers=HEADERS) # Նոր ավելացրածները կլինեն վերևում

if read_response.status_code == 200:
    data = read_response.json()
    if data:
        df = pd.DataFrame(data)
        
        # 🔍 ՍԻՐՈՒՆ ՈՐՈՆՄԱՆ ԴԱՇՏ (Search Bar)
        search_query = st.text_input("🔍 Արագ փնտրում (Գրիր Մոդելը, IMEI-ն, Մատակարարին կամ Գույնը)...", placeholder="Փնտրել...")
        
        # Ֆիլտրում ենք աղյուսակը ըստ որոնման տեքստի
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
            # Դասավորում և մաքրում ենք սյունակները
            ordered_cols = ['id', 'model', 'storage', 'color', 'imei', 'matakarar', 'buy_date', 'nshumner']
            cols_to_show = [c for c in ordered_cols if c in df_filtered.columns]
            df_clean = df_filtered[cols_to_show]
            
            # Հայերեն անուններ
            rename_dict = {
                'id': 'ID', 'model': 'Մոդել', 'storage': 'Հիշողություն', 
                'color': 'Գույն', 'imei': 'IMEI', 'matakarar': 'Մատակարար', 
                'buy_date': 'Գնելու Օր', 'nshumner': 'Նշումներ'
            }
            df_clean = df_clean.rename(columns={k: v for k, v in rename_dict.items() if k in df_clean.columns})
            
            # Ցուցադրում ենք աղյուսակը
            st.dataframe(df_clean, use_container_width=True, hide_index=True)
            st.caption(f"💡 Ցուցադրված է {len(df_clean)} հեռախոս:")
        else:
            st.info("🔍 Համապատասխան հեռախոս չգտնվեց։")
    else:
        st.info("📦 Բազան դեռ դատարկ է։")
else:
    st.error("Չհաջողվեց կապվել բազայի հետ։")

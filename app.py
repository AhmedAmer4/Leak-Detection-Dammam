import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="داشبورد تسربات الدمام", layout="wide")
st.title("🚰 نظام مراقبة تسربات المياه - الدمام")

# أسماء الملفات على GitHub (تأكد أنها data.csv و map.json)
CSV_FILE = "data.csv"
JSON_FILE = "map.json"

def load_data_with_force():
    df = None
    # تجربة كافة أنواع التشفير الممكنة لحل مشكلة 0xa9
    for enc in ['utf-8', 'cp1252', 'latin1', 'iso-8859-1', 'utf-16']:
        try:
            df = pd.read_csv(CSV_FILE, encoding=enc)
            return df, enc
        except:
            continue
    return None, None

try:
    if os.path.exists(CSV_FILE):
        df, successful_enc = load_data_with_force()
        
        if df is not None:
            st.success(f"✅ تم فك التشفير بنجاح باستخدام ({successful_enc})")
            
            # عرض الخريطة
            m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)

            # محاولة تحميل الخريطة وتجاهل أي حرف "بايظ" فيها
            if os.path.exists(JSON_FILE):
                try:
                    with open(JSON_FILE, "r", encoding="utf-8", errors="ignore") as f:
                        geo_data = json.load(f)
                    folium.GeoJson(geo_data, name="الأحياء").add_to(m)
                except:
                    st.warning("⚠️ حدود الأحياء بها مشكلة، سنعرض النقط فقط.")

            # إضافة النقاط
            for _, row in df.iterrows():
                if pd.notnull(row.get('latitude')) and pd.notnull(row.get('longitude')):
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=5, color='red', fill=True,
                        popup=f"بلاغ: {row.get('meter_name', 'مجهول')}"
                    ).add_to(m)

            st_folium(m, width=1100, height=500)
            st.balloons()
        else:
            st.error("❌ الملف موجود لكن التشفير معقد جداً، جرب حفظه كـ CSV UTF-8 من إكسل.")
    else:
        st.error(f"❌ لم أجد ملف {CSV_FILE} على GitHub!")

except Exception as e:
    st.error(f"🚨 خطأ تقني أخير: {e}")


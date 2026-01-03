import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import os

# إعداد الصفحة
st.set_page_config(page_title="تسربات الدمام", layout="wide")

st.title("🚰 نظام مراقبة تسربات المياه - الدمام")

# أسماء الملفات الجديدة (الإنجليزية)
CSV_FILE = "data.csv"
JSON_FILE = "map.json"

# فحص الملفات
col1, col2 = st.columns(2)
with col1:
    if os.path.exists(CSV_FILE):
        st.success(f"✅ تم العثور على {CSV_FILE}")
    else:
        st.error(f"❌ ملف {CSV_FILE} مفقود!")
with col2:
    if os.path.exists(JSON_FILE):
        st.success(f"✅ تم العثور على {JSON_FILE}")
    else:
        st.error(f"❌ ملف {JSON_FILE} مفقود!")

# محاولة التشغيل
try:
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        st.metric("إجمالي البلاغات", len(df))
        
        # إنشاء الخريطة
        m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)
        
        # تحميل الخريطة لو موجودة
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                geo_data = json.load(f)
            folium.GeoJson(geo_data, name="الأحياء").add_to(m)
        
        # إضافة النقاط
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5, color='red', fill=True,
                popup=f"بلاغ رقم: {row.get('meter_name', 'غير معروف')}"
            ).add_to(m)
        
        st_folium(m, width=1200, height=500)
        st.balloons()
    else:
        st.warning("يرجى التأكد من رفع الملفات بأسماء إنجليزية (data.csv و map.json)")

except Exception as e:
    st.error(f"🚨 خطأ فني: {e}")


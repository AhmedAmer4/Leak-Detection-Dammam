import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# 1. إعداد الصفحة (لازم يكون أول سطر)
st.set_page_config(page_title="مراقبة تسربات الدمام", layout="wide")

st.title("🚰 نظام مراقبة تسربات المياه - الدمام")
st.write("---")

# 2. فحص وجود الملفات على GitHub (تأكد من الأسماء دي بالظبط)
csv_file = "water_leakage_data.csv"
json_file = "dammam.json"

# عرض حالة الملفات عشان نعرف المشكلة فين
col1, col2 = st.columns(2)
with col1:
    if os.path.exists(csv_file):
        st.success(f"✅ تم العثور على ملف البيانات: {csv_file}")
    else:
        st.error(f"❌ ملف {csv_file} غير موجود. تأكد من رفعه.")

with col2:
    if os.path.exists(json_file):
        st.success(f"✅ تم العثور على ملف الخريطة: {json_file}")
    else:
        st.error(f"❌ ملف {json_file} غير موجود. تأكد من رفعه.")

# 3. محاولة تشغيل الخريطة والبيانات
try:
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        st.metric("إجمالي البلاغات", len(df))
        
        # خريطة بسيطة
        m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)
        
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=4, color='red', fill=True
            ).add_to(m)
        
        st_folium(m, width=1000, height=500)
        st.balloons() 
        
except Exception as e:
    st.warning(f"هناك مشكلة في محتوى الملفات: {e}")

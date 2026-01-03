import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import os

# 1. إعداد الصفحة
st.set_page_config(page_title="مراقبة تسربات الدمام", layout="wide")

st.title("🚰 لوحة تحكم تسربات المياه - الدمام")
st.write("---")

# أسماء الملفات بعد التعديل
CSV_FILE = "data.csv"
JSON_FILE = "map.json"

# 2. فحص وجود الملفات وعرض الحالة للمستخدم
col1, col2 = st.columns(2)
with col1:
    if os.path.exists(CSV_FILE):
        st.success(f"✅ تم العثور على ملف البيانات: {CSV_FILE}")
    else:
        st.error(f"❌ ملف {CSV_FILE} غير موجود في GitHub")

with col2:
    if os.path.exists(JSON_FILE):
        st.success(f"✅ تم العثور على ملف الخريطة: {JSON_FILE}")
    else:
        st.warning(f"⚠️ ملف {JSON_FILE} غير موجود (ستعمل الخريطة بدون حدود الأحياء)")

# 3. محاولة تشغيل النظام
try:
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        
        # عرض المؤشرات
        st.metric("إجمالي البلاغات المكتشفة", len(df))
        
        # إنشاء الخريطة
        m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)
        
        # تحميل ملف الأحياء لو موجود
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                geo_data = json.load(f)
            folium.GeoJson(geo_data, name="الأحياء", 
                           style_function=lambda x: {'fillColor': 'blue', 'color': 'black', 'weight': 1, 'fillOpacity': 0.1}
                          ).add_to(m)
        
        # إضافة النقط (التسربات)
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=4, color='red', fill=True,
                popup=f"بلاغ: {row.get('meter_name', 'مجهول')}"
            ).add_to(m)
        
        # عرض الخريطة
        st_folium(m, width=1100, height=500)
        st.balloons()
    else:
        st.info("يرجى التأكد من رفع ملف data.csv لكي تظهر البيانات.")

except Exception as e:
    st.error(f"🚨 خطأ فني في الكود أو البيانات: {e}")



import streamlit as st

# 1. أول حاجة نكتب العنوان عشان نتأكد إن التطبيق شغال
st.set_page_config(page_title="تسربات الدمام", layout="wide")
st.title("🚰 نظام مراقبة تسربات المياه - الدمام")
st.write("جاري فحص الملفات وتشغيل النظام...")

import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os

# 2. فحص وجود الملفات قبل أي شيء
csv_path = "water_leakage_data.csv"
json_path = "dammam.json"

if not os.path.exists(csv_path):
    st.error(f"❌ ملف البيانات {csv_path} غير موجود على GitHub!")
    st.stop()

if not os.path.exists(json_path):
    st.error(f"❌ ملف الخريطة {json_path} غير موجود على GitHub!")
    st.stop()

# 3. دالة التحميل
@st.cache_data
def load_data():
    df = pd.read_csv(csv_path)
    with open(json_path, "r", encoding="utf-8") as f:
        raw_json = json.load(f)
    
    # تحويل صيغة ArcGIS لـ GeoJSON
    features = []
    for feat in raw_json.get('features', []):
        if 'geometry' in feat and 'rings' in feat['geometry']:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": feat['geometry']['rings']},
                "properties": feat.get('attributes', {})
            })
    return df, {"type": "FeatureCollection", "features": features}

try:
    df, geo_data = load_data()
    st.success("✅ تم الاتصال بقاعدة البيانات بنجاح")

    # عرض المؤشرات
    c1, c2 = st.columns(2)
    with c1:
        st.metric("إجمالي البلاغات", len(df))
    with c2:
        st.metric("الحالات المكتشفة اليوم", "3")

    # الخريطة
    st.subheader("التوزيع الجغرافي للبلاغات")
    m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)
    folium.GeoJson(geo_data, name="الأحياء").add_to(m)
    
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4, color='red', fill=True
        ).add_to(m)
    
    st_folium(m, width=1100, height=500)

except Exception as e:
    st.error(f"🚨 حدث خطأ أثناء تشغيل البيانات: {e}")

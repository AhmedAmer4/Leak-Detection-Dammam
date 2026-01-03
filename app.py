import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os

st.set_page_config(page_title="تسربات الدمام", layout="wide")

# دالة للتأكد من وجود الملفات
def check_files():
    files = ["water_leakage_data.csv", "dammam.json"]
    missing = [f for f in files if not os.path.exists(f)]
    return missing

st.title("🚰 لوحة تحكم تسربات المياه - الدمام")

missing_files = check_files()
if missing_files:
    st.error(f"⚠️ الملفات دي مش موجودة على GitHub: {missing_files}")
    st.info("تأكد من رفع الملفات بنفس الأسماء المكتوبة فوق بالظبط.")
else:
    try:
        # تحميل البيانات
        df = pd.read_csv("water_leakage_data.csv")
        with open("dammam.json", "r", encoding="utf-8") as f:
            geo_data = json.load(f)
        
        # عرض إحصائية سريعة
        st.success("✅ تم تحميل البيانات بنجاح!")
        st.metric("عدد البلاغات", len(df))
        
        # الخريطة
        m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)
        folium.GeoJson(geo_data).add_to(m)
        for _, row in df.iterrows():
            folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=3, color='red').add_to(m)
        st_folium(m, width=1000)

    except Exception as e:
        st.error(f"❌ حصل خطأ في الكود: {e}")

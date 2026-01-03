import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="داشبورد الدمام", layout="wide")

# الكود ده بيقرأ الملف بترميز utf-8-sig (الـ sig دي مخصوصة عشان تشيل الـ \xef\xbb\xbf اللي شفناها)
CSV_FILE = "data.csv"

st.title("🚰 نظام مراقبة تسربات المياه - الدمام")

if os.path.exists(CSV_FILE):
    try:
        # السر كله في 'utf-8-sig'
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        
        st.success("✅ تم الاتصال وقراءة البيانات بنجاح!")
        
        # عرض الخريطة
        m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)
        
        for _, row in df.iterrows():
            try:
                folium.CircleMarker(
                    location=[float(row['latitude']), float(row['longitude'])],
                    radius=5, color='red', fill=True,
                    popup=f"عداد: {row['meter_name']}"
                ).add_to(m)
            except:
                continue
        
        st_folium(m, width=1200, height=500)
        st.balloons()
        
    except Exception as e:
        st.error(f"🚨 خطأ فني: {e}")
else:
    st.error("❌ الملف غير موجود")

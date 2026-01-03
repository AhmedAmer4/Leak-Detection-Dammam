import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="نظام تسربات الدمام", layout="wide")
st.title("🚰 خريطة بلاغات تسربات المياه - الدمام")

CSV_FILE = "data.csv"

if os.path.exists(CSV_FILE):
    try:
        # القراءة الناجحة اللي وصلنا لها
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        
        st.success("✅ تم استلام البيانات.. جاري رسم الخريطة")
        
        # عرض الجدول (زي ما ظهر عندك في الصورة)
        st.write("عينة من البيانات المرصودة:")
        st.dataframe(df.head(5))
        
        # إنشاء الخريطة وتركز على أول نقطة في ملفك
        start_lat = df['latitude'].iloc[0]
        start_lon = df['longitude'].iloc[0]
        m = folium.Map(location=[start_lat, start_lon], zoom_start=14)
        
        # رسم النقط
        for _, row in df.iterrows():
            try:
                folium.Marker(
                    location=[float(row['latitude']), float(row['longitude'])],
                    popup=f"عداد: {row['meter_name']}",
                    tooltip=row.get('area_name', 'الدمام'),
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)
            except:
                continue
        
        # عرض الخريطة بحجم كبير
        st_folium(m, width=1200, height=600)
        st.balloons()
        
    except Exception as e:
        st.error(f"🚨 خطأ في الرسم: {e}")
else:
    st.error("❌ ملف data.csv غير موجود")

import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os

# 1. إعداد الصفحة (أهم خطوة للسرعة)
st.set_page_config(page_title="داشبورد تسربات الدمام", layout="wide")

# 2. وظيفة تحميل البيانات مع "التخزين المؤقت" عشان ما يهنقش
@st.cache_data
def get_data():
    if os.path.exists("data.csv"):
        return pd.read_csv("data.csv", encoding='utf-8-sig')
    return None

df = get_data()

# --- القائمة الجانبية (Sidebar) المؤشرات اللي طلبتها ---
st.sidebar.title("📊 تحليل التسربات")

if df is not None:
    # مؤشر إجمالي التسربات
    st.sidebar.metric("إجمالي البلاغات", len(df))
    
    # حساب عدد التسربات لكل حي وعمل شارت
    if 'area_name' in df.columns:
        counts = df['area_name'].value_counts().reset_index()
        counts.columns = ['الحي', 'العدد']
        
        # رسم بياني احترافي
        fig = px.bar(counts.head(10), x='العدد', y='الحي', orientation='h',
                     title="أكثر 10 أحياء متضررة",
                     color='العدد', color_continuous_scale='Reds')
        fig.update_layout(showlegend=False, height=400)
        st.sidebar.plotly_chart(fig, use_container_width=True)

# --- الصفحة الرئيسية ---
st.title("🗺️ خريطة الرصد الميداني - الدمام")

if df is not None:
    # إنشاء الخريطة (استخدام Tiles خفيفة للتحميل السريع)
    m = folium.Map(location=[26.4207, 50.0888], zoom_start=11, tiles="CartoDB positron")

    # تحميل ملف الأحياء (بشكل آمن عشان ما يوقفش التحميل)
    if os.path.exists("map.json"):
        try:
            with open("map.json", "r", encoding="utf-8", errors="ignore") as f:
                geo_data = json.load(f)
            
            folium.GeoJson(
                geo_data,
                name="الأحياء",
                style_function=lambda x: {'fillColor': 'blue', 'color': 'black', 'weight': 1, 'fillOpacity': 0.05}
            ).add_to(m)
        except:
            st.sidebar.warning("⚠️ ملف الأحياء ثقيل، تم تحميل النقط فقط.")

    # إضافة نقط التسربات (الدوائر الحمراء)
    for _, row in df.iterrows():
        try:
            folium.CircleMarker(
                location=[float(row['latitude']), float(row['longitude'])],
                radius=4,
                color='red',
                fill=True,
                fill_opacity=0.8,
                popup=f"حي: {row.get('area_name', 'غير محدد')}"
            ).add_to(m)
        except:
            continue

    # عرض الخريطة
    st_folium(m, width="100%", height=600, returned_objects=[])
    st.balloons()
else:
    st.error("لم يتم العثور على ملف data.csv")

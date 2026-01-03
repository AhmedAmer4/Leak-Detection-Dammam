import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os

# إعداد الصفحة لتكون سريعة التحميل
st.set_page_config(page_title="داشبورد تسربات الدمام", layout="wide")

@st.cache_data
def load_data():
    if os.path.exists("data.csv"):
        # استخدام التشفير اللي اكتشفناه سوا
        return pd.read_csv("data.csv", encoding='utf-8-sig')
    return None

df = load_data()

# --- القائمة الجانبية (الشغل الاحترافي) ---
st.sidebar.title("📈 تحليل أحياء الدمام")

if df is not None:
    # 1. حساب عدد التسربات لكل حي
    if 'area_name' in df.columns:
        area_stats = df['area_name'].value_counts().reset_index()
        area_stats.columns = ['الحي', 'عدد البلاغات']
        
        # 2. مؤشر الحي الأكثر تضرراً (Metric)
        top_area = area_stats.iloc[0]
        st.sidebar.error(f"⚠️ أعلى حي بلاغات: {top_area['الحي']}")
        st.sidebar.metric("عدد البلاغات فيه", top_area['عدد البلاغات'])
        
        # 3. شارت احترافي يوضح التوزيع
        fig = px.pie(area_stats.head(8), values='عدد البلاغات', names='الحي', 
                     hole=0.4, title="نسبة التوزيع حسب الأحياء")
        st.sidebar.plotly_chart(fig, use_container_width=True)
    
    st.sidebar.divider()
    st.sidebar.info("تتم التحديثات بناءً على ملف data.csv المرفوع.")

# --- الصفحة الرئيسية ---
st.title("🗺️ خريطة الرصد الذكي للتسربات")

if df is not None:
    # إنشاء الخريطة بستايل خفيف (Positron)
    m = folium.Map(location=[26.4207, 50.0888], zoom_start=11, tiles="cartodbpositron")

    # محاولة إضافة ملف الأحياء "فقط" إذا كان حجمه معقول
    if os.path.exists("map.json"):
        try:
            with open("map.json", "r", encoding="utf-8") as f:
                geo_data = json.load(f)
            # رسم الحدود بخطوط خفيفة جداً لتسريع المتصفح
            folium.GeoJson(geo_data, style_function=lambda x: {
                'fillColor': 'transparent', 'color': 'blue', 'weight': 0.5
            }).add_to(m)
        except:
            pass # لو فشل بسبب الثقل يكمل ولا يوقف الموقع

    # إضافة نقاط التسربات
    for _, row in df.iterrows():
        try:
            folium.CircleMarker(
                location=[float(row['latitude']), float(row['longitude'])],
                radius=5, color='red', fill=True, fill_opacity=0.7,
                popup=f"حي: {row.get('area_name', 'غير معرف')}<br>عداد: {row.get('meter_name', 'مجهول')}"
            ).add_to(m)
        except:
            continue

    # عرض الخريطة
    st_folium(m, width="100%", height=600, returned_objects=[])
else:
    st.error("يرجى التأكد من رفع ملف data.csv")

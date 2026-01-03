import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os

# إعداد الصفحة وتوسيعها
st.set_page_config(page_title="نظام مراقبة تسربات الدمام", layout="wide")

# تحميل البيانات
CSV_FILE = "data.csv"
JSON_FILE = "map.json"

@st.cache_data
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    return None

df = load_data()

# --- القائمة الجانبية (المؤشرات) ---
with st.sidebar:
    st.header("📊 مؤشرات الأداء")
    if df is not None:
        st.metric("إجمالي التسربات", len(df))
        
        # حساب التسربات لكل حي (Chart)
        if 'area_name' in df.columns:
            area_counts = df['area_name'].value_counts().reset_index()
            area_counts.columns = ['الحي', 'عدد التسربات']
            
            # شارت احترافي للأحياء الأكثر تضرراً
            fig = px.bar(area_counts, x='عدد التسربات', y='الحي', orientation='h',
                         title="ترتيب الأحياء حسب التسربات",
                         color='عدد التسربات', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)

# --- الصفحة الرئيسية (الخريطة) ---
st.title("🗺️ الخريطة التفاعلية لتسربات المياه - الدمام")

if df is not None:
    # إنشاء الخريطة
    m = folium.Map(location=[26.4207, 50.0888], zoom_start=11, tiles="cartodbpositron")

    # 1. إضافة طبقة الأحياء (map.json)
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8", errors="ignore") as f:
                geo_data = json.load(f)
            
            # رسم حدود الأحياء بلون شفاف
            folium.GeoJson(
                geo_data,
                name="حدود الأحياء",
                style_function=lambda x: {
                    'fillColor': '#3186cc',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.1
                }
            ).add_to(m)
        except Exception as e:
            st.sidebar.error(f"خطأ في ملف الأحياء: {e}")

    # 2. إضافة نقاط التسربات (نقاط حمراء احترافية)
    for _, row in df.iterrows():
        try:
            folium.CircleMarker(
                location=[float(row['latitude']), float(row['longitude'])],
                radius=5,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.7,
                popup=f"حي: {row.get('area_name', 'غير معروف')}<br>عداد: {row.get('meter_name', 'غير متوفر')}"
            ).add_to(m)
        except:
            continue

    # عرض الخريطة بكامل عرض الصفحة
    st_folium(m, width="100%", height=700)
    st.balloons()

else:
    st.warning("يرجى رفع ملف data.csv لتفعيل لوحة التحكم.")

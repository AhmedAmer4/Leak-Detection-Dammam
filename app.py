import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os

st.set_page_config(page_title="داشبورد تسربات الدمام", layout="wide")

@st.cache_data
def load_all_data():
    df = pd.read_csv("data.csv", encoding='utf-8-sig')
    with open("map.json", "r", encoding="utf-8") as f:
        geo_data = json.load(f)
    return df, geo_data

try:
    df, geo_data = load_all_data()

    # حساب الإحصائيات لكل حي
    area_counts = df['area_name'].value_counts().reset_index()
    area_counts.columns = ['name', 'leaks'] # 'name' يجب أن يطابق المفتاح داخل الـ JSON

    # --- القائمة الجانبية ---
    st.sidebar.title("🚩 تحليل الكثافة")
    st.sidebar.metric("إجمالي البلاغات", len(df))
    fig = px.bar(area_counts, x='leaks', y='name', orientation='h', 
                 title="الأحياء الأكثر تضرراً", color='leaks', color_continuous_scale='Reds')
    st.sidebar.plotly_chart(fig, use_container_width=True)

    # --- الخريطة المقسمة (Choropleth) ---
    st.title("🗺️ خريطة كثافة التسربات في أحياء الدمام")
    
    m = folium.Map(location=[26.4207, 50.0888], zoom_start=11, tiles="cartodbpositron")

    # إضافة طبقة الأحياء الملونة
    folium.Choropleth(
        geo_data=geo_data,
        name="choropleth",
        data=area_counts,
        columns=["name", "leaks"],
        key_on="feature.properties.name", # تأكد أن هذا المفتاح موجود في الـ JSON الخاص بك
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="كثافة التسربات (عدد البلاغات)",
    ).add_to(m)

    # إضافة النقط فوق الأحياء الملونة
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3, color='black', weight=1, fill=True, fill_color='white'
        ).add_to(m)

    st_folium(m, width="100%", height=700)

except Exception as e:
    st.error(f"حدث خطأ في الربط: {e}")
    st.info("تأكد أن أسماء الأحياء في ملف الإكسل هي نفسها تماماً الموجودة في ملف الـ JSON")

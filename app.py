import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os

st.set_page_config(page_title="داشبورد تسربات الدمام", layout="wide")

# تحميل البيانات
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv", encoding='utf-8-sig')
    geo_data = None
    if os.path.exists("map.json"):
        with open("map.json", "r", encoding="utf-8") as f:
            geo_data = json.load(f)
    return df, geo_data

df, geo_data = load_data()

# --- القائمة الجانبية (المؤشرات الاحترافية) ---
st.sidebar.title("📊 مركز إحصائيات الدمام")

# حساب الإحصائيات مباشرة من عمود area_name اللي ظهر في صورتك
stats_df = df['area_name'].value_counts().reset_index()
stats_df.columns = ['الحي', 'عدد البلاغات']

# عرض المؤشر الرقمي
st.sidebar.metric("إجمالي البلاغات", len(df))

# رسم الشارت (Bar Chart)
fig = px.bar(stats_df.head(10), x='عدد البلاغات', y='الحي', 
             orientation='h', title="أكثر 10 أحياء متضررة",
             color='عدد البلاغات', color_continuous_scale='Reds')
st.sidebar.plotly_chart(fig, use_container_width=True)

# --- الخريطة الرئيسية ---
st.title("🗺️ خريطة توزيع تسربات المياه")

m = folium.Map(location=[26.4207, 50.0888], zoom_start=11, tiles="cartodbpositron")

# 1. تلوين الأحياء (Choropleth) باستخدام الربط بالاسم
if geo_data:
    folium.Choropleth(
        geo_data=geo_data,
        name="choropleth",
        data=stats_df,
        columns=["الحي", "عدد البلاغات"],
        key_on="feature.properties.name", # تأكد أن هذا الحقل موجود في الـ JSON
        fill_color="YlOrRd",
        fill_opacity=0.6,
        line_opacity=0.2,
        legend_name="مقياس الكثافة"
    ).add_to(m)

# 2. إضافة النقط الحمراء
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=4, color='red', fill=True, 
        popup=f"الحي: {row['area_name']}<br>العداد: {row['meter_name']}"
    ).add_to(m)

st_folium(m, width="100%", height=650)

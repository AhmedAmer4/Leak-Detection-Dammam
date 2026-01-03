import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px
from shapely.geometry import shape, Point
import os

st.set_page_config(page_title="داشبورد تسربات الدمام", layout="wide")

@st.cache_data
def process_spatial_data():
    # 1. تحميل البيانات
    df = pd.read_csv("data.csv", encoding='utf-8-sig')
    with open("map.json", "r", encoding="utf-8") as f:
        geo_data = json.load(f)
    
    # 2. إنشاء قاموس لتخزين عدد التسربات لكل حي
    # سنستخدم اسم الحي الموجود داخل الـ JSON كمفتاح
    neighborhood_leaks = {}
    for feature in geo_data['features']:
        name = feature['properties'].get('name', 'Unknown') # تأكد من اسم الحقل في الـ JSON
        neighborhood_leaks[name] = 0

    # 3. الربط المكاني (Spatial Join)
    # فحص كل نقطة من الإكسل وربطها بالحي
    for _, row in df.iterrows():
        try:
            point = Point(row['longitude'], row['latitude'])
            for feature in geo_data['features']:
                polygon = shape(feature['geometry'])
                if polygon.contains(point):
                    name = feature['properties'].get('name', 'Unknown')
                    neighborhood_leaks[name] += 1
                    break
        except:
            continue

    return df, geo_data, neighborhood_leaks

try:
    df, geo_data, leaks_dict = process_spatial_data()

    # تحويل نتائج الربط لجدول من أجل الشارت
    stats_df = pd.DataFrame(list(leaks_dict.items()), columns=['الحي', 'عدد التسربات'])
    stats_df = stats_df[stats_df['عدد التسربات'] > 0].sort_values(by='عدد التسربات', ascending=False)

    # --- Sidebar ---
    st.sidebar.title("📊 التحليل المكاني الذكي")
    st.sidebar.info("يتم تحديد الحي بناءً على الإحداثيات الجغرافية للنقطة داخل حدود مضلعات الـ JSON.")
    
    if not stats_df.empty:
        fig = px.pie(stats_df.head(10), values='عدد التسربات', names='الحي', hole=0.4)
        st.sidebar.plotly_chart(fig, use_container_width=True)
    
    # --- Main Map ---
    st.title("🗺️ خريطة كثافة التسربات (ربط إحداثيات)")
    m = folium.Map(location=[26.4207, 50.0888], zoom_start=11, tiles="cartodbpositron")

    # رسم الخريطة الملونة بناءً على الحسابات المكانية
    folium.Choropleth(
        geo_data=geo_data,
        name="choropleth",
        data=stats_df,
        columns=["الحي", "عدد التسربات"],
        key_on="feature.properties.name", # يجب أن يطابق الاسم في الـ JSON
        fill_color="YlOrRd",
        fill_opacity=0.6,
        line_opacity=0.2,
        legend_name="مقياس كثافة التسربات"
    ).add_to(m)

    # إضافة النقاط الفعلية للتأكيد
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=2, color='black', fill=True
        ).add_to(m)

    st_folium(m, width="100%", height=700)

except Exception as e:
    st.error(f"🚨 خطأ فني: {e}")

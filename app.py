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
    if not os.path.exists("data.csv") or not os.path.exists("map.json"):
        return None, None, {}
        
    df = pd.read_csv("data.csv", encoding='utf-8-sig')
    with open("map.json", "r", encoding="utf-8") as f:
        geo_data = json.load(f)
    
    neighborhood_leaks = {}
    
    # التأكد من وجود features في الملف
    features = geo_data.get('features', [])
    
    for feature in features:
        # محاولة الحصول على الاسم بأكثر من طريقة (لحل مشكلة الخطأ)
        props = feature.get('properties', {})
        name = props.get('name') or props.get('district_ar') or props.get('NAME_EN') or "حي غير معرف"
        neighborhood_leaks[name] = 0

    for _, row in df.iterrows():
        try:
            point = Point(row['longitude'], row['latitude'])
            for feature in features:
                polygon = shape(feature.get('geometry'))
                if polygon.contains(point):
                    props = feature.get('properties', {})
                    name = props.get('name') or props.get('district_ar') or props.get('NAME_EN') or "حي غير معرف"
                    neighborhood_leaks[name] += 1
                    break
        except:
            continue

    return df, geo_data, neighborhood_leaks

try:
    df, geo_data, leaks_dict = process_spatial_data()

    if df is not None:
        stats_df = pd.DataFrame(list(leaks_dict.items()), columns=['الحي', 'عدد التسربات'])
        stats_df = stats_df[stats_df['عدد التسربات'] > 0].sort_values(by='عدد التسربات', ascending=False)

        # --- Sidebar ---
        st.sidebar.title("📊 التحليل المكاني الذكي")
        if not stats_df.empty:
            fig = px.pie(stats_df.head(10), values='عدد التسربات', names='الحي', hole=0.4, title="توزيع التسربات")
            st.sidebar.plotly_chart(fig, use_container_width=True)
            st.sidebar.metric("أكثر حي متضرر", stats_df.iloc[0]['الحي'], f"{stats_df.iloc[0]['عدد التسربات']} بلاغ")

        # --- Main Map ---
        st.title("🗺️ خريطة كثافة التسربات (ربط إحداثيات)")
        m = folium.Map(location=[26.4207, 50.0888], zoom_start=11, tiles="cartodbpositron")

        # رسم الخريطة الملونة (Choropleth)
        if geo_data:
            # دالة لتحديد "المفتاح" اللي الكود هيربط عليه (بناءً على أول feature)
            first_feature = geo_data['features'][0]
            available_props = first_feature.get('properties', {}).keys()
            key_path = "feature.properties.name" if "name" in available_props else f"feature.properties.{list(available_props)[0]}"

            folium.Choropleth(
                geo_data=geo_data,
                name="choropleth",
                data=stats_df,
                columns=["الحي", "عدد التسربات"],
                key_on=key_path,
                fill_color="YlOrRd",
                fill_opacity=0.6,
                line_opacity=0.3,
                legend_name="مستوى كثافة التسربات"
            ).add_to(m)

        # إضافة النقاط
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=3, color='black', fill=True, popup=row.get('meter_name')
            ).add_to(m)

        st_folium(m, width="100%", height=700)
    else:
        st.error("تأكد من وجود الملفات data.csv و map.json")

except Exception as e:
    st.error(f"🚨 خطأ فني جديد: {e}")

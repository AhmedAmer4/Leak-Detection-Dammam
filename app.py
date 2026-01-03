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
        return None, None, {}, []
        
    df = pd.read_csv("data.csv", encoding='utf-8-sig')
    with open("map.json", "r", encoding="utf-8") as f:
        geo_data = json.load(f)
    
    neighborhood_leaks = {}
    json_names = []
    
    features = geo_data.get('features', [])
    for feature in features:
        props = feature.get('properties', {})
        # بنجرب كل الاحتمالات لاسم الحي
        name = props.get('name') or props.get('district_ar') or props.get('NAME_AR') or "Unknown"
        neighborhood_leaks[name] = 0
        json_names.append(name)

    # الربط المكاني
    for _, row in df.iterrows():
        try:
            point = Point(row['longitude'], row['latitude'])
            for feature in features:
                polygon = shape(feature.get('geometry'))
                if polygon.contains(point):
                    props = feature.get('properties', {})
                    name = props.get('name') or props.get('district_ar') or props.get('NAME_AR') or "Unknown"
                    neighborhood_leaks[name] += 1
                    break
        except: continue

    return df, geo_data, neighborhood_leaks, json_names

try:
    df, geo_data, leaks_dict, json_names = process_spatial_data()

    # --- Sidebar ---
    st.sidebar.title("📊 نظام كشف الأحياء")
    if json_names:
        st.sidebar.write(f"🔍 تم اكتشاف {len(json_names)} حي في ملف الـ JSON")
        if st.sidebar.checkbox("عرض أسماء الأحياء المكتشفة"):
            st.sidebar.write(list(set(json_names))[:20]) # عرض عينة

    if df is not None:
        stats_df = pd.DataFrame(list(leaks_dict.items()), columns=['name', 'leaks'])
        stats_df = stats_df[stats_df['leaks'] > 0].sort_values(by='leaks', ascending=False)

        if not stats_df.empty:
            fig = px.bar(stats_df.head(10), x='leaks', y='name', orientation='h', 
                         title="الأحياء الأكثر بلاغات (مكانيًا)", color='leaks')
            st.sidebar.plotly_chart(fig, use_container_width=True)

        # --- Main Map ---
        st.title("🗺️ خريطة كثافة التسربات الملونة")
        m = folium.Map(location=[26.4207, 50.0888], zoom_start=11, tiles="cartodbpositron")

        # رسم الملونات (Choropleth)
        if geo_data:
            # بنجرب نلاقي المفتاح الصح أوتوماتيك
            sample_props = geo_data['features'][0].get('properties', {}).keys()
            # بندور على الحقل اللي فيه أسماء الأحياء
            match_key = "name"
            for k in ['name', 'district_ar', 'NAME_AR']:
                if k in sample_props:
                    match_key = k
                    break
            
            folium.Choropleth(
                geo_data=geo_data,
                data=stats_df,
                columns=["name", "leaks"],
                key_on=f"feature.properties.{match_key}",
                fill_color="Reds",
                fill_opacity=0.7,
                line_opacity=0.4,
                legend_name="مقياس التسربات"
            ).add_to(m)

        # النقط الحمراء
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=4, color='black', fill=True, fill_color='red'
            ).add_to(m)

        st_folium(m, width="100%", height=700)

except Exception as e:
    st.error(f"خطأ: {e}")

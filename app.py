import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title="تسربات الدمام", layout="wide")

st.title("🚰 لوحة تحكم تسربات المياه - الدمام")

@st.cache_data
def load_and_fix_data():
    # 1. قراءة البيانات من الإكسل
    try:
        df = pd.read_csv("water_leakage_data.csv")
    except Exception as e:
        st.error(f"مشكلة في ملف الإكسل: {e}")
        return None, None

    # 2. قراءة وتحويل ملف الجيوجيسون الخاص بـ Esri
    try:
        with open("dammam.json", "r", encoding="utf-8") as f:
            esri_json = json.load(f)
        
        # تحويل صيغة Esri لـ GeoJSON بسيط يفهمه Folium
        features = []
        for feat in esri_json.get('features', []):
            if 'geometry' in feat and 'rings' in feat['geometry']:
                geojson_feat = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": feat['geometry']['rings']
                    },
                    "properties": feat.get('attributes', {})
                }
                features.append(geojson_feat)
        
        geo_data = {"type": "FeatureCollection", "features": features}
        return df, geo_data
    except Exception as e:
        st.error(f"مشكلة في ملف الخريطة (JSON): {e}")
        return df, None

df, geo_data = load_and_fix_data()

if df is not None:
    # إحصائيات سريعة
    st.metric("إجمالي البلاغات المكتشفة", len(df))
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("تحليل التوصيلات")
        fig = px.pie(df, names='house_connection_TYPE')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("خريطة التوزيع المكاني")
        # مركز الخريطة (الدمام)
        m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)
        
        if geo_data:
            folium.GeoJson(geo_data, name="الأحياء", 
                           style_function=lambda x: {'fillColor': 'green', 'color': 'black', 'weight': 1, 'fillOpacity': 0.1}).add_to(m)
        
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=3, color='red', fill=True,
                popup=f"عداد: {row['meter_name']}"
            ).add_to(m)
        
        st_folium(m, width=700, height=500)


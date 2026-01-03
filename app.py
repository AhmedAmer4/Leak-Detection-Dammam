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
    # 1. قراءة بيانات الإكسل
    df = pd.read_csv("water_leakage_data.csv")
    
    # 2. قراءة وتحويل ملف Esri JSON
    with open("dammam.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # تحويل من صيغة Esri (rings) إلى صيغة GeoJSON (coordinates)
    features = []
    for feat in data.get('features', []):
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

try:
    df, geo_data = load_and_fix_data()
    
    # صف الإحصائيات
    st.metric("إجمالي البلاغات", len(df))
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("توزيع أنواع التوصيلات")
        fig = px.pie(df, names='house_connection_TYPE')
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("مواقع التسربات على الخريطة")
        # إحداثيات الدمام
        m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)
        
        # إضافة الأحياء بعد التحويل
        folium.GeoJson(geo_data, name="الأحياء", 
                       style_function=lambda x: {'fillColor': 'blue', 'color': 'black', 'weight': 1, 'fillOpacity': 0.1}
                      ).add_to(m)
        
        # إضافة النقط
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=3, color='red', fill=True,
                popup=f"عداد: {row['meter_name']}"
            ).add_to(m)
        
        st_folium(m, width=700, height=500)

except Exception as e:
    st.error(f"حدث خطأ: {e}")
    st.info("تأكد من أن ملف الإكسل اسمه water_leakage_data.csv وملف الجيوجيسون اسمه dammam.json")



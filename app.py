import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os

st.set_page_config(page_title="داشبورد تسربات الدمام", layout="wide")

st.markdown("<h1 style='text-align: right;'>🚰 مراقبة تسربات المياه - الدمام</h1>", unsafe_allow_html=True)

# دالة ذكية لتحويل ملف ArcGIS JSON إلى GeoJSON
def convert_esri_to_geojson(esri_json):
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
    return {"type": "FeatureCollection", "features": features}

# أسماء الملفات (تأكد من مطابقتها في GitHub)
csv_name = "water_leakage_data.csv"
json_name = "dammam.json"

if not os.path.exists(csv_name) or not os.path.exists(json_name):
    st.error(f"⚠️ ملفات ناقصة! تأكد من وجود {csv_name} و {json_name} على GitHub")
else:
    try:
        # 1. تحميل البيانات
        df = pd.read_csv(csv_name)
        with open(json_name, "r", encoding="utf-8") as f:
            raw_json = json.load(f)
        
        # 2. تحويل الخريطة
        geojson_data = convert_esri_to_geojson(raw_json)
        
        # 3. العرض
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("إجمالي البلاغات", len(df))
            fig = px.pie(df, names='house_connection_TYPE', title="أنواع التوصيلات")
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("خريطة المواقع")
            m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)
            folium.GeoJson(geojson_data, name="الأحياء", 
                           style_function=lambda x: {'fillColor': 'blue', 'fillOpacity': 0.1, 'color': 'black', 'weight': 1}
                          ).add_to(m)
            
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=3, color='red', fill=True,
                    popup=f"عداد: {row['meter_name']}"
                ).add_to(m)
            st_folium(m, width=700, height=500)
            
    except Exception as e:
        st.error(f"❌ حدث خطأ داخلي: {e}")



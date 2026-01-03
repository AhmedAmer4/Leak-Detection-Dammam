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
    if not os.path.exists("data.csv"): return None, None, {}
    
    df = pd.read_csv("data.csv", encoding='utf-8-sig')
    geo_data = None
    neighborhood_leaks = {}

    if os.path.exists("map.json"):
        try:
            with open("map.json", "r", encoding="utf-8") as f:
                geo_data = json.load(f)
            
            # التأكد من وجود قائمة Features
            features = geo_data.get('features', [])
            if features:
                for feature in features:
                    props = feature.get('properties', {})
                    # محاولة استخراج أي اسم حي متاح
                    name = props.get('name') or props.get('district_ar') or "حي غير معرف"
                    neighborhood_leaks[name] = 0

                # الربط المكاني (Spatial Join)
                for _, row in df.iterrows():
                    try:
                        point = Point(row['longitude'], row['latitude'])
                        for feature in features:
                            polygon = shape(feature.get('geometry'))
                            if polygon.contains(point):
                                props = feature.get('properties', {})
                                name = props.get('name') or props.get('district_ar') or "حي غير معرف"
                                neighborhood_leaks[name] += 1
                                break
                    except: continue
        except Exception as e:
            st.warning(f"⚠️ مشكلة في ملف الأحياء: {e}")

    return df, geo_data, neighborhood_leaks

try:
    df, geo_data, leaks_dict = process_spatial_data()

    if df is not None:
        # تجهيز بيانات الشارت
        if leaks_dict:
            stats_df = pd.DataFrame(list(leaks_dict.items()), columns=['الحي', 'عدد التسربات'])
            stats_df = stats_df[stats_df['عدد التسربات'] > 0].sort_values(by='عدد التسربات', ascending=False)
        else:
            # لو الربط المكاني فشل، نعتمد على عمود اسم الحي في الإكسل للشارت فقط
            stats_df = df['area_name'].value_counts().reset_index()
            stats_df.columns = ['الحي', 'عدد التسربات']

        # --- Sidebar ---
        st.sidebar.title("📊 مؤشرات الدمام")
        if not stats_df.empty:
            fig = px.bar(stats_df.head(10), x='عدد التسربات', y='الحي', orientation='h', 
                         color='عدد التسربات', color_continuous_scale='Reds')
            st.sidebar.plotly_chart(fig, use_container_width=True)

        # --- Main Map ---
        st.title("🗺️ خريطة كثافة التسربات")
        m = folium.Map(location=[26.4207, 50.0888], zoom_start=11, tiles="cartodbpositron")

        # رسم الملونات فقط إذا كان الملف سليم
        if geo_data and 'features' in geo_data and len(geo_data['features']) > 0:
            try:
                # البحث عن أول خاصية متاحة للربط
                available_keys = list(geo_data['features'][0].get('properties', {}).keys())
                main_key = "name" if "name" in available_keys else (available_keys[0] if available_keys else None)
                
                if main_key:
                    folium.Choropleth(
                        geo_data=geo_data,
                        data=stats_df,
                        columns=["الحي", "عدد التسربات"],
                        key_on=f"feature.properties.{main_key}",
                        fill_color="YlOrRd",
                        fill_opacity=0.6,
                        legend_name="كثافة البلاغات"
                    ).add_to(m)
            except: pass

        # رسم النقط (دائماً تظهر)
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=4, color='red', fill=True, popup=f"عداد: {row.get('meter_name')}"
            ).add_to(m)

        st_folium(m, width="100%", height=700)
    else:
        st.error("ملف data.csv غير موجود!")

except Exception as e:
    st.error(f"خطأ غير متوقع: {e}")

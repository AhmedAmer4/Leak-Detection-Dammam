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
def load_and_verify():
    if not os.path.exists("data.csv"): return None, None, pd.DataFrame()
    
    # 1. تحميل الإكسل (المصدر الموثوق)
    df = pd.read_csv("data.csv", encoding='utf-8-sig')
    
    # 2. تجهيز إحصائيات الأحياء فوراً من الإكسل لضمان ظهور المؤشر
    if 'area_name' in df.columns:
        stats_df = df['area_name'].value_counts().reset_index()
        stats_df.columns = ['الحي', 'عدد التسربات']
    else:
        stats_df = pd.DataFrame(columns=['الحي', 'عدد التسربات'])

    # 3. محاولة تحميل ملف الأحياء
    geo_data = None
    if os.path.exists("map.json"):
        try:
            with open("map.json", "r", encoding="utf-8") as f:
                geo_data = json.load(f)
        except: pass
        
    return df, geo_data, stats_df

df, geo_data, stats_df = load_and_verify()

# ---Sidebar: المؤشرات (هتظهر غصب عنها المرة دي) ---
st.sidebar.title("📊 مركز تحليل البيانات")

if not stats_df.empty:
    st.sidebar.success("✅ تم استخراج المؤشرات من ملف البيانات")
    st.sidebar.metric("إجمالي بلاغات التسرب", len(df))
    
    # شارت احترافي
    fig = px.bar(stats_df.head(15), x='عدد التسربات', y='الحي', 
                 orientation='h', title="أكثر الأحياء بلاغات",
                 color='عدد التسربات', color_continuous_scale='Reds')
    st.sidebar.plotly_chart(fig, use_container_width=True)
    
    # مؤشر نسبة الحي الأكثر تضرراً
    top_area = stats_df.iloc[0]
    st.sidebar.warning(f"🚨 حي {top_area['الحي']} يحتاج تدخل عاجل")
else:
    st.sidebar.error("❌ لم أجد عمود area_name في الملف")

# --- الخريطة ---
st.title("🗺️ خريطة الرصد الميداني")

if df is not None:
    m = folium.Map(location=[26.4207, 50.0888], zoom_start=11, tiles="cartodbpositron")

    # 1. رسم حدود الأحياء (لو الملف سليم)
    if geo_data:
        folium.GeoJson(
            geo_data,
            style_function=lambda x: {'fillColor': 'blue', 'color': 'black', 'weight': 1, 'fillOpacity': 0.1},
            tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['الحي:']) if 'name' in str(geo_data) else None
        ).add_to(m)

    # 2. رسم نقط التسربات (أهم شيء)
    for _, row in df.iterrows():
        try:
            folium.CircleMarker(
                location=[float(row['latitude']), float(row['longitude'])],
                radius=5, color='red', fill=True, fill_opacity=0.8,
                popup=f"حي: {row.get('area_name')}<br>عداد: {row.get('meter_name')}"
            ).add_to(m)
        except: continue

    st_folium(m, width="100%", height=650)
    st.balloons()

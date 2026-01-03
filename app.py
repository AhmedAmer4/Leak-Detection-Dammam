import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import os

# ---------------------------
# 1. إعداد الصفحة
# ---------------------------
st.set_page_config(
    page_title="🚰 نظام مراقبة تسربات المياه - الدمام",
    layout="wide",
    page_icon="💧"
)

# خلفية بيضا للنصوص
st.markdown(
    """
    <style>
    body {
        background-color: #ffffff;
    }
    .stApp {
        background-color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🚰 نظام مراقبة تسربات المياه - الدمام")
st.write("جاري فحص الملفات وتشغيل النظام...")

# ---------------------------
# 2. فحص الملفات
# ---------------------------
csv_path = "water_leakage_data.csv"
json_path = "dammam.json"

if not os.path.exists(csv_path):
    st.error(f"❌ ملف البيانات {csv_path} غير موجود على GitHub!")
    st.stop()

if not os.path.exists(json_path):
    st.error(f"❌ ملف الخريطة {json_path} غير موجود على GitHub!")
    st.stop()

# ---------------------------
# 3. تحميل البيانات
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(csv_path)
    with open(json_path, "r", encoding="utf-8") as f:
        raw_json = json.load(f)
    
    # تحويل صيغة ArcGIS إلى GeoJSON
    features = []
    for feat in raw_json.get('features', []):
        if 'geometry' in feat and 'rings' in feat['geometry']:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": feat['geometry']['rings']},
                "properties": feat.get('attributes', {})
            })
    return df, {"type": "FeatureCollection", "features": features}

try:
    df, geo_data = load_data()
    st.success("✅ تم الاتصال بقاعدة البيانات بنجاح")

    # ---------------------------
    # 4. عرض المؤشرات (Metrics)
    # ---------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي البلاغات", len(df))
    c2.metric("الحالات المكتشفة اليوم", "3")  # ممكن تربطها بالداتا
    c3.metric("عدد الأحياء المتأثرة", len(geo_data['features']))

    # ---------------------------
    # 5. عرض الخريطة
    # ---------------------------
    st.subheader("التوزيع الجغرافي للبلاغات")
    m = folium.Map(
        location=[26.4207, 50.0888], 
        zoom_start=11,
        tiles="OpenStreetMap"  # <- مهم عشان الخلفية فاتحة وواضحة
    )
    
    # إضافة الأحياء من GeoJSON
    folium.GeoJson(
        geo_data,
        name="الأحياء",
        style_function=lambda x: {
            "fillColor": "#add8e6",  # لون فاتح للأحياء
            "color": "blue",
            "weight": 2,
            "fillOpacity": 0.4
        }
    ).add_to(m)

    # إضافة البلاغات
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.7,
            popup=f"الموقع: {row.get('address', 'غير معروف')}"
        ).add_to(m)

    st_folium(m, width=1100, height=500)

except Exception as e:
    st.error(f"🚨 حدث خطأ أثناء تشغيل البيانات: {e}")



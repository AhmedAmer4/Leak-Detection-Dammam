import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="مراقبة تسربات الدمام", layout="wide")
st.title("🚰 لوحة تحكم تسربات المياه - الدمام")

# تأكد أن الأسماء في GitHub هي data.csv و map.json
CSV_FILE = "data.csv"
JSON_FILE = "map.json"

def load_csv_safely(file_path):
    # محاولة القراءة بأكثر من نوع تشفير لفك عقدة 0xa9
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except (UnicodeDecodeError, Exception):
            continue
    return None

try:
    if os.path.exists(CSV_FILE):
        df = load_csv_safely(CSV_FILE)
        
        if df is not None:
            st.success("✅ تم فك تشفير البيانات بنجاح!")
            st.metric("إجمالي البلاغات", len(df))

            # إنشاء الخريطة
            m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)

            # محاولة قراءة الخريطة بتشفير مرن أيضاً
            if os.path.exists(JSON_FILE):
                try:
                    with open(JSON_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                        geo_data = json.load(f)
                    folium.GeoJson(geo_data, name="الأحياء").add_to(m)
                except:
                    st.warning("⚠️ ملف الخريطة به مشكلة في التشفير، سيتم عرض النقاط فقط.")

            # إضافة النقاط
            for _, row in df.iterrows():
                if pd.notnull(row.get('latitude')) and pd.notnull(row.get('longitude')):
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=5, color='red', fill=True,
                        popup=f"عداد: {row.get('meter_name', 'مجهول')}"
                    ).add_to(m)

            st_folium(m, width=1200, height=500)
            st.balloons()
        else:
            st.error("❌ فشل الكود في قراءة ملف CSV حتى مع محاولات تغيير التشفير.")
    else:
        st.error(f"❌ ملف {CSV_FILE} غير موجود. تأكد من رفعه بأسماء إنجليزية.")

except Exception as e:
    st.error(f"🚨 خطأ فني غير متوقع: {e}")



import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="مراقبة تسربات الدمام", layout="wide")
st.title("🚰 لوحة تحكم تسربات المياه - الدمام")

# أسماء الملفات (تأكد أنها مطابقة لـ GitHub)
CSV_FILE = "data.csv"
JSON_FILE = "map.json"

try:
    # 1. محاولة قراءة ملف الإكسل بتشفير مرن لتجنب خطأ utf-8
    if os.path.exists(CSV_FILE):
        try:
            # نحاول أولاً بالتنسيق العادي
            df = pd.read_csv(CSV_FILE, encoding='utf-8')
        except UnicodeDecodeError:
            # لو فشل، نجرب التنسيق اللي بيقبل الرموز الغريبة (مثل 0xa9)
            df = pd.read_csv(CSV_FILE, encoding='ISO-8859-1')
        
        st.success("✅ تم تحميل البيانات بنجاح")
        st.metric("إجمالي البلاغات", len(df))

        # 2. إنشاء الخريطة
        m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)

        # 3. محاولة قراءة ملف الخريطة بتشفير مرن
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    geo_data = json.load(f)
                folium.GeoJson(geo_data, name="الأحياء").add_to(m)
            except Exception as json_err:
                st.warning(f"⚠️ مشكلة في ملف الخريطة، سيتم عرض النقاط فقط. الخطأ: {json_err}")

        # 4. إضافة نقاط التسربات
        for _, row in df.iterrows():
            # التأكد من وجود أعمدة الإحداثيات
            lat = row.get('latitude')
            lon = row.get('longitude')
            if pd.notnull(lat) and pd.notnull(lon):
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5, color='red', fill=True,
                    popup=f"عداد: {row.get('meter_name', 'مجهول')}"
                ).add_to(m)

        st_folium(m, width=1200, height=500)
        st.balloons()
    else:
        st.error(f"❌ لم يتم العثور على ملف {CSV_FILE}. يرجى رفعه بأسماء إنجليزية.")

except Exception as e:
    st.error(f"🚨 خطأ فني غير متوقع: {e}")



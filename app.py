import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# إعدادات الصفحة
st.set_page_config(page_title="اختبار الاتصال", layout="wide")

st.title("🚀 مرحلة كسر الشاشة السمرا")

# اختبار بسيط جداً
st.write("لو شايف الكلام ده، يبقى المشكلة كانت في ملفات البيانات (الأسماء أو التنسيق).")

try:
    # صنع بيانات وهمية للتجربة فقط
    test_data = pd.DataFrame({
        'lat': [26.4207],
        'lon': [50.0888],
        'name': ['نقطة اختبار الدمام']
    })
    
    st.success("✅ المكتبات (Pandas & Folium) شغالة تمام!")
    
    # خريطة تجريبية
    m = folium.Map(location=[26.4207, 50.0888], zoom_start=12)
    folium.Marker([26.4207, 50.0888], popup="الدمام").add_to(m)
    
    st_folium(m, width=700, height=400)
    
    st.balloons()

except Exception as e:
    st.error(f"فيه مشكلة في المكتبات: {e}")

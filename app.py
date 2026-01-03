import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="داشبورد تسربات الدمام", layout="wide")
st.title("🚰 نظام مراقبة تسربات المياه - الدمام")

# اسم الملف اللي حفظناه
CSV_FILE = "data.csv"

if os.path.exists(CSV_FILE):
    try:
        # قراءة الملف الجديد (التنسيق ده بيدعم العربي 100%)
        df = pd.read_csv(CSV_FILE, encoding='utf-8')
        
        st.success("✅ تم رفع وقراءة البيانات بنجاح!")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("عدد البلاغات", len(df))
            st.dataframe(df.head(10))
            
        with col2:
            st.subheader("خريطة المواقع")
            m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)
            
            for _, row in df.iterrows():
                # تأكد أن أسماء الأعمدة مطابقة لملف الإكسل الجديد
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5, color='red', fill=True,
                    popup=f"بلاغ: {row.get('meter_name', 'موقع تسرب')}"
                ).add_to(m)
            
            st_folium(m, width=700, height=500)
            st.balloons()
            
    except Exception as e:
        st.error(f"🚨 خطأ في قراءة الملف: {e}")
else:
    st.error(f"❌ ملف {CSV_FILE} غير موجود على GitHub")


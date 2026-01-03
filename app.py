import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="داشبورد الدمام", layout="wide")
st.title("🚰 نظام مراقبة تسربات المياه - الدمام")

CSV_FILE = "data.csv"

# دالة سحرية لتنظيف الملف من أي حروف "خبيثة" قبل القراءة
def clean_and_load(file_path):
    try:
        # 1. قراءة الملف كمجموعة بايتات خام
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        # 2. تحويل البايتات لنص مع تجاهل أي حرف يسبب خطأ (errors='ignore')
        # دي الخطوة اللي هتمسح الـ 0xa9 وأي حرف تاني عامل أزمة
        decoded_text = raw_data.decode('utf-8', errors='ignore')
        
        # 3. تحويل النص لجدول بيانات
        import io
        return pd.read_csv(io.StringIO(decoded_text))
    except Exception as e:
        st.error(f"فشل التنظيف البرمجي: {e}")
        return None

if os.path.exists(CSV_FILE):
    df = clean_and_load(CSV_FILE)
    
    if df is not None:
        st.success("✅ تم تنظيف البيانات وفتح الملف بنجاح!")
        
        # عرض البيانات الأساسية
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("عدد البلاغات", len(df))
            st.write("عينة من البيانات:")
            st.dataframe(df.head(5))
            
        with col2:
            st.subheader("خريطة المواقع")
            # إحداثيات الدمام
            m = folium.Map(location=[26.4207, 50.0888], zoom_start=11)
            
            for _, row in df.iterrows():
                try:
                    # التأكد من أن الإحداثيات أرقام وليست نصوص
                    lat = float(row['latitude'])
                    lon = float(row['longitude'])
                    
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=5, color='red', fill=True,
                        popup=f"بلاغ: {row.get('meter_name', 'موقع تسرب')}"
                    ).add_to(m)
                except:
                    continue # لو سطر فيه إحداثيات غلط يعديه ويكمل
                    
            st_folium(m, width=700, height=500)
            st.balloons()
    else:
        st.error("🚨 حتى بعد التنظيف، الملف لا يزال غير قابل للقراءة.")
else:
    st.error(f"❌ ملف {CSV_FILE} غير موجود على GitHub")

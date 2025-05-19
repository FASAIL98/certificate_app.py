import streamlit as st
st.set_page_config(page_title="نظام إصدار الشهادات", layout="centered")

# 🔐 حماية بكلمة مرور
AUTHORIZED_USER = "admin"
AUTHORIZED_PASS = "1234"

st.sidebar.title("تسجيل الدخول 🔐")
username = st.sidebar.text_input("اسم المستخدم")
password = st.sidebar.text_input("كلمة المرور", type="password")

if username != AUTHORIZED_USER or password != AUTHORIZED_PASS:
    st.warning("⚠️ يرجى إدخال بيانات صحيحة للوصول للأداة.")
    st.stop()

# --- الكود الرئيسي ---
import pandas as pd
import yagmail
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
import os
from reportlab.lib import colors

st.title("📜 نظام إصدار الشهادات التلقائي - النسخة المحسنة")

uploaded_excel = st.file_uploader("📥 اختر ملف Excel (يحتوي على الاسم والإيميل):", type=["xlsx"])
uploaded_pdf = st.file_uploader("📄 اختر قالب الشهادة (PDF):", type=["pdf"])

sender_email = st.text_input("✉️ بريد المرسل (Gmail)")
app_password = st.text_input("🔑 كلمة مرور التطبيقات", type="password")

custom_message = st.text_area("📝 نص الرسالة المرفقة مع الشهادة", "السلام عليكم،\nمرفق لك شهادة حضورك للدورة الإلكترونية.\nمع خالص التحية.")

font_size = st.slider("🔠 حجم الخط", 20, 40, 28)
font_color = st.color_picker("🎨 اختر لون النص", "#003366")
x_position = st.slider("↔️ موضع الاسم (عرض)", 100, 550, 300)
y_position = st.slider("↕️ موضع الاسم (ارتفاع)", 100, 700, 450)

if st.button("🚀 إصدار الشهادات"):
    if not uploaded_excel or not uploaded_pdf:
        st.error("❌ يرجى تحميل ملف Excel وقالب الشهادة.")
    elif not os.path.exists("Amiri-Regular.ttf"):
        st.error("❌ لم يتم العثور على ملف الخط 'Amiri-Regular.ttf' داخل المشروع.")
    else:
        try:
            excel_path = "data.xlsx"
            template_path = "template.pdf"
            font_path = "Amiri-Regular.ttf"

            with open(excel_path, "wb") as f:
                f.write(uploaded_excel.read())
            with open(template_path, "wb") as f:
                f.write(uploaded_pdf.read())

            pdfmetrics.registerFont(TTFont('CustomArabicFont', font_path))
            df = pd.read_excel(excel_path)
            yag = yagmail.SMTP(user=sender_email, password=app_password)

            for index, row in df.iterrows():
                name = str(row['الاسم']).strip()
                email = str(row['الإيميل']).strip()

                reshaped_text = arabic_reshaper.reshape(name)
                bidi_text = get_display(reshaped_text)

                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.setFont("CustomArabicFont", font_size)
                can.setFillColor(colors.HexColor(font_color))
                can.drawCentredString(x_position, y_position, bidi_text)
                can.save()

                packet.seek(0)
                new_pdf = PdfReader(packet)
                existing_pdf = PdfReader(open(template_path, "rb"))
                output = PdfWriter()
                page = existing_pdf.pages[0]
                page.merge_page(new_pdf.pages[0])
                output.add_page(page)

                output_filename = f"شهادة - {name}.pdf"
                with open(output_filename, "wb") as outputStream:
                    output.write(outputStream)

                yag.send(
                    to=email,
                    subject="🎓 شهادتك بعد الدورة",
                    contents=custom_message,
                    attachments=output_filename
                )

            st.success("✅ تم إرسال جميع الشهادات بنجاح!")
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء التنفيذ: {str(e)}")

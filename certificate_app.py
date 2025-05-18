# 🔐 حماية بكلمة مرور
AUTHORIZED_USER = "admin"
AUTHORIZED_PASS = "1234"  # ← غيرها لكلمة سر خاصة بك

st.sidebar.title("تسجيل الدخول 🔐")
username = st.sidebar.text_input("اسم المستخدم")
password = st.sidebar.text_input("كلمة المرور", type="password")

if username != AUTHORIZED_USER or password != AUTHORIZED_PASS:
    st.warning("⚠️ يرجى إدخال بيانات صحيحة للوصول للأداة.")
    st.stop()# certificate_app.py
import streamlit as st
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

st.set_page_config(page_title="نظام إصدار الشهادات", layout="centered")
st.title("📜 نظام إصدار الشهادات التلقائي")

# تحميل الملفات
uploaded_excel = st.file_uploader("📥 اختر ملف Excel (يحتوي على الاسم والإيميل):", type=["xlsx"])
uploaded_pdf = st.file_uploader("📄 اختر قالب الشهادة (PDF):", type=["pdf"])
uploaded_font = st.file_uploader("🔤 اختر ملف الخط العربي (مثل Cairo-Regular.ttf):", type=["ttf"])

sender_email = st.text_input("fasg6443f@gmail.com")
app_password = st.text_input("eetgmhjlvfiylklw")

font_size = st.slider("🔠 حجم الخط", 20, 40, 28)
font_color = st.color_picker("🎨 اختر لون النص", "#003366")

x_position = st.slider("↔️ موضع الاسم (عرض)", 100, 550, 500)
y_position = st.slider("↕️ موضع الاسم (ارتفاع)", 100, 700, 470)

if st.button("🚀 إصدار الشهادات"):
    if not uploaded_excel or not uploaded_pdf or not uploaded_font:
        st.error("يرجى تحميل جميع الملفات المطلوبة.")
    else:
        try:
            # حفظ الملفات المؤقتة
            excel_path = "data.xlsx"
            template_path = "template.pdf"
            font_path = "arabic_font.ttf"

            with open(excel_path, "wb") as f:
                f.write(uploaded_excel.read())
            with open(template_path, "wb") as f:
                f.write(uploaded_pdf.read())
            with open(font_path, "wb") as f:
                f.write(uploaded_font.read())

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
                can.drawRightString(x_position, y_position, bidi_text)
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
                    contents=f"السلام عليكم {name}\n\nمرفق لك شهادة حضورك للدورة.\nمع التحية.",
                    attachments=output_filename
                )

            st.success("✅ تم إرسال جميع الشهادات بنجاح!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء التنفيذ: {str(e)}")

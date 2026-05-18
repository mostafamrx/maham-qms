import streamlit as st
import requests
import datetime
import pandas as pd
import base64
import json


# 1. إعدادات الصفحة الأساسية (هوية MAHAM)
st.set_page_config(
    page_title="MAHAM QMS",
    page_icon="📋",
    layout="centered"
)
# --- كود إجبار السيرفر على بدء جلسة نظيفة عند أول تحميل أو Refresh حقيقي ---
IMGBB_API_KEY = "0813b58c605aee769f5f8852ca06fb18"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxCe7SSWSPbcbrAR7u-HIKscwtP5v3a7XbBq7ZOaBjDSg-f-OerPJlb9h47npAW8K2K0g/exec"
# --- كود CSS المطور والمتوافق مع شاشات الموبايل (RTL Mobile Friendly) ---
st.markdown(
    """
    <style>
    /* 1. تطبيق RTL على المحتوى الداخلي فقط بدلاً من التطبيق بالكامل لحماية واجهة الموبايل */
    [data-testid="block-container"] {
        direction: rtl;
    }
    
    /* 2. ضبط القائمة الجانبية */
    [data-testid="stSidebar"] {
        direction: rtl;
    }

    /* 3. محاذاة جميع النصوص لليمين */
    p, div, input, label, h1, h2, h3, h4, h5, h6 {
        text-align: right !important;
    }

    /* 4. استثناء الأزرار لتبقى نصوصها في المنتصف ولا يتشوه شكلها */
    button p {
        text-align: center !important;
    }

    /* 5. ضبط الجداول وتقرأ من اليمين لليسار */
    table {
        direction: rtl;
    }
    th, td {
        text-align: right !important;
    }
    
    /* 6. تحسين شكل القوائم المنسدلة */
    .stSelectbox div[data-baseweb="select"] > div {
        direction: rtl;
    }

    /* 7. السطر السحري: إبقاء زر القائمة (الهامبرغر) للموبايل ليعمل بشكل سليم */
    [data-testid="collapsedControl"] {
    
        direction: ltr !important; 
    }
    </style>
    """,
    unsafe_allow_html=True
)
# --- القائمة الجانبية (Sidebar) للتنقل وإدخال البيانات ---
st.sidebar.title("🏢 MAHAM QMS")
st.sidebar.markdown("---")

# اختيار نوع التقرير
page = st.sidebar.radio("📌 اختر نوع النموذج:", ["تقرير الفتح اليومي", "التدقيق الداخلي (Internal Audit)"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 بيانات التقييم الثابتة")

# البيانات الأساسية (نقلناها هنا لتكون متاحة للتقريرين)
branch_name = st.sidebar.selectbox("اختر الفرع", ["كرينكل المحافظ", "كرينكل دله", "كرينكل أكتوبر","كيكن باغوص","كرينكل طلعت حرب","كرينكل شيراتون","كرينكل مول العرب","كرينكل التجمع الأول","كرينكل التجمع الخامس"])
inspector_name = st.sidebar.text_input("اسم مسؤول الجودة")

# الحقول الجديدة
branch_manager = st.sidebar.text_input("اسم مدير الفرع")
shift_manager = st.sidebar.text_input("اسم مدير الوردية")

date = st.sidebar.date_input("تاريخ التقييم", datetime.date.today())
time = st.sidebar.time_input("وقت التقييم", datetime.datetime.now().time())

# ==========================================
# الصفحة الأولى: تقرير الفتح اليومي
# ==========================================
if page == "تقرير الفتح اليومي":
    st.title("📋 تقرير الفتح وتقييم الجودة")
    st.markdown("---")
    evaluation_schema = {
        "المنطقة الخارجية": {
            "weight": 0.10,
            "items": [
                {"id": "ext_1", "text": "اليافطة نظيفة وبحالة جيدة", "target": 10},
                {"id": "ext_2", "text": "زجاج الواجهة نظيف وبحالة جيدة", "target": 15},
                {"id": "ext_3", "text": "منطقة الكاونتر نظيفة ومرتبة", "target": 15},
                {"id": "ext_4", "text": "المنيوبورد نظيف وبحالة جيدة", "target": 10},
            ]
        },
        "المنطقة الداخلية": {
            "weight": 0.15,
            "items": [
                {"id": "int_1", "text": "المنطقة الداخلية نظيفة", "target": 10},
                {"id": "int_2", "text": "المعدات نظيفة", "target": 20},
                {"id": "int_3", "text": "الهود نظيف", "target": 10},
                {"id": "int_4", "text": "محابس الغاز مغلقة", "target": 20},
                {"id": "int_5", "text": "المنطقة الخلفية نظيفة", "target": 10},
                {"id": "int_6", "text": "وحدات التبريد نظيفة وبحالة جيدة", "target": 20},
                {"id": "int_7", "text": "وحدات التجميد نظيفة وبحالة جيدة", "target": 15},
            ]
        },
        "استلام وتخزين المنتجات": {
            "weight": 0.15,
            "items": [
                {"id": "store_1", "text": "استلام المنتجات وتخزينها تتم بصورة صحيحة", "target": 15},
                {"id": "store_2", "text": "يتم تطبيق قاعدة الـ F.I.F.O", "target": 20},
                {"id": "store_3", "text": "إجراءات الإسالة تتم بصورة صحيحة", "target": 15},
            ]
        },
        "إداريات": {
            "weight": 0.10,
            "items": [
                {"id": "admin_1", "text": "تواجد إداري خلال فتح المطعم", "target": 10},
                {"id": "admin_2", "text": "فتح المطعم في المواعيد الرسمية", "target": 10},
                {"id": "admin_3", "text": "عدد العاملين يتناسب مع حجم التشغيل", "target": 10},
                {"id": "admin_4", "text": "مظهر العاملين (اليونيفورم - النظافة الشخصية)", "target": 20},
                {"id": "admin_5", "text": "تم غلق نقاط البيع", "target": 20},
                {"id": "admin_6", "text": "ترشيد استهلاك الطاقة أثناء تجهيز المطعم", "target": 15},
            ]
        },
        "جودة المنتجات": {
            "weight": 0.25,
            "items": [
                {"id": "prod_1", "text": "إجراءات تحضير المنتجات تتم بصورة صحيحة", "target": 15},
                {"id": "prod_2", "text": "إجراءات تحضير الفراير (الشورتننج - البريدنج) تتم بصورة صحيحة", "target": 10},
                {"id": "prod_3", "text": "وحدات التبريد والتسخين درجة حرارتها مطابقة قبل الاستخدام", "target": 10},
                {"id": "prod_4", "text": "عدم وجود سلطة أو صوصات معبئة من أمس", "target": 20},
                {"id": "prod_5", "text": "عدم التلاعب في صلاحية المنتجات", "target": 20},
                {"id": "prod_6", "text": "المنتجات تحت الإسالة مطابقة لمعدلات التشغيل", "target": 20},
                {"id": "prod_7", "text": "عدم وجود منتجات تم عمل إجراءات تشغيلية عليها يفقدها جودتها", "target": 10},
                {"id": "prod_8", "text": "عدم وجود منتجات مطهية من أمس", "target": 20},
                {"id": "prod_9", "text": "الانتهاء من طهي المنتجات مع فتح المطعم للعملاء - الكميات قليلة - طهي البطاطس بالطلب", "target": 20},
            ]
        },
        "أمن وصحة وسلامة الغذاء": {
            "weight": 0.25,
            "items": [
                {"id": "safe_1", "text": "عملية التطهير تتم بصورة صحيحة", "target": 20},
                {"id": "safe_2", "text": "درجة حرارة المنتجات مطابقة للمواصفات القياسية", "target": 15},
                {"id": "safe_3", "text": "درجة حرارة وحدات التبريد والتجميد مطابقة للمواصفات", "target": 10},
                {"id": "safe_4", "text": "الشورتننج مطابق للمواصفات", "target": 10},
                {"id": "safe_5", "text": "الدقيق منخول ولا يوجد به شوائب", "target": 15},
                {"id": "safe_6", "text": "كل أدوات التشغيل نظيفة - ويتم تخزينها بالشكل الصحيح", "target": 15},
                {"id": "safe_7", "text": "عدم وجود منتج تالف أو منتهي الصلاحية", "target": 50},
                {"id": "safe_8", "text": "جميع مخارج ومداخل المطعم محكمة الغلق", "target": 20},
                {"id": "safe_9", "text": "فرصة حدوث تلوث", "target": 50},
            ]
        }
    }
    # 4. بناء واجهة التقييم الديناميكية
    results_data = {}
    opening_images_data = {}
    notes_data = {}
    summary_data = [] # قائمة لحفظ بيانات الجدول النهائي
    total_final_score = 0

    st.markdown("### 📝 تفاصيل التقييم")

    for section_name, section_data in evaluation_schema.items():
        # استخدام Expander لترتيب الشكل
        with st.expander(f"📌 {section_name} (الهدف: {int(section_data['weight']*100)}%)", expanded=False):
            section_score = 0
            section_max = sum(item["target"] for item in section_data["items"])
            
            for item in section_data["items"]:
                col_score, col_text = st.columns([1, 3])
                with col_text:
                    st.write(f"**{item['text']}** (الهدف: {item['target']})")
                with col_score:
                    # إدخال الدرجة المحققة
                    achieved = st.number_input(
                        "المحقق", 
                        min_value=0, 
                        max_value=item['target'], 
                        value=item['target'], 
                        key=f"score_{item['id']}",
                        label_visibility="collapsed"
                    )
                    results_data[item['text']] = achieved
                    section_score += achieved
            
            notes_data[section_name] = st.text_input("ملاحظات القسم", key=f"note_{section_name}")
            
            # 📸 --- الإضافة الجديدة: مكان رفع الصور لتقرير الفتح ---
            uploaded_files = st.file_uploader(f"📸 إرفاق صور إثبات (اختياري)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key=f"open_img_{section_name}")
            
            section_images_base64 = []
            if uploaded_files:
                for file in uploaded_files:
                    bytes_data = file.getvalue()
                    base64_encoded = base64.b64encode(bytes_data).decode('utf-8')
                    section_images_base64.append({
                        "filename": file.name,
                        "mime_type": file.type,
                        "data": base64_encoded
                    })
            
            # حفظ صور هذا القسم
            opening_images_data[section_name] = section_images_base64
            # ------------------------------------------------
            
            # الحسابات الخاصة بالقسم
            weight_percentage = section_data['weight'] * 100
            section_percentage = (section_score / section_max) * weight_percentage
            total_final_score += section_percentage
            
            # حفظ البيانات لجدول التجميع النهائي
            summary_data.append({
                "المنطقة": section_name,
                "الهدف": f"{int(weight_percentage)}%",
                "المحقق (نقاط)": f"{section_score} / {section_max}",
                "النسبة المئوية": f"{section_percentage:.2f}%"
            })

    # 5. رسم جدول تجميع النتيجة النهائية
    st.markdown("---")
    st.markdown("### 📊 جدول تجميع النتيجة النهائية")

    # تحويل البيانات إلى جدول باستخدام Pandas
    df_summary = pd.DataFrame(summary_data)
    df_summary.index += 1 # لبدء الترقيم (م) من 1 بدلاً من 0

    # عرض الجدول بشكل احترافي
    st.table(df_summary)

    # عرض الإجمالي بشكل بارز
    st.success(f"### 🎯 الإجمالي النهائي للمطعم: {total_final_score:.2f}%")

    st.markdown("---")

# 6. زر الإرسال المباشر لـ Google Sheets
    if st.button("🚀 اعتماد وإرسال التقرير", use_container_width=True):
        if not inspector_name:
            st.error("⚠️ برجاء إدخال اسم مسؤول الجودة أعلى الصفحة!")
        else:
            try:
                with st.spinner("جاري معالجة البيانات ورفع الصور... ⏳"):
                    
                    # --- 1. معالجة الصور ورفعها لـ ImgBB ---
                    image_links = []
                    url_imgbb = "https://api.imgbb.com/1/upload"
                    
                    for section, images in opening_images_data.items():
                        for img in images:
                            payload_imgbb = {
                                "key": IMGBB_API_KEY,
                                "image": img["data"]  # نرسل كود الـ base64 الجاهز
                            }
                            res = requests.post(url_imgbb, data=payload_imgbb)
                            
                            if res.status_code == 200:
                                link = res.json()['data']['url']
                                image_links.append(f"[{section}]: {link}")
                            else:
                                image_links.append(f"[{section}]: خطأ في رفع الصورة")
                    
                    images_str = "\n".join(image_links) if image_links else "لا يوجد صور"

                    # --- 2. تنظيف وترتيب الملاحظات ---
                    clean_notes = []
                    for section, note in notes_data.items():
                        if note.strip():
                            clean_notes.append(f"[{section}]: {note}")
                    
                    notes_str = "\n".join(clean_notes) if clean_notes else "لا يوجد ملاحظات"

                    # --- 3. تجميع البيانات النهائية للشيت ---
                    payload = {
                        "timestamp": str(datetime.datetime.now()),
                        "date": str(date),
                        "time": str(time),
                        "branch_name": branch_name,
                        "branch_manager": branch_manager,
                        "shift_manager": shift_manager,
                        "inspector_name": inspector_name,
                        "final_score_percentage": round(total_final_score, 2),
                        "detailed_scores": results_data, 
                        "summary_table": summary_data,   
                        "notes": notes_str,              # الملاحظات المنظفة
                        "uploaded_evidence_images": images_str # الروابط الحقيقية للصور
                    }
                    
                    # --- 4. إرسال البيانات لجوجل شيت ---
                    response = requests.post(GOOGLE_SCRIPT_URL, json=payload)
                    
                    if response.status_code == 200 and "TRUE_SUCCESS" in response.text:
                        st.balloons() 
                        st.success("✅ تم حفظ التقييم بنجاح وإرساله مباشرة إلى قاعدة البيانات!")
                    else:
                        st.warning(f"⚠️ حدث خطأ أثناء حفظ البيانات في الشيت: {response.text}")
                        
            except Exception as e:
                st.error(f"❌ حدث خطأ في الاتصال: {e}")
elif page == "التدقيق الداخلي (Internal Audit)":
    st.title("🔍 التدقيق الداخلي (Internal Audit)")
    st.markdown("---")
    
    # 1. هيكل بيانات التدقيق الداخلي (بناءً على صورك)
    # خيارات الـ options تعكس الخلايا البيضاء فقط المتاحة لكل معيار
    audit_schema = {
        "المنطقة الخارجية": {
            "max_score": 120,
            "weight": 0.05,
            "items": [
                {"id": "ext_1", "text": "الرصيف وموقف السيارات نظيف وبحالة جيدة", "target": 10, "options": ["مطابق (10)", "Minor", "ملاحظة فقط"]},
                {"id": "ext_2", "text": "واجهة المطعم نظيف ومصانة وبحالة جيدة", "target": 30, "options": ["مطابق (30)", "Minor", "Major", "Critical"]},
                {"id": "ext_3", "text": "منطقة المزروعات الخارجية نظيفة ومرتبة", "target": 10, "options": ["مطابق (10)", "Minor", "Critical"]},
                {"id": "ext_4", "text": "زجاج الواجهة نظيف وبحالة جيدة", "target": 30, "options": ["مطابق (30)", "Minor", "Major", "Critical"]},
                {"id": "ext_5", "text": "باب المطعم نظيف وبحالة جيدة", "target": 30, "options": ["مطابق (30)", "Minor", "Major", "Critical"]},
                {"id": "ext_6", "text": "مواد الدعاية الخارجية نظيفة ومتوافقة مع العروض", "target": 10, "options": ["مطابق (10)", "Minor", "Major"]},
            ]
        },
    # 1. هيكل بيانات التدقيق الداخلي المحدث (بناءً على الصور الجديدة)
        "منطقة خدمة العملاء": {
            "max_score": 220,
            "weight": 0.10,
            "items": [
                {"id": "csc_1", "text": "أرصفة وحوائط منطقة خدمة العملاء نظيفة ومصانة وبحالة جيدة", "target": 10, "options": ["مطابق", "Minor", "ملاحظة فقط"]},
                {"id": "csc_2", "text": "السقف ووحدات الإضاءة وكشافات الطوارئ نظيفة وتعمل وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                {"id": "csc_3", "text": "ستائر الهواء.. نظيفة وتعمل ومصانة.. مظهر المنطقة نظيفة ومرتبة", "target": 10, "options": ["مطابق", "Minor", "Major"]},
                {"id": "csc_4", "text": "كاونتر الخدمة نظيف ومرتب وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                {"id": "csc_5", "text": "المنيو بورد نظيف وبحالة جيدة - الأسعار واضحة ومتطابقة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                {"id": "csc_6", "text": "وحدات التكييف نظيفة وبحالة جيدة - درجة حرارة الصالة من 21:25 مئوي", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical"]},
                {"id": "csc_7", "text": "التليفزيونات نظيفة وتعمل وبحالة جيدة وعرض القنوات المصرح بها", "target": 10, "options": ["مطابق", "Minor", "Major"]},
                {"id": "csc_8", "text": "طاولات وكراسي الصالة نظيفة ومصانة وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                {"id": "csc_9", "text": "حمامات العملاء نظيفة ومصانة وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                {"id": "csc_10", "text": "كل مستلزمات حمامات العملاء متوفرة وموجودة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
            ]
        },
        "الضيافة وخدمة العملاء": {
                "max_score": 330,
                "weight": 0.10,
                "items": [
                    {"id": "hosp_1", "text": "مظهر فريق العمل مطابق للمواصفات المحددة من قبل الإدارة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_2", "text": "أداء فريق العمل و فريق الإدارة يتسم بالودية و سرعة الاستجابة لطلبات العملاء - عدد ماكينات الكاش المتاحة متناسب مع حجم العملاء - عدد القائمين بالخدمة يتناسب مع أعداد العملاء", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_3", "text": "الكاشير / متلقي الطلبات يتبع خطوات الخدمة الصحيحة و يقوم باقتراح المبيعات ( كومبو - حجم كبير - أصناف جانبية )", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_4", "text": "المضيفة يتبع خطوات الخدمة والضيافة الصحيحة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_5", "text": "تجهيز طلبات العملاء تتم بطريقة صحيحة ( مظهر الأطباق - تنظيم المنتجات في صينية التقديم - تنظيم المنتجات داخل الشنطة )", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_6", "text": "الاهتمام بالأطفال ( تقديم بالونات - أعلام ........ الخ - عرض وجبات الأطفال في حالة وجودهم )", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_7", "text": "كل منتجات المنيو و العروض الخاصة متوافرة ومتاحة للبيع", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_8", "text": "تتم مراجعة الطلب مع العميل بصورة جيدة", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_9", "text": "وقت خدمة الطلبات لا يتعدى 10 دقائق", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_10", "text": "متوسط وقت تجهيز طلبات الدليفري 20 دقائق", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_11", "text": "صندوق خدمة التوصيل مرتب و غير مكدس و لا يوجد به غير مكونات الاوردرات - يتم فصل البارد عن الساخن في صندوق خدمة التوصيل", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_12", "text": "طلبات التوصيل تراجع بواسطة الديسبتشر و مندوب التوصيل قبل خروجها 3 طلبات الحد الاقصي مع أي مندوب توصيل طلبات", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                    {"id": "hosp_13", "text": "شنط التوصيل مصانة وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical"]},
                ]
            },
        "أمن وصحة وسلامة الغذاء": {
                "max_score": 260,
                "weight": 0.15,
                "items": [
                    {"id": "safe_1", "text": "يتم اتباع خطوات غسيل وتطهير الأيدي من الموظفين بصورة دورية وعند الحاجة لذلك", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "safe_2", "text": "حوض غسيل وتطهير الأيدي متوافر بالمطعم ولا يفتح باليد وبجانبه كل مستلزمات غسيل وتطهير الأيدي", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "safe_3", "text": "درجات حرارة غرف وحدات التبريد والتجميد مطابقة للمواصفات", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "safe_4", "text": "درجات حرارة المنتجات مطابقة لنظام درجات الحرارة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "safe_5", "text": "كل مواد النظافة والتطهير المتوافرة مصرح بها ويتم تخزينها في أماكن خاصة بها ويتم استعمالها وفقاً لنسب التخفيف المصرح بها", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "safe_6", "text": "يوجد نظام لمقاومة الحشرات والقوارض ويتم متابعته من الشركة المسئولة عن المقاومة", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "safe_7", "text": "أدوات التشغيل - أواني الحفظ - صواني الخدمة - من خامات معتمدة وتغسل وتطهر وتحفظ نظيفة وفي حالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "safe_8", "text": "جودة الشورتننج مطابقة للمواصفات", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "safe_9", "text": "المواد الغذائية مصرح باستخدامها - ومواد اللف والحزم مطابقة للمواصفات ومصرح باستخدامها", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "safe_10", "text": "فرصة حدوث تلوث", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                ]
            },
        "استلام وتخزين وتحضير المنتجات": {
                "max_score": 270,
                "weight": 0.17,
                "items": [
                    {"id": "prep_1", "text": "استلام وتخزين المنتجات المبردة والمجمدة والجافة يتم طبقا للاجراءات المتبعة في دليل التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "prep_2", "text": "استلام وتخزين الخضروات يتم طبقا للاجراءات المتبعة في دليل التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "prep_3", "text": "استلام وتخزين وتشغيل الخبز يتم طبقا للاجراءات المتبعة في دليل التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "prep_4", "text": "اجراءات اسالة المنتجات المجمدة تتم بصورة صحيحة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "prep_5", "text": "الخضروات المجهزة مطابقة للمواصفات طبقاً للمواصفات المحددة في دليل التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "prep_6", "text": "كل المنتجات منظمة ومستخدمة وفقا لقاعدة الـ F.I.F.O. (ما تم استلامه اولا يستخدم اولا)", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "prep_7", "text": "المنتجات التي تم تحضيرها بالمطعم مسجل عليها تاريخ وساعة الإنتاج وانتهاء الصلاحية", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "prep_8", "text": "المنتجات التي يتم تحضيرها تتم وفقا لمعدلات التشغيل الخاصة بكل مطعم", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                    {"id": "prep_9", "text": "المنتجات الغذائية غير تالفة أو منتهية الصلاحية", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                ]
            },
        "جودة المنتجات النهائية (شاملة العينات)": {
            "max_score": 620,
            "weight": 0.18,
            "items": [
                # ---- المعايير العامة للطهي والتجهيز ----
                {"id": "fin_1", "text": "المنتجات المطهية مطابقة للمواصفات", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_2", "text": "اجراءات طهي منتجات الجريل تتم طبقا للاجراءات المتبعة في دليل التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_3", "text": "اجراءات طهي منتجات القلايات تتم طبقا للاجراءات المتبعة في دليل التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_4", "text": "اجراءات محطة التجهيزات تتم طبقا للاجراءات المتبعة في دليل التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_5", "text": "اجراءات محطة التنبورة تتم طبقا للاجراءات المتبعة في دليل التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_6", "text": "السلطات يتم تجهيزها وحفظها طبقا للاجراءات المتبعة في دليل التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_7", "text": "المنتجات الأخرى يتم تجهيزها وحفظها وطهيها طبقا للاجراءات المتبعة في دليل التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                
                # ---- تقييم جودة البطاطس - المقبلات ----
                {"id": "fin_8", "text": "[البطاطس والمقبلات] الوزن", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_9", "text": "[البطاطس والمقبلات] درجة الحرارة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_10", "text": "[البطاطس والمقبلات] الطعم والملح", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_11", "text": "[البطاطس والمقبلات] اللون والتسوية", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                
                # ---- تقييم جودة الساندويتش ----
                {"id": "fin_12", "text": "[الساندويتش] الوزن", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_13", "text": "[الساندويتش] درجة حرارة المنتج", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_14", "text": "[الساندويتش] جودة الخبز مطابقة لاجراءات التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_15", "text": "[الساندويتش] كمية وتوزيع الدريسينج في الخبز", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_16", "text": "[الساندويتش] بناء الساندويتش مطابق لإجراءات التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                
                # ---- تقييم جودة المنتجات النهائية (عينة 1) ----
                {"id": "fin_17", "text": "[عينة منتج نهائي 1] الوزن", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_18", "text": "[عينة منتج نهائي 1] درجة حرارة المنتج", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_19", "text": "[عينة منتج نهائي 1] جودة المنتج والخبز مطابقة لاجراءات التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_20", "text": "[عينة منتج نهائي 1] الشكل النهائي للمنتج", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                
                # ---- تقييم جودة المنتجات النهائية (عينة 2) ----
                {"id": "fin_21", "text": "[عينة منتج نهائي 2] الوزن", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_22", "text": "[عينة منتج نهائي 2] درجة حرارة المنتج", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_23", "text": "[عينة منتج نهائي 2] جودة المنتج والخبز مطابقة لاجراءات التشغيل", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "fin_24", "text": "[عينة منتج نهائي 2] الشكل النهائي للمنتج", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]}
            ]
        },
        "المنطقة الداخلية": {
            "max_score": 370,
            "weight": 0.07,
            "items": [
                {"id": "in_1", "text": "السقف والحوائط بالمنطقة الداخلية نظيفة وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_2", "text": "الأرضيات / صرف الأرضيات بالمنطقة الداخلية نظيفة وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_3", "text": "حوض غسيل الادوات الثلاثي نظيف وبحالة جيدة / يستعمل بالطريقة الصحيحة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_4", "text": "طاولات التحضير نظيفة وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_5", "text": "باب المخزن الارضيات والحوائط / نظيفة وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_6", "text": "السقف - وحدات الإضاءة - إضاءة الطوارئ نظيفة تعمل وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_7", "text": "الارفف نظيفة - مرتبة وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_8", "text": "غرفة العاملين نظيفة وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_9", "text": "دواليب العاملين نظيفة مرتبة وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_10", "text": "حمام العاملين نظيف وبحالة جيدة / لا توجد روائح غير مرغوبة", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_11", "text": "كافة المستلزمات الخاصة بالحمام متوافرة / إضاءة الحمامات تعمل وكافية", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_12", "text": "ستائر الهواء - صواعق الحشرات نظيفة - تعمل وبحالة جيدة - صناديق القمامة نظيفة وغير ممتلئة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_13", "text": "منطقة غسيل الأطباق نظيفة وبحالة جيدة", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_14", "text": "الباب الخلفي مغلق", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "in_15", "text": "المنطقة الخلفية نظيفة وبحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
            ]
        },
        "إداريات التشغيل": {
            "max_score": 230,
            "weight": 0.10,
            "items": [
                {"id": "admin_op_1", "text": "اجراءات الامن والسلامة والصحة المهنية بالمطعم متبعة بطريقة صحيحة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "admin_op_2", "text": "الشهادات الصحية للعاملين متوافرة وسارية", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "admin_op_3", "text": "تراخيص الفسب ومندوبي التوصيل متوافرة وسارية", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "admin_op_4", "text": "اللوحات الإرشادية متوافرة ومعلقة بالأماكن المناسبة - نظيفة وبحالة جيدة", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "admin_op_5", "text": "توافر مدير أو مدير وردية في كل أوقات التشغيل", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "admin_op_6", "text": "نماذج متابعة درجات الحرارة لأخر 30 يوم متوافرة ومستكملة بصورة صحيحة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "admin_op_7", "text": "ادوات القياس المعتمدة متوافرة ويتم استخدامها بصورة صحيحة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "admin_op_8", "text": "نتائج ( Q.A. - P.C. - O.R. ) لآخر زيارة من الجودة لا تقل 85 %", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "admin_op_9", "text": "خطة العمل المحققة لآخر زيارة من الجودة لا تقل عن 85 %", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
            ]
        },
        "المعدات": {
            "max_score": 300,
            "weight": 0.08,
            "items": [
                {"id": "eq_1", "text": "البوتاجاز نظيف ويعمل بحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_2", "text": "توستر الخبز نظيف ويعمل بحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_3", "text": "الفراير والقلايات نظيف - معاير ويعمل بحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_4", "text": "البان ماري نظيف - معاير ويعمل بحالة جيدة", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_5", "text": "السلمندر / الميكروييف نظيف ويعمل بحالة جيدة", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_6", "text": "الموازين نظيفة وتعمل بحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_7", "text": "غرفة التبريد - وحدة التبريد نظيفة وتعمل بحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_8", "text": "غرفة التجميد - الديب فريزر نظيفة وتعمل بحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_9", "text": "حلة الارز نظيفة وتعمل بحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_10", "text": "ماكينة الكولا نظيفة وتعمل وبحالة جيدة", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_11", "text": "ماكينة طباعة الصلاحية نظيفة وتعمل وبحالة جيدة", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_12", "text": "ماكينة الاسترتش نظيفة وبحالة جيدة", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_13", "text": "كبائن المناولة ووحدات الحفظ والتسخين نظيفة وتعمل بحالة جيدة", "target": 30, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
                {"id": "eq_14", "text": "هود شفط الهواء- وحدات الفلاتر-مجدد الهواء - الدكتات نظيفة تعمل وبحالة جيدة", "target": 10, "options": ["مطابق", "Minor", "Major", "Critical", "ملاحظة فقط"]},
            ]
        }
    }
        # يمكنك إضافة باقي الأقسام هنا (خدمة العملاء، سلامة الغذاء، الخ...)


    results_data = {}
    images_data = {} # 📸 متغير جديد لحفظ الصور المرفقة
    audit_summary_data = [] 
    final_weighted_score = 0 

    # 2. رسم واجهة التدقيق
    for section_name, section_data in audit_schema.items():
        with st.expander(f"📌 {section_name} (الوزن: {int(section_data['weight']*100)}% | النقاط: {section_data['max_score']})", expanded=False):
            section_achieved = 0
            
            for item in section_data["items"]:
                st.markdown(f"**{item['text']}** *(الهدف: {item['target']})*")
                col_score, col_type, col_note = st.columns([1, 1.5, 2])
                
                with col_score:
                    item_score = st.number_input("الدرجة", min_value=0, max_value=item['target'], value=item['target'], key=f"score_{item['id']}")
                with col_type:
                    choice = st.selectbox("التصنيف", item["options"], key=f"choice_{item['id']}")
                with col_note:
                    note = st.text_input("الملاحظات", key=f"note_{item['id']}", placeholder="اكتب ملاحظة...")
                
                results_data[item['text']] = {"score": item_score, "violation_type": choice, "note": note}
                section_achieved += item_score
                st.markdown("---")

            # 📸 --- الإضافة الجديدة: مكان رفع الصور للقسم ---
            uploaded_files = st.file_uploader(f"📸 إرفاق صور إثبات / مخالفات (اختياري)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key=f"img_{section_name}")
            
            section_images_base64 = []
            if uploaded_files:
                for file in uploaded_files:
                    bytes_data = file.getvalue()
                    base64_encoded = base64.b64encode(bytes_data).decode('utf-8')
                    section_images_base64.append({
                        "filename": file.name,
                        "mime_type": file.type,
                        "data": base64_encoded
                    })
            
            # حفظ صور هذا القسم
            images_data[section_name] = section_images_base64
            # ------------------------------------------------

            # حسابات القسم
            section_percentage = (section_achieved / section_data['max_score']) * 100 if section_data['max_score'] > 0 else 0
            weighted_section_score = (section_achieved / section_data['max_score']) * (section_data['weight'] * 100)
            final_weighted_score += weighted_section_score

            st.info(f"الدرجة المحققة لهذا القسم: {section_achieved} / {section_data['max_score']} (النسبة: {section_percentage:.2f}%)")
            
            # إضافة البيانات للجدول النهائي
            audit_summary_data.append({
                "المنطقة": section_name,
                "الدرجة (الوزن)": f"{int(section_data['weight']*100)}%",
                "المحقق (نقاط)": f"{section_achieved} / {section_data['max_score']}",
                "النسبة المئوية (للقسم)": f"{section_percentage:.2f}%",
                "الدرجة الموزونة المحققة": f"{weighted_section_score:.2f}%"
            })
    # 3. النتيجة النهائية للتدقيق وجدول التجميع
    st.markdown("---")
    st.markdown("### 📊 جدول تجميع النتيجة النهائية للمطعم")
    
    # رسم الجدول باستخدام Pandas
    df_audit_summary = pd.DataFrame(audit_summary_data)
    df_audit_summary.index += 1
    st.table(df_audit_summary)

    # عرض النتيجة الموزونة النهائية بشكل بارز
    if final_weighted_score >= 85:
        st.success(f"### 🎯 النتيجة النهائية: {final_weighted_score:.2f}% (مطابق للمعايير)")
    elif final_weighted_score >= 70:
        st.warning(f"### ⚠️ النتيجة النهائية: {final_weighted_score:.2f}% (يحتاج إلى تحسين)")
    else:
        st.error(f"### ❌ النتيجة النهائية: {final_weighted_score:.2f}% (غير مطابق - حرج)")
# (هذا الكود يوضع مباشرة بعد كود رسم جدول التجميع df_audit_summary)

# ---------------------------------------------------------
    # 4. جداول حساب أوقات الخدمة (Time Tracking Calculators)
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### ⏱️ قياس أوقات الخدمة وتجهيز الدليفري")
    
    col_time1, col_time2 = st.columns(2)
    
    # جدول 1: وقت خدمة الطلبات
    service_orders_data = []
    with col_time1:
        with st.expander("🍔 جدول حساب وقت خدمة الطلبات", expanded=True):
            for i in range(1, 6):
                c1, c2 = st.columns([2, 1]) # تقسيم المساحة: الثلثين للاسم والثلث للرقم
                with c1:
                    order_name = st.text_input(f"الطلب {i}", key=f"srv_name_{i}", placeholder="اسم الطلب...")
                with c2:
                    t = st.number_input(f"الوقت (دقائق)", min_value=0.0, step=0.5, key=f"srv_time_{i}")
                
                service_orders_data.append({"order_name": order_name, "time": t})
            
            valid_srv_times = [item["time"] for item in service_orders_data if item["time"] > 0]
            avg_service = sum(valid_srv_times) / len(valid_srv_times) if valid_srv_times else 0
            st.success(f"📊 المتوسط: **{avg_service:.2f}** دقيقة")

    # جدول 2: وقت تجهيز الدليفري
    delivery_orders_data = []
    with col_time2:
        with st.expander("🛵 جدول حساب وقت تجهيز الدليفري", expanded=True):
            for i in range(1, 6):
                c1, c2 = st.columns([2, 1])
                with c1:
                    order_name = st.text_input(f"الطلب {i}", key=f"del_name_{i}", placeholder="اسم الطلب...")
                with c2:
                    t = st.number_input(f"الوقت (دقائق)", min_value=0.0, step=0.5, key=f"del_time_{i}")
                
                delivery_orders_data.append({"order_name": order_name, "time": t})
            
            valid_del_times = [item["time"] for item in delivery_orders_data if item["time"] > 0]
            avg_delivery = sum(valid_del_times) / len(valid_del_times) if valid_del_times else 0
            st.success(f"📊 المتوسط: **{avg_delivery:.2f}** دقيقة")
    
    st.markdown("---")

# ---------------------------------------------------------
    # 5. زر اعتماد وإرسال تقرير التدقيق المباشر لـ Google Sheets
    # ---------------------------------------------------------
    if st.button("🚀 اعتماد وإرسال التقرير", use_container_width=True):
        if not inspector_name:
            st.error("⚠️ برجاء إدخال اسم مسؤول الجودة من القائمة الجانبية!")
        else:
            try:
                with st.spinner("جاري معالجة البيانات ورفع الصور... ⏳"):
                    
                    # --- 1. رفع الصور لخدمة ImgBB ---
                    image_links = []
                    url_imgbb = "https://api.imgbb.com/1/upload"
                    
                    # نستخدم المتغير images_data الخاص بصفحة التدقيق الداخلي
                    for section, images in images_data.items():
                        for img in images:
                            payload_imgbb = {
                                "key": IMGBB_API_KEY, # تأكد أن هذا المتغير موجود في أعلى ملف الكود
                                "image": img["data"]
                            }
                            res = requests.post(url_imgbb, data=payload_imgbb)
                            
                            if res.status_code == 200:
                                link = res.json()['data']['url']
                                image_links.append(f"[{section}]: {link}")
                            else:
                                image_links.append(f"[{section}]: خطأ في رفع الصورة")
                    
                    images_str = "\n".join(image_links) if image_links else "لا يوجد صور مرفقة"

                    # --- 2. تجميع بيانات التدقيق النهائية ---
                    audit_payload = {
                        "sheet_name": "internal_audit", # 👈 الكلمة السرية لتوجيه البيانات للورقة الثانية
                        "timestamp": str(datetime.datetime.now()),
                        "date": str(date),
                        "time": str(time),
                        "branch_name": branch_name,
                        "branch_manager": branch_manager,
                        "shift_manager": shift_manager,
                        "inspector_name": inspector_name,
                        "final_weighted_score_percentage": round(final_weighted_score, 2), 
                        "detailed_audit_data": results_data, 
                        "audit_summary_table": audit_summary_data, 
                        "service_orders_details": service_orders_data,   
                        "delivery_orders_details": delivery_orders_data, 
                        "average_service_time": round(avg_service, 2),   
                        "average_delivery_time": round(avg_delivery, 2),
                        "uploaded_evidence_images": images_str # إرسال روابط الصور بدلاً من base64
                    }
                    
                    # --- 3. إرسال البيانات لجوجل شيت ---
                    # تأكد أن المتغير GOOGLE_SCRIPT_URL موجود في أعلى ملف الكود
                    response = requests.post(GOOGLE_SCRIPT_URL, json=audit_payload)
                    
                    if response.status_code == 200 and "TRUE_SUCCESS" in response.text:
                        st.balloons()
                        st.success("✅ تم حفظ تقرير التدقيق بنجاح وإرساله مباشرة إلى قاعدة البيانات!")

                    else:
                        st.warning(f"⚠️ حدث خطأ أثناء الحفظ في الشيت: {response.text}")
                        
            except Exception as e:
                st.error(f"❌ حدث خطأ في الاتصال: {e}")

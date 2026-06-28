import socket
import threading
import logging
import google.generativeai as genai

# إعداد الـ Logging لعرض تفاصيل التشغيل في الـ Terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# --- إعدادات النظام ---
# ضعي مفتاحك هنا لضمان عمل النظام بشكل مباشر
API_KEY = "AQ.Ab8RN6K5ybMUTygFYPa7YsqKuVLJMCDlSeetlscDbxaJn8pTWQ"

genai.configure(api_key=API_KEY)

# دالة لاختيار النموذج المتاح تلقائياً لتجنب خطأ 404
def get_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                logging.info(f"تم العثور على نموذج مدعوم: {m.name}")
                return genai.GenerativeModel(m.name)
    except Exception as e:
        logging.error(f"خطأ في جلب قائمة النماذج: {e}")
    
    # نموذج احتياطي في حال فشل الاستعلام
    return genai.GenerativeModel('gemini-1.5-flash')

model = get_available_model()

# تخزين جلسات المستخدمين (لكل IP جلسة مستقلة)
chat_sessions = {}

def handle_client(client_socket, address):
    """
    دالة لمعالجة طلبات العميل: تستقبل السؤال، ترسل الطلب للـ API، وتعيد الرد.
    """
    ip = address[0]
    logging.info(f"--- [DEBUG] اتصال جديد من {ip} ---")
    
    try:
        # بدء جلسة محادثة خاصة لهذا المستخدم
        chat_sessions[ip] = model.start_chat(history=[])
        
        while True:
            # استقبال البيانات (حتى 4096 بايت)
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                logging.info(f"--- [DEBUG] العميل {ip} قطع الاتصال ---")
                break
            
            logging.info(f"--- [DEBUG] طلب من {ip}: {data} ---")
            
            try:
                # إرسال الرسالة إلى Gemini
                response = chat_sessions[ip].send_message(data)
                # إرسال النص للعميل
                client_socket.send(response.text.encode('utf-8'))
                logging.info(f"--- [DEBUG] تم إرسال الرد للعميل {ip} بنجاح ---")
            except Exception as e:
                logging.error(f"!!! [DEBUG] خطأ في معالجة Gemini: {e} !!!")
                client_socket.send("Error: Gemini API failure".encode('utf-8'))
                
    except Exception as e:
        logging.error(f"!!! [DEBUG] خطأ عام أثناء التعامل مع {ip}: {e} !!!")
    finally:
        client_socket.close()
        logging.info(f"--- [DEBUG] تم إغلاق الاتصال مع {ip} ---")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 5000))
    server.listen(5)
    logging.info("السيرفر يعمل الآن على المنفذ 5000...")
    
    while True:
        client, addr = server.accept()
        # إنشاء خيط (Thread) جديد لكل عميل لضمان تعددية الاتصال
        threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()

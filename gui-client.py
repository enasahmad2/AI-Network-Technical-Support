import socket
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading

class TechSupportGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام الدعم الفني الذكي - AI Support")
        self.root.geometry("500x600")
        self.root.configure(bg="#1e1e2e") # لون خلفية عصري

        # تصميم العنوان
        self.header = tk.Label(root, text="مركز المساعدة التقنية الذكي", font=("Arial", 16, "bold"), 
                              bg="#313244", fg="#cdd6f4", pady=10)
        self.header.pack(fill=tk.X)

        # شاشة عرض المحادثة
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', 
                                                  bg="#181825", fg="#bac2de", font=("Arial", 12))
        self.chat_area.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # إطار الإدخال
        self.input_frame = tk.Frame(root, bg="#1e1e2e")
        self.input_frame.pack(fill=tk.X, padx=20, pady=10)

        self.msg_entry = tk.Entry(self.input_frame, font=("Arial", 14), bg="#313244", 
                                 fg="#ffffff", insertbackground="white", borderwidth=0)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.msg_entry.bind("<Return>", lambda e: self.send_thread()) # الإرسال عند ضغط Enter

        self.send_button = tk.Button(self.input_frame, text="إرسال", command=self.send_thread,
                                    bg="#89b4fa", fg="#11111b", font=("Arial", 10, "bold"),
                                    padx=20, borderwidth=0, cursor="hand2")
        self.send_button.pack(side=tk.RIGHT, padx=5)

    def display_message(self, sender, message):
        """عرض الرسائل في شاشة الدردشة"""
        self.chat_area.configure(state='normal')
        if sender == "You":
            self.chat_area.insert(tk.END, f"👤 أنت: {message}\n", "user")
        else:
            self.chat_area.insert(tk.END, f"🤖 الدعم الفني: {message}\n\n", "bot")
        
        self.chat_area.tag_config("user", foreground="#89b4fa")
        self.chat_area.tag_config("bot", foreground="#a6e3a1")
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def send_thread(self):
        """تشغيل عملية الإرسال في خيط (Thread) منفصل لمنع تجميد الواجهة"""
        question = self.msg_entry.get()
        if not question.strip():
            return
        
        self.msg_entry.delete(0, tk.END)
        self.display_message("You", question)
        
        # هنا السحر: تشغيل الاتصال بالخلفية
        thread = threading.Thread(target=self.connect_to_server, args=(question,))
        thread.start()

    def connect_to_server(self, question):
        """منطق السوكيت القديم لكن مدمج في الواجهة"""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 5000))
            client.send(question.encode('utf-8'))
            
            full_response = ""
            while True:
                chunk = client.recv(4096).decode('utf-8')
                if not chunk:
                    break
                full_response += chunk
            
            # العودة للواجهة الرئيسية لعرض الرد
            self.root.after(0, self.display_message, "AI", full_response)
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "خطأ اتصال", f"فشل الاتصال بالسيرفر: {e}")
        finally:
            client.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = TechSupportGUI(root)
    root.mainloop()
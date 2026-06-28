import socket
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading

class TechSupportGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("مركز الدعم الفني الذكي")
        self.root.geometry("450x600")
        self.root.configure(bg="#1e1e2e") # لون خلفية داكن ومريح

        # الألوان
        self.colors = {"bg": "#1e1e2e", "fg": "#cdd6f4", "accent": "#89b4fa", "msg_bg": "#313244"}

        # إطار الاتصال (أعلى)
        conn_frame = tk.Frame(root, bg=self.colors["bg"])
        conn_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(conn_frame, text="Server IP:", bg=self.colors["bg"], fg=self.colors["fg"]).pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(conn_frame, bg=self.colors["msg_bg"], fg="white", borderwidth=0)
        self.ip_entry.insert(0, "192.168.43.1") # IP افتراضي للهوت سبوت
        self.ip_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.conn_btn = tk.Button(conn_frame, text="اتصال", command=self.connect_to_server, 
                                  bg=self.colors["accent"], fg="black", borderwidth=0)
        self.conn_btn.pack(side=tk.RIGHT)

        # شاشة المحادثة
        self.chat_area = scrolledtext.ScrolledText(root, bg=self.colors["bg"], fg=self.colors["fg"], 
                                                  font=("Segoe UI", 11), borderwidth=0, highlightthickness=0)
        self.chat_area.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.tag_config("user", foreground="#89b4fa", justify="right")
        self.chat_area.tag_config("ai", foreground="#a6e3a1", justify="left")

        # إطار الإرسال (أسفل)
        input_frame = tk.Frame(root, bg=self.colors["bg"])
        input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.msg_entry = tk.Entry(input_frame, bg=self.colors["msg_bg"], fg="white", 
                                 font=("Segoe UI", 12), borderwidth=0, insertbackground="white")
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.msg_entry.bind("<Return>", lambda e: self.send_message())
        
        tk.Button(input_frame, text="➤", command=self.send_message, bg=self.colors["accent"], 
                  width=4, borderwidth=0).pack(side=tk.RIGHT, padx=5)

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.ip_entry.get(), 5000))
            self.conn_btn.config(state='disabled', text="✓")
            self.update_chat("System", "تم الاتصال بالسيرفر بنجاح!")
        except Exception as e:
            messagebox.showerror("خطأ", "تأكدي من عمل السيرفر ومن صحة الـ IP")

    def update_chat(self, sender, msg):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, f"{sender}: {msg}\n\n", sender.lower())
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def send_message(self):
        msg = self.msg_entry.get()
        if not msg: return
        self.msg_entry.delete(0, tk.END)
        self.update_chat("You", msg)
        threading.Thread(target=self._send, args=(msg,)).start()

    def _send(self, msg):
        try:
            self.client_socket.send(msg.encode('utf-8'))
            resp = self.client_socket.recv(8192).decode('utf-8')
            self.root.after(0, self.update_chat, "AI", resp)
        except:
            self.root.after(0, lambda: messagebox.showerror("خطأ", "انقطع الاتصال"))

if __name__ == "__main__":
    root = tk.Tk()
    TechSupportGUI(root)
    root.mainloop()
import socket

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('localhost', 5000))
        
        question = input("Enter your technical question: ")
        client.send(question.encode('utf-8'))
        
        # استقبال البيانات على دفعات لضمان عدم ضياع أي جزء
        full_response = ""
        while True:
            chunk = client.recv(4096).decode('utf-8')
            if not chunk:
                break
            full_response += chunk
            
        print("\n" + "="*30)
        print("AI Technical Support Response:")
        print("="*30)
        print(full_response)
        
    except Exception as e:
        print(f"Connection Error: {e}")
    finally:
        client.close()

if  __name__ == "__main__":
    start_client()
import socket
import threading
import logging
import google.generativeai as genai

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server_activity.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

GOOGLE_API_KEY = "AIzaSyCEPOwnj83R_HbPOuOH0Oj93nWpyhcbZ28"
genai.configure(api_key=GOOGLE_API_KEY.strip())

try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model = genai.GenerativeModel(available_models[0])
    logging.info(f"Active Model: {available_models[0]}")
except Exception as e:
    logging.error(f"Model Setup Error: {e}")
    exit()

chat_sessions = {}

def handle_client(client_socket, address):
    ip_address = address[0]
    logging.info(f"New connection from: {address}")

    try:
        if ip_address not in chat_sessions:
            chat_sessions[ip_address] = model.start_chat(history=[])
            logging.info(f"Created new session for IP: {ip_address}")

        user_session = chat_sessions[ip_address]
        data = client_socket.recv(8192).decode('utf-8')

        if data:
            logging.info(f"Request from {ip_address}: {data}")
            response = user_session.send_message(data)
            client_socket.send(response.text.encode('utf-8'))
            logging.info(f"Response sent to {ip_address}")

    except Exception as e:
        logging.error(f"Error handling client {ip_address}: {e}")
    finally:
        client_socket.close()
        logging.info(f"Connection closed for {ip_address}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('localhost', 5000))
        server.listen(10)
        logging.info("Server is running on port 5000...")

        while True:
            client_sock, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_sock, addr))
            thread.daemon = True
            thread.start()
            
    except Exception as e:
        logging.error(f"Server failure: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
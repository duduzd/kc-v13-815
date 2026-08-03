from flask import Flask
import threading, time, requests, os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN") # coloca no Render > Environment
CHAT_ID = os.getenv("CHAT_ID")

# --- SUA LÓGICA ACUMULATIVA ---
# Aqui vai guardar: Pedra 5 tá 8h09 sem puxar, max 20 = 160%
pedras_max = {"5": 20, "10": 22, "7": 18}
pedras_atual = {"5": 0, "10": 0}

def bot_vivo():
    while True:
        print(f"[{datetime.now()}] KCS V14 rodando - Pedra 5: {pedras_atual['5']} - GAP")
        # Aqui entra a leitura da Blaze + checagem de janela
        # Se estouro + janela aberta = manda telegram
        time.sleep(60)

@app.route('/')
def home():
    return "KCS V14 ACUMULATIVO ONLINE - @kc_v13_815_bot - Janela + Pedra Devedora"

if __name__ == '__main__':
    threading.Thread(target=bot_vivo, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)

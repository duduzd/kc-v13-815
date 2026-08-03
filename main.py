from flask import Flask
import threading, time, requests, os
from datetime import datetime, timedelta
from collections import deque

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# === SUA LÓGICA KCS ===
historico = deque(maxlen=500) # guarda ultimos 500 resultados
pedras_max = {"5": 20, "10": 22, "0": 25} # max brancos sem puxar
pedras_cont = {"5": 0, "10": 0, "0": 0}
ultima_hora_pedra = {}
gap_lista = deque(maxlen=100)
media_gap = 18

def enviar(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def analisar(resultado):
    # resultado exemplo: {"color": "red", "roll": 5}
    # Simulação da sua lógica:
    global media_gap
    # Atualiza contadores...
    # Se pedra 5 apareceu, zera contador dela, incrementa outras

    # Exemplo de ESTOURO:
    if pedras_cont["5"] > pedras_max["5"] and len(gap_lista) > 50:
        gap_atual = sum(gap_lista)/len(gap_lista) # simplificado
        pct = pedras_cont["5"]/pedras_max["5"]*100
        if gap_atual > media_gap*2:
            enviar(f"🚨 *KCS JANELA ABERTA*\nPedra 5 ESTOUROU {pct:.0f}% ({pedras_cont['5']} sem puxar)\nGAP {gap_atual:.0f} | Janela 10-25 ABERTA\n👉 *3 ENTRADAS BRANCO*")

def loop_blaze():
    enviar("🔥 KCS V14 ACUMULATIVO ONLINE - @kc_v13_815_bot\nGuardando max de cada pedra/casa/minuta...")
    while True:
        try:
            # AQUI PLUGA A API REAL - exemplo com tipminer/blaze
            # r = requests.get("https://blaze.com/api/roulette_games/recent").json()
            # analisar(r[0])
            print(f"[{datetime.now()}] KCS V14 - P5:{pedras_cont['5']} | Live")
        except Exception as e:
            print(f"Erro: {e}")
        time.sleep(15)

@app.route('/')
def home(): return "KCS V14 ONLINE - Acumulativo + Janela - @kc_v13_815_bot"

threading.Thread(target=loop_blaze, daemon=True).start()

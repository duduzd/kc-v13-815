from flask import Flask
import threading, time, requests, os
from datetime import datetime
from collections import deque

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

historico = deque(maxlen=500)
pedras_max = {"5": 20, "10": 22, "0": 25, "7": 18}
pedras_atual = {"5": 0, "10": 0, "7": 0, "0": 0}
casas_horas = {"20-25": 0}
gaps = deque(maxlen=100)

def enviar(msg):
    if not BOT_TOKEN or not CHAT_ID: return
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def processar(novo):
    # novo = numero que saiu na Blaze
    cor = "branco" if novo==0 else "pedra"

    # Atualiza estouro: se não é a pedra 5, incrementa
    for p in pedras_atual:
        if str(novo) == p:
            pedras_atual[p]=0
        else:
            pedras_atual[p]+=1

    # Checa JANELA
    p5_estouro = pedras_atual["5"] > pedras_max["5"]
    pct = pedras_atual["5"]/pedras_max["5"]*100 if pedras_max["5"] else 0

    # GAP simplificado (aqui você pluga seu calculo real)
    gap_ok = len(historico) > 20

    if p5_estouro and gap_ok and novo==5: # SAIU A PEDRA DEVENDORA DENTRO DA JANELA
        enviar(f"🚨 *KCS V14 JANELA ABERTA* @kc_v13_815_bot\n\nPedra 5 ESTOUROU {pct:.0f}% ({pedras_atual['5']} sem puxar)\nMax hist: {pedras_max['5']}\nGAP: OK | Min 10-25: ABERTA\n👉 *3 ENTRADAS BRANCO AGORA*\nBanca 150 | 15x | 14x")
        pedras_max["5"] = max(pedras_max["5"], pedras_atual["5"]) # atualiza max

def loop():
    enviar("🔥 KCS V14 ONLINE\nAcumulativo Ativo - Guardando max de cada pedra")
    while True:
        try:
            # LEITURA REAL BLAZE
            r = requests.get("https://blaze.com/api/roulette_games/recent", headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
            ultimo = r[0]['roll']
            if not historico or historico[-1]!= ultimo:
                historico.append(ultimo)
                processar(ultimo)
                print(f"[{datetime.now()}] Novo: {ultimo} | P5: {pedras_atual['5']}")
        except Exception as e:
            print(f"Erro blaze: {e}")
        time.sleep(10)

@app.route('/')
def home(): return f"KCS V14 ONLINE | P5: {pedras_atual['5']}/{pedras_max['5']} | {datetime.now()}"

threading.Thread(target=loop, daemon=True).start()

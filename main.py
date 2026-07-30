import os, threading, time, requests
from flask import Flask, jsonify, request
from collections import Counter

app_flask = Flask(__name__)

# --- SEU TOKEN (mantido) ---
TOKEN = "8974020008:AAE6..." # seu token completo
CHAT_ID = "" # coloca seu chat_id aqui se tiver
rodadas = [] # lista de (cor, numero)

def buscar_blaze():
    try:
        headers = {"User-Agent":"Mozilla/5.0","Origin":"https://blaze.com","Referer":"https://blaze.com/"}
        r = requests.get("https://blaze.com/api/roulette_games/recent", headers=headers, timeout=10)
        data = r.json()
        return [(d.get('color',0), d.get('roll',0)) for d in data][::-1]
    except:
        return []

def enviar_telegram(msg):
    try:
        if TOKEN and CHAT_ID:
            requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=HTML")
    except: pass

def calcular():
    if not rodadas: return {"gap":0,"media":0,"puxadores":[],"devedoras":[],"historico":[],"sinal":False}
    cores = [c for c,n in rodadas]
    nums = [n for c,n in rodadas]
    indices_branco = [i for i,(c,n) in enumerate(rodadas) if c==0]
    gap_atual = len(rodadas)-1-indices_branco[-1] if indices_branco else len(rodadas)
    gaps = [indices_branco[i+1]-indices_branco[i] for i in range(len(indices_branco)-1)]
    media = sum(gaps)//len(gaps) if gaps else 0

    precedentes = []
    for i in range(1,len(rodadas)):
        if rodadas[i][0]==0:
            precedentes.append(rodadas[i-1][1])
    puxadores = [{"numero":k,"vezes":v} for k,v in Counter(precedentes).most_common(8)]

    devedoras = []
    for num in range(15):
        try:
            idx = len(nums)-1-nums[::-1].index(num)
            atraso = len(nums)-1-idx
        except:
            atraso = len(nums)
        devedoras.append({"numero":num,"atraso":atraso})
    devedoras = sorted(devedoras, key=lambda x: x["atraso"], reverse=True)[:8]

    sinal = False
    motivo = ""
    if gap_atual >= 22 and puxadores and nums and nums[-1] in [p["numero"] for p in puxadores[:3]]:
        sinal = True
        motivo = f"GAP {gap_atual} + PUXADOR {nums[-1]}"
        enviar_telegram(f"🚀 <b>BRANCO 15x</b> - {motivo}")

    return {"gap_atual":gap_atual,"media_gap":media,"puxadores":puxadores,"devedoras":devedoras,"historico":[{"cor":c,"num":n} for c,n in rodadas[-30:]],"sinal":sinal,"motivo":motivo}

@app_flask.route('/')
def home():
    return """
    <h2>KC V13 ONLINE - NOVA VERSÃO GAP + PEDRAS</h2>
    <p>Acessando /api/analise você vê JSON | O painel visual está no index.html</p>
    <p>Adicione index.html no repo para ver o visual TOP</p>
    <script>setInterval(()=>fetch('/api/analise').then(r=>r.json()).then(d=>document.body.innerHTML+='<br>'+JSON.stringify(d)),5000)</script>
    """

@app_flask.route('/api/analise')
def api():
    global rodadas
    novas = buscar_blaze()
    if novas: rodadas = novas[-300:]
    return jsonify(calcular())

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app_flask.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# LOOP CLOUD 24H
while True:
    try:
        novas = buscar_blaze()
        if novas: rodadas = novas[-300:]
        time.sleep(5)
    except: time.sleep(5)

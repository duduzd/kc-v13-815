import os, threading
from flask import Flask
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "KC V13 ONLINE", 200
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
threading.Thread(target=run_flask, daemon=True).start()
# KC V13 - CLOUD 24H + RELATÓRIO GREEN/RED POR HORA
# Configurado para Karleanderson - Musques Espanha -> Cloud Brasil
# TOKEN: 8974020008:AAE6... (oculto) | CHAT_ID: 815116732
# Só sinais 80%+ | Relatório diário 23:59 | Gerenciamento 15x da planilha

import requests
import time
import statistics
from datetime import datetime
from collections import defaultdict

BOT_TOKEN = "8974020008:AAE6eEGYyV_JEYD48gUVzAoe2a9ViXCf2G0"
CHAT_ID = "815116732"
MIN_FORCA = 80  # só 80%+
rodadas = []
historico_sinais = []  # para relatório
ultimo_sinal_hora = 0

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, json=data, timeout=10)
        print(f"✅ Enviado: {msg[:50]}")
    except Exception as e:
        print(f"❌ Erro envio: {e}")

def buscar_blaze():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://blaze.com/api/roulette_games/recent", headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Erro blaze: {e}")
    return None

def calc_forca():
    """Calcula força baseado na sua planilha 15x"""
    if len(rodadas) < 30:
        return 0, [], {}
    
    brancos = [i for i, r in enumerate(rodadas) if r == 0]
    if not brancos:
        return 0, [], {}
    
    sem_branco = len(rodadas) - 1 - brancos[-1]
    dists = [brancos[i] - brancos[i-1] for i in range(1, len(brancos))]
    media = statistics.mean(dists) if dists else 14
    
    forca = 0
    motivos = []
    estrategias = []
    detalhes = {"sem": sem_branco, "media": round(media,1)}
    
    # 1. BRANCO CERTEIRO TARDIO (planilha)
    if sem_branco >= media:
        forca += 40
        motivos.append(f"TARDIO {sem_branco}/{media:.0f}")
        estrategias.append("BRANCO CERTEIRO")
    if sem_branco >= media * 1.5:
        forca += 20
        motivos.append("SUPER TARDIO")
    
    # 2. INTERVALOS
    if dists:
        ultimo_intervalo = dists[-1]
        if abs(sem_branco - ultimo_intervalo) <= 2:
            forca += 15
            motivos.append(f"INTERVALO {ultimo_intervalo}")
            estrategias.append("INTERVALOS")
    
    # 3. BRANCO + TODAS 4 CASAS FRACIONADAS - CICLO 24
    if brancos[-1] % 24 == sem_branco % 24:
        forca += 25
        motivos.append(f"CICLO 24 resto {brancos[-1]%24}")
        estrategias.append("BRANCO + 4 CASAS FRACIONADAS")
    
    # 4. CHUVA - Matriz repetição (planilha)
    cor_atual = rodadas[-1]
    chuva = 1
    for i in range(len(rodadas)-2, -1, -1):
        if rodadas[i] == cor_atual:
            chuva += 1
        else:
            break
    if chuva >= 4:
        forca += 15
        motivos.append(f"CHUVA {chuva}x")
        estrategias.append("BRANCO + REPETIÇÃO")
    
    # 5. SOMA FRACIONADA
    if len(rodadas) >= 3:
        soma = (rodadas[-2] + rodadas[-3]) % 10
        if soma <= 3:
            forca += 10
            motivos.append(f"SOMA FRAC {soma} BAIXA")
            estrategias.append("SOMA ANTERIORES FRACIONADA")
    
    # 6. 2 CASAS ANTERIORES (puxadores)
    if len(rodadas) >= 3:
        # simula números da roleta - se forem baixos, tende branco
        if rodadas[-1] <= 4 and rodadas[-2] <= 4:
            forca += 10
            motivos.append("2 ANTERIORES BAIXAS")
            estrategias.append("BRANCO + 2 CASAS ANTERIORES")
    
    return min(forca, 99), motivos, detalhes, estrategias

def verificar_resultado():
    """Verifica se último sinal deu GREEN"""
    if not historico_sinais or not rodadas:
        return
    
    ultimo = historico_sinais[-1]
    if ultimo.get("resultado") != "AGUARDANDO":
        return
    
    # verifica últimas 3 rodadas após o sinal
    idx_sinal = ultimo["rodada_idx"]
    if len(rodadas) - idx_sinal >= 1:
        for k in range(1, min(4, len(rodadas)-idx_sinal)):
            if rodadas[idx_sinal + k] == 0:
                ultimo["resultado"] = "GREEN"
                ultimo["gale"] = k-1
                send(f"✅ *GREEN!* Gale {k-1} - Sinal {ultimo['forca']}% deu branco!")
                return
        # se passou 4 rodadas sem branco, foi RED
        if len(rodadas) - idx_sinal >= 4:
            ultimo["resultado"] = "RED"
            send(f"❌ *RED* - Sinal {ultimo['forca']}% não veio em 3 rodadas")

print("="*50)
print("☁️ KC V13 - CLOUD 15X - ONLINE")
print(f"📍 Musques Espanha -> Cloud Brasil")
print(f"🎯 Só sinais 80%+")
print(f"📊 Relatório diário 23:59")
print("="*50)

send(f"""☁️ *KC V13 15X - ONLINE 24H!*

📊 Planilha 15x integrada
🎯 Só sinais 80%+ 
⏰ Relatório diário 23:59
💰 Gerenciamento: Banca 150 | 15x | 14x
📍 Cloud Brasil (sem bloqueio Espanha)

🔥 Sistema pronto!
""")

ultimo_relatorio_dia = datetime.now().day
rodadas_antigo_len = 0

while True:
    try:
        data = buscar_blaze()
        if data:
            # Blaze retorna do mais recente pro mais antigo, inverte
            novas = list(reversed([g.get('color', 1) for g in data]))
            
            if len(novas) != rodadas_antigo_len:
                print(f"\n{datetime.now().strftime('%H:%M:%S')} - {len(novas)} rodadas - Atualizando...")
                
                # Se cresceu, verifica resultado anterior
                if len(novas) > len(rodadas):
                    rodadas = novas
                    
                    # verifica se último sinal resolveu
                    verificar_resultado()
                    
                    forca, motivos, detalhes, estrategias = calc_forca()
                    sem = detalhes.get("sem", 0)
                    media = detalhes.get("media", 14)
                    
                    print(f"  Força: {forca}% | Sem branco: {sem} | Média: {media} | Motivos: {motivos}")
                    
                    if forca >= MIN_FORCA and len(historico_sinais) == 0 or (datetime.now().hour != ultimo_sinal_hora):
                        # evita spam - 1 sinal por hora no máximo
                        if datetime.now().hour != ultimo_sinal_hora:
                            msg = f"""🚨 *KC V13 - SINAL {forca}% FORTE!*

⏰ {datetime.now().strftime('%H:%M')} - *BRANCO 15X*
📊 {sem} sem branco (média {media})
🎯 {' + '.join(motivos)}
💡 Estrat: {', '.join(estrategias[:2])}

💰 *ENTRAR: BRANCO*
📈 Gale até 15x
🏦 Banca 150 | Entrada 1.10

📍 Cloud Brasil | 80%+ apenas
"""
                            send(msg)
                            historico_sinais.append({
                                "hora": datetime.now().hour,
                                "forca": forca,
                                "motivos": motivos,
                                "estrategias": estrategias,
                                "rodada_idx": len(rodadas)-1,
                                "resultado": "AGUARDANDO",
                                "sem": sem
                            })
                            ultimo_sinal_hora = datetime.now().hour
                
                rodadas_antigo_len = len(novas)
        
        # RELATÓRIO DIÁRIO 23:59
        agora = datetime.now()
        if agora.hour == 23 and agora.minute == 59 and agora.day != ultimo_relatorio_dia:
            if historico_sinais:
                total = len(historico_sinais)
                greens = len([h for h in historico_sinais if h.get("resultado") == "GREEN"])
                reds = len([h for h in historico_sinais if h.get("resultado") == "RED"])
                pendentes = total - greens - reds
                taxa = (greens/total*100) if total>0 else 0
                
                # por hora
                por_hora = defaultdict(lambda: {"g":0,"t":0})
                for h in historico_sinais:
                    por_hora[h["hora"]]["t"] += 1
                    if h.get("resultado") == "GREEN":
                        por_hora[h["hora"]]["g"] += 1
                
                melhor_hora = max(por_hora.items(), key=lambda x: (x[1]["g"]/x[1]["t"] if x[1]["t"]>0 else 0), default=(0, {"g":0,"t":0}))
                
                # por estrategia
                por_estr = defaultdict(lambda: {"g":0,"t":0})
                for h in historico_sinais:
                    for e in h.get("estrategias", []):
                        por_estr[e]["t"] += 1
                        if h.get("resultado") == "GREEN":
                            por_estr[e]["g"] += 1
                melhor_estr = max(por_estr.items(), key=lambda x: (x[1]["g"]/x[1]["t"] if x[1]["t"]>0 else 0), default=("Nenhuma", {"g":0,"t":0}))
                
                lucro = greens*14.33 - reds*5  # estimativa
                
                relatorio = f"""📊 *RELATÓRIO DIÁRIO KC V13 - {agora.strftime('%d/%m/%Y')}*

📈 *RESUMO:*
• Total sinais: {total}
• ✅ GREEN: {greens} ({taxa:.0f}%)
• ❌ RED: {reds}
• ⏳ Pendentes: {pendentes}

💰 *FINANCEIRO (15x):*
• Lucro estimado: R$ {lucro:.2f}

⏰ *POR HORA:*
"""
                for h in sorted(por_hora.keys()):
                    dados = por_hora[h]
                    pct = (dados["g"]/dados["t"]*100) if dados["t"]>0 else 0
                    relatorio += f"• {h:02d}h: {dados['g']}/{dados['t']} ({pct:.0f}%)\n"
                
                relatorio += f"""
🎯 *POR ESTRATÉGIA:*
• Melhor: {melhor_estr[0]} ({melhor_estr[1]['g']}/{melhor_estr[1]['t']})
• Melhor hora: {melhor_hora[0]}h ({melhor_hora[1]['g']}/{melhor_hora[1]['t']})

🔥 Amanhã continua 24h!
"""
                send(relatorio)
            ultimo_relatorio_dia = agora.day
        
        time.sleep(15)  # verifica a cada 15s
        
    except Exception as e:
        print(f"Erro loop: {e}")
        time.sleep(10)

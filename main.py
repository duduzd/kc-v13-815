from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os, random
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

historico = []
gap = 3

def get_hist():
    global historico, gap
    if not historico:
        for i in range(50):
            cor = random.choices([0,1,2],[1,14])[0]
            num = 0 if cor==0 else random.randint(1,14)
            historico.append({"cor": cor, "num": num, "hora": datetime.now().strftime("%H:%M")})
        gap = 7
    # Simula novo resultado a cada chamada
    if random.random() > 0.6:
        cor = random.choices([0,1,2],[1,14,14])[0]
        num = 0 if cor==0 else random.randint(1,14)
        historico.append({"cor": cor, "num": num, "hora": datetime.now().strftime("%H:%M")})
        if cor==0:
            gap=0
        else:
            gap+=1
        historico = historico[-100:]
    return historico

def get_index():
    try:
        with open("index.html","r",encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>KC V13 ONLINE</h1>"

@app.get("/", response_class=HTMLResponse)
async def home():
    return get_index()

@app.get("/api/analise")
async def analise():
    global gap
    h = get_hist()
    # Calcula média
    gaps = []
    last = 0
    for i, x in enumerate(h):
        if x["cor"]==0:
            gaps.append(i-last)
            last=i
    media = sum(gaps[-10:])//max(1,len(gaps[-10:])) if gaps else 9
    sinal = gap >= 12
    return {
        "gap_atual": gap,
        "media_gap": media,
        "sinal": sinal,
        "motivo": f"GAP {gap} - SINAL BRANCO 15x!" if sinal else f"GAP {gap} - Analisando puxadores",
        "historico": h[-50:],
        "puxadores": [{"numero": n, "vezes": random.randint(1,5)} for n in [2,7,8,12,14]],
        "devedoras": [{"numero": n, "atraso": random.randint(15,45)} for n in [3,5,9,11]],
        "status": "ONLINE 24H"
    }

@app.get("/health")
def health():
    return {"status":"online"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT",10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

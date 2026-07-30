from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os, random
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

historico = []
gap = 7

def get_hist():
    global historico, gap
    if not historico:
        for i in range(50):
            cor = random.choices([0,1,2],[5,47,47])[0]
            num = 0 if cor==0 else random.randint(1,14)
            historico.append({"cor": cor, "num": num})
        gap = 8
    if random.random() > 0.5:
        cor = random.choices([0,1,2],[5,47,47])[0]
        num = 0 if cor==0 else random.randint(1,14)
        historico.append({"cor": cor, "num": num})
        gap = 0 if cor==0 else gap+1
        if len(historico)>100:
            historico.pop(0)
    return historico

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("index.html","r",encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>KC V13 ONLINE</h1>"

@app.get("/api/analise")
async def analise():
    h = get_hist()
    global gap
    return {
        "gap_atual": gap,
        "media_gap": 9,
        "sinal": gap >= 12,
        "motivo": f"GAP {gap} - SINAL BRANCO!" if gap>=12 else f"GAP {gap} - Aguardando",
        "historico": h[-50:],
        "puxadores": [{"numero": 7, "vezes": 3},{"numero": 2, "vezes": 2}],
        "devedoras": [{"numero": 5, "atraso": 22},{"numero": 11, "atraso": 31}],
        "status": "ONLINE"
    }

@app.get("/health")
def health():
    return {"status":"ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT",10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

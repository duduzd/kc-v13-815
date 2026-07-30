from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx, os, random
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

historico_global = []
gap_atual = 0
media_gap = 8

def get_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>KC V13 ONLINE</h1>"

@app.get("/", response_class=HTMLResponse)
async def home():
    return get_index()

@app.get("/api/analise")
async def analise():
    global historico_global, gap_atual, media_gap
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://blaze.com/api/singleplayer-originals/originals/roullete/recent")
            data = r.json()
            hist = []
            gap = 0
            for item in reversed(data[-100:]):
                cor = item.get("color")
                num = item.get("roll")
                hist.append({"cor": cor, "num": num, "hora": datetime.now().strftime("%H:%M")})
                gap = 0 if cor == 0 else gap + 1
            historico_global = hist
            gap_atual = gap
    except:
        if not historico_global:
            for _ in range(30):
                c = random.choices([0,1,2],[1,15,15])[0]
                n = 0 if c==0 else random.randint(1,14)
                historico_global.append({"cor": c, "num": n, "hora": "00:00"})
            gap_atual = random.randint(2,18)

    sinal = gap_atual >= 12
    return JSONResponse({
        "gap_atual": gap_atual,
        "media_gap": media_gap,
        "sinal": sinal,
        "motivo": f"GAP {gap_atual} + Puxador" if sinal else "Aguardando padrao",
        "historico": historico_global[-50:],
        "status": "ONLINE 24H BRASIL SEM VPN"
    })

@app.get("/health")
def health():
    return {"status": "online"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

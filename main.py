from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os, requests

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_index():
    try:
        with open("index.html","r",encoding="utf-8") as f: return f.read()
    except: return "<h1>KC V13</h1>"

@app.get("/", response_class=HTMLResponse)
async def home(): return get_index()

@app.get("/api/real")
def real():
    try:
        # Tenta 3 APIs diferentes da Blaze
        headers = {"User-Agent":"Mozilla/5.0","Origin":"https://blaze.com","Referer":"https://blaze.com/pt/games/double"}
        r = requests.get("https://blaze.com/api/singleplayer-originals/originals/roulette/recent", headers=headers, timeout=10)
        if r.status_code==200:
            data = r.json()
            # Converte pro formato do painel
            out=[]
            for x in data[:50]:
                out.append({"cor": x.get("color",1), "num": x.get("roll",0)})
            return {"ok":True, "historico": out[::-1]}
    except Exception as e:
        print(e)
    return {"ok":False}

if __name__=="__main__":
    import uvicorn
    port=int(os.environ.get("PORT",10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, time

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# memória
DADOS = {"historico": [], "update": 0}

class Push(BaseModel):
    historico: list
    secret: str

@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open("index.html","r",encoding="utf-8") as f: return f.read()
    except: return "KC V13"

@app.post("/api/push")
def push(p: Push):
    if p.secret!= "kc815": return {"ok":False}
    DADOS["historico"] = p.historico[-50:]
    DADOS["update"] = int(time.time())
    return {"ok":True}

@app.get("/api/real")
def real():
    return {"ok": True if DADOS["historico"] else False, "historico": DADOS["historico"], "age": int(time.time())-DADOS["update"]}

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT",10000)))

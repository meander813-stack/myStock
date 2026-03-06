# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import market, portfolio, watchlist
from database import init_db

app = FastAPI(title="Stock App API")

# CORS: 로컬 개발 + Vercel 배포 URL 모두 허용
# Railway 환경변수 ALLOWED_ORIGINS 에 Vercel URL 추가할 것
# 예) https://your-app.vercel.app,http://localhost:5173
raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
)
origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
def root():
    return {"status": "ok", "message": "Stock App API running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

app.include_router(market.router,    prefix="/api/market",    tags=["market"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

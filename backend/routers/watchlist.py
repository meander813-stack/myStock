# routers/watchlist.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pykrx import stock
from database import get_conn
from datetime import datetime, timedelta
import time

router = APIRouter()

def get_today():
    now = datetime.now()
    if now.hour < 9:
        now -= timedelta(days=1)
    while now.weekday() >= 5:
        now -= timedelta(days=1)
    return now.strftime("%Y%m%d")

def get_prev(days=5):
    d = datetime.strptime(get_today(), "%Y%m%d") - timedelta(days=days)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d.strftime("%Y%m%d")

class WatchItem(BaseModel):
    name:   str
    ticker: str
    market: str = "KRX"

@router.get("")
def get_watchlist():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM watchlist ORDER BY id").fetchall()
    conn.close()

    items = [dict(r) for r in rows]
    td, pd = get_today(), get_prev()

    for item in items:
        try:
            df = stock.get_market_ohlcv(pd, td, item["ticker"])
            if not df.empty:
                current = float(df.iloc[-1]["종가"])
                prev    = float(df.iloc[-2]["종가"]) if len(df) > 1 else current
                chg     = current - prev
                rate    = chg / prev * 100 if prev else 0
                item.update({
                    "price":      current,
                    "change":     round(chg, 0),
                    "changeRate": round(rate, 2),
                    "up":         chg >= 0,
                })
            time.sleep(0.05)
        except:
            item.update({"price": None, "change": 0, "changeRate": 0, "up": False})

    return {"items": items}

@router.post("")
def add_watchlist(item: WatchItem):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO watchlist (name,ticker,market) VALUES (?,?,?)",
            (item.name, item.ticker, item.market)
        )
        conn.commit()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()

@router.delete("/{id}")
def delete_watchlist(id: int):
    conn = get_conn()
    conn.execute("DELETE FROM watchlist WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}

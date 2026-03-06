# routers/portfolio.py
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

class PortfolioItem(BaseModel):
    name:      str
    ticker:    str
    qty:       int
    avg_price: float

@router.get("")
def get_portfolio():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM portfolio ORDER BY id").fetchall()
    conn.close()

    items = [dict(r) for r in rows]
    td, pd = get_today(), get_prev()

    total_gain = total_value = total_invested = 0

    for item in items:
        try:
            df = stock.get_market_ohlcv(pd, td, item["ticker"])
            if not df.empty:
                current = float(df.iloc[-1]["종가"])
                prev    = float(df.iloc[-2]["종가"]) if len(df) > 1 else current
            else:
                current = prev = item["avg_price"]
            time.sleep(0.05)
        except:
            current = prev = item["avg_price"]

        chg      = current - prev
        chg_rate = chg / prev * 100 if prev else 0
        gain     = (current - item["avg_price"]) * item["qty"]
        gain_rate = (current - item["avg_price"]) / item["avg_price"] * 100 if item["avg_price"] else 0
        value    = current * item["qty"]
        invested = item["avg_price"] * item["qty"]

        item.update({
            "current_price": current,
            "change":        round(chg, 0),
            "change_rate":   round(chg_rate, 2),
            "gain":          round(gain, 0),
            "gain_rate":     round(gain_rate, 2),
            "value":         round(value, 0),
            "invested":      round(invested, 0),
        })
        total_gain     += gain
        total_value    += value
        total_invested += invested

    return {
        "items":          items,
        "total_gain":     round(total_gain, 0),
        "total_value":    round(total_value, 0),
        "total_invested": round(total_invested, 0),
        "overall_rate":   round(total_gain / total_invested * 100, 2) if total_invested else 0,
        "timestamp":      datetime.now().strftime("%H:%M"),
    }

@router.post("")
def add_portfolio(item: PortfolioItem):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO portfolio (name,ticker,qty,avg_price) VALUES (?,?,?,?)",
            (item.name, item.ticker, item.qty, item.avg_price)
        )
        conn.commit()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()

@router.put("/{id}")
def update_portfolio(id: int, item: PortfolioItem):
    conn = get_conn()
    conn.execute(
        "UPDATE portfolio SET name=?,ticker=?,qty=?,avg_price=? WHERE id=?",
        (item.name, item.ticker, item.qty, item.avg_price, id)
    )
    conn.commit()
    conn.close()
    return {"ok": True}

@router.delete("/{id}")
def delete_portfolio(id: int):
    conn = get_conn()
    conn.execute("DELETE FROM portfolio WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}

# routers/market.py
from fastapi import APIRouter
from pykrx import stock
from datetime import datetime, timedelta
import requests, time

router = APIRouter()

# ── 날짜 헬퍼 ─────────────────────────────────────────────────────────────────

def get_today():
    """장 시작 전(09시 이전)이면 전 거래일 반환, 주말 건너뜀"""
    now = datetime.now()
    if now.hour < 9:
        now -= timedelta(days=1)
    while now.weekday() >= 5:
        now -= timedelta(days=1)
    return now.strftime("%Y%m%d")

def get_prev(days=5):
    """충분한 이전 거래일 (데이터 보장용)"""
    d = datetime.strptime(get_today(), "%Y%m%d") - timedelta(days=days)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d.strftime("%Y%m%d")

# ── 지수 ──────────────────────────────────────────────────────────────────────

@router.get("/indices")
def get_indices():
    td, pd = get_today(), get_prev(10)
    results = []

    for name in ["KOSPI", "KOSDAQ", "KOSPI200"]:
        try:
            df = stock.get_index_ohlcv(pd, td, name)
            if df.empty:
                raise ValueError("empty")
            row  = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else row
            close = float(row["종가"])
            chg   = round(close - float(prev["종가"]), 2)
            rate  = round(chg / float(prev["종가"]) * 100, 2)
            results.append({
                "name":       name,
                "value":      f"{close:,.2f}",
                "change":     chg,
                "changeRate": rate,
                "up":         chg >= 0,
            })
        except Exception as e:
            results.append({
                "name": name, "value": "N/A",
                "change": 0, "changeRate": 0, "up": False, "error": str(e)
            })

    return {"indices": results, "timestamp": datetime.now().strftime("%H:%M")}

# ── 환율 ──────────────────────────────────────────────────────────────────────

@router.get("/fx")
def get_fx():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = r.json()
        krw_usd = data["rates"]["KRW"]
        krw_eur = krw_usd / data["rates"]["EUR"]
        return {
            "fx": [
                {"name": "원/달러", "value": f"{krw_usd:,.2f}", "changeRate": 0.0, "up": False},
                {"name": "원/유로", "value": f"{krw_eur:,.2f}", "changeRate": 0.0, "up": True},
            ]
        }
    except Exception as e:
        return {"fx": [], "error": str(e)}

# ── 랭킹 ──────────────────────────────────────────────────────────────────────

@router.get("/ranking")
def get_ranking(type: str = "거래대금", limit: int = 5):
    td, pd = get_today(), get_prev(3)
    try:
        df = stock.get_market_ohlcv(td, market="ALL")
        if df.empty:
            df = stock.get_market_ohlcv(pd, market="ALL")
        if df.empty:
            return {"topStocks": [], "error": "데이터 없음"}

        df = df.reset_index()

        col_map = {"거래대금": "거래대금", "상승률": "등락률", "거래량": "거래량"}
        sort_col = col_map.get(type, "거래대금")

        if sort_col not in df.columns:
            return {"topStocks": [], "error": f"컬럼 없음: {sort_col}"}

        df_sorted = df.sort_values(sort_col, ascending=False).head(limit)

        results = []
        for i, (_, row) in enumerate(df_sorted.iterrows()):
            ticker = str(row.get("티커", row.name))
            try:
                name = stock.get_market_ticker_name(ticker)
            except:
                name = ticker
            price    = float(row.get("종가", 0))
            chg_rate = float(row.get("등락률", 0))
            results.append({
                "rank":       i + 1,
                "name":       name,
                "ticker":     ticker,
                "price":      f"{price:,.0f}",
                "changeRate": round(chg_rate, 2),
                "up":         chg_rate >= 0,
            })
            time.sleep(0.05)

        return {"topStocks": results}

    except Exception as e:
        return {"topStocks": [], "error": str(e)}

# ── 단일 종목 시세 ────────────────────────────────────────────────────────────

@router.get("/price/{ticker}")
def get_price(ticker: str):
    td, pd = get_today(), get_prev(5)
    try:
        df = stock.get_market_ohlcv(pd, td, ticker)
        if df.empty:
            return {"ticker": ticker, "price": None}
        row   = df.iloc[-1]
        prev  = df.iloc[-2] if len(df) > 1 else row
        close = float(row["종가"])
        chg   = round(close - float(prev["종가"]), 0)
        rate  = round(chg / float(prev["종가"]) * 100, 2)
        return {
            "ticker": ticker, "price": close,
            "change": chg, "changeRate": rate, "up": chg >= 0,
        }
    except Exception as e:
        return {"ticker": ticker, "price": None, "error": str(e)}

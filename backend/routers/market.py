# routers/market.py
from fastapi import APIRouter
from bs4 import BeautifulSoup
from datetime import datetime
import requests, time, re

router = APIRouter()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://finance.naver.com/",
}

# ── 유틸 ──────────────────────────────────────────────────────────────────────
def to_num(s):
    s = re.sub(r"[^\d.]", "", s.strip())
    return float(s) if s else 0.0

def fetch_yahoo(symbol):
    r = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
        headers={"User-Agent": "Mozilla/5.0"},
        params={"interval": "1d", "range": "5d"}, timeout=8)
    r.raise_for_status()
    closes = [c for c in r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"] if c]
    cur  = closes[-1]
    prev = closes[-2] if len(closes) >= 2 else cur
    chg  = round(cur - prev, 2)
    rate = round(chg / prev * 100, 2) if prev else 0
    return cur, chg, rate

# ── 스크래퍼 ──────────────────────────────────────────────────────────────────
def scrape_quant(sosok):
    """거래대금/거래량 페이지: [2]현재가 [4]등락률 [5]거래대금 [6]거래량"""
    url = f"https://finance.naver.com/sise/sise_quant.naver?sosok={sosok}"
    r   = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "lxml")
    table = soup.select_one("table.type_2")
    if not table:
        return []
    rows = []
    for tr in table.select("tr"):
        tds = tr.select("td")
        a   = tr.select_one("td a")
        if not a or len(tds) < 7:
            continue
        name = a.text.strip()
        if not name:
            continue
        price    = to_num(tds[2].text)
        rate_str = tds[4].text.strip()
        rate_m   = re.search(r"[+-]?\d+\.?\d*", rate_str)
        rate_val = float(rate_m.group()) if rate_m else 0.0
        is_up    = "+" in rate_str or "상승" in rate_str or "상한가" in rate_str
        amt      = to_num(tds[5].text)
        vol      = to_num(tds[6].text)
        href     = a.get("href", "")
        ticker   = re.search(r"code=(\w+)", href)
        ticker   = ticker.group(1) if ticker else ""
        rows.append({"name": name, "ticker": ticker,
                     "price": price, "price_str": f"{price:,.0f}",
                     "changeRate": rate_val, "up": is_up,
                     "amt": amt, "vol": vol})
    return rows

def scrape_rise(sosok):
    """상승률 페이지: [2]현재가 [4]등락률"""
    url  = f"https://finance.naver.com/sise/sise_rise.naver?sosok={sosok}"
    r    = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "lxml")
    table = soup.select_one("table.type_2")
    if not table:
        return []
    rows = []
    for tr in table.select("tr"):
        tds = tr.select("td")
        a   = tr.select_one("td a")
        if not a or len(tds) < 5:
            continue
        name = a.text.strip()
        if not name:
            continue
        price    = to_num(tds[2].text)
        rate_str = tds[4].text.strip()
        rate_m   = re.search(r"[+-]?\d+\.?\d*", rate_str)
        rate_val = float(rate_m.group()) if rate_m else 0.0
        is_up    = "+" in rate_str or "상승" in rate_str or "상한가" in rate_str
        href     = a.get("href", "")
        ticker   = re.search(r"code=(\w+)", href)
        ticker   = ticker.group(1) if ticker else ""
        rows.append({"name": name, "ticker": ticker,
                     "price": price, "price_str": f"{price:,.0f}",
                     "changeRate": rate_val, "up": is_up,
                     "amt": 0, "vol": 0})
    return rows

def make_top(items, sort_key, limit):
    items.sort(key=lambda x: x[sort_key], reverse=True)
    return [
        {"rank": i+1, "name": s["name"], "ticker": s["ticker"],
         "price": s["price_str"], "changeRate": s["changeRate"], "up": s["up"]}
        for i, s in enumerate(items[:limit])
    ]

# ── 지수 ──────────────────────────────────────────────────────────────────────
@router.get("/indices")
def get_indices():
    results = []
    for name, sym in [("KOSPI","^KS11"),("KOSDAQ","^KQ11"),("KOSPI200","^KS200")]:
        try:
            cur, chg, rate = fetch_yahoo(sym)
            results.append({"name": name, "value": f"{cur:,.2f}",
                            "change": chg, "changeRate": rate, "up": chg >= 0})
        except Exception as e:
            results.append({"name": name, "value": "N/A",
                            "change": 0, "changeRate": 0, "up": False, "error": str(e)})
        time.sleep(0.2)
    return {"indices": results, "timestamp": datetime.now().strftime("%H:%M")}

# ── 환율 ──────────────────────────────────────────────────────────────────────
@router.get("/fx")
def get_fx():
    results = []
    for name, sym in [("원/달러","KRW=X"),("원/유로","EURKRW=X")]:
        try:
            cur, chg, rate = fetch_yahoo(sym)
            results.append({"name": name, "value": f"{cur:,.2f}",
                            "changeRate": rate, "up": chg >= 0})
        except:
            results.append({"name": name, "value": "N/A", "changeRate": 0, "up": False})
        time.sleep(0.2)
    return {"fx": results}

# ── 랭킹 ──────────────────────────────────────────────────────────────────────
@router.get("/ranking")
def get_ranking(type: str = "거래대금", limit: int = 5):
    try:
        if type == "거래대금":
            kospi  = scrape_quant("0")
            time.sleep(0.4)
            kosdaq = scrape_quant("1")
            return {"topStocks": make_top(kospi + kosdaq, "amt", limit)}

        elif type == "거래량":
            kospi  = scrape_quant("0")
            time.sleep(0.4)
            kosdaq = scrape_quant("1")
            return {"topStocks": make_top(kospi + kosdaq, "vol", limit)}

        elif type == "상승률":
            kospi  = scrape_rise("0")
            time.sleep(0.4)
            kosdaq = scrape_rise("1")
            return {"topStocks": make_top(kospi + kosdaq, "changeRate", limit)}

        elif type == "52주신고가":
            # 네이버 52주신고가 전용 URL 없음 → 상승률 상위로 대체
            kospi  = scrape_rise("0")
            time.sleep(0.4)
            kosdaq = scrape_rise("1")
            return {"topStocks": make_top(kospi + kosdaq, "changeRate", limit)}

        return {"topStocks": []}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"topStocks": [], "error": str(e)}

# ── 단일 종목 ─────────────────────────────────────────────────────────────────
@router.get("/price/{ticker}")
def get_price(ticker: str):
    sym = ticker if "." in ticker else f"{ticker}.KS"
    try:
        cur, chg, rate = fetch_yahoo(sym)
        return {"ticker": ticker, "price": cur,
                "change": chg, "changeRate": rate, "up": chg >= 0}
    except Exception as e:
        return {"ticker": ticker, "price": None, "error": str(e)}

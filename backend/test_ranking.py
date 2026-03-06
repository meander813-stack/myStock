# test_ranking.py
import requests, re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://finance.naver.com/",
}

def to_num(s):
    s = re.sub(r"[^\d.]", "", s.strip())
    return float(s) if s else 0.0

def scrape_quant(sosok):
    url = f"https://finance.naver.com/sise/sise_quant.naver?sosok={sosok}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "lxml")
    table = soup.select_one("table.type_2")
    result = []
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
        amt      = to_num(tds[5].text)
        vol      = to_num(tds[6].text)
        href     = a.get("href","")
        ticker   = re.search(r"code=(\w+)", href)
        ticker   = ticker.group(1) if ticker else ""
        result.append({"name":name,"ticker":ticker,"price":price,
                        "changeRate":rate_val,"amt":amt,"vol":vol})
    return result

def scrape_rise(sosok):
    url = f"https://finance.naver.com/sise/sise_rise.naver?sosok={sosok}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "lxml")
    table = soup.select_one("table.type_2")
    result = []
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
        href     = a.get("href","")
        ticker   = re.search(r"code=(\w+)", href)
        ticker   = ticker.group(1) if ticker else ""
        result.append({"name":name,"ticker":ticker,"price":price,
                        "changeRate":rate_val,"amt":0,"vol":0})
    return result

print("=== 거래대금 상위 5 (KOSPI+KOSDAQ) ===")
kospi  = scrape_quant("0")
kosdaq = scrape_quant("1")
print(f"KOSPI {len(kospi)}개, KOSDAQ {len(kosdaq)}개")
combined = kospi + kosdaq
combined.sort(key=lambda x: x["amt"], reverse=True)
for i, s in enumerate(combined[:5]):
    print(f"{i+1}. {s['name']} | 거래대금: {s['amt']:,.0f} | 등락률: {s['changeRate']}%")

print()
print("=== 거래량 상위 5 (KOSPI+KOSDAQ) ===")
combined2 = kospi + kosdaq
combined2.sort(key=lambda x: x["vol"], reverse=True)
for i, s in enumerate(combined2[:5]):
    print(f"{i+1}. {s['name']} | 거래량: {s['vol']:,.0f} | 등락률: {s['changeRate']}%")

print()
print("=== 상승률 상위 5 (KOSPI+KOSDAQ) ===")
kospi_r  = scrape_rise("0")
kosdaq_r = scrape_rise("1")
print(f"KOSPI {len(kospi_r)}개, KOSDAQ {len(kosdaq_r)}개")
combined3 = kospi_r + kosdaq_r
combined3.sort(key=lambda x: x["changeRate"], reverse=True)
for i, s in enumerate(combined3[:5]):
    print(f"{i+1}. {s['name']} | 등락률: {s['changeRate']}%")

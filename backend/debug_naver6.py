# debug_naver6.py
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}

mobile_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    "Referer": "https://m.stock.naver.com/",
}

urls = [
    ("거래량 네이버API", "https://m.stock.naver.com/api/stocks/ranks/KOSPI?pageSize=5&page=1&rankType=ACML_VOL", mobile_headers),
    ("상승률 네이버API", "https://m.stock.naver.com/api/stocks/ranks/KOSPI?pageSize=5&page=1&rankType=FLUC_TP_UP", mobile_headers),
    ("거래대금 네이버API","https://m.stock.naver.com/api/stocks/ranks/KOSPI?pageSize=5&page=1&rankType=ACML_TRDE_PBMN", mobile_headers),
    ("52주신고가 네이버API","https://m.stock.naver.com/api/stocks/ranks/KOSPI?pageSize=5&page=1&rankType=NEAR_52WEEK_HIGH", mobile_headers),
    ("거래량 PC",  "https://finance.naver.com/sise/sise_quant.naver?sosok=1", headers),
    ("52주 PC v1", "https://finance.naver.com/sise/sise_fluctuation.naver?sosok=0&page=1", headers),
    ("52주 PC v2", "https://finance.naver.com/sise/sise_fluctuation.naver", headers),
]

for label, url, h in urls:
    try:
        r = requests.get(url, headers=h, timeout=8)
        print(f"\n[{label}] status={r.status_code}")
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"  ✅ JSON: {str(data)[:300]}")
            except:
                soup = BeautifulSoup(r.text, "lxml")
                table = soup.select_one("table.type_2")
                if table:
                    rows = [tr for tr in table.select("tr") if tr.select_one("td a")]
                    if rows:
                        name = rows[0].select_one("td a").text.strip()
                        tds = [td.text.strip() for td in rows[0].select("td")][:6]
                        print(f"  ✅ HTML: {name} | {tds}")
                else:
                    print(f"  내용: {r.text[:150]}")
    except Exception as e:
        print(f"  에러: {e}")

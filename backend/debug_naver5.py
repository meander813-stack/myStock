# debug_naver5.py
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}

urls = [
    ("52주 a", "https://finance.naver.com/sise/sise_high52.naver"),
    ("52주 b", "https://finance.naver.com/sise/sise_high52.naver?sosok=0&page=1"),
    ("52주 c", "https://finance.naver.com/sise/sise_high52.naver?page=1"),
    ("52주 d", "https://finance.naver.com/sise/item/sise_high52.naver"),
    ("52주 e", "https://m.stock.naver.com/api/stock/52weekHigh/KOSPI"),
    ("52주 f", "https://finance.naver.com/sise/sise_high52.nhn"),
    ("52주 g", "https://finance.naver.com/sise/sise_high52.nhn?sosok=0"),
]

for label, url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=8)
        print(f"{label} status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 500:
            soup = BeautifulSoup(r.text, "lxml")
            table = soup.select_one("table.type_2")
            if table:
                rows = [tr for tr in table.select("tr") if tr.select_one("td a")]
                if rows:
                    name = rows[0].select_one("td a").text.strip()
                    tds  = [td.text.strip() for td in rows[0].select("td")][:6]
                    print(f"  ✅ 데이터: {name} | {tds}")
            else:
                # JSON 응답인지 확인
                try:
                    data = r.json()
                    print(f"  ✅ JSON: {str(data)[:200]}")
                except:
                    print(f"  내용 앞부분: {r.text[:200]}")
    except Exception as e:
        print(f"  에러: {e}")

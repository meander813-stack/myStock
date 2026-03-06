# debug_naver4.py
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}

urls = [
    ("거래량 a", "https://finance.naver.com/sise/sise_trading.naver"),
    ("거래량 b", "https://finance.naver.com/sise/sise_volumn.naver?sosok=0"),
    ("거래량 c", "https://finance.naver.com/sise/sise_volume.naver?sosok=0"),
    ("거래량 d", "https://finance.naver.com/sise/sise_quant.naver?sosok=0"),
    ("52주 a",   "https://finance.naver.com/sise/sise_high52.naver?sosok=0"),
    ("52주 b",   "https://finance.naver.com/sise/sise_week52.naver"),
    ("52주 c",   "https://finance.naver.com/sise/sise_high52.naver?sosok=1"),
    ("52주 d",   "https://finance.naver.com/sise/sise_new.naver"),
]

for label, url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, "lxml")
        table = soup.select_one("table.type_2")
        if table:
            rows = [tr for tr in table.select("tr") if tr.select_one("td a")]
            if rows:
                first = rows[0]
                name = first.select_one("td a").text.strip()
                tds  = [td.text.strip() for td in first.select("td")][:6]
                print(f"✅ {label}: {name} | {tds}")
            else:
                print(f"⚠️  {label}: 테이블 있지만 데이터 없음")
        else:
            print(f"❌ {label}: table.type_2 없음 (status={r.status_code})")
    except Exception as e:
        print(f"❌ {label}: {e}")

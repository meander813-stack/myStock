# debug_naver3.py
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}

def parse_table(url, label):
    print(f"=== {label} ({url}) ===")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        table = soup.select_one("table.type_2")
        if not table:
            print("  table.type_2 없음")
            return

        # 헤더 확인
        headers_row = table.select("thead th") or table.select("tr th")
        print(f"  헤더: {[h.text.strip() for h in headers_row]}")

        # 데이터 행
        count = 0
        for row in table.select("tr"):
            tds = row.select("td")
            if len(tds) < 3:
                continue
            name_tag = row.select_one("td a")
            if not name_tag:
                continue
            name = name_tag.text.strip()
            if not name:
                continue
            # 전체 td 텍스트 출력
            td_texts = [td.text.strip() for td in tds]
            print(f"  {count+1}. {name} | tds: {td_texts[:8]}")
            count += 1
            if count >= 3:
                break
    except Exception as e:
        print(f"  에러: {e}")
    print()

# 4가지 URL 테스트
parse_table("https://finance.naver.com/sise/sise_quant.naver",   "거래대금")
parse_table("https://finance.naver.com/sise/sise_rise.naver",    "상승률")
parse_table("https://finance.naver.com/sise/sise_volume.naver",  "거래량 v1")
parse_table("https://finance.naver.com/sise/sise_volumn.naver",  "거래량 v2")
parse_table("https://finance.naver.com/sise/sise_high52.naver",  "52주신고가 v1")
parse_table("https://finance.naver.com/sise/sise_new52.naver",   "52주신고가 v2")

# debug_naver2.py
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}

def parse_naver_ranking(url, label):
    print(f"=== {label} ===")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        # 테이블 찾기
        table = soup.select_one("table.type_2")
        if not table:
            print("table.type_2 없음")
            # 다른 테이블 찾기
            tables = soup.find_all("table")
            print(f"전체 테이블 수: {len(tables)}")
            for i, t in enumerate(tables[:3]):
                print(f"테이블[{i}] class: {t.get('class')}")
            return

        rows = table.select("tr")
        count = 0
        for row in rows:
            cols = row.select("td")
            if len(cols) < 4:
                continue
            name_tag = row.select_one("a")
            if not name_tag:
                continue
            name = name_tag.text.strip()
            price = cols[1].text.strip() if len(cols) > 1 else ""
            rate  = cols[2].text.strip() if len(cols) > 2 else ""
            if name:
                print(f"  {count+1}. {name} | 현재가: {price} | 등락률: {rate}")
                count += 1
            if count >= 5:
                break
    except Exception as e:
        print(f"에러: {e}")
    print()

# 거래대금
parse_naver_ranking("https://finance.naver.com/sise/sise_quant.naver", "거래대금 상위")

# 상승률
parse_naver_ranking("https://finance.naver.com/sise/sise_rise.naver", "상승률 상위")

# 거래량
parse_naver_ranking("https://finance.naver.com/sise/sise_volume.naver", "거래량 상위")

# 52주 신고가
parse_naver_ranking("https://finance.naver.com/sise/sise_high52.naver", "52주 신고가")

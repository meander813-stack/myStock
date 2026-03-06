# debug_naver.py
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}

# 1. 네이버 거래대금 상위
print("=== 네이버 거래대금 상위 ===")
try:
    url = "https://finance.naver.com/sise/sise_quant.naver"
    r = requests.get(url, headers=headers, timeout=10)
    print(f"상태코드: {r.status_code}")
    print(r.text[:500])
except Exception as e:
    print(f"에러: {e}")

print()

# 2. 네이버 상승률 상위
print("=== 네이버 상승률 상위 ===")
try:
    url = "https://finance.naver.com/sise/sise_rise.naver"
    r = requests.get(url, headers=headers, timeout=10)
    print(f"상태코드: {r.status_code}")
    print(r.text[:500])
except Exception as e:
    print(f"에러: {e}")

print()

# 3. 네이버 JSON API
print("=== 네이버 JSON API ===")
try:
    url = "https://finance.naver.com/sise/sise_rise_day.naver?sosok=0"
    r = requests.get(url, headers=headers, timeout=10)
    print(f"상태코드: {r.status_code}")
    print(r.text[:500])
except Exception as e:
    print(f"에러: {e}")

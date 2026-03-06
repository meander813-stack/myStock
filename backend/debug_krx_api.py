# debug_krx_api.py
import requests
from datetime import datetime, timedelta

def get_today():
    now = datetime.now()
    if now.hour < 9:
        now -= timedelta(days=1)
    while now.weekday() >= 5:
        now -= timedelta(days=1)
    return now.strftime("%Y%m%d")

td = get_today()
print(f"오늘: {td}\n")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "http://data.krx.co.kr/",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

# 1. KRX 거래대금 상위
print("=== KRX 거래대금 상위 ===")
try:
    payload = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT01901",
        "trdDd": td,
        "mktId": "ALL",
        "adjStkPrc_check": "Y",
    }
    r = requests.post(
        "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd",
        data=payload, headers=headers, timeout=10
    )
    data = r.json()
    print(f"키: {list(data.keys())}")
    if "OutBlock_1" in data:
        rows = data["OutBlock_1"][:3]
        for row in rows:
            print(row)
except Exception as e:
    print(f"에러: {e}")

print()

# 2. KRX 등락률 상위
print("=== KRX 상승률 상위 ===")
try:
    payload = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT01501",
        "trdDd": td,
        "mktId": "ALL",
        "adjStkPrc_check": "Y",
    }
    r = requests.post(
        "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd",
        data=payload, headers=headers, timeout=10
    )
    data = r.json()
    print(f"키: {list(data.keys())}")
    if "OutBlock_1" in data:
        rows = data["OutBlock_1"][:3]
        for row in rows:
            print(row)
except Exception as e:
    print(f"에러: {e}")

# 📈 주식 앱

> **GitLab** 소스 관리 · **Railway** 백엔드 · **Vercel** 프론트엔드

---

## 🗂️ 프로젝트 구조

```
stock-app/
├── .gitlab-ci.yml          ← GitLab CI (자동 빌드 검사)
├── .gitignore
├── backend/                ← Python FastAPI (Railway 배포)
│   ├── main.py
│   ├── database.py
│   ├── requirements.txt
│   ├── Procfile
│   ├── railway.toml
│   └── routers/
│       ├── market.py       ← KOSPI/KOSDAQ/환율/랭킹
│       ├── portfolio.py    ← 보유종목 CRUD + 실시간 시세
│       └── watchlist.py    ← 관심종목 CRUD + 실시간 시세
└── frontend/               ← React + Vite (Vercel 배포)
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── vercel.json
    └── src/
        ├── main.jsx
        └── App.jsx
```

---

## 🚀 최초 셋업 (한 번만)

### 1단계 — GitLab 저장소 생성 & 푸시

```bash
# 프로젝트 폴더에서
git init
git remote add origin https://gitlab.com/YOUR_USERNAME/stock-app.git
git add .
git commit -m "feat: 초기 프로젝트 세팅"
git push -u origin main
```

---

### 2단계 — Railway 백엔드 배포

1. [railway.app](https://railway.app) 접속 → **Start a New Project**
2. **Deploy from GitLab repo** 선택 → `stock-app` 저장소 연결
3. **Root Directory** → `backend` 로 설정
4. 배포 완료 후 **Settings → Domains** → 도메인 생성
   - 예) `https://stock-app-backend.railway.app`
5. **Variables** 탭에서 환경변수 추가:
   ```
   ALLOWED_ORIGINS = https://YOUR-APP.vercel.app,http://localhost:5173
   ```

---

### 3단계 — Vercel 프론트엔드 배포

1. [vercel.com](https://vercel.com) 접속 → **Add New Project**
2. **Import Git Repository** → GitLab 연결 → `stock-app` 선택
3. **Root Directory** → `frontend` 로 설정
4. **Environment Variables** 추가:
   ```
   VITE_API_URL = https://stock-app-backend.railway.app
   ```
   (Railway에서 생성된 실제 URL로 교체)
5. **Deploy** 클릭 → 완료!

---

### 4단계 — Railway CORS 업데이트

Vercel 배포 후 받은 URL을 Railway 환경변수에 추가:
```
ALLOWED_ORIGINS = https://stock-app-xyz.vercel.app,http://localhost:5173
```

---

## 🔄 이후 개발 흐름 (매일)

```bash
# 기능 개발
git checkout -b feat/새기능이름

# 작업 후 커밋
git add .
git commit -m "feat: 관심종목 정렬 기능 추가"
git push origin feat/새기능이름

# GitLab에서 Merge Request → main 에 머지하면
# → Railway & Vercel 자동 재배포! 🎉
```

---

## 🌐 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /api/market/indices | KOSPI, KOSDAQ, KOSPI200 |
| GET | /api/market/fx | 원/달러, 원/유로 |
| GET | /api/market/ranking?type=거래대금 | 상위 랭킹 종목 |
| GET | /api/portfolio | 보유종목 + 실시간 손익 |
| POST | /api/portfolio | 종목 추가 |
| PUT | /api/portfolio/{id} | 종목 수정 |
| DELETE | /api/portfolio/{id} | 종목 삭제 |
| GET | /api/watchlist | 관심종목 + 실시간 시세 |
| POST | /api/watchlist | 관심종목 추가 |
| DELETE | /api/watchlist/{id} | 관심종목 삭제 |

---

## 💡 로컬 개발

```bash
# 백엔드
cd backend
pip install -r requirements.txt
python main.py          # → localhost:8000

# 프론트엔드 (별도 터미널)
cd frontend
npm install
npm run dev             # → localhost:5173
                        # vite.config.js 프록시로 백엔드 자동 연결
```

---

## ⚠️ 주의사항

- `.env` 파일은 절대 GitLab에 커밋하지 말 것 (`.gitignore` 에 포함됨)
- Railway 무료 플랜은 월 $5 크레딧 제공
- pykrx는 장 시간(09:00~15:30) 기준 실시간 데이터

# database.py
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "stock_app.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            ticker      TEXT    NOT NULL UNIQUE,
            qty         INTEGER NOT NULL DEFAULT 0,
            avg_price   REAL    NOT NULL DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            ticker      TEXT    NOT NULL UNIQUE,
            market      TEXT    NOT NULL DEFAULT 'KRX',
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # 기본 보유 종목 시딩
    c.execute("SELECT COUNT(*) FROM portfolio")
    if c.fetchone()[0] == 0:
        seeds = [
            ("KODEX AI반도체",        "266920", 1830, 29073),
            ("PLUS 글로벌HBM반도체",  "329200", 165,  54166),
            ("TIGER K방산&우주",      "382480", 97,   37365),
            ("SOL 조선TOP3플러스",    "457690", 555,  26000),
            ("KODEX AI전력핵심설비",  "448510", 784,  20204),
        ]
        c.executemany(
            "INSERT OR IGNORE INTO portfolio (name,ticker,qty,avg_price) VALUES (?,?,?,?)",
            seeds
        )

    # 기본 관심 종목 시딩
    c.execute("SELECT COUNT(*) FROM watchlist")
    if c.fetchone()[0] == 0:
        seeds = [
            ("케이뱅크",             "323410", "KOSPI"),
            ("PLUS 글로벌HBM반도체", "329200", "ETF"),
            ("KODEX AI반도체",       "266920", "ETF"),
            ("SOL 조선TOP3플러스",   "457690", "ETF"),
            ("KODEX AI전력핵심설비", "448510", "ETF"),
            ("TIGER K방산&우주",     "382480", "ETF"),
        ]
        c.executemany(
            "INSERT OR IGNORE INTO watchlist (name,ticker,market) VALUES (?,?,?)",
            seeds
        )

    conn.commit()
    conn.close()

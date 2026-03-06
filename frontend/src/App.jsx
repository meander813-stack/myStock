import { useState, useEffect, useCallback } from "react";

// ─── Config ────────────────────────────────────────────────────────────────────
// 로컬: vite.config.js 프록시 → /api = localhost:8000/api
// 배포: Vercel 환경변수 VITE_API_URL = https://xxx.railway.app
const API = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : "/api";

// ─── Theme ────────────────────────────────────────────────────────────────────
const T = {
  bg: "#0A0E1A", surface: "#111827", card: "#161D2E", border: "#1E2A3A",
  accent: "#3B82F6", red: "#EF4444", green: "#10B981",
  text: "#F1F5F9", textMuted: "#64748B", textSub: "#94A3B8", gold: "#F59E0B",
};

// ─── Sparkline ────────────────────────────────────────────────────────────────
function Sparkline({ up, width = 60, height = 24 }) {
  const base = up
    ? [24, 20, 22, 16, 19, 12, 15, 9, 12, 5, 8, 2]
    : [2, 6, 4, 10, 7, 13, 10, 16, 13, 19, 16, 22];
  const max = Math.max(...base), min = Math.min(...base);
  const pts = base.map((v, i) => {
    const x = (i / (base.length - 1)) * width;
    const y = ((v - min) / (max - min || 1)) * height;
    return `${x},${y}`;
  }).join(" ");
  return (
    <svg width={width} height={height} style={{ overflow: "visible" }}>
      <polyline points={pts} fill="none"
        stroke={up ? T.green : T.red} strokeWidth="1.5"
        strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function Skel({ w = "100%", h = 16, r = 6 }) {
  return (
    <div style={{
      width: w, height: h, borderRadius: r,
      background: `linear-gradient(90deg,${T.surface} 25%,${T.card} 50%,${T.surface} 75%)`,
      backgroundSize: "200% 100%", animation: "shimmer 1.4s infinite",
    }} />
  );
}

// ─── useFetch hook ────────────────────────────────────────────────────────────
function useFetch(url, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [ts, setTs] = useState(null);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const r = await fetch(url);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const json = await r.json();
      setData(json);
      setTs(new Date().toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => { load(); }, deps);

  return { data, loading, error, ts, reload: load };
}

// ─── HOME SCREEN ──────────────────────────────────────────────────────────────
function HomeScreen() {
  const [activeTab, setActiveTab] = useState("국내");
  const [rankType, setRankType] = useState("거래대금");
  const [refreshing, setRefreshing] = useState(false);

  const indices = useFetch(`${API}/market/indices`);
  const fx      = useFetch(`${API}/market/fx`);
  const ranking = useFetch(`${API}/market/ranking?type=${rankType}&limit=5`, [rankType]);

  const refreshAll = async () => {
    setRefreshing(true);
    await Promise.all([indices.reload(), fx.reload(), ranking.reload()]);
    setRefreshing(false);
  };

  // 3분 자동 갱신
  useEffect(() => {
    const t = setInterval(refreshAll, 3 * 60 * 1000);
    return () => clearInterval(t);
  }, []);

  const marketTabs = ["국내", "해외", "상품/연금", "자산", "my PICK"];
  const rankTabs   = ["상승률", "거래대금", "거래량", "52주신고가"];

  return (
    <div style={{ padding: "0 0 16px" }}>
      <style>{`
        @keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
        @keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
        @keyframes fadeIn{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
        ::-webkit-scrollbar{display:none}
      `}</style>

      {/* Header */}
      <div style={{ padding: "16px 20px 12px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 18, fontWeight: 700, color: T.text }}>노혜진님</span>
          <span style={{ fontSize: 11, fontWeight: 600, color: T.gold, border: `1px solid ${T.gold}`, borderRadius: 4, padding: "1px 6px" }}>우대</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {indices.ts && <span style={{ fontSize: 11, color: T.textMuted }}>{indices.ts} 기준</span>}
          <button onClick={refreshAll} disabled={refreshing} style={{
            background: T.surface, border: `1px solid ${T.border}`, borderRadius: 20,
            padding: "5px 12px", cursor: "pointer", color: T.textSub, fontSize: 12,
            display: "flex", alignItems: "center", gap: 4,
          }}>
            <span style={{ animation: refreshing ? "spin 1s linear infinite" : "none", display: "inline-block" }}>↻</span>
            {refreshing ? "갱신 중" : "새로고침"}
          </button>
        </div>
      </div>

      {/* Market Tabs */}
      <div style={{ padding: "0 20px", display: "flex", gap: 8, marginBottom: 16, overflowX: "auto" }}>
        {marketTabs.map(t => (
          <button key={t} onClick={() => setActiveTab(t)} style={{
            background: activeTab === t ? T.accent : "transparent",
            border: activeTab === t ? "none" : `1px solid ${T.border}`,
            borderRadius: 20, padding: "5px 14px", fontSize: 13, flexShrink: 0,
            color: activeTab === t ? "#fff" : T.textSub, cursor: "pointer",
            fontWeight: activeTab === t ? 600 : 400, transition: "all 0.2s",
          }}>{t}</button>
        ))}
      </div>

      {/* Error banner */}
      {(indices.error || fx.error || ranking.error) && (
        <div style={{
          margin: "0 20px 12px", background: "#450a0a",
          border: `1px solid ${T.red}`, borderRadius: 12, padding: "10px 14px",
          fontSize: 13, color: "#fca5a5", display: "flex", justifyContent: "space-between", alignItems: "center",
        }}>
          <span>⚠️ 백엔드 연결 실패. 서버가 실행 중인지 확인해주세요.</span>
          <button onClick={refreshAll} style={{ background: T.red, border: "none", borderRadius: 8, color: "#fff", padding: "4px 10px", cursor: "pointer", fontSize: 12 }}>재시도</button>
        </div>
      )}

      {/* Index Cards */}
      <div style={{ padding: "0 20px", display: "flex", gap: 10, overflowX: "auto", paddingBottom: 4 }}>
        {indices.loading
          ? [1,2,3].map(i => (
              <div key={i} style={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 14, padding: "12px 16px", minWidth: 150, flexShrink: 0 }}>
                <Skel w={60} h={11} /><div style={{marginTop:8}}><Skel w={100} h={20}/></div><div style={{marginTop:6}}><Skel w={80} h={11}/></div>
              </div>))
          : (indices.data?.indices || []).map(idx => (
              <div key={idx.name} style={{
                background: T.card, border: `1px solid ${T.border}`, borderRadius: 14,
                padding: "12px 16px", minWidth: 150, flexShrink: 0, animation: "fadeIn 0.3s ease",
              }}>
                <div style={{ fontSize: 12, color: T.textMuted, marginBottom: 6 }}>{idx.name}</div>
                <div style={{ fontSize: 19, fontWeight: 700, color: T.text, marginBottom: 4 }}>{idx.value}</div>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <div>
                    <div style={{ fontSize: 12, color: idx.up ? T.green : T.red }}>
                      {idx.up ? "▲" : "▼"} {Math.abs(idx.changeRate).toFixed(2)}%
                    </div>
                    <div style={{ fontSize: 10, color: T.textMuted }}>
                      {idx.up ? "+" : ""}{Number(idx.change).toFixed(2)}
                    </div>
                  </div>
                  <Sparkline up={idx.up} width={55} height={22} />
                </div>
              </div>))}
      </div>

      {/* FX */}
      <div style={{ margin: "12px 20px", background: T.card, border: `1px solid ${T.border}`, borderRadius: 14, padding: "12px 16px" }}>
        {fx.loading
          ? <div style={{ display: "flex", gap: 20 }}><Skel w={130} h={36} /><Skel w={130} h={36} /></div>
          : (
            <div style={{ display: "flex", gap: 0, alignItems: "center", animation: "fadeIn 0.3s ease" }}>
              {(fx.data?.fx || []).map((f, i) => (
                <div key={f.name} style={{ display: "flex", alignItems: "center", gap: 8, flex: 1 }}>
                  {i > 0 && <div style={{ width: 1, height: 30, background: T.border, marginRight: 16 }} />}
                  <span style={{ fontSize: 18 }}>{i === 0 ? "🇺🇸" : "🇪🇺"}</span>
                  <div>
                    <div style={{ fontSize: 11, color: T.textMuted }}>{f.name}</div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: T.text }}>
                      {f.value}
                      {f.changeRate !== 0 && (
                        <span style={{ fontSize: 12, marginLeft: 6, color: f.up ? T.green : T.red }}>
                          {f.up ? "+" : ""}{f.changeRate.toFixed(2)}%
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
      </div>

      {/* Ranking */}
      <div style={{ margin: "0 20px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
          <span style={{ fontSize: 15, fontWeight: 700, color: T.text }}>상위 랭킹종목</span>
          <span style={{ fontSize: 12, color: T.textMuted, background: T.surface, padding: "2px 8px", borderRadius: 10 }}>KRX</span>
        </div>

        <div style={{ display: "flex", gap: 8, marginBottom: 12, overflowX: "auto" }}>
          {rankTabs.map(t => (
            <button key={t} onClick={() => setRankType(t)} style={{
              background: rankType === t ? T.accent : "transparent",
              border: rankType === t ? "none" : `1px solid ${T.border}`,
              borderRadius: 16, padding: "4px 12px", fontSize: 12, flexShrink: 0,
              color: rankType === t ? "#fff" : T.textSub, cursor: "pointer",
              fontWeight: rankType === t ? 600 : 400,
            }}>{t}</button>
          ))}
        </div>

        {ranking.loading
          ? [1,2,3,4,5].map(i => (
              <div key={i} style={{ padding: "14px 0", borderBottom: `1px solid ${T.border}`, display: "flex", justifyContent: "space-between" }}>
                <div style={{ display: "flex", gap: 10, alignItems: "center" }}><Skel w={32} h={32} r={10}/><Skel w={90} h={14}/></div>
                <div><Skel w={70} h={14}/><div style={{marginTop:4}}><Skel w={50} h={12}/></div></div>
              </div>))
          : (ranking.data?.topStocks || []).map(s => (
              <div key={s.rank} style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "13px 0", borderBottom: `1px solid ${T.border}`, animation: "fadeIn 0.3s ease",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <div style={{
                    width: 32, height: 32, borderRadius: 10, background: T.surface,
                    border: `1px solid ${T.border}`, display: "flex", alignItems: "center",
                    justifyContent: "center", fontSize: 13, fontWeight: 700,
                    color: s.rank <= 3 ? T.gold : T.textSub,
                  }}>{s.rank}</div>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: T.text }}>{s.name}</div>
                    <div style={{ fontSize: 11, color: T.textMuted }}>{s.ticker}</div>
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 15, fontWeight: 700, color: T.text }}>{s.price}</div>
                  <div style={{ fontSize: 12, color: s.up ? T.green : T.red }}>
                    {s.up ? "▲" : "▼"} {Math.abs(s.changeRate).toFixed(2)}%
                  </div>
                </div>
              </div>))}

        {!ranking.loading && ranking.data && (
          <div style={{ marginTop: 10, textAlign: "center" }}>
            <span style={{ fontSize: 11, color: T.textMuted }}>📡 pykrx (KRX) 실시간 데이터 • {ranking.ts} 기준</span>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── WATCHLIST SCREEN ─────────────────────────────────────────────────────────
function WatchlistScreen() {
  const { data, loading, error, reload } = useFetch(`${API}/watchlist`);
  const [activeTab, setActiveTab] = useState("최근조회");
  const tabs = ["보유종목", "최근조회", "소나무 포폴", "서학"];

  const remove = async (id) => {
    await fetch(`${API}/watchlist/${id}`, { method: "DELETE" });
    reload();
  };

  return (
    <div style={{ padding: "0 0 16px" }}>
      <div style={{ padding: "16px 20px 0", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 18, fontWeight: 700, color: T.text }}>관심종목</span>
        <button onClick={reload} style={{
          background: T.surface, border: `1px solid ${T.border}`, borderRadius: 20,
          padding: "5px 12px", cursor: "pointer", color: T.textSub, fontSize: 12,
        }}>↻ 새로고침</button>
      </div>

      <div style={{ display: "flex", padding: "12px 20px 0", borderBottom: `1px solid ${T.border}` }}>
        {tabs.map(t => (
          <button key={t} onClick={() => setActiveTab(t)} style={{
            background: "transparent", border: "none", cursor: "pointer",
            padding: "8px 14px", fontSize: 13,
            color: activeTab === t ? T.accent : T.textSub,
            fontWeight: activeTab === t ? 700 : 400,
            borderBottom: activeTab === t ? `2px solid ${T.accent}` : "2px solid transparent",
          }}>{t}</button>
        ))}
      </div>

      {error && (
        <div style={{ margin: "12px 20px", padding: "10px 14px", background: "#450a0a", border: `1px solid ${T.red}`, borderRadius: 12, fontSize: 13, color: "#fca5a5" }}>
          ⚠️ 백엔드 연결 실패
        </div>
      )}

      {loading
        ? [1,2,3,4,5].map(i => (
            <div key={i} style={{ padding: "14px 20px", borderBottom: `1px solid ${T.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                <Skel w={4} h={40} r={2}/><div><Skel w={130} h={14}/><div style={{marginTop:4}}><Skel w={80} h={11}/></div></div>
              </div>
              <Skel w={80} h={36}/>
            </div>))
        : (data?.items || []).map(s => {
            const isUp = (s.changeRate || 0) >= 0;
            return (
              <div key={s.id} style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "12px 20px", borderBottom: `1px solid ${T.border}`, animation: "fadeIn 0.3s ease",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12, flex: 1 }}>
                  <div style={{ width: 4, height: 40, borderRadius: 2, background: isUp ? T.green : T.red, flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: T.text }}>{s.name}</div>
                    <div style={{ fontSize: 11, color: T.textMuted }}>{s.market} · {s.ticker}</div>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <Sparkline up={isUp} width={50} height={22} />
                  <div style={{ textAlign: "right", minWidth: 80 }}>
                    <div style={{ fontSize: 15, fontWeight: 700, color: T.text }}>
                      {s.price ? s.price.toLocaleString() : "-"}
                    </div>
                    <div style={{ fontSize: 12, color: isUp ? T.green : T.red }}>
                      {isUp ? "▲" : "▼"} {Math.abs(s.changeRate || 0).toFixed(2)}%
                    </div>
                  </div>
                  <button onClick={() => remove(s.id)} style={{ background: "none", border: "none", cursor: "pointer", color: T.textMuted, fontSize: 16 }}>✕</button>
                </div>
              </div>
            );
          })}
    </div>
  );
}

// ─── MY / PORTFOLIO SCREEN ────────────────────────────────────────────────────
function MyScreen() {
  const { data, loading, error, reload, ts } = useFetch(`${API}/portfolio`);
  const [tab, setTab] = useState("주식잔고");
  const tabs = ["주식잔고", "실현손익", "평가손익추이", "예수금"];

  return (
    <div style={{ padding: "0 0 16px" }}>
      {/* Account summary card */}
      <div style={{ margin: "16px 20px 0", background: T.card, border: `1px solid ${T.border}`, borderRadius: 16, padding: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
          <span style={{ fontSize: 12, color: T.textMuted }}>7123404645-15 [연금저축 CMA] 노혜진</span>
          <button onClick={reload} style={{ background: "none", border: "none", cursor: "pointer", color: T.textSub, fontSize: 16 }}>↻</button>
        </div>

        {loading
          ? <div style={{ marginTop: 10 }}><Skel h={30} /><div style={{marginTop:8}}><Skel w="60%" h={14}/></div></div>
          : (
            <div style={{ animation: "fadeIn 0.3s ease" }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginTop: 10 }}>
                <span style={{ fontSize: 13, color: T.textSub }}>평가손익</span>
                <span style={{ fontSize: 26, fontWeight: 800, color: T.red }}>
                  {Number(data?.total_gain || 0).toLocaleString()}원
                </span>
                <span style={{ fontSize: 14, fontWeight: 700, color: "#fff", background: T.red, borderRadius: 8, padding: "2px 8px" }}>
                  {data?.overall_rate}%
                </span>
              </div>
              <div style={{ display: "flex", gap: 20, marginTop: 12, paddingTop: 12, borderTop: `1px solid ${T.border}` }}>
                <div>
                  <div style={{ fontSize: 11, color: T.textMuted }}>주식평가금액</div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: T.text }}>{Number(data?.total_value || 0).toLocaleString()}원</div>
                </div>
                <div>
                  <div style={{ fontSize: 11, color: T.textMuted }}>매수원금</div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: T.text }}>{Number(data?.total_invested || 0).toLocaleString()}원</div>
                </div>
              </div>
              {ts && <div style={{ marginTop: 8, fontSize: 11, color: T.textMuted }}>📡 {ts} 기준 실시간</div>}
            </div>
          )}
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", padding: "0 20px", borderBottom: `1px solid ${T.border}`, marginTop: 12 }}>
        {tabs.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            background: "transparent", border: "none", cursor: "pointer",
            padding: "10px 12px", fontSize: 13, whiteSpace: "nowrap",
            color: tab === t ? T.accent : T.textSub,
            fontWeight: tab === t ? 700 : 400,
            borderBottom: tab === t ? `2px solid ${T.accent}` : "2px solid transparent",
          }}>{t}</button>
        ))}
      </div>

      {/* Table header */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 100px 80px", padding: "8px 20px", gap: 8 }}>
        <span style={{ fontSize: 11, color: T.textMuted }}>종목명</span>
        <span style={{ fontSize: 11, color: T.textMuted, textAlign: "right" }}>평가손익 / 수익률</span>
        <span style={{ fontSize: 11, color: T.textMuted, textAlign: "right" }}>보유수량 / 평균금액</span>
      </div>

      {error && (
        <div style={{ margin: "0 20px 12px", padding: "10px 14px", background: "#450a0a", border: `1px solid ${T.red}`, borderRadius: 12, fontSize: 13, color: "#fca5a5" }}>
          ⚠️ 백엔드 연결 실패 — 서버를 확인해주세요
        </div>
      )}

      {loading
        ? [1,2,3,4,5].map(i => (
            <div key={i} style={{ display: "grid", gridTemplateColumns: "1fr 100px 80px", padding: "12px 20px", gap: 8, borderBottom: `1px solid ${T.border}` }}>
              <div><Skel w="80%" h={13}/><div style={{marginTop:4}}><Skel w="50%" h={11}/></div></div>
              <div style={{textAlign:"right"}}><Skel w="90%" h={13}/><div style={{marginTop:4}}><Skel w="60%" h={11}/></div></div>
              <div style={{textAlign:"right"}}><Skel w="80%" h={13}/><div style={{marginTop:4}}><Skel w="70%" h={11}/></div></div>
            </div>))
        : (data?.items || []).map(s => (
            <div key={s.id} style={{
              display: "grid", gridTemplateColumns: "1fr 100px 80px",
              padding: "12px 20px", gap: 8, borderBottom: `1px solid ${T.border}`,
              animation: "fadeIn 0.3s ease",
            }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: T.text }}>{s.name}</div>
                <div style={{ fontSize: 11, color: T.textMuted, marginTop: 2 }}>
                  현재가 {s.current_price?.toLocaleString() || "-"}
                  {s.change_rate !== undefined && (
                    <span style={{ marginLeft: 6, color: s.change_rate >= 0 ? T.green : T.red }}>
                      {s.change_rate >= 0 ? "▲" : "▼"}{Math.abs(s.change_rate).toFixed(2)}%
                    </span>
                  )}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: s.gain >= 0 ? T.red : T.green }}>
                  {s.gain >= 0 ? "+" : ""}{Number(s.gain).toLocaleString()}
                </div>
                <div style={{ fontSize: 12, color: s.gain_rate >= 0 ? T.red : T.green }}>
                  {s.gain_rate >= 0 ? "+" : ""}{s.gain_rate?.toFixed(2)}%
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 13, color: T.text }}>{Number(s.qty).toLocaleString()}</div>
                <div style={{ fontSize: 11, color: T.textMuted }}>{Number(s.avg_price).toLocaleString()}</div>
              </div>
            </div>))}
    </div>
  );
}

// ─── Bottom Nav ───────────────────────────────────────────────────────────────
function BottomNav({ active, setActive }) {
  const items = [
    { id: "home",      icon: "🏠", label: "홈" },
    { id: "watchlist", icon: "⭐", label: "관심" },
    { id: "trade",     icon: "📊", label: "주문" },
    { id: "my",        icon: "👤", label: "MY" },
    { id: "more",      icon: "≡",  label: "더보기" },
  ];
  return (
    <div style={{
      position: "fixed", bottom: 0, left: "50%", transform: "translateX(-50%)",
      width: "100%", maxWidth: 420, background: T.surface,
      borderTop: `1px solid ${T.border}`, display: "flex", zIndex: 100,
    }}>
      {items.map(item => (
        <button key={item.id} onClick={() => setActive(item.id)} style={{
          flex: 1, background: "none", border: "none", cursor: "pointer",
          padding: "10px 0 14px", display: "flex", flexDirection: "column",
          alignItems: "center", gap: 3, position: "relative",
          color: active === item.id ? T.accent : T.textMuted, transition: "color 0.2s",
        }}>
          {active === item.id && (
            <div style={{ position: "absolute", top: 0, width: 28, height: 2, background: T.accent, borderRadius: 1 }} />
          )}
          <span style={{ fontSize: 20 }}>{item.icon}</span>
          <span style={{ fontSize: 11, fontWeight: active === item.id ? 700 : 400 }}>{item.label}</span>
        </button>
      ))}
    </div>
  );
}

// ─── Root App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [screen, setScreen] = useState("home");
  return (
    <div style={{ fontFamily: "'Noto Sans KR', -apple-system, sans-serif", background: T.bg, minHeight: "100vh", display: "flex", justifyContent: "center" }}>
      <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap" rel="stylesheet" />
      <div style={{ width: "100%", maxWidth: 420, background: T.bg, minHeight: "100vh", paddingBottom: 70, overflowY: "auto", color: T.text }}>
        {screen === "home"      && <HomeScreen />}
        {screen === "watchlist" && <WatchlistScreen />}
        {screen === "my"        && <MyScreen />}
        {(screen === "trade" || screen === "more") && (
          <div style={{ padding: 60, textAlign: "center", color: T.textMuted }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>{screen === "trade" ? "📊" : "≡"}</div>
            <div>준비 중입니다</div>
          </div>
        )}
        <BottomNav active={screen} setActive={setScreen} />
      </div>
    </div>
  );
}

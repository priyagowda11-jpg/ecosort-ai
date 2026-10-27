import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import { useI18n } from "../i18n";
import { CATEGORY_IDS, isCategory } from "../config/categories";
import { getRecent, getSummary, getTimeline, HistoryItem } from "../services/api";

const COLORS: Record<string, string> = { wet: "#5a9e3f", dry: "#d9b44a", plastic: "#2f7dd1", metal: "#6b7a8f", reusable: "#8a5fc7", non_recyclable: "#7a7a7a" };

export function Dashboard() {
  const { t } = useI18n();
  const [cat, setCat] = useState(""); const [start, setStart] = useState(""); const [end, setEnd] = useState("");
  const [state, setState] = useState<"loading" | "error" | "ok">("loading");
  const [sum, setSum] = useState<{ total: number; by_category: Record<string, number> }>({ total: 0, by_category: {} });
  const [line, setLine] = useState<{ date: string; count: number }[]>([]);
  const [recent, setRecent] = useState<HistoryItem[]>([]);

  useEffect(() => {
    let live = true; setState("loading");
    const f = { category: cat || undefined, start: start || undefined, end: end || undefined };
    Promise.all([getSummary(f), getTimeline(f), getRecent(f)])
      .then(([s, l, r]) => { if (live) { setSum(s); setLine(l); setRecent(r); setState("ok"); } })
      .catch(() => live && setState("error"));
    return () => { live = false; };
  }, [cat, start, end]);

  const nm = (id: string) => (isCategory(id) ? t(`cat.${id}.name`) : id);
  const pie = CATEGORY_IDS.filter(id => sum.by_category[id]).map(id => ({ id, name: nm(id), value: sum.by_category[id] }));
  const top = [...pie].sort((a, b) => b.value - a.value);
  const filtered = !!(cat || start || end);

  return (
    <section>
      <h1>{t("dash.title")}</h1>
      <div className="row">
        <label>{t("dash.from")} <input type="date" value={start} onChange={e => setStart(e.target.value)} /></label>
        <label>{t("dash.to")} <input type="date" value={end} onChange={e => setEnd(e.target.value)} /></label>
        <select aria-label={t("dash.all")} value={cat} onChange={e => setCat(e.target.value)}>
          <option value="">{t("dash.all")}</option>{CATEGORY_IDS.map(id => <option key={id} value={id}>{nm(id)}</option>)}
        </select>
      </div>
      {state === "loading" && <p role="status">{t("dash.loading")}</p>}
      {state === "error" && <div role="alert" className="notice error">{t("dash.err")}</div>}
      {state === "ok" && sum.total === 0 && <p className="notice">{t(filtered ? "dash.noresult" : "dash.empty")}</p>}
      {state === "ok" && sum.total > 0 && (<>
        <div className="card"><span className="muted">{t("dash.total")}</span><div className="big">{sum.total}</div></div>
        <h2>{t("dash.dist")}</h2>
        <ResponsiveContainer width="100%" height={260}><PieChart>
          <Pie data={pie} dataKey="value" nameKey="name" innerRadius={55} outerRadius={95}>{pie.map(d => <Cell key={d.id} fill={COLORS[d.id]} />)}</Pie><Tooltip />
        </PieChart></ResponsiveContainer>
        <h2>{t("dash.time")}</h2>
        <ResponsiveContainer width="100%" height={240}><LineChart data={line}>
          <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis allowDecimals={false} /><Tooltip />
          <Line type="monotone" dataKey="count" stroke="#1f6b3a" strokeWidth={2} />
        </LineChart></ResponsiveContainer>
        <h2>{t("dash.top")}</h2>
        <ol>{top.map(d => <li key={d.id}>{d.name}: {d.value}</li>)}</ol>
        <h2>{t("dash.recent")}</h2>
        <ul className="hist">{recent.map(h => <li key={h.id}>{nm(h.category)} · {new Date(h.created_at).toLocaleString()}</li>)}</ul>
      </>)}
    </section>
  );
}

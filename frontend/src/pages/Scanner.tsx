import { useEffect, useState } from "react";
import { useI18n } from "../i18n";
import { CATEGORY_IDS, isCategory } from "../config/categories";
import { ApiError, getHealth, getHistory, HistoryItem, predict, Prediction } from "../services/api";
import { CameraCapture } from "../components/CameraCapture";

const name = (t: (k: string) => string, id: string) => (isCategory(id) ? t(`cat.${id}.name`) : id);

export function Scanner() {
  const { t } = useI18n();
  const [ready, setReady] = useState<boolean | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState<string | null>(null);
  const [cam, setCam] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [res, setRes] = useState<Prediction | null>(null);
  const [hist, setHist] = useState<HistoryItem[]>([]);

  const refresh = () => getHealth().then(h => { setReady(h.model_ready); if (h.model_ready) setErr(null); }).catch(() => { setReady(null); setErr("err.network"); });
  const loadHist = () => getHistory().then(setHist).catch(() => {});
  useEffect(() => { refresh(); loadHist(); }, []);
  useEffect(() => { if (ready === true) return; const id = setInterval(refresh, 5000); return () => clearInterval(id); }, [ready]);
  useEffect(() => () => { if (url) URL.revokeObjectURL(url); }, [url]);

  const pick = (f: File | null) => {
    setRes(null); setErr(null); setFile(f); setUrl(f ? URL.createObjectURL(f) : null); setCam(false);
  };
  const onFile = (f?: File) => {
    if (!f) return;
    if (!(["image/jpeg", "image/png", "image/webp"]).includes(f.type)) return setErr("err.format");
    if (f.size > 8 * 1024 * 1024) return setErr("err.large");
    pick(f);
  };
  const run = async () => {
    if (!file || busy) return;
    setBusy(true); setErr(null);
    try { setRes(await predict(file)); loadHist(); }
    catch (e) { setErr(e instanceof ApiError ? (e.kind === "unavailable" ? "err.unavailable" : `err.${e.kind}`) : "err.generic"); if (e instanceof ApiError && e.kind === "unavailable") setReady(false); }
    finally { setBusy(false); }
  };

  return (
    <section onDragOver={e => e.preventDefault()} onDrop={e => { e.preventDefault(); if (!res && !cam) onFile(e.dataTransfer.files?.[0]); }}>
      <h1>{t("scan.title")}</h1>
      {ready === false && <div role="alert" className="notice error">{t("err.unavailable")}</div>}
      {err && ready !== false && <div role="alert" className="notice error">{t(err)}</div>}

      {!res && (cam ? <CameraCapture onPhoto={pick} onClose={() => setCam(false)} /> : (<>
        {url && <img className="preview" src={url} alt="" />}
        {file && <p className="muted">{file.name} · {(file.size / 1024).toFixed(0)} KB</p>}
        <div className="row">
          <label className="btn">{t("scan.upload")}
            <input type="file" hidden accept="image/jpeg,image/png,image/webp" onChange={e => onFile(e.target.files?.[0])} />
          </label>
          <button className="btn" onClick={() => setCam(true)}>{t("scan.camera")}</button>
          {file && <button className="btn" onClick={() => pick(null)}>{t("scan.remove")}</button>}
          <button className="btn primary" disabled={!file || busy || ready === false} onClick={run}>
            {busy ? t("scan.identifying") : t("scan.identify")}
          </button>
        </div>
        <p className="muted">{t("scan.hint")} · {t("scan.drop")}</p>
      </>))}

      {res && (
        <div className="result">
          {url && <img className="preview" src={url} alt="" />}
          <h2>{t("res.category")}: {name(t, res.category)}</h2>
          {isCategory(res.category) && <p>{t(`cat.${res.category}.desc`)}</p>}
          {isCategory(res.category) && <><h3>{t("res.how")}</h3><p>{t(`cat.${res.category}.tip`)}</p></>}
          <p className="muted">{t("res.note")}</p>
          <button className="btn primary" onClick={() => { pick(null); }}>{t("scan.another")}</button>
        </div>
      )}

      <h3>{t("hist.title")}</h3>
      {hist.length === 0 ? <p className="muted">{t("hist.empty")}</p> :
        <ul className="hist">{hist.map(h => <li key={h.id}>{name(t, h.category)} · {new Date(h.created_at).toLocaleString()}</li>)}</ul>}
    </section>
  );
}

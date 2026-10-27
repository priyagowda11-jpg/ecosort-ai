export const API_URL =
(import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ??
  (import.meta.env.DEV ? "http://localhost:8000" : "");

export interface HistoryItem { id: string; created_at: string; category: string; model_version: string }
export class ApiError extends Error { constructor(public kind: "unavailable" | "unclear" | "large" | "format" | "bad" | "network" | "generic") { super(kind); } }

export async function getHealth(): Promise<{ model_ready: boolean; model_version: string | null }> {
  try { const r = await fetch(`${API_URL}/api/health`); if (!r.ok) throw 0; return await r.json(); }
  catch { throw new ApiError("network"); }
}
export async function predict(file: File): Promise<Prediction> {
  const body = new FormData(); body.append("file", file);
  let r: Response;
  try { r = await fetch(`${API_URL}/api/predict`, { method: "POST", body }); } catch { throw new ApiError("network"); }
  if (r.ok) return r.json();
  throw new ApiError(({ 503: "unavailable", 422: "unclear", 413: "large", 415: "format", 400: "bad" } as const)[r.status as 503] ?? "generic");
}
export async function getHistory(): Promise<HistoryItem[]> {
  const r = await fetch(`${API_URL}/api/history?limit=5`); if (!r.ok) throw new ApiError("generic"); return r.json();
}

export interface Filters { start?: string; end?: string; category?: string }
const qs = (f: Filters, extra: Record<string, string> = {}) => {
  const p = new URLSearchParams(extra);
  (Object.entries(f) as [string, string | undefined][]).forEach(([k, v]) => v && p.set(k, v));
  const s = p.toString(); return s ? `?${s}` : "";
};
async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${API_URL}${path}`); if (!r.ok) throw new ApiError("generic"); return r.json();
}
export const getSummary = (f: Filters) => get<{ total: number; by_category: Record<string, number> }>(`/api/analytics/summary${qs(f)}`);
export const getTimeline = (f: Filters) => get<{ date: string; count: number }[]>(`/api/analytics/timeline${qs(f)}`);
export const getRecent = (f: Filters) => get<HistoryItem[]>(`/api/history${qs(f, { limit: "10" })}`);

import { createContext, useContext, useState, ReactNode } from "react";
import { en } from "./en"; import { kn } from "./kn";
export type Lang = "en" | "kn";
const dict = { en, kn };
const Ctx = createContext<{ lang: Lang; setLang: (l: Lang) => void; t: (k: string) => string }>(null!);
export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, set] = useState<Lang>(() => {
    try { return localStorage.getItem("lang") === "kn" ? "kn" : "en"; } catch { return "en"; }
  });
  const setLang = (l: Lang) => { set(l); try { localStorage.setItem("lang", l); } catch {} document.documentElement.lang = l; };
  const t = (k: string) => dict[lang][k] ?? en[k] ?? k;   // falls back to English
  return <Ctx.Provider value={{ lang, setLang, t }}>{children}</Ctx.Provider>;
}
export const useI18n = () => useContext(Ctx);

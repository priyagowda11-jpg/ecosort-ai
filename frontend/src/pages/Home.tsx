import { Link } from "react-router-dom";
import { Apple, Newspaper, Repeat, Ban, Wrench, Milk, Upload, Search, Recycle } from "lucide-react";
import { useI18n } from "../i18n";
import { CATEGORY_IDS, CategoryId } from "../config/categories";

const ICONS: Record<CategoryId, typeof Apple> = { wet: Apple, dry: Newspaper, plastic: Milk, metal: Wrench, reusable: Repeat, non_recyclable: Ban };
const STEPS = [["upload", Upload], ["identify", Search], ["segregate", Recycle]] as const;

export function Home() {
  const { t } = useI18n();
  return (
    <>
      <section className="hero">
        <h1>{t("home.title")}</h1><p>{t("home.desc")}</p>
        <div className="row"><Link className="btn primary" to="/scan">{t("home.cta")}</Link><Link className="btn" to="/categories">{t("home.explore")}</Link></div>
      </section>
      <h2>{t("home.cats")}</h2>
      <div className="grid">{CATEGORY_IDS.map(id => { const I = ICONS[id]; return (
        <article key={id} className="card"><I aria-hidden size={28} /><h3>{t(`cat.${id}.name`)}</h3><p className="muted">{t(`cat.${id}.desc`)}</p></article>); })}</div>
      <h2>{t("home.steps")}</h2>
      <div className="grid">{STEPS.map(([k, I], n) => (
        <article key={k} className="card"><I aria-hidden size={28} /><h3>{n + 1}. {t(`step.${k}`)}</h3><p className="muted">{t(`step.${k}.d`)}</p></article>))}</div>
      <h2>{t("home.edu.title")}</h2><p>{t("home.edu")}</p>
    </>
  );
}

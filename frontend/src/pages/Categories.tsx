import { useI18n } from "../i18n";
import { CATEGORY_IDS } from "../config/categories";
export function Categories() {
  const { t } = useI18n();
  return (<section><h1>{t("nav.categories")}</h1><div className="grid">
    {CATEGORY_IDS.map(id => <article key={id} className="card"><h2>{t(`cat.${id}.name`)}</h2><p>{t(`cat.${id}.desc`)}</p><p className="muted">{t(`cat.${id}.tip`)}</p></article>)}
  </div></section>);
}

import { HashRouter, NavLink, Route, Routes } from "react-router-dom";
import { Recycle } from "lucide-react";
import { I18nProvider, useI18n } from "./i18n";
import { Home } from "./pages/Home"; import { Scanner } from "./pages/Scanner";
import { Categories } from "./pages/Categories"; import { Dashboard } from "./pages/Dashboard";

function Shell() {
  const { t, lang, setLang } = useI18n();
  const link = ({ isActive }: { isActive: boolean }) => "link" + (isActive ? " active" : "");
  return (<>
    <header className="nav"><strong className="logo"><Recycle aria-hidden size={20} /> EcoSort AI</strong>
      <nav aria-label="Main">
        <NavLink className={link} to="/" end>{t("nav.home")}</NavLink>
        <NavLink className={link} to="/scan">{t("nav.scan")}</NavLink>
        <NavLink className={link} to="/categories">{t("nav.categories")}</NavLink>
        <NavLink className={link} to="/dashboard">{t("nav.dashboard")}</NavLink>
      </nav>
      <select aria-label={t("lang.label")} value={lang} onChange={e => setLang(e.target.value as "en" | "kn")}>
        <option value="en">English</option><option value="kn">ಕನ್ನಡ</option>
      </select>
    </header>
    <main><Routes><Route path="/" element={<Home />} /><Route path="/scan" element={<Scanner />} />
      <Route path="/categories" element={<Categories />} /><Route path="/dashboard" element={<Dashboard />} /></Routes></main>
    <footer className="foot">{t("foot")}</footer>
  </>);
}
export default function App() { return <I18nProvider><HashRouter><Shell /></HashRouter></I18nProvider>; }

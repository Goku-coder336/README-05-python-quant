import Link from "next/link";
import { adminCategories, adminEventTypes, adminTraditions } from "@/lib/admin";
import { CategoryIcon, ICON_CHOICES } from "@/components/Icon";
import { AdminForm } from "@/components/AdminForm";
import { createCategoryAction, createEventTypeAction, createTraditionAction, toggleActiveAction } from "../actions";
export const metadata = { title: "Event types and categories" };
const GROUPS = ["Weddings and family", "Religious and cultural", "Parties and celebrations", "Business and professional", "Community and public", "Something else"];

function Toggle({ what, id, active }: { what: string; id: string; active: boolean }) {
  return <form action={toggleActiveAction}><input type="hidden" name="what" value={what} /><input type="hidden" name="id" value={id} /><input type="hidden" name="active" value={active ? "0" : "1"} />
    <button className="text-xs text-muted underline-offset-4 hover:text-ink hover:underline">{active ? "Hide" : "Show"}</button></form>;
}
const IconSelect = ({ id }: { id: string }) => <select className="input !h-11" id={id} name="icon" defaultValue="Sparkle">{ICON_CHOICES.map(i => <option key={i}>{i}</option>)}</select>;

export default async function Catalogue() {
  const [types, cats, trads] = await Promise.all([adminEventTypes(), adminCategories(), adminTraditions()]);
  return (
    <div className="grid gap-12">
      <div><h1 className="font-display text-4xl">Event types and categories</h1>
        <p className="mt-2 max-w-2xl text-muted">Utsella works for any kind of event. Add an occasion and it gets a starter checklist you can edit. Hiding something removes it from customers&apos; choices without deleting existing plans or listings.</p></div>

      <section aria-labelledby="et"><h2 id="et" className="font-display text-2xl">Occasions ({types.length})</h2>
        <div className="card mt-4 p-5"><AdminForm action={createEventTypeAction} submit="Add occasion">
          <div><label className="label" htmlFor="et-name">Name</label><input className="input !h-11" id="et-name" name="name" placeholder="Bridal shower" /></div>
          <div><label className="label" htmlFor="et-grp">Group</label><select className="input !h-11" id="et-grp" name="grp">{GROUPS.map(g => <option key={g}>{g}</option>)}</select></div>
          <div><label className="label" htmlFor="et-icon">Icon</label><IconSelect id="et-icon" /></div>
        </AdminForm></div>
        {GROUPS.map(g => { const list = types.filter(t => t.grp === g); if (!list.length) return null; return (
          <div key={g} className="mt-6"><h3 className="text-sm font-semibold uppercase tracking-widest text-muted">{g}</h3>
            <ul className="mt-2 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">{list.map(t => (
              <li key={t.id} className={`card flex items-center gap-3 p-3 ${t.active ? "" : "opacity-50"}`}><span className="text-brown"><CategoryIcon name={t.icon} size={20} /></span>
                <span className="min-w-0 flex-1"><span className="block text-sm font-medium">{t.name}</span><span className="text-xs text-muted">{t.templates} checklist{t.templates === 1 ? "" : "s"} · {t.plans} plan{t.plans === 1 ? "" : "s"}</span></span>
                <Toggle what="event_type" id={t.id} active={t.active} /></li>))}</ul></div>); })}
        <p className="mt-4 text-sm"><Link className="underline" href="/admin/templates">Edit or add checklists →</Link></p>
      </section>

      <section aria-labelledby="ct"><h2 id="ct" className="font-display text-2xl">Vendor categories ({cats.length})</h2>
        <div className="card mt-4 p-5"><AdminForm action={createCategoryAction} submit="Add category">
          <div><label className="label" htmlFor="ct-name">Name</label><input className="input !h-11" id="ct-name" name="name" placeholder="Henna artists" /></div>
          <div><label className="label" htmlFor="ct-kind">Type</label><select className="input !h-11" id="ct-kind" name="kind"><option value="service">Service (people)</option><option value="equipment">Gear for rent</option></select></div>
          <div><label className="label" htmlFor="ct-icon">Icon</label><IconSelect id="ct-icon" /></div>
        </AdminForm></div>
        <ul className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">{cats.map(c => (
          <li key={c.id} className={`card flex items-center gap-3 p-3 ${c.active ? "" : "opacity-50"}`}><span className="text-brown"><CategoryIcon name={c.icon} size={20} /></span>
            <span className="min-w-0 flex-1"><span className="block text-sm font-medium">{c.name}</span><span className="text-xs text-muted">{c.kind === "service" ? "Service" : "Rental"} · {c.listings} listing{c.listings === 1 ? "" : "s"}</span></span>
            <Toggle what="category" id={c.id} active={c.active} /></li>))}</ul>
      </section>

      <section aria-labelledby="tr"><h2 id="tr" className="font-display text-2xl">Traditions ({trads.length})</h2>
        <p className="mt-1 text-sm text-muted">Used to suggest checklists and vendors. Customers can always choose &quot;Any or mixed&quot;.</p>
        <div className="card mt-4 p-5"><AdminForm action={createTraditionAction} submit="Add tradition" className="grid gap-3 sm:grid-cols-[1fr_auto] sm:items-end">
          <div><label className="label" htmlFor="tr-name">Name</label><input className="input !h-11" id="tr-name" name="name" placeholder="Konkani" /></div>
        </AdminForm></div>
        <ul className="mt-4 flex flex-wrap gap-2">{trads.map(t => <li key={t.id} className={`chip ${t.active ? "" : "opacity-50"}`}>{t.name}<Toggle what="tradition" id={t.id} active={t.active} /></li>)}</ul>
      </section>
    </div>
  );
}

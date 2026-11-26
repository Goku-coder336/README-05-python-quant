import Link from "next/link";
import { templates, adminEventTypes } from "@/lib/admin";
import { traditions } from "@/lib/data";
import { AdminForm } from "@/components/AdminForm";
import { createTemplateAction } from "../actions";
export const metadata = { title: "Checklists" };
export default async function AdminTemplates() {
  const [list, types, trads] = await Promise.all([templates(), adminEventTypes(), traditions()]);
  return (
    <div>
      <h1 className="font-display text-4xl">Checklist templates</h1>
      <p className="mt-2 max-w-2xl text-muted">These are the starting checklists customers get. Changes apply to new event plans; existing plans keep their own copy.</p>
      <section className="card mt-6 p-5" aria-labelledby="nt"><h2 id="nt" className="mb-3 font-display text-xl">New checklist</h2>
        <p className="mb-3 text-sm text-muted">For example a Sikh wedding, or an intimate version of a birthday. Copy an existing one to save time.</p>
        <AdminForm action={createTemplateAction} submit="Create" className="grid gap-3 sm:grid-cols-2 lg:grid-cols-[1fr_1fr_140px_1fr_auto] lg:items-end">
          <div><label className="label" htmlFor="nt-et">Occasion</label><select className="input !h-11" id="nt-et" name="eventTypeId" defaultValue=""><option value="">Choose</option>{types.filter(t => t.active).map(t => <option key={t.id} value={t.id}>{t.name}</option>)}</select></div>
          <div><label className="label" htmlFor="nt-tr">Tradition</label><select className="input !h-11" id="nt-tr" name="traditionId" defaultValue=""><option value="">Any tradition</option>{trads.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}</select></div>
          <div><label className="label" htmlFor="nt-sz">Size</label><select className="input !h-11" id="nt-sz" name="sizeTier"><option value="standard">Standard</option><option value="intimate">Intimate</option></select></div>
          <div><label className="label" htmlFor="nt-cp">Copy items from</label><select className="input !h-11" id="nt-cp" name="copyFrom" defaultValue=""><option value="">Start empty</option>{list.map(t => <option key={t.id} value={t.id}>{t.tradition ?? "Any"} {t.eventType.toLowerCase()}{t.sizeTier === "intimate" ? ", intimate" : ""}</option>)}</select></div>
        </AdminForm></section>
      <ul className="mt-6 grid gap-3 sm:grid-cols-2">{list.map(t => (
        <li key={t.id}><Link href={`/admin/templates/${t.id}`} className="card block p-5 transition hover:border-brown">
          <p className="font-medium">{t.tradition ?? "Any tradition"} {t.eventType.toLowerCase()}{t.sizeTier === "intimate" ? ", intimate" : ""}</p>
          <p className="text-sm text-muted">{t.items} items</p></Link></li>))}</ul>
    </div>
  );
}

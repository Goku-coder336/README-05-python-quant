import Link from "next/link";
import { templates } from "@/lib/admin";
export const metadata = { title: "Checklists" };
export default async function AdminTemplates() {
  const list = await templates();
  return (
    <div>
      <h1 className="font-display text-4xl">Checklist templates</h1>
      <p className="mt-2 max-w-2xl text-muted">These are the starting checklists customers get. Changes apply to new event plans; existing plans keep their own copy.</p>
      <ul className="mt-6 grid gap-3 sm:grid-cols-2">{list.map(t => (
        <li key={t.id}><Link href={`/admin/templates/${t.id}`} className="card block p-5 transition hover:border-brown">
          <p className="font-medium">{t.tradition ?? "Any tradition"} {t.eventType.toLowerCase()}{t.sizeTier === "intimate" ? ", intimate" : ""}</p>
          <p className="text-sm text-muted">{t.items} items</p></Link></li>))}</ul>
    </div>
  );
}

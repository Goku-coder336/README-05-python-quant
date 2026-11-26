import Link from "next/link";
import { notFound } from "next/navigation";
import { template, templateItems } from "@/lib/admin";
import { categories } from "@/lib/data";
import { TemplateItemForm } from "@/components/TemplateItemForm";
import { deleteItemAction } from "../../actions";
export default async function EditTemplate({ params }: { params: Promise<{ id: string }> }) {
  const id = (await params).id; const t = await template(id); if (!t) notFound();
  const [items, cats] = await Promise.all([templateItems(id), categories()]);
  const subEvents = [...new Set(items.map(i => i.subEvent))]; const total = items.reduce((s, i) => s + i.budgetShare, 0);
  const catList = cats.map(c => ({ id: c.id, name: c.name }));
  return (
    <div>
      <Link href="/admin/templates" className="text-sm text-muted hover:underline">← All checklists</Link>
      <h1 className="mt-2 font-display text-4xl">{t.tradition ?? "Any tradition"} {t.eventType.toLowerCase()}{t.sizeTier === "intimate" ? ", intimate" : ""}</h1>
      <p className={`mt-2 text-sm ${total === 100 ? "text-muted" : "text-danger"}`}>Budget shares add up to {total}%{total !== 100 && ". Aim for 100% so suggested amounts match the customer's budget."}</p>
      <datalist id={`se-${id}`}>{subEvents.map(s => <option key={s} value={s} />)}</datalist>
      <ul className="mt-6 grid gap-3">{items.map(i => (
        <li key={i.id} className="card p-4">
          <TemplateItemForm templateId={id} item={i} categories={catList} subEvents={subEvents} />
          <form action={deleteItemAction} className="mt-2 text-right"><input type="hidden" name="templateId" value={id} /><input type="hidden" name="itemId" value={i.id} /><button className="text-xs text-muted hover:text-danger hover:underline">Delete “{i.label}”</button></form>
        </li>))}</ul>
      <section className="card mt-8 p-4" aria-labelledby="new"><h2 id="new" className="mb-3 font-display text-xl">Add an item</h2><TemplateItemForm templateId={id} categories={catList} subEvents={subEvents} /></section>
    </div>
  );
}

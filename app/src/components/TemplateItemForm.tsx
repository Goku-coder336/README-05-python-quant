"use client";
import { useActionState, useEffect, useRef } from "react";
import { saveItemAction, type ItemState } from "@/app/admin/actions";
type Item = { id?: number; categoryId: string; subEvent: string; label: string; note: string; budgetShare: number; sort: number };
export function TemplateItemForm({ templateId, item, categories, subEvents }: { templateId: string; item?: Item; categories: { id: string; name: string }[]; subEvents: string[] }) {
  const [state, action, pending] = useActionState<ItemState, FormData>(saveItemAction, {});
  const ref = useRef<HTMLFormElement>(null); const k = item?.id ?? "new";
  useEffect(() => { if (state.ok && !item) ref.current?.reset(); }, [state, item]);
  return (
    <form ref={ref} action={action} className="grid gap-2 sm:grid-cols-[1.4fr_1fr_1fr_1.2fr_70px_60px_auto] sm:items-end" noValidate>
      <input type="hidden" name="templateId" value={templateId} /><input type="hidden" name="id" value={item?.id ?? ""} />
      <div><label className="text-xs text-muted" htmlFor={`l-${k}`}>Label</label><input className="input !h-10 text-sm" id={`l-${k}`} name="label" defaultValue={item?.label} /></div>
      <div><label className="text-xs text-muted" htmlFor={`c-${k}`}>Category</label><select className="input !h-10 text-sm" id={`c-${k}`} name="categoryId" defaultValue={item?.categoryId ?? ""}><option value="">Choose</option>{categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
      <div><label className="text-xs text-muted" htmlFor={`s-${k}`}>Part of day</label><input className="input !h-10 text-sm" id={`s-${k}`} name="subEvent" list={`se-${templateId}`} defaultValue={item?.subEvent ?? subEvents[0] ?? "Main event"} /></div>
      <div><label className="text-xs text-muted" htmlFor={`o-${k}`}>Note</label><input className="input !h-10 text-sm" id={`o-${k}`} name="note" defaultValue={item?.note} /></div>
      <div><label className="text-xs text-muted" htmlFor={`b-${k}`}>Budget %</label><input className="input !h-10 text-sm" id={`b-${k}`} name="budgetShare" type="number" min="0" max="100" defaultValue={item?.budgetShare ?? 0} /></div>
      <div><label className="text-xs text-muted" htmlFor={`r-${k}`}>Order</label><input className="input !h-10 text-sm" id={`r-${k}`} name="sort" type="number" min="0" defaultValue={item?.sort ?? 99} /></div>
      <button className={item ? "btn-line !py-2" : "btn-primary !py-2"} disabled={pending}>{pending ? "Saving…" : item ? "Save" : "Add"}</button>
      {state.error && <p role="alert" className="text-sm text-danger sm:col-span-7">{state.error}</p>}
      {state.ok && <p role="status" className="text-sm text-success sm:col-span-7">Saved.</p>}
    </form>
  );
}

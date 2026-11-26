"use client";
import { useActionState, useEffect, useRef } from "react";
import { addItemAction, type FormState } from "@/app/actions";
export function AddItemForm({ eventId, categories, subEvents }: { eventId: string; categories: { id: string; name: string }[]; subEvents: string[] }) {
  const [state, action, pending] = useActionState<FormState, FormData>(addItemAction, {});
  const ref = useRef<HTMLFormElement>(null);
  useEffect(() => { if (state.ok) ref.current?.reset(); }, [state]);
  return (
    <form ref={ref} action={action} className="grid gap-3 sm:grid-cols-[1fr_1fr_1fr_auto] sm:items-end" noValidate>
      <input type="hidden" name="eventId" value={eventId} />
      <div><label className="label" htmlFor="label">Item</label><input className="input" id="label" name="label" placeholder="Welcome drinks" /></div>
      <div><label className="label" htmlFor="ic">Category</label><select className="input" id="ic" name="categoryId" defaultValue=""><option value="">Choose</option>{categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
      <div><label className="label" htmlFor="se">Part of the day</label><select className="input" id="se" name="subEvent">{[...subEvents, "Added by you"].filter((x, i, a) => a.indexOf(x) === i).map(s => <option key={s}>{s}</option>)}</select></div>
      <button className="btn-line" disabled={pending}>{pending ? "Adding…" : "Add"}</button>
      {state.error && <p role="alert" className="text-sm text-danger sm:col-span-4">{state.error}</p>}
    </form>
  );
}

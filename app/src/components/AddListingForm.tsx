"use client";
import { useActionState, useState, useEffect, useRef } from "react";
import { addListing, type FormState } from "@/app/actions";

type Cat = { id: string; name: string; kind: "service" | "equipment" };
export function AddListingForm({ handle, categories, currency }: { handle: string; categories: Cat[]; currency: string }) {
  const [state, action, pending] = useActionState<FormState, FormData>(addListing, {});
  const [catId, setCatId] = useState(""); const kind = categories.find(c => c.id === catId)?.kind;
  const ref = useRef<HTMLFormElement>(null);
  useEffect(() => { if (state.ok) { ref.current?.reset(); setCatId(""); } }, [state]);
  const done = state.ok;
  return (
    <form ref={ref} action={action} className="grid gap-4" noValidate>
      <input type="hidden" name="handle" value={handle} />
      <div><label className="label" htmlFor="categoryId">What are you listing?</label>
        <select className="input" id="categoryId" name="categoryId" value={catId} onChange={e => setCatId(e.target.value)} required>
          <option value="">Choose a category</option>
          <optgroup label="Services">{categories.filter(c => c.kind === "service").map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</optgroup>
          <optgroup label="Gear for rent">{categories.filter(c => c.kind === "equipment").map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</optgroup>
        </select></div>
      <div><label className="label" htmlFor="title">Title</label><input className="input" id="title" name="title" placeholder={kind === "equipment" ? "Compact PA kit for 80 guests" : "Bridal look with saree draping"} required /></div>
      <div><label className="label" htmlFor="description">Description</label><textarea className="input h-24 py-3" id="description" name="description" /></div>
      <div className="grid grid-cols-2 gap-3">
        <div><label className="label" htmlFor="price">{kind === "equipment" ? "Day rate" : "Price"} ({currency})</label><input className="input" id="price" name="price" type="number" min="1" inputMode="decimal" required /></div>
        {kind === "equipment"
          ? <div><label className="label" htmlFor="deposit">Deposit ({currency})</label><input className="input" id="deposit" name="deposit" type="number" min="0" inputMode="decimal" /></div>
          : <div><label className="label" htmlFor="maxGuests">Max guests <span className="font-normal text-muted">(optional)</span></label><input className="input" id="maxGuests" name="maxGuests" type="number" min="1" /></div>}
      </div>
      {kind === "equipment" ? (
        <div className="grid grid-cols-2 items-end gap-3">
          <div><label className="label" htmlFor="units">How many units?</label><input className="input" id="units" name="units" type="number" min="1" max="50" defaultValue={1} /></div>
          <label className="flex h-12 items-center gap-2 text-sm"><input type="checkbox" name="needsOperator" className="h-4 w-4 accent-[var(--brown)]" />Comes with a technician</label>
        </div>
      ) : (
        <div><label className="label" htmlFor="included">What is included <span className="font-normal text-muted">(comma separated)</span></label><input className="input" id="included" name="included" placeholder="Trial session, hair styling, draping" /></div>
      )}
      {state.error && <p role="alert" className="rounded-2xl bg-blush px-4 py-3 text-sm text-danger">{state.error}</p>}
      {done && <p role="status" className="rounded-2xl bg-sage px-4 py-3 text-sm text-success">Listing published. It now shows in your city.</p>}
      <button className="btn-primary" disabled={pending}>{pending ? "Publishing…" : "Publish listing"}</button>
    </form>
  );
}

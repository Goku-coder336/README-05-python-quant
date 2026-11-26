"use client";
import { useActionState } from "react";
import { requestBooking, type FormState } from "@/app/actions";

export function BookForm({ kind, itemId, cta }: { kind: "service" | "equipment"; itemId: string; cta: string }) {
  const [state, action, pending] = useActionState<FormState, FormData>(requestBooking, {});
  const v = state.fields ?? {};
  const min = new Date().toISOString().slice(0, 10);
  return (
    <form action={action} className="grid gap-4" noValidate>
      <input type="hidden" name="kind" value={kind} /><input type="hidden" name="itemId" value={itemId} />
      <div className={kind === "equipment" ? "grid grid-cols-2 gap-3" : ""}>
        <div><label className="label" htmlFor="startsOn">{kind === "equipment" ? "From" : "Event date"}</label><input className="input" id="startsOn" name="startsOn" type="date" min={min} defaultValue={v.startsOn} required /></div>
        {kind === "equipment" && <div><label className="label" htmlFor="endsOn">Until</label><input className="input" id="endsOn" name="endsOn" type="date" min={min} defaultValue={v.endsOn} /></div>}
      </div>
      <div><label className="label" htmlFor="name">Your name</label><input className="input" id="name" name="name" autoComplete="name" defaultValue={v.name} required /></div>
      <div><label className="label" htmlFor="phone">WhatsApp number</label><input className="input" id="phone" name="phone" type="tel" inputMode="tel" autoComplete="tel" placeholder="+91 98470 12345" defaultValue={v.phone} required /></div>
      <div><label className="label" htmlFor="note">Anything the vendor should know? <span className="font-normal text-muted">(optional)</span></label><textarea className="input h-24 py-3" id="note" name="note" maxLength={500} defaultValue={v.note} /></div>
      {state.error && <p role="alert" className="rounded-2xl bg-blush px-4 py-3 text-sm text-danger">{state.error}</p>}
      <button className="btn-primary w-full" disabled={pending}>{pending ? "Sending request…" : cta}</button>
      <p className="text-center text-xs text-muted">No payment yet. The vendor confirms first, then you pay the advance.</p>
    </form>
  );
}

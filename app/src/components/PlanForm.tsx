"use client";
import { useActionState, useState } from "react";
import { createEventAction, type FormState } from "@/app/actions";

type Opt = { id: string; name: string };
export function PlanForm({ types, traditions, cities }: { types: (Opt & { icon: React.ReactNode; grp: string })[]; traditions: Opt[]; cities: (Opt & { group: string })[] }) {
  const [state, action, pending] = useActionState<FormState, FormData>(createEventAction, {});
  const v = state.fields ?? {};
  const [type, setType] = useState(v.eventTypeId ?? types[0]?.id);
  const groups2 = [...new Set(types.map(t => t.grp))];
  const [grp, setGrp] = useState(types.find(t => t.id === type)?.grp ?? groups2[0]);
  const [guests, setGuests] = useState(v.guestCount ?? "");
  const intimate = guests !== "" && Number(guests) > 0 && Number(guests) <= 50;
  const groups = [...new Set(cities.map(c => c.group))];
  return (
    <form action={action} className="grid gap-6" noValidate>
      <fieldset><legend className="label">What are you planning?</legend>
        <div className="mt-1 flex flex-wrap gap-2" role="tablist" aria-label="Kind of event">
          {groups2.map(g => <button key={g} type="button" role="tab" aria-selected={grp === g} onClick={() => setGrp(g)} className={grp === g ? "chip-on" : "chip"}>{g}</button>)}
        </div>
        <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3" role="radiogroup">
          {types.filter(t => t.grp === grp).map(t => (
            <label key={t.id} className={`flex min-h-12 cursor-pointer items-center gap-2 rounded-2xl border px-4 py-3 transition has-[:focus-visible]:outline has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-brown ${type === t.id ? "border-brown bg-latte" : "border-line bg-paper hover:border-brown"}`}>
              <input type="radio" name="eventTypeId" value={t.id} checked={type === t.id} onChange={() => setType(t.id)} className="sr-only" />
              <span className="shrink-0 text-brown">{t.icon}</span><span className="text-sm font-medium leading-snug">{t.name}</span>
            </label>
          ))}
        </div>
        <p className="mt-2 text-xs text-muted">Selected: <strong>{types.find(t => t.id === type)?.name}</strong></p>
      </fieldset>
      <div className="grid gap-4 sm:grid-cols-2">
        <div><label className="label" htmlFor="traditionId">Tradition <span className="font-normal text-muted">(shapes your checklist)</span></label>
          <select className="input" id="traditionId" name="traditionId" defaultValue={v.traditionId ?? ""}><option value="">Any or mixed</option>{traditions.filter(t => t.id !== "t-any").map(t => <option key={t.id} value={t.id}>{t.name}</option>)}</select></div>
        <div><label className="label" htmlFor="cityId">City</label>
          <select className="input" id="cityId" name="cityId" defaultValue={v.cityId ?? ""} required><option value="">Choose a city</option>{groups.map(g => <optgroup key={g} label={g}>{cities.filter(c => c.group === g).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</optgroup>)}</select></div>
      </div>
      <div><label className="label" htmlFor="title">Name your event</label><input className="input" id="title" name="title" placeholder="Anu and Joel's wedding" defaultValue={v.title} required /></div>
      <div className="grid gap-4 sm:grid-cols-3">
        <div><label className="label" htmlFor="guestCount">Guests</label><input className="input" id="guestCount" name="guestCount" type="number" min="1" inputMode="numeric" value={guests} onChange={e => setGuests(e.target.value)} /></div>
        <div><label className="label" htmlFor="eventDate">Date <span className="font-normal text-muted">(if known)</span></label><input className="input" id="eventDate" name="eventDate" type="date" min={new Date().toISOString().slice(0, 10)} defaultValue={v.eventDate} /></div>
        <div><label className="label" htmlFor="budget">Total budget <span className="font-normal text-muted">(optional)</span></label><input className="input" id="budget" name="budget" type="number" min="0" inputMode="numeric" defaultValue={v.budget} /></div>
      </div>
      <p aria-live="polite" className={`rounded-2xl px-4 py-3 text-sm transition ${intimate ? "bg-blush" : "bg-sand text-muted"}`}>
        {intimate ? "Intimate event: we will start you with a small-event checklist and show compact packages first." : "Tip: 50 guests or fewer gets an intimate checklist with smaller packages."}
      </p>
      {state.error && <p role="alert" className="rounded-2xl bg-blush px-4 py-3 text-sm text-danger">{state.error}</p>}
      <button className="btn-primary" disabled={pending}>{pending ? "Building your checklist…" : "Create my plan"}</button>
    </form>
  );
}

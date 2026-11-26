"use client";
import { useActionState } from "react";
import { joinAsVendor, type FormState } from "@/app/actions";

type City = { id: string; name: string; group: string };
export function JoinForm({ cities, traditions }: { cities: City[]; traditions: { id: string; name: string }[] }) {
  const [state, action, pending] = useActionState<FormState, FormData>(joinAsVendor, {});
  const v = state.fields ?? {};
  const groups = [...new Set(cities.map(c => c.group))];
  return (
    <form action={action} className="grid gap-5" noValidate>
      <div><label className="label" htmlFor="businessName">Business name</label><input className="input" id="businessName" name="businessName" defaultValue={v.businessName} autoComplete="organization" required /></div>
      <div><label className="label" htmlFor="phone">WhatsApp number</label><input className="input" id="phone" name="phone" type="tel" inputMode="tel" placeholder="+91 98470 12345" defaultValue={v.phone} required /><p className="mt-1 text-xs text-muted">Booking requests arrive here.</p></div>
      <div><label className="label" htmlFor="cityId">Where are you based?</label>
        <select className="input" id="cityId" name="cityId" defaultValue={v.cityId ?? ""} required>
          <option value="">Choose a city</option>
          {groups.map(g => <optgroup key={g} label={g}>{cities.filter(c => c.group === g).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</optgroup>)}
        </select></div>
      <fieldset><legend className="label">Ceremonies you know well <span className="font-normal text-muted">(optional)</span></legend>
        <div className="flex flex-wrap gap-2">{traditions.map(t => <label key={t.id} className="chip cursor-pointer has-[:checked]:border-brown has-[:checked]:bg-latte"><input type="checkbox" name="traditionIds" value={t.id} className="accent-[var(--brown)]" />{t.name}</label>)}</div>
      </fieldset>
      <div><label className="label" htmlFor="bio">Tell customers about your work <span className="font-normal text-muted">(optional)</span></label><textarea className="input h-28 py-3" id="bio" name="bio" maxLength={400} defaultValue={v.bio} /></div>
      {state.error && <p role="alert" className="rounded-2xl bg-blush px-4 py-3 text-sm text-danger">{state.error}</p>}
      <button className="btn-primary" disabled={pending}>{pending ? "Creating your profile…" : "Create my free profile"}</button>
    </form>
  );
}

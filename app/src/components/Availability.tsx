import type { Block } from "@/lib/data";
import type { Booking } from "@/lib/types";
import { niceDate } from "@/lib/format";
import { removeBlockAction } from "@/app/actions";
import { BlockForm } from "./BlockForm";

const iso = (d: Date) => d.toISOString().slice(0, 10);
const inRange = (d: string, a: string, b: string) => d >= a && d <= b;

/** Vendor dashboard: two months at a glance (booked, requested, blocked) and the form to block days. */
export function Availability({ vendorId, handle, blocks, bookings }: { vendorId: string; handle: string; blocks: Block[]; bookings: Booking[] }) {
  const now = new Date(); const today = iso(now);
  const live = bookings.filter(b => b.status === "accepted" || b.status === "requested");
  const months = [0, 1].map(k => new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + k, 1)));
  const state = (d: string) => live.some(b => b.status === "accepted" && inRange(d, b.startsOn, b.endsOn)) ? "booked"
    : live.some(b => inRange(d, b.startsOn, b.endsOn)) ? "requested" : blocks.some(x => inRange(d, x.startsOn, x.endsOn)) ? "blocked" : "free";
  const style = { booked: "bg-sage text-success font-semibold", requested: "bg-caramel text-caramel-on", blocked: "bg-latte text-muted line-through", free: "" } as const;
  const label = { booked: "booked", requested: "request waiting", blocked: "blocked", free: "free" } as const;
  return (
    <section className="card mt-10 p-6" aria-labelledby="av">
      <h2 id="av" className="font-display text-2xl">Availability</h2>
      <p className="mt-1 text-sm text-muted">Block days you are not working. Customers cannot request them. Booked days are blocked for you automatically.</p>
      <div className="mt-6 grid gap-8 lg:grid-cols-[1fr_340px]">
        <div className="grid gap-6 sm:grid-cols-2">
          {months.map(m => {
            const first = (m.getUTCDay() + 6) % 7; const n = new Date(Date.UTC(m.getUTCFullYear(), m.getUTCMonth() + 1, 0)).getUTCDate();
            return <div key={m.toISOString()}>
              <h3 className="font-medium">{m.toLocaleDateString("en-GB", { month: "long", year: "numeric", timeZone: "UTC" })}</h3>
              <div className="mt-2 grid grid-cols-7 gap-1 text-center text-xs" role="list">
                {["M", "T", "W", "T", "F", "S", "S"].map((d, i) => <span key={i} aria-hidden className="text-muted">{d}</span>)}
                {Array.from({ length: first }, (_, i) => <span key={`b${i}`} aria-hidden />)}
                {Array.from({ length: n }, (_, i) => { const d = iso(new Date(Date.UTC(m.getUTCFullYear(), m.getUTCMonth(), i + 1))); const s = state(d);
                  return <span key={d} role="listitem" aria-label={`${niceDate(d)}, ${label[s]}`} className={`rounded-md py-1.5 ${style[s]} ${d < today ? "opacity-40" : ""} ${d === today ? "ring-1 ring-brown" : ""}`}>{i + 1}</span>; })}
              </div>
            </div>;
          })}
          <p className="flex flex-wrap gap-3 text-xs text-muted sm:col-span-2">{(["booked", "requested", "blocked"] as const).map(k => <span key={k} className="flex items-center gap-1"><span className={`inline-block h-3 w-3 rounded ${style[k]}`} aria-hidden />{label[k]}</span>)}</p>
        </div>
        <div>
          <BlockForm vendorId={vendorId} handle={handle} today={today} />
          {blocks.length > 0 && <ul className="mt-6 grid gap-2">{blocks.map(b => (
            <li key={b.id} className="flex items-center justify-between gap-3 rounded-xl bg-sand px-4 py-2 text-sm">
              <span>{b.startsOn === b.endsOn ? niceDate(b.startsOn) : `${niceDate(b.startsOn)} to ${niceDate(b.endsOn)}`}{b.note && <span className="text-muted"> · {b.note}</span>}</span>
              <form action={removeBlockAction}><input type="hidden" name="blockId" value={b.id} /><input type="hidden" name="handle" value={handle} /><button className="underline">Unblock</button></form>
            </li>))}</ul>}
        </div>
      </div>
    </section>
  );
}

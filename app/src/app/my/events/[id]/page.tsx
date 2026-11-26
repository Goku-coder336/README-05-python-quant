import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { ArrowRight, CheckCircle, X } from "@phosphor-icons/react/dist/ssr";
import { currentUser } from "@/lib/auth";
import { categories } from "@/lib/data";
import { eventBookings, eventItems, myEvent, shortlistFor, type EventItem } from "@/lib/planner";
import { money, niceDate } from "@/lib/format";
import { CategoryIcon } from "@/components/Icon";
import { AddItemForm } from "@/components/AddItemForm";
import { deleteEventAction, removeItemAction, setItemStatusAction, unsaveAction } from "@/app/actions";

export const metadata = { title: "Your event" };

const statusStyle = { todo: "bg-sand text-muted", shortlisted: "bg-latte text-brown", booked: "bg-brown text-brown-on", skipped: "bg-paper text-muted line-through" } as const;
const statusText = { todo: "To do", shortlisted: "Shortlisted", booked: "Booked", skipped: "Skipped" } as const;

export default async function EventHub({ params }: { params: Promise<{ id: string }> }) {
  const id = (await params).id;
  const user = await currentUser(); if (!user) redirect(`/signin?next=/my/events/${id}`);
  const ev = await myEvent(id, user.id); if (!ev) notFound();
  const [items, saved, bookings, cats] = await Promise.all([eventItems(id, user.id), shortlistFor(id, user.id), eventBookings(id, user.id), categories()]);

  const active = items.filter(i => i.status !== "skipped");
  const booked = active.filter(i => i.status === "booked").length;
  const committed = bookings.reduce((s, b) => s + b.subtotalMinor, 0);
  const daysLeft = ev.eventDate ? Math.ceil((Date.parse(ev.eventDate) - Date.now()) / 86400000) : null;
  const groups = items.reduce<Record<string, EventItem[]>>((g, i) => ((g[i.subEvent] ??= []).push(i), g), {});
  const findHref = (i: EventItem) => {
    const p = new URLSearchParams({ for: i.id });
    if (ev.sizeTier === "intimate" && i.categoryKind === "service") p.set("intimate", "1");
    return `/${ev.countryCode}/${ev.citySlug}/${i.categorySlug}?${p}`;
  };

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 md:px-8 md:py-14">
      <Link href="/my/events" className="text-sm text-muted hover:underline">← My events</Link>

      <header className="card mt-4 overflow-hidden">
        <div className="bg-espresso p-6 text-paper md:p-8">
          <p className="text-xs font-semibold uppercase tracking-widest text-caramel">{ev.tradition ? `${ev.tradition} ` : ""}{ev.eventType.toLowerCase()} · {ev.city}{ev.guestCount ? ` · ${ev.guestCount} guests` : ""}{ev.sizeTier === "intimate" ? " · intimate" : ""}</p>
          <h1 className="mt-2 font-display text-4xl md:text-5xl">{ev.title}</h1>
          <p className="mt-2 text-paper/80">{ev.eventDate ? `${niceDate(ev.eventDate)}${daysLeft !== null && daysLeft >= 0 ? ` · ${daysLeft} days to go` : ""}` : "Date not set yet"}</p>
        </div>
        <div className="grid gap-4 p-6 sm:grid-cols-3 md:p-8">
          <div><p className="text-xs text-muted">Checklist</p><p className="mt-1 font-display text-3xl">{booked}<span className="text-lg text-muted"> of {active.length} booked</span></p>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-sand" role="progressbar" aria-valuemin={0} aria-valuemax={active.length} aria-valuenow={booked} aria-label="Items booked"><div className="h-full rounded-full bg-brown transition-[width] duration-700 ease-out" style={{ width: `${active.length ? (booked / active.length) * 100 : 0}%` }} /></div></div>
          <div className="sm:col-span-2"><p className="text-xs text-muted">Budget</p>
            {ev.budgetMinor ? <>
              <p className="mt-1 font-display text-3xl">{money(committed, ev.currency)}<span className="text-lg text-muted"> of {money(ev.budgetMinor, ev.currency)} committed</span></p>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-sand" role="progressbar" aria-valuemin={0} aria-valuemax={ev.budgetMinor} aria-valuenow={committed} aria-label="Budget committed"><div className={`h-full rounded-full ${committed > ev.budgetMinor ? "bg-danger" : "bg-caramel"}`} style={{ width: `${Math.min(100, (committed / ev.budgetMinor) * 100)}%` }} /></div>
              {committed > ev.budgetMinor && <p className="mt-1 text-sm text-danger">Over budget by {money(committed - ev.budgetMinor, ev.currency)}.</p>}
            </> : <p className="mt-1 text-muted">{money(committed, ev.currency)} committed. Add a budget when you create your next event to track it here.</p>}
          </div>
        </div>
      </header>

      {items.length === 0 && <div className="card mt-8 p-8 text-center"><h2 className="font-display text-2xl">Your checklist is empty</h2><p className="mt-2 text-muted">Add the first thing you need below.</p></div>}

      {Object.entries(groups).map(([sub, list]) => (
        <section key={sub} className="mt-10" aria-labelledby={`g-${sub}`}>
          <h2 id={`g-${sub}`} className="font-display text-2xl">{sub}</h2>
          <ul className="mt-4 grid gap-3">
            {list.map(i => {
              const mine = saved.filter(s => s.eventItemId === i.id);
              const bk = bookings.filter(b => b.eventItemId === i.id);
              const budgetHint = ev.budgetMinor && i.budgetShare ? money(Math.round(ev.budgetMinor * i.budgetShare / 100), ev.currency) : null;
              return (
                <li key={i.id} className={`card p-5 ${i.status === "skipped" ? "opacity-60" : ""}`}>
                  <div className="flex flex-wrap items-start gap-4">
                    <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-latte text-brown"><CategoryIcon name={i.categoryIcon} size={20} /></span>
                    <div className="min-w-0 flex-1">
                      <p className="font-medium">{i.label}</p>
                      <p className="text-sm text-muted">{i.categoryName}{i.note && ` · ${i.note}`}{budgetHint && ` · around ${budgetHint}`}</p>
                    </div>
                    <span className={`badge ${statusStyle[i.status]}`}>{statusText[i.status]}</span>
                  </div>

                  {bk.length > 0 && <ul className="mt-4 grid gap-2">{bk.map(b => (
                    <li key={b.id} className="flex flex-wrap items-center justify-between gap-2 rounded-2xl bg-sand px-4 py-3 text-sm">
                      <span className="flex items-center gap-2"><CheckCircle size={18} weight="fill" className="text-brown" aria-hidden /><Link href={`/bookings/${b.id}`} className="font-medium hover:underline">{b.itemTitle}</Link></span>
                      <span className="text-muted">{niceDate(b.startsOn)} · {money(b.subtotalMinor, b.currency)} · {b.status === "requested" ? "waiting for vendor" : b.status}</span>
                    </li>))}</ul>}

                  {mine.length > 0 && i.status !== "booked" && <ul className="mt-4 grid gap-2" aria-label="Shortlisted">{mine.map(s => (
                    <li key={s.itemId} className="flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-line px-4 py-3 text-sm">
                      <span><Link href={`/${s.itemKind === "service" ? "s" : "e"}/${s.itemId}?for=${i.id}`} className="font-medium hover:underline">{s.title}</Link> <span className="text-muted">· {s.vendor} · {money(s.priceMinor, s.currency)}{s.itemKind === "equipment" ? " per day" : ""}</span></span>
                      <span className="flex items-center gap-2">
                        <Link href={`/${s.itemKind === "service" ? "s" : "e"}/${s.itemId}?for=${i.id}`} className="btn-primary !px-3 !py-1.5 text-xs">Book</Link>
                        <form action={unsaveAction}><input type="hidden" name="eventId" value={ev.id} /><input type="hidden" name="eventItemId" value={i.id} /><input type="hidden" name="itemKind" value={s.itemKind} /><input type="hidden" name="itemId" value={s.itemId} />
                          <button className="grid h-8 w-8 place-items-center rounded-full hover:bg-sand" aria-label={`Remove ${s.title} from shortlist`}><X size={16} aria-hidden /></button></form>
                      </span>
                    </li>))}</ul>}

                  <div className="mt-4 flex flex-wrap items-center gap-2">
                    {i.status !== "booked" && i.status !== "skipped" && <Link href={findHref(i)} className="btn-line !px-4 !py-2">Find {i.categoryName.charAt(0).toLowerCase() + i.categoryName.slice(1)} <ArrowRight size={14} aria-hidden /></Link>}
                    {i.status !== "booked" && (
                      <form action={setItemStatusAction}><input type="hidden" name="eventId" value={ev.id} /><input type="hidden" name="itemId" value={i.id} />
                        <button name="status" value={i.status === "skipped" ? (mine.length ? "shortlisted" : "todo") : "skipped"} className="btn !px-4 !py-2 text-muted hover:bg-sand">{i.status === "skipped" ? "Bring back" : "Not needed"}</button></form>
                    )}
                    {i.status !== "booked" && bk.length === 0 && <form action={removeItemAction}><input type="hidden" name="eventId" value={ev.id} /><input type="hidden" name="itemId" value={i.id} /><button className="btn !px-4 !py-2 text-muted hover:bg-sand">Remove</button></form>}
                  </div>
                </li>
              );
            })}
          </ul>
        </section>
      ))}

      <section className="card mt-12 p-6" aria-labelledby="add"><h2 id="add" className="font-display text-2xl">Add something else</h2><p className="mb-4 mt-1 text-sm text-muted">Anything your family needs that is not on the list.</p>
        <AddItemForm eventId={ev.id} categories={cats.map(c => ({ id: c.id, name: c.name }))} subEvents={Object.keys(groups)} />
      </section>

      <form action={deleteEventAction} className="mt-10 text-right"><input type="hidden" name="eventId" value={ev.id} /><button className="text-sm text-muted underline-offset-4 hover:text-danger hover:underline">Delete this event</button></form>
    </div>
  );
}

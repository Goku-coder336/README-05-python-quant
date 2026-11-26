import Link from "next/link";
import { redirect } from "next/navigation";
import { CalendarBlank } from "@phosphor-icons/react/dist/ssr";
import { currentUser } from "@/lib/auth";
import { eventItems, myEvents } from "@/lib/planner";
import { niceDate } from "@/lib/format";
export const metadata = { title: "My events" };
export default async function MyEvents() {
  const u = await currentUser(); if (!u) redirect("/signin?next=/my/events");
  const evs = await myEvents(u.id);
  const progress = await Promise.all(evs.map(async e => { const it = (await eventItems(e.id, u.id)).filter(i => i.status !== "skipped"); return { done: it.filter(i => i.status === "booked").length, total: it.length }; }));
  return (
    <div className="mx-auto max-w-4xl px-4 py-12 md:py-20">
      <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="eyebrow">Event planner</p><h1 className="mt-3 font-display text-4xl md:text-5xl">My events</h1></div><Link href="/plan" className="btn-primary">Plan a new event</Link></div>
      {evs.length === 0 ? (
        <div className="card mt-10 p-10 text-center"><CalendarBlank size={40} className="mx-auto text-muted" aria-hidden /><h2 className="mt-3 font-display text-2xl">No events yet</h2><p className="mx-auto mt-2 max-w-md text-muted">Start a plan and get a checklist made for your occasion and tradition.</p><Link href="/plan" className="btn-primary mt-6">Start planning</Link></div>
      ) : (
        <ul className="mt-10 grid gap-4">{evs.map((e, i) => (
          <li key={e.id}><Link href={`/my/events/${e.id}`} className="card block p-6 transition hover:-translate-y-0.5 hover:border-brown">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted">{e.tradition ? `${e.tradition} ` : ""}{e.eventType.toLowerCase()} · {e.city}{e.sizeTier === "intimate" && " · intimate"}</p>
            <h2 className="mt-1 font-display text-2xl">{e.title}</h2>
            <p className="mt-1 text-sm text-muted">{e.eventDate ? niceDate(e.eventDate) : "Date not set"} · {progress[i].done} of {progress[i].total} booked</p>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-sand" aria-hidden><div className="h-full rounded-full bg-brown" style={{ width: `${progress[i].total ? (progress[i].done / progress[i].total) * 100 : 0}%` }} /></div>
          </Link></li>))}</ul>
      )}
    </div>
  );
}

import Link from "next/link";
import { notFound } from "next/navigation";
import { CheckCircle, SealCheck } from "@phosphor-icons/react/dist/ssr";
import { categories, region, service, traditions, vendorById } from "@/lib/data";
import { money, unitLabel } from "@/lib/format";
import { BookForm } from "@/components/BookForm";
import { SaveToEvent } from "@/components/SaveToEvent";
import { Gallery } from "@/components/Gallery";
import { photosFor } from "@/lib/media";
import { currentUser } from "@/lib/auth";
import { itemContext, myEvents } from "@/lib/planner";

export default async function ServicePage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ for?: string }> }) {
  const s = await service((await params).id); if (!s) notFound();
  const user = await currentUser(); const forId = (await searchParams).for;
  const ctx = user && forId ? await itemContext(forId, user.id) : null;
  const events = user ? (await myEvents(user.id)).map(x => ({ id: x.id, title: x.title })) : [];
  const v = (await vendorById(s.vendorId))!; const cat = (await categories()).find(c => c.id === s.categoryId)!; const city = (await region(v.baseRegionId))!;
  const trads = (await traditions()).filter(t => s.traditionIds.includes(t.id));
  return (
    <div className="mx-auto grid max-w-6xl gap-10 px-4 py-10 md:px-8 lg:grid-cols-[1fr_400px] lg:py-16">
      <div>
        <p className="text-sm text-muted">{cat.name} · {city.name}</p>
        <h1 className="mt-2 font-display text-4xl md:text-5xl">{s.title}</h1>
        <p className="mt-3 text-sm">by <Link href={`/v/${v.handle}`} className="font-medium underline-offset-4 hover:underline">{v.businessName}</Link>{v.verification === "verified" && <span className="badge ml-2 bg-sage text-success"><SealCheck size={12} weight="fill" aria-hidden />Verified</span>}</p>
        <div className="mt-8"><Gallery photos={await photosFor("service", s.id)} title={s.title} /></div>
        <p className="mt-8 text-lg leading-relaxed">{s.description}</p>
        {s.included.length > 0 && <><h2 className="mt-10 font-display text-2xl">What is included</h2><ul className="mt-4 grid gap-2">{s.included.map(i => <li key={i} className="flex gap-2"><CheckCircle size={20} weight="fill" className="mt-0.5 shrink-0 text-brown" aria-hidden />{i}</li>)}</ul></>}
        <div className="mt-10 flex flex-wrap gap-2">
          {s.maxGuests && <span className="chip">Up to {s.maxGuests} guests</span>}
          {s.styles.map(x => <span key={x} className="chip capitalize">{x}</span>)}
          {trads.map(t => <span key={t.id} className="chip">{t.name}</span>)}
        </div>
      </div>
      <aside className="card h-fit p-6 lg:sticky lg:top-24" aria-label="Request a booking">
        <p className="text-2xl font-semibold">{money(s.priceMinor, s.currency)} <span className="text-base font-normal text-muted">{unitLabel[s.priceUnit]}</span></p>
        <p className="mt-1 text-sm text-muted">{s.advancePct}% advance once confirmed</p>
        {ctx && <p className="mb-6 rounded-2xl bg-latte px-4 py-3 text-sm">Booking for <strong>{ctx.label}</strong> in <Link href={`/my/events/${ctx.eventId}`} className="font-medium underline">{ctx.eventTitle}</Link></p>}
        <div className="mt-6"><BookForm kind="service" itemId={s.id} eventItemId={ctx?.itemId} defaultDate={ctx?.eventDate} cta="Request this date" /></div>
        <div className="mt-4 border-t border-line pt-4"><SaveToEvent itemKind="service" itemId={s.id} events={events} signedIn={!!user} next={`/s/${s.id}`} /></div>
      </aside>
    </div>
  );
}

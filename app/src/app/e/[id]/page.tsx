import Link from "next/link";
import { notFound } from "next/navigation";
import { ShieldCheck, Wrench } from "@phosphor-icons/react/dist/ssr";
import { categories, equipmentItem, region, vendorById } from "@/lib/data";
import { money } from "@/lib/format";
import { BookForm } from "@/components/BookForm";
import { SaveToEvent } from "@/components/SaveToEvent";
import { Gallery } from "@/components/Gallery";
import { photosFor } from "@/lib/media";
import { currentUser } from "@/lib/auth";
import { itemContext, myEvents } from "@/lib/planner";

export default async function EquipmentPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ for?: string }> }) {
  const e = await equipmentItem((await params).id); if (!e) notFound();
  const user = await currentUser(); const forId = (await searchParams).for;
  const ctx = user && forId ? await itemContext(forId, user.id) : null;
  const events = user ? (await myEvents(user.id)).map(x => ({ id: x.id, title: x.title })) : [];
  const v = (await vendorById(e.vendorId))!; const cat = (await categories()).find(c => c.id === e.categoryId)!; const city = (await region(v.baseRegionId))!;
  return (
    <div className="mx-auto grid max-w-6xl gap-10 px-4 py-10 md:px-8 lg:grid-cols-[1fr_400px] lg:py-16">
      <div>
        <p className="text-sm text-muted">{cat.name} · {city.name}</p>
        <h1 className="mt-2 font-display text-4xl md:text-5xl">{e.title}</h1>
        <p className="mt-3 text-sm">from <Link href={`/v/${v.handle}`} className="font-medium hover:underline">{v.businessName}</Link></p>
        <div className="mt-8"><Gallery photos={await photosFor("equipment", e.id)} title={e.title} dark /></div>
        <p className="mt-8 text-lg leading-relaxed">{e.description}</p>
        {Object.keys(e.specs).length > 0 && <dl className="mt-8 grid grid-cols-2 gap-3">{Object.entries(e.specs).map(([k, val]) => <div key={k} className="card p-4"><dt className="text-xs text-muted">{k}</dt><dd className="font-medium">{val}</dd></div>)}</dl>}
        <div className="mt-8 grid gap-3 sm:grid-cols-2">
          <p className="card flex gap-3 p-4 text-sm"><ShieldCheck size={22} className="shrink-0 text-brown" aria-hidden />Deposit of {money(e.depositMinor, e.currency)} is held, then released after the gear is returned and checked.</p>
          {e.needsOperator && <p className="card flex gap-3 p-4 text-sm"><Wrench size={22} className="shrink-0 text-brown" aria-hidden />Comes with a technician who sets up and runs it.</p>}
        </div>
      </div>
      <aside className="card h-fit p-6 lg:sticky lg:top-24" aria-label="Request a rental">
        <p className="text-2xl font-semibold">{money(e.dayRateMinor, e.currency)} <span className="text-base font-normal text-muted">per day</span></p>
        <p className="mt-1 text-sm text-muted">{e.units} {e.units === 1 ? "unit" : "units"} available · deposit {money(e.depositMinor, e.currency)}</p>
        {ctx && <p className="mb-6 rounded-2xl bg-latte px-4 py-3 text-sm">Booking for <strong>{ctx.label}</strong> in <Link href={`/my/events/${ctx.eventId}`} className="font-medium underline">{ctx.eventTitle}</Link></p>}
        <div className="mt-6"><BookForm kind="equipment" itemId={e.id} eventItemId={ctx?.itemId} defaultDate={ctx?.eventDate} cta="Check dates and request" /></div>
        <div className="mt-4 border-t border-line pt-4"><SaveToEvent itemKind="equipment" itemId={e.id} events={events} signedIn={!!user} next={`/e/${e.id}`} /></div>
      </aside>
    </div>
  );
}

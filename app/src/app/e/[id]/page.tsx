import Link from "next/link";
import { notFound } from "next/navigation";
import { ShieldCheck, Wrench } from "@phosphor-icons/react/dist/ssr";
import { categories, equipmentItem, region, vendorById } from "@/lib/data";
import { money } from "@/lib/format";
import { BookForm } from "@/components/BookForm";

export default async function EquipmentPage({ params }: { params: Promise<{ id: string }> }) {
  const e = equipmentItem((await params).id); if (!e) notFound();
  const v = vendorById(e.vendorId)!; const cat = categories().find(c => c.id === e.categoryId)!; const city = region(v.baseRegionId)!;
  return (
    <div className="mx-auto grid max-w-6xl gap-10 px-4 py-10 md:px-8 lg:grid-cols-[1fr_400px] lg:py-16">
      <div>
        <p className="text-sm text-muted">{cat.name} · {city.name}</p>
        <h1 className="mt-2 font-display text-4xl md:text-5xl">{e.title}</h1>
        <p className="mt-3 text-sm">from <Link href={`/v/${v.handle}`} className="font-medium hover:underline">{v.businessName}</Link></p>
        <div className="mt-8 h-64 rounded-3xl bg-espresso md:h-80" role="img" aria-label="Equipment photos appear here once the owner uploads them" />
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
        <div className="mt-6"><BookForm kind="equipment" itemId={e.id} cta="Check dates and request" /></div>
      </aside>
    </div>
  );
}

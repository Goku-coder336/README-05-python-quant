import { notFound } from "next/navigation";
import { SealCheck } from "@phosphor-icons/react/dist/ssr";
import { region, traditions, vendorByHandle, vendorItems } from "@/lib/data";
import { ListingCard } from "@/components/ListingCard";

export default async function VendorProfile({ params }: { params: Promise<{ handle: string }> }) {
  const v = await vendorByHandle((await params).handle); if (!v) notFound();
  const { services, equipment } = await vendorItems(v.id); const city = await region(v.baseRegionId); const trads = await traditions();
  const items = [...services.filter(s => s.status === "live").map(item => ({ kind: "service" as const, item, vendor: v })), ...equipment.filter(e => e.status === "live").map(item => ({ kind: "equipment" as const, item, vendor: v }))];
  return (
    <div className="mx-auto max-w-6xl px-4 py-10 md:px-8 md:py-16">
      <div className="flex flex-wrap items-center gap-4">
        <div className="grid h-16 w-16 place-items-center rounded-full bg-brown font-display text-2xl text-brown-on" aria-hidden>{v.businessName[0]}</div>
        <div>
          <h1 className="font-display text-4xl">{v.businessName}</h1>
          <p className="mt-1 text-sm text-muted">{city?.name}{v.verification === "verified" && <span className="badge ml-2 bg-sage text-success"><SealCheck size={12} weight="fill" aria-hidden />Verified</span>}{v.ratingCount > 0 && <> · ★ {v.ratingAvg.toFixed(1)} ({v.ratingCount})</>}</p>
        </div>
      </div>
      {v.bio && <p className="mt-6 max-w-2xl text-lg">{v.bio}</p>}
      <div className="mt-4 flex flex-wrap gap-2">{trads.filter(t => v.traditionIds.includes(t.id)).map(t => <span key={t.id} className="chip">{t.name}</span>)}</div>
      <h2 className="mt-12 font-display text-2xl">Packages and rentals</h2>
      {items.length === 0 ? <p className="mt-4 text-muted">No listings yet.</p> :
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{items.map(l => <div key={l.item.id} className="relative"><ListingCard l={l} /></div>)}</div>}
    </div>
  );
}

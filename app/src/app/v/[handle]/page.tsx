import { notFound } from "next/navigation";
import { SealCheck } from "@phosphor-icons/react/dist/ssr";
import { region, traditions, vendorByHandle, vendorItems } from "@/lib/data";
import { ListingCard } from "@/components/ListingCard";
import { coversFor, photosFor } from "@/lib/media";
import { vendorReviews } from "@/lib/reviews";
import { ReviewList } from "@/components/ReviewList";
import { Stars } from "@/components/Stars";

export default async function VendorProfile({ params }: { params: Promise<{ handle: string }> }) {
  const v = await vendorByHandle((await params).handle); if (!v) notFound();
  const { services, equipment } = await vendorItems(v.id); const city = await region(v.baseRegionId); const trads = await traditions(); const portfolio = await photosFor("vendor", v.id); const revs = await vendorReviews(v.id);
  const items = [...services.filter(s => s.status === "live").map(item => ({ kind: "service" as const, item, vendor: v })), ...equipment.filter(e => e.status === "live").map(item => ({ kind: "equipment" as const, item, vendor: v }))];
  const covers = await coversFor(items.map(l => ({ kind: l.kind, id: l.item.id })));
  return (
    <div className="mx-auto max-w-6xl px-4 py-10 md:px-8 md:py-16">
      <div className="flex flex-wrap items-center gap-4">
        <div className="grid h-16 w-16 place-items-center rounded-full bg-brown font-display text-2xl text-brown-on" aria-hidden>{v.businessName[0]}</div>
        <div>
          <h1 className="font-display text-4xl">{v.businessName}</h1>
          <p className="mt-1 text-sm text-muted">{city?.name}{v.verification === "verified" && <span className="badge ml-2 bg-sage text-success"><SealCheck size={12} weight="fill" aria-hidden />Verified</span>}{v.ratingCount > 0 && <> · <Stars value={v.ratingAvg} size={14} /> {v.ratingAvg.toFixed(1)} ({v.ratingCount})</>}</p>
        </div>
      </div>
      {v.bio && <p className="mt-6 max-w-2xl text-lg">{v.bio}</p>}
      <div className="mt-4 flex flex-wrap gap-2">{trads.filter(t => v.traditionIds.includes(t.id)).map(t => <span key={t.id} className="chip">{t.name}</span>)}</div>
      {portfolio.length > 0 && <><h2 className="mt-12 font-display text-2xl">Portfolio</h2>
        <ul className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">{portfolio.map((p, i) => <li key={p.id}>{/* eslint-disable-next-line @next/next/no-img-element */}<img src={p.url} alt={`${v.businessName} work, photo ${i + 1}`} width={p.width} height={p.height} loading="lazy" className="aspect-square w-full rounded-2xl bg-latte object-cover" /></li>)}</ul></>}
      <h2 className="mt-12 font-display text-2xl">Packages and rentals</h2>
      {items.length === 0 ? <p className="mt-4 text-muted">No listings yet.</p> :
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{items.map(l => <div key={l.item.id} className="relative"><ListingCard l={l} cover={covers.get(l.item.id)} /></div>)}</div>}
      <section className="mt-12" aria-labelledby="rv"><h2 id="rv" className="font-display text-2xl">Reviews{revs.length > 0 && <span className="ml-2 align-middle text-base font-normal text-muted">{v.ratingAvg.toFixed(1)} from {revs.length}</span>}</h2>
        <ReviewList reviews={revs} vendorName={v.businessName} empty="No reviews yet. Reviews come only from customers who booked through Utsella." /></section>
    </div>
  );
}

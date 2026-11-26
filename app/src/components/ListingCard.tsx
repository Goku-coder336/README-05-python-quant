import Link from "next/link";
import { SealCheck, Users, Wrench } from "@phosphor-icons/react/dist/ssr";
import type { Listing } from "@/lib/data";
import { money, unitLabel } from "@/lib/format";

export function ListingCard({ l, forItem }: { l: Listing; forItem?: string }) {
  const href = (l.kind === "service" ? `/s/${l.item.id}` : `/e/${l.item.id}`) + (forItem ? `?for=${encodeURIComponent(forItem)}` : "");
  const intimate = l.kind === "service" && l.item.maxGuests !== null && l.item.maxGuests <= 50;
  return (
    <article className="card group overflow-hidden transition duration-500 ease-out hover:-translate-y-1 hover:shadow-[0_20px_40px_rgba(58,38,25,.12)]">
      <div className={`flex h-36 items-end gap-2 p-3 ${l.kind === "service" ? "bg-latte" : "bg-espresso"}`}>
        {l.kind === "equipment" && <span className="badge bg-paper/15 text-paper"><Wrench size={12} aria-hidden />Rental{l.item.needsOperator ? " with operator" : ""}</span>}
        {intimate && <span className="badge bg-blush text-ink"><Users size={12} aria-hidden />Intimate</span>}
      </div>
      <div className="grid gap-1.5 p-4">
        <p className="text-xs text-muted">{l.vendor.businessName}{l.vendor.verification === "verified" && <SealCheck size={14} weight="fill" className="ml-1 inline text-success" aria-label="Verified" />}</p>
        <h3 className="line-clamp-2 font-medium leading-snug"><Link href={href} className="after:absolute after:inset-0 focus-visible:outline-none">{l.item.title}</Link></h3>
        <p className="text-sm font-semibold">
          {l.kind === "service"
            ? <>{money(l.item.priceMinor, l.item.currency)} <span className="font-normal text-muted">{unitLabel[l.item.priceUnit]}</span></>
            : <>{money(l.item.dayRateMinor, l.item.currency)} <span className="font-normal text-muted">per day · deposit {money(l.item.depositMinor, l.item.currency)}</span></>}
        </p>
        {l.vendor.ratingCount > 0 && <p className="text-xs text-muted">★ {l.vendor.ratingAvg.toFixed(1)} ({l.vendor.ratingCount} reviews)</p>}
      </div>
    </article>
  );
}

import Link from "next/link";
import { notFound } from "next/navigation";
import { CheckCircle } from "@phosphor-icons/react/dist/ssr";
import { booking, vendorById } from "@/lib/data";
import { money, niceDate } from "@/lib/format";

const label = { requested: "Waiting for the vendor", accepted: "Confirmed by the vendor", declined: "Declined by the vendor", cancelled: "Cancelled", completed: "Completed" } as const;

export default async function BookingPage({ params }: { params: Promise<{ id: string }> }) {
  const b = await booking((await params).id); if (!b) notFound();
  const v = (await vendorById(b.vendorId))!;
  return (
    <div className="mx-auto max-w-xl px-4 py-16">
      <CheckCircle size={48} weight="fill" className="text-success" aria-hidden />
      <h1 className="mt-4 font-display text-4xl">Request sent to {v.businessName}</h1>
      <p className="mt-3 text-muted">They will confirm on WhatsApp. Once confirmed you pay the advance here.</p>
      <dl className="card mt-8 divide-y divide-line">
        {[["Status", label[b.status]], ["Item", b.itemTitle], ["Dates", b.startsOn === b.endsOn ? niceDate(b.startsOn) : `${niceDate(b.startsOn)} to ${niceDate(b.endsOn)}`], ["Price", money(b.subtotalMinor, b.currency)], ["Tax", money(b.taxMinor, b.currency)], ...(b.depositMinor ? [["Refundable deposit", money(b.depositMinor, b.currency)]] : [])].map(([k, val]) => (
          <div key={k} className="flex justify-between gap-4 p-4 text-sm"><dt className="text-muted">{k}</dt><dd className="text-right font-medium">{val}</dd></div>
        ))}
      </dl>
      <p className="mt-4 text-xs text-muted">Reference {b.id}</p>
      <Link href={`/v/${v.handle}`} className="btn-line mt-8">Back to {v.businessName}</Link>
    </div>
  );
}

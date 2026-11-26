import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { currentUser } from "@/lib/auth";
import { canViewBooking } from "@/lib/data";
import { CheckCircle } from "@phosphor-icons/react/dist/ssr";
import { booking, vendorById } from "@/lib/data";
import { money, niceDate } from "@/lib/format";

const label = { requested: "Waiting for the vendor", accepted: "Confirmed by the vendor", declined: "Declined by the vendor", cancelled: "Cancelled", completed: "Completed" } as const;

export default async function BookingPage({ params }: { params: Promise<{ id: string }> }) {
  const id = (await params).id;
  const user = await currentUser(); if (!user) redirect(`/signin?next=/bookings/${id}`);
  const b = await booking(id); if (!b || !(await canViewBooking(id, user.id))) notFound();
  const isCustomer = b.customerId === user.id;
  const v = (await vendorById(b.vendorId))!;
  return (
    <div className="mx-auto max-w-xl px-4 py-16">
      <CheckCircle size={48} weight="fill" className={b.status === "declined" || b.status === "cancelled" ? "text-muted" : "text-success"} aria-hidden />
      <h1 className="mt-4 font-display text-4xl">{b.status === "requested" ? `Request sent to ${v.businessName}` : b.status === "accepted" ? `${v.businessName} confirmed` : label[b.status]}</h1>
      <p className="mt-3 text-muted">{b.status === "requested" ? "We have emailed them. You will get an email as soon as they reply." : b.status === "accepted" ? "Online payment of the advance arrives soon. For now, agree the advance directly with the vendor." : "Nothing was charged."}</p>
      <dl className="card mt-8 divide-y divide-line">
        {[["Status", label[b.status]], ["Item", b.itemTitle], ["Dates", b.startsOn === b.endsOn ? niceDate(b.startsOn) : `${niceDate(b.startsOn)} to ${niceDate(b.endsOn)}`], ["Price", money(b.subtotalMinor, b.currency)], ["Tax", money(b.taxMinor, b.currency)], ...(b.depositMinor ? [["Refundable deposit", money(b.depositMinor, b.currency)]] : [])].map(([k, val]) => (
          <div key={k} className="flex justify-between gap-4 p-4 text-sm"><dt className="text-muted">{k}</dt><dd className="text-right font-medium">{val}</dd></div>
        ))}
      </dl>
      <p className="mt-4 text-xs text-muted">Reference {b.id}</p>
      <div className="mt-8 flex flex-wrap gap-3">{isCustomer && <Link href="/my/bookings" className="btn-primary">All my bookings</Link>}{isCustomer && b.status === "accepted" && <a className="btn-line" href={`https://wa.me/${v.phone.replace("+", "")}`}>Message on WhatsApp</a>}<Link href={`/v/${v.handle}`} className="btn-line">{v.businessName}</Link></div>
    </div>
  );
}

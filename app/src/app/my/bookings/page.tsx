import Link from "next/link";
import { redirect } from "next/navigation";
import { CalendarCheck, WhatsappLogo } from "@phosphor-icons/react/dist/ssr";
import { currentUser } from "@/lib/auth";
import { customerBookings } from "@/lib/data";
import { money, niceDate } from "@/lib/format";
import { cancelBookingAction } from "@/app/actions";
export const metadata = { title: "My bookings" };
const label = { requested: "Waiting for vendor", accepted: "Confirmed", declined: "Declined", cancelled: "Cancelled", completed: "Completed" } as const;
const pill = { requested: "bg-caramel text-caramel-on", accepted: "bg-brown text-brown-on", declined: "bg-blush text-danger", cancelled: "bg-sand text-muted", completed: "bg-sage text-success" } as const;

export default async function MyBookings() {
  const u = await currentUser(); if (!u) redirect("/signin?next=/my/bookings");
  const list = await customerBookings(u.id);
  const open = list.filter(b => b.status === "requested" || b.status === "accepted"); const past = list.filter(b => !open.includes(b));
  const Row = ({ b }: { b: (typeof list)[number] }) => (
    <li className="card p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div><Link href={`/bookings/${b.id}`} className="font-medium hover:underline">{b.itemTitle}</Link>
          <p className="text-sm text-muted">{b.vendorName} · {b.startsOn === b.endsOn ? niceDate(b.startsOn) : `${niceDate(b.startsOn)} to ${niceDate(b.endsOn)}`}{b.eventTitle && <> · <Link className="underline" href={`/my/events/${b.eventId}`}>{b.eventTitle}</Link></>}</p>
          <p className="mt-1 text-sm font-semibold">{money(b.subtotalMinor, b.currency)}{b.depositMinor > 0 && <span className="font-normal text-muted"> + {money(b.depositMinor, b.currency)} refundable deposit</span>}</p></div>
        <span className={`badge ${pill[b.status]}`}>{label[b.status]}</span>
      </div>
      {(b.status === "requested" || b.status === "accepted") && (
        <div className="mt-4 flex flex-wrap gap-2">
          {b.status === "accepted" && <a className="btn-line !py-2" href={`https://wa.me/${b.vendorPhone.replace("+", "")}`}><WhatsappLogo size={16} aria-hidden />Message {b.vendorName}</a>}
          <form action={cancelBookingAction}><input type="hidden" name="bookingId" value={b.id} /><button className="btn !py-2 text-muted hover:bg-sand">{b.status === "requested" ? "Withdraw request" : "Cancel booking"}</button></form>
        </div>
      )}
    </li>
  );
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 md:py-20">
      <p className="eyebrow">Your bookings</p><h1 className="mt-3 font-display text-4xl md:text-5xl">My bookings</h1>
      {list.length === 0 ? (
        <div className="card mt-10 p-10 text-center"><CalendarCheck size={40} className="mx-auto text-muted" aria-hidden /><h2 className="mt-3 font-display text-2xl">No bookings yet</h2><p className="mx-auto mt-2 max-w-md text-muted">Requests you send to vendors show up here, with their replies.</p><div className="mt-6 flex flex-wrap justify-center gap-3"><Link href="/plan" className="btn-primary">Plan an event</Link><Link href="/explore" className="btn-line">Browse vendors</Link></div></div>
      ) : <>
        <section className="mt-10" aria-labelledby="up"><h2 id="up" className="font-display text-2xl">Upcoming and waiting</h2>{open.length ? <ul className="mt-4 grid gap-3">{open.map(b => <Row key={b.id} b={b} />)}</ul> : <p className="mt-2 text-muted">Nothing upcoming.</p>}</section>
        {past.length > 0 && <section className="mt-10" aria-labelledby="pa"><h2 id="pa" className="font-display text-2xl">Past, declined and cancelled</h2><ul className="mt-4 grid gap-3">{past.map(b => <Row key={b.id} b={b} />)}</ul></section>}
      </>}
    </div>
  );
}

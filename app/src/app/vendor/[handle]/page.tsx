import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { currentUser } from "@/lib/auth";
import { Tray } from "@phosphor-icons/react/dist/ssr";
import { categories, countries, region, vendorBookings, vendorByHandle, vendorItems } from "@/lib/data";
import { money, niceDate } from "@/lib/format";
import { decideBooking } from "@/app/actions";
import { AddListingForm } from "@/components/AddListingForm";

export const metadata = { title: "Vendor dashboard" };
const pill = { requested: "bg-caramel text-caramel-on", accepted: "bg-sage text-success", declined: "bg-blush text-danger", cancelled: "bg-latte text-muted", completed: "bg-latte text-ink" } as const;

export default async function Dashboard({ params, searchParams }: { params: Promise<{ handle: string }>; searchParams: Promise<{ welcome?: string }> }) {
  const handle = (await params).handle;
  const user = await currentUser(); if (!user) redirect(`/signin?next=/vendor/${handle}`);
  const v = await vendorByHandle(handle); if (!v || v.ownerId !== user.id) notFound();
  const welcome = (await searchParams).welcome === "1";
  const city = (await region(v.baseRegionId))!; const cur = (await countries()).find(c => c.code === city.countryCode)!.currency;
  const bookings = (await vendorBookings(v.id, user.id)) ?? []; const { services, equipment } = await vendorItems(v.id); const cats = await categories();
  const open = bookings.filter(b => b.status === "requested").length;
  return (
    <div className="mx-auto max-w-6xl px-4 py-10 md:px-8 md:py-14">
      {welcome && <p role="status" className="mb-8 rounded-2xl bg-sage px-5 py-4 text-success">Your profile is live at <Link href={`/v/${v.handle}`} className="font-semibold underline">/v/{v.handle}</Link>. Add your first listing below. We will verify your business before the badge appears.</p>}
      <div className="mt-6 flex flex-wrap items-end justify-between gap-4">
        <div><p className="eyebrow">Dashboard</p><h1 className="mt-2 font-display text-4xl">{v.businessName}</h1><p className="mt-1 text-sm text-muted">{city.name} · {v.verification === "verified" ? "Verified" : "Verification pending"}</p></div>
        <Link href={`/v/${v.handle}`} className="btn-line">View public profile</Link>
      </div>
      <div className="mt-8 grid grid-cols-3 gap-3">
        {[["New requests", open], ["Listings", services.length + equipment.length], ["All bookings", bookings.length]].map(([k, n]) => <div key={k} className="card p-4"><p className="text-xs text-muted">{k}</p><p className="mt-1 font-display text-3xl">{n}</p></div>)}
      </div>
      <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_420px]">
        <section aria-labelledby="req"><h2 id="req" className="font-display text-2xl">Booking requests</h2>
          {bookings.length === 0 ? (
            <div className="card mt-4 grid place-items-center p-10 text-center"><Tray size={36} className="text-muted" aria-hidden /><p className="mt-3 font-medium">No requests yet</p><p className="mt-1 max-w-sm text-sm text-muted">Once your listings are live, requests from customers show up here and on WhatsApp.</p></div>
          ) : (
            <ul className="mt-4 grid gap-3">{bookings.map(b => (
              <li key={b.id} className="card p-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div><p className="font-medium">{b.itemTitle}</p><p className="mt-1 text-sm text-muted">{b.startsOn === b.endsOn ? niceDate(b.startsOn) : `${niceDate(b.startsOn)} to ${niceDate(b.endsOn)}`}{b.unitIndex !== null && ` · unit ${b.unitIndex + 1}`}</p></div>
                  <span className={`badge ${pill[b.status]}`}>{b.status}</span>
                </div>
                <p className="mt-3 text-sm">{b.customerName} · <a className="underline" href={`https://wa.me/${b.customerPhone.replace("+", "")}`}>{b.customerPhone}</a></p>
                {b.note && <p className="mt-1 text-sm text-muted">“{b.note}”</p>}
                <p className="mt-2 text-sm font-semibold">{money(b.subtotalMinor, b.currency)}{b.depositMinor > 0 && <span className="font-normal text-muted"> + {money(b.depositMinor, b.currency)} deposit</span>}</p>
                {b.status === "requested" && <form action={decideBooking} className="mt-4 flex gap-2"><input type="hidden" name="handle" value={v.handle} /><input type="hidden" name="bookingId" value={b.id} /><button name="decision" value="accepted" className="btn-primary !py-2">Accept</button><button name="decision" value="declined" className="btn-line !py-2">Decline</button></form>}
              </li>))}</ul>
          )}
        </section>
        <section aria-labelledby="add" className="card h-fit p-6"><h2 id="add" className="font-display text-2xl">Add a listing</h2><p className="mb-5 mt-1 text-sm text-muted">A service package, or gear you rent out.</p>
          <AddListingForm handle={v.handle} categories={cats.map(c => ({ id: c.id, name: c.name, kind: c.kind }))} currency={cur} />
        </section>
      </div>
    </div>
  );
}

import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { currentUser } from "@/lib/auth";
import { Tray } from "@phosphor-icons/react/dist/ssr";
import { categories, countries, region, vendorBlocks, vendorBookings, vendorByHandle, vendorItems } from "@/lib/data";
import { Availability } from "@/components/Availability";
import { money, niceDate } from "@/lib/format";
import { decideBooking } from "@/app/actions";
import { AddListingForm } from "@/components/AddListingForm";
import { PhotoManager } from "@/components/PhotoManager";
import { MAX_PER_OWNER, photosFor } from "@/lib/media";
import { unitLabel } from "@/lib/format";
import { vendorReviews } from "@/lib/reviews";
import { Stars } from "@/components/Stars";
import { replyReviewAction } from "@/app/actions";

export const metadata = { title: "Vendor dashboard" };
const pill = { requested: "bg-caramel text-caramel-on", accepted: "bg-sage text-success", declined: "bg-blush text-danger", cancelled: "bg-latte text-muted", completed: "bg-latte text-ink" } as const;

export default async function Dashboard({ params, searchParams }: { params: Promise<{ handle: string }>; searchParams: Promise<{ welcome?: string }> }) {
  const handle = (await params).handle;
  const user = await currentUser(); if (!user) redirect(`/signin?next=/vendor/${handle}`);
  const v = await vendorByHandle(handle); if (!v || v.ownerId !== user.id) notFound();
  const welcome = (await searchParams).welcome === "1";
  const city = (await region(v.baseRegionId))!; const cur = (await countries()).find(c => c.code === city.countryCode)!.currency;
  const bookings = (await vendorBookings(v.id, user.id)) ?? []; const { services, equipment } = await vendorItems(v.id); const cats = await categories();
  const portfolio = await photosFor("vendor", v.id); const revs = await vendorReviews(v.id, true); const blocks = await vendorBlocks(v.id);
  const listingPhotos = new Map(await Promise.all([...services.map(s => ["service", s.id] as const), ...equipment.map(e => ["equipment", e.id] as const)].map(async ([k, id]) => [id, await photosFor(k, id)] as const)));
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
      <Availability vendorId={v.id} handle={v.handle} blocks={blocks} bookings={bookings} />
      <section className="mt-10" aria-labelledby="rvs"><h2 id="rvs" className="font-display text-2xl">Reviews {revs.length > 0 && <span className="ml-1 align-middle text-base font-normal text-muted">{v.ratingAvg.toFixed(1)} average</span>}</h2>
        {revs.length === 0 ? <p className="mt-2 text-sm text-muted">Customers can review you after their event. A short thank-you reply helps future customers trust you.</p> :
        <ul className="mt-4 grid gap-3">{revs.map(r => (
          <li key={r.id} className={`card p-5 ${r.hidden ? "opacity-60" : ""}`}>
            <div className="flex flex-wrap items-center justify-between gap-2"><span className="flex items-center gap-2"><Stars value={r.rating} /><span className="font-medium">{r.authorName}</span><span className="text-sm text-muted">· {r.itemTitle}</span></span>{r.hidden && <span className="badge bg-blush text-danger">Hidden by Utsella</span>}</div>
            {r.body && <p className="mt-2">{r.body}</p>}
            <form action={replyReviewAction} className="mt-3 grid gap-2"><input type="hidden" name="reviewId" value={r.id} /><input type="hidden" name="handle" value={v.handle} />
              <label className="text-sm font-medium" htmlFor={`rp-${r.id}`}>{r.vendorReply ? "Your public reply" : "Reply publicly"}</label>
              <textarea id={`rp-${r.id}`} name="reply" maxLength={600} defaultValue={r.vendorReply ?? ""} className="input h-20 py-2 text-sm" placeholder="Thank you, it was lovely working with your family." />
              <button className="btn-line w-fit !py-2">{r.vendorReply ? "Update reply" : "Post reply"}</button></form>
          </li>))}</ul>}
      </section>
      <section className="card mt-10 p-6" aria-labelledby="pf"><h2 id="pf" className="font-display text-2xl">Portfolio</h2><p className="mb-4 mt-1 text-sm text-muted">Your best work. Shown on your public profile.</p>
        <PhotoManager kind="vendor" ownerId={v.id} handle={v.handle} photos={portfolio} max={MAX_PER_OWNER.vendor} label="Portfolio" /></section>
      {services.length + equipment.length > 0 && <section className="mt-10" aria-labelledby="ls"><h2 id="ls" className="font-display text-2xl">Your listings</h2>
        <ul className="mt-4 grid gap-3">{[...services.map(s => ({ kind: "service" as const, id: s.id, title: s.title, price: `${money(s.priceMinor, s.currency)} ${unitLabel[s.priceUnit]}` })), ...equipment.map(e => ({ kind: "equipment" as const, id: e.id, title: e.title, price: `${money(e.dayRateMinor, e.currency)} per day · ${e.units} unit${e.units === 1 ? "" : "s"}` }))].map(l => {
          const ph = listingPhotos.get(l.id) ?? [];
          return <li key={l.id} className="card p-5"><div className="flex flex-wrap items-center justify-between gap-2"><span><span className="font-medium">{l.title}</span> <span className="text-sm text-muted">· {l.price}</span></span><span className="text-sm text-muted">{ph.length} photo{ph.length === 1 ? "" : "s"}</span></div>
            <div className="mt-4"><PhotoManager kind={l.kind} ownerId={l.id} handle={v.handle} photos={ph} max={MAX_PER_OWNER[l.kind]} label={l.title} /></div></li>;
        })}</ul></section>}
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

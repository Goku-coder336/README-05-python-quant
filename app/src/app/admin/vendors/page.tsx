import Link from "next/link";
import { adminVendors } from "@/lib/admin";
import { verifyVendorAction } from "../actions";
export const metadata = { title: "Vendors" };
export default async function AdminVendors({ searchParams }: { searchParams: Promise<{ show?: string }> }) {
  const show = ((await searchParams).show ?? "pending") as "pending" | "verified" | "all";
  const list = await adminVendors(["pending", "verified", "all"].includes(show) ? show : "pending");
  return (
    <div>
      <h1 className="font-display text-4xl">Vendors</h1>
      <p className="mt-2 max-w-2xl text-muted">Before verifying, check: ID matches the business owner, the business is real (registration, GST or a public page), and the portfolio is their own work. Call the WhatsApp number once.</p>
      <div className="mt-6 flex gap-2">{(["pending", "verified", "all"] as const).map(s => <Link key={s} href={`?show=${s}`} className={show === s ? "chip-on" : "chip"} aria-current={show === s ? "page" : undefined}>{s === "pending" ? "Waiting for review" : s === "verified" ? "Verified" : "All"}</Link>)}</div>
      {list.length === 0 ? <div className="card mt-6 p-10 text-center text-muted">{show === "pending" ? "Nobody is waiting for review." : "No vendors here."}</div> :
        <ul className="mt-6 grid gap-4">{list.map(v => (
          <li key={v.id} className="card p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div><p className="font-display text-2xl">{v.businessName}</p>
                <p className="text-sm text-muted">{v.city} · <a className="underline" href={`https://wa.me/${v.phone.replace("+", "")}`}>{v.phone}</a> · {v.ownerEmail ?? "no owner account"} · joined {new Date(v.createdAt).toLocaleDateString("en-GB")}</p>
                <p className="mt-1 text-sm text-muted">{v.listings} listings · {v.bookings} bookings · <Link className="underline" href={`/v/${v.handle}`}>public profile</Link></p></div>
              <span className={`badge ${v.verification === "verified" ? "bg-sage text-success" : "bg-caramel text-caramel-on"}`}>{v.verification === "verified" ? "Verified" : "Waiting"}</span>
            </div>
            {v.bio && <p className="mt-3 text-sm">{v.bio}</p>}
            <form action={verifyVendorAction} className="mt-4 flex flex-wrap items-end gap-2">
              <input type="hidden" name="vendorId" value={v.id} />
              <div className="min-w-[220px] flex-1"><label className="label" htmlFor={`n-${v.id}`}>Review note <span className="font-normal text-muted">(only admins see this)</span></label><input id={`n-${v.id}`} name="note" className="input !h-11" defaultValue={v.reviewNote} placeholder="ID checked on call, GST seen" /></div>
              {v.verification === "verified"
                ? <button name="verified" value="0" className="btn-line !py-2.5">Remove badge</button>
                : <button name="verified" value="1" className="btn-primary !py-2.5">Verify</button>}
            </form>
          </li>))}</ul>}
    </div>
  );
}

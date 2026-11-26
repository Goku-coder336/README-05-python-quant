import Link from "next/link";
import { redirect } from "next/navigation";
import { currentUser } from "@/lib/auth";
import { vendorsOwnedBy } from "@/lib/data";
import { deleteAccountAction, signOutAction } from "@/app/actions";
export const metadata = { title: "Your account" };
export default async function Account({ searchParams }: { searchParams: Promise<{ delete?: string }> }) {
  const u = await currentUser(); if (!u) redirect("/signin?next=/account");
  const mine = await vendorsOwnedBy(u.id); const mismatch = (await searchParams).delete === "mismatch";
  return (
    <div className="mx-auto max-w-2xl px-4 py-12 md:py-20">
      <p className="eyebrow">Your account</p>
      <h1 className="mt-3 font-display text-4xl">{u.email}</h1>
      <section className="card mt-8 p-6" aria-labelledby="biz"><h2 id="biz" className="font-display text-2xl">Your businesses</h2>
        {mine.length === 0 ? <p className="mt-2 text-muted">You have not listed a business. <Link className="underline" href="/vendor/join">List one free</Link>.</p> :
          <ul className="mt-3 grid gap-2">{mine.map(v => <li key={v.id}><Link className="font-medium underline-offset-4 hover:underline" href={`/vendor/${v.handle}`}>{v.businessName}</Link> <span className="text-sm text-muted">· dashboard</span></li>)}</ul>}
      </section>
      <section className="card mt-4 flex flex-wrap gap-3 p-6" aria-label="Sign out">
        <form action={signOutAction}><button className="btn-line">Sign out</button></form>
        <form action={signOutAction}><input type="hidden" name="everywhere" value="1" /><button className="btn-line">Sign out on all devices</button></form>
      </section>
      <section className="card mt-4 p-6" aria-labelledby="del"><h2 id="del" className="font-display text-2xl">Delete account</h2>
        <p className="mt-2 text-sm text-muted">Removes your account and sign-ins. Your business listings are taken offline. Vendors keep the booking records they need.</p>
        <form action={deleteAccountAction} className="mt-4 grid gap-3">
          <label className="label" htmlFor="confirm">Type your email to confirm</label><input className="input" id="confirm" name="confirm" autoComplete="off" />
          {mismatch && <p role="alert" className="text-sm text-danger">That did not match your email.</p>}
          <button className="btn w-fit bg-danger text-paper">Delete my account</button>
        </form>
      </section>
    </div>
  );
}
